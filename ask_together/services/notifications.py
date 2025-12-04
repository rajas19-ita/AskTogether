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
    