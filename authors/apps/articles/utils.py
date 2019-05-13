def get_comments(comments):
    parents = []
    for comment in comments:
        if comment.is_parent:
            parents.append({
                "id": comment.pk,
                "createdAt": comment.created_at,
                "updatedAt": comment.updated_at,
                "body": comment.body,
                "author": comment.get_profile_details(),
                "replies": [{
                    "id": child.pk,
                    "createdAt": child.created_at,
                    "updatedAt": child.updated_at,
                    "body": child.body,
                    "author": child.get_profile_details(),
                } for child in comment.children()]
            })
    return parents
