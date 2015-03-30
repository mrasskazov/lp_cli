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
import re

from launchpad_client import launchpad_client


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
    parser.add_argument('-a', '--update-if-affects-another',
                        action='store_true',
                        required=False,
                        default=False,
                        help='Perform operation if bug affects more projects '
                        'than specified in "project" or "--affects-only". '
                        'Operation will be skipped in this case by default.')

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
