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
        "link",
    )

    readonly_fields = (
        "created_date",
        "created_by",
        "modified_date",
        "modified_by",
    )

    fieldsets = (
            (
                "Overview",
                {
                    "fields": (
                        "system_id",
                        "name",
                        "division",
                        "status",
                        "link",
                        "description",
                    ),
                },
            ),
            (
                "Contacts",
                {
                    "fields": (
                        "system_owner",
                        "technology_custodian",
                        "information_custodian",
                        "business_service_owner",
                    ),
                },
            ),
            (
                "Details",
                {
                    "fields": (
                        "file_store_link",
                        "vital_records",
                        "disposal_authority",
                        "retention_and_disposal",
                        "sensitivity",
                        "system_type",
                        "ubcs",
                    ),
                },
            ),
            (
                "Meta-Data",
                {
                    "description": "Automatically captured during creation & modification",
                    "fields": (
                        "created_by",
                        "created_date",
                        "modified_by",
                        "modified_date",
                    ),
                },
            ),
        )


    search_fields = ("system_id","name", "description")

    list_filter = ("division", "status")

    # Updates meta-data upon save.
    # Populates Created_* fields only during creation
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user.email
        obj.modified_by = request.user.email
        return super().save_model(request, obj, form, change)
    
    # Retrieves read-only fields, but only allows editing of system_id during creation.
    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj=obj)
        if obj:
            readonly_fields = tuple(readonly_fields) + ('system_id', )  
        return readonly_fields