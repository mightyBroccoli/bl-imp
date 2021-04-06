# -*- coding: utf-8 -*-
from pathlib import Path


def local_file_present(somepath) -> bool:
    """
    check if a given local filepath exists
    :return: true if present
    """
    if not Path(somepath).is_file():
        return False

    return True
