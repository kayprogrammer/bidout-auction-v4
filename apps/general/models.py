from django.db import models
from apps.common.models import BaseModel
from apps.accounts.models import User


class SiteDetail(BaseModel):
    name = models.CharField(max_length=300, default="Kay's Auction House")
    email = models.CharField(max_length=300, default="kayprogrammer1@gmail.com")
    phone = models.CharField(max_length=300, default="+2348133831036")
    address = models.CharField(max_length=300, default="234, Lagos, Nigeria")
    fb = models.CharField(max_length=300, default="https://facebook.com")
    tw = models.CharField(max_length=300, default="https://twitter.com")
    wh = models.CharField(max_length=300, default="https://wa.me/2348133831036")
    ig = models.CharField(max_length=300, default="https://instagram.com")

    def __str__(self):
        return self.name


class Subscriber(BaseModel):
    email = models.EmailField(unique=True)
    exported = models.BooleanField(default=False)

    def __str__(self):
        return self.email


class Review(BaseModel):
    __tablename__ = "reviews"

    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    show = models.BooleanField(default=False)
    text = models.CharField(max_length=200)

    def __str__(self):
        return str(self.reviewer.full_name)
