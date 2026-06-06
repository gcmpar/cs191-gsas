from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Applicant
from .forms import ApplicantForm, ApplicantsQueryForm
from applications.models import Application, ApplicationTranscript
from applications.forms import ExportOptionsForm


SEARCH_FIELDS = ['applicant_id', 'first_name', 'middle_name', 'last_name', 'email', 'contact_number', 'notes']

def applicants_search(request):
    applicants = Applicant.objects.all()

    query_form = ApplicantsQueryForm(request.GET)
    if query_form.is_valid():
        query = query_form.cleaned_data.get('search')
        status = query_form.cleaned_data.get('status')

        if query:
            query_filter = Q()
            for field in SEARCH_FIELDS:
                query_filter |= Q(**{f'{field}__icontains': query})
            applicants = applicants.filter(query_filter)
        
        if status:
            applicants = applicants.filter(applicant_status=status)
    
    applicants = applicants.order_by('applicant_id')

    page_param_name = 'page'
    page_number = request.GET.get(page_param_name)
    paginator = Paginator(applicants, 15)
    page = paginator.get_page(page_number)

    query_clear = {
        field.html_name: None for field in query_form
    }
    query_clear[page_param_name] = None
    context = {
        'page_param_name': page_param_name,
        'applicants_page': page,
        'query_form': query_form,
        'query_clear': query_clear
    }
    return render(request, 'applicants/search.html', context)


def applicant_view(request, applicant_id):
    applicant    = get_object_or_404(Applicant, pk=applicant_id)
    applications = Application.objects.filter(applicant=applicant)

    school_map = {}
    program_map = {}
    course_map = {}
    
    for app in applications:
        transcripts = ApplicationTranscript.objects.filter(application=app).select_related('course').prefetch_related('course__programs__school')
        for transcript in transcripts:
            c = transcript.course
            
            if c.pk not in course_map:
                course_map[c.pk] = {'course': c, 'applications': set()}
            course_map[c.pk]['applications'].add(app)

            for p in c.programs.all():
                s = p.school
                
                if s.pk not in school_map:
                    school_map[s.pk] = {'school': s, 'applications': set()}
                school_map[s.pk]['applications'].add(app)
                
                if p.pk not in program_map:
                    program_map[p.pk] = {'program': p, 'applications': set()}
                program_map[p.pk]['applications'].add(app)

    school_list = [
        {
            'school': v['school'],
            'applications': sorted(
                list(v['applications']),
                key=lambda a: a.application_id
            )
        } for v in school_map.values()
    ]
    program_list = [
        {
            'program': v['program'],
            'applications': sorted(
                list(v['applications']),
                key=lambda a: a.application_id
            )
        } for v in program_map.values()
    ]
    course_list = [
        {
            'course': v['course'],
            'applications': sorted(
                list(v['applications']),
                key=lambda a: a.application_id
            )
        } for v in course_map.values()
    ]

    return render(request, 'applicants/view.html', {
        'applicant':    applicant,
        'applications': applications,
        'school_list':  school_list,
        'program_list': program_list,
        'course_list':  course_list,
        'export_form': ExportOptionsForm()
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
    })


def applicant_delete(request, applicant_id):
    applicant = get_object_or_404(Applicant, pk=applicant_id)
    if request.method == 'POST':
        applicant.delete()
        return redirect('applicants:search')
    return redirect('applicants:edit', applicant_id=applicant_id)