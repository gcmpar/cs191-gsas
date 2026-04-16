import json
import tempfile
import os
import openpyxl
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Application, ApplicationTranscript
from applicants.models import Applicant
from .forms import ApplicationForm, ApplicationTranscriptFormSet
from courses.models import Course, EquivalenceMapCourses
from common.ocr import extract_courses_from_pdf


SEARCH_FIELDS = ['application_number', 'program', 'study_load', 'notes']


def get_equivalences(entry):
    
    equivalences = []

    # Probe which equivalence maps this course is part of.
    associated_entries = EquivalenceMapCourses.objects.filter(course=entry.course).select_related('map')
    for a_entry in associated_entries:
        
        map = a_entry.map

        # Get the courses of this particular map.
        map_entries = EquivalenceMapCourses.objects.filter(map=map).select_related('course')

        equivalences.append({
            'group': [m_entry.course for m_entry in map_entries],
            'target_course': map.target_course,
            'map': map,
        })

    return equivalences


def applications_search(request):
    query = request.GET.get('search')
    filter_status = request.GET.getlist('status')

    applications = Application.objects.select_related('applicant')

    if query:
        query_filter = Q()
        for field in SEARCH_FIELDS:
            query_filter |= Q(**{f'{field}__icontains': query})
        applications = applications.filter(query_filter)
    
    if len(filter_status) > 0:
        applications = applications.filter(application_status__in=filter_status)
    
    applications = applications.order_by('-date_applied')

    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'applications_page': page,
        'search_query': query,
        'filter_status': filter_status
    }
    return render(request, 'applications/search.html', context)


