from itassets.test_api import ApiTestCase
import json

from django.urls import reverse

class ITSystemResourceTestCase(ApiTestCase):

    def test_list(self):
        """Test the ITSystemResource list response
        """
        url = '/api/itsystems/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # The 'development' & decommissioned IT systems won't be in the response.
        self.assertNotContains(response, self.it2.name)
        self.assertNotContains(response, self.it_dec.name)

    def test_list_all(self):
        """Test the ITSystemResource list response with all param
        """
        url = '/api/itsystems/?all'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # The 'development' IT system will be in the response.
        self.assertContains(response, self.it2.name)

    def test_list_filter(self):
        """Test the ITSystemResource list response with system_id param
        """
        url = '/api/itsystems/?system_id={}'.format(self.it1.system_id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.it1.name)
        self.assertNotContains(response, self.it2.name)


class ITSystemHardwareResourceTestCase(ApiTestCase):

    def test_list(self):
        url = '/api/itsystem-hardware/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # The 'decommissioned' IT system won't be in the response.
        self.assertNotContains(response, self.it_dec.name)

#confirm the url is correct for this viewset
class ChangeRequestViewSetTestCase(ApiTestCase):

    def test_list(self):
        #url = reverse('changerequest-list')

        url = '/api/v2/changerequest/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    # def test_retrieve(self):
    #     url = reverse('changerequest-retrieve')
    #
    #     # url = '/api/v2/changerequest/retrieve'
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)

    def test_create(self):

        url=reverse('change_request_create')

        data = {
            'title' : 'Test',
            'requester' : 'John Doe',
            'endorser' : 'Doe1' ,
            'implementor' : 'Doe2',

            'status': 0,
            'unexpected_issues': False,
            'caused_issues': False

        }

        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)


    def test_update(self):
        pass

# Confirm the url is right
class StandardChangeViewSetTestCase(ApiTestCase):

    def test_list(self):
        url = reverse('standardchange-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)