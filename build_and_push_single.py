#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from configirl import json_load
from pathlib_mate import Path

from rabbit_docker_cicd_pipeline.config import (
    AppConfig, RepoConfig, TagConfig, Runtime, CURRENT_RUNTIME, logger,
)

HERE = Path(__file__).parent

app_config_data = json_load(Path(HERE, "app-config.json").abspath)

if CURRENT_RUNTIME == Runtime.circleci:
    app_config_data["repo_docker_hub_password"] = os.environ["DOCKER_HUB_PASS"]
elif CURRENT_RUNTIME == Runtime.aws_codebuild:
    app_config_data["repo_docker_hub_password"] = os.environ["DOCKER_HUB_PASS"]
else:
    app_config_secret_data = json_load(Path(HERE, "app-config-secret.json").abspath)
    app_config_data["repo_docker_hub_password"] = app_config_secret_data["repo_docker_hub_password"]

app = AppConfig(
    app_root_dir=Path(HERE).abspath,
    app_repos_dir=Path(HERE, "repos").abspath,
    **app_config_data,
)

if CURRENT_RUNTIME == Runtime.circleci:
    os.environ["AWS_DEFAULT_REGION"] = app.app_aws_region_dynamic
elif CURRENT_RUNTIME == Runtime.aws_codebuild:
    pass
else:
    os.environ["AWS_DEFAULT_PROFILE"] = app.app_aws_profile_dynamic
    os.environ["AWS_DEFAULT_REGION"] = app.app_aws_region_dynamic


if __name__ == "__main__":
    import sys

    # repo_dir = "repos/runtime"
    # tag_dir = "repos/runtime/python3.6.8-crawler"

    repo_dir = sys.argv[1]
    tag_dir = sys.argv[2]

    repo = RepoConfig(repo_root_dir=Path(HERE, repo_dir).abspath)
    repo.absorb(app)
    repo.fill_na_with_default()
    repo.validate()

    tag = TagConfig(tag_root_dir=Path(HERE, tag_dir).abspath)
    tag.absorb(repo)
    tag.fill_na_with_default()
    tag.validate()
    tag.run_build_and_push()
