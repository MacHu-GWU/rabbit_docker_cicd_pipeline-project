# -*- coding: utf-8 -*-


from attrs_mate import attr, AttrsClass


@attr.s
class AppConfig(AttrsClass):
    path = AttrsClass.ib_str()
    project_name = AttrsClass.ib_str()
    aws_profile = AttrsClass.ib_str()
    dynamodb_table_name = AttrsClass.ib_str(default="rabbit-docker-cicd-pipeline-state")
    repo_config_file = AttrsClass.ib_str(default="repo-config.json")
    tag_config_file = AttrsClass.ib_str(default="tag-config.json")
    docker_file = AttrsClass.ib_str(default="Dockerfile")


app_config = AppConfig()
