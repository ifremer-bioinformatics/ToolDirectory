#!/usr/bin/env python3

import os
import rich_click as click
from .lib import core as td


@click.version_option("5.1.1", prog_name="tooldir")
@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """
    ToolDirectory: A dynamic visualization of pieces of software managed by a Bioinformatics Core Facility
    """


@cli.command()
@click.option('--name', '-n', type=str, required=True, help='Tool name')
@click.option('--bid', '-b', type=str, help='Bio.tools tool ID')
@click.option('--version', '-v', type=str, required=True, help='Tool version')
@click.option('--owner', '-o', type=str, required=True, help='Installer uid')
@click.option('--cmd', '-c', type=click.Choice(['true', 'false']), default='true', help='Available in cmdline [True]')
@click.option('--galaxy', '-g', type=click.Choice(['true', 'false']), default='false',
              help='Available in Galaxy [False]')
@click.option('--environment', '-e', type=click.Choice(['conda', 'bash', 'docker', 'singularity', 'other']), default='conda',
              help='conda/bash/docker/singularity/other [conda]')
@click.option('--workflow', '-w', type=click.Choice(['false', 'true']), default='false', help='Is a workflow')
@click.option('--path', '-p', type=click.Path(exists=True), required=True, help='Path to modulefiles')
@click.option('--date', '-d', type=str, help='Installation date [Current date]')
def create(name, bid, version, owner, cmd, galaxy, environment, workflow, path, date):
    """Create tool properties or add a new version"""
    td.check_path(path, name, version)
    properties = os.path.join(path, name, 'properties.json')
    if os.path.isfile(properties):
        td.add_version(name, version, date, owner, environment, cmd, galaxy, workflow, properties)
    else:
        td.create_properties(name, bid, version, owner, cmd, galaxy, environment, workflow, date, properties)


@cli.command()
@click.option('--json', '-j', type=click.Path(exists=True), required=True, help='Path to json')
@click.option('--bid', '-b', type=str, help='Force update using Bio.tools ID')
def update(json, bid):
    """Update metadata of a tool"""
    td.update(json, bid)


@cli.command()
@click.argument('version', nargs=-1, type=str)
@click.option('--json', '-j', type=click.Path(exists=True), required=True, help='Path to json')
@click.option('--status', '-s', type=click.Choice(['active', 'inactive']), default='inactive',
              help='Version status [active]')
def status(version, json, status):
    """Set installation status of a tool's version"""
    td.set_status(json, version, status)


@cli.command()
@click.option('--path', '-p', type=click.Path(exists=True), required=True, help='Tools main folder')
@click.option('--csv', '-c', type=str, required=True, help='Output csv name')
def kcsv(path, csv):
    """Create csv for Keshif visualisation"""
    directories = td.walk_level(path)
    prop_json = td.get_json(directories)
    td.kcsv_writing(csv, prop_json)


click.rich_click.COMMAND_GROUPS = {
    "tooldir": [
        {
            "name": "Main usage",
            "commands": ["create", "update", "status"],
        },
        {
            "name": "Visualization",
            "commands": ["kcsv"],
        },
    ]
}

if __name__ == "__main__":
    cli()
