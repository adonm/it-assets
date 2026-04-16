import csv
from .models import ITSystemRecord

# Exports the IT System Register to a CSV file
def ExportCSV(writer):
    headers = [field.verbose_name for field in ITSystemRecord._meta.get_fields()][1:-4]
    writer.writerow(headers)

    records = ITSystemRecord.objects.all()
        # 'system_id',
        # 'name',
        # 'division',
        # 'status',
        # 'seasonality',
        # 'availability',
        # 'description',
        # 'link',
        # 'file_store_link',
        # 'system_owner__email',
        # 'technology_custodian__email',
        # 'information_custodian__email',
        # 'business_service_owner__email',
        # 'vital_records',
        # 'disposal_authority',
        # 'retention_and_disposal',
        # 'sensitivity',
        # 'system_type',
        # 'ubcs',
    for record in records:
        record_vals = [
            record.system_id,
            record.name,
            record.get_division_display(),
            record.get_status_display(),
            record.get_seasonality_display(),
            record.get_availability_display(),
            record.link,
            record.file_store_link,
            record.system_owner.email,
            record.technology_custodian.email if record.technology_custodian else "",
            record.information_custodian.email if record.information_custodian else "",
            record.business_service_owner.email if record.business_service_owner else "",
            record.vital_records,
            record.disposal_authority,
            record.retention_and_disposal,
            record.get_sensitivity_display(),
            record.get_system_type_display(),
            record.ubcs
        ]
        writer.writerow(record_vals)

def ImportCSV(self):
    pass