from .unknown_domain import UnknownDomain
from .test import test, get_domain

from .domains import domains as _domains

domains = set(_domains.keys())
