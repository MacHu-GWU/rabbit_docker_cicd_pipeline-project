# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path

from rabbit_docker_cicd_pipeline.repo import (
    NotValidRepoDirError, Repo,
    NotValidTagDirError, Tag,
)

dir_repos = Path(__file__).parent.parent.append_parts("repos")

valid_repo_path = Path(dir_repos, "runtime").abspath
repo_path_no_config_file = Path(dir_repos, "runtime-bad-case1-no-config-file").abspath
repo_path_invalid_registry = Path(dir_repos, "runtime-bad-case2-invalid-registry").abspath
repo_path_docker_hub_no_username = Path(dir_repos, "runtime-bad-case3-docker-hub-no-username").abspath


class TestRepo(object):
    def test_init(self):
        repo = Repo(path=valid_repo_path)

    def test_init_bad_case(self):
        with pytest.raises(NotValidRepoDirError) as e:
            Repo(path=repo_path_no_config_file)
        assert "doesn't exists" in str(e)

        with pytest.raises(NotValidRepoDirError) as e:
            Repo(path=repo_path_invalid_registry)
        assert "is a invalid registry" in str(e)

        with pytest.raises(NotValidRepoDirError) as e:
            Repo(path=repo_path_docker_hub_no_username)
        assert "docker_hub_username config is invalid" in str(e)
        # print(e)

valid_tag_path = Path(dir_repos, "runtime", "python3.6.8-crawler").abspath
tag_path_no_config_file = Path(dir_repos, "runtime", "python3.6.8-crawler-bad-case1-no-config-file").abspath
tag_path_no_docker_file = Path(dir_repos, "runtime", "python3.6.8-crawler-bad-case2-no-docker-file").abspath

class TestTag(object):
    # def test_init(self):
    #     repo = Repo(path=valid_repo_path)
    #     tag = Tag(path=valid_tag_path, repo=repo)

    def test_init_bad_case(self):
        repo = Repo(path=valid_repo_path)
        with pytest.raises(NotValidTagDirError) as e:
            Tag(path=tag_path_no_config_file, repo=repo)
        assert "doesn't exists" in str(e)
        
        with pytest.raises(NotValidTagDirError) as e:
            Tag(path=tag_path_no_docker_file, repo=repo)
        assert "Dockerfile not found" in str(e)



if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
