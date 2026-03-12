import unittest
from threaded_context import (get_current_context, reset_context,
                              update_current_context,
                              ThreadedContext, WeakThreadedContext,
                              BrutalThreadedContext)


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

    def test_post_mortem_context_on_exception(self):
        # Post-mortem should hold the innermost resolved context after exception
        with self.assertRaises(ValueError):
            with WeakThreadedContext(weak='weak', override='no'):
                with ThreadedContext(normal='normal', override='yes'):
                    with BrutalThreadedContext(brutal='brutal'):
                        raise ValueError('pipo')
        self.assert_context_equals({
            'weak': 'weak', 'override': 'yes',
            'normal': 'normal', 'brutal': 'brutal',
        })

    def test_post_mortem_cleared_on_reenter(self):
        # After an exception, entering a new context clears the post-mortem
        with self.assertRaises(ValueError):
            with ThreadedContext(key='value'):
                raise ValueError('pipo')
        self.assert_context_equals({'key': 'value'})
        with ThreadedContext(key='new'):
            self.assert_context_equals({'key': 'new'})
        self.assert_context_equals({})

    def test_post_mortem_cleared_by_reset(self):
        with self.assertRaises(ValueError):
            with ThreadedContext(key='value'):
                raise ValueError('pipo')
        self.assert_context_equals({'key': 'value'})
        reset_context()
        self.assert_context_equals({})

    def test_post_mortem_not_returned_inside_live_context(self):
        # While inside a live context, post-mortem must not bleed in
        with self.assertRaises(ValueError):
            with ThreadedContext(key='post'):
                raise ValueError('pipo')
        with ThreadedContext(key='live'):
            self.assert_context_equals({'key': 'live'})
        self.assert_context_equals({})

    def test_context_reusable_after_exception(self):
        # The exact scenario from the bug report: same context managers
        # must produce identical results whether or not a prior exception occurred
        def run():
            result = {}
            with WeakThreadedContext(weak='weak', weak_should_be_overrided='no'):
                with ThreadedContext(normal='normal',
                                     weak_should_be_overrided='yes',
                                     normal_should_be_overrided='no'):
                    with BrutalThreadedContext(brutal='brutal',
                                               normal_should_be_overrided='yes'):
                        result['brutal'] = get_current_context()
                    result['normal'] = get_current_context()
                result['weak'] = get_current_context()
            result['out'] = get_current_context()
            return result

        expected = {
            'brutal': {'weak': 'weak', 'weak_should_be_overrided': 'yes',
                       'normal': 'normal', 'normal_should_be_overrided': 'yes',
                       'brutal': 'brutal'},
            'normal': {'weak': 'weak', 'weak_should_be_overrided': 'yes',
                       'normal': 'normal', 'normal_should_be_overrided': 'no'},
            'weak':   {'weak': 'weak', 'weak_should_be_overrided': 'no'},
            'out':    {},
        }

        self.assertEqual(run(), expected)

        # Trigger an exception inside the same structure, then re-run
        with self.assertRaises(ValueError):
            with WeakThreadedContext(weak='weak', weak_should_be_overrided='no'):
                with ThreadedContext(normal='normal',
                                     weak_should_be_overrided='yes',
                                     normal_should_be_overrided='no'):
                    with BrutalThreadedContext(brutal='brutal',
                                               normal_should_be_overrided='yes'):
                        raise ValueError('pipo')

        self.assertEqual(run(), expected)

    def test_resilient_thread_type(self):
        self.assert_context_equals({})
        with WeakThreadedContext(knights='ni'):
            self.assert_context_equals({'knights': 'ni'})
            with ThreadedContext(color='red'):
                self.assert_context_equals({'knights': 'ni', 'color': 'red'})
                with WeakThreadedContext(knights='eki'):
                    self.assert_context_equals({'knights': 'eki',
                                                'color': 'red'})
