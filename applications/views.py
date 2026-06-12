import tempfile
import os
import difflib
import openpyxl

from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import Http404
from django.template.loader import render_to_string
from django.http import HttpResponse
from .models import (
    Application, ApplicationTranscript,
    PrerequisiteMap, PrerequisiteMapCourses, BatchImport
)
from courses.models import EquivalenceMap, EquivalenceMapCourses
from applicants.models import Applicant
from .forms import (
    ApplicationForm, ApplicationsQueryForm, ApplicationTranscriptForm,
    PrereqMapForm, PrereqCourseForm, BatchImportRowForm, BatchImportFormSet, OCRRowForm, OCRFormSet,
    ExportOptionsForm
)
from courses.models import Course
from common.ocr import extract_courses_from_pdf
from .nlp import compute_similarity, compute_similarity_batch
from .export import generate_export_zip


TRANSCRIPT_FORM_PREFIX = 'transcript_'
PREREQ_MAP_PREFIX = 'prereq_map_'
PREREQ_COURSE_PREFIX = 'prereq_course_'

SEARCH_FIELDS = ['application_number', 'program', 'study_load', 'notes', 'applicant__first_name', 'applicant__middle_name', 'applicant__last_name']

def transcript_form_prefix(index):
    return f'{TRANSCRIPT_FORM_PREFIX}{index}_'

def transcript_param_index(param):
    rest = param[len(TRANSCRIPT_FORM_PREFIX):]
    return int(rest.split('_')[0])

def get_transcript_forms_from_request(request_params):
    indices = set()
    for param in request_params.keys():
        if param.startswith(TRANSCRIPT_FORM_PREFIX):
            indices.add(transcript_param_index(param))
            
    transcript_data = []
    for i in indices:
        form = ApplicationTranscriptForm(request_params, prefix=transcript_form_prefix(i))
        course = None
        course_id = request_params.get(form['course'].html_name)
        if course_id and str(course_id).isdigit():
            course = Course.objects.filter(pk=course_id).first()
        transcript_data.append({
            'form': form,
            'course': course,
            'index': i,
        })
    return transcript_data

def get_transcript_forms_from_application(application):
    entries = ApplicationTranscript.objects.filter(application=application).select_related('course')
    transcript_data = []
    
    for i, entry in enumerate(entries):
        transcript_data.append({
            'form': ApplicationTranscriptForm(prefix=transcript_form_prefix(i), instance=entry),
            'course': entry.course,
            'index': i,
        })
        
    if not transcript_data:
        transcript_data.append({
            'form': ApplicationTranscriptForm(prefix=transcript_form_prefix(0)),
            'course': None,
            'index': 0,
        })
        
    return transcript_data

def prereq_map_form_prefix(map_id):
    return f'{PREREQ_MAP_PREFIX}{map_id}_'

def prereq_course_form_prefix(map_id, index):
    return f'{PREREQ_COURSE_PREFIX}{map_id}_{index}_'

def get_prereq_snapshot_from_request(request_params, application):
    map_ids = set()
    for param in request_params.keys():
        if param.startswith(PREREQ_MAP_PREFIX):
            map_id = param[len(PREREQ_MAP_PREFIX):].split('_')[0]
            map_ids.add(int(map_id))
            
    indices_map = {map_id: set() for map_id in map_ids}
    for param in request_params.keys():
        if param.startswith(PREREQ_COURSE_PREFIX):
            rest = param[len(PREREQ_COURSE_PREFIX):].split('_')
            map_id = int(rest[0])
            index = int(rest[1])
            if map_id in indices_map:
                indices_map[map_id].add(index)
    
    all_descs = [c.description for c in Course.objects.all()]
    snapshot = {}
    for map_id in map_ids:
        indices = indices_map[map_id]
        map_form = PrereqMapForm(request_params, prefix=prereq_map_form_prefix(map_id))
        
        target_course = None
        target_course_id = request_params.get(map_form['target_course'].html_name)
        if target_course_id and str(target_course_id).isdigit():
            target_course = Course.objects.filter(pk=target_course_id).first()

        course_data = []
        for i in indices:
            prefix = prereq_course_form_prefix(map_id, i)
            form = PrereqCourseForm(request_params, application=application, prefix=prefix)
            
            course_id = request_params.get(form['course'].html_name)
            course = None

            similarity = None
            grade = None
            
            if course_id and str(course_id).isdigit():
                course = Course.objects.filter(pk=course_id).first()
                
            if course:
                transcript = ApplicationTranscript.objects.filter(application=application, course=course).first()
                if transcript:
                    grade = transcript.grade

            if course and target_course:
                similarity = compute_similarity(course.description, target_course.description, all_descs)

            course_data.append({
                'form': form,
                'course': course,
                'grade': grade,
                'similarity': similarity,
                'index': i,
            })
            
        snapshot[map_id] = {
            'map_form': map_form,
            'target_course': target_course,
            'course_data': course_data
        }
    return snapshot

