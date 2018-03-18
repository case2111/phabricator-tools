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
 * Find hidden tasks
 */
public static void hiddenTasks(API api, string roomId, JSONValue context)
{
    auto parsed = parseBody(context, HiddenTasks);
    if (!parsed[0])
    {
        return;
    }

    int start;
    int page;
    auto opts = getopt(parsed[2],
                       "start",
                       "starting task number",
                       &start,
                       "page",
                       "paging range",
                       &page);
    if (checkOpts(api, roomId, parsed[1], opts))
    {
        hiddenTasks(api, roomId, start, page, true);
    }
}

/**
 * Hidden task checking
 */
private static int hiddenTasks(API api,
                               string roomId,
                               int start,
                               int page,
                               bool report)
{
    auto show = "none found";
    int last = -1;
    if (page < 1 || start < 1)
    {
        show = "please select a bounded start (> 0) and page (> 0)";
    }
    else
    {
        auto settings = getSettings(api);
        auto results = restricted(settings, start, page);
        if (results.length > 0)
        {
            show = "T" ~ join(results, ", T");
            foreach (result; results)
            {
                auto id = to!int(result);
                if (last == -1 || id < last)
                {
                    last = id;
                }
            }
        }
    }

    if (report)
    {
        api.sendText(roomId, show);
    }

    return last;
}

/**
 * Scheduled hidden task checking
 */
public static bool doHiddenTasks(API api)
{
    try
    {
        auto lastStart = 1;
        auto opts = api.context[HiddenOpts].split(",");
        auto phid = opts[0];
        auto room = opts[1];
        auto settings = getSettings(api);
        auto paste = construct!PasteAPI(settings);
        auto contents = paste.activeByPHID(phid, true)[ResultKey][DataKey];
        auto attached = contents.array[0]["attachments"]["content"]["content"];
        auto text = attached.str.split("=");
        lastStart = to!int(text[1].strip());

        auto result = hiddenTasks(api, room, lastStart, 500, false);
        if (result != lastStart && result >= 0)
        {
            auto today = Clock.currTime().dayOfYear();
            paste.editText(phid, format("%s=%s", today, result));
        }
        else
        {
            api.sendText(room,
                         format("task visibility index unchanged: T%s",
                                result));
        }

        return true;
    }
    catch (Exception e)
    {
        return false;
    }
}

/**
 * Unmodified operations
 */
public static bool tasksUnmodified(API api)
{
    auto settings = getSettings(api);
    auto opts = api.context[UnmodifiedOpts].split(",");
    auto result = unmodified(settings, opts[0], to!int(opts[1]));
    return result;
}

/**
 * Entry point
 */
void main(string[] args)
{
    auto api = setup(args);
    if (!tasksUnmodified(api))
    {
        onError("unmod tasks");
    }
    if (!doHiddenTasks(api))
    {
        onError("hidden tasks");
    }
}
