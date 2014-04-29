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
import ConfigParser
import os
import sys

from launchpadlib.launchpad import Launchpad
from launchpadlib.launchpad import uris


lp_cache_dir = os.path.expanduser(
    os.environ.get('LAUNCHPAD_CACHE_DIR', '~/.launchpadlib/cache'))

lp_creds_filename = os.path.expanduser(
    os.environ.get('LAUNCHPAD_CREDS_FILENAME', '~/.launchpadlib/creds'))


def get_argparser():

    parser = argparse.ArgumentParser(prog='lp_cli.py',
                                     description='Command line client '
                                     'for Launchpad')
    parser.add_argument('project',
                        help='Launchpad project\'s name.')
    parser.add_argument('message',
                        help='Message body. Can be multiline. Use quites.')
    parser.add_argument('bug_id',
                        help='Bug id to list.',
                        nargs='+')
    return parser


def main():

    try:
        parser = get_argparser()
        options = parser.parse_args()
    except Exception, ex:
        sys.exit(str(ex))

    launchpad = Launchpad.login_with(options.project.lower(),
                                     uris.LPNET_SERVICE_ROOT,
                                     lp_cache_dir,
                                     credentials_file=lp_creds_filename,
                                     version='devel')
    project = launchpad.projects[options.project]
    for bid in options.bug_id:
        bug = launchpad.bugs[bid]
        o_bugs = project.searchTasks(owner=bug.owner)
        for b in o_bugs:
            if bug.self_link == b.bug_link:
                print bug
                print bug.title
                print bug.owner
                print bug.newMessage(content=options.message)


if __name__ == '__main__':
    main()
