# -*- coding: utf-8 -*-

from datetime import datetime

import pytest

from rabbit_docker_cicd_pipeline.state import BaseTagStateModel


class TagStateModel(BaseTagStateModel):
    class Meta:
        table_name = "docker-image-tag-state"


class TestBaseTagStatetModel(object):
    def test_property_attribuet(self):
        model = TagStateModel(last_update="2020-01-01 00:00:00.123456")
        assert isinstance(model.last_update_datetime, datetime)
        assert isinstance(model.seconds_from_last_update, float)


if __name__ == "__main__":
    import os

    basename = os.path.basename(__file__)
    pytest.main([basename, "-s", "--tb=native"])
