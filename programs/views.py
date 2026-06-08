from django_select2.views import AutoResponseView
from django.http import JsonResponse
from django.utils.module_loading import import_string
from django_select2.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from applications.models import Application
from courses.models import Course
from .models import Program
from .forms import ProgramForm, ProgramsQueryForm, RelatedCoursesQueryForm, RelatedAppsQueryForm


def programs_search(request):
    programs = Program.objects.select_related('school').all()

    query_form = ProgramsQueryForm(request.GET)
    if query_form.is_valid():
        query = query_form.cleaned_data.get('search')
        school = query_form.cleaned_data.get('school')
        
        if query:
            programs = programs.filter(
                Q(program_name__icontains=query) | Q(description__icontains=query)
            )
        if school:
            programs = programs.filter(school=school)

    programs = programs.order_by('program_id')

    page_param_name = 'page'
    page_number = request.GET.get(page_param_name)
    paginator = Paginator(programs, 15)
    page = paginator.get_page(page_number)

    query_clear = {
        field.html_name: None for field in query_form
    }
    query_clear[page_param_name] = None

    return render(request, 'programs/search.html', {
        'page_param_name': page_param_name,
        'programs_page': page,
        'query_form': query_form,
        'query_clear': query_clear
    })


def program_view(request, program_id):
    program = get_object_or_404(Program.objects.select_related('school'), pk=program_id)
    
    courses = Course.objects.filter(programs=program)
    courses_query_form = RelatedCoursesQueryForm(request.GET, prefix='courses')
    if courses_query_form.is_valid():
        courses_query = courses_query_form.cleaned_data.get('search')

        if courses_query:
            courses = courses.filter(
                Q(course_code__icontains=courses_query) |
                Q(course_name__icontains=courses_query) |
                Q(description__icontains=courses_query)
            )
    courses_page_param_name = 'courses_page'
    courses_page_number = request.GET.get(courses_page_param_name)
    courses_paginator = Paginator(courses, 10)
    courses_page = courses_paginator.get_page(courses_page_number)

    courses_query_clear = {
        field.html_name: None for field in courses_query_form
    }
    courses_query_clear[courses_page_param_name] = None
    
    applications = Application.objects.filter(applicationtranscript__course__programs=program).select_related('applicant').distinct()
    apps_query_form = RelatedAppsQueryForm(request.GET, prefix='apps')
    if apps_query_form.is_valid():
        apps_query = apps_query_form.cleaned_data.get('search')

        if apps_query:
            applications = applications.filter(
                Q(applicant__first_name__icontains=apps_query) |
                Q(applicant__last_name__icontains=apps_query) |
                Q(application_number__icontains=apps_query) |
                Q(program__icontains=apps_query)
        )
    apps_page_param_name = 'apps_page'
    apps_page_number = request.GET.get(apps_page_param_name)
    apps_paginator = Paginator(applications, 10)
    apps_page = apps_paginator.get_page(apps_page_number)

    apps_query_clear = {
        field.html_name: None for field in apps_query_form
    }
    apps_query_clear[apps_page_param_name] = None
    
    return render(request, 'programs/view.html', {
        'program': program,

        'courses_page_param_name': courses_page_param_name,
        'courses_page': courses_page,
        'courses_query_form': courses_query_form,

        'apps_page_param_name': apps_page_param_name,
        'apps_page': apps_page,
        'apps_query_form': apps_query_form,

        'courses_query_clear': courses_query_clear,
        'apps_query_clear': apps_query_clear,
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


class ProgramsGroupedAutoResponseView(AutoResponseView):
    def get(self, request, *args, **kwargs):
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get('term', request.GET.get('term', ''))
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        grouped = {}
        for program in context['object_list']:
            group_name = program.school.school_name
            if group_name not in grouped:
                grouped[group_name] = []
            grouped[group_name].append(self.widget.result_from_instance(program, request))

        return JsonResponse(
            {
                'results': [
                    {'text': group_name, 'children': items}
                    for group_name, items in grouped.items()
                ],
                'more': context['page_obj'].has_next(),
            },
            encoder=import_string(settings.SELECT2_JSON_ENCODER),
        )
    def get_queryset(self):
        queryset = Program.objects.select_related('school')
        school_id = self.request.GET.get('school')
        if school_id:
            queryset = queryset.filter(
                school__isnull=False,
                school__school_id=school_id
            )
        return queryset