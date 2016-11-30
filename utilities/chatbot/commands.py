#!/usr/bin/python
"""Commands for bot."""

ECHO_CMD = "echo"
HELP_CMD = "help"
CMD_HELP = "available commands: " + " ".join(sorted([ECHO_CMD, HELP_CMD]))


class Context(object):
    """Context for executing commands."""

    CONPH = "conph"
    ROOM_PHID = "room_phid"
    BOT_USER_PHID = "bot_user_phid"
    BOT_USER = "bot_user"
    LAST_TRANS = "last_transactions."

    def __init__(self):
        """init instance."""
        self.cache = {}

    def get(self, key):
        """get a value."""
        return self.cache[key]

    def set(self, key, val):
        """set a value."""
        self.cache[key] = val


def _updatethread(ctx, room_id, msg):
    """Update a conpherence thread."""
    ctx.get(Context.CONPH).updatethread(room_id, msg)


def execute(command, parameters, room_id, ctx):
    """Execute a command."""
    if command == ECHO_CMD:
        _updatethread(ctx, room_id, " ".join(parameters))
    else:
        _updatethread(ctx, room_id, CMD_HELP)
