from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import JsonResponse, Http404
from django.utils.module_loading import import_string
from django_select2.conf import settings
from django_select2.views import AutoResponseView
from django.db.models import Q
from .models import Course, EquivalenceMap, EquivalenceMapCourses
from .forms import (
    CourseForm,
    CoursesQueryForm,
    ProgramRowForm,
    EquivRowForm
)

PROGRAMS_PARAM_PREFIX = 'programs_'
EQUIV_PARAM_PREFIX = 'equiv_'

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

def equiv_param_form_prefix(map_id, index):
    return f'{EQUIV_PARAM_PREFIX}{map_id}_{index}_'
def equiv_param_id_index(param):
    rest = param[len(EQUIV_PARAM_PREFIX):]
    rest_split = rest.split('_')

    map_id = int(rest_split[0])
    index = int(rest_split[1])

    return map_id, index
def get_equiv_snapshot_from_request(request):
    indices_map = {}
    for param in request.POST.keys():
        if param.startswith(EQUIV_PARAM_PREFIX):
            map_id, index = equiv_param_id_index(param)
            if map_id not in indices_map:
                indices_map[map_id] = set()
            indices_map[map_id].add(index)
    
    equiv_snapshot = {}
    for map_id, indices in indices_map.items():
        equiv_snapshot[map_id] = {
            'equiv_forms': [
                EquivRowForm(request.POST, prefix=equiv_param_form_prefix(map_id, i))
                for i in indices
            ],
            'next_index': max(indices)+1 if indices else 0
        }
    return equiv_snapshot
def get_equiv_snapshot_from_course(course):
    existing_maps = EquivalenceMap.objects.filter(
        target_course=course
    ).prefetch_related(
        'equivalencemapcourses_set__course'
    ).order_by('map_id')

    equiv_snapshot = {}

    for equiv_map in existing_maps:
        equiv_forms = []
        for i, entry in enumerate(equiv_map.equivalencemapcourses_set.all()):
            equiv_forms.append(
                EquivRowForm(
                    prefix=equiv_param_form_prefix(equiv_map.map_id, i),
                    initial={
                        'course': entry.course
                    }
                )
            )

        if len(equiv_forms) == 0:
            equiv_forms.append(EquivRowForm(prefix=equiv_param_form_prefix(equiv_map.map_id, 0)))

        equiv_snapshot[equiv_map.map_id] = {
            'equiv_forms': equiv_forms,
            'next_index': len(equiv_forms)
        }
    return equiv_snapshot



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
                program_form.cleaned_data['program']
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

    if request.method == 'POST':
        equiv_snapshot = get_equiv_snapshot_from_request(request)

        if all(
            form.is_valid()
            for info in equiv_snapshot.values()
            for form in info['equiv_forms']
        ):
            raw_snapshot = {
                map_id: {
                    form.cleaned_data['course'].course_id
                    for form in info['equiv_forms']
                    if form.cleaned_data.get('course')
                } for map_id, info in equiv_snapshot.items()
            }

            for map_id, course_ids in raw_snapshot.items():
                # Check validity first.
                if EquivalenceMap.objects.filter(
                    pk=map_id,
                    target_course=course,
                ).first() is None:
                    raise Http404()

                equiv_map = get_object_or_404(
                    EquivalenceMap,
                    pk=map_id,
                    target_course=course,
                )

                # Remove missing courses from equiv map
                EquivalenceMapCourses.objects.filter(map=equiv_map).exclude(course_id__in=course_ids).delete()
                
                # Add new courses
                existing_course_ids = set(EquivalenceMapCourses.objects.filter(map=equiv_map).values_list('course_id', flat=True))
                EquivalenceMapCourses.objects.bulk_create([
                    EquivalenceMapCourses(map=equiv_map, course_id=c_id)
                    for c_id in course_ids
                    if c_id not in existing_course_ids
                ])

            # Remove empty maps
            EquivalenceMap.objects.filter(
                target_course=course,
                equivalencemapcourses__isnull=True
            ).delete()

            # Remove deleted maps
            submitted_map_ids = set(raw_snapshot.keys())
            EquivalenceMap.objects.filter(
                target_course=course
            ).exclude(
                map_id__in=submitted_map_ids
            ).delete()

            return redirect('courses:equiv_view', course_id=course_id)
                
    else:
        equiv_snapshot = get_equiv_snapshot_from_course(course)

    return render(request, 'courses/equiv_edit.html', {
        'course': course,
        'equiv_snapshot': equiv_snapshot
    })
def course_equiv_map(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    equiv_map = EquivalenceMap.objects.create(target_course=course)

    return render(
        request,
        'courses/partials/equiv_map.html',
        {
            'map_id': equiv_map.map_id,
            'equiv_forms': []
        }
    )
def course_equiv_form(request, map_id):
    index = int(request.GET.get('index', 0))

    equiv_map = get_object_or_404(EquivalenceMap, pk=map_id)
    equiv_form = EquivRowForm(prefix=equiv_param_form_prefix(equiv_map.map_id, index))
    return render(
        request,
        'courses/partials/equiv_form.html',
        {
            'equiv_form': equiv_form,
        }
    )


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