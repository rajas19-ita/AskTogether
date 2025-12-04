from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

# Create your models here.

class MyUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
    location = models.CharField(max_length=150, blank=True)
    title = models.CharField(max_length=150, blank=True)
    about = models.TextField(blank=True)
    website = models.URLField(blank=True)
    github = models.CharField(max_length=100, blank=True)
    x_handle = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profiles', blank=True)
    is_profile_complete = models.BooleanField(default=False)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    


class Question(models.Model):
    title = models.CharField(max_length=200,blank=False, null=False)
    description = models.TextField()
    user = models.ForeignKey(
        MyUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='questions'
    )
    accepted_answer = models.OneToOneField(
        "Answer",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="accepted_for"
    )
    upvotes = models.SmallIntegerField(default=0)
    downvotes = models.SmallIntegerField(default=0)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, related_name='answers')
    content = models.TextField()
    upvotes = models.SmallIntegerField(default=0)
    downvotes = models.SmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class Vote(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='votes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True, related_name='votes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True, related_name='votes')
    value = models.SmallIntegerField(default = 1)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user','question'], name='unique_user_question_vote'),
            models.UniqueConstraint(fields=['user','answer'], name='unique_user_answer_vote')
        ]
        
    def clean(self):
        super().clean()
        if (self.question and self.answer) or (not self.question and not self.answer):
            raise ValidationError("Vote must be linked to exactly one of Question or Answer")
        
    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
        

class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True, related_name='comments')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        super().clean()
        if (self.question and self.answer) or (not self.question and not self.answer):
            raise ValidationError("Comment must be linked to exactly one of Question or Answer")
        
    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)