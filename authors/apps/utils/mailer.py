from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

class ConfirmationMail:
    """
    Email class for sending confirmation mail
    """

    def __init__(self, data):
        self.username = data.get("username")
        self.email = data.get("email")
        self.token = data.get("token")

    def compose_mail(self):
        """
        Composes the email
        """
        html_body = render_to_string(
            template_name="mail.html",
            context={
                "name": self.username,
                "verification": settings.VERIFICATION_URL+self.token
            }
        )
        self.message = EmailMultiAlternatives(
            subject="Welcome {}".format(self.username),
            body="Confirmation email",
            from_email="noreply@authorsheaven.com",
            to=[self.email]
        )
        self.message.attach_alternative(html_body, "text/html")

    def send_mail(self):
        """
        Sends the composed email
        """
        self.compose_mail()
        self.message.send()
