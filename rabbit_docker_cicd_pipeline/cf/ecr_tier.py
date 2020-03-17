# -*- coding: utf-8 -*-

import json

from troposphere_mate import Template, ecr, camelcase

try:
    from ..config import AppConfig
except:
    pass


def create_template(app):
    """
    :type app: AppConfig

    :rtype: Template
    """
    template = Template()

    for repo in app.repos:
        if repo.repo_registry != AppConfig.Options.RepoRegistry.aws_ecr:
            continue
        ecr.Repository(
            f"Repository{camelcase(repo.repo_name)}",
            template=template,
            RepositoryName=repo.repo_name,
            LifecyclePolicy=ecr.LifecyclePolicy(
                LifecyclePolicyText=json.dumps({
                    "rules": [
                        {
                            "rulePriority": 1,
                            "description": "Expire images older than 14 days",
                            "selection": {
                                "tagStatus": "untagged",
                                "countType": "sinceImagePushed",
                                "countUnit": "days",
                                "countNumber": repo.repo_aws_ecr_life_cycle_expire_days
                            },
                            "action": {
                                "type": "expire"
                            }
                        }
                    ]
                })
            ),
            DeletionPolicy="Retain",
        )
    common_tags = dict(
        ProjectName=app.app_name,
    )
    template.update_tags(common_tags)
    return template
