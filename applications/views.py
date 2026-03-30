from django.shortcuts import render, get_object_or_404, redirect
from applicants.models import Application, ApplicationTranscript
from courses.models import EquivalenceGroup, EquivalenceGroupMap
from .forms import ApplicationForm


def applications_search(request):
    pending = Application.objects.filter(
        application_status='processing'
    ).select_related('applicant')
    return render(request, 'applications/search.html', {
        'pending': pending,
    })


def application_view(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    applicant   = application.applicant
    transcripts = ApplicationTranscript.objects.filter(application=application).select_related('course')

    transcript_rows = []
    for t in transcripts:
        equiv_group   = EquivalenceGroup.objects.filter(course=t.course).first()
        equiv_courses = []
        if equiv_group:
            equiv_courses = EquivalenceGroupMap.objects.filter(group=equiv_group).select_related('course')
        transcript_rows.append({'transcript': t, 'equiv_courses': equiv_courses})

    return render(request, 'applications/view.html', {
        'applicant':       applicant,
        'application':     application,
        'transcript_rows': transcript_rows,
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
    transcripts = ApplicationTranscript.objects.filter(application=application).select_related('course')

    transcript_rows = []
    for t in transcripts:
        equiv_group   = EquivalenceGroup.objects.filter(course=t.course).first()
        equiv_courses = []
        if equiv_group:
            equiv_courses = EquivalenceGroupMap.objects.filter(group=equiv_group).select_related('course')
        transcript_rows.append({'transcript': t, 'equiv_courses': equiv_courses})

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
        'transcript_rows': transcript_rows,
    })


def application_delete(request, application_id):
    application = get_object_or_404(Application, pk=application_id)
    if request.method == 'POST':
        application.delete()
        return redirect('applications:search')
    return redirect('applications:edit', application_id=application_id)