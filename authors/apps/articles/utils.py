# from .views import CommentAPIView

# user = CommentAPIView.get_user()


def get_comments(comments, request=None):
    # global user
    parents = []
    for comment in comments:
        if comment.is_parent:
            parents.append({
                "id": comment.pk,
                "createdAt": comment.created_at,
                "updatedAt": comment.updated_at,
                "body": comment.body,
                "author": comment.get_profile_details(),
                "parent": comment.parent,
                "likesInfo": {
                    "like": comment.liked(request),
                    "dislike": comment.disliked(request),
                    "like_count": comment.likes_count(),
                    "dislikes_count": comment.dislikes_count()
                },
                "replies": [{
                    "id": child.pk,
                    "createdAt": child.created_at,
                    "updatedAt": child.updated_at,
                    "body": child.body,
                    "author": child.get_profile_details(),
                    "parent_id": comment.pk,
                    "likesInfo": {
                        "like": child.liked(request),
                        "dislike": child.disliked(request),
                        "like_count": child.likes_count(),
                        "dislikes_count": child.dislikes_count()
                    },
                } for child in comment.children()]
            })
    return parents
