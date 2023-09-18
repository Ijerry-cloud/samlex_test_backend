from django.db import models
from uuid import uuid4
from django.contrib.auth import get_user_model

# Create your models here.
class NotificationEmails(models.Model):

    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "A user with that email address already exists.",
        },
    )
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        get_user_model(),
        related_name='creator',
        null=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.ForeignKey(
        get_user_model(),
        related_name='last_updated',
        null=True,
        on_delete=models.SET_NULL
    )
    updated_at = models.DateTimeField(auto_now=True) 


    def __str__(self):
        return self.name
