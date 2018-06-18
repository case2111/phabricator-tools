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
import std.algorithm: canFind, sort;
import std.conv: to;
import std.datetime.systime;
import std.json;
import std.path: baseName, buildPath, stripExtension;
import std.stdio: File, writeln;
import std.string: format, join, split, startsWith, strip;

// This is irritagin to get dynamic sorting via mixins
const string SortTemplateStart = "foreach (obj; res[2..res.length].sort!(\"";
const string SortTemplateEnd = "\"))
{
    objects ~= obj;
}
";

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
private static void updateWhoIs(WikiCtx ctx)
{
    wikiFromSource(ctx, "whois", &fullWhoIs);
}

/**
 * Update contacts
 */
private static void upContacts(WikiCtx ctx)
{
    wikiFromSource(ctx, "contacts", &doContacts);
}

/**
 * Full whois processing
 */
private static bool fullWhoIs(WikiCtx ctx)
{
    auto result = wikiFromSource(ctx, WhoIsOpts, Conv.nameAlias);
    if (result)
    {
        try
        {
            auto opts = ctx.api.context[WhoIsOpts].split(",");
            auto raw = getDiffusion(ctx.settings, opts[0], opts[1], "master");
            auto lines = raw.split("\n");
            string[string] lookups;
            foreach (user; ctx.users[ResultKey][DataKey].array)
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
            construct!PasteAPI(ctx.settings).editText(ctx.api.context[LookupsPHID], json);
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
private static bool doContacts(WikiCtx ctx)
{
    return wikiFromSource(ctx, ContactsOpts, Conv.catsub);
}

/**
 * Wiki generation from a source input
 */
private static void wikiFromSource(WikiCtx ctx,
                                   string key,
                                   bool function(WikiCtx) callback)
{
    if (!callback(ctx))
    {
        writeln(key ~ " wiki update failed");
    }
}

/**
 * Generate a page from a source repo location
 */
private static bool wikiFromSource(WikiCtx ctx, string key, Conv mode)
{
    try
    {
        auto opts = ctx.api.context[key].split(",");
        auto src = opts[0];
        auto text = wikiDiffusion(ctx.settings,
                                  src,
                                  opts[1],
                                  "master",
                                  mode);
        auto name = baseName(stripExtension(src));
        writeReport(ctx, name, text);
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
private static void writeReport(WikiCtx ctx, string name, string data)
{
    auto inbox = ctx.api.context[ReportInbox];
    auto filePath = buildPath(inbox, name ~ ".md");
    auto f = File(filePath, "w");
    f.write(data);
}

/**
 * Generate a page
 */
private static void genPage(WikiCtx ctx,
                            string contextKey,
                            string[] function(WikiCtx, Settings) callback,
                            bool reverse)
{
    auto parts = ctx.api.context[contextKey].split(",");
    auto name = parts[0];
    auto settings = ctx.settings;
    auto res = callback(ctx, settings);
    string[] objects;
    objects ~= res[0];
    objects ~= res[1];
    if (reverse)
    {
        mixin(SortTemplateStart ~ "b < a" ~ SortTemplateEnd);
    }
    else
    {
        mixin(SortTemplateStart ~ "a < b" ~ SortTemplateEnd);
    }

    auto page = join(objects, "\n");
    writeReport(ctx, name, page);
}

/**
 * Build the index list
 */
private static string[] doIndexList(WikiCtx ctx, Settings settings)
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
private static void doIndex(WikiCtx ctx)
{
    try
    {
        genPage(ctx, IndexOpts, &doIndexList, false);
    }
    catch (Exception e)
    {
        writeln("unable to generate index page");
        writeln(e);
    }
}

private class WikiCtx
{
    @property public API api;
    @property public Settings settings;
    @property public JSONValue users;
}

/**
 * Entry point
 */
void main(string[] args)
{
    auto api = setup(args);
    auto ctx = new WikiCtx();
    ctx.api = api;
    ctx.settings = getSettings(api);
    ctx.users = construct!UserAPI(ctx.settings).activeUsers();
    updateWhoIs(ctx);
    upContacts(ctx);
    doIndex(ctx);
    info("wiki");
}
