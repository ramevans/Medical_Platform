from .device import DEVICES_API_BLUEPRINT # noqa: F401
from .data import DATA_API_BLUEPRINT # noqa: F401
from .chat import MESSAGES_API_BLUEPRINT # noqa: F401
from .users import USERS_API_BLUEPRINT # noqa: F401
try:
    # Some of the dependencies for speech-to-text may not
    # be available in all setups.
    from .speech2text import S2T_BLUEPRINT_API # noqa: F401
except ImportError:
    pass
