from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import query
from django.forms.models import ModelForm
from django.shortcuts import render, redirect, reverse
# mixins = additional functions that can be added to a class/method. Normally, a class only pass in 1 argument which is equivalent to 1 function
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.http import HttpResponse
from django.views import generic
from django.views.generic.edit import CreateView
from .models import Category, Lead, Agent, Category
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm
from agents.mixins import OrganisorAndLoginRequiredMixin


class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm # need to create your own form instead of built-in form

    def get_success_url(self):
        return reverse("login") # reverse = redirect


class LandingPageView(generic.TemplateView):
    template_name = "landing.html"


def landing_page(request):
    return render(request, "landing.html")


# pass LoginRequiredMixin first to make sure it check if user is login first, then show the ListView later.
class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"
    context_object_name = "leads"

    
    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            # if user is an organisor, show ALL leads that belong to this organisor
            queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=False) # userprofile = test_admin who is an organisor
        elif user.is_agent:
            queryset = Lead.objects.filter(organisation=user.agent.organisation, agent__isnull=False) # user.agent.organisation shows ALL the leads that belong to Agent's organisation)
            # filter for the agent that is logged in
            queryset = Lead.objects.filter(agent__user=user) # agent__user shows ONLY the leads that are assigned to Agent
        return queryset

    # Since we want to add unassigned_leads to lead_list.html, we need to use get_context_data for it.
    # get_context_data helps you add more context besides the one defined in context_object_name (leads).
    # It happens this way because you only have ONE context_object_name in a class based view.
    def get_context_data(self, **kwargs): # populate result from get_queryset into a dictionary to be used as the template context
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs) # grab any context existing out there
        # only an organisor get to see unassigned leads
        if user.is_organisor:
            # if user is an organisor, show ALL leads that belong to this organisor
            queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=True) # agent__isnull is used to check if a lead has an agent or not
            context.update({
                "unassigned_leads": queryset # add unassigned_leads to the context dictionary
            })
        return context
    
def lead_list(request):
    leads = Lead.objects.all()
    # context are the variables used in HTML files.
    context = {
        "leads": leads
    }
    return render(request, "leads/lead_list.html", context)


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    # template_name, queryset, context_object_name = what a Class Based View requires
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            # if user is an organisor, show ALL leads that belong to this organisor
            queryset = Lead.objects.filter(organisation=user.userprofile) # userprofile = test_admin who is an organisor
        elif user.is_agent:
            queryset = Lead.objects.filter(organisation=user.agent.organisation) # user.agent.organisation shows ALL the leads that belong to Agent's organisation)
            # filter for the agent that is logged in
            queryset = Lead.objects.filter(agent__user=user) # agent__user shows ONLY the leads that are assigned to Agent
        return queryset


def lead_detail(request, pk):
    lead = Lead.objects.get(id=pk)
    context = {
        "lead": lead
    }
    return render(request, "leads/lead_detail.html", context)


class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organisation = self.request.user.userprofile
        lead.save()
        # This method is called when valid form data has been POSTed.
        # TODO send email
        send_mail(
            subject="A lead has been created", 
            message="Go to the website to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        messages.success(self.request, "You have successfully created a lead")
        return super(LeadCreateView, self).form_valid(form) # save form instance, set current objects for the view, and redirect to get_success_url()
        # since form_valid is overridden, we need to use super() so it also inherits methods from the parent class.
        # without using super(), methods from parent class won't be called, it means the form_valid won't redirect to get_success_url()
        # https://stackoverflow.com/questions/19197684/clarification-when-where-to-use-super-in-django-python
        # http://ccbv.co.uk/projects/Django/3.1/django.views.generic.edit/FormMixin/


def lead_create(request):
    form = LeadModelForm()
    if request.method == "POST":
        form = LeadModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/leads")
    context = {
        "form": form
    }
    return render(request, "leads/lead_create.html", context)


class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    # only organisor can update lead information
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile) # userprofile = test_admin who is an organisor


    def get_success_url(self):
        return reverse("leads:lead-list")


