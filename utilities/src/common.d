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

// NOTE: relic of coming from matrix-bot
private enum SynapseLine = "SYNAPSE_";

// Phabricator items
private enum PhabIndicator = "PHAB_";

// URL for phab
private enum PhabricatorURL = PhabIndicator ~ "URL";

// phabricator api token
private enum PhabricatorToken = PhabIndicator ~ "TOKEN";

// dashboard (to update, wiki phid)
public enum DashOpts = PhabIndicator ~ "TO_DASH";

// Unmodified tasks (project, months, room)
public enum UnmodifiedOpts = PhabIndicator ~ "UNMODIFIED";

// index settings (slug, title)
public enum IndexOpts = PhabIndicator ~ "INDEX";

// contact settings (slug, title, path, callsign)
public enum ContactsOpts = PhabIndicator ~ "CONTACTS";

// whois settings (slug, title, path, callsign)
public enum WhoIsOpts = PhabIndicator ~ "WHOIS";

// Synapse lookup resolution (Paste PHID)
public enum LookupsPHID = "LOOKUP_PHID";

// User PHID
public enum PhabricatorUser = PhabIndicator ~ "USER_PHID";

// hidden tasks (paste phid, room)
public enum HiddenOpts = PhabIndicator ~ "HIDDEN";

// Where we place reports for phab to be uploaded
public enum ReportInbox = PhabIndicator ~ "INBOX";

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
 * Write messages on error
 */
public static void onError(string message)
{
    writeln(message);
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
    api.context = loadEnvironmentFile(env, SynapseLine);
    return api;
}
