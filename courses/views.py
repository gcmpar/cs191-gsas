import json
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils.module_loading import import_string
from django_select2.conf import settings
from django_select2.views import AutoResponseView
from .models import Course, EquivalenceMap, EquivalenceMapCourses
from .forms import (
    CourseForm,
    CourseProgramFormSet,
    EquivMapInlineFormSet,
    NewEquivMappingFormSet,
)


def courses_search(request):
    from schools.models import School
    from programs.models import Program as ProgramModel
    query = request.GET.get('search', '')
    filter_school = request.GET.get('school', '')
    filter_program = request.GET.get('program', '')

    courses = Course.objects.prefetch_related('programs__school').all()

    if query:
        from django.db.models import Q
        courses = courses.filter(
            Q(course_code__icontains=query) |
            Q(course_name__icontains=query) |
            Q(description__icontains=query)
        )
    if filter_school:
        courses = courses.filter(programs__school__school_id=filter_school).distinct()
    if filter_program:
        courses = courses.filter(programs__program_id=filter_program).distinct()

    courses = courses.order_by('course_id')
    paginator = Paginator(courses, 15)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    all_schools = School.objects.all().order_by('school_name')
    all_programs = ProgramModel.objects.select_related('school').order_by('school__school_name', 'program_name')

    return render(request, 'courses/search.html', {
        'courses_page': page,
        'search_query': query,
        'filter_school': filter_school,
        'filter_program': filter_program,
        'all_schools': all_schools,
        'all_programs': all_programs,
    })


def course_general_view(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related('programs__school'),
        pk=course_id,
    )
    return render(request, 'courses/view_general.html', {
        'course': course,
        'active_tab': 'general',
        'mode': 'view',
    })


def course_general_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)

    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        prog_formset = CourseProgramFormSet(request.POST, prefix='programs')

        if form.is_valid() and prog_formset.is_valid():
            form.save()
            programs = [
                f.cleaned_data['program']
                for f in prog_formset
                if f.cleaned_data.get('program') and not f.cleaned_data.get('DELETE')
            ]
            course.programs.set(programs)
            return redirect('courses:view', course_id=course_id)
    else:
        form = CourseForm(instance=course)
        initial = [{'program': p} for p in course.programs.all()]
        prog_formset = CourseProgramFormSet(prefix='programs', initial=initial)

    return render(request, 'courses/edit_general.html', {
        'course': course,
        'form': form,
        'prog_formset': prog_formset,
        'active_tab': 'general',
        'mode': 'edit',
    })


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

    return render(request, 'courses/view_equiv.html', {
        'course': course,
        'as_target': as_target,
        'as_source': as_source,
        'active_tab': 'equiv',
        'mode': 'view',
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

    return render(request, 'courses/edit_equiv.html', {
        'course': course,
        'map_formsets': map_formsets,
        'new_map_formset': new_map_formset,
        'active_tab': 'equiv',
        'mode': 'edit',
    })


@require_POST
def delete_equivalence_map(request, course_id, map_id):
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
            return redirect('courses:view', course_id=course.course_id)
    else:
        form = CourseForm()
    return render(request, 'courses/add.html', {'form': form})


def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('courses:search')
    return redirect('courses:edit', course_id=course_id)


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