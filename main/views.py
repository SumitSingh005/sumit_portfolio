import json
from urllib import request as url_request
from urllib.error import HTTPError, URLError

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.views.decorators.csrf import ensure_csrf_cookie

from .forms import ContactForm
from .models import Project, Skill


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
    except (HTTPError, URLError, TimeoutError, OSError):
        return False


@ensure_csrf_cookie
def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            name = contact.name
            email = contact.email
            message = contact.message

            email_sent = False
            email_failed = False
            try:
                email_sent = send_contact_email(name, email, message)
            except Exception:
                email_failed = True

            whatsapp_sent = send_whatsapp_notification(name, email, message)

            if email_failed:
                messages.warning(
                    request,
                    'Your message was saved, but email notification failed.',
                )
            elif email_sent and whatsapp_sent:
                messages.success(
                    request,
                    'Thanks, your message has been saved and sent via Email and WhatsApp.',
                )
            elif email_sent:
                messages.success(
                    request,
                    'Thanks, your message has been saved and emailed.',
                )
            elif whatsapp_sent:
                messages.success(
                    request,
                    'Thanks, your message has been saved and notified via WhatsApp.',
                )
            else:
                messages.success(
                    request,
                    'Thanks, your message has been saved.',
                )
        else:
            errors = []
            for field, field_errors in form.errors.items():
                for error in field_errors:
                    errors.append(error)
            error_message = ' '.join(errors) if errors else 'Please check the form fields and try again.'
            messages.error(request, error_message)

        return redirect('/#contact')

    skills = Skill.objects.all()
    projects = Project.objects.all()

    featured_project = (
        projects.filter(is_featured=True).first()
        or projects.filter(image__isnull=False).exclude(image='').first()
        or projects.first()
    )

    context = {
        'skills': skills,
        'projects': projects,
        'featured_project': featured_project,
        'contact_email': getattr(settings, 'PORTFOLIO_CONTACT_EMAIL', 'panwarfm@gmail.com'),
        'contact_phone': getattr(settings, 'PORTFOLIO_CONTACT_PHONE', '8126725409'),
    }

    return render(request, 'home.html', context)


