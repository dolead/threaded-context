# threaded-context

Thread-safe context manager with nested inheritance and conflict resolution strategies for Python.

## Install

```bash
pip install threaded-context
```

## Usage

```python
from threaded_context import (
    ThreadedContext, WeakThreadedContext,
    get_current_context,
)

# Contexts nest and merge — inner values are visible alongside outer ones.
# With ThreadedContext (strong), the outer value wins on conflict.
with ThreadedContext(knights='ni', eki='patang'):
    print(get_current_context())
    # {'eki': 'patang', 'knights': 'ni'}
    with ThreadedContext(knights='round table', color='red'):
        print(get_current_context())
        # {'eki': 'patang', 'color': 'red', 'knights': 'ni'}
    print(get_current_context())
    # {'eki': 'patang', 'knights': 'ni'}
print(get_current_context())
# {}

# With WeakThreadedContext, inner contexts can override the outer values.
with WeakThreadedContext(knights='ni', eki='patang'):
    print(get_current_context())
    # {'eki': 'patang', 'knights': 'ni'}
    with ThreadedContext(knights='round table', color='red'):
        print(get_current_context())
        # {'eki': 'patang', 'color': 'red', 'knights': 'round table'}
    print(get_current_context())
    # {'eki': 'patang', 'knights': 'ni'}
print(get_current_context())
# {}
```

## Context types

| Class | Behavior |
|---|---|
| `ThreadedContext` | Strong — this level's values win over children's |
| `WeakThreadedContext` | Weak — children can override this level's values |
| `BrutalThreadedContext` | Strong + forcefully overrides parent values |
| `WeakBrutalThreadedContext` | Weak + forcefully overrides parent values |

All context classes work as both context managers and decorators.

## Development

```bash
make test    # run tests
make lint    # pycodestyle, black, flake8, pylint, mypy
make build   # clean + lint + test + build
```
