from django.shortcuts import render , redirect , HttpResponse , HttpResponsePermanentRedirect , HttpResponseRedirect
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login , logout , authenticate
from django.contrib.auth.hashers import check_password
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from PIL import Image as images
from django.db.models import Q
from secondary.models import *
import uuid 
import os


# Create your views here.

def home(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    
    posts = Post.objects.prefetch_related('post_image').order_by("-created_at")
    user = Profile.objects.get(user=request.user)
    notifications = Notifications.objects.filter(notification_for = user , is_read = False).count()
    print(notifications)
    
    post_details = []
    for post in posts:
        comments = Comments.objects.filter(post = post).count()
        liked = Loves.objects.filter(user=user, post=post).exists()
        R_likes = Loves.objects.filter(post=post).values('user').distinct().count()
        post_details.append({
            'post': post,
            'liked': liked,
            'R_likes': R_likes,
            'comments' : comments
        })

    context = {
        "user": user,
        "posts": post_details,
        "notifications" : notifications,
    }
    return render(request, "index.html", context)


# Creating Notifications 


def createNotifications(request , type_of_notification , comment_id = None , post_id = None , follower_id = None , parent_comment_id = None):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    
    if post_id is not None:
        psot_1 = Post.objects.get(sno = post_id)

    profile = Profile.objects.get(user = request.user)
    
    if type_of_notification == "like_post":
        body = "liked your"
        post = Post.objects.get(sno = post_id)
        created_for = post.user
    
    elif type_of_notification == "comment":
        body = "Commented on your"
        post = Post.objects.get(sno = post_id)
        created_for = post.user
    
    elif type_of_notification == "like_comment":
        body = "Liked your"
        comment_like = Comments.objects.get(comment_id = comment_id)
        created_for = comment_like.commenter
    
    elif type_of_notification == "replied":
        body = "replied to your comment"
        post = Post.objects.get(sno = post_id)
        parent_comment = Comments.objects.get(comment_id = parent_comment_id)
        created_for = parent_comment.commenter 
        
    
    elif type_of_notification == "started_following":
        body = "Started you following"
        print(f"\n\n\n\n\n\n\n\n\n\n\n\n\n{follower_id} \n\n\n\n\n\n\n\n\n\n")
        follower = Profile.objects.get(uid = follower_id)
        created_for = follower
    
    else :
        pass
    
    if type_of_notification == "started_following":
            
        notifications = Notifications.objects.create(
                notification_by = profile,
                type_of_notification = type_of_notification,
                body = body,
                notification_for = created_for,
            )
    elif type_of_notification == "replied":
        notifications = Notifications.objects.create(
                notification_by = profile,
                type_of_notification = type_of_notification,
                body = body,
                post = psot_1,
                notification_for = created_for,
                parent_comment = parent_comment,
            )
    
    elif type_of_notification == "like_comment":
        notifications = Notifications.objects.create(
                notification_by = profile,
                type_of_notification = type_of_notification,
                body = body,
                notification_for = created_for,
                comment_like = comment_like,
            )
    
    else:    
        notifications = Notifications.objects.create(
                notification_by = profile,
                type_of_notification = type_of_notification,
                body = body,
                post = psot_1,
                notification_for = created_for,
            )


# Login User


def loginUser(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username = username , password = password)
        if user is not None :
            login(request , user)
            return redirect("/")
        else :
            messages.warning(request , "Incorrect username or password.")
    return render(request , "login-user.html")


# Complete profile Details 


def completeProfile(request):
    if not request.user.is_authenticated:
        return redirect("loginUser")
    
    if request.method == "POST":
        profile_image = request.FILES.get("profile_image")
        cover_image = request.FILES.get("cover_image")
        bio = request.POST.get("bio")
        phone_number = request.POST.get("phone_number")
        education = request.POST.get("education")
        profile = Profile(Profile_image = profile_image , cover_image = cover_image , bio = bio , phone_number = phone_number , education = education , user = request.user)
        Profile.save(profile)

        if all([profile_image, cover_image, bio, phone_number, education]):
            completed = Completed(completed="true")
            completed.save()

        return redirect("profile_page")
    return render(request , "complete-signup-details.html")


# Signup user


def signupUser(request):
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
        else:
            user = User.objects.create_user(username = username , email = email , password = password , first_name = f_name , last_name = l_name)
            user.save()
            login(request , user)
            return redirect("completeProfile")
    return render(request , "signup-user.html")


# Post Details


def post_details(request , sno):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == "POST":
        user = Profile.objects.get(user=request.user)
        comment_text = request.POST.get("comment_text")
        post_id = request.POST.get("post_id")
        post = Post.objects.get(sno=post_id)
        comment = Comments(post=post, commenter=user, comment_text=comment_text)
        comment.save()
        if user != post.user:
            notification = createNotifications(request , type_of_notification = "comment" , post_id = post_id)
        response_data = {
                    "comment_id": comment.comment_id,
                    "comment_text": comment.comment_text,
                    "commenter_image": comment.commenter.Profile_image.url,
                    "commenter_name": f"{comment.commenter.user.first_name} {comment.commenter.user.last_name}",
                    "Verified": comment.commenter.verified if comment.commenter.verified else None,
                }

        return JsonResponse(response_data)
    
    post = Post.objects.get(sno = sno)
    comments = Comments.objects.filter(post = post , parent__isnull = True).order_by("-comment_time")
    
    user = Profile.objects.get(user = request.user)
    comments_count = Comments.objects.filter(post = post).count()
    liked = Loves.objects.filter(user=user, post=post).exists()
    likes = Loves.objects.filter(post=post).values('user').distinct().count()
    
    data = []
    
    for comment_range in comments:
        loved = CommentLoves.objects.filter(comment = comment_range , user = user).exists()
        likes_count = CommentLoves.objects.filter(comment = comment_range).values("user").distinct().count()
        print(loved)
        data.append({
            "loved" : loved,
            "comments" : comment_range,
            "loves_count" : likes_count,
        })
    
    context = {
        "user" : user,
        "post" : post,
        "comments" : data,
        "comments_count" : comments_count,
        "likes" : likes,
        "liked" : liked,
        "loved" : loved,
    }
    return render(request , "post-details.html" , context)


# Create Post With Compressed Images


def create_post(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == "POST":
        post_text = request.POST.get("post-text")
        post_privacy = request.POST.get("post-privacy")
        post_images = request.FILES.getlist("post-images")
        user = Profile.objects.get(user=request.user)
        
        post = Post(post_title=post_text, post_privacy=post_privacy, user=user)
        post.save()
        
        for image in post_images:
            img = images.open(image)
            width, height = img.size
            original_size = image.size
            
            if original_size > 1024 * 1024:
                unique_filename = str(uuid.uuid4())[:8]
                output_image_path = os.path.join(settings.MEDIA_ROOT, 'post_images', f'{unique_filename}_compressed.jpg')
                resized_image = img.resize((width // 2, height // 2))
                resized_image.save(output_image_path, optimize=True, quality=50)
                
                img_obj = Image.objects.create(image=f'post_images/{unique_filename}_compressed.jpg', post=post)
                post.post_image.add(img_obj)
            else:
                unique_filename = str(uuid.uuid4())[:8]
                output_image_path = os.path.join(settings.MEDIA_ROOT, 'post_images', f'{unique_filename}.jpg')  
                img.save(output_image_path)
                
                img_obj = Image.objects.create(image=f'post_images/{unique_filename}.jpg', post=post)
                post.post_image.add(img_obj)
        
        return redirect("/")
    
    user = Profile.objects.get(user=request.user)
    context = {
        "user": user,
    }
    return render(request, "create-post.html", context)


# Profile Page


def profile_page(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    profile = Profile.objects.get(user = request.user)
    # Countings 
    followers_count = Followers.objects.filter(following = profile).count()
    following_count = Followers.objects.filter(follower = profile).count()
    # Showing Posts of the user
    post = Post.objects.filter(user = profile).order_by("-created_at")
    # Followers Showing
    followers = Followers.objects.filter(following=profile).select_related('follower')[:9]

    for follow in followers:
        follow.follower.is_followed_by_user = Followers.objects.filter(follower=profile, following=follow.follower).exists()
    
    post_details = []
    for posts in post:
        R_likes = Loves.objects.filter(post=posts).values('user').distinct().count()
        liked = Loves.objects.filter(user = profile, post = posts).exists()
        post_details.append({
            'post': posts,
            'R_likes': R_likes,
            "liked" : liked,
        })
    
    context = {
        "profile" : profile,
        "followers_count" : followers_count,
        "following_count" : following_count,
        "followers" : followers,
        "posts" : post,
        "post" : post_details,
    }
    return render(request , "profile.html" , context)


# Logout


def logoutUser(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    logout(request)
    return redirect("loginUser")


# Show all Users


def allPeople(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    user_profile = get_object_or_404(Profile, user=request.user)
    people = Profile.objects.exclude(user=request.user)
    
    for person in people:
        person.is_followed_by_user = Followers.objects.filter(follower=user_profile, following=person).exists()
        person.is_following_user = Followers.objects.filter(follower=person, following=user_profile).exists()
    
    context = {
        "people": people,
    }
    return render(request, "friend-list.html", context)


# Follow a User


def follow_user(request, uid):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == 'POST':
        user_profile = get_object_or_404(Profile, user=request.user)
        target_profile = get_object_or_404(Profile, uid=uid)
        if user_profile != target_profile:
            Followers.objects.get_or_create(follower=user_profile, following=target_profile)
            is_following_back = Followers.objects.filter(follower=target_profile, following=user_profile).exists()
            print(target_profile.uid)
            notification = createNotifications(request , type_of_notification = "started_following" , follower_id = target_profile.uid)
            return JsonResponse({'status': 'success', 'is_following_back': is_following_back})
    return JsonResponse({'status': 'error'}, status=400)


# Unfollow a User


def unfollow_user(request, uid):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == 'POST':
        user_profile = get_object_or_404(Profile, user=request.user)
        target_profile = get_object_or_404(Profile, uid=uid)
        follow_relationship = Followers.objects.filter(follower=user_profile, following=target_profile)
        if follow_relationship.exists():
            follow_relationship.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


# Followers of the User


def followers(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    user_profile = Profile.objects.get(user=request.user)
    followers = Followers.objects.filter(following=user_profile).select_related('follower')
    
    for follow in followers:
        follow.follower.is_followed_by_user = Followers.objects.filter(follower=user_profile , following=follow.follower).exists()
    
    context = {
        "followers": followers,
    }
    return render(request, "friend-list.html", context)


# Following of the User


def following(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    user_profile = get_object_or_404(Profile, user=request.user)
    following = Followers.objects.filter(follower=user_profile).select_related('following')
    
    for follow in following:
        follow.following.is_followed_by_user = Followers.objects.filter(follower=user_profile, following=follow.following).exists()
    
    context = {
        "following": following,
    }
    return render(request, "friend-list.html", context)

    
# Post reacts 


def post_likes(request, post_id):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    post = get_object_or_404(Post, sno=post_id)
    user = Profile.objects.get(user=request.user)
    liked = Loves.objects.filter(user=user, post=post).exists()

    if not liked:
        Loves.objects.create(user=user, post=post)
        post.likes += 1
        post.post_reach += 50
        post_obj = Post.objects.get(sno = post_id)
        if user != post.user :
            notification = createNotifications(request , type_of_notification = "like_post" , post_id = post_id)
        else:
            pass

    else:
        Loves.objects.filter(user=user, post=post).delete()
        post.likes -= 1 
        post.post_reach -= 40

    post.save()

    R_likes = Loves.objects.filter(post=post).values('user').distinct().count()

    data = {
        'current_likes': post.likes,
        'liked': not liked,
        'R_likes': R_likes,
    }

    return JsonResponse(data)


# Create comment 


def create_main_comment(user, comment_text, post_id):

    try:
        post = Post.objects.get(sno=post_id)
        comment = Comments(post=post, commenter=user, comment_text=comment_text)
        comment.save()
        print("here 1")
        return comment
    except Post.DoesNotExist:
        raise ValueError("Post does not exist.")



def create_reply(user, comment_text, parent_comment_id):

    try:
        parent_comment = Comments.objects.get(comment_id=parent_comment_id)
        reply = Comments(post=parent_comment.post, commenter=user, comment_text=comment_text)
        reply.parent = parent_comment
        print("here")
        reply.save()
        return reply
    except Comments.DoesNotExist:
        raise ValueError("Parent comment does not exist.")



def create_comment(request):
    if not request.user.is_authenticated:
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == "POST":
        user = Profile.objects.get(user=request.user)
        comment_text = request.POST.get("comment_text", "").strip()
        post_id = request.POST.get("post_id")
        parent_comment_id = request.POST.get("parent_comment_id")

        if comment_text:
            try:
                if parent_comment_id:
                    comment = create_reply(user, comment_text, parent_comment_id)
                    parent_comment = Comments.objects.get(comment_id = parent_comment_id)
                    created_for = parent_comment.commenter
                    if user != created_for:
                        notification = createNotifications(request , type_of_notification = "replied" , post_id = post_id , parent_comment_id = parent_comment_id)
                else:
                    comment = create_main_comment(user, comment_text, post_id)
                    print("here")
                    notification = createNotifications(request , type_of_notification = "comment" , post_id = post_id)

                response_data = {
                    "comment_id": comment.comment_id,
                    "comment_text": comment.comment_text,
                    "commenter_image": comment.commenter.Profile_image.url,
                    "commenter_name": f"{comment.commenter.user.first_name} {comment.commenter.user.last_name}",
                    "parent_comment_id": comment.parent.comment_id if comment.parent else None,
                }

                return JsonResponse(response_data)
            except Post.DoesNotExist:
                return JsonResponse({"message": "Post does not exist."}, status=400)



# Show live comments


def getProfiles(request, sno):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    post = Post.objects.get(sno=sno)
    comments = Comments.objects.filter(post=post , parent__isnull = True).order_by("-comment_time")
    comment_html = render_to_string('comments.html', {'comments': comments , "user" : request.user})
    return JsonResponse({"comments_html": comment_html})



# User Profile 


def userProfile(request , uid):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    profile = Profile.objects.get(uid = uid)
    user_profile = get_object_or_404(Profile, user=request.user)
    people = profile
    
    if profile.user == request.user :
        return redirect("profile_page")

    followers_count = Followers.objects.filter(following = profile).count()
    following_count = Followers.objects.filter(follower = profile).count()




    post = Post.objects.filter(user = profile).order_by("-created_at")
    
    
    followers = Followers.objects.filter(following=profile).select_related('follower')[:9]

    for follow in followers:
        follow.follower.is_followed_by_user = Followers.objects.filter(follower=profile, following=follow.follower).exists()

    profile.is_followed_by_user = Followers.objects.filter(follower=user_profile, following=profile).exists()
    profile.is_following_user = Followers.objects.filter(follower=profile, following=user_profile).exists()


    post_details = []
    for posts in post:
        R_likes = Loves.objects.filter(post=posts).values('user').distinct().count()
        liked = Loves.objects.filter(user = user_profile, post = posts).exists()
        post_details.append({
            'post': posts,
            'R_likes': R_likes,
            "liked" : liked,
        })


    context = {
        "post": post_details,
        "profile" : profile,
        "followers_count" : followers_count,
        "following_count" : following_count,
        "followers" : followers,
        "posts" : post,
        "people": people,
    }
    
    return render(request , "user_profile.html" , context)


# Delete a Comment



def deleteComment(request, id):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == 'POST':
        comment = Comments.objects.get(comment_id = id)
        
        # Check if the logged-in user is the owner of the comment
        if comment.commenter.user == request.user:
            comment.delete()
            return JsonResponse({'message': 'Comment deleted successfully'})
        else:
            return JsonResponse({'error': 'You are not authorized to delete this comment'}, status = 403)
    
    return JsonResponse({'error': 'Method not allowed'}, status = 405)


# Delete Post


def deletePost(request , sno):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == "POST":
        post = Post.objects.get(sno = sno)
        
        if post.user.user == request.user :
            post.delete()
            return JsonResponse({'message': 'Post deleted successfully'})
        else :
            return JsonResponse({'error': 'You are not authorized to delete this post'}, status = 403)
    return JsonResponse({'error' : 'Method not allowed'} , status = 405)


# Settings 


def setting(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    return render(request , "settings.html")


# Change personal details 


def change_name(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    current_name = Profile.objects.get(user = request.user)
    if request.method == "POST":
        f_name = request.POST.get("f_name")
        l_name = request.POST.get("l_name")
        password = request.POST.get("password")
        user = request.user
        
        if check_password(password , user.password):
            user.first_name = f_name
            user.last_name = l_name
            user.save()
            
            update_session_auth_hash(request , user)
            
            messages.success(request , "Your name was updated successfully!")
            return redirect('profile_page')
        else :
            messages.error(request , "The password you entered is incorrect.")
    
    f_name1 = current_name.user.first_name
    l_name1 = current_name.user.last_name
    
    context = {
        "data" : "name",
        "f_name" : f_name1,
        "l_name" : l_name1
    }
    return render(request , "change-details.html" , context)


# Change Email Address


def change_email(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = request.user
        
        if check_password(password , user.password):
            user.email = email
            user.save()
            
            messages.success(request , "Your name was updated successfully!")
        else :
            messages.error(request , "The password you entered is incorrect.")
            
    user = Profile.objects.get(user = request.user)
    email = user.user.email
    context = {
        "data" : "email",
        "email" : email,
    }
    return render(request , "change_email.html" , context)


# Change Password


def change_password(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == "POST":
        old_pass = request.POST.get("password")
        new_password = request.POST.get("new_pass")
        confirm_new_pass = request.POST.get("confirm_new_pass")
        
        # Check if new passwords match
        if new_password != confirm_new_pass:
            messages.warning(request, "Passwords didn't match!")
            return redirect('change_password')

        # Authenticate old password
        user = authenticate(username=request.user.username, password=old_pass)
        if user is not None:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            
            return redirect('change_password')
        else:
            messages.error(request, "Enter correct password")
    
    context = {
        "data" : "password",
    }
    return render(request, "change-details.html" , context)


# Show Notifications


def showNotifications(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    user = Profile.objects.get(user = request.user)
    notification = Notifications.objects.filter(notification_for = user).order_by("-created_time")
    context = {
        "notification" : notification
    }
    return render(request , "notifications.html" , context)


# Viewed Notification 


def mark_notification_as_read(request, notification_id):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    notification = get_object_or_404(Notifications, notification_id=notification_id)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})


# Mark all as read 


def mark_all_as_read(request):
    if not request.user.is_authenticated:
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    profile = Profile.objects.get(user = request.user)
    Notifications.objects.filter(notification_for = profile , is_read = False).update(is_read = True)
    
    return redirect("notifications")


# Poll notifications 


def poll_notifications(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    user = Profile.objects.get(user=request.user)
    notifications = Notifications.objects.filter(notification_for=user).order_by("-created_time").values('notification_id', 'is_read')
    return JsonResponse({'notifications': list(notifications)})


# Comment Replies


def commentReplies(request , comment_id):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    comment = Comments.objects.get(comment_id = comment_id)
    replies = Comments.objects.filter(parent = comment).order_by("-comment_time")
    profile = Profile.objects.get(user = request.user)
    
    parent_loved = CommentLoves.objects.filter(comment = comment , user = profile).exists()
    parent_likes_count = CommentLoves.objects.filter(comment = comment).values("user").distinct().count()
    
    print("Parent Loved = ",parent_loved)
    
    data = []
    
    for comments in replies:
        loved = CommentLoves.objects.filter(comment = comments , user = profile).exists()
        likes_count = CommentLoves.objects.filter(comment = comments).values("user").distinct().count()
        print(likes_count)
        print(loved)
        data.append({
            "loved" : loved,
            "reply" : comments,
            "loves_count" : likes_count,
        })

    context = {
        "comment" : comment,
        "replies" : data,
        "profile" : profile,
        "parent_loved" : parent_loved,
        "parent_likes_count" : parent_likes_count,
    }
    return render(request , "comment-replies.html" , context)



# Error Pages


def custom_404(request, exception):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)


# Help Page 


def helpPage(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    if request.method == "POST":
        message = request.POST.get("help_text")
        user = Profile.objects.get(user = request.user)
        help = HelpMessage.objects.create(message_body = message , user = user)
        messages.success(request , "Your message was submitted successfully we will notify you soon.")
        
    return render(request , "help.html")



# Comment Likes 


def commentLoves(request , comment_id):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comment = Comments.objects.get(comment_id = comment_id)
    user = Profile.objects.get(user = request.user)
    
    loved = CommentLoves.objects.filter(comment = comment , user = user).exists()
    
    if not loved:
        CommentLoves.objects.create(comment = comment , user = user)
        if comment.commenter != user:
            notification = createNotifications(request , type_of_notification = "like_comment" , comment_id = comment_id)
    
    else :
        CommentLoves.objects.filter(comment = comment , user = user).delete()
    
    comment.save()
    
    likes_count = CommentLoves.objects.filter(comment = comment).values("user").distinct().count()
    
    data = {
        "likes_count" : likes_count,
        "loved" : not loved,
    }
    
    return JsonResponse(data)


# Messages 


def message(request , uid):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    profile = Profile.objects.get(uid = uid)
    user = Profile.objects.get(user = request.user)
    
    if request.method == "POST":
        message_body = request.POST.get("message_body")
        message = Messages.objects.create(message_body = message_body , sender = user , reciever = profile)
        
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        else:
            return redirect('some_default_view')
        
    messages = Messages.objects.filter(
        (Q(sender = user) & Q(reciever = profile)) |
        (Q(sender = profile) & Q(reciever = user))
    ).order_by("-message_time")
    
    data = []
    
    for i in messages:
        formated_time = i.formated_time
        data.append({
            "message" : i,
            "formated_time" : formated_time,
        })
        
    context = {
        "profile" : profile,
        "user" : user,
        "messages" : data,
    }
    return render(request , "messages.html" , context)


# Messanger People list


def peopleList(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
        
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    user = Profile.objects.get(user=request.user)
    followers = Followers.objects.filter(follower=user)
    
    data = []
    
    for follower in followers:
        profile = follower.following
        last_message = Messages.objects.filter(
            (Q(sender=user) & Q(reciever=profile)) |
            (Q(sender=profile) & Q(reciever=user))
        ).order_by('-message_time').first()
        
        data.append({
            "messages": last_message,
            "profile": profile,
        })
    
    context = {
        "followers": data,
    }
    return render(request, "people-list.html", context)

# Get Verified

def verified(request):
    if not request.user.is_authenticated :
        return redirect("loginUser")
    
    comp = Completed.objects.filter(user = request.user).first()

    if not comp or comp.completed != "true":
        return redirect("completeProfile")
    if request.method == "POST":
        name = request.POST.get("full_name")
        image = request.FILES.get("profile_image")
        account_type = request.POST.get("account_type")
        desc = request.POST.get("desc")
        link1 = request.POST.get("e_links1")
        link2 = request.POST.get("e_links2")
        link3 = request.POST.get("e_links3")
        additional_notes = request.POST.get("additional_notes")
        profile = Profile.objects.get(user = request.user)
        GetVerified.objects.create(name = name , profile_image = image , account_type = account_type , desc = desc , social_link1 = link1 , social_link2 = link2 , social_link3 = link3 , additional_notes = additional_notes , user = profile)
        messages.success(request , "Your message was submitted successfully we will notify you soon.")
    return render(request , "verified.html")