/**
 * Copyright 2018
 * MIT License
 * Phabricator specific handling
 */
module tasks;
import common;
import phabricator.api;
import phabricator.common;
import std.algorithm: sort;
import std.conv: to;
import std.datetime;
import std.json;
import std.string: format, join, split, strip;
import std.stdio: writeln;

/**
 * Hidden task checking
 */
private static int hiddenTasks(TaskCtx ctx, int start, int page)
{
    auto show = "none found";
    int last = -1;
    if (page < 1 || start < 1)
    {
        show = "please select a bounded start (> 0) and page (> 0)";
    }
    else
    {
        auto results = restricted(ctx.settings, start, page);
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

    return last;
}

/**
 * Scheduled hidden task checking
 */
private static bool doHiddenTasks(TaskCtx ctx)
{
    try
    {
        auto lastStart = 1;
        auto opts = ctx.api.context[HiddenOpts].split(",");
        auto phid = opts[0];
        auto room = opts[1];
        auto paste = construct!PasteAPI(ctx.settings);
        auto contents = paste.activeByPHID(phid, true)[ResultKey][DataKey];
        auto attached = contents.array[0]["attachments"]["content"]["content"];
        auto text = attached.str.split("=");
        lastStart = to!int(text[1].strip());
        auto result = hiddenTasks(ctx, lastStart, 500);
        if (result != lastStart && result >= 0)
        {
            auto today = Clock.currTime().dayOfYear();
            paste.editText(phid, format("%s=%s", today, result));
        }
        else
        {
            writeln(format("task visibility index unchanged: T%s", result));
        }

        return true;
    }
    catch (Exception e)
    {
        writeln(e);
        return false;
    }
}

/**
 * Unmodified operations
 */
private static bool tasksUnmodified(TaskCtx ctx)
{
    auto opts = ctx.api.context[UnmodifiedOpts].split(",");
    auto result = unmodified(ctx.settings, opts[0], to!int(opts[1]));
    return result;
}

private class TaskCtx
{
    @property public API api;
    @property public Settings settings;
}

/**
 * Entry point
 */
void main(string[] args)
{
    auto api = setup(args);
    auto ctx = new TaskCtx();
    ctx.api = api;
    ctx.settings = getSettings(api);
    if (!tasksUnmodified(ctx))
    {
        writeln("unmod tasks");
    }
    if (!doHiddenTasks(ctx))
    {
        writeln("hidden tasks");
    }
    info("tasks");
}

// Id field for tasks
private enum IdField = "id";

/**
 * Get a task id e.g. T[0-9]+
 */
private static string getId(JSONValue task)
{
    return "T" ~ to!string(task[IdField].integer);
}

/**
 * Move all tasks from a query to a project
 */
private static int queryToProject(Settings settings,
                                   string query,
                                   string projectPHID)
{
    int count = 0;
    try
    {
        auto maniphest = construct!ManiphestAPI(settings);
        auto queried = maniphest.byQueryKey(query)[ResultKey][DataKey];
        foreach (task; queried.array)
        {
            maniphest.addProject(task[PHID].str, projectPHID);
            count++;
        }
    }
    catch (Exception e)
    {
        count = count * -1;
    }

    return count;
}

/**
 * Unmodified task handling
 */
private static bool unmodified(Settings settings,
                                  string projectPHID,
                                  int months)
{
    try
    {
        auto maniphest = construct!ManiphestAPI(settings);
        auto all = maniphest.openProject(projectPHID)[ResultKey][DataKey];
        foreach (task; all.array)
        {
            maniphest.invalid(task[PHID].str);
        }

        string[] projs;
        auto active = construct!ProjectAPI(settings).active();
        auto now = Clock.currTime();
        foreach (proj; active[ResultKey][DataKey].array)
        {
            auto open = maniphest.openProject(proj[PHID].str);
            foreach (task; open[ResultKey][DataKey].array)
            {
                if (FieldsKey in task)
                {
                    auto fields = task[FieldsKey];
                    auto modified = fields["dateModified"].integer;
                    auto actual = SysTime.fromUnixTime(modified);
                    actual.add!"months"(months);
                    if (actual < now)
                    {
                        auto taskStr = task[PHID].str;
                        maniphest.addProject(taskStr, projectPHID);
                        maniphest.comment(taskStr,
                                          "task updated due to inactivity");
                    }
                }
            }
        }

        return true;
    }
    catch (Exception e)
    {
        writeln(e);
        return false;
    }
}

/**
 * Detects restricted tasks
 */
private static string[] restricted(Settings settings, int start, int page)
{
    try
    {
        if (page < 0)
        {
            return [];
        }

        int paging = 0;
        int[] ids;
        bool[long] matched;
        while (paging <= page)
        {
            ids ~= start + paging;
            matched[start + paging] = false;
            paging++;
        }

        auto maniphest = construct!ManiphestAPI(settings);
        auto raw = maniphest.byIds(ids);
        auto all = raw[ResultKey][DataKey];
        foreach (task; all.array)
        {
            if (FieldsKey in task)
            {
                auto id = task[IdField].integer;
                if (id in matched)
                {
                    matched[id] = true;
                }
                else
                {
                    matched[id] = false;
                }
            }
        }

        string[] results;
        foreach (match; matched.keys.sort!())
        {
            if (!matched[match])
            {
                results ~= to!string(match);
            }
        }

        return results;
    }
    catch (Exception e)
    {
        return [];
    }
}
