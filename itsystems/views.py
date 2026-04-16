from datetime import date, datetime
import csv

from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, View
from django.http import HttpResponse

from .models import ITSystemRecord
from .csv_handling import ExportCSV

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
    
class ExportRegisterAsCSV(View):
    def get(self, request, *args, **kwargs):
        attachment_header = 'attachment; filename="it_systems_register_' + str(date.today().isoformat()) + '_' + str(datetime.now().strftime('%H%M')) + '.csv"'
        response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition":attachment_header}
        )
        ExportCSV(writer=csv.writer(response))
        return response

class ImportRegisterChangesFromCSV(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse(content="IMPORT OK")