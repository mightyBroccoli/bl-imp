#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

import requests
from appdirs import *

from .bl_process import ProcessBlocklist
from .misc import *


class BlacklistImporter:
    def __init__(self, args):
        self.outfile = args.outfile
        self.dryrun = args.dry_run
        self.path = Path(user_cache_dir("blimp"))
        self.url = "https://raw.githubusercontent.com/JabberSPAM/blacklist/master/blacklist.txt"
        self.blacklist = ""
        self.apply_changes = False

        self.etag_path = self.path.joinpath(".etag")
        self.blacklist_path = self.path.joinpath("blacklist.txt")

    def cache_dir_check(self):
        if not self.path.is_dir():
            Path(self.path).mkdir(parents=True, exist_ok=True)

    def download_required(self, etag) -> bool:
        """
        method to determine if a new download should be initiated
        :param etag: requests etag object
        :return: true if download is required
        """
        # always trigger download if any local cache file is missing
        if not local_file_present(self.blacklist_path):
            return True

        if not local_file_present(self.etag_path):
            return True

        # etag file is present but outdated
        else:
            with open(self.etag_path, "r") as local_file:
                local_etag = local_file.read()

            if local_etag != etag:
                return True

        return False

    def start_request(self):
        """
        determine if the download is required
        """
        with requests.Session() as s:
            # head request to check etag
            head = s.head(self.url)
            etag = head.headers["etag"]

            if head.status_code != requests.codes.ok:
                return

            if not self.download_required(etag):
                with open(self.blacklist_path, "r", encoding="utf-8") as local_file:
                    self.blacklist = local_file.read()

            else:
                r = s.get(self.url)
                r.encoding = "utf-8"
                local_etag = head.headers["etag"]
                self.blacklist = r.content.decode()

                with open(self.blacklist_path, "w", encoding="utf-8") as local_file:
                    local_file.write(self.blacklist)

                with open(self.etag_path, "w", encoding="utf-8") as local_file:
                    local_file.write(local_etag)

    def main(self):
        # check the cache dir first
        self.cache_dir_check()

        # only output the selected outfile
        if self.dryrun:
            print("outfile selected: %s" % self.outfile)

        # go
        self.start_request()

        # blacklist processing
        ProcessBlocklist().process(self.blacklist, self.outfile, self.dryrun)

        """# reload config if changes have been applied
        if self.change:
            # catch ejabberdctl missing
            if Path("/usr/sbin/ejabberdctl").is_file():
                subprocess.call(["/usr/sbin/ejabberdctl", "reload_config"], shell=False)

            # report missing ejabberdctl reload_config
            else:
                print("/usr/sbin/ejabberdctl was not found", file=sys.stderr)
                print("blacklist changes have been applied\nejabberd config was not reloaded", file=sys.stderr)
                sys.exit(1)
"""


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-out", "--outfile", help="set path to output file", action="store", default=None)
    parser.add_argument("-dr", "--dry-run", help="perform a dry run", action="store_true", default=False)
    args = parser.parse_args()

    # run
    BlacklistImporter(args).main()
