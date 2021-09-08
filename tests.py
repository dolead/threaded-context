import unittest
from threaded_context import (get_current_context, reset_context,
                              update_current_context,
                              ThreadedContext, WeakThreadedContext)


class ThreadedContextTestCase(unittest.TestCase):

    def assert_context_equals(self, context):
        self.assertEqual(context, get_current_context())

    def test_base(self):
        self.assert_context_equals({})
        with ThreadedContext(knights='ni', eki='patang'):
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
            with ThreadedContext(knights='round table', color='red'):
                self.assert_context_equals({'eki': 'patang', 'color': 'red',
                                            'knights': 'ni'})
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
        self.assert_context_equals({})

    def test_base_weak(self):
        self.assert_context_equals({})
        with WeakThreadedContext(knights='ni', eki='patang'):
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
            with ThreadedContext(knights='round table', color='red'):
                self.assert_context_equals({'eki': 'patang', 'color': 'red',
                                            'knights': 'round table'})
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
        self.assert_context_equals({})

    def test_double_weak(self):
        self.assert_context_equals({})
        with WeakThreadedContext(knights='ni', eki='patang'):
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
            with WeakThreadedContext(knights='round table', color='red'):
                self.assert_context_equals({'eki': 'patang', 'color': 'red',
                                            'knights': 'round table'})
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
        self.assert_context_equals({})

    def test_as_decorator(self):
        self.assert_context_equals({})

        @ThreadedContext(knights='round table', color='red')
        def wrapped():
            self.assert_context_equals({'eki': 'patang', 'color': 'red',
                                        'knights': 'ni'})

        @ThreadedContext(knights='ni', eki='patang')
        def wrapping():
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
            wrapped()
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
        wrapping()
        self.assert_context_equals({})

    def test_cant_modify_current_context(self):
        with ThreadedContext(knights='ni', eki={'eki': 'patang'}):
            ctx = get_current_context()
            ctx['knights'] = 'round table'
            self.assert_context_equals({'knights': 'ni',
                                        'eki': {'eki': 'patang'}})
            ctx = get_current_context()
            ctx['eki']['eki'] = 'patong'
            ctx['eki']['eko'] = 'shrubbery'
            self.assert_context_equals({'knights': 'ni',
                                        'eki': {'eki': 'patang'}})

    def test_reseting_context(self):
        self.assert_context_equals({})
        with ThreadedContext(knights='ni', eki='patang'):
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
            with ThreadedContext(knights='round table', color='red'):
                self.assert_context_equals({'eki': 'patang', 'color': 'red',
                                            'knights': 'ni'})
                reset_context()
                self.assert_context_equals({})
            self.assert_context_equals({})
        self.assert_context_equals({})

    def test_updating_current_context(self):
        self.assert_context_equals({})
        with ThreadedContext(knights='ni'):
            self.assert_context_equals({'knights': 'ni'})
            update_current_context(knights='round table', color='red')
            self.assert_context_equals({'knights': 'round table',
                                        'color': 'red'})
        with WeakThreadedContext(knights='ni'):
            self.assert_context_equals({'knights': 'ni'})
            update_current_context(knights='round table', color='red')
            self.assert_context_equals({'knights': 'round table',
                                        'color': 'red'})
        self.assert_context_equals({})
        update_current_context(knights='round table', color='red')
        self.assert_context_equals({'knights': 'round table', 'color': 'red'})
        reset_context()
        self.assert_context_equals({})

    def test_recursive_context(self):
        my_ctx = ThreadedContext(knights='ni')
        with my_ctx:
            self.assert_context_equals({'knights': 'ni'})
            with my_ctx:
                self.assert_context_equals({'knights': 'ni'})
                with my_ctx:
                    self.assert_context_equals({'knights': 'ni'})

    def test_resilient_thread_type(self):
        self.assert_context_equals({})
        with WeakThreadedContext(knights='ni'):
            self.assert_context_equals({'knights': 'ni'})
            with ThreadedContext(color='red'):
                self.assert_context_equals({'knights': 'ni', 'color': 'red'})
                with WeakThreadedContext(knights='eki'):
                    self.assert_context_equals({'knights': 'eki',
                                                'color': 'red'})
