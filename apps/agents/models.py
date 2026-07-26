from django.db import models
from django.contrib.auth.models import User

class Agent(models.Model):
    user       = models.OneToOneField(User,on_delete=models.CASCADE,related_name='agent_profile')
    phone      = models.CharField(max_length=30,blank=True)
    region     = models.CharField(max_length=100,blank=True)
    district   = models.CharField(max_length=100,blank=True)
    status     = models.CharField(max_length=20,default='active',choices=[('active','Active'),('inactive','Inactive')])
    last_seen  = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['user__first_name']
    def __str__(self): return self.user.get_full_name() or self.user.username
    @property
    def name(self): return self.user.get_full_name() or self.user.username
    @property
    def email(self): return self.user.email
    @property
    def username(self): return self.user.username
    @property
    def is_online(self):
        if not self.last_seen: return False
        from django.utils import timezone
        return (timezone.now()-self.last_seen).total_seconds()<300
