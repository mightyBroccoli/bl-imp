#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# workflow
# start options main.py --ejabberd/prosody --dry-run --outfile file

import requests
import sys
import os
import argparse
import yaml


class BlacklistImporter:
	def __init__(self, args):
		self.server = args.software
		self.outfile = args.outfile
		self.dryrun = args.dryrun
		self.url = "https://raw.githubusercontent.com/JabberSPAM/blacklist/master/blacklist.txt"
		self.blacklist = None

	def request(self):
		# check if etag header is present if not set local_etag to ""
		if os.path.isfile(".etag"):
			with open(".etag") as file:
				local_etag = file.read()
		else:
			local_etag = ""

		with requests.Session() as s:
			# head request to check etag
			head = s.head(self.url)
			etag = head.headers['etag']

			# compare etag with local_etag if they match up no request is made
			if local_etag == etag:
				with open("blacklist.txt", "r") as file:
					self.blacklist = file.readline()

			# if the connection is not possible use cached xml if present
			elif os.path.isfile("blacklist.txt") and head.status_code != 200:
				with open("blacklist.txt", "r") as file:
					self.blacklist = file.readline()

			# in any other case request a new file
			else:
				r = s.get(self.url)
				r.encoding = 'utf-8'
				local_etag = head.headers['etag']

				with open("blacklist.txt", "w") as file:
					file.write(r.content.decode())

				with open('.etag', 'w') as string:
					string.write(local_etag)

	def main(self):
		# first check if blacklist is updated
		self.request()

		if self.dryrun:
			# only output the selected software and outfile
			print("server software selected: %s" % self.server)
			print("outfile selected: %s" % self.outfile)

		if self.server == "ejabberd":
			# select ejabberd processing
			self.ejabberd()

		elif self.server == "prosody":
			# select prosody processing
			self.prosody()
		else:
			# in any other case exit
			sys.exit(3)

	def ejabberd(self):
		# check if file was altered
		local_file = yaml.load(open(self.outfile, "r"))

		remote_file = {
			"acl": {
				"spamblacklist": {
					"server": []
				}
			}
		}

		for entry in self.blacklist.split():
			remote_file["acl"]["spamblacklist"]["server"].append(entry)

		if self.dryrun:
			print(yaml.dump(remote_file))

		elif local_file != remote_file:
			yaml.dump(remote_file, open(self.outfile, "w"))

	def prosody(self):
		pass


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-e', '--ejabberd', help='set server software to ejabberd', action='store_const', dest='software',
						const="ejabberd", default=None)
	parser.add_argument('-p', '--prosody', help='set server software to prosody', action='store_const', dest='software',
						const="prosody", default=None)
	parser.add_argument('-o', '--outfile', help='set path to output file', dest='outfile', default=None)
	parser.add_argument('--dry-run', help='perform only a dry run', action='store_true', dest='dryrun', default=False)
	args = parser.parse_args()

	BlacklistImporter(args).main()
