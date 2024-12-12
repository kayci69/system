from django.db import models
from users.models import CustomUser

class AdminLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.CharField(max_length=50, blank=False, null=False)
    message = models.TextField(max_length=500, blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.timestamp}"