def application_view(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant

    entries = ApplicationTranscript.objects.filter(application=application).select_related('course')

    return render(request, 'applications/view.html', {
        'applicant':       applicant,
        'application':     application,
        'transcript_entries': {entry: get_equivalences(entry) for entry in entries},
    })


def application_add(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            return redirect('applications:view', application_id=application.application_id)
    else:
        form = ApplicationForm()
    return render(request, 'applications/add.html', {
        'form': form,
    })


def application_edit(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant

    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        formset = ApplicationTranscriptFormSet(request.POST, instance=application)

        if form.is_valid() and formset.is_valid():
            application = form.save()
            formset.instance = application
            formset.save()
            return redirect('applications:view', application_id=application_id)
    else:
        form = ApplicationForm(instance=application)
        formset = ApplicationTranscriptFormSet(instance=application)

    for entry_form in formset:
        if entry_form.instance.pk:
            entry_form.equivalences = get_equivalences(entry_form.instance)
        else:
            entry_form.equivalences = []

    return render(request, 'applications/edit.html', {
        'applicant':       applicant,
        'application':     application,
        'form':            form,
        'formset':         formset,
    })


def application_delete(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    if request.method == 'POST':
        application.delete()
        return redirect('applications:search')
    return redirect('applications:edit', application_id=application_id)


def application_scan_tor(request, application_id):
    """POST: Accept a TOR PDF upload, run OCR, store results in session, redirect to preview."""
    application = get_object_or_404(Application, pk=application_id)

    if request.method != 'POST':
        return redirect('applications:edit', application_id=application_id)

    uploaded = request.FILES.get('tor_pdf')
    if not uploaded:
        messages.error(request, 'No PDF file was uploaded.')
        return redirect('applications:edit', application_id=application_id)

    if not uploaded.name.lower().endswith('.pdf'):
        messages.error(request, 'Only PDF files are supported for TOR scanning.')
        return redirect('applications:edit', application_id=application_id)

    # Write to a temporary file, run OCR, then immediately delete.
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
            for chunk in uploaded.chunks():
                tmp.write(chunk)

        courses = extract_courses_from_pdf(tmp_path)
    except Exception as exc:
        messages.error(request, f'OCR failed: {exc}')
        return redirect('applications:edit', application_id=application_id)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not courses:
        messages.warning(request, 'No courses could be extracted from the PDF. Please check the file and try again.')
        return redirect('applications:edit', application_id=application_id)

    request.session[f'ocr_preview_{application_id}'] = courses
    return redirect('applications:ocr_preview', application_id=application_id)


def application_ocr_preview(request, application_id):
    """GET: Show editable OCR preview table. POST: Save confirmed rows as ApplicationTranscript."""
    application = get_object_or_404(Application, pk=application_id)

    session_key = f'ocr_preview_{application_id}'
    scanned_courses = request.session.get(session_key)

    if not scanned_courses:
        messages.error(request, 'No OCR data found. Please upload the TOR again.')
        return redirect('applications:edit', application_id=application_id)

    all_courses = Course.objects.prefetch_related('programs__school').order_by('course_code')

    if request.method == 'POST':
        # Collect checked-row indices from the POST data.
        included_indices = set(request.POST.getlist('include[]'))

        saved = 0
        errors = []
        for idx_str in included_indices:
            try:
                idx = int(idx_str)
                row = scanned_courses[idx]
            except (ValueError, IndexError):
                continue

            course_id = request.POST.get(f'course_id_{idx}')
            grade     = request.POST.get(f'grade_{idx}', '').strip()

            if not course_id:
                errors.append(f"Row {idx + 1}: no course selected, skipped.")
                continue

            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                errors.append(f"Row {idx + 1}: course not found, skipped.")
                continue

            # Map free-text grade to a valid choice; fall back to closest or skip.
            valid_grades = [g[0] for g in ApplicationTranscript.Grade.choices]
            if grade not in valid_grades:
                grade = 'INC'  # fallback for unrecognisable grades

            # Avoid duplicate transcript entries for the same application+course.
            ApplicationTranscript.objects.get_or_create(
                application=application,
                course=course,
                defaults={
                    'academic_year': date.today().year,
                    'semester':      ApplicationTranscript.Semester.Sem_1,
                    'grade':         grade,
                },
            )
            saved += 1

        # Clear session data after saving.
        if session_key in request.session:
            del request.session[session_key]

        for err in errors:
            messages.warning(request, err)

        messages.success(request, f'{saved} course(s) added to the transcript.')
        return redirect('applications:edit', application_id=application_id)

    # GET: build context — attempt auto-match on course_code for each scanned row.
    rows_context = []
    for idx, row in enumerate(scanned_courses):
        # Try exact match first, then case-insensitive prefix.
        matched_course = (
            Course.objects.filter(course_code__iexact=row['course_code']).first()
            or Course.objects.filter(course_code__istartswith=row['course_code'].split()[0]).first()
        )
        rows_context.append({
            'index':           idx,
            'course_code':     row['course_code'],
            'description':     row['description'],
            'grade':           row['grade'],
            'units':           row['units'],
            'matched_course':  matched_course,
        })

    return render(request, 'applications/ocr_preview.html', {
        'application':   application,
        'rows':          rows_context,
        'all_courses':   all_courses,
        'grade_choices': ApplicationTranscript.Grade.choices,
    })


def batch_import_upload(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            
            headers = [str(h).lower().strip() if h else '' for h in rows[0]] if rows else []
            data = []
            
            for row in rows[1:]:
                if not any(row):
                    continue
                    
                row_dict = dict(zip(headers, row))
                
                notes = str(row_dict.get('ngse remarks', '') or '').strip()
                
                app_no = str(row_dict.get('application no.', ''))
                if not app_no:
                    app_no = str(row_dict.get('application number', ''))
                    
                contact_raw = str(row_dict.get('contact number', '') or '')
                if contact_raw.endswith('.0'):
                    contact_raw = contact_raw[:-2]
                    
                program_raw = str(row_dict.get('program', '') or '').strip()
                if 'phd' in program_raw.lower(): program_raw = 'PhD CS'
                elif 'bio' in program_raw.lower(): program_raw = 'MS Bioinfo'
                elif 'ms' in program_raw.lower(): program_raw = 'MS CS'

                load_raw = str(row_dict.get('applying as full-time or part-time', '') or '').strip()
                if not load_raw:
                    for k in row_dict.keys():
                        if 'full-time' in k or 'part-time' in k or 'study load' in k:
                            load_raw = str(row_dict[k] or '').strip()
                            break
                if 'full' in load_raw.lower(): load_raw = 'Full-Time'
                elif 'part' in load_raw.lower(): load_raw = 'Part-Time'
                
                status_raw = str(row_dict.get('application status', '') or '').strip()
                if 'accept' in status_raw.lower(): status_raw = 'Accepted'
                elif 'reject' in status_raw.lower(): status_raw = 'Rejected'
                else: status_raw = 'Processing'
                    
                data.append({
                    'application_number': app_no,
                    'last_name': str(row_dict.get('last name', '') or '').strip(),
                    'first_name': str(row_dict.get('first name', '') or '').strip(),
                    'middle_name': str(row_dict.get('middle name', '') or '').strip(),
                    'contact_number': contact_raw.strip(),
                    'email': str(row_dict.get('email address', '') or '').strip(),
                    'application_status': status_raw,
                    'folder_link': str(row_dict.get('link to applicant main folder', '') or '').strip(),
                    'program': program_raw,
                    'study_load': load_raw,
                    'notes': notes
                })

            request.session['batch_import_data'] = data
            return redirect('applications:batch_import_confirm')

    return render(request, 'applications/batch_import.html')

def batch_import_confirm(request):
    data = request.session.get('batch_import_data', [])
    if not data:
        return redirect('applications:batch_import_upload')

    if request.method == 'POST':
        app_nos = request.POST.getlist('application_number[]')
        applicant_ids = request.POST.getlist('applicant_id[]')
        programs = request.POST.getlist('program[]')
        study_loads = request.POST.getlist('study_load[]')
        application_statuses = request.POST.getlist('application_status[]')
        notes_list = request.POST.getlist('notes[]')
        
        from .models import BatchImport
        batch_import = BatchImport.objects.create()
        
        for i in range(len(app_nos)):
            app_id = applicant_ids[i]
            if not app_id:
                continue
                
            applicant = get_object_or_404(Applicant, pk=app_id)
            Application.objects.create(
                applicant=applicant,
                application_number=app_nos[i],
                application_status=application_statuses[i],
                date_applied=date.today(),
                program=programs[i],
                study_load=study_loads[i],
                notes=notes_list[i],
                batch_import=batch_import
            )
            
        if 'batch_import_data' in request.session:
            del request.session['batch_import_data']
            
        return redirect('applications:batch_import_history')
        
    applicants = Applicant.objects.all().order_by('last_name', 'first_name')
    return render(request, 'applications/batch_import_confirm.html', {
        'data': data,
        'applicants': applicants
    })

def batch_import_history(request):
    from .models import BatchImport
    imports = BatchImport.objects.all().order_by('-date_imported')
    paginator = Paginator(imports, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, 'applications/batch_import_history.html', {
        'imports_page': page
    })

def batch_import_detail(request, import_id):
    from .models import BatchImport
    batch = get_object_or_404(BatchImport, pk=import_id)
    applications = Application.objects.filter(batch_import=batch).select_related('applicant')
    
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, 'applications/batch_import_detail.html', {
        'batch': batch,
        'applications_page': page
    })