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

CONFIG = dict()


def config(key, unset=False):

    conf_dir_name = '~/.config/ls_cli'
    conf_file_name = os.path.expanduser(conf_dir_name + '/ls_cli.conf')
    parser = ConfigParser.ConfigParser()

    if os.path.isfile(conf_file_name):
        parser.read(conf_file_name)
    else:
        print 'no config file found, generating it'
        if not os.path.isdir(os.path.expanduser(conf_dir_name)):
            os.makedirs(os.path.expanduser(conf_dir_name))

    parser.has_section('general') or parser.add_section('general')

    if unset:
        del CONFIG[key]
        parser.remove_option('general', key)

    if key in CONFIG:
        return CONFIG.get(key)
    elif parser.has_option('general', key):
        CONFIG[key] = parser.get('general', key)
        return parser.get('general', key)
    elif key == 'project':
        project = raw_input('enter project:')
        CONFIG['project'] = project
        parser.set('general', 'project', project)

    with open(conf_file_name, 'wb') as conf_file:
        parser.write(conf_file)

    return CONFIG[key]


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

    launchpad = Launchpad.login_with(options.project.lower(), 'production')
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
