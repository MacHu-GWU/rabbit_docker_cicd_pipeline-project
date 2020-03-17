#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib_mate import Path
from create_app import app
from rabbit_docker_cicd_pipeline.config import RepoConfig, TagConfig

HERE = Path(__file__).parent

if __name__ == "__main__":
    import sys

    tag_dir = "repos/runtime/python3.6.8-crawler"

    # tag_dir = sys.argv[1]

    if Path(tag_dir).is_absolute():
        tag_root_dir = tag_dir
    else:
        tag_root_dir = Path(HERE, tag_dir).abspath

    repo_root_dir = Path(tag_root_dir).parent.abspath

    repo = RepoConfig(repo_root_dir=repo_root_dir)
    repo.absorb(app)
    repo.fill_na_with_default()
    repo.validate()

    tag = TagConfig(tag_root_dir=tag_root_dir)
    tag.absorb(repo)
    tag.fill_na_with_default()
    tag.validate()
    tag.run_build_test_and_push()
