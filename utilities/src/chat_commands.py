#!/usr/bin/python
"""Commands for bot."""
import conduit
import time
import pdf_from_phriction
import pdf_from_diffusion
import random
import os

ECHO_CMD = "echo"
HELP_CMD = "help"
CHAT_CMD = "chat"
DEBUG_CMD = "debug"
ALIVE_CMD = "alive"
REBOOT_CMD = "reboot"
STATUS_CMD = "status"
GEN_PAGE_CMD = "genpage"
PDF_FROM_REPO = "repo2pdf"
PDF_FROM_WIKI = "wiki2pdf"
DEBUG_CMDS = [ECHO_CMD, CHAT_CMD, DEBUG_CMD]
ALL_CMDS = [HELP_CMD, ALIVE_CMD, STATUS_CMD, REBOOT_CMD]
ADMIN_CMDS = [ALIVE_CMD, REBOOT_CMD, STATUS_CMD, GEN_PAGE_CMD]

PHAB_TOOL_TYPE = "phabtools"


class Context(object):
    """Context for executing commands."""

    CONPH = "conph"
    ROOM_PHID = "room_phid"
    BOT_USER_PHID = "bot_user_phid"
    BOT_USER = "bot_user"
    LAST_TRANS = "last_transactions."
    CHATBOT = "chatbot"
    DEBUG = "debug"
    FACTORY = "factory"
    ADMINS = "admins"
    LOCK_FILE = "lock_file"
    STARTED = "started"
    CONFIG = "config"

    def __init__(self, factory):
        """init instance."""
        self.cache = {}
        self.cache[Context.DEBUG] = False
        self.cache[Context.FACTORY] = factory
        self.factory_obj(Context.CONPH, conduit.Conpherence)

    def get(self, key):
        """get a value."""
        if key in self.cache:
            return self.cache[key]
        else:
            return None

    def set(self, key, val):
        """set a value."""
        self.cache[key] = val

    def factory_obj(ctx, key, obj_type):
        """Get (or create -> get) a factory-backed object."""
        obj = ctx.get(key)
        if obj is None:
            obj = ctx.get(Context.FACTORY).create(obj_type)
            ctx.set(key, obj)
        return obj


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


def _reboot(lock_file):
    """reboot the monitor."""
    import os
    try:
        os.remove(lock_file)
    except OSError:
        return


def get_opts(options):
    """Get the backing options for the worker."""
    if options == PHAB_TOOL_TYPE:
        return PhabTools
    else:
        raise Exception("unknown options: " + options)


class OptionCommand(object):
    """Base option context."""

    def __init__(self, command, parameters, room_id, ctx, debugging, is_admin):
        """Init the instance."""
        self.cmd = command
        self.params = parameters
        self.room = room_id
        self.context = ctx
        self.debug = debugging
        self.admin = is_admin
        use_supported = self._support()
        self.supported = []
        cfg = ctx.get(Context.CONFIG)
        if self.cmd in cfg:
            self.config = cfg[self.cmd]
        else:
            self.config = {}
        if self.admin:
            self.supported = use_supported
        else:
            for sup in use_supported:
                if sup not in ADMIN_CMDS:
                    self.supported.append(sup)

    def _support(self):
        """Get supported commands."""
        raise Exception("must implement support")

    def operate(self):
        """Operate the context."""
        if self.cmd in self.supported and self.is_command():
            self._operate()
            return True
        else:
            return False

    def is_command(self):
        """Check if this is a command for this option set."""
        raise Exception("must implement is_command")

    def _operate(self):
        """Run the operation."""
        raise Exception("must implement operate")


class PhabTools(OptionCommand):
    """Phabricator co-located tooling."""

    def _support(self):
        return [GEN_PAGE_CMD, PDF_FROM_WIKI, PDF_FROM_REPO]

    def is_command(self):
        """inherited."""
        if self.cmd == GEN_PAGE_CMD:
            if len(self.params) == 5:
                return True
            else:
                raise Exception("requires parameters: " + ",".join(["slug",
                                                                    "title",
                                                                    "path",
                                                                    "callsign",
                                                                    "branch"]))
        elif self.cmd == PDF_FROM_WIKI:
            if len(self.params) == 1:
                return True
            else:
                raise Exception("requires a slug parameter")
        elif self.cmd == PDF_FROM_REPO:
            if len(self.params) == 3:
                return True
            else:
                raise Exception("requires parameters: " + ",".join(["path",
                                                                    "callsign",
                                                                    "branch"]))
        else:
            return False

    def _operate(self):
        """inherited."""
        factory = self.context.get(Context.FACTORY)
        if self.cmd == GEN_PAGE_CMD:
            import diffusion_phriction
            time.sleep(self.config["sleep"])
            slug = self.params[0]
            diffusion_phriction._process(factory,
                                         slug,
                                         self.params[1],
                                         self.params[2],
                                         self.params[3],
                                         self.params[4])
            _updatethread(self.context,
                          self.room,
                          "[[{0}]] page updated".format(slug))
        elif self.cmd == PDF_FROM_WIKI or self.cmd == PDF_FROM_REPO:
            file_name = self._get_artifact_path().replace(".", "")
            output_path = os.path.join(self.config["path"], file_name)
            if self.cmd == PDF_FROM_WIKI:
                pdf_from_phriction._get(factory,
                                        self.params[0],
                                        output_path)
            if self.cmd == PDF_FROM_REPO:
                pdf_from_diffusion._get(factory,
                                        self.params[0],
                                        self.params[1],
                                        self.params[2],
                                        output_path)
            _updatethread(self.context,
                          self.room,
                          "download: {0}/sfh/{1}.pdf".format(factory.host,
                                                             file_name))

    def _get_artifact_path(self):
        return "{0}{1}".format(time.time(),
                               random.randint(0, 2147483647))


def execute(command, parameters, room_id, ctx, debugging, is_admin, added_ctx):
    """Execute a command."""
    try:
        options = added_ctx(command,
                            parameters,
                            room_id,
                            ctx,
                            debugging,
                            is_admin)
        if options.operate():
            return
        cmd = command
        debug = ctx.get(Context.DEBUG)
        if not debug and command in DEBUG_CMDS:
            cmd = HELP_CMD
        if not is_admin and (command in ADMIN_CMDS or command in DEBUG_CMDS):
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
        elif cmd == ALIVE_CMD:
            _updatethread(ctx, room_id, "yes")
        elif cmd == REBOOT_CMD:
            _reboot(ctx.get(Context.LOCK_FILE))
        elif cmd == STATUS_CMD:
            _updatethread(ctx, room_id, ctx.get(Context.STARTED))
        else:
            use_cmds = ALL_CMDS + options.supported
            if debug:
                use_cmds += DEBUG_CMDS
            msg = []
            for commands in sorted(use_cmds):
                flavor = commands
                added = ""
                if commands in ADMIN_CMDS:
                    added = " (admin/agent)"
                if commands in DEBUG_CMDS:
                    added = " (debug)"
                msg.append(flavor + added)
            _updatethread(ctx,
                          room_id,
                          "available: " + " , ".join(msg))
    except Exception as e:
        _updatethread(ctx, room_id, str(e))
