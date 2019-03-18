# -*- coding: utf-8 -*-

import os
from subprocess import Popen, PIPE

from opinel.utils.console import printError
from opinel.utils.fs import read_ip_ranges


#
# AWS recipes test class (Python only)
#
class TestPythonRecipesClass:

    #
    # Implement cmp() for tests in Python3
    #
    def cmp(self, a, b):
        tmp1 = sorted(a, key = lambda x:sorted(x.keys()))
        tmp2 = sorted(b, key = lambda x:sorted(x.keys()))
        return (tmp1 > tmp2) - (tmp1 < tmp2)

    #
    # Set up
    #
    def setUp(self):
        self.recipes_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../Python'))
        self.recipes = [f for f in os.listdir(self.recipes_dir) if os.path.isfile(os.path.join(self.recipes_dir, f)) and f.startswith('awsrecipes_') and f.endswith('.py')]
        self.data_dir = 'tests/data'
        self.result_dir = 'tests/results'

    #
    # Every Python recipe must run fine with --help
    #
    def test_all_recipes_help(self):
        successful_help_runs = True
        for recipe in self.recipes:
            recipe_path = os.path.join(self.recipes_dir, recipe)
            process = Popen(['python', recipe_path, '--help'], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()
            if exit_code != 0:
                print('The recipe %s does not run properly.' % recipe)
                successful_help_runs = False
        assert successful_help_runs

    #
    # Every python recipe must have a test method
    #
    def all_recipes_test_function_must_exist(self):
        for recipe in self.recipes:
            methods = dir(self)
            method_name = 'test_%s' % recipe.replace('.py', '')
            if method_name not in methods:
                printError('%s does not exist.' % method_name)
            assert method_name in methods

    #
    #
    #
    def test_awsrecipes_enable_mfa(self):
        print('a')

    #
    #
    #
    def test_awsrecipes_assume_role(self):
        print('a')

    #
    #
    #
    def test_awsrecipes_configure_iam(self):
        print('a')

    #
    # Test aws_recipes_create_ip_ranges.py
    #
    def test_awsrecipes_create_ip_ranges(self):
        successful_aws_recipes_create_ip_ranges_runs = True
        recipe = os.path.join(self.recipes_dir, 'awsrecipes_create_ip_ranges.py')
        test_cases = [
            # Matching header names, use all data
            ['--csv-ip-ranges tests/data/ip-ranges-1.csv --force', 'ip-ranges-1a.json'],
            # Matching header names, use partial data
            ['--csv-ip-ranges tests/data/ip-ranges-1.csv --force --attributes ip_prefix field_b --skip-first-line', 'ip-ranges-1b.json'],
            # Matching header names, use partial data with mappings (must skip first line)
            ['--csv-ip-ranges tests/data/ip-ranges-1.csv --force --attributes ip_prefix field_b --mappings 0 2 --skip-first-line', 'ip-ranges-1c.json'],
            # Matching header names but swap with mappings (must skip first line)
            ['--csv-ip-ranges tests/data/ip-ranges-1.csv --force --attributes ip_prefix field_a --mappings 0 2 --skip-first-line', 'ip-ranges-1d.json'],
            # No headers, use all data
            ['--csv-ip-ranges tests/data/ip-ranges-2.csv --force --attributes ip_prefix field_a, field_b --mappings 0 1 2', 'ip-ranges-2a.json'],
            # No headers, use partial data
            ['--csv-ip-ranges tests/data/ip-ranges-2.csv --force --attributes ip_prefix field_b --mappings 0 2', 'ip-ranges-2b.json'],
            # Different header names (must skip first line)
            ['--csv-ip-ranges tests/data/ip-ranges-3.csv --force --attributes ip_prefix new_field_b --mappings 0 2 --skip-first-line', 'ip-ranges-3a.json'],
            # Different header names with ip_prefix not in first column (must skip first line)
            ['--csv-ip-ranges tests/data/ip-ranges-4.csv --force --attributes ip_prefix new_field_a new_field_b --mappings 1 0 2 --skip-first-line', 'ip-ranges-4a.json'],
        ]
        for test_case in test_cases:
            args, result_file = test_case
            cmd =  ['python' , recipe] + args.split(' ')
            process = Popen(cmd, stdout=PIPE)
            exit_code = process.wait()
            if exit_code != 0:
                print('The recipe %s failed to run with arguments %s.' % (recipe, args))
                successful_aws_recipes_create_ip_ranges_runs = False
                continue
            test_results = read_ip_ranges('ip-ranges-default.json')
            known_results = read_ip_ranges(os.path.join(self.result_dir, result_file))
            if self.cmp(test_results, known_results) != 0:
                print('Failed when comparing:\n%s\n%s\n' % (test_results, known_results))
                successful_aws_recipes_create_ip_ranges_runs = False
            os.remove('ip-ranges-default.json')
        assert(successful_aws_recipes_create_ip_ranges_runs)

    #
    #
    #
    def test_awsrecipes_init_sts_session(self):
        print('a')

    def test_awsrecipes_configure_organization_profiles(self):
        pass

    def test_awsrecipes_delete_iam_user(self):
        pass

    def test_awsrecipes_get_all_ips(self):
        pass
    
    def test_awsrecipes_get_cloudtrail_logs(self):
        pass

    def test_awsrecipes_create_iam_user(self):
        pass

    def test_awsrecipes_rotate_my_key(self):
        pass

    def test_awsrecipes_get_iam_permissions(self):
        pass

    def test_awsrecipes_create_default_iam_groups(self):
        pass

    def test_awsrecipes_empty_default_security_groups(self):
        pass

    def test_awsrecipes_create_iam_policy(self):
        pass

    def test_awsrecipes_sort_iam_users(self):
        pass

    def test_awsrecipes_enable_organization_forward_events(self):
        pass

    def test_awsrecipes_create_cloudformation_stack(self):
        pass

    def test_awsrecipes_deploy_stacks(self):
        pass
