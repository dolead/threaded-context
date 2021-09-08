import threading
from copy import deepcopy
from contextlib import ContextDecorator

thread_local = threading.local()


def _get_current_context_object():
    return getattr(thread_local, 'threaded_context', None)


class ThreadedContext(ContextDecorator):

    def __init__(self, **context):
        self._context = context
        self.parent = None

    def __enter__(self):
        "Will provided context will be overrided by existing one."
        # Avoiding finding ourselve in an infinite loop
        if self not in list(_browse_up_context()):
            self.parent = _get_current_context_object()
        thread_local.threaded_context = self
        return self

    def __exit__(self, rtype, rvalue, traceback):
        # not erasing context when execepting so it can be analysed post-mortem
        existing_context = getattr(thread_local, 'threaded_context', None)
        is_exception = isinstance(rvalue, Exception)
        # if no existing_context, context has been erased
        # not pushing parent as current context
        if not is_exception and existing_context:
            if self.parent is not None:
                thread_local.threaded_context = self.parent
            else:
                del thread_local.threaded_context

    @property
    def context(self):
        return get_current_context(self)

    @property
    def level_context(self):
        return deepcopy(self._context)

    def update_context(self, **context):
        self._context.update(context)


class WeakThreadedContext(ThreadedContext):
    """This context will be overridden by its children on conflicting value"""


class BrutalThreadedContext(ThreadedContext):
    """This context will override its parent value"""


class WeakBrutalThreadedContext(WeakThreadedContext, BrutalThreadedContext):
    pass


def _browse_up_context(current=None):
    current = current or _get_current_context_object()
    if current is not None:
        if current.parent is not None:
            yield from _browse_up_context(current.parent)
        yield current


def get_current_context(current=None):
    current = current or _get_current_context_object()
    final_context = {}
    from_ctx = {}
    for ctx in _browse_up_context(current):
        for key, value in ctx.level_context.items():
            if key not in final_context:
                final_context[key] = value
                from_ctx[key] = ctx
            elif isinstance(from_ctx[key], WeakThreadedContext):
                final_context[key] = value
                from_ctx[key] = ctx
            elif isinstance(ctx, BrutalThreadedContext):
                final_context[key] = value
                from_ctx[key] = ctx
    return final_context


def reset_context():
    if _get_current_context_object():
        del thread_local.threaded_context


def update_current_context(**context):
    current_context = _get_current_context_object()
    if current_context is None:
        thread_local.threaded_context = ThreadedContext(**context)
    else:
        current_context.update_context(**context)
