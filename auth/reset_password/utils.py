from django.core import mail
import re


def extract_link_uid_and_token_from_email(self):
    """
    Helper method to extract the uidb64 and token from the reset link inside the email.
    Returns a tuple: (uidb64, token).
    Asserts that:
    - one email was sent,        
    - the email contains a URL,
    - the URL matches the pattern /forget-password-reset/<uidb64>/<token>/.
    """
    self.assertEqual(len(mail.outbox), 1, "No email was sent")
    email_body = mail.outbox[0].body

    match_link = re.search(r'https?://[^\s]+', email_body)
    self.assertIsNotNone(match_link, "No URL found in email body")
    reset_link = match_link.group(0)

    match = re.search(r'/forget-password-reset/(?P<uidb64>[^/]+)/(?P<token>[^/]+)/', reset_link)
    self.assertIsNotNone(match, "Reset URL does not contain UID and token")
    return reset_link, match.group("uidb64"), match.group("token")