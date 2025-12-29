from ask_together.models import Answer, Vote, Comment
from django.db.models import ExpressionWrapper, F,IntegerField, Count, Prefetch, Value, Subquery, OuterRef
from django.db.models.functions import Coalesce


def answer_base_qs():
    return (
        Answer.objects
        .select_related("author")
        .only(
            "id",
            "content",
            "created_at",
            "question_id",
            "author__id",
            "author__username",
            "author__profile_image",
        )
        .annotate(
            total_votes=ExpressionWrapper(
                F("upvotes") - F("downvotes"),
                output_field=IntegerField(),
            )
        )
    )
    
def with_user_vote(qs, user):
    if not user.is_authenticated:
        return qs.annotate(
            user_vote=Value(0, output_field=IntegerField())
        )

    subq = Vote.objects.filter(
        answer=OuterRef("pk"),
        user=user
    ).values("value")[:1]

    return qs.annotate(
        user_vote=Coalesce(Subquery(subq), Value(0), output_field=IntegerField())
    )
    
def with_comments(qs):
    return qs.prefetch_related(
        Prefetch(
            "comments",
            queryset=(Comment.objects
                .select_related("user")
                .only(
                    "id",
                    "content",
                    "created_at",
                    "answer_id",
                    "user__id",
                    "user__username",
                    "user__profile_image",
                )
                .order_by("created_at")),
            to_attr="prefetched_comments"
        )
    )