import functools


def create_run_after_decorator(method_name_to_call):
    """
    Factory function: Create a decorator will be called after the decorated
    method *successfully* completes.
    """

    def decorator(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            result = method(self, *args, **kwargs)

            func_to_call = getattr(self, method_name_to_call, None)
            if func_to_call and callable(func_to_call):
                func_to_call()

            return result

        return wrapper

    return decorator
