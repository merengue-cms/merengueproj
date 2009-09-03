from plugins.feedback.models import Feedback
from plugins.feedback.forms import CaptchaFeedbackForm


def get_model():
    return Feedback


def get_form():
    return CaptchaFeedbackForm
