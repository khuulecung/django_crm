from django.db import models
from django.db.models.signals import post_save # Send signal after save method is committed to the db
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    is_organisor = models.BooleanField(default=True) # Is Organisor field checked in django admin
    is_agent = models.BooleanField(default=False) # Is Agent field unchecked in django admin

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) #CASCADE = if User is delete, the UserProfile is also delete
    # OneToOne => an account can only have 1 profile.
    # OneToOne also allows us to call user.userprofile

    # Return a string instead of an object address
    def __str__(self):
        return self.user.username

class Lead(models.Model):
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    age = models.IntegerField(default=0)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE) # add this to allow filtering leads by organisation
    # UserProfile is created before Lead, therefore you can refer to UserProfile in class/object format.
    agent = models.ForeignKey("Agent", null=True, blank=True, on_delete=models.SET_NULL)  # Agent is created after Lead, therefore you must refer to it in string format.
    category = models.ForeignKey("Category", related_name="leads", null=True, blank=True, on_delete=models.SET_NULL)
    # Foreign key means an Agent can have multiple leads
    # on_delete in agent dictates what to do with lead once agent is deleted?
    # SET_NULL => leads won't be deleted when agents are deleted
    description = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # OneToOne => each Agent can only have 1 account
    # Pass in User => lead information (first name, last name, etc.) is inherited from User class
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    # Foreign key => an organization can have multiple agents
    # CASCADE => if UserProfile is deleted, Agent is deleted as well
    def __str__(self):
        return self.user.email


class Category(models.Model):
    name = models.CharField(max_length=30)
    organisation = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# call this function when post_save signal is sent
def post_user_created_signal(sender, instance, created, **kwargs):
    # sender = the model that send save method (User)
    # instance = string method of username (cung)
    # created = boolean variable, shows whether it's create (True) or update (False) signal
    # **kwargs (keyword argument) is a dictionary that takes in any new argument
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(post_user_created_signal, sender=User)
# 1st argument post_user_created_signal is the function that is called when a save signal is sent.