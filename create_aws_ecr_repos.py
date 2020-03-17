# -*- coding: utf-8 -*-

"""
This script implements one-click create all AWS ECR repository.
"""

from pathlib_mate import Path
from troposphere_mate import StackManager

from create_app import app
from rabbit_docker_cicd_pipeline.cf.ecr_tier import create_template

HERE = Path(__file__).parent

app.plan()
template = create_template(app)

sm = StackManager(
    boto_ses=app.app_boto_ses,
    cft_bucket=app.app_cft_bucket,
)
sm.deploy(template, stack_name=app.app_name)
