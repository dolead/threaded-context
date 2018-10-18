import threading
from functools import wraps

thread_local = threading.local()


class ThreadedContext:

    def __init__(self, **context):
        self._context = context
        self.is_weak = False
        self.parent = None

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return wrapper

    def __enter__(self):
        "Will provided context will be overrided by existing one."
        if hasattr(thread_local, "threaded_context"):
            self.parent = thread_local.threaded_context
            if self.parent.is_weak:
                new_context = thread_local.threaded_context._context.copy()
                new_context.update(self._context)
                self._context = new_context
            else:
                self._context.update(thread_local.threaded_context._context)
        thread_local.threaded_context = self
        return self

    def __exit__(self, rtype, rvalue, traceback):
        # not erasing context when execepting so it can be analysed post-mortem
        if not isinstance(rvalue, Exception):
            if self.parent is not None:
                thread_local.threaded_context = self.parent
            else:
                del thread_local.threaded_context


class WeakThreadedContext(ThreadedContext):

    def __init__(self, **context):
        super().__init__(**context)
        self.is_weak = True


def get_current():
    if hasattr(thread_local, 'threaded_context'):
        return thread_local.threaded_context._context
    return {}
