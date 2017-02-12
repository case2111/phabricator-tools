#!/usr/bin/python
"""Commands for bot."""
import conduit
import os
import diffusion_phriction
import pdf_from_diffusion
import pdf_from_phriction
import time
import random
import task_ping
import task_onsub
import task_duedates
import task_unmod
import git_version
import dash_from_phriction
import database
import uuid
import maniphest_tag_index


class Bot(object):
    """Bot definition."""

    ALIVE = "alive"
    STATUS = "status"
    REBOOT = "reboot"
    VERSION = "version"
    MON_BOT_TYPE = "monitor"
    SCHED_BOT_TYPE = "schedule"
    BOT_TYPES = [MON_BOT_TYPE, SCHED_BOT_TYPE]

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
        self.id = str(uuid.uuid4())
        self.named = None

    def go(self, command, parameters, is_admin, is_all):
        """Execute a bot command."""
        try:
            print("{0} ({1}) admin? {2}, all? {3}, id: {4}"
                  .format(command,
                          ",".join(parameters),
                          is_admin,
                          is_all,
                          self.id))
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
                self._chat("rebooting...")
                self._reboot()
                no_cmd = False
            if pkg.cmd == self.VERSION:
                vers = git_version._version(self.ctx.env("TOOLS"))
                self._chat(vers)
                no_cmd = False
        if no_cmd:
            if pkg.cmd == self.ALIVE:
                self._alive()
            elif pkg.cmd == self.STATUS:
                self._status()
        if pkg.cmd == "help":
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
            help_items[self.VERSION] = "get version information (git)"
        text = []
        for key in sorted(help_items.keys()):
            txt = "{0} -> {1}".format(key, help_items[key])
            text.append(txt)
        self._chat("\n".join(text))

    def _status(self):
        """check status call."""
        self._chat(self.ctx.get(Context.STARTED) + ", " + self.id)

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

    def _dash_from_wiki(self):
        """Dashboard from wiki page."""
        obj = self.ctx.env("DASH_OBJECT")
        slug = self.ctx.env("DASH_WIKI")
        dash_from_phriction.update(self.ctx.factory, slug, obj)

    def _index_now(self, quiet):
        """index now."""
        maniphest_tag_index._process(self.ctx.factory,
                                     self.ctx.env("CHECK_IDX"),
                                     self.ctx.env("VALID_IDX"),
                                     self.ctx.bots,
                                     quiet)


class ScheduleBot(Bot):
    """Schedule bot."""

    DO = "do"
    DAILY = "daily"
    WEEKLY = "weekly"

    def _go(self, pkg):
        """inherited."""
        if pkg.is_admin and pkg.cmd == self.DO:
            if len(pkg.params) == 1:
                tasks = pkg.params[0]
                if tasks == self.DAILY or tasks == self.WEEKLY:
                    settings = ScheduleBot.Settings(self.ctx)
                    self._chat("starting {0} tasks".format(tasks))
                    if tasks == self.DAILY:
                        self._daily(settings)
                    else:
                        self._weekly(settings)
                    self._chat("{0} tasks completed".format(tasks))
                    return True
            self._subcommand_help(pkg, [self.DAILY + " or " + self.WEEKLY])

    def _daily(self, settings):
        """daily tasks."""
        task_onsub.process(settings.monitor_factory,
                           settings.bot_room,
                           settings.admin_project)
        task_ping.check(settings.status_factory,
                        settings.bot_room,
                        settings.check_hosts())
        self._dash_from_wiki()
        self._index_now(True)

    def _weekly(self, settings):
        """weekly tasks."""
        task_duedates.process(settings.task_factory)
        database.user_check(settings.db_user,
                            settings.db_pass,
                            settings.monitor_factory,
                            settings.bot_room)
        task_unmod.process(settings.monitor_factory,
                           settings.common_room,
                           settings.autoclose_threshold,
                           settings.autoclose_proj)

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
            self.db_user = ctx.env("DB_USER")
            self.db_pass = ctx.env("DB_PASS")
            self.autoclose_threshold = int(ctx.env("AUTOCLOSE_THRESH"))
            self.autoclose_proj = ctx.env("AUTOCLOSE_PROJ")

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
    DASH_WIKI = "wiki2dash"
    IDX_VALID = "index"

    def _go(self, pkg):
        """inherited."""
        if pkg.cmd == self.GEN_PAGE and pkg.is_admin:
            if len(pkg.params) >= 4:
                slug = pkg.params[0]
                self._chat("generating please hold...")
                time.sleep(int(self.ctx.env("MON_SLEEP")))
                main_idx = 0
                sec_idx = 1
                if len(pkg.params) >= 5:
                    main_idx = int(pkg.params[4])
                    if len(pkg.params) == 6:
                        sec_idx = int(pkg.params[5])
                diffusion_phriction._process(self.ctx.factory,
                                             slug,
                                             pkg.params[1],
                                             pkg.params[3],
                                             pkg.params[2][1:],
                                             "master",
                                             diffusion_phriction.CSV_CONVERT,
                                             main_idx,
                                             sec_idx)
                self._chat("[[{0}]] page updated".format(slug))
            else:
                self._subcommand_help(pkg,
                                      ["slug",
                                       "title",
                                       "callsign",
                                       "path",
                                       "main index (optional)",
                                       "secondary index (optional)"])
            return True
        elif pkg.cmd == self.DASH_WIKI and pkg.is_admin:
            self._dash_from_wiki()
            self._chat("dashboard updated")
            return True
        elif pkg.cmd == self.IDX_VALID and pkg.is_admin:
            self._index_now(False)
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
            avail[self.DASH_WIKI] = "update dashboard panel from wiki"
            avail[self.IDX_VALID] = "validate index values"
        return avail


def bot(bot_type):
    """create bots of types."""
    if bot_type == Bot.MON_BOT_TYPE:
        return MonitorBot()
    elif bot_type == Bot.SCHED_BOT_TYPE:
        return ScheduleBot()
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
