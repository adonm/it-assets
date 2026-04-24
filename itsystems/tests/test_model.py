from django.test import TestCase
from mixer.backend.django import mixer
from uuid import uuid1

from itsystems.models import ITSystemRecord
from organisation.models import DepartmentUser
from organisation.tests.test_models import random_string
from itassets.test_api import random_dbca_email

class ITSystemRecordTestCase(TestCase):
    def setUp(self):
        self.record = create_random_record()

    def test_compare(self):
        """
        Tests the ITSystemRecord method Compare().
        compare() returns a list of differences between itself and in imported model.
        If the list is empty, it's identical outside of meta-data and the primary key.
        """

        # Creates duplicate record
        copied_record = duplicate_record(self.record)

        # Creates completely random record, ensuring it can't accidentally generate the same vals for non-unique.
        diff_record_1 = create_random_record()
        diff_record_1.name = self.record.description + random_string()
        diff_record_1.description = self.record.description + random_string()

        # Creates record with 1 difference
        diff_record_2 = duplicate_record(self.record)
        diff_record_2.description = self.record.description + " with extra text"

        no_changes = self.record.compare(copied_record)
        all_changes = self.record.compare(diff_record_1)
        single_change = self.record.compare(diff_record_2)

        # asserts that identical records do not have any reported changes
        self.assertIs(len(no_changes),0)

        # asserts that a singular change is accurately reported in the change log
        self.assertIs(len(single_change),1)
        self.assertIs(single_change[0]['new'], diff_record_2.description)
        self.assertIs(single_change[0]['old'], self.record.description)

        # asserts multiple changes are accurately reported in the change log
        self.assertIs(len(all_changes),6)
        self_fields = self.record.__dict__
        diff_fields = diff_record_1.__dict__
        for change in all_changes:
            self.assertIs(change['old'],self_fields[change['field']])
            self.assertIs(change['new'],diff_fields[change['field']])
            self.assertIs(diff_fields[change['field']] == self_fields[change['field']], False)
    
# Creates a DepartmentUser object for testing
def create_test_user():
    return mixer.blend(
            DepartmentUser,
            active=True,
            email=random_dbca_email,
            given_name=mixer.RANDOM,
            surname=mixer.RANDOM,
            employee_id=mixer.RANDOM,
            dir_sync_enabled=True,
            ad_data={"DistinguishedName": random_string()},
            azure_guid=uuid1,
    )

# Creates a random ITSystemRecord object for testing
def create_random_record():
    return mixer.blend(
            ITSystemRecord,
            system_id = mixer.RANDOM,
            name = mixer.RANDOM,
            description = mixer.RANDOM,
            business_service_owner = create_test_user(),
            system_owner = create_test_user(),
            technology_custodian = create_test_user(),
            information_custodian = create_test_user()
        )

# Duplicates an ITSystemRecord object for testing
def duplicate_record(record):
    return mixer.blend(
            ITSystemRecord,
            system_id = record.system_id + random_string(),
            name = record.name,
            description = record.description,
            business_service_owner = record.business_service_owner,
            system_owner = record.system_owner,
            technology_custodian = record.technology_custodian,
            information_custodian = record.information_custodian
        )