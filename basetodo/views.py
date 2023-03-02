from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView,UpdateView,DeleteView,FormView
from django.urls import reverse_lazy

from .models import Task
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views import View
from django.shortcuts import redirect
from django.db import transaction
from .forms import PositionForm

class CustomLoginView(LoginView):
    template_name="login.html"
    feilds='__all__'
    redirect_authenticated_user=True

    def get_success_url(self):
        return reverse_lazy('tasks')

class RegisterView(FormView):
    template_name="register.html"
    form_class=UserCreationForm
    redirect_authenticated_user=True
    success_url=reverse_lazy('tasks')

    def form_valid(self, form):
        user=form.save()
        if user is not None:
            login(self.request,user)
        return super(RegisterView,self).form_valid(form)

    def get(self,*args,**kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterView,self).get(*args,**kwargs)

class TaskList(LoginRequiredMixin,ListView):
    model=Task
    template_name="task_list.html"
    context_object_name='tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context

class TaskDetails(LoginRequiredMixin,DetailView):
    model=Task
    template_name="task_detail.html"
    context_object_name='task'

class TaskCreate(LoginRequiredMixin,CreateView):
    model=Task
    template_name="task_form.html"
    fields={'title','description','complete'}
    success_url=reverse_lazy("tasks")

    def form_valid(self, form):
        form.instance.user=self.request.user
        return super(TaskCreate,self).form_valid(form)

class TaskUpdate(LoginRequiredMixin,UpdateView):
    model=Task
    template_name="task_form.html"
    fields={'title','description','complete'}
    success_url=reverse_lazy("tasks")

class TaskDelete(LoginRequiredMixin,DeleteView):
    model=Task
    template_name="task_confirm_delete.html"
    context_object_name='task'
    success_url=reverse_lazy("tasks")

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))