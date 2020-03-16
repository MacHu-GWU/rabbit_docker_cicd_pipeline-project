# -*- coding: utf-8 -*-

import os


class Runtime:
    circleci = "circleci"
    aws_codebuild = "aws_codebuild"
    local = "local"


def is_circleci_runtime():
    return "CIRCLECI" in os.environ


def is_aws_codebuild_runtime():
    return "CODEBUILD_BUILD_ID" in os.environ


def detect_runtime():
    if is_circleci_runtime():
        return Runtime.circleci
    elif is_aws_codebuild_runtime():
        return Runtime.aws_codebuild
    else:
        return Runtime.local


CURRENT_RUNTIME = detect_runtime()
