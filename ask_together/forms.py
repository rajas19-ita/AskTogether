from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import MyUser, Question, Answer
from django import forms
from django_summernote.widgets import SummernoteWidget
from .utils import sanitize_html
from django.utils.html import strip_tags
from bs4 import BeautifulSoup


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                'id':'email'
            }
        )
    )


class SignUpForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ['username','email']
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        widgets = {
            'content': SummernoteWidget(attrs={
                'summernote':{
                    'toolbar':[
                        ['style',['style']],
                        ['font', ['bold', 'italic', 'underline', 'strikethrough', 'clear']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol']],
                        ['insert', ['link', 'picture','hr']],
                        ['view', ['help']],
                    ],
                    'width':'100%',
                    'height': '400px'
                }
            })
        }
        
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'description']
        widgets = {
            'description': SummernoteWidget(attrs={
                'summernote':{
                    'toolbar':[
                        ['style',['style']],
                        ['font', ['bold', 'italic', 'underline', 'strikethrough', 'clear']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol']],
                        ['insert', ['link', 'picture','hr']],
                        ['view', ['help']],
                    ],
                    'width':'100%'
                }
            })
        }
            
    def clean_description(self):
        html = self.cleaned_data.get("description","")
        
        soup = BeautifulSoup(html, "html.parser")
        
        self.cleaned_data['description_text'] = soup.get_text(separator=" ", strip=True)
        
        return sanitize_html(html)
        
        
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = MyUser
        fields = ['profile_image', 'title', 'location', 'about', 'website', 'github', 'x_handle']
        widgets = {
            'about': SummernoteWidget(attrs={
                'summernote':{
                    'toolbar':[
                        ['style',['style']],
                        ['font', ['bold', 'italic', 'underline', 'strikethrough', 'clear']],
                        ['color', ['color']],
                        ['para', ['ul', 'ol']],
                        ['insert', ['link', 'picture','hr']],
                        ['view', ['help']],
                    ],
                    'width':'100%'
                }
            })
        }
        
    def clean_about(self):
        return sanitize_html(self.cleaned_data.get("about",""))     
