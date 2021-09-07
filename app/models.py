from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Count
# Create your models here.
DEFAULT = '/image/image.jpg'
class User(AbstractUser):
    image=models.ImageField(default=DEFAULT, blank=True, null=True, upload_to='image/')
    ONLINE = 'online'
    OFFLINE = 'offline'
    STATUS = (
        (ONLINE, 'On-line'),
        (OFFLINE, 'Off-line'),
    )
    status = models.CharField( max_length=100, choices=STATUS,default=OFFLINE )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

class Threading(models.Manager):
    def get_or_create_personal_thread(self, user1, user2):
        threads = self.get_queryset().filter(thread_type='personal')
        threads = threads.filter(users__in=[user1, user2]).distinct()
        threads = threads.annotate(u_count=Count('users')).filter(u_count=2)
        if threads.exists():
            return threads.first()
        else:
            thread = self.create(thread_type='personal')
            thread.users.add(user1)
            thread.users.add(user2)
            return thread

    def by_user(self, user):
        return self.get_queryset().filter(users__in=[user])
class TrackingModel(models.Model):
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Thread(TrackingModel):
    THREAD_TYPE = (
        ('personal', 'Personal'),
        ('group', 'Group')
    )

    name = models.CharField(max_length=50, null=True, blank=True)
    thread_type = models.CharField(max_length=15, choices=THREAD_TYPE, default='group')
    users = models.ManyToManyField(User)

    objects = Threading()

    def __str__(self) -> str:
        if self.thread_type == 'personal' and self.users.count() == 2:
            return f'{self.users.first()} and {self.users.last()}'
        return f'{self.name}'

class Message(TrackingModel):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='Thread')
    sender = models.ForeignKey(User, on_delete=models.CASCADE , related_name="Message")
    text = models.TextField(blank=False, null=False)

    def __str__(self) -> str:
        return f'From <Thread - {self.thread}>'