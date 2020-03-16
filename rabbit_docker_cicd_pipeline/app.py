# -*- coding: utf-8 -*-

from attrs_mate import attr, AttrsClass, LazyClass
from configirl import ConfigClass, Constant, json_load
from pathlib_mate import Path
from .app_config import AppConfig
from .repo import Repo, Tag, NotValidRepoDirError, NotValidTagDirError

@attr.s
class Application(AttrsClass):
    git_dir = AttrsClass.ib_str()
    repos_dir = AttrsClass.ib_str()
    config = AppConfig.ib_nested(default=None)

    def plan(self):
        for repo_dir in Path(self.repos_dir).select_dir(recursive=False):
            try:
                repo = Repo(path=repo_dir.abspath)
                print(repo)
                for tag_dir in Path(repo.path).select_dir(recursive=False):
                    try:
                        tag = Tag(path=tag_dir.abspath, repo=repo)
                        print(tag)
                    except NotValidTagDirError:
                        pass
            except NotValidRepoDirError:
                pass