def get_prereq_snapshot_from_application(application):
    existing_maps = list(PrerequisiteMap.objects.filter(
        application=application
    ).prefetch_related(
        'prerequisitemapcourses_set__course'
    ).order_by('map_id'))

    all_descs = [c.description for c in Course.objects.all()]
    snapshot = {}
    
    if not existing_maps:
        dummy_map = PrerequisiteMap.objects.create(application=application)
        existing_maps.append(dummy_map)

    for prereq_map in existing_maps:
        map_form = PrereqMapForm(
            prefix=prereq_map_form_prefix(prereq_map.map_id),
            initial={'target_course': prereq_map.target_course}
        )
        
        course_data = []
        for i, entry in enumerate(prereq_map.prerequisitemapcourses_set.all()):
            course = entry.course
            grade = None
            transcript = ApplicationTranscript.objects.filter(application=application, course=course).first()
            if transcript:
                grade = transcript.grade
                
            similarity = None
            if prereq_map.target_course:
                similarity = compute_similarity(course.description, prereq_map.target_course.description, all_descs)
                
            course_data.append({
                'form': PrereqCourseForm(
                    prefix=prereq_course_form_prefix(prereq_map.map_id, i),
                    application=application,
                    initial={'course': course.pk}
                ),
                'course': course,
                'grade': grade,
                'similarity': similarity,
                'index': i,
            })
            
        if len(course_data) == 0:
            course_data.append({
                'form': PrereqCourseForm(prefix=prereq_course_form_prefix(prereq_map.map_id, 0), application=application),
                'course': None,
                'grade': None,
                'similarity': None,
                'index': 0,
            })
            
        snapshot[prereq_map.map_id] = {
            'map_form': map_form,
            'target_course': prereq_map.target_course,
            'course_data': course_data
        }
    return snapshot

def get_equiv_transcripts(transcripts, target_course):
    maps = EquivalenceMap.objects.filter(
        target_course=target_course
    ).prefetch_related('equivalencemapcourses_set__course')
    course_groups = [
        (m.map_id, [entry.course for entry in m.equivalencemapcourses_set.all()])
        for m in maps
    ]
    transcripts_map = {
        t.course.course_id: t
        for t in transcripts
    }

    # Get the first group in which ALL courses were taken by applicant (has transcript).
    # Return its corresponding transcripts.
    for (map_id, group) in course_groups:
        if all(c.course_id in transcripts_map for c in group):
            return map_id, [
                transcripts_map[c.course_id] for c in group
            ]
    return None

def get_matching_course(course_code, course_name, all_courses_list):
    matching_course = None
    
    course_code = course_code.strip().lower()
    course_name = course_name.strip().lower()

    if course_code:
        # Exact match on course code first
        for course in all_courses_list:
            if course.course_code.strip().lower() == course_code:
                matching_course = course
                break
                
    if not matching_course:
        best_match = None
        best_ratio = 0.0
        
        for course in all_courses_list:
            c_code = (course.course_code or '').strip().lower()
            c_name = (course.course_name or '').strip().lower()
            
            code_ratio = difflib.SequenceMatcher(None, course_code, c_code).ratio() if course_code and c_code else 0.0
            name_ratio = difflib.SequenceMatcher(None, course_name, c_name).ratio() if course_name and c_name else 0.0
            
            ratio = max(code_ratio, name_ratio)
            
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = course
                
        if best_ratio > 0.8:
            matching_course = best_match

    return matching_course

def get_matching_applicant(first_name, middle_name, last_name, email, applicants):
    matching_applicant = None

    first_name = first_name.strip().lower()
    middle_name = middle_name.strip().lower()
    last_name = last_name.strip().lower()
    email = email.strip().lower()

    if email:
        for app in applicants:
            if (app.email or '').strip().lower() == email:
                matching_applicant = app
                break
    
    if not matching_applicant:
        target_name = f"{first_name} {middle_name} {last_name}".strip().lower()
        if target_name:
            best_match = None
            best_ratio = 0.0
            for app in applicants:
                app_name = f"{app.first_name} {app.middle_name} {app.last_name}".strip().lower()
                ratio = difflib.SequenceMatcher(None, target_name, app_name).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = app
            
            if best_ratio > 0.8:
                matching_applicant = best_match

    return matching_applicant


def applications_search(request):
    applications = Application.objects.select_related('applicant')

    query_form = ApplicationsQueryForm(request.GET)
    if query_form.is_valid():
        query = query_form.cleaned_data.get('search')
        status = query_form.cleaned_data.get('status')

        if query:
            query_filter = Q()
            for field in SEARCH_FIELDS:
                query_filter |= Q(**{f'{field}__icontains': query})
            applications = applications.filter(query_filter)
        
        if status:
            applications = applications.filter(application_status__in=status)
    
    applications = applications.order_by('-date_applied')

    page_param_name = 'page'
    page_number = request.GET.get(page_param_name)
    paginator = Paginator(applications, 15)
    page = paginator.get_page(page_number)

    query_clear = {
        field.html_name: None for field in query_form
    }
    query_clear[page_param_name] = None
    context = {
        'applications_page': page,
        'query_form': query_form,
        'query_clear': query_clear,
        'export_form': ExportOptionsForm()
    }
    return render(request, 'applications/search.html', context)

def applications_export(request):
    redirect_to = request.GET.get('next', '/')
    if request.method == 'POST':
        application_ids = request.POST.getlist('application_ids')
        
        export_form = ExportOptionsForm(request.POST)
        if not export_form.is_valid():
            messages.error(request, "Please select a valid export format.")
            return redirect(redirect_to)
            
        export_format = export_form.cleaned_data['export_format']

        if not application_ids:
            messages.warning(request, "Please select at least one application to export.")
            return redirect(redirect_to)

        applications = Application.objects.filter(pk__in=application_ids)

        return generate_export_zip(applications, export_format)
    
    return redirect(redirect_to)

