from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import RequestFactory, SimpleTestCase

from .utils import send_password_reset_email


class EmailUtilityTests(SimpleTestCase):
    def test_send_password_reset_email_sends_message(self):
        request = RequestFactory().get('/forgot-password/')
        user = User(username='alice', email='alice@example.com')

        with patch('main_app.utils.render_to_string', return_value='<html>reset</html>'), \
             patch('main_app.utils.EmailMultiAlternatives.send') as mock_send, \
             patch('main_app.utils.settings.DEFAULT_FROM_EMAIL', 'support@thepeoplesera.com'):
            send_password_reset_email(request, user)

        mock_send.assert_called_once()
