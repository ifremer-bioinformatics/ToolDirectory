#!/usr/bin/env python3

import os
import re
import random

def parseProperties(directory, ignore):

	# Regexes to detect each category
	regexes = {
	'name':          'NAME=',
	'description':   'DESCRIPTION=',
	'version':       'VERSION=',
	'cmdline':       'CMDLINE=',
	'galaxy':        'GALAXY=',
	'documentation': 'URLDOC=',
	'edam':          'KEYWORDS=',
	'environment':   'CMD_INSTALL='
	}

	# Main dict with the result for each tool
	properties = {}

	# First, list level 1 dirs in order to not explore galaxy/ folder
	for dir in os.listdir(directory):
		# Ignore galaxy/
		if not dir in ignore:
			# Second, list all files in all subdirectories
			# WARNING: beware of "latest" symlinks. os.walk() do not explore symlink folders by default so it's ok
			for root, dirs, files in os.walk(os.path.join(directory,dir)):
				for file in files:
					if file == "tool.properties":

						# In case of error, get the full path to the file
						print(os.path.join(root, file))

						# Open the tool.properties
						tool_infos = open(os.path.join(root, file), 'r')
						# Create a tmp dict
						parsed_data = {}
						parsed_data['path'] = root

						for l in tool_infos:
							# Use regex to ensure the correct recovery of each category
							# In case of wrong category order
							for k, v in regexes.items():
								if v in l:
									regex, value = re.split(r'=', l.rstrip('\n'))
									parsed_data[k] = value

						# Create a uniq tool ID
						toolID = parsed_data['name'] +'-'+ parsed_data['version']
						# Transfert into the main dict
						properties[toolID] = parsed_data

	# Return the dict for printing
	return(properties)

def outputWriting(dictData):

	txt = open('tool.properties.csv', 'w')
	txt.write('Name,EDAM,Environment,Topic,Access,Doc,Description,Path\n')

	# Iterate over each tool - sorted by name
	for tool in sorted(dictData.keys(), key=lambda x:x.lower()):
		# Get properties
		p = dictData[tool]

		# Accesses
		if p['cmdline'] == 'true' and p['galaxy'] == 'true':
			p['access'] = 'Galaxy and cmdline'
		elif p['cmdline'] == 'true' and p['galaxy'] == 'false':
			p['access'] = 'Cmdline only'
		else:
			p['access'] = 'Galaxy only'

		# Thematic
		p['topic'] = random.choice(['Epigenetics','Multi-thematic','Genomics','Metabarcoding','Metagenomics','Transcriptomics','Other'])

		# Write, ordered
		name = p['name'] + ' - ' + p['version']
		txt.write('"{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}"\n'.format(name,p['edam'],p['environment'],p['topic'],p['access'],p['documentation'],p['description'],p['path']))

	# Close file
	txt.close()

def main():

	# 0 - Directories
	bioinfoDir = '/appli/bioinfo'
	# bioinfoDir = '/home/datawork-bioinfo-ss/projects/edam/tmp'
	ignoreDirs = {'galaxy': None, 'w4m': None}

	# 1 - parse all tool.properties
	parsedProperties = parseProperties(bioinfoDir, ignoreDirs)

	# 2 - write csv file
	outputWriting(parsedProperties)

if __name__ == '__main__':
	main()
