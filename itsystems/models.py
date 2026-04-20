from django.db import models

from organisation.models import DepartmentUser

class ITSystemRecord(models.Model):
    """Represents a named system providing a package of functionality to
    Department staff (normally vendor or bespoke software), which is supported
    by OIM and/or an external vendor.
    """

    class Meta:
        verbose_name = "IT System"
        verbose_name_plural = "IT Systems"

    STATUS_CHOICES = (
        (1, "Production"), 
        (2, "Production (Legacy)"), 
        (3, "Decommissioned"), 
        (4, "Draft"), 
        (5, "Unknown")
    )
    SEASONALITY_CHOICES = (
        (1, "Bushfire season"),
        (2, "End of financial year"),
        (3, "Annual reporting"),
        (4, "School holidays"),
        (5, "Default"),
    )
    AVAILABILITY_CHOICES = (
        (1, "24/7/365"),
        (2, "Business hours"),
    )
    SYSTEM_TYPE_CHOICES = (
        (1, "Application"),
        (2, "Infrastructure"),
        (3, "Platform"),
    )
    SENSITIVITY_CHOICES = (
        (1, "Official"),
        (2, "Official Sensitive"),
    )

    # This probably shouldn't be hardcoded, at the very least it should reference an existing dataset.
    # Also, a lot of these are outdated and should be revised
    DIVISION_CHOICES = (
        (1,"Botanic Gardens and Parks Authority"),
        (2,"Conservation and Parks Commission"),
        (3,"DBCA Biodiversity and Conservation Science"),
        (4,"DBCA Strategy and Governance"),
        (5,"Parks and Wildlife Service"),
        (6,"Rottnest Island Authority"),
        (7,"Zoological Parks Authority"),
        (8,"Nature-based Tourism Branch"),
    )

    # ORIGINAL FIELDS:
    # --------------------
    # System ID - Name : Single Line of Text
    # Division : Choice
    # Status : Choice
    # Seasonality : Choice
    # Availability : Choice
    # Description : Multiple Lines of Text
    # Link : Hyperlink
    # File Store Link : Hyperlink
    # System Owner : Person
    # Technology Custodian : Person
    # Information Custodian : Person
    # Business Service Owner : Person
    # Vital Records : Boolean
    # Disposal Authority: Single Line of Text
    # Retention and Disposal: Single Line of Text
    # Sensitivity: Single Line of Text
    # System Type : Choice
    # UBCS: Single Line of Text
    # Modified : Date and Time
    # Created : Date and Time
    # Created By : Person
    # Modified By : Person

    # The below fields were specified based on the existing sharepoint list.
    # Any specification for default values or blank/null values was taken directly from the list.

    system_id = models.CharField(max_length=255, unique=True, verbose_name="System ID")
    name = models.CharField(max_length=255, unique=True, verbose_name="Name")
    division =  models.PositiveSmallIntegerField(choices=DIVISION_CHOICES, verbose_name= "Division")
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1 ,verbose_name= "Status")
    seasonality = models.PositiveSmallIntegerField(choices=SEASONALITY_CHOICES, default=5, verbose_name="Seasonality")
    availability = models.PositiveSmallIntegerField(choices=AVAILABILITY_CHOICES, default=2, verbose_name="Availability")
    description = models.TextField(blank=True)
    link = models.URLField(max_length=2048, null=True, blank=True, help_text="URL to web application")
    file_store_link = models.URLField(max_length=2048, null=True, blank=True, verbose_name="File Store Link", help_text="URL to file store")
    system_owner = models.ForeignKey(
        DepartmentUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="System Owner",
        related_name="systems_owner_of",
        help_text="IT system owner",
    )
    technology_custodian = models.ForeignKey(
        DepartmentUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Technology Custodian",
        related_name="systems_technology_custodian_of",
        help_text="IT system technology custodian",
    )
    information_custodian = models.ForeignKey(
        DepartmentUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Information Custodian",
        related_name="systems_information_custodian_of",
        help_text="IT system information custodian",
    )
    business_service_owner = models.ForeignKey(
        DepartmentUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Business Service Owner",
        related_name="systems_business_service_owner_of",
        help_text="IT system business service owner",
    )
    vital_records = models.BooleanField(default=False)
    disposal_authority = models.CharField(max_length=255, null=True, blank=True, verbose_name="Disposal Authority")
    retention_and_disposal = models.CharField(max_length=255, null=True, blank=True, verbose_name="Retention and Disposal")
    sensitivity =  models.PositiveSmallIntegerField(choices=SENSITIVITY_CHOICES, default=1, null = True, blank=True, verbose_name="Sensitivity")
    system_type = models.PositiveSmallIntegerField(choices = SYSTEM_TYPE_CHOICES, default = 1, null=True, blank=True, verbose_name="System Type")
    ubcs = models.CharField(max_length=255, null=True, blank=True, verbose_name="UBCS")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    created_by = models.EmailField(editable=False, verbose_name="Created By")
    modified_date = models.DateTimeField(auto_now=True, verbose_name= "Modified")
    modified_by = models.EmailField(editable=False, verbose_name="Modified By")

    # Compares itself with another instance, returning a list of differences of changes
    def compare(self, obj):
        excluded_fields = ['created_date','modified_date', 'created_by', 'modified_by', 'id', '_state']
        changes = []
        if obj:
            self_fields = self.__dict__
            obj_fields = obj.__dict__

            for self_val, obj_val in self_fields.items():
                if not (self_val in excluded_fields):
                    try:
                        if self_fields[self_val] != obj_fields[self_val]:
                            print(str(self_val) + ": " + str(obj_fields[self_val]) + " > " + str(self_fields[self_val]))
                            changes.append({"field": str(self_val), "old":self_fields[self_val], "new": obj_fields[self_val] })
                    except KeyError as e:
                        print("couldn't find " + self_val)
                        print(e)
        else:
            self_fields = self.__dict__
            for self_val in self_fields.items():
                if not (self_val[0] in excluded_fields):
                    changes.append({"field": self_val[0], "old":None, "new": self_val[1] })

        return changes

    def __str__(self):
        return self.system_id_name
    
    @property
    def system_id_name(self):
        return self.system_id + " - " + self.name