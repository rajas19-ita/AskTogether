from .forms import SignUpForm, QuestionForm, UserUpdateForm
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from .models import Question, MyUser
from django.db.models import Sum
from django.core.paginator import Paginator


# Create your views here.

class HomePageView(LoginRequiredMixin,TemplateView):
    login_url = reverse_lazy('ask_together:login')
    template_name = 'ask_together/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = Question.objects.all().order_by('-created_at') 
        
        paginator = Paginator(questions, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        
        return context
    
    
class UserLoginView(LoginView):
    template_name = 'ask_together/login.html'

    def get_success_url(self):
        return reverse('ask_together:home')


class SignUpView(CreateView):
    template_name = 'ask_together/signup.html'
    form_class = SignUpForm

    def get_success_url(self):
        return reverse('ask_together:login')

    
class UserLogoutView(LogoutView):
    next_page = reverse_lazy('ask_together:login')
    
class QuestionCreateView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy('ask_together:login')
    template_name = 'ask_together/question_form.html'
    form_class = QuestionForm
    
    
    def get_success_url(self):
        return reverse('ask_together:home')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    
class QuestionDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('ask_together:login')
    template_name='ask_together/question_detail.html'
    model = Question
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object = context['object']
        
        total_votes = object.votes.aggregate(score=Sum('value'))['score'] or 0
        context['total_votes'] = total_votes
        
        user_vote = object.votes.filter(user=self.request.user).first()
        context['user_vote'] = user_vote.value if user_vote else 0
        
        answers = object.answers.annotate(
            total_votes=Sum('votes__value')
        ).order_by('-created_at')
        
        paginator = Paginator(answers, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        for ans in page_obj:
            ans.total_votes = ans.total_votes or 0
            vote = ans.votes.filter(user=self.request.user).first()
            ans.user_vote = vote.value if vote else 0
            
        context['answers'] = page_obj
                
        return context
    
    
    
class UserDetailView(LoginRequiredMixin, DetailView):
    login_url = reverse_lazy('ask_together:login')
    template_name = 'ask_together/user_profile.html'
    model = MyUser

class UserUpdateView(LoginRequiredMixin, UpdateView):
    model= MyUser
    login_url = reverse_lazy('ask_together:login')
    form_class = UserUpdateForm
    template_name = 'ask_together/user_profile_edit.html'
    
    def get_success_url(self):
        return reverse('ask_together:user_profile', args=[self.request.user.id])
    
    def get_object(self, queryset = None):
        return self.request.user