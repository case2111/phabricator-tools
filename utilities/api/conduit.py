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
    def _build(self, name, value):
        """build a parameter for posting."""
        return name + "=" + value

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


class User(ConduitBase):
    """User implementation."""
    def by_phids(self, phids):
        """user by phid."""
        return self._query({"phids": phids})
    def _query(self, params=None):
        """Query users."""
        return self._get("query", params)
    def _get(self, op, params=None):
        """Get data."""
        return self._execute("user." + op, params)


class Conpherence(ConduitBase):
    """Conpherence implementation."""
    def updatethread(self, room, message):
        """Update a conpherence thread."""
        return self._post("updatethread", {"id": room, "message": message})
    def _post(self, op, params=None):
        """Post to a conpherence endpoint."""
        return self._execute("conpherence." + op, params)


class Maniphest(ConduitBase):
    """Maniphest implementation."""
    def open(self):
        """Open tasks."""
        return self._query({"status": "status-open"}) 
    def _query(self, params=None):
        """Query operations."""
        return self._get("query", params)
    def _get(self, op, params=None):
        """Get a maniphest data payload."""
        return self._execute("maniphest." + op, params)
