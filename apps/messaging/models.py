from django.db import models

class Message(models.Model):
    ROLES=[('admin','Admin'),('agent','Agent')]
    sender_id=models.IntegerField(); sender_role=models.CharField(max_length=10,choices=ROLES)
    receiver_id=models.IntegerField(); receiver_role=models.CharField(max_length=10,choices=ROLES)
    content=models.TextField(); read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['created_at']
    def __str__(self): return f"[{self.sender_role}→{self.receiver_role}] {self.content[:40]}"
