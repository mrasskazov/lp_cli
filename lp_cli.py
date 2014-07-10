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

from launchpadlib.launchpad import Launchpad
from launchpadlib.launchpad import uris


class launchpad_client(object):

    def __init__(self, project, bug_id=None):

        lp_cache_dir = os.path.expanduser(
            os.environ.get('LAUNCHPAD_CACHE_DIR',
                           '~/.launchpadlib/cache'))

        lp_creds_filename = os.path.expanduser(
            os.environ.get('LAUNCHPAD_CREDS_FILENAME',
                           '~/.launchpadlib/creds'))

        self.Launchpad = Launchpad.login_with(
            project,
            uris.LPNET_SERVICE_ROOT,
            lp_cache_dir,
            credentials_file=lp_creds_filename)

        self.Project = self.launchpad.projects[project]

        self.Bug = None
        self.Tasks = []
        if bug_id is not None:
            self.Bug = self.bug(bug_id)

            self.Tasks = self.tasks(bug_id)

    @property
    def launchpad(self):
        return self.Launchpad

    @property
    def project(self):
        return self.Project

    def bug(self, bug_id=None):
        return self.Bug if bug_id is None else self.launchpad.bugs[bug_id]

    def tasks(self, bug_id=None):
        if bug_id is not None:
            for task in self.bug(bug_id).bug_tasks:
                if task.bug_target_name == self.project.name:
                    self.Tasks.append(task)
            if not self.Tasks:
                raise Exception("Bug #{} not affected on project '{}'".format(
                    bug_id, self.project))
        return self.Tasks

    def add_comment(self, comment):
        return self.bug().newMessage(content=comment)

    def change_status(self, status, current_status=None):
        for task in self.tasks():
            #if current_status:
            #    if task.status != current_status:
            #        raise Exception('Bug status is not updated because '
            #                        'current value is not up to expectations')
            task.status = status
            task.lp_save()

    def create_bug(self, title, description):
        return self.launchpad.bugs.createBug(target=self.project.self_link,
                                             title=title,
                                             description=description)


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

    accessibility = ['Public',
                     'Public Security',
                     'Private',
                     'Private Seciruty',
                     'Proprietary']

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
                        help='Launchpad project\'s name for auth.')
    parser.add_argument('-a', '--affected',
                        nargs='*',
                        default=None,
                        help='Launchpad project\'s name for check that bug is '
                        'affected on it. If specified, bug will be updated '
                        'only in this case.')

    subparsers = parser.add_subparsers(title='Commands')

    parser_comment = subparsers.add_parser('comment')
    parser_comment.set_defaults(func=command_comment)
    parser_comment.add_argument('bug_id', help='Bug id on Launchpad.')
    parser_comment.add_argument('comment', help='Comment body.', nargs='+')

    parser_status = subparsers.add_parser('status')
    parser_status.set_defaults(func=command_status)
    parser_status.add_argument('bug_id', help='Bug id on Launchpad.')
    parser_status.add_argument('-s', '--status',
                               help='New status for a bug.')
    #parser_status.add_argument('-c', '--current-status',
    #                           help='Current status for bug. If specified, '
    #                           'status will be updated only when according.')

    parser_report = subparsers.add_parser('report')
    parser_report.set_defaults(func=command_report)
    parser_report.add_argument('title',
                               nargs='+',
                               help='Bug title.')
    parser_report.add_argument('-d', '--description',
                               nargs='+',
                               default=None,
                               help='Bug description.')
    parser_report.add_argument('-a', '--accessibility',
                               default='Public',
                               choices=accessibility,
                               help='Bug accessibility')

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
                               help='Add specified tags.')
    parser_report.add_argument('-o', '--assign-to',
                               default=None,
                               help='Assign bug to specified user/group.')
    #TODO: add attach subcommand w/ parameters:
    #TODO: "Description for it" --patch(True/False) filename

    parser_update = subparsers.add_parser('update')
    parser_update.set_defaults(func=command_update)
    parser_update.add_argument('title',
                               nargs='+',
                               help='Bug title.')
    parser_update.add_argument('-d', '--description',
                               nargs='+',
                               default=None,
                               help='Bug description.')
    parser_update.add_argument('-a', '--accessibility',
                               default='Public',
                               choices=accessibility,
                               help='Bug accessibility')

    parser_update.add_argument('-s', '--status',
                               choices=statuses_update,
                               default='New',
                               help='Bug status.')
    parser_update.add_argument('-i', '--importance',
                               choices=importance,
                               default='Undecided',
                               help='Bug importance.')
    parser_update.add_argument('-m', '--milestone',
                               default=None,
                               help='Milestone')
    parser_update.add_argument('-t', '--tags',
                               nargs='+',
                               help='Add specified tags.')
    parser_update.add_argument('-o', '--assign-to',
                               default=None,
                               help='Assign bug to specified user/group.')
    #TODO: add attach subcommand w/ parameters:
    #TODO: "Description for it" --patch(True/False) filename

    return parser


def command_comment(launchpad_client, options):
    comment = ' '.join(options.comment).strip()
    print 'Added comment: {}'.format(
        launchpad_client.add_comment(comment).web_link)


def command_status(launchpad_client, options):
    launchpad_client.change_status(options.status)
    print 'Status for bug #{} changed to "{}"'.format(options.bug_id,
                                                      options.status)


def command_report(launchpad_client, options):
    title = ' '.join(options.title).strip()
    description = ' '.join(options.description).strip() or ''
    bug = launchpad_client.create_bug(title, description)
    print 'Reported bug #{} {}'.format(bug.id, bug.web_link)


def main():

    parser = get_argparser()
    options = parser.parse_args()
    #lp = launchpad_client(project=options.project, bug_id=options.bug_id)
    lp = launchpad_client(project=options.project)
    options.func(lp, options)


if __name__ == '__main__':
    main()
