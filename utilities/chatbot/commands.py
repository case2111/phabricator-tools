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


def _create_chatbot():
    """Create a chatbot."""
    from chatterbot import ChatBot
    chat = ChatBot("chatbot",
                   trainer='chatterbot.trainers.ChatterBotCorpusTrainer')
    chat.train("chatterbot.corpus.english")
    return chat


def execute(command, parameters, room_id, ctx, debugging):
    """Execute a command."""
    try:
        cmd = command
        debug = ctx.get(Context.DEBUG)
        if not debug and command in DEBUG_CMDS:
            cmd = HELP_CMD
        if cmd == ECHO_CMD:
            _updatethread(ctx, room_id, " ".join(parameters))
        elif cmd == CHAT_CMD:
            chatty = ctx.get(Context.CHATBOT)
            if chatty is None:
                chatty = _create_chatbot()
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
            _updatethread(ctx,
                          room_id,
                          "available: " + ",".join(sorted(use_cmds)))
    except Exception as e:
        _updatethread(ctx, room_id, str(e))
