# -*- coding: utf-8 -*-
import sys

from ruamel.yaml import YAML, scalarstring

from .misc import local_file_present


class ProcessBlocklist:
    def __init__(self):
        pass

    @classmethod
    def process(self, blacklist, outfile, dryrun: bool):
        """
        function to build and compare the local yaml file to the remote file
        if the remote file is different, the local file gets overwritten
        """
        # cheeky none catch
        try:
            # load local blacklist outfile
            if local_file_present(outfile):
                with open(outfile, "r", encoding="utf-8") as local_file:
                    local_blacklist = local_file.read()

        except TypeError:
            # no local copy use empty one instead
            local_blacklist = YAML(typ="safe")

        # blacklist frame
        remote_file = {"acl": {"spamblacklist": {"server": []}}}

        # build the blacklist with the given frame to compare to local blacklist
        for entry in blacklist.split():
            entry = scalarstring.DoubleQuotedScalarString(entry)
            remote_file["acl"]["spamblacklist"]["server"].append(entry)

        yml = YAML()
        yml.indent(offset=2)
        yml.default_flow_style = False

        # if dry-run true print expected content
        if dryrun:
            yml.dump(remote_file, sys.stdout)
            return

        if local_blacklist == remote_file:
            return

        if outfile is None:
            print("no outfile assigned", file=sys.stderr)
            sys.exit(2)

        # proceed to update the defined outfile
        with open(outfile, "w", encoding="utf-8") as new_local_file:
            yml.dump(remote_file, new_local_file)
