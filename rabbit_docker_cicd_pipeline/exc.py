# -*- coding: utf-8 -*-


class NotValidValueError(Exception):
    tpl_not_valid_type = (
        "{invalid_type} is not a valid type for `Config.{attribute_name}`, "
        "it has to be {valid_type}!"
    )

    tpl_not_from_choices = (
        "{invalid_value!r} is not a valid value for `Config.{attribute_name}`, "
        "it has to be one of {valid_values!r}!"
    )


class NotValidAppDirError(Exception):
    tpl_config_error = (
        "{} is not a valid docker image cicd app directory, "
        "failed to load app config from {}, "
        "because {}"
    )


class NotValidRepoDirError(Exception):
    tpl_config_error = (
        "{} is not a valid docker image repo directory, "
        "failed to load repo config from {}, "
        "because {}"
    )

class NotValidTagDirError(Exception):
    tpl_config_error = (
        "{} is not a valid docker image tag directory, "
        "failed to load tag config from {}, "
        "because {}"
    )

