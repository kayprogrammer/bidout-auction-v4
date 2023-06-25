from django.db import models


class GetOrNoneManager(models.Manager):
    """Adds get_or_none method to objects"""

    async def get_or_none(self, **kwargs):
        try:
            return await self.aget(**kwargs)
        except self.model.DoesNotExist:
            return None
