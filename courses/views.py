from django.shortcuts import render, get_object_or_404, redirect
from django_select2.conf import settings
from django_select2.views import AutoResponseView
from django.http import JsonResponse
from django.utils.module_loading import import_string
from .models import Course
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
    return render(request, 'courses/view.html', {
        'course': course,
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