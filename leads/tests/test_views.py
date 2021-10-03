from django.test import TestCase
from django.shortcuts import reverse
# Create your tests here.

# LandingPageTest is to test Landing Page
class LandingPageTest(TestCase):
# each method is a separate test, however it is faster to run many tests in one method instead of creating multiple methods
# self keyword gives access to functionalities
    def test_status_code(self):
        # client is similar to request
        response = self.client.get(reverse("landing-page")) # use reverse to avoid hard coding the URL, reverse allows you to input the URL name instead of the actual URL.
        self.assertEqual(response.status_code, 200) # compare status_code to the value 200, if not equal, return error messages
        self.assertTemplateUsed(response, "landing.html") # compare template name used to the value "landing.html"
        # type 'py manage.py test' to run test

        
