#!/usr/bin/env bash

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
  rsync -a --prune-empty-dirs --include '*/' --include 'tool.properties' --exclude '*' $tooldir $TARGET_DIR
done

