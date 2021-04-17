#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import requests
from appdirs import user_cache_dir

from .bl_process import ProcessBlocklist
from .misc import local_file_present


class Blimp:
    def __init__(self, args):
        self.outfile = args.outfile
        self.dryrun = args.dry_run
        self.path = Path(user_cache_dir("blimp"))
        self.url = "https://raw.githubusercontent.com/JabberSPAM/blacklist/master/blacklist.txt"
        self.blacklist = ""

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

        with open(self.etag_path, "r") as local_file:
            local_etag = local_file.read()

        # etag file is present but outdated
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
        ProcessBlocklist.process(self.blacklist, self.outfile, self.dryrun)


if __name__ == "__main__":
    from .cli import cli
    cli()
