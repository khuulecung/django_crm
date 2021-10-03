import random
from django.shortcuts import render, reverse
from django.core.mail import send_mail
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from leads.models import Agent, UserProfile
from .forms import AgentModelForm
from .mixins import OrganisorAndLoginRequiredMixin

# Create your views here.
class AgentListView(OrganisorAndLoginRequiredMixin, generic.ListView):
    template_name = "agents/agent_list.html"
    context_object_name = "agents"
    # You can use this instead of queryset = Agent.objects.all()
    def get_queryset(self):
        # Super User can only see Agent created by his organisation
        # To do this, you can filter the queryset to only return the organisation
        organisation = self.request.user.userprofile # define organisation_1 | organisatio_1 right now = test_admin
        return Agent.objects.filter(organisation=organisation) 
        # assign organisation_1 (test_admin) to organisation_2 (new variable), 
        # and only return Agents that belong to test_admin organisation


class AgentCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "agents/agent_create.html"
    form_class = AgentModelForm # form_class = the model form class created in forms.py

    def get_success_url(self):
        return reverse("agents:agent-list")

    def form_valid(self, form):
        user = form.save(commit=False) # user = username entered by user
        user.is_agent = True # set Is agent field as True in django admin
        user.is_organisor = False # set Is organisation field as False in django admin
        user.set_password(f"{random.randint(0, 1000000)}")
        user.save()
        Agent.objects.create(
            user=user, #user = username entered by user
            organisation=self.request.user.userprofile,
        )

        send_mail(
            subject="You are invited to be an agent",
            message="You were added as an agent on DJCRM. Please come login to start working.",
            from_email="admin@test.com",
            recipient_list=[user.email]
        )
        return super(AgentCreateView, self).form_valid(form)


class AgentDetailView(OrganisorAndLoginRequiredMixin, generic.DetailView):
    template_name = "agents/agent_detail.html"
    context_object_name = "agent" # allow you to use variable such as agent.firstname, agent.user.username, etc.

    def get_queryset(self):
        organisation = self.request.user.userprofile # define organisation_1 | organisatio_1 right now = test_admin
        return Agent.objects.filter(organisation=organisation)


class AgentUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "agents/agent_update.html"
    form_class = AgentModelForm # form_class = the model form class created in forms.py

    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        return Agent.objects.all()


class AgentDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "agents/agent_delete.html"
    context_object_name = "agent" # allow you to use variable such as agent.firstname, agent.user.username, etc.

    def get_success_url(self):
        return reverse("agents:agent-list")

    def get_queryset(self):
        organisation = self.request.user.userprofile # define organisation_1 | organisatio_1 right now = test_admin
        return Agent.objects.filter(organisation=organisation)