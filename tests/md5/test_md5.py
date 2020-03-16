# -*- coding: utf-8 -*-

import pytest
from pathlib_mate import Path

from rabbit_docker_cicd_pipeline.md5 import get_dockerfile_md5

HERE = Path(__file__).parent


def test_get_dockerfile_md5():
    v1 = get_dockerfile_md5(HERE.append_parts("Dockerfile1").abspath)
    v2 = get_dockerfile_md5(HERE.append_parts("Dockerfile2").abspath)
    v3 = get_dockerfile_md5(HERE.append_parts("Dockerfile3").abspath)
    v4 = get_dockerfile_md5(HERE.append_parts("Dockerfile4").abspath)

    assert v1 == v2 == v3 == v4


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
