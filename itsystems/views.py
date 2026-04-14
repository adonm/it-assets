from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import ITSystemRecord

class ITSystemsRegister(LoginRequiredMixin, ListView):
    template_name = "itsystems/it_systems_register.html"
    model = ITSystemRecord
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_title"] = "Office of Information Management"
        context["site_acronym"] = "OIM"
        context["page_title"] = "IT Systems Register"
        return super().get_context_data(**kwargs)