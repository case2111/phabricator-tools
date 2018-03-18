/**
 * Copyright 2018
 * MIT License
 * Phabricator specific handling
 */
module projects;
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
 * Join projects
 */
public static bool doJoinProjects(MatrixAPI api)
{
    try
    {
        auto settings = getSettings(api);
        auto user = api.context[PhabricatorUser];
        auto proj = construct!ProjectAPI(settings);
        auto membership = proj.membersActive()[ResultKey][DataKey];
        string[] results;
        foreach (project; membership.array)
        {
            auto members = project["attachments"]["members"]["members"].array;
            auto matched = false;
            foreach (member; members)
            {
                auto phid = member["phid"].str;
                if (phid == user)
                {
                    matched = true;
                    break;
                }
            }

            if (!matched)
            {
                results ~= project[FieldsKey]["name"].str;
            }
        }

        if (results.length > 0)
        {
            api.sendText(api.context[DebugRoom],
                         "not a member of these projects:\n" ~
                         join(results, "\n"));
            return assignToActive(getSettings(api), user);
        }
        else
        {
            return true;
        }
    }
    catch (Exception e)
    {
        return false;
    }
}
