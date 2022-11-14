import os
import sys
from loguru import logger


def make_tool_dir(params, tool_name, tool_version):
    install_dir_path = params['install_dir_path']
    path_tool = os.path.join(install_dir_path, tool_name, tool_version)
    if os.path.isdir(path_tool):
        logger.warning(f"{path_tool} already exist")
        logger.warning(f"File(s) inside will be overwritten")
    else:
        logger.info(f"Create install folder at: {path_tool}")
        os.makedirs(path_tool)
    return path_tool


def conda_tool(params, tool_name, tool_version):
    logger.info(f"Conda installation")
    install_conda = params['conda_envs_path']
    install_dir = params['install_dir_path']
    path_tool = os.path.join(install_dir, tool_name, tool_version)
    env_tool = tool_name + '-' + tool_version
    path_env = os.path.join(install_conda, env_tool)
    if not os.path.isdir(path_env):
        logger.error(f"{path_env} does not exist")
        logger.error(f"Was conda environment has been created?")
        exit(1)
    logger.info(f"Create env.sh and delenv.sh")
    env_sh = open(os.path.join(path_tool, 'env.sh'), 'w')
    env_sh.write(f"#!/usr/bin/env bash\n")
    env_sh.write(f". {params['anaconda_profile_d']}\n")
    env_sh.write(f"conda activate {path_env}\n")
    env_sh.close()
    delenv_sh = open(os.path.join(path_tool, 'delenv.sh'), 'w')
    delenv_sh.write(f"#!/usr/bin/env bash\n")
    delenv_sh.write(f"conda deactivate\n")
    delenv_sh.write(f'PATH=$(echo "$PATH" | sed -e "s@ {params["anaconda_dir_path"]}.*/condabin:@@g")\n')
    delenv_sh.write(f"unset CONDA_EXE CONDA_PYTHON_EXE\n")
    delenv_sh.close()
