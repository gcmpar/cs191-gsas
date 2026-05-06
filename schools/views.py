from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from .models import School
from .forms import SchoolForm, SchoolsFilterForm, RelatedProgramsFilterForm, RelatedAppsFilterForm
from programs.models import Program
from applications.models import Application


def schools_search(request):
    schools = School.objects.all()

    query_form = SchoolsFilterForm(request.GET)
    if query_form.is_valid():
        query = query_form.cleaned_data.get('search')

        if query:
            schools = schools.filter(Q(school_name__icontains=query))

    schools = schools.order_by('school_id')
    paginator = Paginator(schools, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'schools/search.html', {
        'schools_page': page,
        'query_form': query_form,
        'query_clear': {
            field.html_name: None for field in query_form
        }
    })


def school_view(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    
    programs = Program.objects.filter(school=school)
    programs_query_form = RelatedProgramsFilterForm(request.GET, prefix='programs')
    if programs_query_form.is_valid():
        programs_query = programs_query_form.cleaned_data.get('search')
        
        if programs_query:
            programs = programs.filter(
                Q(program_name__icontains=programs_query) | 
                Q(description__icontains=programs_query)
            )
    program_paginator = Paginator(programs, 10)
    program_page_number = request.GET.get('programs_page')
    programs_page = program_paginator.get_page(program_page_number)
    
    applications = Application.objects.filter(applicationtranscript__course__programs__school=school).select_related('applicant').distinct()
    apps_query_form = RelatedAppsFilterForm(request.GET, prefix='apps')
    if apps_query_form.is_valid():
        apps_query = apps_query_form.cleaned_data.get('search')
        
        if apps_query:
            applications = applications.filter(
                Q(applicant__first_name__icontains=apps_query) |
                Q(applicant__last_name__icontains=apps_query) |
                Q(application_number__icontains=apps_query) |
                Q(program__icontains=apps_query)
        )
    apps_paginator = Paginator(applications, 10)
    apps_page_number = request.GET.get('apps_page')
    apps_page = apps_paginator.get_page(apps_page_number)

    return render(request, 'schools/view.html', {
        'school': school,
        'programs_page': programs_page,
        'programs_query_form': programs_query_form,
        'apps_page': apps_page,
        'apps_query_form': apps_query_form,
        
        'programs_query_clear': {
            field.html_name: None for field in programs_query_form
        },
        'apps_query_clear': {
            field.html_name: None for field in apps_query_form
        }
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