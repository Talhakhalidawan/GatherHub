from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
import datetime

# Create your models here.

PRIVACY_CHOICES = [
    ('public', 'Public'),
    ('private', 'Private'),
    ('friends_only', 'Friends'),
]
class Completed(models.Model):
    user = models.ForeignKey(User , on_delete = models.CASCADE)
    completed = models.CharField(max_length = 10)

class Profile(models.Model):
    uid = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    user = models.ForeignKey(User , on_delete = models.CASCADE)
    Profile_image = models.ImageField(upload_to = "Images" , max_length = None)
    cover_image = models.ImageField(upload_to = "Images" , max_length = None)
    bio = models.TextField()
    phone_number = models.CharField(max_length = 15)
    education = models.TextField()
    joined_on = models.DateTimeField(auto_now_add = True)
    updated_on = models.DateTimeField(auto_now = True)
    
    verified = models.BooleanField(default = False)
    
    def __str__(self):
        return self.user.username

class Followers(models.Model):
    id = models.AutoField(primary_key = True)
    following = models.ForeignKey(Profile , on_delete = models.CASCADE , related_name = "followed")
    follower = models.ForeignKey(Profile , on_delete = models.CASCADE , related_name = "follower")
    time_follow = models.DateTimeField(auto_now_add = True)
    
    def __str__(self) -> str:
        return self.follower
    
class Post(models.Model):
    sno = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    user = models.ForeignKey(Profile , on_delete = models.CASCADE)
    post_image = models.ManyToManyField("Image" , related_name = "post_images")
    post_title = models.TextField()
    post_privacy = models.CharField(max_length = 20 , choices = PRIVACY_CHOICES , default = "Friends")
    post_reach = models.IntegerField( default = 0)
    likes = models.IntegerField(default = 0)
    updated_at = models.DateTimeField(auto_now = True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self) -> str:
        return self.post_title

class Image(models.Model):
    image = models.ImageField(upload_to = "Post_images" , max_length = None)
    post = models.ForeignKey(Post , on_delete = models.CASCADE , related_name = "images")
    
class Loves(models.Model):
    react_id = models.AutoField(primary_key = True)
    user = models.ForeignKey(Profile , on_delete = models.CASCADE)
    post = models.ForeignKey(Post , on_delete = models.CASCADE , related_name = "post_loves")
    react_time = models.DateTimeField(auto_now_add = True)
    
    def __str__(self) -> str:
        return self.post.post_title
    
class Comments(models.Model):
    comment_id = models.AutoField(primary_key = True)
    commenter = models.ForeignKey(Profile , on_delete = models.CASCADE)
    post = models.ForeignKey(Post , on_delete = models.CASCADE)
    comment_text = models.CharField( max_length = 150)
    comment_time = models.DateTimeField(auto_now_add = True)
    parent = models.ForeignKey('self' , on_delete = models.CASCADE , null = True , blank = True , related_name = "replies")

class CommentLoves(models.Model):
    id = models.AutoField(primary_key = True)
    comment = models.ForeignKey(Comments , on_delete = models.CASCADE , related_name = "comment_lover")
    user = models.ForeignKey(Profile , on_delete = models.CASCADE)
    react_time = models.DateTimeField(auto_now_add = True)

class Notifications(models.Model):
    started_following = "started_following"
    like_post = "like_post"
    comment = "comment"
    reply = "replied"
    comment_like = "like_comment"
    
    CHOICES_OF_NOTIFICATION = (
        (started_following , "New Follower"),
        (like_post , "New Post like"),
        (comment , "New Comment"),
        (reply , "Replied"),
        (comment_like , "New Comment Like"),
    )

    type_of_notification = models.CharField(max_length = 50 , choices = CHOICES_OF_NOTIFICATION)
    notification_id = models.UUIDField(primary_key = True , default = uuid.uuid4 , editable = False)
    is_read = models.BooleanField(default = False)
    body = models.TextField()
    post = models.ForeignKey(Post , on_delete = models.CASCADE , blank = True , null = True)
    notification_by = models.ForeignKey(Profile , related_name = "notification_created_by" , on_delete = models.CASCADE)
    notification_for = models.ForeignKey(Profile , related_name = "notification_create_for" , on_delete = models.CASCADE)
    created_time = models.DateTimeField(auto_now_add = True)
    parent_comment = models.ForeignKey(Comments , related_name = "parent_comment" , on_delete = models.CASCADE , blank = True , null = True)
    comment_like = models.ForeignKey(Comments , related_name = "Comment_like"  , on_delete = models.CASCADE , blank = True , null = True)
    
    def __str__(self) -> str:
        return self.body
    
class Messages(models.Model):
    id = models.AutoField(primary_key = True)
    message_body = models.CharField(max_length = 500)
    message_time = models.TimeField(auto_now_add = True)
    message_date = models.DateTimeField(auto_now_add = True)
    seen = models.BooleanField(default = True)
    
    sender = models.ForeignKey(Profile , on_delete = models.CASCADE , related_name = "message_sender")
    reciever = models.ForeignKey(Profile , on_delete = models.CASCADE , related_name = "message_reciever")
    
    def formated_time(self):
        return self.message_time.strftime("%I:%M%p").upper().replace(".","").replace("PM"," PM").replace("AM"," AM")

class HelpMessage(models.Model):
    id = models.AutoField(primary_key = True)
    message_body = models.TextField()
    time = models.DateTimeField(auto_now_add = True)
    
    user = models.ForeignKey(Profile , on_delete = models.CASCADE)
    
class GetVerified(models.Model):
    id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 50)
    account_type = models.CharField(max_length = 100)
    profile_image = models.ImageField(upload_to = "request_images" , max_length = None , null = True , blank = True)
    desc = models.TextField()
    social_link1 = models.TextField()
    social_link2 = models.TextField()
    social_link3 = models.TextField()
    user = models.ForeignKey(Profile , on_delete = models.CASCADE)
    additional_notes = models.TextField()
    date_posted = models.DateTimeField(auto_now_add = True)

# class SharePost(models.Model):
#     share_id = models.UUIDField(primary_key = True , default = uuid.uuid4 , editable = False)
#     post = models.ForeignKey(Post , related_name = "share_post" , on_delete = models.CASCADE)
#     shared_by = models.ForeignKey(Profile , on_delete = models.CASCADE , related_name = "shared_by")
#     share_time = models.DateTimeField(auto_now_add = True)
#     update_time = models.DateTimeField(auto_now = True)
    
#     def __str__(self) -> str:
#         return f"{self.post.user.user.first_name} {self.post.user.user.last_name}"