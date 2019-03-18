#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

from opinel.utils.aws import connect_service, get_aws_account_id
from opinel.utils.cli_parser import OpinelArgumentParser
from opinel.utils.console import configPrintException, printError, printException, printInfo, prompt_4_value, prompt_4_yes_no
from opinel.utils.credentials import read_creds
from opinel.utils.globals import check_requirements

########################################
##### Globals
########################################

re_aws_account_id = re.compile('AWS_ACCOUNT_ID', re.DOTALL|re.MULTILINE)

########################################
##### Main
########################################

def main():

    # Parse arguments
    parser = OpinelArgumentParser()
    parser.add_argument('debug')
    parser.add_argument('profile')
    parser.add_argument('managed',
                        dest='is_managed',
                        default=False,
                        action='store_true',
                        help='Create a managed policy.')
    parser.add_argument('type',
                        default=[ None ],
                        nargs='+',
                        choices=['group', 'managed', 'role', 'user'],
                        help='Type of target that the policy will apply or be attached to.')
    parser.add_argument('targets',
                        default=[],
                        nargs='+',
                        help='Name of the IAM entity the policy will be added to (required for inline policies).')
    parser.add_argument('templates',
                        default=[],
                        nargs='+',
                        help='Path to the template IAM policies that will be created.')
    parser.add_argument('save',
                        dest='save_locally',
                        default=False,
                        action='store_true',
                        help='Generates the policies and store them locally.')
    args = parser.parse_args()

    # Configure the debug level
    configPrintException(args.debug)

    # Check version of opinel
    if not check_requirements(os.path.realpath(__file__)):
        return 42

    # Arguments
    profile_name = args.profile[0]
    target_type = args.type[0]
    if len(args.templates) == 0:
        printError('Error: you must specify the path the template IAM policies.')
        return 42
    if not args.is_managed and target_type == None:
        printError('Error: you must either create a managed policy or specify the type of IAM entity the policy will be attached to.')
        return 42
    if not args.is_managed and target_type == None and len(args.targets) < 1:
        printError('Error: you must provide the name of at least one IAM %s you will attach this inline policy to.' % target_type)
        return 42

    # Read creds
    credentials = read_creds(args.profile[0])
    if not credentials['AccessKeyId']:
        return 42

    # Connect to IAM APIs
    iam_client = connect_service('iam', credentials)
    if not iam_client:
        return 42

    # Get AWS account ID
    aws_account_id = get_aws_account_id(credentials)

    # Create the policies
    for template in args.templates:
        if not os.path.isfile(template):
            printError('Error: file \'%s\' does not exist.' % template)
            continue
        with open(template, 'rt') as f:
            policy = f.read()
        policy = re_aws_account_id.sub(aws_account_id, policy)
        policy_name = os.path.basename(template).split('.')[0]
        if not args.is_managed:
            callback = getattr(iam_client, 'put_' + target_type + '_policy')
            params = {}
            params['PolicyName'] = policy_name
            params['PolicyDocument' ] = policy
            for target in args.targets:
                params[target_type.title() + 'Name'] = target
                try:
                    printInfo('Creating policy \'%s\' for the \'%s\' IAM %s...' % (policy_name, target, target_type))
                    callback(**params)
                except Exception as e:
                    printException(e)
                    pass
        else:
            params = {}
            params['PolicyDocument'] = policy
            params['PolicyName'] = policy_name
            description = ''
            # Search for a description file
            descriptions_dir = os.path.join(os.path.dirname(template), 'descriptions')
            if os.path.exists(descriptions_dir):
                description_file = os.path.join(descriptions_dir, os.path.basename(template).replace('.json', '.txt'))
                if os.path.isfile(description_file):
                    with open(description_file, 'rt') as f:
                        params['Description'] = f.read()
            elif prompt_4_yes_no('Do you want to add a description to the \'%s\' policy' % policy_name):
                params['Description'] = prompt_4_value('Enter the policy description:')
            params['Description'] = params['Description'].strip()
            printInfo('Creating policy \'%s\'...' % (policy_name))
            new_policy = iam_client.create_policy(**params)
            if len(args.targets):
                callback = getattr(iam_client, 'attach_' + target_type + '_policy')
                for target in args.targets:
                    printInfo('Attaching policy to the \'%s\' IAM %s...' % (target, target_type))
                    params = {}
                    params['PolicyArn'] = new_policy['Policy']['Arn']
                    params[target_type.title() + 'Name'] = target
                    callback(**params)

        if args.save_locally:
            with open('%s-%s.json' % (policy_name, profile_name), 'wt') as f:
                f.write(policy)
                f.close()


if __name__ == '__main__':
    sys.exit(main())
