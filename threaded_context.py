import threading
from copy import deepcopy
from contextlib import ContextDecorator

thread_local = threading.local()


def _get_current_context_object():
    return getattr(thread_local, 'threaded_context', None)


class ThreadedContext(ContextDecorator):

    def __init__(self, **context):
        self.context = context
        self.parent = None

    def __enter__(self):
        "Will provided context will be overrided by existing one."
        self.parent = _get_current_context_object()
        if self.parent is not None:
            old_context = deepcopy(self.parent.context)
            if isinstance(self.parent, WeakThreadedContext):
                old_context.update(self.context)
                self.context = old_context
            else:
                self.context.update(old_context)
        thread_local.threaded_context = self
        return self

    def __exit__(self, rtype, rvalue, traceback):
        # not erasing context when execepting so it can be analysed post-mortem
        existing_context = hasattr(thread_local, 'threaded_context')
        is_exception = isinstance(rvalue, Exception)
        # if no existing_context, context has been erased
        # not pushing parent as current context
        if not is_exception and existing_context:
            if self.parent is not None:
                thread_local.threaded_context = self.parent
            else:
                del thread_local.threaded_context


class WeakThreadedContext(ThreadedContext):
    pass


def get_current_context():
    current_context = _get_current_context_object()
    if current_context is not None:
        return deepcopy(current_context.context)
    return {}


def reset_context():
    if _get_current_context_object():
        del thread_local.threaded_context


def update_current_context(**context):
    current_context = _get_current_context_object()
    if current_context is None:
        current_context = ThreadedContext(**context)
    else:
        if isinstance(current_context, WeakThreadedContext):
            current_context.context.update(context)
        else:
            context.update(current_context.context)
            current_context.context = context
    thread_local.threaded_context = current_context
