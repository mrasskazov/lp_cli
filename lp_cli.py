#!/usr/bin/env python
#-*- coding: utf-8 -*-

# Copyright (c) 2014 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import re

from launchpadlib.launchpad import Launchpad
from launchpadlib.launchpad import uris


class launchpad_client(object):

    def __init__(self, project):

        lp_cache_dir = os.path.expanduser(
            os.environ.get('LAUNCHPAD_CACHE_DIR',
                           '~/.launchpadlib/cache'))

        lp_creds_filename = os.path.expanduser(
            os.environ.get('LAUNCHPAD_CREDS_FILENAME',
                           '~/.launchpadlib/creds'))

        self.Launchpad = Launchpad.login_with(
            project.lower(),
            uris.LPNET_SERVICE_ROOT,
            lp_cache_dir,
            credentials_file=lp_creds_filename)

        self.Project = None
        self.Bug = None
        self.Tasks = []

        self.project(project.lower())

    @property
    def launchpad(self):
        return self.Launchpad

    def project(self, project=None):
        if project is not None:
            self.Project = self.launchpad.projects[project]
        return self.Project

    def bug(self, bug_id=None):
        if bug_id is not None:
            if self.Bug is None or self.Bug.id != bug_id:
                self.Bug = self.launchpad.bugs[bug_id]
        return self.Bug

    def tasks(self, bug_id=None):
        if bug_id is not None:
            self.Tasks = self.bug(bug_id).bug_tasks
        return self.Tasks

    def create_bug(self, title, description, **properties):
        bug = self.launchpad.bugs.createBug(target=self.project().self_link,
                                            title=title,
                                            description=description)
        self.update_bug(bug.id, **properties)
        return bug

    def update_bug(self, bug_id=None, **properties):
        bug = self.bug(bug_id)
        updated = False
        for p in ['title', 'description', 'private', 'tags']:
            if p in properties:
                setattr(bug, p, properties[p])
                updated = True
        if 'affects_project' in properties:
            self.bug().addTask(
                target=self.launchpad.projects[properties['affects_project']])
        if updated:
            bug.lp_save()

        for task in self.tasks(bug_id):
            self.update_task(task, **properties)

        return bug

    def update_task(self, task, **properties):
        updated = False
        if task.target.name in properties['affects_only']:
            if 'assignee' in properties:
                properties['assignee'] = \
                    self.launchpad.people(properties['assignee'])
            if 'milestone' in properties:
                properties['milestone'] = \
                    self.project().getMilestone(name=properties['milestone'])
            for p in ['status', 'importance', 'milestone', 'assignee']:
                if p in properties:
                    setattr(task, p, properties[p])
                    updated = True
            if updated:
                task.lp_save()

    def add_comment(self, comment, bug_id=None, **properties):
        for p in [task.target.name for task in self.tasks(bug_id)]:
            if p in properties['affects_only']:
                return self.bug(bug_id).newMessage(content=comment)


