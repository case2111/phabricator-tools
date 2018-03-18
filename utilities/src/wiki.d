/**
 * Copyright 2018
 * MIT License
 * Phabricator specific handling
 */
module matrixd.phabricator;
import matrix.api;
import matrixd.common;
import phabricator.api;
import phabricator.common;
import phabricator.util.conv2wiki;
import phabricator.util.diffusion;
import phabricator.util.indexing;
import phabricator.util.projects;
import phabricator.util.tasks;
import phabricator.util.wiki2dash;
import std.algorithm: canFind, sort;
import std.ascii: isDigit, isPunctuation, isWhite;
import std.conv: to;
import std.datetime;
import std.getopt;
import std.json;
import std.random;
import std.string: endsWith, format, join, split, startsWith, strip, toLower;
import std.typecons;

/**
 * Update whois
 */
public static void updateWhoIs(MatrixAPI api, string roomId, JSONValue context)
{
    wikiFromSource(api, roomId, context, WhoIsValues, &doWhoIs);
}

/**
 * Update contacts
 */
public static void upContacts(MatrixAPI api, string roomId, JSONValue context)
{
    wikiFromSource(api, roomId, context, ContactValues, &doContacts);
}

/**
 * Update index stats
 */
public static void upIndex(MatrixAPI api, string roomId, JSONValue context)
{
    if (isSingleCommand(context, IndexValues))
    {
        doIndex(api);
        api.sendText(roomId, "index page updated");
    }
}

/**
 * Full whois processing
 */
private static bool fullWhoIs(MatrixAPI api)
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

            if (scheduled)
            {
                auto obj = JSONValue(lookups);
                auto json = toJSON(obj);
                construct!PasteAPI(settings).editText(api.context[LookupsPHID],
                                                      json);
                requestUrl(api, "shutdown");
            }
        }
        catch (Exception e)
        {
            result = false;
        }
    }

    return result;
}

/**
 * Process contacts
 */
public static bool doContacts(MatrixAPI api)
{
    return wikiFromSource(api, ContactsOpts, Conv.catsub);
}

/**
 * Generate a page from a source repo location
 */
private static bool wikiFromSource(MatrixAPI api, string key, Conv mode)
{
    auto settings = getSettings(api);
    auto opts = api.context[key].split(",");
    return wikiDiffusion(settings,
                         GenPageHeader,
                         opts[0],
                         opts[1],
                         opts[2],
                         opts[3],
                         "master",
                         mode);
}

/**
 * Generate a page
 */
private static void genPage(MatrixAPI api,
                            string contextKey,
                            string[] function(MatrixAPI, Settings) callback)
{
    auto parts = api.context[contextKey].split(",");
    auto slug = parts[0];
    auto title = parts[1];
    auto settings = getSettings(api);
    auto res = callback(api, settings);
    string[] objects;
    objects ~= res[0];
    objects ~= res[1];
    foreach (obj; res[2..res.length].sort!("a < b"))
    {
        objects ~= obj;
    }

    auto page = GenPageHeader ~ "---\n\n" ~ join(objects, "\n");
    auto phriction = construct!PhrictionAPI(settings);
    phriction.edit(slug, title, page);
}

/**
 * Build the index list
 */
private static string[] doIndexList(MatrixAPI api, Settings settings)
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
            writeDump("duplicate index found", traced);
        }

        tracked ~= clean;
    }

    return indexItems;
}

/**
 * Do index processing
 */
public static bool doIndex(MatrixAPI api)
{
    try
    {
        genPage(api, IndexOpts, &doIndexList);
        return true;
    }
    catch (Exception e)
    {
        return false;
    }
}


/**
 * Convert a wiki/phriction page to dashboard
 */
public static void wikiToDash(MatrixAPI api, string roomId, JSONValue context)
{
    if (!isSingleCommand(context, WikiToDash))
    {
        return;
    }

    auto displayText = "";
    if (wikiToDash(api))
    {
        displayText = "updated";
    }
    else
    {
        displayText = "failed";
    }

    api.sendText(roomId, displayText);
}

/**
 * Convert wiki to dashboard
 */
public static bool wikiToDash(MatrixAPI api)
{
    auto settings = getSettings(api);
    auto dashOpts = api.context[DashOpts].split(",");
    return convertToDashboard(settings,
                              dashOpts[1],
                              dashOpts[0]);
}
