# this is where flask finds the entry point for the application.

from aspen.app.app import application  # noqa: F401
from aspen.app.views.auth import callback_handling, login, logout  # noqa: F401
from aspen.app.views.health import health  # noqa: F401
from aspen.app.views.index import serve  # noqa: F401
from aspen.app.views.phylo_trees import phylo_trees  # noqa: F401
from aspen.app.views.sample import samples  # noqa: F401
from aspen.app.views.usergroup import usergroup  # noqa: F401
from aspen.app.views.auspice import auspice # noqa: F401
