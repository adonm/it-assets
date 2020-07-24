from calendar import monthrange
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView
from organisation.models import DepartmentUser
from pytz import timezone
import re

from bigpicture.models import Platform
from .models import ITSystem, Incident, ChangeRequest, ChangeLog, StandardChange
from .forms import (
    ChangeRequestCreateForm, StandardChangeRequestCreateForm, ChangeRequestChangeForm,
    StandardChangeRequestChangeForm, ChangeRequestEndorseForm, ChangeRequestCompleteForm,
    EmergencyChangeRequestForm, ChangeRequestApprovalForm
)
from .reports import it_system_export, itsr_staff_discrepancies, incident_export, change_request_export, it_system_platform_export
from .utils import search_filter

TZ = timezone(settings.TIME_ZONE)


class ITSystemExport(LoginRequiredMixin, View):
    """A custom view to export all IT Systems to an Excel spreadsheet.
    """
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=it_systems_{}_{}.xlsx'.format(
            date.today().isoformat(), datetime.now().strftime('%H%M')
        )

        if 'all' in request.GET:  # Return all IT systems.
            it_systems = ITSystem.objects.all().order_by('system_id')
        else:  # Default to prod/prod-legacy IT systems only.
            it_systems = ITSystem.objects.filter(**ITSystem.ACTIVE_FILTER).order_by('system_id')

        response = it_system_export(response, it_systems)
        return response


class ITSystemDiscrepancyReport(LoginRequiredMixin, View):
    """A custom view to return a spreadsheet containing discrepancies related to IT Systems.
    """
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=it_system_discrepancies_{}_{}.xlsx'.format(
            date.today().isoformat(), datetime.now().strftime('%H%M')
        )
        it_systems = ITSystem.objects.filter(**ITSystem.ACTIVE_FILTER)
        response = itsr_staff_discrepancies(response, it_systems)
        return response


class ITSystemPlatformExport(LoginRequiredMixin, View):
    """A custom view to export IT System & their platform to an Excel spreadsheet.
    """
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=it_systems_platforms_{}_{}.xlsx'.format(
            date.today().isoformat(), datetime.now().strftime('%H%M')
        )

        if 'all' in request.GET:  # Return all IT systems.
            it_systems = ITSystem.objects.all().order_by('system_id')
        else:  # Default to prod/prod-legacy IT systems only.
            it_systems = ITSystem.objects.filter(**ITSystem.ACTIVE_FILTER).order_by('system_id')

        platforms = Platform.objects.all()
        response = it_system_platform_export(response, it_systems, platforms)
        return response


class IncidentList(LoginRequiredMixin, ListView):
    paginate_by = 20

    def get_queryset(self):
        # By default, return ongoing incidents only.
        if 'all' in self.request.GET:
            return Incident.objects.all()
        return Incident.objects.filter(resolution__isnull=True)


class IncidentDetail(LoginRequiredMixin, DetailView):
    model = Incident


class IncidentExport(LoginRequiredMixin, View):
    """A custom view to export all Incident values to an Excel spreadsheet.
    """
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=incident_register_{}_{}.xlsx'.format(date.today().isoformat(), datetime.now().strftime('%H%M'))
        incidents = Incident.objects.all()
        response = incident_export(response, incidents)
        return response


class ChangeRequestList(LoginRequiredMixin, ListView):
    model = ChangeRequest
    paginate_by = 20

    def get_queryset(self):
        from .admin import ChangeRequestAdmin
        queryset = super().get_queryset()
        if 'mine' in self.request.GET:
            email = self.request.user.email
            queryset = queryset.filter(requester__email__iexact=email)
        if 'q' in self.request.GET and self.request.GET['q']:
            q = search_filter(ChangeRequestAdmin.search_fields, self.request.GET['q'])
            queryset = queryset.filter(q)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass in any query string
        if 'q' in self.request.GET:
            context['query_string'] = self.request.GET['q']
        return context


