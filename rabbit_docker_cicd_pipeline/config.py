# -*- coding: utf-8 -*-

"""

**中文文档**

Config 初始化的过程:

1. 首先从 __init__(attr=value) 中读取数值, 通常是文件夹路径一类的值, 这些值要用于
    决定 config 文件的位置, 所以要先行读取.
2. 然后从当前文件夹中对应的 config 文件中读取数值.
3. 将 父 节点 (Repo 的父节点是 App, Tag 的父节点是 Repo) 中的 config 使用 absorb()
    方法填充自身还没有被复制的 field
4. 使用 fill_na_with_default() 方法填充自身还没有被复制的 field
"""

import os
import sys
import time
import typing
from datetime import datetime

import boto3
import docker
from attrs_mate import attr, LazyClass
from configirl import json_load
from constant2 import Constant
from invoke import run
from pathlib_mate import Path
from troposphere_mate import Sentinel, REQUIRED

from . import exc
from .logger import logger
from .md5 import get_dockerfile_md5
from .runtime import Runtime, CURRENT_RUNTIME
from .state import BaseTagStateModel


@attr.s
class BaseConfig(LazyClass):
    """
    **中文文档**

    一个特殊的用于指定配置的数据类型. 该基础类用于指定 Lambda Function, API Gateway Method
    等配置.

    - 所有必要的属性都给予 ``REQUIRED`` 默认值
    - 所有可选的属性都给予 ``NOTHING`` 默认值
    - ``_default`` 中只定义那些 一定会有用到, 但是值不一定的值
    """
    _default = dict()  # type: dict

    def absorb(self, other):
        """
        inherit values from other config if the current one is a Sentinel.
        :type other: FunctionConfig

        **中文文档**

        从另一个 实例 当中吸取那些被数值化的数据.
        """
        this_data = attr.asdict(self)
        other_data = attr.asdict(other)
        for key, value in this_data.items():
            if isinstance(value, Sentinel):
                if key in other_data:
                    setattr(self, key, other_data[key])

    def fill_na_with_default(self):
        """
        Fill default value into current instance, if the field already has
        a value, then skip that field.

        **中文文档**
        针对于可选属性, 如果用户未指定初始值, 则使用 ``_default`` 变量中的值.
        """
        for key, value in self._default.items():
            if isinstance(getattr(self, key), Sentinel):
                setattr(self, key, value)


