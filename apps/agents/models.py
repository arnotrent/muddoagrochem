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

    # Self-service profile — the agent can change these any time, no admin
    # approval needed. The account's real name (user.first_name/last_name,
    # set by admin when the account was created) is never touched by this,
    # so admin always has the original on file — see `original_name` below.
    display_name = models.CharField(max_length=150, blank=True)
    avatar       = models.ImageField(upload_to='avatars/agents/', blank=True, null=True)

    class Meta: ordering=['user__first_name']
    def __str__(self): return self.name

    @property
    def name(self):
        """Public-facing name — the agent's own chosen display name if set,
        otherwise falls back to the original account name."""
        return self.display_name.strip() if self.display_name and self.display_name.strip() else self.original_name

    @property
    def original_name(self):
        """The name admin originally set up the account with. Never changed
        by the agent's own profile edits — shown to admin as a quiet
        reference under the chosen display name."""
        return self.user.get_full_name() or self.user.username

    @property
    def email(self): return self.user.email
    @property
    def username(self): return self.user.username
    @property
    def is_online(self):
        if not self.last_seen: return False
        from django.utils import timezone
        return (timezone.now()-self.last_seen).total_seconds()<300
    @property
    def avatar_url(self):
        try:
            return self.avatar.url if self.avatar else None
        except ValueError:
            return None