class StandardChangeList(LoginRequiredMixin, ListView):
    model = StandardChange
    paginate_by = 100


class StandardChangeDetail(LoginRequiredMixin, DetailView):
    model = StandardChange


class ChangeRequestDetail(LoginRequiredMixin, DetailView):
    model = ChangeRequest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rfc = self.get_object()
        context['may_complete'] = (
            rfc.is_ready and
            self.request.user.email.lower() in [rfc.requester.email.lower(), rfc.implementer.email.lower()] and
            rfc.planned_end <= datetime.now().astimezone(TZ)
        )
        # Context variables that determines if determine is certain template elements are displayed.
        if rfc.requester:
            context['is_requester'] = self.request.user.email.lower() == rfc.requester.email.lower()
        if rfc.endorser:
            context['is_endorser'] = self.request.user.email.lower() == rfc.endorser.email.lower()
        else:
            context['is_endorser'] = False
        emails = []
        if rfc.requester:
            emails.append(rfc.requester.email.lower())
        if rfc.endorser:
            emails.append(rfc.endorser.email.lower())
        if rfc.implementer:
            emails.append(rfc.implementer.email.lower())
        context['user_authorised'] = self.request.user.email.lower() in [emails] or self.request.user.is_staff is True
        # Displays the 'Approve This Change' button:
        context['user_is_cab'] = self.request.user.groups.filter(name='CAB members').exists()
        return context


class ChangeRequestCreate(LoginRequiredMixin, CreateView):
    model = ChangeRequest

    def get_form_class(self):
        if 'std' in self.kwargs and self.kwargs['std']:
            return StandardChangeRequestCreateForm
        elif 'emerg' in self.kwargs and self.kwargs['emerg']:
            return EmergencyChangeRequestForm
        return ChangeRequestCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'std' in self.kwargs and self.kwargs['std']:
            context['title'] = 'Create a draft standard change request'
        elif 'emerg' in self.kwargs and self.kwargs['emerg']:
            context['title'] = 'Create an emergency change request'
        else:
            context['title'] = 'Create a draft change request'
        return context

    def form_valid(self, form):
        rfc = form.save(commit=False)
        # Set the requester as the request user (email match case-insensitive).
        if DepartmentUser.objects.filter(email__iexact=self.request.user.email).exists():
            rfc.requester = DepartmentUser.objects.get(email__iexact=self.request.user.email)
        # Set the endorser and implementer (if required).
        if self.request.POST.get('endorser_choice'):
            rfc.endorser = DepartmentUser.objects.get(pk=int(self.request.POST.get('endorser_choice')))
        if self.request.POST.get('implementer_choice'):
            rfc.implementer = DepartmentUser.objects.get(pk=int(self.request.POST.get('implementer_choice')))
        # Autocomplete normal/standard change fields.
        if 'std' in self.kwargs and self.kwargs['std']:
            rfc.change_type = 1
            rfc.endorser = rfc.standard_change.endorser
            rfc.implementation = rfc.standard_change.implementation
            rfc.description = rfc.standard_change.description
        elif 'emerg' in self.kwargs and self.kwargs['emerg']:
            rfc.change_type = 2
            if rfc.completed:  # If a completion date was recorded, set the status as "Completed".
                rfc.status = 4
            else:  # Otherwise, just set the status to "Scheduled for CAB".
                rfc.status = 2
        else:
            rfc.change_type = 0
        rfc.save()
        if 'std' in self.kwargs and self.kwargs['std']:
            # Must be carried out after save()
            rfc.it_systems.set(rfc.standard_change.it_systems.all())
        return super().form_valid(form)


