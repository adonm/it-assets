import csv
import io
from .models import ITSystemRecord, DepartmentUser, Division

# Exports the IT System Register to a CSV file
def ExportCSV(response):
    writer=csv.writer(response)
    headers = [field.name for field in __get_model_fields()]
    writer.writerow(headers)

    records = ITSystemRecord.objects.all()
    for record in records:
        record_vals = [
            record.system_id,
            record.name,
            record.get_status_display(),
            record.division.name if record.division else "",
            record.business_service_owner.email if record.business_service_owner else "",
            record.system_owner.email if record.system_owner else "",
            record.technology_custodian.email if record.technology_custodian else "",
            record.information_custodian.email if record.information_custodian else "",
            record.get_seasonality_display(),
            record.get_availability_display(),
            record.link,
            record.description,
            record.file_store_link,
            record.vital_records,
            record.disposal_authority,
            record.retention_and_disposal,
            record.ubcs,
            record.get_sensitivity_display(),
            record.get_system_type_display()
        ]
        writer.writerow(record_vals)

# Imports new records and updates of existing records to database through csv_file
def ImportCSV(request):
    csv_file = request.FILES['csv_file']
    update_list = []
    create_list = []
    failed_list = []

    validate_results = __validate_csv(csv_file)
    if validate_results['valid']:
        raw_text = validate_results['raw_text']
        record_list = list(csv.DictReader(io.StringIO(raw_text)))
        for record in record_list:
            # Search for existing record in database
            try:
                found_record = ITSystemRecord.objects.get(system_id=record['system_id'])
            except: 
                found_record = None
        
            try:
                # Populate new record with data
                new_record = ITSystemRecord()
                __load_data(new_record,record)

                if found_record:
                    changes = found_record.compare(new_record)
                    if len(changes)>0:
                        __load_data(found_record,record)
                        found_record.modified_by = request.user.email
                        found_record.save()
                        update_list.append({"record":found_record.system_id_name, "changes":changes})
                elif not found_record:
                    new_record.created_by = request.user.email
                    new_record.modified_by = request.user.email
                    new_record.save()
                    changes = new_record.compare(None)
                    create_list.append({"record":new_record.system_id_name, "changes":changes})
            except Exception as e:
                if hasattr(e, 'message'):
                    error_message = e.message
                else:
                    error_message = str(e)
                failed_list.append({"record":record['system_id'], "changes": error_message})

    else:
        print(validate_results['message'])

    return {'validation':{'valid':validate_results['valid'], 'message':validate_results['message']},'created':create_list,'updated':update_list, 'failed':failed_list}


def __validate_csv(csv_file):
    valid = False
    msg = ""
    raw_text = None
    # Checks that file is a CSV
    if csv_file.name.endswith(".csv"):
        # Checks that file isn't chunked / over 2 mb
        if not csv_file.multiple_chunks():
            raw_text = csv_file.read().decode(encoding='utf-8', errors='replace')
            csv_headers = raw_text.split("\r\n")[0].split(",")
            model_fields = __get_model_fields()
            # Checks that csv has the correct headers
            if all(csv == model.name for csv, model in zip(csv_headers, model_fields)):
                valid = True
                msg = "CSV is Valid"
            else:
                msg = "CSV Headers do not match the required format"
        else:
            msg = "File size is too large (>2MB)."
    else:
        msg = "The selected file isn't a CSV"
    return {"valid":valid, "message":msg, "raw_text":raw_text}

def __load_data(new_record, record):
    new_record.system_id = record['system_id']
    new_record.name = record['name']
    new_record.division = __get_division_fk(record['division'])
    new_record.status = __get_choice_val(record['status'],ITSystemRecord.STATUS_CHOICES, 'status')
    new_record.seasonality = __get_choice_val(record['seasonality'],ITSystemRecord.SEASONALITY_CHOICES, 'seasonality')
    new_record.availability = __get_choice_val(record['availability'],ITSystemRecord.AVAILABILITY_CHOICES, 'availability')
    new_record.description = record['description']
    new_record.link = record['link']
    new_record.file_store_link = record['file_store_link']
    new_record.system_owner = __get_user_fk(record['system_owner'],'system_owner')
    new_record.technology_custodian = __get_user_fk(record['technology_custodian'],'technology_custodian')
    new_record.information_custodian = __get_user_fk(record['information_custodian'],'information_custodian')
    new_record.business_service_owner = __get_user_fk(record['business_service_owner'],'business_service_owner')
    new_record.vital_records = record['vital_records'].lower().strip()=='true'
    new_record.disposal_authority = record['disposal_authority']
    new_record.retention_and_disposal = record['retention_and_disposal']
    new_record.sensitivity = __get_choice_val(record['sensitivity'],ITSystemRecord.SENSITIVITY_CHOICES, 'sensitivity')
    new_record.system_type = __get_choice_val(record['system_type'],ITSystemRecord.SYSTEM_TYPE_CHOICES, 'system_type')
    new_record.ubcs = record['ubcs']

def __get_choice_val(text,choicelist, field):
    choice = next((choice for choice in choicelist if text in choice),[None])
    if text and not choice[0]:
        raise Exception(field + ": Can't find '" + text + "' in options " + str(choicelist) + "." )
    return choice[0]

def __get_user_fk(email, field):
    user = None
    suffix = "@dbca.wa.gov.au"
    email_query = None
    try:
        if email:
            if email.endswith(suffix):
                email_query = email
            elif " " in email:
                names = email.split(" ")
                email_query = names[0].lower() + "." + "".join(names[1:]).lower() + suffix
        if email_query:
            user = DepartmentUser.objects.get(email=email_query)
    except Exception as e:
        print(str(e) + ": " + email)
        if email:
            raise Exception(field + ": Can't find user '" + email + "'.")
        user = None
    return user

def __get_division_fk(name):
    fk = None
    try:
        if name:
            fk = Division.objects.get(name=name)
    except Exception as e:
        print(str(e))
        raise Exception("Division: Can't find option '" + name + "'.")
    return fk

def __get_model_fields():
    return ITSystemRecord._meta.get_fields()[1:-4]