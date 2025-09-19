from django.contrib.auth.forms import UserCreationForm
from .models import MyUser, Question, Answer
from django import forms
from django_summernote.widgets import SummernoteWidget
from .utils import sanitize_html


class SignUpForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ['username','email']
        
        
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
                }
            })
        }
            
    def clean_description(self):
        return sanitize_html(self.cleaned_data.get("description",""))
        
        
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
                }
            })
        }
        
    def clean_about(self):
        return sanitize_html(self.cleaned_data.get("about",""))     
