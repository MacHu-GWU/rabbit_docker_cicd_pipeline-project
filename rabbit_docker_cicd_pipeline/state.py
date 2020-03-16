# -*- coding: utf-8 -*-

from datetime import datetime

from pynamodb.attributes import UnicodeAttribute
from pynamodb.models import Model


class BaseTagStateModel(Model):
    identifier = UnicodeAttribute(hash_key=True)
    fingerprint = UnicodeAttribute()
    last_update = UnicodeAttribute()

    @property
    def last_update_datetime(self):
        """
        datetime type of ``last_update``

        :rtype: datetime
        """
        return datetime.strptime(self.last_update, "%Y-%m-%d %H:%M:%S.%f")

    @property
    def seconds_from_last_update(self):
        """
        elapsed seconds from last update

        :rtype: float
        """
        return (datetime.utcnow() - self.last_update_datetime).total_seconds()