class ChangeRequestChange(LoginRequiredMixin, UpdateView):
    """View for all end-user changes to an RFC: update, submit, endorse, etc.
    """
    model = ChangeRequest

    def get(self, request, *args, **kwargs):
        # Validate that the RFC may still be updated.
        rfc = self.get_object()
        if not rfc.is_draft:
            # Redirect to the object detail view.
            return HttpResponseRedirect(rfc.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def get_form_class(self):
        rfc = self.get_object()
        if rfc.is_standard_change:
            return StandardChangeRequestChangeForm
        elif rfc.is_emergency_change:
            return EmergencyChangeRequestForm
        return ChangeRequestChangeForm

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        rfc = self.get_object()
        if rfc.endorser and not rfc.is_standard_change:
            form.fields['endorser_choice'].choices = [(rfc.endorser.pk, rfc.endorser.email)]
        if rfc.implementer:
            form.fields['implementer_choice'].choices = [(rfc.implementer.pk, rfc.implementer.email)]
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rfc = self.get_object()
        if rfc.is_standard_change:
            context['title'] = 'Update draft standard change request {}'.format(rfc.pk)
        else:
            context['title'] = 'Update draft change request {}'.format(rfc.pk)
        return context

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        rfc = form.save(commit=False)
        # Set the endorser and implementer (if required).
        if self.request.POST.get('endorser_choice'):
            rfc.endorser = DepartmentUser.objects.get(pk=int(self.request.POST.get('endorser_choice')))
        if self.request.POST.get('implementer_choice'):
            rfc.implementer = DepartmentUser.objects.get(pk=int(self.request.POST.get('implementer_choice')))
        rfc.save()

        errors = False
        # If the user clicked "submit" (for approval), undertake additional form validation.
        if self.request.POST.get('submit'):
            # If a standard change, this must be selected.
            if rfc.is_standard_change and not rfc.standard_change:
                form.add_error('standard_change', 'Standard change must be selected.')
                errors = True
                # NOTE: standard change will bypass several of the business rules below.
            # Requester is required.
            if not rfc.requester:
                form.add_error('requester', 'Requester cannot be blank.')
                errors = True
            # Endorser is required.
            if not rfc.endorser:
                form.add_error('endorser_choice', 'Endorser cannot be blank.')
                errors = True
            # Implementer is required.
            if not rfc.implementer:
                form.add_error('implementer_choice', 'Implementer cannot be blank.')
                errors = True
            # Planned start is required.
            if not rfc.planned_start:
                form.add_error('planned_start', 'Planned start time must be specified.')
                errors = True
            # Planned end is required.
            if not rfc.planned_end:
                form.add_error('planned_end', 'Planned end time must be specified.')
                errors = True
            # Either implementation text or upload is required if not a standard change.
            if not rfc.is_standard_change and (not rfc.implementation and not rfc.implementation_docs):
                form.add_error('implementation', 'Implementation instructions must be specified (instructions, document upload or both).')
                form.add_error('implementation_docs', 'See above.')
                errors = True
            # Communication is required if not a standard change.
            if not rfc.is_standard_change and not rfc.communication:
                form.add_error('communication', 'Details relating to any communications must be specified (or input "NA").')
                errors = True
            # No validation errors: change the RFC status, send an email to the endorser and make a log.
            if not errors:
                # Standard change workflow: submit directly to CAB.
                if rfc.is_standard_change:
                    rfc.status = 2
                    rfc.save()
                    msg = 'Standard change request {} submitted to CAB.'.format(rfc.pk)
                    messages.success(self.request, msg)
                    log = ChangeLog(change_request=rfc, log=msg)
                    log.save()
                # Normal change workflow: submit for endorsement, then to CAB.
                else:
                    rfc.status = 1
                    rfc.save()
                    rfc.email_endorser()
                    msg = 'Change request {} submitted for endorsement by {}.'.format(rfc.pk, self.request.user.get_full_name())
                    messages.success(self.request, msg)
                    log = ChangeLog(change_request=rfc, log=msg)
                    log.save()
                    log = ChangeLog(
                        change_request=rfc, log='Request for endorsement emailed to {}.'.format(rfc.endorser.get_full_name()))
                    log.save()

        # Emergency RFC changes.
        if self.request.POST.get('save') and rfc.is_emergency_change:
            if rfc.completed:  # If a completed date is recorded, set the status automatically.
                rfc.status = 4
                rfc.save()

        if errors:
            return super().form_invalid(form)
        return super().form_valid(form)


class ChangeRequestEndorse(LoginRequiredMixin, UpdateView):
    model = ChangeRequest
    form_class = ChangeRequestEndorseForm
    template_name = 'registers/changerequest_endorse.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Endorse change request {}'.format(self.get_object().pk)
        return context

    def get(self, request, *args, **kwargs):
        # Validate that the RFC may be endorsed.
        rfc = self.get_object()
        if not rfc.is_submitted:
            # Redirect to the object detail view.
            messages.warning(self.request, 'Change request {} is not ready for endorsement.'.format(rfc.pk))
            return HttpResponseRedirect(rfc.get_absolute_url())
        if not rfc.endorser:
            messages.warning(self.request, 'Change request {} has no endorser recorded.'.format(rfc.pk))
            return HttpResponseRedirect(rfc.get_absolute_url())
        if self.request.user.email.lower() != rfc.endorser.email.lower():
            messages.warning(self.request, 'You are not the endorser for change request {}.'.format(rfc.pk))
            return HttpResponseRedirect(rfc.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        rfc = form.save()

        if self.request.POST.get('endorse'):
            # If the user clicked "Endorse", log this and change status to Scheduled.
            rfc.status = 2
            rfc.save()
            msg = 'Change request {} has been endorsed by {}; it is now scheduled to be assessed at CAB.'.format(rfc.pk, self.request.user.get_full_name())
            messages.success(self.request, msg)
            log = ChangeLog(change_request=rfc, log=msg)
            log.save()
            # Send an email to the requester.
            subject = 'Change request {} has been endorsed'.format(rfc.pk)
            detail_url = self.request.build_absolute_uri(rfc.get_absolute_url())
            text_content = """This is an automated message to let you know that change request
                {} ("{}") has been endorsed by {}, and it is now scheduled to be assessed by
                the OIM Change Advisory Board.\n
                {}\n
                """.format(rfc.pk, rfc.title, rfc.endorser.get_full_name(), detail_url)
            html_content = """<p>This is an automated message to let you know that change request
                {0} ("{1}") has been endorsed by {2}, and it is now scheduled to be assessed by
                the OIM Change Advisory Board.</p>
                <ul><li><a href="{3}">{3}</a></li></ul>
                """.format(rfc.pk, rfc.title, rfc.endorser.get_full_name(), detail_url)
            msg = EmailMultiAlternatives(subject, text_content, settings.NOREPLY_EMAIL, [rfc.requester.email])
            msg.attach_alternative(html_content, 'text/html')
            msg.send()

            # Email Change Manager(s), if they are specified.
            if User.objects.filter(groups__name='Change Managers').exists():
                changeManagers = User.objects.filter(groups__name='Change Managers')
                msg = EmailMultiAlternatives(subject, text_content, settings.NOREPLY_EMAIL, [i.email for i in changeManagers])
                msg.attach_alternative(html_content, 'text/html')
                msg.send()

        elif self.request.POST.get('reject'):
            # If the user clicked "Reject", log this and change status back to Draft.
            rfc.status = 0
            rfc.save()
            msg = 'Change request {} has been rejected by {}; status has been reset to Draft.'.format(rfc.pk, self.request.user.get_full_name())
            messages.warning(self.request, msg)
            log = ChangeLog(change_request=rfc, log=msg)
            log.save()
            # Send an email to the requester.
            subject = 'Change request {} has been rejected'.format(rfc.pk)
            detail_url = self.request.build_absolute_uri(rfc.get_absolute_url())
            text_content = """This is an automated message to let you know that change request
                {} ("{}") has been rejected by {}. Its status has been reset to "Draft" for updates
                and re-submission.\n
                {}\n
                """.format(rfc.pk, rfc.title, rfc.endorser.get_full_name(), detail_url)
            html_content = """<p>This is an automated message to let you know that change request
                {0} ("{1}") has been rejected by {2}. Its status has been reset to "Draft" for updates
                and re-submission.</p>
                <ul><li><a href="{3}">{3}</a></li></ul>
                """.format(rfc.pk, rfc.title, rfc.endorser.get_full_name(), detail_url)
            msg = EmailMultiAlternatives(subject, text_content, settings.NOREPLY_EMAIL, [rfc.requester.email])
            msg.attach_alternative(html_content, 'text/html')
            msg.send()
        return super().form_valid(form)


class ChangeRequestApproval(LoginRequiredMixin, UpdateView):
    form_class = ChangeRequestApprovalForm
    template_name = 'registers/changerequest_approval.html'
    model = ChangeRequest

    def form_valid(self, form):
        obj = self.get_object()

        if not self.request.user.groups.filter(name='CAB members').exists():
            msg = 'You are not logged in as a member of CAB, The action has been cancelled.'
            messages.warning(self.request, msg)
            return HttpResponseRedirect(reverse('change_request_detail', args=(obj.pk,)))
        else:
            if 'approve' in self.request.POST:
                logText = 'CAB member approval: change request has been approved by {}.'.format(self.request.user.get_full_name())
                changelog = ChangeLog(change_request=self.object, log=logText)
                changelog.save()
                msg = 'You have approved this change on behalf of CAB'
                messages.success(self.request, msg)
                return HttpResponseRedirect(reverse('change_request_list'))
            elif 'cancel' in self.request.POST:
                return HttpResponseRedirect(reverse('change_request_detail', args=(obj.pk,)))
            else:
                return super().form_valid(form)


class ChangeRequestExport(LoginRequiredMixin, View):
    """A custom view to export all ChangeRequest objects to an Excel spreadsheet.
    """
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=change_requests_{}_{}.xlsx'.format(date.today().isoformat(), datetime.now().strftime('%H%M'))
        rfcs = ChangeRequest.objects.all()
        response = change_request_export(response, rfcs)
        return response


class ChangeRequestCalendar(LoginRequiredMixin, ListView):
    model = ChangeRequest
    template_name = 'registers/changerequest_calendar.html'

    def get_date_param(self, **kwargs):
        if 'date' in self.kwargs:
            # Parse the date YYYY-MM-DD, then YYYY-MM.
            if re.match('^\d{4}-\d{1,2}-\d{1,2}$', self.kwargs['date']):
                return ('week', datetime.strptime(self.kwargs['date'], '%Y-%m-%d').date())
            elif re.match('^\d{4}-\d{1,2}$', self.kwargs['date']):
                return ('month', datetime.strptime(self.kwargs['date'], '%Y-%m').date())
        else:
            # If no starting date is specifed, fall back to Monday in the current week.
            return ('week', date.today() - timedelta(days=date.today().weekday()))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cal, d = self.get_date_param()
        context['start'] = d
        context['today'] = date.today()
        if cal == 'week':
            context['format'] = 'Weekly'
            context['date_last'] = d - timedelta(7)
            context['date_next'] = d + timedelta(7)
        elif cal == 'month':
            context['format'] = 'Monthly'
            context['date_last'] = (d + relativedelta(months=-1)).strftime('%Y-%m')
            context['date_next'] = (d + relativedelta(months=1)).strftime('%Y-%m')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        cal, d = self.get_date_param()
        if cal == 'week':
            # Convert week_start to a TZ-aware datetime object.
            week_start = datetime.combine(d, datetime.min.time()).astimezone(TZ)
            week_end = week_start + timedelta(days=7)
            return queryset.filter(planned_start__range=[week_start, week_end]).order_by('planned_start')
        elif cal == 'month':
            # Convert month_start to a TZ-aware datetime object.
            month_start = datetime.combine(d, datetime.min.time()).astimezone(TZ)
            last_day = monthrange(d.year, d.month)[1]
            month_end = datetime.combine(date(d.year, d.month, last_day), datetime.max.time()).astimezone(TZ)
            return queryset.filter(planned_start__range=[month_start, month_end]).order_by('planned_start')
        return queryset


class ChangeRequestComplete(LoginRequiredMixin, UpdateView):
    """View for all 'completion' changes to an RFC: success/failure/notes etc.
    """
    model = ChangeRequest
    form_class = ChangeRequestCompleteForm
    template_name = 'registers/changerequest_complete.html'

    def get(self, request, *args, **kwargs):
        rfc = self.get_object()
        # Validate that the RFC may be completed.
        if not rfc.is_ready:
            # Redirect to the detail view.
            messages.warning(self.request, 'Change request {} is not ready for completion.'.format(rfc.pk))
            return HttpResponseRedirect(rfc.get_absolute_url())
        # Business rule: only the implementer or requester may complete the change.
        if self.request.user.email.lower() not in [rfc.requester.email.lower(), rfc.implementer.email.lower()]:
            messages.warning(self.request, 'You are not authorised to complete change request {}.'.format(rfc.pk))
            return HttpResponseRedirect(rfc.get_absolute_url())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Complete/finalise change request {}'.format(self.get_object().pk)
        return context

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def form_valid(self, form):
        rfc = form.save()
        d = form.cleaned_data
        log = ChangeLog(change_request=rfc)

        # Change the RFC status and make a log.
        if d['outcome'] == 'complete':
            rfc.status = 4
            log.log = 'Change {} was marked "Completed successfully" by {}.'.format(rfc.pk, self.request.user.get_full_name())
            messages.success(self.request, 'Change request {} was been marked as completed.'.format(rfc.pk))
        elif d['outcome'] == 'rollback':
            rfc.status = 5
            log.log = 'Change {} was marked "Undertaken and rolled back" by {}.'.format(rfc.pk, self.request.user.get_full_name())
            messages.info(self.request, 'Change request {} was been marked as rolled back.'.format(rfc.pk))
        elif d['outcome'] == 'cancelled':
            rfc.status = 6
            log.log = 'Change {} was marked "Cancelled" by {}.'.format(rfc.pk, self.request.user.get_full_name())
            messages.info(self.request, 'Change request {} was been marked as cancelled.'.format(rfc.pk))
        rfc.save()
        log.save()

        return super().form_valid(form)


class ITSystemRiskAssessmentList(LoginRequiredMixin, ListView):
    model = ITSystem
    paginate_by = 20
    template_name = 'registers/riskassessment_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'IT System Risk Assessments'
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        # Default to prod/prod-legacy IT systems only.
        qs = qs.filter(**ITSystem.ACTIVE_FILTER).order_by('system_id')
        return qs


class ITSystemRiskAssessmentDetail(LoginRequiredMixin, DetailView):
    model = ITSystem
    template_name = 'registers/riskassessment_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        context['page_title'] = 'IT System Risk Assessment - {}'.format(obj)
        context['obj_dependencies'] = obj.dependencies.order_by('category')
        context['itsystem_ct'] = ContentType.objects.get_for_model(obj)
        context['dependency_ct'] = ContentType.objects.get(app_label='bigpicture', model='dependency')

        # Get 'maximum' risks in each category for the IT system.
        max_risks = obj.get_risk_category_maxes()
        context['top_function_risk'] = max_risks['Critical function']
        context['top_traffic_risk'] = max_risks['Traffic']
        context['top_access_risk'] = max_risks['Access']
        context['top_vuln_risk'] = max_risks['Vulnerability']
        context['top_backup_risk'] = max_risks['Backups']
        context['top_support_risk'] = max_risks['Support']
        context['top_os_risk'] = max_risks['Operating System']
        context['top_plan_risk'] = max_risks['Contingency plan']

        return context
