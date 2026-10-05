def active_role_processor(request):
    """
    Adds the current session-based 'active_role' to the template context.
    Falls back to the user's base role if no session override exists.
    """
    if request.user.is_authenticated:
        role = request.session.get('active_role', request.user.role)
        return {'active_role': role}
    return {}
