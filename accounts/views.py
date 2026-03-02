from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class RedirectorLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        
        else:
            return reverse_lazy('applicants:search')