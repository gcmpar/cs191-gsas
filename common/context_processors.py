from django_select2.forms import Select2Widget
from django.forms import Form, CharField

class DummyForm(Form):
    dummy = CharField(widget=Select2Widget())

def select2_media(request):
    """
    Context processor to ensure django_select2 media is available on all pages.
    This prevents issues when select2 widgets are dynamically added via HTMX
    to pages that didn't initially have any select2 widgets.
    """
    return {
        'select2_media': DummyForm().media
    }
