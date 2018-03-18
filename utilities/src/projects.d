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
import common;

/**
 * Join projects
 */
private static void doJoinProjects(API api)
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
            auto assigned = assignToActive(getSettings(api), user);
            onError("not a member of these projects:\n" ~ join(results, "\n"));
            if (!assigned)
            {
                onError("unable to assign self to projects...");
            }
        }
    }
    catch (Exception e)
    {
        onError("unexepected exception joining projects");
    }
}

void main(string[] args)
{
}