@attr.s
class AbstractAppConfig(BaseConfig):
    # app level config
    app_name = attr.ib(default=REQUIRED)
    app_root_dir = attr.ib(default=REQUIRED)
    app_config_file = attr.ib(default="app-config.json")

    app_repos_dir = attr.ib(default=REQUIRED)
    app_aws_profile = attr.ib(default=REQUIRED)
    app_aws_region = attr.ib(default=REQUIRED)
    app_dynamodb_table = attr.ib(default=REQUIRED)

    # repo level config
    repo_name = attr.ib(default=REQUIRED)
    repo_root_dir = attr.ib(default=REQUIRED)
    repo_config_file = attr.ib(default="repo-config.json")
    repo_registry = attr.ib(default=REQUIRED)
    repo_docker_hub_username = attr.ib(default=REQUIRED)
    repo_docker_hub_password = attr.ib(default=REQUIRED)

    repo_aws_ecr_life_cycle_expire_days = attr.ib(default=365)  # type: int

    repo_ci_service = attr.ib(default=REQUIRED)
    repo_circleci_orch_mode = attr.ib(default=REQUIRED)
    repo_circleci_context_name = attr.ib(default=REQUIRED)
    repo_aws_codebuild_orch_mode = attr.ib(default=REQUIRED)

    # tag level config
    tag_name = attr.ib(default=REQUIRED)
    tag_root_dir = attr.ib(default=REQUIRED)
    tag_config_file = attr.ib(default="tag-config.json")
    tag_docker_file = attr.ib(default="Dockerfile")
    tag_smoke_test_file = attr.ib(default="smoke-test.sh")
    tag_force_update_interval_in_seconds = attr.ib(default=REQUIRED)  # type: int

    class Options(Constant):
        class RepoRegistry(Constant):
            docker_hub = "docker_hub"
            aws_ecr = "aws_ecr"

        class RepoCIService(Constant):
            circleci = "circleci"
            aws_codebuild = "aws_codebuild"

        class RepoCircleCIOrchMode(Constant):
            single = "single"
            parallel = "parallel"

        class RepoAWSCodeBuildOrchMode(Constant):
            single = "single"
            parallel = "parallel"

    @LazyClass.lazyproperty
    def uuid(self):
        return self.app_name

    @property
    def app_aws_profile_dynamic(self):
        if CURRENT_RUNTIME == Runtime.circleci:
            return None
        elif CURRENT_RUNTIME == Runtime.aws_codebuild:
            return None
        else:
            return self.app_aws_profile

    @property
    def app_aws_region_dynamic(self):
        if CURRENT_RUNTIME == Runtime.circleci:
            return self.app_aws_region
        elif CURRENT_RUNTIME == Runtime.aws_codebuild:
            return None
        else:
            return self.app_aws_region

    @LazyClass.lazyproperty
    def app_boto_ses(self):
        """
        :rtype: boto3.session.Session
        """
        return boto3.session.Session(
            profile_name=self.app_aws_profile_dynamic,
            region_name=self.app_aws_region_dynamic,
        )

    @LazyClass.lazyproperty
    def app_aws_account_id(self):
        return self.app_boto_ses.client("sts").get_caller_identity()["Account"]

    @LazyClass.lazyproperty
    def app_aws_iam_user_arn(self):
        return self.app_boto_ses.client("sts").get_caller_identity()["Arn"]

    @LazyClass.lazyproperty
    def app_docker_client(self) -> docker.DockerClient:
        """

        :rtype: docker.DockerClient
        """
        return docker.from_env()

    @property
    def repo_dirname(self):
        return Path(self.repo_root_dir).basename

    @property
    def repo_local_identifier(self):
        return self.repo_name

    @property
    def repo_remote_identifier(self):
        if self.repo_registry == self.Options.RepoRegistry.docker_hub:
            return f"{self.repo_docker_hub_username}/{self.repo_name}"
        elif self.repo_registry == self.Options.RepoRegistry.aws_ecr:
            return f"{self.app_aws_account_id}.dkr.ecr.{self.app_aws_region_dynamic}.amazonaws.com/{self.repo_name}"
        else:
            raise ValueError

    @property
    def tag_dirname(self):
        return Path(self.tag_root_dir).basename

    @property
    def tag_local_identifier(self):
        return f"{self.repo_local_identifier}:{self.tag_name}"

    @property
    def tag_remote_identifier(self):
        return f"{self.repo_remote_identifier}:{self.tag_name}"

    _TagStateModel = None  # type: BaseTagStateModel

    @property
    def TagStateModel(self):
        """
        :rtype: BaseTagStateModel
        """
        if self._TagStateModel is None:
            if CURRENT_RUNTIME == Runtime.circleci:
                os.environ["AWS_DEFAULT_REGION"] = self.app_aws_region_dynamic
            elif CURRENT_RUNTIME == Runtime.aws_codebuild:
                pass
            else:
                os.environ["AWS_DEFAULT_PROFILE"] = self.app_aws_profile_dynamic
                os.environ["AWS_DEFAULT_REGION"] = self.app_aws_region_dynamic

            class TagStateModel(BaseTagStateModel):
                class Meta:
                    region = self.app_aws_region_dynamic
                    table_name = self.app_dynamodb_table

            self._TagStateModel = TagStateModel

            if not TagStateModel.exists():
                print(
                    f"Dynamodb table arn:aws:dynamodb:{self.app_aws_region_dynamic}:{self.app_aws_account_id}:table/{TagStateModel.Meta.table_name} not exists! Creating it, please wait for 30 seconds ...")
                TagStateModel.create_table(billing_mode="PAY_PER_REQUEST")
                time.sleep(30)

        return self._TagStateModel


@attr.s
class AppConfig(AbstractAppConfig):
    repos = attr.ib(default=REQUIRED)  # type: typing.List[RepoConfig]
    tags = attr.ib(default=REQUIRED)  # type: typing.List[TagConfig]

    _default = dict(
        app_dynamodb_table="rabbit-docker-cicd-pipeline-image-state",
    )

    @property
    def app_config_abspath(self):
        return Path(self.app_root_dir, self.app_config_file)

    def __attrs_post_init__(self):
        if not self.app_config_abspath.exists():
            raise exc.NotValidAppDirError(f"{self.app_config_abspath} doesn't exists!")

        try:
            for attr, value in json_load(self.app_config_abspath.abspath).items():
                setattr(self, attr, value)
        except Exception as e:
            raise exc.NotValidAppDirError(str(e))

        self.fill_na_with_default()

    def plan(self):
        logger.show_in_cyan("Inspect docker build execution plan ...")
        self.repos = list()  # type: typing.List[RepoConfig]
        self.tags = list()  # type: typing.List[TagConfig]
        for repo_dir in Path.sort_by_abspath(Path(self.app_repos_dir).select_dir(recursive=False)):
            try:
                repo = RepoConfig(repo_root_dir=repo_dir.abspath)
                repo.absorb(self)
                repo.fill_na_with_default()
                repo.validate()
                self.repos.append(repo)
                for tag_dir in Path.sort_by_abspath(repo_dir.select_dir(recursive=False)):
                    try:
                        tag = TagConfig(tag_root_dir=tag_dir.abspath)
                        tag.absorb(repo)
                        tag.fill_na_with_default()
                        tag.validate()
                        if not tag.is_up_to_date():
                            self.tags.append(tag)
                    except Exception as e:
                        # print(e)
                        pass
            except Exception as e:
                # print(e)
                pass

        if len(self.repos):
            logger.show_in_cyan("Detected these docker image REPOSITORIES:")
            for repo in self.repos:
                logger.show_in_cyan("- " + repo.repo_remote_identifier, indent=1)
        else:
            logger.show_in_cyan("No docker image REPOSITORIES detected.", indent=1)

        if len(self.tags):
            logger.show_in_cyan("Detected these docker image TAGS to update:")
            for tag in self.tags:
                logger.show_in_cyan("- " + tag.tag_remote_identifier, indent=1)
        else:
            logger.show_in_cyan("No need to build any docker image TAGS.", indent=1)

    def build_all(self):
        pass

    def cft_template(self):
        pass


