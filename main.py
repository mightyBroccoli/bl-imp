#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# workflow
# start options main.py --dry-run --outfile file

import requests
import os
import sys
import argparse
from ruamel.yaml import YAML, scalarstring


class BlacklistImporter:
	def __init__(self, args):
		self.outfile = args.outfile
		self.dryrun = args.dryrun
		self.url = "https://raw.githubusercontent.com/JabberSPAM/blacklist/master/blacklist.txt"
		self.blacklist = None
		self.change = False

	def request(self):
		# check if etag header is present if not set local_etag to ""
		if os.path.isfile(".etag"):
			with open(".etag", "r") as file:
				local_etag = file.read()
		else:
			local_etag = ""

		with requests.Session() as s:
			# head request to check etag
			head = s.head(self.url)
			etag = head.headers['etag']

			# if etags match up or if a connection is not possible fall back to local cache
			if local_etag == etag or head.status_code != 200:
				# check if local cache is present
				if os.path.isfile("blacklist.txt"):
					with open("blacklist.txt", "r", encoding="utf-8") as file:
						self.blacklist = file.read()

			# in any other case request a new file
			else:
				r = s.get(self.url)
				r.encoding = 'utf-8'
				local_etag = head.headers['etag']
				self.blacklist = r.content.decode()

				with open("blacklist.txt", "w") as file:
					file.write(self.blacklist)

				with open('.etag', 'w') as string:
					string.write(local_etag)

	def main(self):
		# first check if blacklist is updated
		self.request()

		if self.dryrun:
			# only output the selected software and outfile
			print("outfile selected: %s" % self.outfile)

		# select ejabberd processing
		self.process()

		# reload config if changes have been applied
		if self.change:
			os.system("ejabberdctl reload_config")

	def process(self):
		# init new YAML variable
		local_file = YAML(typ="safe")
		try:
			local_file = local_file.load(open(self.outfile, "r", encoding="utf-8"))
		except FileNotFoundError:
			pass

		remote_file = {
			"acl": {
				"spamblacklist": {
					"server": []
				}
			}
		}

		for entry in self.blacklist.split():
			entry = scalarstring.DoubleQuotedScalarString(entry)
			remote_file["acl"]["spamblacklist"]["server"].append(entry)

		yml = YAML()
		yml.indent(offset=2)
		yml.default_flow_style = False

		if self.dryrun:
			# if dryrun true print expected content
			yml.dump(remote_file, sys.stdout)

		elif local_file != remote_file:
			self.change = True
			# only if the local_file and remote_file are unequal write new file
			yml.dump(remote_file, open(self.outfile, "w"))


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--outfile', help='set path to output file', dest='outfile', default=None)
	parser.add_argument('-dr', '--dry-run', help='perform a dry run', action='store_true', dest='dryrun', default=False)
	args = parser.parse_args()

	# run
	BlacklistImporter(args).main()
