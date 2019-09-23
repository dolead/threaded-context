import unittest
from threaded_context import get_current_context, ThreadedContext, WeakThreadedContext


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
            self.assert_context_equals({'eki': 'patang', 'color': 'red', 'knights': 'ni'})

        @ThreadedContext(knights='ni', eki='patang')
        def wrapping():
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
            wrapped()
            self.assert_context_equals({'eki': 'patang', 'knights': 'ni'})
        wrapping()
        self.assert_context_equals({})
