# -*- coding: utf-8 -*-

from attrs_mate import attr, AttrsClass
from configirl import json_load
from pathlib_mate import Path

from .app_config import app_config
from .exc import NotValidRepoDirError, NotValidTagDirError


@attr.s
class RepoConfig(AttrsClass):
    repo_name = AttrsClass.ib_str()

    registry = AttrsClass.ib_str()

    docker_hub_username = AttrsClass.ib_str(default=None)

    aws_ecr_life_cycle_expire_days = AttrsClass.ib_int(default=365)

    class RegistryOptions:
        docker_hub = "docker_hub"
        aws_ecr = "aws_ecr"

    _valid_registry_options = [
        RegistryOptions.docker_hub,
        RegistryOptions.aws_ecr,
    ]

    @registry.validator
    def check_registry(self, attr, value):
        if value not in self._valid_registry_options:
            raise ValueError(f"'{value}' is a invalid registry! Has to be one of {self._valid_registry_options}")

    @property
    def aws_ecr_life_cycle_policy(self):
        return {
            "rules": [
                {
                    "rulePriority": 1,
                    "description": "Expire images older than {} days".format(self.aws_ecr_life_cycle_expire_days),
                    "selection": {
                        "tagStatus": "untagged",
                        "countType": "sinceImagePushed",
                        "countUnit": "days",
                        "countNumber": self.aws_ecr_life_cycle_expire_days
                    },
                    "action": {
                        "type": "expire"
                    }
                }
            ]
        }

    def __attrs_post_init__(self):
        if self.registry == self.RegistryOptions.docker_hub:
            if not isinstance(self.docker_hub_username, str):
                raise ValueError("docker_hub_username config is invalid!")

    @classmethod
    def from_json(cls, path):
        """
        :rtype: RepoConfig
        """
        if not Path(path).exists():
            raise EnvironmentError(f"{path} doesn't exists!")
        return cls(**json_load(path))


@attr.s
class Repo(AttrsClass):
    path = AttrsClass.ib_str()
    config = attr.ib(default=None)

    def __attrs_post_init__(self):
        try:
            self.config = RepoConfig.from_json(
                Path(self.path, app_config.repo_config_file).abspath)
        except Exception as e:
            raise NotValidRepoDirError(
                NotValidRepoDirError.tpl_config_error.format(
                    self.path,
                    app_config.repo_config_file,
                    str(e),
                )
            )


@attr.s
class TagConfig(AttrsClass):
    tag_name = AttrsClass.ib_str()

    @classmethod
    def from_json(cls, path):
        """
        :rtype: TagConfig
        """
        if not Path(path).exists():
            raise EnvironmentError(f"{path} doesn't exists!")
        return cls(**json_load(path))


@attr.s
class Tag(AttrsClass):
    path = AttrsClass.ib_str()
    repo = Repo.ib_nested()
    config = attr.ib(default=None)

    def __attrs_post_init__(self):
        try:
            self.config = TagConfig.from_json(
                Path(self.path, app_config.tag_config_file))
        except Exception as e:
            raise NotValidTagDirError(
                NotValidTagDirError.tpl_config_error.format(
                    self.path,
                    app_config.tag_config_file,
                    str(e),
                )
            )

        if not Path(self.path, app_config.docker_file).exists():
            raise NotValidTagDirError(
                "{} not found in {}".format(
                    app_config.docker_file,
                    self.path,
                )
            )
