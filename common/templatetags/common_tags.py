from django import template


register = template.Library()

NAVBAR_BUTTONS = {
    'home': {
        'url': 'home:home',
        'text': 'Home',
    },
    'applicants': {
        'url': 'applicants:search',
        'text': 'Applicants',
    },
    'applications': {
        'url': 'applications:search',
        'text': 'Applications',
    },
    'schools': {
        'url': 'schools:search',
        'text': 'Schools',
    },
    'programs': {
        'url': 'programs:search',
        'text': 'Programs',
    },
    'courses': {
        'url': 'courses:search',
        'text': 'Courses',
    },
    'application': {
        'url': 'applications:batch_import_history',
        'text': 'Imports',
    },
}


@register.inclusion_tag('navbar.html', takes_context=True)
def render_navbar(context):
    request = context['request']

    buttons = NAVBAR_BUTTONS.copy()

    # Remove values from button if user doesn't match permission.
    # (currently no such checks here)

    return {
        'request': request,
        'user': context.get('user'),
        'perms': context.get('perms'),

        'navbar_buttons': buttons,
    }


@register.simple_tag(takes_context=True)
def param_replace(context, param_name, value):
    """
    Returns a URL-encoded querystring for the current page,
    updating the specified parameter with the given value.
    """
    request = context.get('request')
    if not request:
        return f"?{param_name}={value}"
    
    dict_ = request.GET.copy()
    dict_[param_name] = value
    return f"?{dict_.urlencode()}"