@attr.s
class RepoConfig(AbstractAppConfig):
    _default = dict(

    )

    @property
    def repo_config_abspath(self):
        return Path(self.repo_root_dir, self.repo_config_file)

    def __attrs_post_init__(self):
        if not self.repo_config_abspath.exists():
            raise exc.NotValidRepoDirError(f"{self.repo_config_abspath} doesn't exists!")

        try:
            for attr, value in json_load(self.repo_config_abspath.abspath).items():
                setattr(self, attr, value)
        except Exception as e:
            raise exc.NotValidRepoDirError(str(e))

    def validate_repo_registry(self):
        if self.repo_registry not in self.Options.RepoRegistry.Values():
            raise exc.NotValidValueError(
                exc.NotValidValueError.tpl_not_from_choices.format(
                    invalid_value=self.repo_registry,
                    attribute_name="repo_registry",
                    valid_values=self.Options.RepoRegistry.Values(),
                )
            )

    def validate_repo_docker_hub_username(self):
        if self.repo_registry == self.Options.RepoRegistry.docker_hub:
            if not isinstance(self.repo_docker_hub_username, str):
                raise exc.NotValidValueError(
                    exc.NotValidValueError.tpl_not_valid_type.format(
                        invalid_type=type(self.repo_docker_hub_username),
                        attribute_name="repo_docker_hub_username",
                        valid_type=str,
                    )
                )

    def validate_repo_aws_ecr_life_cycle_expire_days(self):
        if self.repo_registry == self.Options.RepoRegistry.aws_ecr:
            # if self.aws_ecr_life_cycle_expire_days no:
            pass

    def validate_repo_circleci_orch_mode(self):
        if self.repo_circleci_orch_mode not in self.Options.RepoCircleCIOrchMode.Values():
            raise exc.NotValidValueError(
                exc.NotValidValueError.tpl_not_from_choices.format(
                    invalid_value=self.repo_circleci_orch_mode,
                    attribute_name="repo_circleci_orch_mode",
                    valid_values=self.Options.RepoCircleCIOrchMode.Values(),
                )
            )

    def validate_repo_aws_codebuild_orch_mode(self):
        if self.repo_aws_codebuild_orch_mode not in self.Options.RepoAWSCodeBuildOrchMode.Values():
            raise exc.NotValidValueError(
                exc.NotValidValueError.tpl_not_from_choices.format(
                    invalid_value=self.repo_aws_codebuild_orch_mode,
                    attribute_name="repo_aws_codebuild_orch_mode",
                    valid_values=self.Options.RepoAWSCodeBuildOrchMode.Values(),
                )
            )

    def validate(self):
        self.validate_repo_registry()
        self.validate_repo_docker_hub_username()
        self.validate_repo_aws_ecr_life_cycle_expire_days()
        self.validate_repo_circleci_orch_mode()
        self.validate_repo_aws_codebuild_orch_mode()


