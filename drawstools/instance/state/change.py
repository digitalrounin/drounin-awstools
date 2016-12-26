#! /usr/bin/env python

import argparse
import logging
import logging.config
import os
import re
import sys

from termios import tcflush, TCIOFLUSH

import boto3

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
NAME = 'ec2-instance-start-stop'
LOGGER = None
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'level': 'INFO',
            'formatter': 'default'
        }
    },
    'loggers': {
        NAME: {
            'handlers': ['console'],
            'level': 'INFO'
        }
    }
}


# -----------------------------------------------------------------------------
# The Code
# -----------------------------------------------------------------------------
def get_instance_name(instance):
    tag = list(filter(lambda x: x['Key'] == 'Name', instance.tags))
    return tag[0]['Value']


def stop_instances(instances, dry_run=False, cmd_args=None):
    # pylint: disable=unused-argument
    for instance in instances:
        state = instance.state['Name']
        name = get_instance_name(instance)
        if state in ('running', 'pending'):
            LOGGER.info('Changing state of "{}" from "{}" to "{}".'
                        .format(name, state, 'stopped'))
            if not dry_run:
                instance.stop()
            else:
                LOGGER.warning('No change made, in "dry-run" mode.')
        elif state == 'terminated':
            LOGGER.info('Instance "{}" is "terminated".  Cannot start.'
                        .format(name))
        else:
            LOGGER.info('Instance "{}" is already stopped, or stopping.'
                        .format(name))


def start_instances(instances, dry_run=False, cmd_args=None):
    # pylint: disable=unused-argument
    for instance in instances:
        state = instance.state['Name']
        name = get_instance_name(instance)
        if state not in ('running', 'terminated'):
            LOGGER.info('Changing state of "{}" from "{}" to "{}".'
                        .format(name, state, 'running'))
            if not dry_run:
                instance.start()
            else:
                LOGGER.warning('No change made, in "dry-run" mode.')
        elif state == 'terminated':
            LOGGER.info('Instance "{}" is "terminated".  Cannot start.'
                        .format(name))
        else:
            LOGGER.info('Instance "{}" is already running.'
                        .format(name))


def terminate_instances(instances, dry_run=False, cmd_args=None):
    for instance in instances:
        state = instance.state['Name']
        name = get_instance_name(instance)
        if not (cmd_args.force or confirm('terminate', name, instance.id)):
            continue

        if state != 'terminated':
            LOGGER.info('Changing state of "{}" from "{}" to "{}".'
                        .format(name, state, 'terminated'))
            if not dry_run:
                instance.terminate()
            else:
                LOGGER.warning('No change made, in "dry-run" mode.')
        else:
            LOGGER.info('Instance "{}" is already terminated.'
                        .format(name))


def confirm(action, instance, instance_id):
    responce = ''
    while responce not in ('a', 'y', 'n'):
        tcflush(sys.stdin, TCIOFLUSH)
        responce = input('"{}" instance "{}({})" (y/n/a): '
                         .format(action, instance, instance_id))
        responce = responce.lower()

    if responce == 'y':
        return True
    elif responce == 'n':
        return False
    elif responce == 'a':
        LOGGER.warn('Aborting')
        sys.exit(1)
    else:
        raise NotImplementedError('Unknown responce of "{}".'.format(responce))


def get_instances_by_name(values, region):
    ec2 = boto3.resource('ec2', region_name=region)
    name_filter = {'Name': 'tag:Name', 'Values': values}
    return ec2.instances.filter(Filters=[name_filter])


def get_instances_by_id(values, region):
    ec2 = boto3.resource('ec2', region_name=region)
    return ec2.instances.filter(InstanceIds=values)


def get_instances_by_name_regex(values, region):
    regexes = [re.compile(x) for x in values]
    matched_instances = list()
    ec2 = boto3.resource('ec2', region_name=region)
    for instance in ec2.instances.all():
        instance_names = get_instance_name(instance)
        if any(x.match(instance_names) for x in regexes):
            matched_instances.append(instance)
    return matched_instances


def config_logging(log_file=None):
    # pylint: disable=global-statement
    if log_file:
        log_file = os.path.abspath(log_file)
        LOGGING_CONFIG['handlers'].update({
            'file': {
                'class': 'logging.FileHandler',
                'filename': log_file,
                'level': 'INFO',
                'formatter': 'default',
            }})

        LOGGING_CONFIG['loggers'][NAME]['handlers'].append('file')
    logging.config.dictConfig(LOGGING_CONFIG)
    global LOGGER
    LOGGER = logging.getLogger(NAME)
    if log_file:
        LOGGER.info('Logging to "%s"', log_file)


def process_args():
    # ---
    # Process command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run',
                        action='store_true',
                        dest='dry_run',
                        help='Run in dry-run mode (default: False)')

    parser.add_argument('--log-file',
                        type=str,
                        required=False,
                        dest='log_file',
                        help='File to log to')

    parser.add_argument('--region',
                        type=str,
                        required=True,
                        help='AWS region')

    values_type_group = parser.add_mutually_exclusive_group()
    values_type_group.add_argument('--instance-names',
                                   action='store_const',
                                   const=get_instances_by_name,
                                   dest='instances_getter',
                                   help=('Values are a list instance names '
                                         '(default)'))
    values_type_group.add_argument('--instance-name-regexes',
                                   action='store_const',
                                   const=get_instances_by_name_regex,
                                   dest='instances_getter',
                                   help=('Values are a list instance name '
                                         'regexes'))
    values_type_group.add_argument('--instance-ids',
                                   action='store_const',
                                   const=get_instances_by_id,
                                   dest='instances_getter',
                                   help='Values are a list of instance_ids')
    values_type_group.set_defaults(instances_getter=get_instances_by_name)
    parser.add_argument_group(values_type_group)

    common = {
        'type': str,
        'nargs': argparse.REMAINDER,
        'help': 'list of either instance names, name regexes, or ids'}
    subparsers = parser.add_subparsers(help='State to transition to')

    start_parser = subparsers.add_parser('start')
    start_parser.add_argument('values', **common)
    start_parser.set_defaults(func=start_instances)

    stop_parser = subparsers.add_parser('stop')
    stop_parser.add_argument('values', **common)
    stop_parser.set_defaults(func=stop_instances)

    terminate_parser = subparsers.add_parser('terminate')
    terminate_parser.set_defaults(func=terminate_instances)
    terminate_parser.add_argument(
        '--force',
        action='store_true',
        dest='force',
        help='Do not prompt for confirmation (default: False)')

    terminate_parser.add_argument('values', **common)

    return parser.parse_args()


def main():
    args = process_args()
    config_logging(log_file=args.log_file)
    LOGGER.info('Execution started')
    instances = args.instances_getter(values=args.values, region=args.region)
    args.func(instances=instances, dry_run=args.dry_run, cmd_args=args)
    LOGGER.info('Execution ended')


if __name__ == '__main__':
    main()

# vim: filetype=python tabstop=4 shiftwidth=4 expandtab nowrap
