from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django_select2.conf import settings
from django_select2.views import AutoResponseView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.module_loading import import_string
from .models import Course, EquivalenceMap, EquivalenceMapCourses
from .forms import CourseForm


def courses_search(request):
    courses = Course.objects.prefetch_related('programs__school').all()
    return render(request, 'courses/search.html', {
        'courses': courses,
    })


def course_view(request, course_id):
    course = get_object_or_404(
        Course.objects.prefetch_related('programs__school'),
        pk=course_id
    )

    # Equivalence Groups this Course is part of (as a source)
    member_of_maps = EquivalenceMapCourses.objects.filter(
        course=course
    ).select_related('map__target_course').prefetch_related('map__equivalencemapcourses_set__course')

    # Equivalence Groups that map securely to this course (as target)
    equivalent_to_this = EquivalenceMap.objects.filter(
        target_course=course
    ).prefetch_related('equivalencemapcourses_set__course')

    all_courses = Course.objects.all().order_by('course_code')

    return render(request, 'courses/view.html', {
        'course': course,
        'member_of_maps': member_of_maps,
        'equivalent_to_this': equivalent_to_this,
        'all_courses': all_courses,
    })


def course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect('courses:view', course_id=course.course_id)
    else:
        form = CourseForm()
    return render(request, 'courses/add.html', {
        'form': form,
    })


def course_edit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('courses:view', course_id=course_id)
    else:
        form = CourseForm(instance=course)
    return render(request, 'courses/edit.html', {
        'course': course,
        'form':   form,
    })


def course_delete(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        return redirect('courses:search')
    return redirect('courses:edit', course_id=course_id)


@require_POST
def save_equivalence_mapping_to_course(request, course_id):
    target_course = get_object_or_404(Course, pk=course_id)
    source_ids = request.POST.getlist('source_course_ids[]')

    if not source_ids:
        messages.error(request, "Please select at least one source course.")
        return redirect('courses:view', course_id=course_id)

    source_id_set = frozenset(int(i) for i in source_ids)

    # Check for identical mapping
    for existing_map in EquivalenceMap.objects.filter(target_course=target_course).prefetch_related('equivalencemapcourses_set'):
        existing_source_ids = frozenset(
            existing_map.equivalencemapcourses_set.values_list('course_id', flat=True)
        )
        if existing_source_ids == source_id_set:
            messages.info(request, "This equivalence mapping already exists.")
            return redirect('courses:view', course_id=course_id)

    # Create the Equivalence Map
    new_map = EquivalenceMap.objects.create(target_course=target_course)
    for sid in source_id_set:
        course = get_object_or_404(Course, pk=sid)
        EquivalenceMapCourses.objects.create(map=new_map, course=course)

    messages.success(request, "Equivalence mapping created successfully.")
    return redirect('courses:view', course_id=course_id)


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