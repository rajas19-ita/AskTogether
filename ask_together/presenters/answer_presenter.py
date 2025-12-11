class AnswerPresenter:
    COMMENTS_LIMIT = 6
    
    def __init__(self, answer, request, question=None, user_vote = None, skip_comments=False):
        self.answer = answer
        self.request = request
        self.user = request.user
        self.question = question or answer.question
        
        if not self.user.is_authenticated:
            self.user_vote = 0
        else:
            self.user_vote = (
                user_vote if user_vote is not None else self.get_user_vote()
            )
            
        self.total_votes = answer.upvotes - answer.downvotes
        
        self.is_accepted = self.question.accepted_answer_id == answer.id
        self.can_accept_answer = (
            self.user.is_authenticated and 
            self.question.user_id == self.user.id 
        )
        
        self.is_answer_author_question_owner = (
            answer.author_id == self.question.user_id
        )
        
        if skip_comments:
            self.first_comments = []
            self.has_more_comments = False
            self.last_comment_id = None
        else:
            (
                self.first_comments, 
                self.has_more_comments, 
                self.last_comment_id
            ) = self.get_first_comments()
        
        
    def get_user_vote(self):
        vote = self.answer.votes.filter(user = self.user).first()
        return vote.value if vote else 0
        
    def get_first_comments(self):
        limit = self.COMMENTS_LIMIT
        qs = list(self.answer.comments.order_by('id')[:limit+1])
        
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
            "user_vote": self.user_vote,
            "total_votes": self.total_votes,
            
            "is_accepted": self.is_accepted,
            "can_accept_answer": self.can_accept_answer,
            "is_answer_author_question_owner": self.is_answer_author_question_owner,
            
            "first_comments": self.first_comments,
            "has_more_comments": self.has_more_comments,
            "last_comment_id": self.last_comment_id,
            
            "request": self.request,
            "user": self.user
        }