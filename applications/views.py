from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Application, ApplicationTranscript
from .forms import ApplicationForm
from courses.models import EquivalenceMapCourses, EquivalenceMap


SEARCH_FIELDS = ['application_number', 'program', 'study_load', 'notes']


def get_transcript_entries(application):
    transcript_entries = []

    transcripts = ApplicationTranscript.objects.filter(application=application).select_related('course')
    for t in transcripts:
        
        equivalences = []

        # Probe which equivalence maps this course is part of.
        associated_entries = EquivalenceMapCourses.objects.filter(course=t.course).select_related('map')
        for a_entry in associated_entries:
            
            map = a_entry.map

            # Get the courses of this particular map.
            map_entries = EquivalenceMapCourses.objects.filter(map=map).select_related('course')

            equivalences.append({
                'group': [entry.course for entry in map_entries],
                'target_course': map.target_course,
                'map': map,
            })

        transcript_entries.append({'transcript': t, 'equivalences': equivalences})

    return transcript_entries


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

    return render(request, 'applications/view.html', {
        'applicant':       applicant,
        'application':     application,
        'transcript_entries': get_transcript_entries(application),
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
        if form.is_valid():
            form.save()
            return redirect('applications:view', application_id=application_id)
    else:
        form = ApplicationForm(instance=application)

    return render(request, 'applications/edit.html', {
        'applicant':       applicant,
        'application':     application,
        'form':            form,
        'transcript_entries': get_transcript_entries(application),
    })


def application_delete(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    if request.method == 'POST':
        application.delete()
        return redirect('applications:search')
    return redirect('applications:edit', application_id=application_id)