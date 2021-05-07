from django.urls import reverse
from mixer.backend.django import mixer

from itassets.test_api import ApiTestCase
from organisation.models import Location, OrgUnit


class OptionResourceTestCase(ApiTestCase):

    def test_data_cost_centre(self):
        """Test the data_cost_centre API endpoint
        """
        url = '/api/options/?list=cost_centre'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 001 will be present in the response.
        self.assertContains(response, self.cc1.code)
        # Add 'inactive' to Division 1 name to inactivate the CC.
        self.div1.name = 'Division 1 (inactive)'
        self.div1.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # 001 won't be present in the response.
        self.assertNotContains(response, self.cc1.code)

    def test_data_org_unit(self):
        """Test the data_org_unit API endpoint
        """
        url = '/api/options/?list=org_unit'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Org unit names will be present in the response.
        self.assertContains(response, self.dept.name)
        self.assertContains(response, self.div1.name)
        self.assertContains(response, self.div2.name)

    def test_data_dept_user(self):
        """Test the data_dept_user API endpoint
        """
        url = '/api/options/?list=dept_user'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # User 1 will be present in the response.
        self.assertContains(response, self.user1.email)
        # Make a user inactive to test exclusion
        self.user1.active = False
        self.user1.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # User 1 won't be present in the response.
        self.assertNotContains(response, self.user1.email)


class DepartmentUserAPIResourceTestCase(ApiTestCase):

    def test_list(self):
        """Test the DepartmentUserAPIResource list responses
        """
        url = reverse('department_user_api_resource')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Response should not contain inactive or shared accounts.
        self.assertContains(response, self.user1.email)
        self.assertContains(response, self.user2.email)
        self.assertNotContains(response, self.inactive_user.email)
        self.assertNotContains(response, self.contractor.email)
        self.assertNotContains(response, self.shared_acct.email)
        # Test the "selectlist" response.
        url = '{}?selectlist='.format(reverse('department_user_api_resource'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_filtering(self):
        """Test the DepartmentUserAPIResource filtered responses
        """
        url = '{}?q={}'.format(reverse('department_user_api_resource'), self.user1.email)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.email)
        self.assertNotContains(response, self.user2.email)


class LocationAPIResourceTestCase(ApiTestCase):

    def test_list(self):
        """Test the LocationAPIResource list response
        """
        loc_inactive = mixer.blend(Location, manager=None, active=False)
        url = reverse('location_api_resource')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.loc1.name)
        # Response should not contain the inactive Location.
        self.assertNotContains(response, loc_inactive.name)
        # Test the "selectlist" response.
        url = '{}?selectlist='.format(reverse('location_api_resource'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_filter(self):
        """Test the LocationAPIResource filtered response
        """
        url = '{}?q={}'.format(reverse('location_api_resource'), self.loc1.name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.loc1.name)
        self.assertNotContains(response, self.loc2.name)


class OrgUnitAPIResourceTestCase(ApiTestCase):

    def test_list(self):
        """Test the OrgUnitAPIResource list response
        """
        ou_inactive = mixer.blend(Location, manager=None, active=False)
        ou_inactive = OrgUnit.objects.create(
            name='Divison 3', unit_type=1, division_unit=self.dept, location=self.loc1, acronym='DIV3', active=False)
        url = reverse('orgunit_api_resource')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.div1.name)
        self.assertContains(response, self.branch1.name)
        # Response should not contain the inactive OrgUnit.
        self.assertNotContains(response, ou_inactive.name)
        # Test the "selectlist" response.
        url = '{}?selectlist='.format(reverse('orgunit_api_resource'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_filter(self):
        """Test the OrgUnitAPIResource filtered response
        """
        url = '{}?q={}'.format(reverse('orgunit_api_resource'), self.div1.name)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.div1.name)
        self.assertNotContains(response, self.div2.name)
        url = '{}?division'.format(reverse('orgunit_api_resource'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.div1.name)
        self.assertNotContains(response, self.branch1.name)
        url = '{}?division_id={}'.format(reverse('orgunit_api_resource'), self.div1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.branch1.name)
        self.assertNotContains(response, self.branch2.name)


class LicenseAPIResourceTestCase(ApiTestCase):

    def setUp(self):
        super(LicenseAPIResourceTestCase, self).setUp()
        self.user1.assigned_licences = ['MICROSOFT 365 E5']
        self.user1.save()
        self.user2.assigned_licences = ['OFFICE 365 E1']
        self.user2.save()

    def test_list(self):
        """Test the LicenseAPIResource list response
        """
        url = reverse('license_api_resource')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.email)
        self.assertContains(response, self.user2.email)
        self.assertNotContains(response, self.contractor.email)

    def test_filter(self):
        """Test the LicenseAPIResource filtered response
        """
        url = '{}?q={}'.format(reverse('license_api_resource'), self.user1.email)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user1.email)
        self.assertNotContains(response, self.user2.email)
        self.assertNotContains(response, self.contractor.email)
