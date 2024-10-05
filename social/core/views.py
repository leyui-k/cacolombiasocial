from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django_user_agents.utils import get_user_agent
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Profile, Post, LikePost, FollowersCount, Notification, Comment
from itertools import chain
import random
from uuid import UUID


# Create your views here.

from django.db.models import Q

from django.db.models import Q

from django.db.models import Q

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    # Get notifications for the current user
    notifications = Notification.objects.filter(user=request.user).select_related('follower_profile').order_by('-timestamp')[:5]

    # Get the list of users followed by the current user
    user_following_list = FollowersCount.objects.filter(follower=request.user.username).values_list('user', flat=True)

    # Obtain all publications, excluding your own
    feed_list = Post.objects.all()
    for post in feed_list:
        for comment in post.comments.all():
            comment.comments_profile = Profile.objects.get(user=comment.user)
            comment.save()

    # user suggestion starts
    all_users = User.objects.all()
    user_following_all = User.objects.filter(username__in=user_following_list)

    new_suggestions_list = all_users.exclude(username__in=user_following_all.values_list('username', flat=True))
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = new_suggestions_list.exclude(username__in=current_user.values_list('username', flat=True))
    final_suggestions_list = list(final_suggestions_list)  # Convert to list
    random.shuffle(final_suggestions_list)

    username_profile_list = list(Profile.objects.filter(user__in=final_suggestions_list))

    suggestions_username_profile_list = username_profile_list
    final_user_following_list = user_following_list

    # Detectar el tipo de dispositivo
    user_agent = get_user_agent(request)
    es_dispositivo_movil = user_agent.is_mobile

    if es_dispositivo_movil:
        template_name = 'mobile_index.html'
    else:
        template_name = 'index.html'

    return render(request, template_name, {'user_profile': user_profile, 'posts': feed_list, 'suggestions_username_profile_list': suggestions_username_profile_list[:4], 'final_user_following_list': final_user_following_list[:4], 'notifications': notifications})

@login_required(login_url='signin')
def comment_post(request, post_id):
    if request.method == 'POST':
        # Obtener la publicación a la que se está comentando
        post = get_object_or_404(Post, id=post_id)
        
        # Obtener el comentario del formulario
        comment_text = request.POST.get('comment')
        
        # Crear el comentario y asociarlo con la publicación
        new_comment = Comment.objects.create(post=post, user=request.user, text=comment_text)
        
        # Asignar el perfil del usuario que realizó el comentario al campo comments_profile
        new_comment.comments_profile = Profile.objects.get(user=request.user)
        
        # Guardar el comentario
        new_comment.save()
        
        # Redireccionar a la página de inicio u otra página después de comentar
        return redirect('/')
    else:
        # Manejar el caso de acceso directo a la URL sin enviar un formulario POST
        return redirect('/')
    
def delete_comment(request, comment_id):
    # Obtener el comentario a eliminar
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Verificar si el usuario actual es el autor del comentario
    if comment.user == request.user:
        # Eliminar el comentario
        comment.delete()
        # Redireccionar a la página principal o a donde sea apropiado después de eliminar el comentario
        return redirect('/')
    else:
        # Manejar el caso en que el usuario no esté autorizado para eliminar el comentario
        # Puedes mostrar un mensaje de error o redireccionar a otra página
        return redirect('/')

from django.core.files.base import ContentFile

@login_required(login_url='signin')
def upload(request):

    if request.method == 'POST':
        user = request.user.username
        image_upload = request.FILES.get('image_upload')
        caption = request.POST.get('caption', '')

        if image_upload:
            if 'video' in image_upload.content_type:
                # Es un video
                post = Post.objects.create(user=user, video=image_upload, caption=caption)
            elif 'image' in image_upload.content_type:
                # Es una imagen
                if image_upload.name.lower().endswith('.gif'):
                    # Es un GIF
                    post = Post.objects.create(user=user, image=image_upload, is_gif=True, caption=caption)
                else:
                    # Es una imagen estándar
                    post = Post.objects.create(user=user, image=image_upload, caption=caption)

            # Asignar el perfil del usuario al post
            post.post_profile = Profile.objects.get(user=request.user)
            post.save()

        return redirect('/')
    else:
        return redirect('/')



