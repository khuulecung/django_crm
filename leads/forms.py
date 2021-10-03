from django import forms
from django.contrib.auth import get_user_model
from django.http import request
from .models import Lead, Agent
from django.contrib.auth.forms import UserCreationForm, UsernameField

# Since AUTH_USER_MODEL has been changed because we create a customized user model instead, you can't reference User directly anymore
# Use get_user_model() to return the currently active user model – the custom user model if one is specified, or User otherwise.
User = get_user_model()


class LeadModelForm(forms.ModelForm):
    class Meta: #provide metadata to your model, this is optional
        model = Lead
        fields = (
            'first_name',
            'last_name',
            'age',
            'agent',
            'description',
            'phone_number',
            'email',
        )

class LeadForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    age = forms.IntegerField(min_value=0)

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        field_classes = {'username': UsernameField}

class AssignAgentForm(forms.Form):
    agent = forms.ModelChoiceField(queryset=Agent.objects.none())

    def __init__(self, *args, **kwargs):
        # Unlike views, in forms, you have to assign (populate) values to the request variable instead of just importing it.
        # A dictionary that includes "request" will be populated into the kwargs as one of its elements.
        # Remove "request" from kwargs and store it in "request" object/instance
        request = kwargs.pop("request") # Form's __init__  method doesn't take user argument (request), so we remove "request" from __init__ and store it in "request" variable instead
        agents = Agent.objects.filter(organisation=request.user.userprofile) # request is now available for use
        super(AssignAgentForm, self).__init__(*args, **kwargs) # Call __init__ from Form class
        self.fields["agent"].queryset = agents # assign agent list of the specified organisation to the Agent dropdown


class LeadCategoryUpdateForm(forms.ModelForm):
    class Meta: #provide metadata to your model, this is optional
        model = Lead
        fields = (
            'category',
        )