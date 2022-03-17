#!/usr/bin/env bash

# =============================================================================
# Tool Directory 
#
# A program to prepare an HTML table listing softwares available on
# a file system.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# (c) 2017-20 Ifremer-Bioinformatics Team
# =============================================================================

# Utility script to create and maintain up to date catalogue of
# 'tool.properties' files.

# Repository of softwares. Within that repository we must have two levels
# of sub-directories: <tool-name>/<tool-version>. In turn, <tool-version>
# is expected to contain a 'tool.properties'. See '../test/catalogue' for
# a example.
SOURCE_DIR="/path/to/bioinfo/software"

# Target to sync content of above directory
TARGET_DIR="../test/catalogue"

# Instead of a unique huge rsync, we run it one tool at a time
for tooldir in $(find $SOURCE_DIR -maxdepth 1 -mindepth 1 -type d | sort):
do
  echo "Collect tool.properties from: $tooldir"
  rsync -a --prune-empty-dirs --include '*/' --include 'properties.json' --exclude '*' $tooldir $TARGET_DIR
done

