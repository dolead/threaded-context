[![Build Status](https://travis-ci.org/dolead/threaded-context.svg?branch=master)](https://travis-ci.org/dolead/threaded-context)
[![Code Climate](https://codeclimate.com/github/dolead/threaded-context/badges/gpa.svg)](https://codeclimate.com/github/dolead/threaded-context)
[![Coverage Status](https://coveralls.io/repos/github/dolead/threaded-context/badge.svg?branch=master)](https://coveralls.io/github/dolead/threaded-context?branch=master)

```python
>>> with ThreadedContext(knights='ni', eki='patang'):
>>>     print(get_current())
>>>     with ThreadedContext(knights='round table', color='red'):
>>>         print(get_current())
>>>     print(get_current())
>>> print(get_current())
... {'eki': 'patang', 'knights': 'ni'}
... {'eki': 'patang', 'color': 'red', 'knights': 'ni'}
... {'eki': 'patang', 'knights': 'ni'}
... {}

# A weak context will be overrided by values declared in other context inside it.
>>> with WeakThreadedContext(knights='ni', eki='patang'):
>>>     print(get_current())
>>>     with ThreadedContext(knights='round table', color='red'):
>>>         print(get_current())
>>>     print(get_current())
>>> print(get_current())
... {'eki': 'patang', 'knights': 'ni'}
... {'eki': 'patang', 'color': 'red', 'knights': 'round table'}
... {'eki': 'patang', 'knights': 'ni'}
... {}

# Even if the context inside is also weak. The last weak or the first strong will prevail.
>>> with WeakThreadedContext(knights='ni', eki='patang'):
>>>     print(get_current())
>>>     with WeakThreadedContext(knights='round table', color='red'):
>>>         print(get_current())
>>>     print(get_current())
>>> print(get_current())
... {'eki': 'patang', 'knights': 'ni'}
... {'eki': 'patang', 'color': 'red', 'knights': 'round table'}
... {'eki': 'patang', 'knights': 'ni'}
... {}
```