def get_argparser():
    statuses_report = ['New',
                       'Confirmed',
                       'Triaged',
                       'In Progress',
                       'Fix Committed',
                       'Fix Released']
    statuses_update = ['Imcomplete',
                       'Opinion',
                       'Invalid',
                       'Won\'t fix']
    statuses_update += statuses_report

    importance = ['Undecided',
                  'Critical',
                  'High',
                  'Medium',
                  'Low',
                  'Wishlist']

    parser = argparse.ArgumentParser(prog='lp_cli.py',
                                     description='Command line client '
                                     'for Launchpad')
    parser.add_argument('project',
                        help='Launchpad project\'s name for auth. Bug will be '
                        'updated only if affected with it if --affects-only '
                        'is not specified')
    parser.add_argument('-o', '--affects-only',
                        required=False,
                        default=None,
                        help='Comma separated Launchpad project\'s names. '
                        'If specified, bug will be updated '
                        'only if it affected with specified projects.')

    subparsers = parser.add_subparsers(title='Commands')

    parser_comment = subparsers.add_parser('comment')
    parser_comment.set_defaults(func=command_comment)
    parser_comment.add_argument('bug_id', help='Bug id on Launchpad.')
    parser_comment.add_argument('comment', help='Comment body.', nargs='+')

    parser_report = subparsers.add_parser('report')
    parser_report.set_defaults(func=command_report)
    parser_report.add_argument('title',
                               help='Bug title.')
    parser_report.add_argument('-p', '--private',
                               action='store_true',
                               help='Bug is private.')
    parser_report.add_argument('-d', '--description',
                               required=True,
                               help='Bug description.')

    parser_report.add_argument('-s', '--status',
                               choices=statuses_report,
                               default='New',
                               help='Bug status.')
    parser_report.add_argument('-i', '--importance',
                               choices=importance,
                               default='Undecided',
                               help='Bug importance.')
    parser_report.add_argument('-m', '--milestone',
                               default=None,
                               help='Milestone')
    parser_report.add_argument('-t', '--tags',
                               nargs='+',
                               default=[],
                               help='Add specified tags.')
    parser_report.add_argument('-a', '--assignee',
                               default=None,
                               help='Assign bug to specified user/group.')
    #TODO: add attach subcommand w/ parameters:
    #TODO: "Description for it" --patch(True/False) filename

    parser_update = subparsers.add_parser('update')
    parser_update.set_defaults(func=command_update)
    parser_update.add_argument('bug_id', help='Bug id on Launchpad.')
    parser_update.add_argument('-p', '--private',
                               dest='private',
                               action='store_true',
                               help='Bug is private.')
    parser_update.add_argument('-u', '--public',
                               dest='private',
                               action='store_false',
                               help='Bug is public.')
    parser_update.set_defaults(private=None)
    parser_update.add_argument('-l', '--title',
                               default=None,
                               help='Bug title.')
    parser_update.add_argument('-d', '--description',
                               default=None,
                               help='Bug description.')

    parser_update.add_argument('-f', '--affects-project',
                               default=None,
                               help='Also affects project')

    parser_update.add_argument('-s', '--status',
                               choices=statuses_update,
                               default=None,
                               help='Bug status.')
    parser_update.add_argument('-i', '--importance',
                               choices=importance,
                               default=None,
                               help='Bug importance.')
    parser_update.add_argument('-m', '--milestone',
                               default=None,
                               help='Milestone')
    parser_update.add_argument('-t', '--tags',
                               nargs='+',
                               default=[],
                               help='Add specified tags.')
    parser_update.add_argument('-a', '--assignee',
                               default=None,
                               help='Assign bug to specified user/group.')
    #TODO: add attach subcommand w/ parameters:
    #TODO: "Description for it" --patch(True/False) filename

    return parser


def command_comment(launchpad_client, options):
    comment = ' '.join(options.comment).strip()
    print 'Added comment: {}'.format(
        launchpad_client.add_comment(comment=comment,
                                     bug_id=options.bug_id).web_link)


def command_comment(launchpad_client, options):
    properties = vars(options)
    properties['comment'] = ' '.join(options.comment).strip()
    comment = launchpad_client.add_comment(**properties)
    if comment is not None:
        print 'Added comment: {}'.format(comment.web_link)


def command_report(launchpad_client, options):
    title = options.title
    description = options.description
    properties = vars(options)
    properties.pop('title', None)
    properties.pop('description', None)
    for k in properties.keys():
        if properties[k] is None or properties[k] == []:
            properties.pop(k, None)
    bug = launchpad_client.create_bug(title, description, **properties)
    print 'Reported bug #{} {}'.format(bug.id, bug.web_link)


def command_update(launchpad_client, options):
    properties = vars(options)
    for k in properties.keys():
        if properties[k] is None or properties[k] == []:
            properties.pop(k, None)
    bug = launchpad_client.update_bug(**properties)
    print 'Updated bug #{} {}'.format(bug.id, bug.web_link)


def main():

    parser = get_argparser()
    options = parser.parse_args()
    lp = launchpad_client(project=options.project)
    properties = vars(options)
    if 'affects_only' in properties and properties['affects_only'] is not None:
        properties['affects_only'] = \
            set(re.split(' |,|;|/', properties['affects_only']))
    else:
        properties['affects_only'] = set([properties['project']])
    options.func(lp, options)


if __name__ == '__main__':
    main()
