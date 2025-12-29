class QuestionPresenter:
    COMMENTS_LIMIT = 6
    
    def __init__(self, question):
        self.question = question
        (
            self.first_comments,
            self.has_more_comments, 
            self.last_comment_id
        ) = self.slice_comments()
             
        
    def slice_comments(self):
        limit = self.COMMENTS_LIMIT
        qs = list(
            self.question.comments
            .select_related("user")
            .only(
                "id",
                "content",
                "created_at",
                "answer_id",
                "question_id",
                "user__id",
                "user__username",
                "user__profile_image"
            )
            .order_by("created_at")
            [:limit+1])
        
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
            "total_votes": self.question.total_votes,
            "user_vote": self.question.user_vote,
            "first_comments": self.first_comments,
            "has_more_comments": self.has_more_comments,
            "last_comment_id": self.last_comment_id
        }