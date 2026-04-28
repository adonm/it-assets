from django.db import models

from organisation.models import DepartmentUser

class Division(models.Model):
    class Meta:
        verbose_name = "Division"
        verbose_name_plural = "Divisions"

    name = models.CharField(max_length=255, unique=True, verbose_name="Name")

    def __str__(self):
        return self.name


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

    system_id = models.CharField(max_length=255, unique=True, verbose_name="System ID")
    name = models.CharField(max_length=255, verbose_name="Name")
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1 ,verbose_name= "Status")
    division =  models.ForeignKey(
        Division,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Division",
        related_name="assigned_division",
        help_text="Division",
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
    seasonality = models.PositiveSmallIntegerField(choices=SEASONALITY_CHOICES, default=5, verbose_name="Seasonality")
    availability = models.PositiveSmallIntegerField(choices=AVAILABILITY_CHOICES, default=2, verbose_name="Availability")
    link = models.URLField(max_length=2048, null=True, blank=True, help_text="URL to web application")
    description = models.TextField(null=True, blank=True)
    file_store_link = models.URLField(max_length=2048, null=True, blank=True, verbose_name="File Store Link", help_text="URL to file store")
    vital_records = models.BooleanField(default=False)
    disposal_authority = models.CharField(max_length=255, null=True, blank=True, verbose_name="Disposal Authority")
    retention_and_disposal = models.CharField(max_length=255, null=True, blank=True, verbose_name="Retention and Disposal")
    ubcs = models.CharField(max_length=255, null=True, blank=True, verbose_name="UBCS")
    sensitivity =  models.PositiveSmallIntegerField(choices=SENSITIVITY_CHOICES, default=1, null = True, blank=True, verbose_name="Sensitivity")
    system_type = models.PositiveSmallIntegerField(choices = SYSTEM_TYPE_CHOICES, default = 1, null=True, blank=True, verbose_name="System Type")

    # Meta-Data fields
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    created_by = models.EmailField(editable=False, verbose_name="Created By")
    modified_date = models.DateTimeField(auto_now=True, verbose_name= "Modified")
    modified_by = models.EmailField(editable=False, verbose_name="Modified By")

    # Compares itself with another instance, returning a list of differences of changes
    def compare(self, obj):
        excluded_fields = ['created_date','modified_date', 'created_by', 'modified_by', 'id', '_state', 'system_id']
        changes = []
        if obj:
            self_fields = self.__dict__
            obj_fields = obj.__dict__

            for self_val, obj_val in self_fields.items():
                if self_val not in excluded_fields:
                    try:
                        #  obj_fileds' 'Or None' accounts for empty string values, self fields' 'Or None' allows for Boolean 'False' equivalency
                        if (self_fields[self_val] or None) != (obj_fields[self_val] or None):
                            changes.append({"field": str(self_val), "old":self_fields[self_val], "new": obj_fields[self_val] })
                    except KeyError as e:
                        print("couldn't find " + self_val)
                        print(e)
        else:
            self_fields = self.__dict__
            for self_val in self_fields.items():
                if self_val[0] not in excluded_fields:
                    changes.append({"field": self_val[0], "old":None, "new": self_val[1] })

        return changes

    def __str__(self):
        return self.system_id_name
    
    def save(self, *args, **kwargs):
        if self.description == '':
            self.description = None
        if self.link == '':
            self.link = None
        if self.file_store_link == '':
            self.file_store_link = None
        if self.disposal_authority == '':
            self.disposal_authority = None
        if self.retention_and_disposal == '':
            self.retention_and_disposal = None
        if self.ubcs == '':
            self.ubcs = None

        super(ITSystemRecord, self).save(*args, **kwargs)

    
    @property
    def system_id_name(self):
        return self.system_id + " - " + self.name