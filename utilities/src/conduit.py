#!/usr/bin/python
"""Conduit helpers."""

from io import BytesIO
import json
from urllib.parse import urlencode, quote
import pycurl


AUX_KEY = "auxiliary"
CUSTOM = "std:maniphest:custom:"
IDX_KEY = CUSTOM + "index"
DUE_KEY = CUSTOM + "duedate"
DATA_FIELD = "data"
FIELDS = "fields"


class ObjectHelper(object):
    """object helper."""

    def user_has_role(obj, role):
        """check if a user has a role."""
        return role in obj[FIELDS]["roles"]

    def user_get_username(obj):
        """get a user name."""
        return obj[FIELDS]["username"]


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

    def _go(self, operator, params=None, manual_post=True, data_filter=None):
        """run an operation."""
        if self.prefix is None:
            raise Exception("no prefix configured")
        return self._execute(self.prefix + "." + operator,
                             manual_post=manual_post,
                             parameters=params,
                             filter_data=data_filter)

    def _encode_list(self, prefix, vals):
        """encode a list set."""
        idx = 0
        for elem in vals:
            yield self._build(prefix + "[" + str(idx) + "]", elem)
            idx = idx + 1

    def _encode_dict(self, prefix, vals, nested):
        """encode a dictionary."""
        for item in vals:
            key = item
            if nested:
                key = prefix + "[" + item + "]"
            for e in self._encode(key, vals[item], True):
                yield e

    def _encode(self, prefix, vals, child):
        """Encode data parameters."""
        if isinstance(vals, str):
            yield self._build(prefix, vals)
        else:
            if isinstance(vals, dict):
                for d in self._encode_dict(prefix, vals, child):
                    yield d
            else:
                for l in self._encode_list(prefix, vals):
                    yield l

    def _execute(self,
                 endpoint,
                 manual_post=True,
                 parameters=None,
                 filter_data=None):
        """Execute a conduit query."""
        if self.token is None:
            raise Exception("no token given...")
        if self.host is None:
            raise Exception("no host given...")
        curl = pycurl.Curl()
        curl.setopt(curl.URL, self.host + "/api/" + endpoint)
        # post-data
        if manual_post:
            fields = []
            fields.append(self._build("api.token", self.token))
            if parameters is not None and len(parameters) > 0:
                for f in self._encode("", parameters, False):
                    fields.append(f)
            posting = "&".join(fields)
        else:
            params = parameters
            if params is None:
                params = {}
            params["api.token"] = self.token
            posting = urlencode(params)
        buf = BytesIO()
        curl.setopt(curl.POSTFIELDS, posting)
        curl.setopt(curl.WRITEDATA, buf)
        curl.perform()
        # and data back
        res = json.loads(buf.getvalue().decode("iso-8859-1"))
        errored = res["error_code"]
        if errored is None:
            data = res["result"]
            if filter_data is not None:
                data = self._filter_data(data, filter_data)
            return data
        else:
            raise Exception(res["error_info"])

    def _filter_data(self, inputs, filtered):
        """filter data."""
        data = inputs[DATA_FIELD]
        new_data = []
        for item in data:
            if filtered(item):
                new_data.append(item)
        inputs[DATA_FIELD] = new_data
        return inputs


class Diffusion(ConduitBase):
    """Diffusion queries."""

    def __init__(self):
        """init the instance."""
        self.prefix = "diffusion"

    def filecontent_by_path_branch(self, path, callsign, branch):
        """file content query/lookup."""
        return self._go("filecontentquery", {"path": path,
                                             "repository": "r" + callsign,
                                             "branch": branch})


class File(ConduitBase):
    """File queries."""

    def __init__(self):
        """Init the instance."""
        self.prefix = "file"

    def download(self, phid):
        """Download a file."""
        return self._go("download", {"phid": phid})


class Dashboard(ConduitBase):
    """Dashboard queries."""

    def __init__(self):
        """init the instance."""
        self.prefix = "dashboard"

    def edit_text(self, identifier, text):
        """edit dashboard text."""
        vals = {}
        vals["transactions[0][type]"] = "custom.text"
        vals["transactions[0][value]"] = quote(text)
        vals["objectIdentifier"] = identifier
        return self._go("panel.edit", vals, manual_post=True)


class Project(ConduitBase):
    """Project queries."""

    def __init__(self):
        """init the instance."""
        self.prefix = "project"

    def open(self):
        """Open projects."""
        return self._search("active")

    def by_name(self, name):
        """get projects by name."""
        vals = {}
        vals["constraints[name]"] = name

        def _filter_name(item):
            return item[FIELDS]["name"] == name
        return self._search("all", vals, _filter_name)

    def _search(self, key, params=None, filtered=None):
        """Query projects."""
        vals = params
        if params is None:
            vals = {}
        vals["queryKey"] = key
        return self._go("search",
                        vals,
                        manual_post=True,
                        data_filter=filtered)


