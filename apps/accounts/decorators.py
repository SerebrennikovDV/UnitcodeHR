"""Декораторы проверки ролей пользователей."""
from functools import wraps
from django.core.exceptions import PermissionDenied


def role_required(*role_codes):
    """Декоратор: разрешает доступ только пользователям с одной из указанных ролей."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')
            if not request.user.role or request.user.role.code not in role_codes:
                raise PermissionDenied('Недостаточно прав для выполнения операции.')
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
