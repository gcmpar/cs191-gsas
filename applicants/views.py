from django.shortcuts import render, get_object_or_404, redirect
from .models import Applicant, Application, ApplicationTranscript
from .forms import ApplicantForm


def applicants_search(request):
    applicants = Applicant.objects.all()
    return render(request, 'applicants/search.html', {
        'applicants': applicants,
    })


def applicant_view(request, applicant_id):
    applicant    = get_object_or_404(Applicant, pk=applicant_id)
    applications = Application.objects.filter(applicant=applicant)

    course_map = {}
    for app in applications:
        transcripts = ApplicationTranscript.objects.filter(application=app).select_related('course')
        for transcript in transcripts:
            c = transcript.course
            if c.pk not in course_map:
                course_map[c.pk] = {'course': c, 'app_ids': []}
            course_map[c.pk]['app_ids'].append(app.application_id)

    return render(request, 'applicants/view.html', {
        'applicant':    applicant,
        'applications': applications,
        'course_list':  list(course_map.values()),
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

    course_map = {}
    for app in applications:
        transcripts = ApplicationTranscript.objects.filter(application=app).select_related('course')
        for transcript in transcripts:
            c = transcript.course
            if c.pk not in course_map:
                course_map[c.pk] = {'course': c, 'app_ids': []}
            course_map[c.pk]['app_ids'].append(app.application_id)

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
        'course_list':  list(course_map.values()),
    })


def applicant_delete(request, applicant_id):
    applicant = get_object_or_404(Applicant, pk=applicant_id)
    if request.method == 'POST':
        applicant.delete()
        return redirect('applicants:search')
    return redirect('applicants:edit', applicant_id=applicant_id)