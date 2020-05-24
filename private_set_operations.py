#!/usr/bin/python3
import argparse
from argparse import RawTextHelpFormatter
from http import HTTPStatus
import sys
import getpass
import ssl
import http.client
import json
import datetime

def main():
    
    client = Client()

    description = 'Welcome to the Vulnerability Submission Platform\n\
    register                    Register new client account\n\
    submit                      Submit vulnerability\n\
    show                        Show submissions\n\
    score                       Show scores\n\
    admin_show                  Show submissions of all users\n\
    admin_remove_user           Removes a user\n\
    admin_remove_submission     Removes a submission\n'

    usage = '\n\
    client <command> [<args>]\n\
    client register\n\
    client submit <vuln_description> <fingerprint>\n\
    client show\n\
    client score\n\
    client admin_show\n\
    client admin_remove_user <username_to_remove>\n\
    client admin_remove_submission <id_to_remove>\n'

    parser = argparse.ArgumentParser(prog='client', description=description,
                                     usage=usage, formatter_class=RawTextHelpFormatter)
    parser.add_argument('command', type=str, choices=['register', 'submit', 'show', 'score',
                                                      'admin_show',
                                                      'admin_remove_user', 'admin_remove_submission'])
    parser.add_argument('first', nargs='?')
    parser.add_argument('second', nargs='?')

    args = parser.parse_args()

    if args.command.__eq__('register'):
        client.register()
    elif args.command.__eq__('submit'):
        # args.first => vuln_description
        # args.second => fingerprint
        if args.first and args.second:
            client.submit(args.first, args.second)
        else:
            parser.error('wrong arguments for submit command')
    elif args.command.__eq__('show'):
        client.show()
    elif args.command.__eq__('score'):
        client.score()
    elif args.command.__eq__('admin_show'):
        client.admin_show()
    elif args.command.__eq__('admin_remove_user'):
        # args.first => usernameToRemove
        if args.first:
            client.remove_user(args.first)
        else:
            parser.error('wrong arguments for remove_user command')
    elif args.command.__eq__('admin_remove_submission'):
        # args.first => idToRemove
        if args.first:
            client.remove_submission(args.first)
        else:
            parser.error('wrong arguments for remove_user command')


if __name__ == "__main__":
    main()