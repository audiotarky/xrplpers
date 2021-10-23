# xrplpers

_A pun on XRPL Helpers_

A collection of little helper functions, to grow as we do more with the ledger.

## Setup

Recommend you use a venv:

```
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip setuptools
```

If you want a dev environment (installs black & mypy):

```
pip install -q -e .[dev] --upgrade --upgrade-strategy eager
```

If you just want the library:

```
pip install -q . --upgrade --upgrade-strategy eager
```

## Developing

Code should autoformat with black.

### Testing & type checking

```
python -m unittest test/*.py
mypy xrplpers/
```
