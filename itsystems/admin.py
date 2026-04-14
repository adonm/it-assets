from django.contrib import admin

from .models import ITSystemRecord

@admin.register(ITSystemRecord)
class ITSystemRecordAdmin(admin.ModelAdmin):
    list_display = (
        "system_id_name",
        "status",
        "division",
        "business_service_owner",
        "system_owner",
        "technology_custodian",
        "information_custodian",
    )

    readonly_fields = (
        "created_date",
        "created_by",
        "modified_date",
        "modified_by",
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user.email
        obj.modified_by = request.user.email
        return super().save_model(request, obj, form, change)