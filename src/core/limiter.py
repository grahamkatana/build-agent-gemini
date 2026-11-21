from slowapi import Limiter
from slowapi.util import get_remote_address

# Keyed by client IP address; uses in-memory storage out of the box
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
