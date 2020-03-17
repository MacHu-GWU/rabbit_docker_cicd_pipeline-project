# -*- coding: utf-8 -*-

import os
from configirl import json_load
from pathlib_mate import Path

from rabbit_docker_cicd_pipeline.config import (
    AppConfig, Runtime, CURRENT_RUNTIME,
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