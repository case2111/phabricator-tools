#!/usr/bin/python
"""Commands for bot."""
import conduit
import os
import diffusion_phriction
import pdf_from_diffusion
import pdf_from_phriction
import time
import random
import task_today
import task_ping
import task_onsub
import task_duedates
import task_unmod


class Bot(object):
    """Bot definition."""

    ALIVE = "alive"
    STATUS = "status"
    REBOOT = "reboot"

    class Package(object):
        """Package of a command."""

        def __init__(self, command, parameters, admin):
            """Init the instance."""
            self.cmd = command
            self.params = parameters
            self.is_admin = admin

    def __init__(self):
        """Init the instance."""
        self.room = None
        self.ctx = None

    def go(self, command, parameters, is_admin, is_all):
        """Execute a bot command."""
        try:
            print("{0} ({1}) admin? {2}, all? {3}".format(command,
                                                          ",".join(parameters),
                                                          is_admin,
                                                          is_all))
            pkg = Bot.Package(command, parameters, is_admin)
            common = False
            if is_all:
                common = True
            else:
                if not self._go(pkg):
                    common = True
            if common:
                self._common(pkg)
        except Exception as e:
            print(e)
            if is_admin:
                self._chat(str(e))
            else:
                self._chat("unable to process request")

    def _go(self, pkg):
        """bot implementation."""
        pass

    def _get_help(self, pkg):
        """bot help."""
        return {}

    def _common(self, pkg):
        """common commands."""
        no_cmd = True
        if pkg.is_admin:
            if pkg.cmd == self.REBOOT:
                self._reboot()
                no_cmd = False
        need_help = False
        if no_cmd:
            if pkg.cmd == self.ALIVE:
                self._alive()
            elif pkg.cmd == self.STATUS:
                self._status()
            else:
                need_help = True
        if need_help:
            self._help(pkg)

    def _chat(self, msg):
        """send a chat message."""
        self.ctx.get(Context.CONPH).updatethread(self.room, msg)

    def _help(self, pkg):
        """get bot help."""
        help_items = self._get_help(pkg)
        help_items[self.ALIVE] = "check if the bot is alive in chat"
        help_items[self.STATUS] = "check bot status"
        if pkg.is_admin:
            help_items[self.REBOOT] = "reboot the bot"
        text = []
        for key in help_items:
            txt = "{0} -> {1}".format(key, help_items[key])
            text.append(txt)
        self._chat("\n".join(text))

    def _status(self):
        """check status call."""
        self._chat(self.ctx.get(Context.STARTED))

    def _alive(self):
        """alive call."""
        self._chat("yes")

    def _reboot(self):
        """reboot call."""
        try:
            os.remove(self.ctx.get(Context.LOCK))
        except OSError:
            return

    def _subcommand_help(self, pkg, params):
        """subcommand help output."""
        self._chat("{0} requires parameters:\n{1}".format(pkg.cmd,
                                                          "\n".join(params)))


class PruneBot(Bot):
    """Pruner bot."""

    DO = "do"
    DAILY = "daily"
    WEEKLY = "weekly"

    def _go(self, pkg):
        """inherited."""
        if pkg.is_admin and pkg.cmd == self.DO:
            if len(pkg.params) == 1:
                tasks = pkg.params[0]
                if tasks == self.DAILY or tasks == self.WEEKLY:
                    settings = PruneBot.Settings(self.ctx)
                    if tasks == self.DAILY:
                        self._daily(settings)
                    else:
                        self._weekly(settings)
                    self._chat("{0} tasks completed".format(tasks))
                    return True
            self._subcommand_help(pkg, [self.DAILY + " or " + self.WEEKLY])

    def _daily(self, settings):
        """daily tasks."""
        task_duedates.process(settings.task_factory,
                              task_duedates.RESOLVE_OVER)
        task_today.process(settings.monitor_factory, settings.bot_room)
        task_onsub.process(settings.monitor_factory,
                           settings.bot_room,
                           settings.admin_project)
        task_ping.check(settings.status_factory,
                        settings.bot_room,
                        settings.check_hosts())

    def _weekly(self, settings):
        """weekly tasks."""
        task_duedates.process(settings.task_factory,
                              task_duedates.COMMENT_OVER)
        task_unmod.process(settings.task_factory,
                           settings.host,
                           settings.common_room,
                           30,
                           45)

    def _get_help(self, pkg):
        """Inherited."""
        if pkg.is_admin:
            return {self.DO: "do a set of scheduled/enumerated tasks."}
        else:
            return {}

    class Settings(object):
        """Settings object."""

        def __init__(self, ctx):
            """Init instance."""
            self.host = ctx.factory.host
            self.common_room = ctx.env("COMMON_ROOM")
            self.task_factory = self._factory(ctx, "TASK_TOKEN")
            self.monitor_factory = self._factory(ctx, "MON_TOKEN")
            self.bot_room = ctx.bots
            self.status_factory = self._factory(ctx, "STATUS_TOKEN")
            self.admin_project = ctx.env("ADMIN_PROJ")
            self.domain = ctx.env("CHECK_DOMAIN")
            self.hosts = ctx.env("CHECK_HOSTS").split(' ')

        def _factory(self, ctx, token):
            """create/clone a factory."""
            factory = conduit.Factory()
            factory.host = ctx.factory.host
            factory.token = ctx.env(token)
            return factory

        def check_hosts(self):
            """Host(s) to check for being up."""
            yield self.domain
            for host in self.hosts:
                yield host + "." + self.domain


