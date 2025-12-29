class AnswerPresenter:
    COMMENTS_LIMIT = 6
    
    def __init__(self, answer, request, question):
        self.answer = answer
        self.request_user = request.user
        self.question = question      
        
        self.is_accepted = self.question.accepted_answer_id == answer.id
        self.can_accept_answer = (
            self.request_user.is_authenticated and 
            self.question.user_id == self.request_user.id 
        )
        
        self.is_answer_author_question_owner = (
            answer.author.id == self.question.user_id
        )
        
    
        (
            self.first_comments, 
            self.has_more_comments, 
            self.last_comment_id
        ) = self.get_first_comments()
        
        
    def get_first_comments(self):
        limit = self.COMMENTS_LIMIT
        comments = getattr(self.answer, "prefetched_comments", [])
        qs = comments[:limit+1]
        
        if len(qs) > limit:
            has_more_comments = True
            first_comments = qs[:limit]
            last_comment_id = first_comments[-1].id
        else:
            has_more_comments = False
            first_comments = qs
            last_comment_id = qs[-1].id if qs else None
        
        return (first_comments, has_more_comments, last_comment_id)
    
    def to_context(self):
        return {
            "answer": self.answer,
            "user_vote": getattr(self.answer, "user_vote", 0),
            "total_votes":  getattr(self.answer, "total_votes", 0),
            
            "is_accepted": self.is_accepted,
            "can_accept_answer": self.can_accept_answer,
            "is_answer_author_question_owner": self.is_answer_author_question_owner,
            
            "first_comments": self.first_comments,
            "has_more_comments": self.has_more_comments,
            "last_comment_id": self.last_comment_id,
            
            "request_user": self.request_user
        }