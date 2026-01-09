from .forms import SignUpForm, QuestionForm, UserUpdateForm, LoginForm, AnswerForm
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from .models import Question, MyUser, Answer, Comment, Vote, SavedQuestion
from django.db.models import Sum
from django.core.paginator import Paginator
from django.views import View
from google_auth_oauthlib.flow import Flow
from django.shortcuts import redirect, render
import os
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.conf import settings
import string
import random
import requests as rq
from django.core.files.base import ContentFile
from ask_together.presenters.answer_presenter import AnswerPresenter
from ask_together.presenters.question_presenter import QuestionPresenter
import logging
from django.http import HttpResponse
from django.db.models import ExpressionWrapper, F,IntegerField, Count, Prefetch, Value, Subquery, OuterRef, Exists, BooleanField
from django.db.models.functions import Coalesce
from .services.queries import answer_base_qs, with_user_vote, with_comments
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.http import QueryDict

logger = logging.getLogger(__name__)

GOOGLE_CLIENT_CONFIG = settings.GOOGLE_CLIENT_CONFIG

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'ask_together/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        questions =  (Question.objects
            # .order_by("-created_at")
            .select_related("user")
            .only(
                "id",
                "title",
                "description",
                "upvotes",
                "downvotes",
                "created_at",
                "accepted_answer_id",
                "user__id",
                "user__username",
                "user__profile_image"
            )
            .annotate(
                total_votes=ExpressionWrapper(
                    F("upvotes") - F("downvotes"),
                    output_field=IntegerField(),
                ),
                answers_count=Count("answers", distinct=True),
            ))
        
        user = self.request.user
        
        if user.is_authenticated:
            saved_qs = SavedQuestion.objects.filter(
                user=user,
                question = OuterRef("pk")
            )
            questions = questions.annotate(is_saved=Exists(saved_qs))
        else:
            questions = questions.annotate(
                is_saved = Value(False, output_field=BooleanField())
            )
        
        filter_type = self.request.GET.get("filter", "latest")
        
        if filter_type == "unanswered":
            questions = questions.filter(answers__isnull=True).order_by("-created_at")
        elif filter_type == "top":
            questions = questions.order_by("-total_votes","-created_at")
        else:
            questions = questions.order_by("-created_at")
        
        paginator = Paginator(questions, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['page_obj'] = page_obj
        context["question_count"] = Question.objects.count()
        context["answer_count"]= Answer.objects.count()
        context["user_count"]= MyUser.objects.count()
        
        return context
    
class SavedQuestionsView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('ask_together:login')
    template_name='ask_together/saved_questions.html'
    
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
    
        saved_questions = (
                    Question.objects
                    .filter(saved_by__user=self.request.user)
                    .select_related("user")
                    .only(
                        "id",
                        "title",
                        "description",
                        "upvotes",
                        "downvotes",
                        "created_at",
                        "accepted_answer_id",
                        "user__id",
                        "user__username",
                        "user__profile_image"
                    )
                    .annotate(
                        total_votes=ExpressionWrapper(
                            F("upvotes") - F("downvotes"),
                            output_field=IntegerField(),
                        ),
                        answers_count=Count("answers", distinct=True),
                        is_saved=Value(True, output_field=BooleanField()),   
                    )
                    .order_by("-saved_by__saved_at")
                    
                )
                
        paginator = Paginator(saved_questions, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context["saved_questions"] = page_obj
        context['question_count'] = paginator.count
        
        
        return context
        
    
class SearchPageView(TemplateView):
    template_name = 'ask_together/search_result.html'
    
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        
        q = self.request.GET.get('q',"").strip()
        
        results = []
        if q:
            query = SearchQuery(q, config="english")
            
            results = (
                Question.objects
                .select_related("user")
                .only(
                    "id",
                    "title",
                    "description",
                    "upvotes",
                    "downvotes",
                    "created_at",
                    "accepted_answer_id",
                    "user__id",
                    "user__username",
                    "user__profile_image"
                )
                .annotate(
                    total_votes=ExpressionWrapper(
                        F("upvotes") - F("downvotes"),
                        output_field=IntegerField(),
                    ),
                    answers_count=Count("answers", distinct=True),
                    rank=SearchRank(F("search_vector"), query)
                )
                .filter(search_vector=query)
                .order_by("-rank","-created_at")
            )
            
            user = self.request.user
            
            if user.is_authenticated:
                saved_qs = SavedQuestion.objects.filter(
                    user=user,
                    question = OuterRef("pk")
                )
                results = results.annotate(is_saved=Exists(saved_qs))
            else:
                results = results.annotate(
                    is_saved = Value(False, output_field=BooleanField())
                )
            
        paginator = Paginator(results, 5)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        params = self.request.GET.copy()
        params.pop('page',None)
        
        context['search_query'] = q
        context["search_result"] = page_obj
        context['question_count'] = paginator.count
        context['query_string'] = params.urlencode()
        
        return context
        
    
class NotificationsView(TemplateView):
    template_name='ask_together/notifications.html'
    
    
class UserLoginView(LoginView):
    template_name = 'ask_together/login.html'
    authentication_form = LoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        return next_url or reverse('ask_together:home')


class SignUpView(CreateView):
    template_name = 'ask_together/signup.html'
    form_class = SignUpForm
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_profile_complete = True
        user.save()
        
        login(self.request, user)
        
        return redirect('ask_together:home')
        

    
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
        
        form.instance.description_text = form.cleaned_data["description_text"]
        
        return super().form_valid(form)
    
    
class QuestionDetailView(DetailView):
    template_name='ask_together/question_detail.html'
    model = Question


    def get_queryset(self):
        qs = (Question.objects
            .select_related("user")
            .only(
                "id",
                "title",
                "description",
                "created_at",
                "accepted_answer_id",
                "user__id",
                "user__username",
                "user__profile_image"
            )
            .annotate(
                total_votes =ExpressionWrapper(
                    F("upvotes") - F("downvotes"),
                    output_field=IntegerField(),
                ))
            )
        
        user = self.request.user
        
        # USER VOTE ANNOTATION
        if user.is_authenticated:
            user_vote = Vote.objects.filter(question=OuterRef('pk'), user=user).values('value')[:1]
            
            qs = qs.annotate(
                user_vote = Coalesce(
                    Subquery(user_vote),
                    Value(0),
                    output_field=IntegerField()
                )
            )
        else:
           qs = qs.annotate(
               user_vote = Value(0,output_field=IntegerField())
           )
        
        if user.is_authenticated:
            saved_qs = SavedQuestion.objects.filter(
                user=user,
                question = OuterRef("pk")
            )
            qs = qs.annotate(is_saved=Exists(saved_qs))
        else:
            qs = qs.annotate(
                is_saved = Value(False, output_field=BooleanField())
            ) 
           
        return qs 
    
    
    def get_queryset(self):
        qs = (Question.objects
            .select_related("user")
            .only(
                "id",
                "title",
                "description",
                "created_at",
                "accepted_answer_id",
                "user__id",
                "user__username",
                "user__profile_image"
            )
            .annotate(
                total_votes =ExpressionWrapper(
                    F("upvotes") - F("downvotes"),
                    output_field=IntegerField(),
                ))
            )
        
        user = self.request.user
        
        # USER VOTE ANNOTATION
        if user.is_authenticated:
            user_vote = Vote.objects.filter(question=OuterRef('pk'), user=user).values('value')[:1]
            
            qs = qs.annotate(
                user_vote = Coalesce(
                    Subquery(user_vote),
                    Value(0),
                    output_field=IntegerField()
                )
            )
        else:
           qs = qs.annotate(
               user_vote = Value(0,output_field=IntegerField())
           ) 
           
        # IS_SAVED ANNOTATION
        if user.is_authenticated:
            saved_qs = SavedQuestion.objects.filter(
                user=user,
                question = OuterRef("pk")
            )
            qs = qs.annotate(is_saved=Exists(saved_qs))
        else:
            qs = qs.annotate(
                is_saved = Value(False, output_field=BooleanField())
            )
           
        return qs 
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        question = context['object']
        request = self.request
        answer_form = AnswerForm()
        context['answer_form'] = answer_form

        question_presenter = QuestionPresenter(question)
        context.update(question_presenter.to_context())
        
        answers = (
            answer_base_qs()
            .filter(question=question)
        )                  
        answers = with_user_vote(answers, request.user)
        answers = with_comments(answers)   
        answers = answers.order_by('-created_at')
        
        paginator = Paginator(answers, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        presenter_list = []
        for ans in page_obj:
            presenter = AnswerPresenter(ans, request, question)
            presenter_list.append(presenter.to_context())
            
            
        page_obj.object_list = presenter_list
        context['answers'] = page_obj
        context['answer_count'] = paginator.count
                
        return context
    
    
    
class UserDetailView(DetailView):
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
    
    
    
class PasswordReset(PasswordResetView):
    template_name = 'ask_together/password_reset_form.html'
    email_template_name = 'ask_together/password_reset_email.html'
    subject_template_name = 'ask_together/password_reset_subject.txt'
    from_email = 'rajas@gmail.com'
    success_url = reverse_lazy('ask_together:password_reset_done')
    
    
class PasswordResetDone(PasswordResetDoneView):
    template_name = 'ask_together/password_reset_done.html'
    
    
class PasswordResetConfirm(PasswordResetConfirmView):
    template_name = 'ask_together/password_reset_confirm.html'
    success_url=reverse_lazy('ask_together:password_reset_complete')
    
class PasswordResetComplete(PasswordResetCompleteView):
    template_name= 'ask_together/password_reset_complete.html'
    
    
class GoogleLoginView(View):
    def get(self, request):
        flow = Flow.from_client_config(
             GOOGLE_CLIENT_CONFIG,
             scopes=[
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'openid',
            ],
        )
        
        flow.redirect_uri = GOOGLE_CLIENT_CONFIG['web']['redirect_uris'][0]
        
        authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
        
        request.session['state'] = state
        
        return redirect(authorization_url)
        
        

class GoogleCallbackView(View):
    def get(self, request):
        state = request.session.pop("state", None)
        
        if 'error' in request.GET:
            messages.error(request,"Google login cancelled.")
            return redirect(reverse('ask_together:login'))
        
        if request.GET.get("state") != state:
            messages.error(request, "Invalid OAuth state.")
            return redirect(reverse('ask_together:login'))
            
        
        flow = Flow.from_client_config(
             GOOGLE_CLIENT_CONFIG,
             scopes=[
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'openid',
             ],
             state=state
        )
        
        flow.redirect_uri = GOOGLE_CLIENT_CONFIG['web']['redirect_uris'][0]
        
        authorization_response = request.build_absolute_uri() 
        
        if settings.DEBUG:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        try:
            flow.fetch_token(authorization_response=authorization_response)
        except Exception as e:
            messages.error(request, "Google Authentication failed, Please try again.")
            return redirect(reverse('ask_together:login'))
        
        credentials = flow.credentials
        
        
        try:
            idinfo = id_token.verify_oauth2_token(
                credentials.id_token,
                requests.Request(),
                GOOGLE_CLIENT_CONFIG['web']['client_id']
            )
            
            if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
                raise Exception("Bad issuer")
            if not idinfo.get("email_verified"):
                raise Exception("Email not verified")
        except Exception:
            messages.error(request, "Could not verify Google login, Try again.")
            return redirect(reverse('ask_together:login'))
        
        
        email = idinfo.get('email')
        picture_url = idinfo.get('picture')
    
        
        user = MyUser.objects.filter(email=email).first()
        
        if not user:
            base = email.split('@')[0].lower()
            
            if not MyUser.objects.filter(username=base).exists():
                username = base
            else:
                while True:
                    suffix = ''.join(random.choices(string.ascii_lowercase+string.digits, k=5))
                    username = f'{base}{suffix}'
                    if not MyUser.objects.filter(username=username).exists():
                        break
                       
            user = MyUser.objects.create(
                username = username,
                email = email
            )
            
            user.set_unusable_password()
            user.save()
            
            try:
                response = rq.get(picture_url)
                image_content = response.content
                filename = f'{username}_profile.jpg'
                user.profile_image.save(filename, ContentFile(image_content), save=True)
            except e:
                pass
            
            login(request, user) 
            return redirect('ask_together:account_setup')
            
        login(request, user) 
        return redirect(reverse('ask_together:home'))
    
    

class AccountSetupView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('ask_together:login')
        
        if request.user.is_profile_complete:
            return redirect('ask_together:home')
        
        return render(request, "ask_together/account_setup.html", {'user':request.user})
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('ask_together:login')
        
        if request.user.is_profile_complete:
            return redirect('ask_together:home')
        
        username = request.POST.get('username')
        
        if not username or MyUser.objects.filter(username=username).exclude(id=request.user.id).exists():
            if not username:
                messages.error(request, f'Please provide valid username')
            else:                
                messages.error(request, f'username "{username}" is already taken')
            return redirect('ask_together:account_setup')
        
        request.user.username = username
        request.user.is_profile_complete = True
        request.user.save()
    
        return redirect('ask_together:home')
        
        
        
def custom_404(request, exception):
    return render(request, "ask_together/404.html", status=404)

def custom_500(request):
    return render(request, "ask_together/500.html", status=500)