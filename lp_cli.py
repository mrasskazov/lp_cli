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

    def __init__(self, project):

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

    @property
    def launchpad(self):
        return self.Launchpad

    @property
    def project(self):
        return self.Project

    def bug(self, bug_id):
        by_id = self.launchpad.bugs[bug_id]
        o_bugs = self.project.searchTasks(owner=by_id.owner)
        for by_own in o_bugs:
            if by_id.self_link == by_own.bug_link:
                return by_id, by_own

    def add_comment(self, bug_id, comment):
        by_id, by_own = self.bug(bug_id)
        return by_id.newMessage(content=comment)


def get_argparser():

    parser = argparse.ArgumentParser(prog='lp_cli.py',
                                     description='Command line client '
                                     'for Launchpad')
    parser.add_argument('project',
                        help='Launchpad project\'s name.')

    subparsers = parser.add_subparsers(title='subcommands')

    parser_comment = subparsers.add_parser('comment')
    parser_comment.set_defaults(func=command_comment)
    parser_comment.add_argument('bug_id', help='Bug id on Launchpad.')
    parser_comment.add_argument('comment', help='Comment body.', nargs='+')
    return parser


def command_comment(launchpad_client, options):
    comment = ' '.join(options.comment).strip()
    print 'Added comment: {}'.format(launchpad_client.add_comment(
        options.bug_id, comment).web_link)


def main():

    parser = get_argparser()
    options = parser.parse_args()
    lp = launchpad_client(project=options.project)
    options.func(lp, options)


if __name__ == '__main__':
    main()
