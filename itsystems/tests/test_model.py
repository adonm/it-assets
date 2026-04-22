from django.test import TestCase

from itsystems.models import ITSystemRecord

class ITSystemModelTests(TestCase):
    def test_compare(self):
        """
        compare() returns a list of differences between itself and in imported model.
        If the list is empty, it's identical outside of meta-data and the primary key
        """
        base_record = ITSystemRecord(
            system_id = "T01",
            name = "base_test",
            description = "A test record",
            vital_records = True
        )

        copied_record = ITSystemRecord(
            system_id = base_record.system_id,
            name = base_record.name,
            description = base_record.description,
            vital_records = base_record.vital_records
        )

        diff_record_1 = ITSystemRecord(
            system_id = "T02",
            name = "diff_record_1",
            description = "A different record",
            vital_records = False
        )

        diff_record_2 = ITSystemRecord(
            system_id = "T01",
            name = "base_test",
            description = "A test record, but only a little bit",
            vital_records = True
        )

        no_changes = base_record.compare(copied_record)
        all_changes = base_record.compare(diff_record_1)
        single_change = base_record.compare(diff_record_2)

        self.assertIs(len(no_changes),0)

        self.assertIs(len(all_changes),4)
        self.assertIs(all_changes[0]['field'],'system_id')
        self.assertIs(single_change[0]['new'], diff_record_1.system_id)
        self.assertIs(single_change[0]['old'], base_record.system_id)
        self.assertIs(all_changes[1]['field'],'name')
        self.assertIs(single_change[1]['new'], diff_record_1.name)
        self.assertIs(single_change[1]['old'], base_record.name)
        self.assertIs(all_changes[2]['field'],'description')
        self.assertIs(single_change[2]['new'], diff_record_1.description)
        self.assertIs(single_change[2]['old'], base_record.description)
        self.assertIs(all_changes[3]['field'],'vital_records')
        self.assertIs(single_change[3]['new'], diff_record_1.vital_records)
        self.assertIs(single_change[3]['old'], base_record.vital_records)


        self.assertIs(len(single_change),1)
        self.assertIs(single_change[0]['new'], diff_record_2.description)
        self.assertIs(single_change[0]['old'], base_record.description)

