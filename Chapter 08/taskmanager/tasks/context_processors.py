def feature_flags(request):
    user = request.user
    flags = {
        "is_priority_feature_enabled": False,
    }

    # Ensure the user is authenticated before checking groups
    if user.is_authenticated:
        flags["is_priority_feature_enabled"] = user.groups.filter(
            name="Task Prioritization Beta Testers"
        ).exists()

    return flags
