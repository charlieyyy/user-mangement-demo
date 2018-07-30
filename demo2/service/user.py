from flask import _request_ctx_stack
from functools import wraps


def rule_required(level=None):
    if level is None:
        # 2 编辑 9 管理员
        level = [2, 9]

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_current_user()
            if user.level not in level:
                raise Exception("user don't has authority")
            return fn(*args, **kwargs)
        return decorator
    return wrapper


def get_current_user():
    return _request_ctx_stack.top.current_identity
