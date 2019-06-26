#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import subprocess
import sys

import requests
from ruamel.yaml import YAML, scalarstring


class BlacklistImporter:
	def __init__(self, args):
		self.outfile = args.outfile
		self.dryrun = args.dryrun
		self.path = os.path.dirname(__file__)
		self.url = "https://raw.githubusercontent.com/JabberSPAM/blacklist/master/blacklist.txt"
		self.blacklist = ""
		self.change = False

	def request(self):
		"""
		determine if the download is required
		"""
		etag_path = "/".join([self.path, ".etag"])
		blacklist_path = "/".join([self.path, "blacklist.txt"])

		# check if etag header is present if not set local_etag to ""
		if os.path.isfile(etag_path):
			# catch special case were etag file is present and blacklist.txt is not
			if not os.path.isfile(blacklist_path):
				local_etag = ""
			else:
				# if both files are present continue normally
				with open(etag_path, "r") as local_file:
					local_etag = local_file.read()
		else:
			local_etag = ""

		with requests.Session() as s:
			# head request to check etag
			head = s.head(self.url)
			etag = head.headers['etag']

			# if etags match up or if the connection is not possible fall back to local cache
			if local_etag == etag or head.status_code != 200:
				# if local cache is present overwrite blacklist var
				if os.path.isfile(blacklist_path):
					with open(blacklist_path, "r", encoding="utf-8") as local_file:
						self.blacklist = local_file.read()

			# in any other case request a new file
			else:
				r = s.get(self.url)
				r.encoding = 'utf-8'
				local_etag = head.headers['etag']
				self.blacklist = r.content.decode()

				with open(blacklist_path, "w") as local_file:
					local_file.write(self.blacklist)

				with open(etag_path, 'w') as local_file:
					local_file.write(local_etag)

	def main(self):
		# first check if blacklist is updated
		self.request()

		# only output the selected outfile
		if self.dryrun:
			print("outfile selected: %s" % self.outfile)

		# blacklist processing
		self.process()

		# reload config if changes have been applied
		if self.change:
			subprocess.call(['/usr/sbin/ejabberdctl', 'reload_config'], shell=False)

	def process(self):
		"""
		function to build and compare the local yaml file to the remote file
		if the remote file is different, the local file gets overwritten
		"""
		# init new YAML variable
		local_file = YAML(typ="safe")

		# None catch
		if self.outfile is not None:
			# prevent FileNotFoundError on first run or file missing
			if os.path.isfile(self.outfile):
				local_file = local_file.load(open(self.outfile, "r", encoding="utf-8"))

		# blacklist frame
		remote_file = {
			"acl": {
				"spamblacklist": {
					"server": []
				}
			}
		}

		# build the blacklist with the given frame to compare to local blacklist
		for entry in self.blacklist.split():
			entry = scalarstring.DoubleQuotedScalarString(entry)
			remote_file["acl"]["spamblacklist"]["server"].append(entry)

		yml = YAML()
		yml.indent(offset=2)
		yml.default_flow_style = False

		# if dry-run true print expected content
		if self.dryrun:
			yml.dump(remote_file, sys.stdout)

		# only if the local_file and remote_file are unequal write new file
		elif local_file != remote_file:

			# prevent FileNotFoundError if self.outfile is not assigned
			if self.outfile is None:
				print("no outfile assigned", file=sys.stderr)
				print(parser.format_help(), file=sys.stderr)
				sys.exit(2)

			# proceed to update the defined outfile
			elif self.outfile is not None:
				self.change = True
				yml.dump(remote_file, open(self.outfile, "w"))

			# if that's impossible break and display help message
			else:
				print(parser.format_help(), file=sys.stderr)
				sys.exit(1)


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--outfile', help='set path to output file', dest='outfile', default=None)
	parser.add_argument('-dr', '--dry-run', help='perform a dry run', action='store_true', dest='dryrun', default=False)
	args = parser.parse_args()

	# run
	BlacklistImporter(args).main()
