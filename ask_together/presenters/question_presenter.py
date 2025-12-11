class QuestionPresenter:
    COMMENTS_LIMIT = 6
    
    def __init__(self, question, request):
        self.question = question
        self.total_votes = question.upvotes - question.downvotes
        self.user = request.user
        self.user_vote = self.get_user_vote()
        
        (
            self.first_comments,
            self.has_more_comments, 
            self.last_comment_id
        ) = self.get_first_comments()
             
             
    
    def get_user_vote(self):
        if not self.user.is_authenticated:
            return 0
        
        vote = self.question.votes.filter(user=self.user).first()
        return vote.value if vote else 0
        
    def get_first_comments(self):
        limit = self.COMMENTS_LIMIT
        qs = list(self.question.comments.order_by('id')[:limit+1])
        
        if len(qs)> limit:
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
            "total_votes": self.total_votes,
            "user_vote": self.user_vote,
            "first_comments": self.first_comments,
            "has_more_comments": self.has_more_comments,
            "last_comment_id": self.last_comment_id
        }