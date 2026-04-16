from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Applicant
from applications.models import Application, ApplicationTranscript
from .forms import ApplicantForm


SEARCH_FIELDS = ['applicant_id', 'first_name', 'middle_name', 'last_name', 'email', 'contact_number', 'notes']

def applicants_search(request):
    query = request.GET.get('search')
    filter_status = request.GET.getlist('status')

    applicants = Applicant.objects

    if query:
        query_filter = Q()
        for field in SEARCH_FIELDS:
            query_filter |= Q(**{f'{field}__icontains': query})
        applicants = applicants.filter(query_filter)
    
    if len(filter_status) > 0:
        applicants = applicants.filter(applicant_status__in=filter_status)
    
    applicants = applicants.order_by('applicant_id')

    paginator = Paginator(applicants, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'applicants_page': page,
        'search_query': query,
        'filter_status': filter_status
    }
    return render(request, 'applicants/search.html', context)


def applicant_view(request, applicant_id):
    applicant    = get_object_or_404(Applicant, pk=applicant_id)
    applications = Application.objects.filter(applicant=applicant)

    school_map = {}
    program_map = {}
    course_map = {}
    
    for app in applications:
        transcripts = ApplicationTranscript.objects.filter(application=app).select_related('course', 'course__program', 'course__program__school')
        for transcript in transcripts:
            c = transcript.course
            p = c.program
            s = p.school
            
            if s.pk not in school_map:
                school_map[s.pk] = {'school': s, 'app_ids': set()}
            school_map[s.pk]['app_ids'].add(app.application_id)
            
            if p.pk not in program_map:
                program_map[p.pk] = {'program': p, 'app_ids': set()}
            program_map[p.pk]['app_ids'].add(app.application_id)

            if c.pk not in course_map:
                course_map[c.pk] = {'course': c, 'app_ids': set()}
            course_map[c.pk]['app_ids'].add(app.application_id)

    school_list = [{'school': v['school'], 'app_ids': sorted(list(v['app_ids']))} for v in school_map.values()]
    program_list = [{'program': v['program'], 'app_ids': sorted(list(v['app_ids']))} for v in program_map.values()]
    course_list = [{'course': v['course'], 'app_ids': sorted(list(v['app_ids']))} for v in course_map.values()]

    return render(request, 'applicants/view.html', {
        'applicant':    applicant,
        'applications': applications,
        'school_list':  school_list,
        'program_list': program_list,
        'course_list':  course_list,
    })


def applicant_add(request):
    if request.method == 'POST':
        form = ApplicantForm(request.POST)
        if form.is_valid():
            applicant = form.save()
            return redirect('applicants:view', applicant_id=applicant.applicant_id)
    else:
        form = ApplicantForm()
    return render(request, 'applicants/add.html', {
        'form': form,
    })


def applicant_edit(request, applicant_id):
    applicant    = get_object_or_404(Applicant, pk=applicant_id)
    applications = Application.objects.filter(applicant=applicant)

    school_map = {}
    program_map = {}
    course_map = {}
    
    for app in applications:
        transcripts = ApplicationTranscript.objects.filter(application=app).select_related('course', 'course__program', 'course__program__school')
        for transcript in transcripts:
            c = transcript.course
            p = c.program
            s = p.school
            
            if s.pk not in school_map:
                school_map[s.pk] = {'school': s, 'app_ids': set()}
            school_map[s.pk]['app_ids'].add(app.application_id)
            
            if p.pk not in program_map:
                program_map[p.pk] = {'program': p, 'app_ids': set()}
            program_map[p.pk]['app_ids'].add(app.application_id)

            if c.pk not in course_map:
                course_map[c.pk] = {'course': c, 'app_ids': set()}
            course_map[c.pk]['app_ids'].add(app.application_id)

    school_list = [{'school': v['school'], 'app_ids': sorted(list(v['app_ids']))} for v in school_map.values()]
    program_list = [{'program': v['program'], 'app_ids': sorted(list(v['app_ids']))} for v in program_map.values()]
    course_list = [{'course': v['course'], 'app_ids': sorted(list(v['app_ids']))} for v in course_map.values()]

    if request.method == 'POST':
        form = ApplicantForm(request.POST, instance=applicant)
        if form.is_valid():
            form.save()
            return redirect('applicants:view', applicant_id=applicant_id)
    else:
        form = ApplicantForm(instance=applicant)

    return render(request, 'applicants/edit.html', {
        'applicant':    applicant,
        'form':         form,
        'applications': applications,
        'school_list':  school_list,
        'program_list': program_list,
        'course_list':  course_list,
    })


def applicant_delete(request, applicant_id):
    applicant = get_object_or_404(Applicant, pk=applicant_id)
    if request.method == 'POST':
        applicant.delete()
        return redirect('applicants:search')
    return redirect('applicants:edit', applicant_id=applicant_id)