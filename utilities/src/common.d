/**
 * Copyright 2018
 * MIT License
 * Phabricator specific handling
 */
module common;
import phabricator.api;
import phabricator.common;
import std.getopt;
import std.stdio: writeln;
import std.string: format;

// Phabricator items
private enum PhabIndicator = "PHAB_";

// URL for phab
private enum PhabricatorURL = "HOST";

// phabricator api token
private enum PhabricatorToken = "TOKEN";

// dashboard (to update, wiki phid)
public enum DashOpts = "TO_DASH";

// Unmodified tasks (project, months, room)
public enum UnmodifiedOpts = "UNMODIFIED";

// index settings (name)
public enum IndexOpts = "INDEX";

// activity settings (name)
public enum ActivityOpts = "ACTIVITY";

// contact settings (path, callsign)
public enum ContactsOpts = "CONTACTS";

// whois settings (path, callsign)
public enum WhoIsOpts = "WHOIS";

// Synapse lookup resolution (Paste PHID)
public enum LookupsPHID = "LOOKUP_PHID";

// User PHID
public enum PhabricatorUser = "USER_PHID";

// hidden tasks (paste phid, room)
public enum HiddenOpts = "HIDDEN";

// Where we place reports for phab to be uploaded
public enum ReportInbox = "INBOX";

public class API
{
    @property public string[string] context;
}

/**
 * Get settings
 */
public static Settings getSettings(API api)
{
    auto settings = Settings();
    settings.url = api.context[PhabricatorURL];
    settings.token = api.context[PhabricatorToken];
    return settings;
}

/**
 * Report when completed
 */
public static void info(string name)
{
    writeln(format("[INFO] done -> %s", name));
}

/**
 * Perform setup
 */
API setup(string[] args)
{
    string env;
    auto opts = getopt(args,
                       std.getopt.config.required,
                       "env",
                       &env);

    auto api = new API();
    api.context = loadEnvironmentFile(env, PhabIndicator);
    return api;
}
