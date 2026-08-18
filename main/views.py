import json
from urllib import request as url_request
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import ContactMessage, Project, Skill


def build_contact_notification(name, email, message):
    return (
        'New portfolio contact message\n\n'
        f'Name: {name}\n'
        f'Email: {email}\n\n'
        f'Message:\n{message}'
    )


def send_contact_email(name, email, message):
    if not settings.CONTACT_NOTIFICATION_EMAIL:
        return False

    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        return False

    if settings.EMAIL_BACKEND.endswith('.smtp.EmailBackend') and not settings.EMAIL_HOST:
        return False

    email_message = EmailMessage(
        subject=f'New portfolio message from {name}',
        body=build_contact_notification(name, email, message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.CONTACT_NOTIFICATION_EMAIL],
        reply_to=[email],
    )
    email_message.send(fail_silently=False)
    return True


def send_whatsapp_notification(name, email, message):
    if not all([
        settings.WHATSAPP_ACCESS_TOKEN,
        settings.WHATSAPP_PHONE_NUMBER_ID,
        settings.WHATSAPP_TO_NUMBER,
    ]):
        return False

    endpoint = (
        'https://graph.facebook.com/v19.0/'
        f'{settings.WHATSAPP_PHONE_NUMBER_ID}/messages'
    )
    payload = {
        'messaging_product': 'whatsapp',
        'to': settings.WHATSAPP_TO_NUMBER,
        'type': 'text',
        'text': {
            'preview_url': False,
            'body': build_contact_notification(name, email, message),
        },
    }
    encoded_payload = json.dumps(payload).encode('utf-8')
    whatsapp_request = url_request.Request(
        endpoint,
        data=encoded_payload,
        headers={
            'Authorization': f'Bearer {settings.WHATSAPP_ACCESS_TOKEN}',
            'Content-Type': 'application/json',
        },
        method='POST',
    )

    try:
        with url_request.urlopen(whatsapp_request, timeout=10):
            return True
    except (HTTPError, URLError, TimeoutError):
        return False


@ensure_csrf_cookie
def home(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message,
            )

            try:
                email_sent = send_contact_email(name, email, message)
            except Exception:
                messages.warning(
                    request,
                    'Your message was saved, but email notification failed.',
                )
            else:
                if email_sent:
                    messages.success(
                        request,
                        'Thanks, your message has been saved and emailed.',
                    )
                else:
                    messages.success(
                        request,
                        'Thanks, your message has been saved.',
                    )

            if send_whatsapp_notification(name, email, message):
                messages.success(request, 'WhatsApp notification sent.')
        else:
            messages.error(request, 'Please fill in every contact field.')

        return redirect('/#contact')

    skills = Skill.objects.all()
    projects = Project.objects.all()

    context = {
        'skills': skills,
        'projects': projects,
        'featured_project': projects.first(),
    }

    return render(request, 'home.html', context)