class User(ConduitBase):
    """User implementation."""

    def __init__(self):
        """init the instance."""
        self.prefix = "user"

    def by_phids(self, phids):
        """user by phid."""
        vals = {}
        vals["constraints[phids]"] = phids
        return self._search(vals)

    def whoami(self):
        """get user information."""
        return self._go("whoami")

    def _search(self, params=None):
        """Query users."""
        vals = params
        if vals is None:
            vals = {}
        vals["queryKey"] = "all"
        return self._go("search", vals)

    def query(self):
        """Query users."""
        return self._search()


class Conpherence(ConduitBase):
    """Conpherence implementation."""

    def __init__(self):
        """init the instance."""
        self.prefix = "conpherence"

    def updatethread(self, room, message):
        """Update a conpherence thread."""
        return self._go("updatethread", {"id": room, "message": message})

    def querythread_by_id(self, room_id):
        """query a thread by id."""
        return self._querythread({"ids": [room_id]})

    def querytransaction_by_phid_last(self, room_phid, last):
        """get a transaction by room and last count."""
        return self._go("querytransaction", {"roomPHID": room_phid,
                                             "limit": last})

    def querythread(self):
        """Query thread."""
        return self._querythread(None)

    def _querythread(self, params=None):
        return self._go("querythread", params)


class Phriction(ConduitBase):
    """Phriction implementation."""

    def __init__(self):
        """init the instance."""
        self.prefix = "phriction"

    def info(self, slug):
        """get information for a page/slug."""
        return self._go("info", {"slug": slug})

    def edit(self, slug, title, content):
        """edit a phriction page."""
        return self._go("edit",
                        params={"slug": slug,
                                "title": title,
                                "content": content},
                        manual_post=False)


class Maniphest(ConduitBase):
    """Maniphest implementation."""

    def __init__(self):
        """init the instance."""
        self.prefix = "maniphest"

    def create(self, title, text, owner_phid, project_phid):
        """create a task."""
        params = {}
        params["title"] = title
        params["description"] = text
        params["ownerPHID"] = owner_phid
        params["projectPHIDs"] = [project_phid]
        return self._go("createtask", params)

    def comment_by_id(self, task_id, message):
        """comment on a task by using the id."""
        params = self._comment_params(task_id, message)
        return self._update(params)

    def get_by_ids(self, task_ids):
        """get a task by id."""
        return self._query({"ids": task_ids})

    def get_by_owner(self, owner):
        """get tasks by owner."""
        return self._get_by_user_field("ownerPHIDs", owner)

    def get_by_cc(self, cc):
        """get by subscriber."""
        return self._get_by_user_field("ccPHIDs", cc)

    def get_by_author(self, author):
        """author query."""
        return self._get_by_user_field("authorPHIDs", author)

    def _get_by_user_field(self, field, phids):
        """get by a user field."""
        params = {}
        params[field] = [phids]
        return self._query(params)

    def open(self):
        """Open tasks."""
        return self._query(self._open_params())

    def invalid_by_id(self, task_id):
        """close as invalid by id."""
        return self._close_by_id(task_id, "invalid")

    def resolve_by_id(self, task_id):
        """resolve as closed by id."""
        return self._close_by_id(task_id, "resolved")

    def _close_by_id(self, task_id, status):
        """close a task by id."""
        params = self._comment_params(task_id, "marking closed")
        params["status"] = status
        return self._update(params)

    def open_and_subscribed(self, user_phid):
        """Open by project phid."""
        params = self._open_params()
        params["ccPHIDs"] = [user_phid]
        return self._query(params)

    def open_by_project_phid(self, project_phid):
        """Open by project phid."""
        params = self._open_params()
        params["projectPHIDs"] = [project_phid]
        return self._query(params)

    def _comment_params(self, task_id, message):
        """Comment parameters."""
        return {"id": task_id, "comments": message}

    def _open_params(self):
        """Open status parameter building."""
        return {"status": "status-open"}

    def _update(self, params=None):
        """task updates."""
        return self._go("update", params)

    def _query(self, params=None):
        """Query operations."""
        return self._go("query", params)

    def update_projects(self, task_id, project_phids, comment):
        """add a project to a task."""
        params = self._comment_params(task_id, comment)
        params["projectPHIDs"] = project_phids
        return self._update(params)

    def move_column(self, task, column):
        """move tasks to a column."""
        vals = {}
        vals["transactions[0][type]"] = "column"
        vals["transactions[0][value]"] = column
        vals["objectIdentifier"] = task
        return self._go("edit", vals, manual_post=True)
