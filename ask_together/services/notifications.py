from ask_together.models import Notification

def notify_answer_posted(answer):
    Notification.objects.create(
        user=answer.question.user,
        actor=answer.author,
        event_type="ANSWER_POSTED",
        message=f"{answer.author.username} answered your question.",
        question=answer.question,
        answer=answer
    )
    
    
def notify_comment_on_question(comment):
    if comment.user == comment.question.user:
        return
    
    Notification.objects.create(
        user=comment.question.user,
        actor=comment.user,
        event_type="COMMENT_ON_QUESTION",
        message=f"{comment.user.username} commented on your question.",
        question=comment.question,
    )
    
def notify_comment_on_answer(comment):
    if comment.user == comment.answer.author:
        return
    
    Notification.objects.create(
        user=comment.answer.author,
        actor=comment.user,
        event_type="COMMENT_ON_ANSWER",
        message=f"{comment.user.username} replied to your answer.",
        question=comment.answer.question,
        answer = comment.answer
    )
    
def notify_answer_accepted(answer):
    if answer.author == answer.question.user:
        return
    
    if Notification.objects.filter(
        user = answer.author,
        event_type = "ANSWER_SELECTED",
        answer = answer
    ).exists():
        return
    
    Notification.objects.create(
        user=answer.author,
        actor=answer.question.user,
        event_type="ANSWER_SELECTED",
        message=f"Your answer was accepted.",
        question=answer.question,
        answer=answer
    )
    
def notify_question_upvote_milestone(question, milestone):
    Notification.objects.create(
        user = question.user,
        actor=None,
        event_type="UPVOTE_MILESTONE",
        message=f"Congratulations! your question has crossed {milestone} upvotes.",
        question = question,
        upvotes = milestone
    )
    
def notify_answer_upvote_milestone(answer, milestone):
    Notification.objects.create(
        user = answer.author,
        actor=None,
        event_type="UPVOTE_MILESTONE",
        message=f"Congratulations! your answer has crossed {milestone} upvotes.",
        question = answer.question,
        answer = answer,
        upvotes = milestone
    )