from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import AnswerSerializer, CommentSerializer
from ask_together.models import Question, Answer, MyUser, Vote, Comment
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.utils import timezone

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_answer(request):
    serializer = AnswerSerializer(data=request.data)
    if serializer.is_valid():   
        serializer.save(author=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['POST', 'PATCH', 'DELETE'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def accept_answer(request, pk):
    try:
        question = Question.objects.get(pk=pk)
    except Question.DoesNotExist:
        return Response({"message":"Question not Found"}, status=404)
    
    if question.user != request.user:
        return Response({"message":"You are not allowed to accept answer for this question."}, status=403)
    
    if request.method == 'POST':
        if question.accepted_answer:
            return Response({"message":"You have accepted answer for this question"}, status=400)
        
        answer_id = request.data.get("answer")
        if not answer_id:
            return Response({"message":"Answer Id is required"}, status=400)
        
        try:
            answer = Answer.objects.get(id=answer_id, question=question)
        except Answer.DoesNotExist:
            return Response({"message":"Answer not found"}, status=404)
        
        
        question.accepted_answer = answer
        question.accepted_at = timezone.now()
        question.save()
        
        return Response({
            "question_id":question.id,
            "accepted_answer": answer.id,
            "accepted_at": question.accepted_at
        }, status=200)
        
    elif request.method == 'PATCH':
        if not question.accepted_answer:
            return Response({"message":"You have not accepted answer for this question"}, status=400)
        
        answer_id = request.data.get("answer")
        if not answer_id:
            return Response({"message":"Answer Id is required"}, status=400)
        
        if int(answer_id) == question.accepted_answer.id:
            return Response({"message":"You have already accepted this answer"}, status=400)
        
        try:
            answer = Answer.objects.get(id=answer_id, question=question)
        except Answer.DoesNotExist:
            return Response({"message":"Answer not found"}, status=404)
        
        question.accepted_answer = answer
        question.accepted_at = timezone.now()
        question.save()
        
        return Response({
            "question_id": question.id,
            "accepted_answer": answer.id,
            "accepted_at": question.accepted_at
        }, status=200)
    
    elif request.method == "DELETE":
        if not question.accepted_answer:
            return Response({"message":"You have not accepted answer for this question"}, status=400)
        
        question.accepted_answer = None
        question.accepted_at = None
        question.save()
        
        return Response({
            "question_id": question.id,
            "accepted_answer": None,
            "accepted_at": None
        }, status=200)
        
        

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def create_comment(request):
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_posts(request, pk):
    user = get_object_or_404(MyUser, pk=pk)
    
    questions = Question.objects.filter(user=user).order_by('-updated_at')[:10]
    answers = Answer.objects.filter(author=user).order_by('-updated_at')[:10]
    items = []
        
    for q in questions:
        items.append({
            "question_id": q.id,
            "answer_id": None,
            "type": "question",
            "title": q.title,
            "created_at": q.created_at,
            "updated_at": q.updated_at,
            "author": {"id": q.user.id, "username": q.user.username},
            })
        
    for a in answers:
        items.append({
            "question_id": a.question.id,
            "answer_id": a.id,
            "type": "answer",
            "title": a.question.title,
            "created_at": a.created_at,
            "updated_at": a.updated_at,
            "author": {"id": a.author.id, "username": a.author.username},
        })
    
    items.sort(key=lambda x: x['updated_at'], reverse=True)
        
    return Response(items[:10])

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vote_question(request, pk):
    action = request.data.get('action')
    
    if not action or action not in ['upvote', 'downvote', 'remove']:
        return Response({'message':'Please provide valid action: upvote/downvote/remove'}, status=400)
    
    try:
        question = get_object_or_404(Question, pk = pk)
    except Http404:
        return Response({
            "message":"Question does not exist."
        }, status=404)
    
    if action == 'remove':
        vote = Vote.objects.filter(user=request.user, question=question).first()
        if not vote:
            return Response({
                "message": "You haven't voted on this question yet.",
                "question_id": question.id,
                "u_vote": 0
            }, status=404)
            
        vote.delete()
        return Response({'message':'Vote removed successfully', 'question_id':question.id, 'u_vote':0})

    
    action_map = {"upvote": 1, "downvote":-1}
    value = action_map[action]

    vote, created = Vote.objects.get_or_create(user=request.user, 
                                              question=question,
                                              defaults={'value': value})
    
    if not created:
        if value == vote.value:
            return Response({'message':f'You have already {action}d','question_id':vote.question.id, 'u_vote':vote.value})
        else:
            vote.value = value
            vote.save()
            return Response({'message':f'switched to {action}','question_id':vote.question.id, 'u_vote':vote.value})
    
    
    return Response({'message':f'{action}d successfully', 'question_id':vote.question.id, 'u_vote':vote.value})

@api_view(['POST'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def vote_answer(request, pk):
    action = request.data.get('action')
    
    if not action or action not in ['upvote', 'downvote', 'remove']:
        return Response({'message':'Please provide valid action: upvote/downvote/remove'}, status=400)
    
    try:
        answer = get_object_or_404(Answer, pk = pk)
    except Http404:
        return Response({
            "message":"Answer does not exist."
        }, status=404)
    
    if action == 'remove':
        vote = Vote.objects.filter(user=request.user, answer=answer).first()
        if not vote:
            return Response({
                "message": "You haven't voted on this answer yet.",
                "answer_id": answer.id,
                "u_vote": 0
            }, status=404)
            
        vote.delete()
        return Response({'message':'Vote removed successfully', 'answer_id':answer.id, 'u_vote':0})

    
    action_map = {"upvote": 1, "downvote":-1}
    value = action_map[action]

    vote, created = Vote.objects.get_or_create(user=request.user, 
                                              answer=answer,
                                              defaults={'value': value})
    
    if not created:
        if value == vote.value:
            return Response({'message':f'You have already {action}d','answer_id':vote.answer.id, 'u_vote':vote.value})
        else:
            vote.value = value
            vote.save()
            return Response({'message':f'switched to {action}','answer_id':vote.answer.id, 'u_vote':vote.value})
    
    
    return Response({'message':f'{action}d successfully', 'answer_id':vote.answer.id, 'u_vote':vote.value})


@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_comments(request):
    try:
        limit = int(request.GET.get('limit',20))
    except (ValueError,TypeError):
        return Response({"error":"Invalid Limit"}, status=400)
    
    try:
        last_id = request.GET.get('last_id')
        last_id = int(last_id) if last_id is not None else None
    except (ValueError, TypeError):
        return Response({"error": "Invalid last_id"}, status=400)
    
    limit = max(1, min(limit, 20))

    if request.GET.get('question_id'):
        try:
            question_id = int(request.GET.get('question_id'))
        except (ValueError, TypeError):
            return Response({"error": "Invalid question_id"}, status=400)
        
        qs = Comment.objects.filter(question_id = question_id).order_by('id')   
    else:    
        try:
            answer_id = int(request.GET.get('answer_id'))
        except (ValueError, TypeError):
            return Response({"error": "Invalid answer_id"}, status=400)

        qs = Comment.objects.filter(answer_id = answer_id).order_by('id')
    
    
    
    if last_id:
        qs = qs.filter(id__gt=last_id)
        
    comments = list(qs[:limit+1])
    has_more = len(comments) > limit
    
    if has_more:
        comments = comments[:limit]
    
    data = {
        "comments": [
            {
                'id':comment.id,
                'content': comment.content,
                'user': {
                    "id": comment.user.id,
                    "username":comment.user.username
                },
                'created_at': comment.created_at.isoformat(),
                'updated_at': comment.updated_at.isoformat()
            } 
            for comment in comments
        ],
        "has_more":has_more,
        "last_id": comments[-1].id if comments else None,
    }
    
    
    return Response(data)

@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def check_username(request):
    username = request.GET.get('username')
    if not username:
        return Response({"error":"username query param is required"}, status=400)
    
    
    if request.user.username == username:
        return Response({"available": True}, status=200)
    
    username_exists = MyUser.objects.filter(username=username).exists()
    
    if username_exists:
        return Response({"available":False}, status=200)
    else:
        return Response({"available":True}, status=200)
    
        
