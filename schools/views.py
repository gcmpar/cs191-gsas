from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import School
from .forms import SchoolForm
from programs.models import Program
from applications.models import Application


def schools_search(request):
    query = request.GET.get('search', '')
    schools = School.objects.all()

    if query:
        schools = schools.filter(Q(school_name__icontains=query))

    schools = schools.order_by('school_id')
    paginator = Paginator(schools, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'schools/search.html', {
        'schools_page': page,
        'search_query': query,
    })


def school_view(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    
    programs = Program.objects.filter(school=school)
    program_search = request.GET.get('program_search', '')
    if program_search:
        programs = programs.filter(
            Q(program_name__icontains=program_search) | 
            Q(description__icontains=program_search)
        )
    program_paginator = Paginator(programs, 10)
    program_page_number = request.GET.get('program_page')
    programs_page = program_paginator.get_page(program_page_number)
    
    applications = Application.objects.filter(applicationtranscript__course__programs__school=school).select_related('applicant').distinct()
    applicant_search = request.GET.get('applicant_search', '')
    if applicant_search:
        applications = applications.filter(
            Q(applicant__first_name__icontains=applicant_search) |
            Q(applicant__last_name__icontains=applicant_search) |
            Q(application_number__icontains=applicant_search)
        )
    applicant_paginator = Paginator(applications, 10)
    applicant_page_number = request.GET.get('applicant_page')
    applicants_page = applicant_paginator.get_page(applicant_page_number)

    return render(request, 'schools/view.html', {
        'school': school,
        'programs_page': programs_page,
        'program_search': program_search,
        'applicants_page': applicants_page,
        'applicant_search': applicant_search,
    })


def school_add(request):
    if request.method == 'POST':
        form = SchoolForm(request.POST)
        if form.is_valid():
            school = form.save()
            return redirect('schools:view', school_id=school.school_id)
    else:
        form = SchoolForm()
    return render(request, 'schools/add.html', {
        'form': form,
    })


def school_edit(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    if request.method == 'POST':
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            return redirect('schools:view', school_id=school_id)
    else:
        form = SchoolForm(instance=school)
    return render(request, 'schools/edit.html', {
        'school': school,
        'form':   form,
    })


def school_delete(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    if request.method == 'POST':
        school.delete()
        return redirect('schools:search')
    return redirect('schools:edit', school_id=school_id)