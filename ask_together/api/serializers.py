from rest_framework import serializers
from ask_together.models import Answer, MyUser, Comment, Notification, Question
from ask_together.utils import sanitize_html


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username']

class AnswerSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True) 
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
        extra_kwargs = {
            'content': {
                'error_messages': {
                    'blank': 'Answer cannot be empty',
                    'required': 'Please provide an answer'
                }
            }
        }
        
    def validate_content(self, value):
        return sanitize_html(value)
    
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'question', 'answer', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        extra_kwargs = {
            'content':{
                'error_messages':{
                    'blank':'Comment cannot be empty',
                    'required': 'Please provide content'
                }
            }
        }
        
    def validate(self, data):
        question = data.get('question')
        answer = data.get('answer')
        
        if (question and answer) or (not question and not answer):
            raise serializers.ValidationError('Comment must be linked to exactly one of Question or Answer.')
        
        return data
    

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'profile_image']
        
class QuestionShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'title']

class NotificationSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    actor = UserShortSerializer()
    question = QuestionShortSerializer()
    
    class Meta:
        model = Notification
        fields = ['id', 'user', 'actor', 'message', 'question', 'answer', 'event_type', 'upvotes', 'is_read','created_at']
        
        