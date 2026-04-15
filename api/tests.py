from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch
from api.models import Profile


def make_profile(**kwargs):
    defaults = {
        "name": "ella",
        "gender": "female",
        "gender_probability": 0.99,
        "sample_size": 1234,
        "age": 46,
        "age_group": "adult",
        "country_id": "DRC",
        "country_probability": 0.85,
    }
    defaults.update(kwargs)
    return Profile.objects.create(**defaults)


class ProfileCreateTests(TestCase):
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
        make_profile()
        response = self.client.post(self.url, {"name": "ELLA"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Profile already exists')
        self.assertEqual(Profile.objects.count(), 1)
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


class ProfileListTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('profiles')
        make_profile(name="ella", gender="female", country_id="DRC", age_group="adult")
        make_profile(name="john", gender="male", country_id="NG", age_group="adult")
        make_profile(name="kim", gender="female", country_id="NG", age_group="teenager", age=17)

    def test_get_all_profiles(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_filter_by_gender(self):
        response = self.client.get(self.url, {'gender': 'female'})
        self.assertEqual(response.data['count'], 2)

    def test_filter_gender_case_insensitive(self):
        response = self.client.get(self.url, {'gender': 'Male'})
        self.assertEqual(response.data['count'], 1)

    def test_filter_by_country_id(self):
        response = self.client.get(self.url, {'country_id': 'NG'})
        self.assertEqual(response.data['count'], 2)

    def test_filter_by_age_group(self):
        response = self.client.get(self.url, {'age_group': 'teenager'})
        self.assertEqual(response.data['count'], 1)

    def test_combined_filters(self):
        response = self.client.get(self.url, {'gender': 'female', 'country_id': 'NG'})
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['data'][0]['name'], 'kim')


class ProfileDetailTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile = make_profile()
        self.url = reverse('profile-detail', kwargs={'id': self.profile.id})

    def test_get_profile_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['name'], 'ella')

    def test_get_profile_not_found(self):
        import uuid
        url = reverse('profile-detail', kwargs={'id': uuid.uuid4()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_profile_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Profile.objects.count(), 0)

    def test_delete_profile_not_found(self):
        import uuid
        url = reverse('profile-detail', kwargs={'id': uuid.uuid4()})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)