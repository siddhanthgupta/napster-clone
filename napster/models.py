from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


# Create your models here.
class User(models.Model):
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(default=0, validators=[
                               MaxValueValidator(65535), MinValueValidator(0)])

    class Meta:
        unique_together = (('ip_address', 'port'),)


class File(models.Model):
    filename = models.CharField(primary_key=True, max_length=65535)
    filehash = models.CharField(max_length=65535)


class UserFileMap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File)

    class Meta:
        unique_together = (('user', 'file'))
