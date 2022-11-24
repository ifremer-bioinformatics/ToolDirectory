#!/usr/bin/env python3

import os
from lib import core as cl
from loguru import logger
import rich_click as click

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.version_option("1.0", prog_name="systemd_call.py")
@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('-p', '--path', type=click.Path(exists=True), default='../test_env/', required=True,
              help='Path to tools dir.')
def main(path):
    logger.info(f'Explorer path')
    directories = cl.walk_level(path)
    logger.info(f'Collect env.sh files')
    envs = get_envs(directories)
    logger.info(f'Check calls in env.sh files')
    envs = check_existing_call(envs)
    logger.info('Add systemd call to env.sh')
    add_systemd_call(envs)


def get_envs(directories):
    envs_lst = []
    for root, dirs, files in directories:
        if 'env.sh' in files:
            abs_f = os.path.join(root, 'env.sh')
            logger.info(f'Found env.sh at: {abs_f}')
            envs_lst.append(abs_f)
    return envs_lst


def check_existing_call(envs):
    word = 'sebimer-tool-activation'
    envs_filter = []
    for env in envs:
        with open(env, 'r') as file:
            content = file.read()
            if word not in content:
                envs_filter.append(env)
            else:
                logger.warning(f'Call already present in {env}')
    return envs_filter


def add_systemd_call(envs):
    for env in envs:
        folders = os.path.normpath(env).split(os.path.sep)
        tool_name = folders[-3]
        tool_version = folders[-2]
        logger.info(f'Add call to: {tool_name}-{tool_version}')
        try:
            env_app = open(env, 'a')
            env_app.write(f'\n')
            env_app.write(
                f'echo "`date +%d-%m-%Y`|sebimer-tool-activation|{tool_name}:{tool_version}:`hostname`:`whoami`" | systemd-cat -p info')
            env_app.close()
        except Exception as error:
            logger.error(f"Error occurred: {error}")
            pass


if __name__ == '__main__':
    main()
