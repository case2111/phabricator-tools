#!/usr/bin/python
"""Conduit helpers."""

from io import BytesIO
import json
import pycurl


class Factory:
    """Common case to create conduit-derived classes."""
    token = None
    host = None
    def create(self, obj_type):
        """Create an instance."""
        obj = obj_type()
        obj.token = self.token
        obj.host = self.host
        return obj


class ConduitBase(object):
    """Conduit common operations."""
    token = None
    host = None
    prefix = None
    def _build(self, name, value):
        """build a parameter for posting."""
        return name + "=" + value

    def _go(self, operator, params=None):
        """run an operation."""
        if self.prefix is None:
            raise Exception("no prefix configured")
        return self._execute(self.prefix + "." + operator, params)

    def _execute(self, endpoint, parameters=None):
        """Execute a conduit query."""
        if self.token is None:
            raise Exception("no token given...")
        if self.host is None:
            raise Exception("no host given...")
        curl = pycurl.Curl()
        curl.setopt(curl.URL, self.host + "/" + endpoint)
        # post-data
        fields = []
        fields.append(self._build("api.token", self.token))
        if parameters is not None and len(parameters) > 0:
            for p in parameters:
                vals = parameters[p]
                if isinstance(vals, str):
                    fields.append(self._build(p, vals))
                else:
                    idx = 0
                    for elem in vals:
                        fields.append(self._build(p + "[" + str(idx) + "]",
                                                  elem))
                        idx = idx + 1
        posting = "&".join(fields)
        buf = BytesIO()
        curl.setopt(curl.POSTFIELDS, posting);
        curl.setopt(curl.WRITEDATA, buf)
        curl.perform()
        # and data back
        res = json.loads(buf.getvalue().decode("iso-8859-1"))
        errored = res["error_code"]
        if errored is None:
            return res["result"]
        else:
            raise Exception(res["error_info"])


class Project(ConduitBase):
    """Project queries."""
    def __init__(self):
        """init the instance."""
        self.prefix = "project"

    """Project implementation."""
    def open(self):
        """Open projects."""
        return self._go("query", {"status": "status-open"})

class User(ConduitBase):
    """User implementation."""
    def __init__(self):
        """init the instance."""
        self.prefix = "user"

    def by_phids(self, phids):
        """user by phid."""
        return self._query({"phids": phids})

    def _query(self, params=None):
        """Query users."""
        return self._go("query", params)


class Conpherence(ConduitBase):
    """Conpherence implementation."""
    def __init__(self):
        """init the instance."""
        self.prefix = "conpherence"

    def updatethread(self, room, message):
        """Update a conpherence thread."""
        return self._go("updatethread", {"id": room, "message": message})

class Maniphest(ConduitBase):
    """Maniphest implementation."""
    def __init__(self):
        """init the instance."""
        self.prefix = "maniphest"

    def comment_by_id(self, task_id, message):
        """comment on a task by using the id."""
        return self._update({"id": task_id, "comments": message})

    def open(self):
        """Open tasks."""
        return self._query(self._open_params())
    
    def open_by_project_phids(self, project_phids):
        """Open by project phid."""
        return self._query(self._open_params({"projectPHIDs": project_phids}))

    def _open_params(self, added=None):
        """Open status parameter building."""
        obj = {"status": "status-open"}
        if added:
            for k in added:
                obj[k] = added[k]
        return obj

    def _update(self, params=None):
        """task updates."""
        return self._go("update", params)

    def _query(self, params=None):
        """Query operations."""
        return self._go("query", params)
