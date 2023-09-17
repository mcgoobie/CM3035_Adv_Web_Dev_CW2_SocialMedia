# Start of code I wrote
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# User = settings.AUTH_USER_MODEL


class AccountManager(BaseUserManager):

    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have a valid email. ')
        if not username:
            raise ValueError('Users must have a valid username. ')
        user = self.model(
            # Make sure things like capitalization doesnt affect the email
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, f_name, l_name, gender, dob, password):
        user = self.model(
            # Make sure things like capitalization doesnt affect the email
            email=self.normalize_email(email),
            username=username,
            f_name=f_name,
            l_name=l_name,
            gender=gender,
            dob=dob,
        )
        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


def get_pfp_filepath(self, filename):
    # Return url of profile picture
    return f'profile_pictures/{self.pk}/{"profile_picture.png"}'


def get_default_pfp():
    # Fetch default blank profile picture
    return 'static_icons/blank-pfp.png'

# Create your models here.


class UserAccount(AbstractBaseUser):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    email = models.EmailField(verbose_name="Email",
                              max_length=100, unique=True)
    f_name = models.CharField(max_length=50)
    l_name = models.CharField(max_length=50)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    username = models.CharField(max_length=20, unique=True)
    date_joined = models.DateTimeField(
        verbose_name="Date Joined", auto_now_add=True)
    last_login = models.DateTimeField(
        verbose_name="Last Online", auto_now=True)
    # Include to override AbstractBaseUser class versions
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    profile_picture = models.ImageField(
        max_length=255, upload_to=get_pfp_filepath, null=True, blank=True, default=get_default_pfp)
    # For Privacy in a social media web
    hide_email = models.BooleanField(default=True)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['f_name', 'l_name', 'gender', 'dob', 'username']

    def __str__(self):
        return self.username
    
    def get_f_name(self):
        return self.f_name

    # Include to override ABUser Class versions
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class UserPosts(models.Model):
    image = models.ImageField(upload_to='posts', blank=True)
    content = models.TextField(max_length=500, null=False)
    post_date = models.DateTimeField(auto_now_add=True)
    user_account = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="author")  # Author of the post

    def __str__(self):
        return f'By: {self.user_account.username}'
    
    def get_author(self):
        return str(self.user_account)


# End of Code I wrote