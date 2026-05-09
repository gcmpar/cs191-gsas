from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils.module_loading import import_string
from django_select2.conf import settings
from django_select2.views import AutoResponseView
from django.db.models import Q
from .models import Course, EquivalenceMap, EquivalenceMapCourses
from .forms import (
    CourseForm,
    CoursesQueryForm,
    ProgramRowForm,
    EquivMapInlineFormSet,
    NewEquivMappingFormSet,
)

PROGRAMS_PARAM_PREFIX = 'programs_'

def programs_param_form_prefix(index):
    return f'{PROGRAMS_PARAM_PREFIX}{index}_'
def programs_param_index(param):
    rest = param[len(PROGRAMS_PARAM_PREFIX):]
    index = int(rest.split('_')[0])
    return index
def get_program_forms_from_request(request):
    indices = set()
    for param in request.POST.keys():
        if param.startswith(PROGRAMS_PARAM_PREFIX):
            index = programs_param_index(param)
            indices.add(index)
    program_forms = [ProgramRowForm(request.POST, prefix=programs_param_form_prefix(i)) for i in indices]
    next_index = max(indices)+1 if indices else 0

    return program_forms, next_index
def get_program_forms_from_course(course):
    program_forms = []
    for i, program in enumerate(course.programs.all()):
        program_form = ProgramRowForm(prefix=programs_param_form_prefix(i), initial={'program': program})
        program_forms.append(program_form)
    
    if len(program_forms) == 0:
        program_forms.append(ProgramRowForm(prefix=programs_param_form_prefix(0)))
    
    next_index = len(program_forms)

    return program_forms, next_index




def courses_search(request):
    courses = Course.objects.prefetch_related('programs__school').all()

    query_form = CoursesQueryForm(request.GET)
    if query_form.is_valid():
        query = query_form.cleaned_data.get('search')
        school = query_form.cleaned_data.get('school')
        program = query_form.cleaned_data.get('program')
        
        if query:
            courses = courses.filter(
                Q(course_code__icontains=query) | Q(course_name__icontains=query) | Q(description__icontains=query)
            )
        if program:
            courses = courses.filter(programs=program)
        if school:
            courses = courses.filter(programs__school=school)

    courses = courses.order_by('course_code')

    page_param_name = 'page'
    page_number = request.GET.get(page_param_name)
    paginator = Paginator(courses, 15)
    page = paginator.get_page(page_number)

    query_clear = {
        field.html_name: None for field in query_form
    }
    query_clear[page_param_name] = None

    return render(request, 'courses/search.html', {
        'page_param_name': page_param_name,
        'courses_page': page,
        'search_query': query,
        'query_form': query_form,
        'query_clear': query_clear
    })


def course_general_view(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related('programs__school'),
        pk=course_id,
    )
    return render(request, 'courses/general_view.html', {
        'course': course,
    })


def course_general_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)

        program_forms, next_index = get_program_forms_from_request(request)

        if form.is_valid() and all(program_form.is_valid() for program_form in program_forms):
            form.save()

            course.programs.set([
                program_form.cleaned_data['program'].program_id
                for program_form in program_forms
                if program_form.cleaned_data.get('program')
            ])
        
            return redirect('courses:general_view', course_id=course_id)
    else:
        form = CourseForm(instance=course)
        program_forms, next_index = get_program_forms_from_course(course)

    return render(request, 'courses/general_edit.html', {
        'course': course,
        'form': form,
        'program_forms': program_forms,
        'next_index': next_index,
    })
def course_general_program_form(request):
    index = int(request.GET.get('index', 0))

    program_form = ProgramRowForm(prefix=programs_param_form_prefix(index))
    return render(
        request,
        'courses/partials/program_form.html',
        {
            'program_form': program_form,
        }
    )

def course_equiv_view(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related('programs__school'),
        pk=course_id,
    )
    as_target = EquivalenceMap.objects.filter(
        target_course=course
    ).prefetch_related('equivalencemapcourses_set__course')

    as_source = EquivalenceMapCourses.objects.filter(
        course=course
    ).select_related('map__target_course').prefetch_related('map__equivalencemapcourses_set__course')

    return render(request, 'courses/equiv_view.html', {
        'course': course,
        'as_target': as_target,
        'as_source': as_source,
    })


def course_equiv_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    existing_maps = EquivalenceMap.objects.filter(
        target_course=course
    ).prefetch_related('equivalencemapcourses_set__course').order_by('map_id')

    if request.method == 'POST':
        all_valid = True
        bound_map_formsets = []

        for map_obj in existing_maps:
            prefix = f'map_{map_obj.pk}'
            fs = EquivMapInlineFormSet(request.POST, instance=map_obj, prefix=prefix)
            bound_map_formsets.append((map_obj, fs))
            if not fs.is_valid():
                all_valid = False

        new_fs = NewEquivMappingFormSet(request.POST, prefix='new_map')
        if not new_fs.is_valid():
            all_valid = False

        if all_valid:
            for map_obj, fs in bound_map_formsets:
                fs.save()

            new_courses = [
                f.cleaned_data['course']
                for f in new_fs
                if f.cleaned_data.get('course') and not f.cleaned_data.get('DELETE')
            ]
            if new_courses:
                new_map = EquivalenceMap.objects.create(target_course=course)
                for c in new_courses:
                    EquivalenceMapCourses.objects.create(map=new_map, course=c)

            messages.success(request, 'Equivalence mappings saved.')
            return redirect('courses:equiv_view', course_id=course_id)

        map_formsets = bound_map_formsets
        new_map_formset = new_fs
    else:
        map_formsets = [
            (map_obj, EquivMapInlineFormSet(instance=map_obj, prefix=f'map_{map_obj.pk}'))
            for map_obj in existing_maps
        ]
        new_map_formset = NewEquivMappingFormSet(prefix='new_map')

    return render(request, 'courses/equiv_edit.html', {
        'course': course,
        'map_formsets': map_formsets,
        'new_map_formset': new_map_formset,
    })


@require_POST
def course_equiv_delete(request, course_id, map_id):
    course = get_object_or_404(Course, pk=course_id)
    mapping = get_object_or_404(EquivalenceMap, pk=map_id, target_course=course)
    mapping.delete()
    messages.success(request, 'Mapping deleted.')
    return redirect('courses:equiv_edit', course_id=course_id)


def course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect('courses:general_view', course_id=course.course_id)
    else:
        form = CourseForm()
    return render(request, 'courses/add.html', {'form': form})


def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('courses:search')
    return redirect('courses:general_edit', course_id=course_id)


class CoursesGroupedAutoResponseView(AutoResponseView):
    def get(self, request, *args, **kwargs):
        self.widget = self.get_widget_or_404()
        self.term = kwargs.get('term', request.GET.get('term', ''))
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        grouped = {}
        for course in context['object_list']:
            for program in course.programs.all():
                group_name = f'{program.school.school_name} - {program.program_name}'
                if group_name not in grouped:
                    grouped[group_name] = []
                grouped[group_name].append(self.widget.result_from_instance(course, request))

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
        return Course.objects.prefetch_related('programs__school')