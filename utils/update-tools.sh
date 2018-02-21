#!/usr/bin/env bash

#
# A shell script used to update tool.properties files
# to introduce the new feature "CMD_INSTALL"
#
# Note: this script creates a copy of all tool.properties
# before updating them... so, after you have checked
# that update is fine, use:
#   find . -name "tool.properties.bak" -exec rm {} \;
#

# Manually explore bioinfo app content:
#   cd /appli/bioinfo
#   find . -name "tool.properties" | wc -l
#   grep -r --include "env.sh" "anaconda" | wc -l
#   grep -r --include "*.pbs" "DOCKER_IMAGE" | wc -l

# location of bioinfo app 
TOOL_DIR=/appli/bioinfo

# search for all properties files
for f in $(find ${TOOL_DIR} -name "tool.properties"); do
  # get tool absolute path
  TOOL_PATH=`dirname $f`
  echo "> Updating $TOOL_PATH"
  cp ${f} ${f}.bak
  # do we have env.sh ? 
  #  Yes: tool is either Conda or shell based.
  #   No: tool is either Docker or shell based.
  #  ... we have to check...
  ENV_FILE="${TOOL_PATH}/env.sh"
  if [ -e ${ENV_FILE}  ]; then
    grep "anaconda" ${ENV_FILE} > /dev/null 2>&1
    if [ $? == 0  ]; then
       echo "CMD_INSTALL=conda" >> ${f}
       continue
    fi
  else
    grep "DOCKER_IMAGE" ${TOOL_PATH}/*.pbs > /dev/null 2>&1
    if [ $? == 0  ]; then
       echo "CMD_INSTALL=docker" >> ${f}
       continue
    fi
  fi
  echo "CMD_INSTALL=shell" >> ${f}
done 
