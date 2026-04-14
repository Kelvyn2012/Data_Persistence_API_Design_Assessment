from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from api.models import Profile

class ProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('profiles')

    @patch('api.services.ProfileAggregatorService.fetch_and_process_data')
    def test_create_profile_success(self, mock_fetch):
        mock_fetch.return_value = {
            "name": "ella",
            "gender": "female",
            "gender_probability": 0.99,
            "sample_size": 1234,
            "age": 46,
            "age_group": "adult",
            "country_id": "DRC",
            "country_probability": 0.85
        }
        response = self.client.post(self.url, {"name": "ella"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], 'ella')
        self.assertEqual(Profile.objects.count(), 1)
        
    @patch('api.services.ProfileAggregatorService.fetch_and_process_data')
    def test_idempotency(self, mock_fetch):
        Profile.objects.create(
            name="ella",
            gender="female",
            gender_probability=0.99,
            sample_size=1234,
            age=46,
            age_group="adult",
            country_id="DRC",
            country_probability=0.85
        )
        response = self.client.post(self.url, {"name": "ELLA"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile already exists')
        self.assertEqual(Profile.objects.count(), 1)
        # Verify fetch never called
        mock_fetch.assert_not_called()

    def test_missing_name(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_empty_name(self):
        response = self.client.post(self.url, {"name": ""}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_invalid_type_name(self):
        response = self.client.post(self.url, {"name": 123}, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
