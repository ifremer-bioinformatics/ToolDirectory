import os
import sys


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def make_tool_dir(params, args):
    install_dir_path = params['install_dir_path']
    tool_name = args.tool_name
    tool_version = args.tool_version
    path_tool = os.path.join(install_dir_path, tool_name, tool_version)
    if os.path.isdir(path_tool):
        eprint(f"\033[0;31;47m WARNING:" + path_tool + " already exist! \033[0m")
        eprint(f"\033[0;31;47m WARNING: file(s) inside will be overwritten \033[0m")
    else:
        eprint(f"\033[0;37;46m LOG: Create install folder at: " + path_tool + "\033[0m")
        os.makedirs(path_tool)
    return path_tool


def conda_tool(params, args):
    eprint(f"\033[0;37;46m LOG: Conda installation detected \033[0m")
    tool_name = args.tool_name
    tool_version = args.tool_version
    install_conda = params['conda_envs_path']
    install_dir = params['install_dir_path']
    path_tool = os.path.join(install_dir, tool_name, tool_version)
    env_tool = tool_name + '-' + tool_version
    path_env = os.path.join(install_conda, env_tool)
    if not os.path.isdir(path_env):
        eprint(f"\033[0;31;47m ERROR:" + path_env + " do not exist! \033[0m")
        eprint(f"\033[0;31;47m ERROR: Was conda environment has been created? \033[0m")
        eprint(f"\033[0;31;47m ERROR: Processus killed \033[0m")
        exit(1)

    env_sh = open(os.path.join(path_tool, 'env.sh'), 'w')
    env_sh.write('#!/usr/bin/env bash\n')
    env_sh.write('. ' + params['anaconda_profile_d'] + '\n')
    env_sh.write('conda activate ' + path_env + '\n')
    env_sh.close()
    delenv_sh = open(os.path.join(path_tool, 'delenv.sh'), 'w')
    delenv_sh.write('#!/usr/bin/env bash\n')
    delenv_sh.write('conda deactivate\n')
    delenv_sh.write('PATH=$(echo "$PATH" | sed -e "s@' + params['anaconda_dir_path'] + '.*/condabin:@@g")\n')
    delenv_sh.write('unset CONDA_EXE CONDA_PYTHON_EXE\n')
    delenv_sh.close()
    eprint(f"\033[0;37;46m LOG: Create env.sh and delenv.sh \033[0m")