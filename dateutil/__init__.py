"""A tiny stub of the :mod:`python-dateutil` package used in the tests.

The original project depends on :mod:`python-dateutil`.  Installing optional
dependencies is not possible inside the execution environment, therefore we
bundle a very small portion of the functionality that is required by the unit
tests.  Only the :func:`parse` helper is implemented which mirrors the API of
``dateutil.parser.parse`` for the inputs used throughout the test-suite.
"""

from . import parser

__all__ = ["parser"]

