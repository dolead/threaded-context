import unittest
from threaded_context import get_current, ThreadedContext, WeakThreadedContext


class ThreadedContextTestCase(unittest.TestCase):

    @staticmethod
    def test_base():
        assert get_current() == {}
        with ThreadedContext(knights='ni', eki='patang'):
            assert get_current() == {'eki': 'patang', 'knights': 'ni'}
            with ThreadedContext(knights='round table', color='red'):
                assert get_current() == {'eki': 'patang',
                        'color': 'red', 'knights': 'ni'}
            assert get_current() == {'eki': 'patang', 'knights': 'ni'}
        assert get_current() == {}

    @staticmethod
    def test_base_weak():
        assert get_current() == {}
        with WeakThreadedContext(knights='ni', eki='patang'):
            assert get_current() == {'eki': 'patang', 'knights': 'ni'}
            with ThreadedContext(knights='round table', color='red'):
                assert get_current() == {'eki': 'patang',
                        'color': 'red', 'knights': 'round table'}
            assert get_current() == {'eki': 'patang', 'knights': 'ni'}
        assert get_current() == {}

    @staticmethod
    def test_double_weak():
        assert get_current() == {}
        with WeakThreadedContext(knights='ni', eki='patang'):
            assert get_current() == {'eki': 'patang', 'knights': 'ni'}
            with WeakThreadedContext(knights='round table', color='red'):
                assert get_current() == {'eki': 'patang',
                        'color': 'red', 'knights': 'round table'}
            assert get_current() == {'eki': 'patang', 'knights': 'ni'}
        assert get_current() == {}

    def test_as_decorator(self):
        self.assertEqual({}, get_current())
        @ThreadedContext(knights='round table', color='red')
        def wrapped():
            self.assertEqual({'eki': 'patang', 'color': 'red', 'knights': 'ni'},
                    get_current())
        @ThreadedContext(knights='ni', eki='patang')
        def wrapping():
            self.assertEqual({'eki': 'patang', 'knights': 'ni'}, get_current())
            wrapped()
            self.assertEqual({'eki': 'patang', 'knights': 'ni'}, get_current())
        wrapping()
        self.assertEqual({}, get_current())