@login_required(login_url='signin')
def delete_post(request, post_id=None):
    # Obtener el post usando el ID proporcionado
    post_to_delete = get_object_or_404(Post, id=post_id)
    if request.user.username == post_to_delete.user:
        post_to_delete.delete()
        return redirect('/')  # Ajusta 'home' al nombre de tu URL de inicio
    else:
        # Si el usuario no es el propietario del post, mostrar un mensaje de error o redirigir a otra página
        return redirect('/')

@login_required(login_url='signin')
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)
        
        username_profile_list = list(chain(*username_profile_list))

          # Detectar el tipo de dispositivo
    user_agent = get_user_agent(request)
    es_dispositivo_movil = user_agent.is_mobile

    if es_dispositivo_movil:
        template_name = 'mobile_search.html'
    else:
        template_name = 'search.html'

    return render(request, template_name, {'user_profile': user_profile, 'username_profile_list': username_profile_list})

def like_post(request):
    if request.method == 'POST' and is_ajax(request):
        post_id = request.POST.get('post_id')
        username = request.user.username

        post = get_object_or_404(Post, id=post_id)
        like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

        if like_filter is None:
            new_like = LikePost.objects.create(post_id=post_id, username=username)
            post.no_of_likes += 1
            post.save()
            return JsonResponse({'success': True, 'action': 'liked', 'likes': post.no_of_likes})
        else:
            like_filter.delete()
            post.no_of_likes -= 1
            post.save()
            return JsonResponse({'success': True, 'action': 'unliked', 'likes': post.no_of_likes})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)
    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Eliminar'
    else:
        button_text = 'Añadir'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    # Detectar el tipo de dispositivo
    user_agent = get_user_agent(request)
    es_dispositivo_movil = user_agent.is_mobile

    if es_dispositivo_movil:
        template_name = 'mobile_profile.html'
    else:
        template_name = 'profile.html'

    return render(request, template_name, context)

@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        try:
            # Get the value of 'follower' and 'user' from the POST request
            follower = request.POST.get('follower', None)
            user = request.POST.get('user', None)

            # Verify if 'follower' and 'user' are present in the POST request
            if follower is not None and user is not None:
                # Checks if the follower already follows the user
                if FollowersCount.objects.filter(follower=follower, user=user).first():
                    delete_follower = FollowersCount.objects.get(follower=follower, user=user)
                    delete_follower.delete()
                    return redirect('/profile/'+user)
                else:
                    # Create a new FollowersCount entry
                    new_follower = FollowersCount.objects.create(follower=follower, user=user)
                    new_follower.save()

                    # Gets the profile of the following user
                    follower_profile = Profile.objects.get(user__username=follower)

                    # Creates a notification using the following user profile
                    notification_text = f'{follower} te sigue.'
                    Notification.objects.create(user=User.objects.get(username=user), text=notification_text, timestamp=datetime.now(), follower_profile=follower_profile)
                    return redirect('/profile/'+user)
            else:
                # Return BadRequest error response if 'follower' or 'user' is not present in the POST request
                return JsonResponse({'status': 'error', 'message': "Missing 'follower' or 'user' in POST data"}, status=400)
        except Exception as e:
            # Returns an error JSON response with error details
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return redirect('/')

@login_required(login_url='signin')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        
        if request.FILES.get('image') == None:
            image = user_profile.profileimg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        
        return redirect('settings')
    return render(request, 'setting.html', {'user_profile': user_profile})

def signup(request):

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                #log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a Profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('/')
        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
        
    else:
        return render(request, 'signup.html')

def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid.')
            return redirect('signin')

    else:
        return render(request, 'signin.html')
    
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    notification.delete()
    return JsonResponse({'message': 'Notification deleted successfully'})

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')
