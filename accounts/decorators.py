from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied


def role_required(required_role):
    """
    A decorator that restricts a view to users with a specific role.

    Usage:
        @role_required('EMPLOYER')
        def my_view(request): ...

    - Redirects unauthenticated users to the login page.
    - Raises a 403 PermissionDenied error if the user has the wrong role.
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Redirect to login if the user is not logged in
            if not request.user.is_authenticated:
                return redirect('login')

            # Block access if the user's role doesn't match
            if request.user.role != required_role:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
