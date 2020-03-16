# -*- coding: utf-8 -*-

import json
from pathlib_mate import Path
from rabbit_docker_cicd_pipeline.config import AppConfig

HERE = Path(__file__).parent

app = AppConfig(
    app_name="rabbit_docker_cicd",
    app_root_dir=Path(HERE).abspath,
    app_repos_dir=Path(HERE, "repos").abspath,
    repo_docker_hub_password=json.loads(Path(HERE, "app-config-secret.json").read_text())["repo_docker_hub_password"],
)
# print(app.app_aws_account_id)
# print(app)
app.plan()
# print(app.repos)
# print(app.tags)
tag = app.tags[0]
# print(tag)
# if not tag.is_up_to_date():
#     tag.run_docker_build()
# tag.run_docker_build()
tag.run_docker_push()