class MonitorBot(Bot):
    """Monitor bot."""

    GEN_PAGE = "genpage"
    PDF_WIKI = "wiki2pdf"
    PDF_REPO = "repo2pdf"

    def _go(self, pkg):
        """inherited."""
        if pkg.cmd == self.GEN_PAGE and pkg.is_admin:
            if len(pkg.params) == 4:
                slug = pkg.params[0]
                time.sleep(int(self.ctx.env("MON_SLEEP")))
                diffusion_phriction._process(self.ctx.factory,
                                             slug,
                                             pkg.params[1],
                                             pkg.params[3],
                                             pkg.params[2][1:],
                                             "master")
                self._chat("[[{0}]] page updated".format(slug))
            else:
                self._subcommand_help(pkg,
                                      ["slug", "title", "callsign", "path"])
            return True
        elif pkg.cmd == self.PDF_WIKI:
            if len(pkg.params) == 1:
                self._pdf(pkg)
            else:
                self._subcommand_help(pkg, ["slug"])
            return True
        elif pkg.cmd == self.PDF_REPO:
            if len(pkg.params) == 2:
                self._pdf(pkg)
            else:
                self._subcommand_help(pkg, ["callsign", "path"])
            return True

    def _pdf(self, pkg):
        """do pdf conversion steps."""
        file_name = self._get_artifact_path().replace(".", "")
        output_path = os.path.join(self.ctx.env("MON_PATH"), file_name)
        if pkg.cmd == self.PDF_WIKI:
            pdf_from_phriction._get(self.ctx.factory,
                                    pkg.params[0],
                                    output_path)
        else:
            pdf_from_diffusion._get(self.ctx.factory,
                                    pkg.params[1],
                                    pkg.params[0][1:],
                                    "master",
                                    output_path)
        self._chat(
                "{0}\n{1}".format(
                    "download: {0}/sfh/{1}.pdf".format(
                        self.ctx.factory.host,
                        file_name),
                    "this download will expire at the end of the day"))

    def _get_artifact_path(self):
        """get an artifact output file name."""
        return "{0}{1}".format(time.time(),
                               random.randint(0, 2147483647))

    def _get_help(self, pkg):
        """inherited."""
        avail = {self.PDF_WIKI: "produce a pdf from a phriction page",
                 self.PDF_REPO: "produce a pdf from a repository/path"}
        if pkg.is_admin:
            avail[self.GEN_PAGE] = "generate a wiki page from a repo/path"
        return avail


def bot(bot_type):
    """create bots of types."""
    if bot_type == "monitor":
        return MonitorBot()
    elif bot_type == "prune":
        return PruneBot()
    else:
        raise Exception("unknown bot type: " + bot_type)


class Context(object):
    """Context for executing commands."""

    CONPH = "conph"
    ROOM_PHID = "room_phid"
    BOT_USER_PHID = "bot_user_phid"
    BOT_USER = "bot_user"
    LAST_TRANS = "last_transactions."
    ADMINS = "admins"
    STARTED = "started"
    LOCK = "lock_file"

    def env(self, key):
        """environment variables."""
        if key not in self.cache:
            with open("/etc/environment", 'r') as f:
                for line in f.readlines():
                    if "=" in line:
                        parts = line.split("=")
                        if parts[0] == "PHAB_" + key:
                            self.cache[key] = parts[1][1:len(parts[1]) - 2]
        return self.cache[key]

    def __init__(self, factory):
        """init instance."""
        self.cache = {}
        self.factory = factory
        self.api(Context.CONPH, conduit.Conpherence)
        self.bots = self.env("BOT_ROOM")

    def get(self, key):
        """get a value."""
        if key in self.cache:
            return self.cache[key]
        else:
            return None

    def set(self, key, val):
        """set a value."""
        self.cache[key] = val

    def api(self, key, obj_type):
        """Get (or create -> get) a factory-backed object."""
        obj = self.get(key)
        if obj is None:
            obj = self.factory.create(obj_type)
            self.set(key, obj)
        return obj