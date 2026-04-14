from django.db import models

class ITSystemRecord(models.Model):
    """Represents a named system providing a package of functionality to
    Department staff (normally vendor or bespoke software), which is supported
    by OIM and/or an external vendor.
    """

    ACTIVE_FILTER = {"status__in": [0, 2]}  # Defines a queryset filter for "active" IT systems.
    STATUS_CHOICES = (
        (0, "Production"), 
        (1, "Production (Legacy)"), 
        (2, "Decommissioned"), 
        (3, "Draft"), 
        (4, "Unknown")
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
