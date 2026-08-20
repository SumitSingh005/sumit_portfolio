from unittest.mock import patch

from django.contrib.messages import get_messages
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ContactMessage, Project, Skill


class HomeViewTests(TestCase):
    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_home_page_renders_portfolio_content(self):
        Skill.objects.create(name='Django')
        Project.objects.create(
            title='AI Portfolio',
            description='Portfolio site with Django projects.',
        )

        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Portfolio')
        self.assertContains(response, 'Django')

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_featured_project_selection_priority(self):
        proj_a = Project.objects.create(
            title='A Project No Image',
            description='Project A description',
            is_featured=False,
        )
        proj_b = Project.objects.create(
            title='B Featured Project',
            description='Project B description',
            is_featured=True,
        )

        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['featured_project'], proj_b)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='portfolio@example.com',
        CONTACT_NOTIFICATION_EMAIL='owner@example.com',
        WHATSAPP_ACCESS_TOKEN='',
        WHATSAPP_PHONE_NUMBER_ID='',
        WHATSAPP_TO_NUMBER='',
        SECURE_SSL_REDIRECT=False,
    )
    def test_contact_form_saves_message_and_sends_email(self):
        response = self.client.post(
            reverse('home'),
            {
                'name': 'Visitor',
                'email': 'visitor@example.com',
                'message': 'I would like to discuss a project.',
            },
            follow=True,
        )

        self.assertRedirects(response, '/#contact')
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Visitor', mail.outbox[0].subject)
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertIn('Thanks, your message has been saved and emailed.', messages)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
        EMAIL_HOST='',
        CONTACT_NOTIFICATION_EMAIL='owner@example.com',
        WHATSAPP_ACCESS_TOKEN='',
        WHATSAPP_PHONE_NUMBER_ID='',
        WHATSAPP_TO_NUMBER='',
        SECURE_SSL_REDIRECT=False,
    )
    def test_contact_form_saves_message_without_email_configuration(self):
        response = self.client.post(
            reverse('home'),
            {
                'name': 'Visitor',
                'email': 'visitor@example.com',
                'message': 'Please save this message.',
            },
            follow=True,
        )

        self.assertRedirects(response, '/#contact')
        self.assertEqual(ContactMessage.objects.count(), 1)
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertIn('Thanks, your message has been saved.', messages)

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_contact_form_requires_valid_email(self):
        response = self.client.post(
            reverse('home'),
            {'name': 'Visitor', 'email': 'not-a-valid-email', 'message': 'Hello'},
            follow=True,
        )

        self.assertEqual(ContactMessage.objects.count(), 0)
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(any('valid email' in msg.lower() for msg in messages))

    @override_settings(SECURE_SSL_REDIRECT=False)
    def test_contact_form_requires_all_fields(self):
        response = self.client.post(
            reverse('home'),
            {'name': '', 'email': '', 'message': ''},
            follow=True,
        )

        self.assertEqual(ContactMessage.objects.count(), 0)
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertTrue(len(messages) > 0)

    @override_settings(SECURE_SSL_REDIRECT=False)
    @patch('main.views.url_request.urlopen')
    def test_whatsapp_notification_is_sent_when_configured(self, mock_urlopen):
        mock_urlopen.return_value.__enter__.return_value = object()

        with self.settings(
            WHATSAPP_ACCESS_TOKEN='token',
            WHATSAPP_PHONE_NUMBER_ID='phone-id',
            WHATSAPP_TO_NUMBER='919999999999',
        ):
            from .views import send_whatsapp_notification

            sent = send_whatsapp_notification(
                'Visitor',
                'visitor@example.com',
                'Hello from the site.',
            )

        self.assertTrue(sent)
        self.assertTrue(mock_urlopen.called)

