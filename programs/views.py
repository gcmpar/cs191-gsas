from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from applications.models import Application
from courses.models import Course
from .models import Program
from .forms import ProgramForm


def programs_search(request):
    from schools.models import School
    query = request.GET.get('search', '')
    filter_school = request.GET.get('school', '')

    programs = Program.objects.select_related('school').all()

    if query:
        programs = programs.filter(
            Q(program_name__icontains=query) | Q(description__icontains=query)
        )
    if filter_school:
        programs = programs.filter(school__school_id=filter_school)

    programs = programs.order_by('program_id')
    paginator = Paginator(programs, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    all_schools = School.objects.all().order_by('school_name')

    return render(request, 'programs/search.html', {
        'programs_page': page,
        'search_query': query,
        'filter_school': filter_school,
        'all_schools': all_schools,
    })


def program_view(request, program_id):
    program = get_object_or_404(Program.objects.select_related('school'), pk=program_id)
    
    courses = Course.objects.filter(programs=program)
    course_search = request.GET.get('course_search', '')
    if course_search:
        courses = courses.filter(
            Q(course_code__icontains=course_search) |
            Q(course_name__icontains=course_search) |
            Q(description__icontains=course_search)
        )
    course_paginator = Paginator(courses, 10)
    course_page_number = request.GET.get('course_page')
    courses_page = course_paginator.get_page(course_page_number)
    
    applications = Application.objects.filter(applicationtranscript__course__programs=program).select_related('applicant').distinct()
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
    
    return render(request, 'programs/view.html', {
        'program': program,
        'courses_page': courses_page,
        'course_search': course_search,
        'applicants_page': applicants_page,
        'applicant_search': applicant_search,
    })


def program_add(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            return redirect('programs:view', program_id=program.program_id)
    else:
        form = ProgramForm()
    return render(request, 'programs/add.html', {
        'form': form,
    })


def program_edit(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect('programs:view', program_id=program_id)
    else:
        form = ProgramForm(instance=program)
    return render(request, 'programs/edit.html', {
        'program': program,
        'form':    form,
    })


def program_delete(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    if request.method == 'POST':
        program.delete()
        return redirect('programs:search')
    return redirect('programs:edit', program_id=program_id)