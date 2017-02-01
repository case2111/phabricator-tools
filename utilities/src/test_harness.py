import conduit
import json
tests = {}
IGNORED = ['host', 'token', 'prefix']


def _get_env(key):
    """get environment variable."""
    val = None
    with open("/etc/environment", 'r') as f:
        key_entry = "PHAB_" + key + "="
        for line in f:
            if line.startswith(key_entry):
                val = line[len(key_entry) + 1: -2]
    return val

# testing vals from env
USER_PHIDS = _get_env("CHECK_IDX").split(" ")
TEST_PROJS = _get_env("TEST_PRJ_NAME")

# testing keys
KEY_DELIM = "."
USER_KEY = "User"
PROJ_KEY = "Project"

# test definitions
tests[USER_KEY + KEY_DELIM + "by_phids"] = USER_PHIDS
tests[USER_KEY + KEY_DELIM + "whoami"] = None
tests[USER_KEY + KEY_DELIM + "query"] = None
tests[PROJ_KEY + KEY_DELIM + "open"] = None
tests[PROJ_KEY + KEY_DELIM + "by_name"] = TEST_PROJS


def main():
    """main entry for harness."""
    host = _get_env("HOST")
    tok = _get_env("MON_TOKEN")
    fails = False
    for item in conduit.ConduitBase.__subclasses__():
        if item.__name__ not in [PROJ_KEY, USER_KEY]:
            continue
        inst = item()
        inst.host = host
        inst.token = tok
        for obj in dir(item):
            if not obj.startswith("_") and obj not in IGNORED:
                method = getattr(inst, obj)
                if method is not None:
                    key = item.__name__ + KEY_DELIM + obj
                    print("===")
                    print(key)
                    if key not in tests:
                        print("unknown test for: " + key)
                        fails = True
                    else:
                        env_val = tests[key]
                        if env_val is None:
                            env = []
                        else:
                            env = [env_val]
                        res = method(*env)
                        dumped = json.dumps(res,
                                            indent=4,
                                            sort_keys=True,
                                            separators=[',', ': '])
                        print(dumped)
                    print("===\n")
    if fails:
        raise Exception("test failure")


if __name__ == "__main__":
    try:
        main()
        exit(0)
    except Exception as e:
        print('error encountered')
        print(str(e))
        exit(1)
