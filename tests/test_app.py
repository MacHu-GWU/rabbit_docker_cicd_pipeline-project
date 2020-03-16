# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path
from rabbit_docker_cicd_pipeline.app import Application

repos_dir = Path(__file__).parent.parent.append_parts("repos").abspath


class TestApplication(object):
    def test(self):
        app = Application(
            project_name="docker_sanhe",
            repos_dir=repos_dir,
        )
        app.plan()


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