def lead_update(request, pk):
    lead = Lead.objects.get(id=pk) #updating is specific to one lead, so primary key (pk) is needed.
    form = LeadModelForm(instance=lead) #input instance to let django know we are updating a specific instance instead of creating a new one.
    if request.method == "POST":
        form = LeadModelForm(request.POST, instance=lead)
        if form.is_valid(): # check if user has filled the form?
            form.save()
            return redirect("/leads")
    context = {
        "form": form,
        "lead": lead
    }
    return render(request, "leads/lead_update.html", context)


class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"
    queryset = Lead.objects.all()

    def get_success_url(self):
        return reverse("leads:lead-list")

    # only organisor can delete lead
    def get_queryset(self):
        user = self.request.user
        return Lead.objects.filter(organisation=user.userprofile) # userprofile = test_admin who is an organisor


def lead_delete(request, pk):
    lead = Lead.objects.get(id=pk)
    lead.delete()
    return redirect("/leads")


class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self, **kwargs):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)
        kwargs.update({
            "request": self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead-list")
    
    def form_valid(self, form):
        agent = form.cleaned_data["agent"] # specify the agent. clean_data normalizes the data into a consistent format. Whatever you input will be formatted in the same way.
        lead = Lead.objects.get(id=self.kwargs["pk"]) # grab primary key from the URL to get the right lead
        lead.agent = agent # assign lead to the specified agent
        lead.save() # save everything into the database
        return super(AssignAgentView, self).form_valid(form) # call form_valid method from the FormView -> BaseFormView -> FormMixins class to return get_success_url()


class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        # call parent method to get all the context of the views
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user
    
        if user.is_organisor:
            # if user is an organisor, show ALL categories that belong to this organisor
            queryset = Lead.objects.filter(organisation=user.userprofile) # userprofile = test_admin who is an organisor
            category_set = Category.objects.all()
        elif user.is_agent:
            queryset = Lead.objects.filter(organisation=user.agent.organisation) # user.agent.organisation shows ALL the categories that belong to Agent's organisation)
            category_set = Category.objects.all()
        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count(),
            "contacted_lead_count": category_set.filter(name="Contacted").count(),
            "converted_lead_count": category_set.filter(name="Converted").count(),
        })
        
        print(category_set)
        return context
    

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            # if user is an organisor, show ALL categories that belong to this organisor
            queryset = Category.objects.filter(organisation=user.userprofile) # userprofile = test_admin who is an organisor
        elif user.is_agent:
            queryset = Category.objects.filter(organisation=user.agent.organisation) # user.agent.organisation shows ALL the categories that belong to Agent's organisation)
        return queryset


class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        leads = self.get_object().leads.all() # get_object gets the category that user is accessing, and return all leads belong to the category => self.contacted.leads.all()
        context.update({
            "leads": leads
        })
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_organisor:
            # if user is an organisor, show ALL categories that belong to this organisor
            queryset = Category.objects.filter(organisation=user.userprofile) # userprofile = test_admin who is an organisor
        elif user.is_agent:
            queryset = Category.objects.filter(organisation=user.agent.organisation) # user.agent.organisation shows ALL the categories that belong to Agent's organisation)
        return queryset


class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"
    form_class = LeadCategoryUpdateForm


    # only organisor can update lead information
    def get_queryset(self):
        user = self.request.user
        # initial queryset of leads for the entire organisation
        if user.is_organisor:
            # if user is an organisor, show ALL leads that belong to this organisor
            queryset = Lead.objects.filter(organisation=user.userprofile) # userprofile = test_admin who is an organisor
        elif user.is_agent:
            queryset = Lead.objects.filter(organisation=user.agent.organisation) # user.agent.organisation shows ALL the leads that belong to Agent's organisation)
            # filter for the agent that is logged in
            queryset = Lead.objects.filter(agent__user=user) # agent__user shows ONLY the leads that are assigned to Agent
        return queryset


    def get_success_url(self):
        return reverse("leads:lead-detail", kwargs={"pk": self.get_object().pk}) # get_object return a single object from queryset. It will return a link /leads/4/
