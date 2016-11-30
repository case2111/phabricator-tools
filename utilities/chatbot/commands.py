#!/usr/bin/python
"""Commands for bot."""

ECHO_CMD = "echo"
HELP_CMD = "help"
CHAT_CMD = "chat"
DEBUG_CMD = "debug"
DEBUG_CMDS = [ECHO_CMD, CHAT_CMD, DEBUG_CMD]
ALL_CMDS = [HELP_CMD]

class Context(object):
    """Context for executing commands."""

    CONPH = "conph"
    ROOM_PHID = "room_phid"
    BOT_USER_PHID = "bot_user_phid"
    BOT_USER = "bot_user"
    LAST_TRANS = "last_transactions."
    CHATBOT = "chatbot"
    DEBUG = "debug"

    def __init__(self):
        """init instance."""
        self.cache = {}
        self.cache[Context.DEBUG] = False

    def get(self, key):
        """get a value."""
        if key in self.cache:
            return self.cache[key]
        else:
            return None

    def test(self, key):
        """test for a key."""
        return key in self.cache

    def set(self, key, val):
        """set a value."""
        self.cache[key] = val


def _updatethread(ctx, room_id, msg):
    """Update a conpherence thread."""
    ctx.get(Context.CONPH).updatethread(room_id, msg)


def execute(command, parameters, room_id, ctx, debugging):
    """Execute a command."""
    debug = ctx.get(Context.DEBUG)
    if command == ECHO_CMD and debug:
        _updatethread(ctx, room_id, " ".join(parameters))
    elif command == CHAT_CMD and debug:
        from chatterbot import ChatBot
        chatty = ctx.get(Context.CHATBOT)
        if chatty is None:
            chatty = ChatBot("chatbot", trainer='chatterbot.trainers.ChatterBotCorpusTrainer')
            chatty.train("chatterbot.corpus.english")
            ctx.set(Context.CHATBOT, chatty)
        if len(parameters) == 0:
            resp = "/silence"
        else:
            resp = chatty.get_response(" ".join(parameters))
        _updatethread(ctx, room_id, str(resp))
    elif command == DEBUG_CMD and debugging:
        ctx.set(Context.DEBUG, not debug)
        _updatethread(ctx, room_id, "debug mode toggled")
    else:
        use_cmds = ALL_CMDS
        if debug:
            use_cmds += DEBUG_CMDS
        _updatethread(ctx, room_id, "available: " + ",".join(sorted(use_cmds)))
