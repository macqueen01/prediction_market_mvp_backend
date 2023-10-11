from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from main.models import User, Portfolio
from main.serializers import SinglePortfolioSerializer

class GetPortfoliosOfUserTest(TestCase):
    def setUp(self):

        self.user = User.objects.get_or_create(username="test_user1")

        self.client = APIClient()

    def test_get_portfolios_of_user(self):
        # Define the URL for your view
        url = reverse('get_portfolios_of_user')  # Make sure to set the correct URL name

        # Make a GET request to the view
        response = self.client.get(url)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        print(response.data)