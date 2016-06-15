#! /usr/bin/env python

import argparse

import boto3
from colorama import Fore, Style


SESSION = None


def list_status():
    args = parse_args()
    init_aws_session(profile=args.profile, region=args.region)

    instances = list()
    for instance in aws_resource('ec2').instances.all():
        instances.append(InstanceHelper(instance))

    name_size = max(len(instance.name)
                    for instance in instances
                    if instance.name) + 1
    state_size = max(len(instance.state) for instance in instances) + 1

    format_string = '{{:>{}}} : {{:{}}}'.format(name_size, state_size)
    for instance in sorted(instances, key=lambda x: x.name):
        print(format_string.format(instance.name, instance.state_colorized))


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--profile')
    parser.add_argument('--region')
    return parser.parse_args()


class InstanceHelper(object):
    def __init__(self, boto_instance):
        self.boto_instance = boto_instance

    @property
    def tags(self):
        return {tag['Key']: tag['Value']
                for tag in self.boto_instance.tags}

    @property
    def name(self):
        return self.tags.get('Name', None)

    @property
    def state(self):
        return self.boto_instance.state['Name']

    @property
    def state_colorized(self):
        mapping = {
            'running': Fore.GREEN,
            'stopped': Fore.RED,
            'terminated': Fore.MAGENTA,
            'pending': Fore.YELLOW,
            'shutting-down': Fore.YELLOW,
            'stopping': Fore.YELLOW}
        state = self.state
        return '{}{}{}{}'.format(
            Style.BRIGHT, mapping.get(state, Fore.BLUE), state,
            Style.RESET_ALL)

    def __getattr__(self, name):
        """Passing to Boto3 EC2.Instance object by default."""
        return getattr(self.boto_instance, name)


def init_aws_session(profile=None, region=None):
    # pylint: disable=global-statement
    kwargs = {}
    if profile:
        kwargs['profile_name'] = profile
    if region:
        kwargs['region_name'] = region

    global SESSION
    SESSION = boto3.session.Session(**kwargs)


def aws_client(*arg, **kwarg):
    return SESSION.client(*arg, **kwarg)


def aws_resource(*arg, **kwarg):
    return SESSION.resource(*arg, **kwarg)


if __name__ == "__main__":
    list_status()