def application_export(request, application_id):
    redirect_to = request.GET.get('next', '/')
    if request.method == 'POST':
        export_form = ExportOptionsForm(request.POST)
        if not export_form.is_valid():
            messages.error(request, "Please select a valid export format.")
            return redirect(redirect_to)
            
        export_format = export_form.cleaned_data['export_format']

        application = Application.objects.filter(pk=application_id).first()
        return generate_export_zip([application], export_format)
    
    return redirect(redirect_to)


def application_general_view(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant

    return render(request, 'applications/general_view.html', {
        'applicant':   applicant,
        'application': application,
    })


def application_add(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            return redirect('applications:general_view', application_id=application.application_id)
    else:
        form = ApplicationForm()
    return render(request, 'applications/add.html', {
        'form': form,
    })


def application_general_edit(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant

    if request.method == 'POST':
        form = ApplicationForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save()
            return redirect('applications:general_view', application_id=application_id)
    else:
        form = ApplicationForm(instance=application)

    return render(request, 'applications/general_edit.html', {
        'applicant':   applicant,
        'application': application,
        'form':        form,
    })

def application_transcripts_view(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant
    entries = ApplicationTranscript.objects.filter(application=application).select_related('course')

    return render(request, 'applications/transcripts_view.html', {
        'applicant':          applicant,
        'application':        application,
        'transcript_entries': entries,
    })

def application_transcripts_edit(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant

    if request.method == 'POST':
        transcript_data = get_transcript_forms_from_request(request.POST)
        if all(data['form'].is_valid() for data in transcript_data):
            # Save logic
            saved_course_ids = set()
            for data in transcript_data:
                form = data['form']
                if not form.cleaned_data.get('course'):
                    continue
                    
                course = form.cleaned_data['course']
                saved_course_ids.add(course.pk)
                
                # Update or create transcript entry
                ApplicationTranscript.objects.update_or_create(
                    application=application,
                    course=course,
                    defaults={
                        'academic_year': form.cleaned_data['academic_year'],
                        'semester': form.cleaned_data['semester'],
                        'grade': form.cleaned_data['grade'],
                    }
                )
                
            # Delete transcripts that were removed
            ApplicationTranscript.objects.filter(application=application).exclude(course_id__in=saved_course_ids).delete()
            
            return redirect('applications:transcripts_view', application_id=application_id)
    else:
        transcript_data = get_transcript_forms_from_application(application)

    return render(request, 'applications/transcripts_edit.html', {
        'applicant':   applicant,
        'application': application,
        'transcript_data': transcript_data,
    })

def application_transcript_form(request, application_id):
    index = int(request.GET.get('index', 0))
    update = request.GET.get('update')

    application = get_object_or_404(Application, pk=application_id)
    transcript_form = ApplicationTranscriptForm(request.GET, prefix=transcript_form_prefix(index))

    course = None
    course_id = request.GET.get(transcript_form['course'].html_name)
    if course_id and str(course_id).isdigit():
        course = Course.objects.filter(course_id=course_id).first()

    return render(
        request,
        'applications/partials/transcript_form.html',
        {
            'transcript_form': transcript_form,
            'application': application,
            'course': course,
            'index': index,
            'update': update,
        }
    )

def application_prereq_view(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant

    prereq_maps = PrerequisiteMap.objects.filter(
        application=application
    ).prefetch_related('prerequisitemapcourses_set__course').order_by('map_id')

    mappings = []
    all_descs = [c.description for c in Course.objects.all()]

    grades_map = {}
    for transcript in ApplicationTranscript.objects.filter(application=application):
        grades_map[transcript.course.course_id] = transcript.grade

    for prereq_map in prereq_maps:
        course_data = []

        target_course = prereq_map.target_course
        taken_courses = [entry.course for entry in prereq_map.prerequisitemapcourses_set.all()]

        if target_course:
            similarities = compute_similarity_batch(taken_courses, target_course, all_descs)

            for i, course in enumerate(taken_courses):
                sim = similarities[i]
                course_data.append({
                    'course': course,
                    'grade': grades_map.get(course.course_id),
                    'similarity': sim,
                })
        else:
            for course in taken_courses:
                course_data.append({
                    'course': course,
                    'grade': grades_map.get(course.course_id),
                    'similarity': None,
                })
        
        mappings.append({
            'map': prereq_map,
            'course_data': course_data,
        })

    return render(request, 'applications/prereq_view.html', {
        'applicant':   applicant,
        'application': application,
        'mappings': mappings,
        'export_form': ExportOptionsForm()
    })
def application_prereq_save_to_equiv(request, application_id):
    application = get_object_or_404(Application, pk=application_id)

    if request.method == 'POST':
        map_ids_param = request.POST.getlist('map_ids[]')
        map_ids = []
        for id in map_ids_param:
            if str(id).isdigit():
                map_ids.append(int(id))
                
        prereq_maps = PrerequisiteMap.objects.filter(
            application=application,
            map_id__in=map_ids,
        ).prefetch_related('prerequisitemapcourses_set__course').order_by('map_id')


        target_course_ids = []
        for prereq_map in prereq_maps:
            if prereq_map.target_course:
                target_course_ids.append(prereq_map.target_course.course_id)
        target_equiv_maps = EquivalenceMap.objects.select_related('target_course').prefetch_related('equivalencemapcourses_set__course').filter(target_course__course_id__in=target_course_ids)

        html_data = []
        for prereq_map in prereq_maps:
            result, message = None, None

            target_course = prereq_map.target_course
            if target_course:
                courses = [entry.course for entry in prereq_map.prerequisitemapcourses_set.all()]
                course_set = set([c.course_id for c in courses])

                found = None
                related_equiv_maps = target_equiv_maps.filter(target_course=target_course)
                for equiv_map in related_equiv_maps:
                    equiv_course_set = set([entry.course.course_id for entry in equiv_map.equivalencemapcourses_set.all()])
                    if course_set == equiv_course_set:
                        found = equiv_map
                        break
                
                if found is None:
                    new_equiv_map = EquivalenceMap.objects.create(target_course=target_course)
                    for course in courses:
                        EquivalenceMapCourses.objects.create(map=new_equiv_map, course=course)

                    result = 'success'
                    message = f'Saved to Equivalence Map #{new_equiv_map.map_id} for "{target_course.course_code}".'
                else:
                    result = 'warning'
                    message = f'This mapping combination already exists (Equivalence Map #{found.map_id}) for "{target_course.course_code}"!'

            else:
                result = 'error'
                message = f'No target course selected!'
            
            html_data.append(
                render_to_string('applications/partials/prereq_alert.html', {
                    'map_id': prereq_map.map_id,
                    'result': result,
                    'message': message,
                    'update': True,
                })
            )

        return HttpResponse(''.join(html_data))

    raise Http404()

def application_prereq_edit(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant

    if request.method == 'POST':
        prereq_snapshot = get_prereq_snapshot_from_request(request.POST, application)

        # Validate all forms
        all_valid = True
        for info in prereq_snapshot.values():
            if not info['map_form'].is_valid():
                all_valid = False
            for data in info['course_data']:
                if not data['form'].is_valid():
                    all_valid = False

        if all_valid:
            raw_snapshot = {}
            for map_id, info in prereq_snapshot.items():
                target_course = info['map_form'].cleaned_data.get('target_course')
                
                course_ids = {
                    data['form'].cleaned_data['course'].course_id
                    for data in info['course_data']
                    if data['form'].cleaned_data.get('course')
                }
                raw_snapshot[map_id] = {
                    'target_course': target_course,
                    'course_ids': course_ids
                }

            for map_id, data in raw_snapshot.items():
                target_course = data['target_course']
                course_ids = data['course_ids']

                # Check if map exists for this application
                if PrerequisiteMap.objects.filter(pk=map_id, application=application).first() is None:
                    raise Http404()

                prereq_map = get_object_or_404(PrerequisiteMap, pk=map_id, application=application)
                prereq_map.target_course = target_course
                prereq_map.save()

                # Remove missing courses from map
                PrerequisiteMapCourses.objects.filter(map=prereq_map).exclude(course_id__in=course_ids).delete()
                
                # Add new courses
                existing_course_ids = set(PrerequisiteMapCourses.objects.filter(map=prereq_map).values_list('course_id', flat=True))
                PrerequisiteMapCourses.objects.bulk_create([
                    PrerequisiteMapCourses(map=prereq_map, course_id=c_id)
                    for c_id in course_ids
                    if c_id not in existing_course_ids
                ])

            # Remove deleted maps entirely
            submitted_map_ids = set(raw_snapshot.keys())
            PrerequisiteMap.objects.filter(
                application=application
            ).exclude(
                map_id__in=submitted_map_ids
            ).delete()

            return redirect('applications:prereq_view', application_id=application_id)
                
    else:
        prereq_snapshot = get_prereq_snapshot_from_application(application)

    return render(request, 'applications/prereq_edit.html', {
        'applicant':   applicant,
        'application': application,
        'prereq_snapshot': prereq_snapshot,
    })

# Unlike entries, maps are created immediately on every add.
# Thus, let's separate add and update into two partial views.
def application_prereq_map(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    prereq_map = PrerequisiteMap.objects.create(application=application)

    return render(
        request,
        'applications/partials/prereq_map.html',
        {
            'map_id': prereq_map.map_id,
            'map_form': PrereqMapForm(prefix=prereq_map_form_prefix(prereq_map.map_id)),
            'target_course': prereq_map.target_course,
            'course_data': [],
            'application': application,
        }
    )
def application_prereq_map_update(request, application_id, map_id):
    application = get_object_or_404(Application, pk=application_id)
    prereq_map = PrerequisiteMap.objects.filter(pk=map_id).first()

    prereq_snapshot = get_prereq_snapshot_from_request(request.GET, application)
    map_snapshot = prereq_snapshot.get(prereq_map.map_id)
    if not map_snapshot:
        raise Http404()
    
    # set update=True for the HTMX OOB swaps for each entry form.
    return render(
        request,
        'applications/partials/prereq_map.html',
        {
            'map_id': prereq_map.map_id,
            'map_form': map_snapshot['map_form'],
            'target_course': map_snapshot['target_course'],
            'course_data': map_snapshot['course_data'],
            'application': application,
            'update': True,
        }
    )

def application_prereq_form(request, application_id, map_id):
    application = get_object_or_404(Application, pk=application_id)
    prereq_map = PrerequisiteMap.objects.filter(pk=map_id).first()

    index = int(request.GET.get('index', 0))
    update = request.GET.get('update')
    prefix = prereq_course_form_prefix(map_id, index)

    course_form = PrereqCourseForm(request.GET, prefix=prefix, application=application)
    similarity = None
    grade = None

    course_id = request.GET.get(course_form['course'].html_name)
    target_course_id = request.GET.get(prereq_map_form_prefix(map_id) + '-target_course')
    course, target_course = None, None
    if course_id and str(course_id).isdigit():
        course = Course.objects.filter(pk=course_id).first()

    if target_course_id and str(target_course_id).isdigit():
        target_course = Course.objects.filter(pk=target_course_id).first()
    
    if course:
        transcript = ApplicationTranscript.objects.filter(application=application, course=course).first()
        if transcript:
            grade = transcript.grade
    if course and target_course:
            all_descs = [c.description for c in Course.objects.all()]
            similarity = compute_similarity(course.description, target_course.description, all_descs)

    return render(
        request,
        'applications/partials/prereq_form.html',
        {
            'course_form': course_form,
            'course': course,
            'grade': grade,
            'similarity': similarity,
            'map_id': map_id,
            'index': index,
            'update': update,
            'application': application,
        }
    )

def application_prereq_detect_equiv(request, application_id, map_id):
    application = get_object_or_404(Application, pk=application_id)
    prereq_map = PrerequisiteMap.objects.filter(pk=map_id).first()
    
    target_course_id = request.GET.get(prereq_map_form_prefix(map_id) + '-target_course')
    target_course = None
    if target_course_id and str(target_course_id).isdigit():
        target_course = Course.objects.filter(pk=target_course_id).first()
    
    html_data = []
    result, message = None, None
    if target_course:
        transcripts = None
        if application.applicant is None:
            transcripts = list(ApplicationTranscript.objects.filter(application=application).select_related('course'))
        else:
            transcripts = list(ApplicationTranscript.objects.filter(application__applicant=application.applicant).select_related('course'))
        detected_equiv = get_equiv_transcripts(transcripts, target_course)

        matched_forms_data = []
        if detected_equiv:
            (valid_map_id, valid_transcripts) = detected_equiv
            valid_taken_courses = [t.course for t in valid_transcripts]
            all_descs = [c.description for c in Course.objects.all()]
            similarities = compute_similarity_batch(valid_taken_courses, target_course, all_descs)

            index = 0
            for i, transcript in enumerate(valid_transcripts):
                course = transcript.course
                sim = similarities[i]
                prefix = prereq_course_form_prefix(map_id, index)
                form = PrereqCourseForm(prefix=prefix, application=application, initial={'course': course.pk})
                matched_forms_data.append({
                    'course_form': form,
                    'course': course,
                    'grade': transcript.grade,
                    'similarity': sim,
                    'map_id': map_id,
                    'index': index
                })
                index += 1
                
        else:
            prefix = prereq_course_form_prefix(map_id, 0)
            form = PrereqCourseForm(prefix=prefix, application=application)
            matched_forms_data.append({
                'course_form': form,
                'course': None,
                'grade': None,
                'similarity': None,
                'map_id': map_id,
                'index': 0
            })

        for data in matched_forms_data:
            data['application'] = application
            html_data.append(render_to_string('applications/partials/prereq_form.html', data, request=request))
        
        if detected_equiv:
            (valid_map_id, _) = detected_equiv
            result = 'success'
            message = f'Loaded Equivalence Map #{valid_map_id} from "{target_course.course_code}".'
        else:
            result = 'warning'
            message = f'No detected equivalences found for "{target_course.course_code}".'
    else:
        result = 'error'
        message = f'No target course selected!'

    
    # Alert
    html_data.append(
        render_to_string('applications/partials/prereq_alert.html', {
            'map_id': map_id,
            'result': result,
            'message': message,
            'update': True,
        })
    )
        
    return HttpResponse(''.join(html_data))

def application_prereq_detect_similar(request, application_id, map_id):
    application = get_object_or_404(Application, pk=application_id)
    prereq_map = PrerequisiteMap.objects.filter(pk=map_id).first()
    
    target_course_id = request.GET.get(prereq_map_form_prefix(map_id) + '-target_course')
    target_course = None
    if target_course_id and str(target_course_id).isdigit():
        target_course = Course.objects.filter(pk=target_course_id).first()
    
    html_data = []
    result, message = None, None
    if target_course:
        
        transcripts = None
        if application.applicant is None:
            transcripts = list(ApplicationTranscript.objects.filter(application=application).select_related('course'))
        else:
            transcripts = list(ApplicationTranscript.objects.filter(application__applicant=application.applicant).select_related('course'))
        
        taken_courses = [t.course for t in transcripts]
        all_descs = [c.description for c in Course.objects.all()]
        similarities = compute_similarity_batch(taken_courses, target_course, all_descs)
        
        matched_forms_data = []
        index = 0
        found = False
        lower_bound = 30.0
        for i, transcript in enumerate(transcripts):
            course = transcript.course
            sim = similarities[i]
            if sim > lower_bound:
                prefix = prereq_course_form_prefix(map_id, index)
                form = PrereqCourseForm(prefix=prefix, application=application, initial={'course': course.pk})
                matched_forms_data.append({
                    'course_form': form,
                    'course': course,
                    'grade': transcript.grade,
                    'similarity': sim,
                    'map_id': map_id,
                    'index': index
                })
                index += 1
                found = True
                
        if not matched_forms_data:
            prefix = prereq_course_form_prefix(map_id, 0)
            form = PrereqCourseForm(prefix=prefix, application=application)
            matched_forms_data.append({
                'course_form': form,
                'course': None,
                'grade': None,
                'similarity': None,
                'map_id': map_id,
                'index': 0
            })

        for data in matched_forms_data:
            data['application'] = application
            html_data.append(render_to_string('applications/partials/prereq_form.html', data, request=request))
        
        if found:
            count = len(matched_forms_data)
            result = 'success'
            message = f'{count} similar course{'s' if count > 1 else ''} found (above {lower_bound}%).'
        else:
            result = 'warning'
            message = 'No similar courses found.'
    else:
        result = 'error'
        message = 'No target course selected!'
    
    # Alert
    html_data.append(
        render_to_string('applications/partials/prereq_alert.html', {
            'map_id': map_id,
            'result': result,
            'message': message,
            'update': True,
        })
    )
        
    return HttpResponse(''.join(html_data))


def application_delete(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    if request.method == 'POST':
        application.delete()
        return redirect('applications:search')
    return redirect('applications:general_edit', application_id=application_id)





def application_scan_tor(request, application_id):
    """POST: Accept a TOR PDF upload, run OCR, store results in session, redirect to preview."""
    application = get_object_or_404(Application, pk=application_id)

    if request.method != 'POST':
        return redirect('applications:transcripts_edit', application_id=application_id)

    uploaded = request.FILES.get('tor_pdf')
    if not uploaded:
        messages.error(request, 'No PDF file was uploaded.')
        return redirect('applications:transcripts_edit', application_id=application_id)

    if not uploaded.name.lower().endswith('.pdf'):
        messages.error(request, 'Only PDF files are supported for TOR scanning.')
        return redirect('applications:transcripts_edit', application_id=application_id)

    # Write to a temporary file, run OCR, then immediately delete.
    try:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp_path = tmp.name
            for chunk in uploaded.chunks():
                tmp.write(chunk)

        courses = extract_courses_from_pdf(tmp_path)
    except Exception as exc:
        messages.error(request, f'OCR failed: {exc}')
        return redirect('applications:transcripts_edit', application_id=application_id)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    if not courses:
        messages.warning(request, 'No courses could be extracted from the PDF. Please check the file and try again.')
        return redirect('applications:transcripts_edit', application_id=application_id)

    request.session[f'ocr_preview_{application_id}'] = courses
    return redirect('applications:ocr_preview', application_id=application_id)


def application_ocr_preview(request, application_id):
    """GET: Show editable OCR preview table. POST: Save confirmed rows as ApplicationTranscript."""
    application = get_object_or_404(Application, pk=application_id)

    session_key = f'ocr_preview_{application_id}'
    scanned_courses = request.session.get(session_key)

    if not scanned_courses:
        messages.error(request, 'No OCR data found. Please upload the TOR again.')
        return redirect('applications:transcripts_edit', application_id=application_id)

    if request.method == 'POST':
        formset = OCRFormSet(request.POST)
        if formset.is_valid():
            saved = 0
            errors = []
            
            for i, form in enumerate(formset):
                if form.cleaned_data.get('include'):
                    course = form.cleaned_data.get('course')
                    grade = form.cleaned_data.get('grade') or 'unknown'
                    
                    if not course:
                        errors.append(f"Row {i + 1}: no course selected, skipped.")
                        continue
                        
                    ApplicationTranscript.objects.get_or_create(
                        application=application,
                        course=course,
                        defaults={
                            'academic_year': timezone.now().year,
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

            messages.success(request, f'{saved} course(s) added to the transcript. Please update their AY and Semesters.')
            return redirect('applications:transcripts_edit', application_id=application_id)
        else:
            messages.error(request, 'Please correct the errors below.')

        for form in formset:
            course_id = form['course'].value()
            if course_id:
                form.course_instance = Course.objects.filter(course_id=course_id).first()
            else:
                form.course_instance = None

    else:
        detect_courses = request.GET.get('detect_courses')
        update = request.GET.get('update')
        all_courses_list = list(Course.objects.prefetch_related('programs__school').order_by('course_code'))

        if detect_courses:
            get = request.GET.copy()
            matching_courses = {}

            formset = OCRFormSet(get)
            for form in formset:
                matching_course = get_matching_course(
                    get[form.add_prefix('scanned_code')],
                    get[form.add_prefix('scanned_name')],
                    all_courses_list
                )

                get[form.add_prefix('course')] = matching_course.course_id if matching_course else None
                matching_courses[form.prefix] = matching_course
        
            formset = OCRFormSet(get)
            for form in formset:
                form.course_instance = matching_courses.get(form.prefix)
            
            return render(request, 'applications/partials/ocr_preview_formset.html', {
                'application':    application,
                'formset':        formset,
                'detect_courses': detect_courses,
            })
        elif update:
            formset = OCRFormSet(request.GET)
            for form in formset:
                course_id = form['course'].value()
                if course_id:
                    form.course_instance = Course.objects.filter(course_id=course_id).first()
                else:
                    form.course_instance = None
            
            return render(request, 'applications/partials/ocr_preview_formset.html', {
                'application':    application,
                'formset':        formset,
                'update':         update,
            })

        else:
            # GET: build context — attempt auto-match on course_code and course_name for each scanned row.
            initial_data = []
            for idx, row in enumerate(scanned_courses):
                scanned_code = row.get('course_code')[:OCRRowForm.base_fields['scanned_code'].max_length]
                scanned_name = row.get('course_name')[:OCRRowForm.base_fields['scanned_name'].max_length]

                matching_course = get_matching_course(
                    scanned_code,
                    scanned_name,
                    all_courses_list
                )

                initial_data.append({
                    'include': True,
                    'scanned_code': scanned_code,
                    'scanned_name': scanned_name,
                    'scanned_units': row.get('units'),
                    'course': matching_course.course_id if matching_course else None,
                    'grade': row.get('grade')
                })
            
            formset = OCRFormSet(initial=initial_data)
            for form in formset:
                course_id = form['course'].value()
                if course_id:
                    form.course_instance = Course.objects.filter(course_id=course_id).first()
                else:
                    form.course_instance = None

    return render(request, 'applications/ocr_preview.html', {
        'application':   application,
        'formset':       formset,
    })


def batch_import_upload(request):
    if request.method == 'POST':
        if 'excel_file' in request.FILES:
            excel_file = request.FILES['excel_file']
            wb = openpyxl.load_workbook(excel_file, data_only=True)
            sheet = wb.active
            rows = list(sheet.iter_rows(values_only=True))
            
            headers = [str(h).lower().strip() if h else '' for h in rows[0]] if rows else []
            data = []
            
            for row in rows[1:]:
                if not any(row):
                    continue
                    
                row_dict = dict(zip(headers, row))
                
                notes = ''
                
                app_no = str(row_dict.get('application no.', ''))
                if not app_no:
                    app_no = str(row_dict.get('application number', ''))
                    
                contact_raw = str(row_dict.get('contact number', '') or '')
                if contact_raw.endswith('.0'):
                    contact_raw = contact_raw[:-2]
                    
                program_raw = str(row_dict.get('program', '') or '').strip()
                program_raw_lower = program_raw.lower()
                if any(text in program_raw_lower for text in ['bio']): program_raw = 'MS Bioinfo'
                elif any(text in program_raw_lower for text in ['phd', 'doctor', 'philosophy']): program_raw = 'PhD CS'
                elif any(text in program_raw_lower for text in ['ms', 'master']): program_raw = 'MS CS'

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

                ngse_requirements_complete_raw = str(row_dict.get('ngse\nrequirements complete?', '') or row_dict.get('ngse requirements complete', '') or '').strip().lower()
                if ngse_requirements_complete_raw in ['yes', 'true', '1', 'y']:
                    ngse_requirements_complete_raw = True
                elif ngse_requirements_complete_raw in ['no', 'false', '0', 'n']:
                    ngse_requirements_complete_raw = False
                else:
                    ngse_requirements_complete_raw = None

                data.append({
                    'application_number': app_no,
                    'last_name': str(row_dict.get('last name', '') or '').strip(),
                    'first_name': str(row_dict.get('first name', '') or '').strip(),
                    'middle_name': str(row_dict.get('middle name', '') or '').strip(),
                    'contact_number': contact_raw.strip(),
                    'email': str(row_dict.get('email address', '') or '').strip(),
                    'application_status': status_raw,
                    'folder_link': str(row_dict.get('link to applicant\nmain folder', '') or row_dict.get('link to applicant main folder', '') or '').strip(),
                    'program': program_raw,
                    'study_load': load_raw,
                    'unit': str(row_dict.get('unit', '') or '').strip(),
                    'research_field_1': str(row_dict.get('research field 1', '') or '').strip(),
                    'research_field_2': str(row_dict.get('research field 2', '') or '').strip(),
                    'research_field_3': str(row_dict.get('research field 3', '') or '').strip(),
                    'special_project_topic_interest': str(row_dict.get('special project topic interest', '') or '').strip(),
                    'undergraduate_gwa': str(row_dict.get('undergradute gwa \n(ex. ge subj)', '') or row_dict.get('undergraduate gwa', '') or '').strip(),
                    'undergraduate_failed_subjects': str(row_dict.get('undergraduate number of failed subjects', '') or '').strip(),
                    'graduate_gwa': str(row_dict.get('graduate\ngwa', '') or row_dict.get('graduate gwa', '') or '').strip(),
                    'graduate_failed_subjects': str(row_dict.get('graduate\nnumber of failed subjects', '') or row_dict.get('graduate number of failed subjects', '') or '').strip(),
                    'ngse_requirements_complete': ngse_requirements_complete_raw,
                    'ngse_remarks': str(row_dict.get('ngse remarks', '') or '').strip(),
                    'notes': notes,
                })

            request.session['batch_import_data'] = data
            return redirect('applications:batch_import_confirm')

    return render(request, 'applications/batch_import.html')

def batch_import_confirm(request):
    data = request.session.get('batch_import_data', [])
    if not data:
        return redirect('applications:batch_import_upload')
    

    if request.method == 'POST':
        formset = BatchImportFormSet(request.POST)
        if formset.is_valid():
            batch_import = BatchImport.objects.create()
            
            for form in formset:
                application = form.save(commit=False)
                application.date_applied = timezone.localdate()
                application.batch_import = batch_import
                application.save()
                
            if 'batch_import_data' in request.session:
                del request.session['batch_import_data']
                
            return redirect('applications:batch_import_history')

        for form in formset:
            applicant_id = form['applicant'].value()
            if applicant_id:
                form.applicant_instance = Applicant.objects.filter(applicant_id=applicant_id).first()
            else:
                form.applicant_instance = None
        
    else:
        detect_applicants = request.GET.get('detect_applicants')
        update = request.GET.get('update')
        all_applicants_list = list(Applicant.objects.all())

        if detect_applicants:
            get = request.GET.copy()
            matching_applicants = {}

            formset = BatchImportFormSet(get)
            for form in formset.forms:
                matching_applicant = get_matching_applicant(
                    get.get(form.add_prefix('scanned_first_name')),
                    get.get(form.add_prefix('scanned_middle_name')),
                    get.get(form.add_prefix('scanned_last_name')),
                    get.get(form.add_prefix('scanned_email')),
                    all_applicants_list
                )

                get[form.add_prefix('applicant')] = matching_applicant
                matching_applicants[form.prefix] = matching_applicant
            
            formset = BatchImportFormSet(get)
            for form in formset:
                form.applicant_instance = matching_applicants.get(form.prefix)
            return render(request, 'applications/partials/batch_import_confirm_formset.html', {
                'formset': formset,
                'detect_applicants': detect_applicants,
            })

        elif update:
            formset = BatchImportFormSet(request.GET)
            for form in formset:
                applicant_id = form['applicant'].value()
                if applicant_id:
                    form.applicant_instance = Applicant.objects.filter(applicant_id=applicant_id).first()
                else:
                    form.applicant_instance = None
            return render(request, 'applications/partials/batch_import_confirm_formset.html', {
                'formset': formset,
                'update': update,
            })
        else:

            initial_data = []
            for row in data:
                scanned_first_name = row.get('first_name')[:BatchImportRowForm.base_fields['scanned_first_name'].max_length]
                scanned_middle_name = row.get('middle_name')[:BatchImportRowForm.base_fields['scanned_middle_name'].max_length]
                scanned_last_name = row.get('last_name')[:BatchImportRowForm.base_fields['scanned_last_name'].max_length]
                scanned_email = row.get('email')[:BatchImportRowForm.base_fields['scanned_email'].max_length]
                scanned_contact_number = row.get('contact_number')[:BatchImportRowForm.base_fields['scanned_contact_number'].max_length]

                matching_applicant = get_matching_applicant(
                    scanned_first_name,
                    scanned_middle_name,
                    scanned_last_name,
                    scanned_email,
                    all_applicants_list
                )
                
                # For ngse_requirements_complete field.
                ngse_requirements_complete_raw = row.get('ngse_requirements_complete')
                ngse_requirements_complete = None
                if ngse_requirements_complete_raw == True:
                    ngse_requirements_complete = 'true'
                elif ngse_requirements_complete_raw == False:
                    ngse_requirements_complete = 'false'
                else:
                    ngse_requirements_complete = 'null'

                initial_data.append({
                    'application_number': row.get('application_number'),
                    'scanned_last_name': scanned_last_name,
                    'scanned_first_name': scanned_first_name,
                    'scanned_middle_name': scanned_middle_name,
                    'scanned_email': scanned_email,
                    'scanned_contact_number': scanned_contact_number,
                    'applicant': matching_applicant.applicant_id if matching_applicant else None,
                    'application_status': row.get('application_status'),
                    'folder_link': row.get('folder_link'),
                    'program': row.get('program'),
                    'study_load': row.get('study_load'),
                    'unit': row.get('unit'),
                    'research_field_1': row.get('research_field_1'),
                    'research_field_2': row.get('research_field_2'),
                    'research_field_3': row.get('research_field_3'),
                    'special_project_topic_interest': row.get('special_project_topic_interest'),
                    'undergraduate_gwa': row.get('undergraduate_gwa'),
                    'undergraduate_failed_subjects': row.get('undergraduate_failed_subjects'),
                    'graduate_gwa': row.get('graduate_gwa'),
                    'graduate_failed_subjects': row.get('graduate_failed_subjects'),
                    'ngse_requirements_complete': ngse_requirements_complete,
                    'ngse_remarks': row.get('ngse_remarks'),
                    'notes': row.get('notes'),
                })
            formset = BatchImportFormSet(initial=initial_data)
            for form in formset:
                applicant_id = form['applicant'].value()
                if applicant_id:
                    form.applicant_instance = Applicant.objects.filter(applicant_id=applicant_id).first()
                else:
                    form.applicant_instance = None
        
    return render(request, 'applications/batch_import_confirm.html', {
        'formset': formset,
    })
def batch_import_create_applicant(request):
    post = request.POST.copy()
    prefix = post.get('prefix')
    form = BatchImportRowForm(post, prefix=prefix)
    
    scanned_first_name = form['scanned_first_name'].value() or ''
    scanned_middle_name = form['scanned_middle_name'].value() or ''
    scanned_last_name = form['scanned_last_name'].value() or ''
    scanned_email = form['scanned_email'].value() or ''
    scanned_contact_number = form['scanned_contact_number'].value() or ''
    
    applicant = Applicant.objects.create(
        first_name       = scanned_first_name[:Applicant._meta.get_field('first_name').max_length],
        middle_name      = scanned_middle_name[:Applicant._meta.get_field('middle_name').max_length],
        last_name        = scanned_last_name[:Applicant._meta.get_field('last_name').max_length],
        applicant_status = Applicant.Status.APPLYING,
        email            = scanned_email[:Applicant._meta.get_field('email').max_length],
        contact_number   = scanned_contact_number[:Applicant._meta.get_field('contact_number').max_length],
        notes            = None,
    )
    post[form.add_prefix('applicant')] = applicant

    form = BatchImportRowForm(post, prefix=prefix)
    form.applicant_instance = applicant

    return render(
        request,
        'applications/partials/batch_import_confirm_form.html',
        {
            'form': form,
            'detect_applicants': True,
        }
    )

def batch_import_history(request):
    imports = BatchImport.objects.all().order_by('-date_imported')
    paginator = Paginator(imports, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, 'applications/batch_import_history.html', {
        'imports_page': page
    })

def batch_import_detail(request, import_id):
    batch = get_object_or_404(BatchImport, pk=import_id)
    applications = Application.objects.filter(batch_import=batch).select_related('applicant')
    
    paginator = Paginator(applications, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, 'applications/batch_import_detail.html', {
        'batch': batch,
        'applications_page': page
    })