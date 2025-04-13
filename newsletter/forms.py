from django import forms
from .models import NewsletterSignup


class NewsletterSignupForm(forms.ModelForm):
    class Meta:
        model = NewsletterSignup
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data['email']
        existing = NewsletterSignup.objects.filter(email=email).first()

        if existing and not existing.unsubscribed:
            raise forms.ValidationError("This email is already subscribed.")
        
        return email


class NewsletterUnsubscribeForm(forms.Form):
    email = forms.EmailField()