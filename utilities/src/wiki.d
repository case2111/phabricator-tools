/**
 * Copyright 2018
 * MIT License
 * Phabricator specific handling
 */
module wiki;
import common;
import phabricator.api;
import phabricator.common;
import helpers.conv2wiki;
import helpers.diffusion;
import helpers.indexing;
import helpers.wiki2dash;
import std.algorithm: canFind, sort;
import std.conv: to;
import std.json;
import std.path: baseName, buildPath, stripExtension;
import std.stdio: File, writeln;
import std.string: format, join, split, startsWith, strip;

/**
 * Generate primitive markdown columns/tables
 */
private static string generateColumns(string[] args)
{
    return format("| %s |", join(args, " | "));
}

/**
 * Update whois
 */
private static void updateWhoIs(API api)
{
    wikiFromSource(api, "whois", &fullWhoIs);
}

/**
 * Update contacts
 */
private static void upContacts(API api)
{
    wikiFromSource(api, "contacts", &doContacts);
}

/**
 * Full whois processing
 */
private static bool fullWhoIs(API api)
{
    auto result = wikiFromSource(api, WhoIsOpts, Conv.nameAlias);
    if (result)
    {
        try
        {
            auto settings = getSettings(api);
            auto opts = api.context[WhoIsOpts].split(",");
            auto raw = getDiffusion(settings, opts[2], opts[3], "master");
            auto lines = raw.split("\n");
            auto users = construct!UserAPI(settings).activeUsers();
            string[string] lookups;
            foreach (user; users[ResultKey][DataKey].array)
            {
                auto rawName = user[FieldsKey]["username"].str;
                auto userName = "@" ~ rawName;
                foreach (line; lines)
                {
                    if (line.startsWith(userName ~ ","))
                    {
                        auto parts = line.split(",");
                        foreach (part; parts[1..parts.length])
                        {
                            if (part != rawName && part.length > 0)
                            {
                                if (rawName !in lookups)
                                {
                                    lookups[rawName] = "";
                                }
                                else
                                {
                                    lookups[rawName] ~= ",";
                                }

                                lookups[rawName] ~= part;
                            }
                        }

                        break;
                    }
                }
            }

            auto obj = JSONValue(lookups);
            auto json = toJSON(obj);
            construct!PasteAPI(settings).editText(api.context[LookupsPHID], json);
        }
        catch (Exception e)
        {
            writeln(e);
            result = false;
        }
    }

    return result;
}

/**
 * Process contacts
 */
private static bool doContacts(API api)
{
    return wikiFromSource(api, ContactsOpts, Conv.catsub);
}

/**
 * Wiki generation from a source input
 */
private static void wikiFromSource(API api,
                                   string key,
                                   bool function(API) callback)
{
    if (!callback(api))
    {
        writeln(key ~ " wiki update");
    }
}

/**
 * Generate a page from a source repo location
 */
private static bool wikiFromSource(API api, string key, Conv mode)
{
    try
    {
        auto settings = getSettings(api);
        auto opts = api.context[key].split(",");
        auto src = opts[0];
        auto text = wikiDiffusion(settings,
                                  src,
                                  opts[1],
                                  "master",
                                  mode);
        auto name = baseName(stripExtension(src));
        writeReport(api, name, text);
        return true;
    }
    catch (Exception e)
    {
        writeln(e);
        return false;
    }
}

/**
 * Write a report to disk for later upload
 */
private static void writeReport(API api, string name, string page)
{
    auto inbox = api.context[ReportInbox];
    auto filePath = buildPath(inbox, name ~ ".md");
    auto f = File(filePath, "w");
    f.write(page);
}

/**
 * Generate a page
 */
private static void genPage(API api,
                            string contextKey,
                            string[] function(API, Settings) callback)
{
    auto parts = api.context[contextKey].split(",");
    auto name = parts[0];
    auto settings = getSettings(api);
    auto res = callback(api, settings);
    string[] objects;
    objects ~= res[0];
    objects ~= res[1];
    foreach (obj; res[2..res.length].sort!("a < b"))
    {
        objects ~= obj;
    }

    auto page = join(objects, "\n");
    writeReport(api, name, page);
}

/**
 * Build the index list
 */
private static string[] doIndexList(API api, Settings settings)
{
    string[] indexItems;
    indexItems ~= generateColumns(["index", "count"]);
    indexItems ~= generateColumns(["---", "---"]);
    auto vals = getIndexItems(settings);
    string[] tracked;
    string[] traced;
    foreach (item; vals.keys.sort!("a < b"))
    {
        auto tasks = vals[item].tasks;
        auto count = tasks.length;
        indexItems ~= generateColumns([item, to!string(count)]);
        foreach (phid; tasks)
        {
            traced ~= format("%s -> %s", item, phid);
        }

        auto clean = item.strip();
        if (tracked.canFind(clean))
        {
            writeln("duplicate index found");
        }

        tracked ~= clean;
    }

    return indexItems;
}

/**
 * Do index processing
 */
private static void doIndex(API api)
{
    try
    {
        genPage(api, IndexOpts, &doIndexList);
    }
    catch (Exception e)
    {
        writeln("unable to generate index page");
        writeln(e);
    }
}

/**
 * Convert wiki to dashboard
 */
private static void wikiToDash(API api)
{
    auto settings = getSettings(api);
    auto dashOpts = api.context[DashOpts].split(",");
    auto result =  convertToDashboard(settings,
                                      dashOpts[1],
                                      dashOpts[0]);
    if (!result)
    {
        writeln("unable to update dashboard");
    }
}

/**
 * Entry point
 */
void main(string[] args)
{
    auto api = setup(args);
    updateWhoIs(api);
    upContacts(api);
    doIndex(api);
    wikiToDash(api);
    info("wiki");
}

