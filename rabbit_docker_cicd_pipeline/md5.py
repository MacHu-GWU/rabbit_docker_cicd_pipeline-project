# -*- coding: utf-8 -*-

import hashlib


def get_dockerfile_md5(dockerfile_path):
    """
    Get md5 check sum of a dockerfile, comments, empty line, tailing space
    are ignored.

    :param dockerfile_path: the absolute path of the Dockerfile

    :rtype: str
    """
    valid_lines = list()
    with open(dockerfile_path, "rb") as f:
        lines = f.read().decode("utf-8").split("\n")
        for line in lines:
            line = line.rstrip()
            # ignore comment line
            if line.startswith("#"):
                continue
            # ignore empty line
            if not bool(line):
                continue
            # trim tailing comment
            if "#" in line:
                line = line[:-(line[::-1].index("#") + 1)].rstrip()
                if line:
                    valid_lines.append(line)
            else:
                valid_lines.append(line)
    md5 = hashlib.md5()
    md5.update("\n".join(valid_lines).encode("utf-8"))
    return md5.hexdigest()
