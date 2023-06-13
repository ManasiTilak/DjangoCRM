from django.core.mail import send_mail
from django.shortcuts import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from agents.mixins import OrganisorAndLoginRequiredMixin
from .models import Lead, Category
from .forms import LeadModelForm, CustomUserCreationForm, AssignAgentForm, LeadCategoryUpdateForm

#CRUD-L - Create, Retrieve, Update and Delete - List

# Create your views here.

class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class = CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")

class LandingPageView(generic.TemplateView):
    template_name = "landing.html"  

# def landing_page(request):
#     return render(request, "landing.html")

class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/lead_list.html"    
    # Default way to call context is "obeject_list"
    # To change context name
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user
        # Checks the request user. We have a user for sure because we are logged in.

        #Now we get the initial queerset of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile, agent__isnull=False)
        else: 
        #if they are an agent  
            queryset = Lead.objects.filter(organisation=user.agent.organization)
            #filter the leads based on the agent field leads ki where the user is the logged in user
            queryset = queryset.filter(agent__user=user)

        return queryset
    
    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)
        if user.is_organisor:
            queryset = Lead.objects.filter(
                organisation=user.userprofile, 
                agent__isnull=True)
            context.update({
                "unassigned_leads": queryset
            })
        return context

# def lead_list(request):
#     leads = Lead.objects.all()
#     context = {
#         "leads" : leads
#     }
#     return render(request, "leads/lead_list.html", context)

class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"    
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user
        # Checks the request user. We have a user for sure because we are logged in.

        #Now we get the initial queerset of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else: 
        #if they are an agent  
            queryset = Lead.objects.filter(organisation=user.agent.organization)
            #filter the leads based on the agent field leads ki where the user is the logged in user
            queryset = queryset.filter(agent__user=user)

        return queryset

# def lead_detail(request, pk):   
#     lead = Lead.objects.get(id=pk)
#     context = {
#         "lead": lead
#     }
#     return render(request, "leads/lead_detail.html", context)

class LeadCreateView(OrganisorAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"    
    form_class = LeadModelForm
    context_object_name = "lead"

    def get_success_url(self):
        return reverse("leads:lead_list")
    
    def form_valid(self, form):
        # lead = form.save(commit=False)
        # lead.organisation = self.request.user.userprofile
        # lead.save()
        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        # messages.success(self.request, "You have successfully created a lead")
        return super(LeadCreateView, self).form_valid(form)

# def lead_create(request):
#     form = LeadModelForm()
#     if request.method == "POST":
#         form = LeadModelForm(request.POST)
#         if form.is_valid():
#             form.save()
#             #redirects after the form is saved
#             send_mail(
#                 subject="A new lead has been created",
#                 message="Go to the site to view the new lead",
#                 from_email="test@text.com",
#                 recipient_list=["test2@test.com"]
            
#             )
#             return redirect("/leads")
#     context ={
#         "form": form
#     }
    # return render(request, "leads/lead_create.html", context)

class LeadUpdateView(OrganisorAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"   
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        # gets the logged in user
        return Lead.objects.filter(organisation=user.userprofile)
    
    def get_success_url(self):
        return reverse("leads:lead_list")

# def lead_update(request, pk):
#     lead = Lead.objects.get(id=pk)
#     form = LeadModelForm(instance=lead)
#     #instance = lead makes sure that the instance is updated rather than a new lead being saved
#     if request.method == "POST":
#         form = LeadModelForm(request.POST, instance=lead)
#         if form.is_valid():
#             form.save()
#             #redirects after the form is saved
#             return redirect("/leads")
#     context = {
#         "form": form,
#         "lead": lead
#     }
#     return render(request, "leads/lead_update.html", context)

class LeadDeleteView(OrganisorAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"  
    
    def get_success_url(self):
        return reverse("leads:lead_list")

    def get_queryset(self):
        user = self.request.user
        # gets the logged in user
        return Lead.objects.filter(organisation=user.userprofile)

# def lead_delete(request, pk):
#     lead = Lead.objects.get(id=pk)
#     lead.delete()
#     return redirect("/leads")

class AssignAgentView(OrganisorAndLoginRequiredMixin, generic.FormView):
    template_name = "leads/assign_agent.html"
    form_class = AssignAgentForm

    def get_form_kwargs(self):
        kwargs = super(AssignAgentView, self).get_form_kwargs(**kwargs)

        kwargs.update({
            "request": self.request
        })
        return kwargs

    def get_success_url(self):
        return reverse("leads:lead_list")
    
    def form_valid(self, form):
        agent = form.cleaned_data["agent"]
        lead = Lead.objects.get(id=self.kwargs["pk"])
        lead.agent= agent
        lead.save()
        return super(AssignAgentView, self).form_valid(form)
    
class CategoryListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/category_list.html"
    context_object_name = "category_list"

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        user = self.request.user

        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else: 
        #if they are an agent  
            queryset = Lead.objects.filter(organisation=user.agent.organization)
        
        context.update({
            "unassigned_lead_count": queryset.filter(category__isnull=True).count()
        })
        return context   

    def get_queryset(self):
        user = self.request.user
        # Checks the request user. We have a user for sure because we are logged in.

        #Now we get the initial queerset of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else: 
        #if they are an agent  
            queryset = Category.objects.filter(organisation=user.agent.organization)
        return queryset

class CategoryDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/category_detail.html"
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
            
        # qs = Lead.objects.filter(category=self.get_object())
        # leads = self.get_object().lead_set.all()
        leads = self.get_object().leads.all() 
        # lead ke model mein, foreign key se jahan category link ki hai udhar related name is given as leads. Hence we don't need to use "lead_set"
        context.update({
            "leads": leads
        })
        return context  
    
    def get_queryset(self):
        user = self.request.user
        # Checks the request user. We have a user for sure because we are logged in.

        #Now we get the initial queerset of leads for the entire organisation
        if user.is_organisor:
            queryset = Category.objects.filter(organisation=user.userprofile)
        else: 
        #if they are an agent  
            queryset = Category.objects.filter(organisation=user.agent.organization)
        return queryset

class LeadCategoryUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_category_update.html"   
    form_class = LeadCategoryUpdateForm

    def get_queryset(self):
        user = self.request.user
        # Checks the request user. We have a user for sure because we are logged in.

        #Now we get the initial queerset of leads for the entire organisation
        if user.is_organisor:
            queryset = Lead.objects.filter(organisation=user.userprofile)
        else: 
        #if they are an agent  
            queryset = Lead.objects.filter(organisation=user.agent.organization)
            #filter the leads based on the agent field leads ki where the user is the logged in user
            queryset = queryset.filter(agent__user=user)

        return queryset
    
    def get_success_url(self):
        return reverse("leads:lead_detail", kwargs={"pk": self.get_object().id})