from django.contrib.auth.views import PasswordResetView , PasswordResetDoneView , PasswordResetConfirmView , PasswordResetCompleteView
from django.urls import path ,register_converter , include
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.conf import settings
from secondary.views import *
import uuid

class UUIDConverter:
    regex = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

    def to_python(self, value):
        return uuid.UUID(value)

    def to_url(self, value):
        return str(value)

register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    path("" , home , name = "home"),
    path("post-details/<uuid:sno>" , post_details , name = "post_details"),
    path("create-post/" , create_post , name = "create_post"),
    path("profile/" , profile_page , name = "profile_page"),
    path("login-user/" , loginUser , name = "loginUser"),  
    path("signup-user/" , signupUser , name = "signupUser"),
    path("complete-signup-details/" , completeProfile , name = "completeProfile"),
    path("logout-user/" , logoutUser , name = "logoutUser"),
    path("all_people/" , allPeople , name = "all_people"),
    path('follow/<uuid:uid>/', follow_user , name='follow_user'),
    path('unfollow/<uuid:uid>/', unfollow_user , name='unfollow_user'),
    path("followers/" , followers , name = "followers"),
    path("following/" , following , name = "following"),
    path('likes/<uuid:post_id>/', post_likes, name = 'post_likes'),
    path("create_comment/" , create_comment , name = "create_comment"),
    path("user_profile/<uuid:uid>/" , userProfile , name = "user_profile"),
    path("getProfiles/<uuid:sno>/" , getProfiles , name = "getProfiles"),
    path("delete_comment/<int:id>/" , deleteComment , name = "delete_comment"),
    path("delete_post/<uuid:sno>/" , deletePost , name = "delete_post"),
    path("settings/" , setting , name = "settings"),
    path("change_details/" , change_name , name = "change_details"),
    path("change_pass/" , change_password , name = "change_pass"),
    path("reset/" , PasswordResetView.as_view(template_name = "password_reset_form.html" , html_email_template_name = "password_reset_email.html") , name = "password_reset"),
    path("reset_done/" , PasswordResetDoneView.as_view(template_name = "password_reset_done.html") , name = "password_reset_done"),
    path("reset_confirm/<uidb64>/<token>/" , PasswordResetConfirmView.as_view(template_name = "password_reset_confirm.html") , name = "password_reset_confirm"),
    path("reset_complete/" , PasswordResetCompleteView.as_view(template_name = "passowrd_reset_complete.html") , name = "password_reset_complete"),
    path("change_email/" , change_email , name = "change_email"),
    path("notifications/" , showNotifications , name = "notifications"),
    path('notification/<uuid:notification_id>/read/', mark_notification_as_read, name='mark_notification_as_read_ajax'),
    path('poll_notifications/', poll_notifications, name='poll_notifications'),
    path("comment_replies/<int:comment_id>" , commentReplies , name = "comment_replies"),
    path("ask_for_help/" , helpPage , name = "ask_for_help"),
    path("settings/get-verified-gatherhub/" , verified , name = "get-verified-gatherhub"),
    path("commentReacts/<int:comment_id>/" , commentLoves , name = "commentReacts"),
    path("mark-all-as-read/" , mark_all_as_read , name = "mark-all-as-read"),
    path("message/<uuid:uid>" , message , name = "message"),
    path("chat-list/" , peopleList , name = "chat-list"),
]

handler404 = 'secondary.views.custom_404'
handler500 = 'secondary.views.custom_500'

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)