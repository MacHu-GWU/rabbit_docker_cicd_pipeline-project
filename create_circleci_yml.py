# -*- coding: utf-8 -*-

from jinja2 import Environment, Template
from pathlib_mate import Path
from create_app import app
from rabbit_docker_cicd_pipeline.config import RepoConfig, TagConfig

HERE = Path(__file__).parent

# jinja2 Template creation reference: https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.Template
# circleci_single_template = Template(
#     Path(HERE, ".circleci", "config-single.yml").read_text(encoding="utf-8")
# )
# print(Path(HERE, ".circleci", "config-parallel.yml").read_text(encoding="utf-8"))
circleci_parallel_template = Template(
    Path(HERE, ".circleci", "config-parallel.yml").read_text(encoding="utf-8")
)

app.plan()


circleci_config_yml = Path(HERE, ".circleci", "config.yml")
circleci_config_yml.write_text(
    circleci_parallel_template.render(app=app)
)