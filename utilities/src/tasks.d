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
    info("tasks");
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
