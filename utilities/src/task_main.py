#!/usr/bin/python
"""Main implementation of executing system checks/operations."""

import argparse
import conduit
import task_today
import task_ping
import task_onsub
import task_duedates
import task_unmod


WEEKLY = "weekly"
DAILY = "daily"

PHAB_ENV = "PHAB_"


class Settings(object):
    """Settings object."""

    def __init__(self):
        """Init instance."""
        self._environ = self._init_env()
        self.host = self._env("HOST")
        self.common_room = self._env("COMMON_ROOM")
        self.task_factory = self._create_factory(self._env("TASK_TOKEN"))
        self.monitor_factory = self._create_factory(self._env("MON_TOKEN"))
        self.bot_room = self._env("BOT_ROOM")
        self.status_factory = self._create_factory(self._env("STATUS_TOKEN"))
        self.admin_project = self._env("ADMIN_PROJ")
        self.domain = self._env("CHECK_DOMAIN")
        self.hosts = self._env("CHECK_HOSTS").split(' ')

    def _init_env(self):
        """init env variables."""
        res = {}
        with open("/etc/environment", 'r') as f:
            for line in f.readlines():
                if line.startswith(PHAB_ENV):
                    idx = line.index("=")
                    name = line[0:idx]
                    val = line[idx + 1:].strip()
                    if val.startswith("\""):
                        val = val[1:]
                    if val.endswith("\""):
                        val = val[:len(val) - 1]
                    res[name] = val
        return res

    def check_hosts(self):
        """Host(s) to check for being up."""
        yield self.domain
        for host in self.hosts:
            yield host + "." + self.domain

    def _env(self, name):
        """Get an environment variable."""
        return self._environ[PHAB_ENV + name]

    def _create_factory(self, token):
        """Create a factory."""
        factory = conduit.Factory()
        factory.host = self.host
        factory.token = token
        return factory


def main():
    """Entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode",
                        required=True,
                        type=str,
                        choices=[WEEKLY, DAILY])
    args = parser.parse_args()
    settings = Settings()
    if args.mode == DAILY:
        task_duedates.process(settings.task_factory,
                              task_duedates.RESOLVE_OVER)
        task_today.process(settings.monitor_factory, settings.bot_room)
        task_onsub.process(settings.monitor_factory,
                           settings.bot_room,
                           settings.admin_project)
        task_ping.check(settings.status_factory,
                        settings.bot_room,
                        settings.check_hosts())
    else:
        if args.mode == WEEKLY:
            task_duedates.process(settings.task_factory,
                                  task_duedates.COMMENT_OVER)
            task_unmod.process(settings.task_factory,
                               settings.host,
                               settings.common_room,
                               30,
                               45)
    task_ping.process(settings.status_factory,
                      settings.bot_room,
                      "{0} executed".format(args.mode))

if __name__ == '__main__':
    main()
