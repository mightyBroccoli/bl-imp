#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path


def local_file_present(somepath) -> bool:
    """
    check local etag copy
    :return: true if present
    """
    if not Path(somepath).is_file():
        return False

    return True

def asd():
    print("yo")