@attr.s
class TagConfig(AbstractAppConfig):
    _default = dict(

    )

    def __attrs_post_init__(self):
        if not self.tag_config_abspath.exists():
            raise exc.NotValidTagDirError(f"{self.tag_config_abspath} doesn't exists!")

        try:
            for attr, value in json_load(self.tag_config_abspath.abspath).items():
                setattr(self, attr, value)
        except Exception as e:
            raise exc.NotValidRepoDirError(str(e))

    @property
    def tag_config_abspath(self):
        return Path(self.tag_root_dir, self.tag_config_file)

    @property
    def tag_docker_file_abspath(self):
        return Path(self.tag_root_dir, self.tag_docker_file)

    @property
    def tag_smoke_test_file_abspath(self):
        return Path(self.tag_root_dir, self.tag_smoke_test_file)

    @property
    def tag_fingerprint(self):
        return get_dockerfile_md5(self.tag_docker_file_abspath.abspath)

    def validate_docker_file(self):
        if not self.tag_docker_file_abspath.exists():
            raise exc.NotValidTagDirError(f"{self.tag_docker_file_abspath} doesn't exists!")

    def validate(self):
        self.validate_docker_file()

    def is_up_to_date(self):
        try:
            tag_state = self.TagStateModel.get(self.tag_remote_identifier)
            if tag_state.fingerprint == self.tag_fingerprint:
                if tag_state.seconds_from_last_update <= self.tag_force_update_interval_in_seconds:
                    return True
                else:
                    logger.show_in_cyan(
                        f"elapsed time from last update longer than {self.tag_force_update_interval_in_seconds} seconds.")
                    return False
            else:
                logger.show_in_cyan(f"fingerprint of the image changed.")
                return False
        except self.TagStateModel.DoesNotExist:
            logger.show_in_cyan(f"fingerprint info not found in dynamodb.")
            return False

    # --- High level operation API ---
    def run_docker_build(self):
        """
        Run `docker build` command.

        Raise except as soon as possible.
        """
        logger.show_in_cyan(f"Build `{self.tag_local_identifier}` at {self.tag_root_dir} ...")
        try:
            # use invoke
            cmd = f"docker build -t {self.tag_local_identifier} {self.tag_root_dir}"
            run(cmd)

            # use docker client
            # docker_client = self.app_docker_client  # type: docker.DockerClient
            # docker_client.images.build(path=self.tag_root_dir, tag=self.tag_local_identifier, quiet=False)

            logger.show_in_green("Success!", indent=1)
        except Exception as e:
            logger.show_in_red(f"Failed! Error: {e}", indent=1)
            raise e

    def run_smoke_test(self):
        """
        Run `bash smoke-test.sh`` shell script.

        Raise except as soon as possible.
        """
        logger.show_in_cyan(f"run smoke test script `{self.tag_smoke_test_file_abspath}` ...")
        try:
            cmd = f"bash {self.tag_smoke_test_file_abspath}"
            run(cmd)
            logger.show_in_green("Success!", indent=1)
        except Exception as e:
            logger.show_in_red(f"Failed! Error: {e}", indent=1)
            raise e

    def run_docker_push(self):
        """
        Run `docker tag`, `docker login` and `docker push` command.

        Raise except as soon as possible.
        """
        if self.repo_registry == self.Options.RepoRegistry.docker_hub:
            # tag
            logger.show_in_cyan(f"Tag `{self.tag_local_identifier}` to `{self.tag_remote_identifier}` ...")
            docker_client = self.app_docker_client  # type: docker.DockerClient
            try:
                image = docker_client.images.get(name=self.tag_local_identifier)  # type: docker.i
                image.tag(repository=self.repo_remote_identifier, tag=self.tag_name)
                logger.show_in_green("Success!", indent=1)
            except Exception as e:
                logger.show_in_red(f"Failed! Error: {e}", indent=1)
                raise e

            # login
            logger.show_in_cyan(f"login to docker hub, username = `{self.repo_docker_hub_username}` ...")
            try:
                docker_client.login(
                    username=self.repo_docker_hub_username,
                    password=self.repo_docker_hub_password,
                )
                logger.show_in_green("Success!", indent=1)
            except Exception as e:
                logger.show_in_red(f"Failed! Error: {e}", indent=1)
                raise e

            # docker push
            logger.show_in_cyan(f"Push `{self.tag_remote_identifier}` to {self.repo_registry} ...")
            try:
                docker_client.images.push(repository=self.repo_remote_identifier, tag=self.tag_name)
                logger.show_in_green("Success!", indent=1)
            except Exception as e:
                logger.show_in_red(f"Failed! Error: {e}", indent=1)
                raise e

            # update dynamodb state
            logger.show_in_cyan("update dynamodb state ...")
            now = datetime.utcnow()
            try:
                tag_state = self.TagStateModel.get(self.tag_remote_identifier)
                tag_state.update(
                    actions=[
                        self.TagStateModel.fingerprint.set(self.tag_fingerprint),
                        self.TagStateModel.last_update.set(str(now))
                    ]
                )
                logger.show_in_green("Success!", indent=1)
            except self.TagStateModel.DoesNotExist:
                tag_state = self.TagStateModel(
                    identifier=self.tag_remote_identifier,
                    fingerprint=self.tag_fingerprint,
                    last_update=str(now),
                )
                tag_state.save()
                logger.show_in_green("Success!", indent=1)
            except Exception as e:
                logger.show_in_red("Failed!", indent=1)
                raise e

    def run_build_test_and_push(self):
        if self.is_up_to_date():
            logger.show_in_cyan(f"{self.tag_remote_identifier} is up to date.")
            return

        logger.show_in_cyan(f"{self.tag_remote_identifier} is NOT up to date.")
        self.run_docker_build()
        self.run_smoke_test()
        self.run_docker_push()

