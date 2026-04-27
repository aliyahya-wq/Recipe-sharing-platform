from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import User
from recipes.models import Recipe, Follow
from django.db.models import Count

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'تم إنشاء الحساب بنجاح! أنت الآن مسجل الدخول.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accountes/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'مرحباً بك مجدداً، {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة. يرجى المحاولة مرة أخرى.')
    return render(request, 'accountes/login.html')

@login_required
def profile(request):
    return user_profile(request, username=request.user.username)

@login_required
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    recipes = Recipe.objects.filter(author=profile_user).order_by('-created_at')
    recipe_count = recipes.count()
    followers_qs = Follow.objects.filter(following=profile_user).select_related('follower')
    following_qs = Follow.objects.filter(follower=profile_user).select_related('following')
    is_following = False
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    # الإحصائيات الجديدة
    from recipes.models import Like, Favorite
    total_likes_received = Like.objects.filter(recipe__author=profile_user).count()
    saved_recipes_count = Favorite.objects.filter(user=profile_user).count()
    liked_recipes_count = Like.objects.filter(user=profile_user).count()

    return render(request, 'accountes/profile.html', {
        'profile_user': profile_user,
        'recipes': recipes,
        'recipe_count': recipe_count,
        'is_own_profile': request.user == profile_user,
        'is_following': is_following,
        'followers': [follow.follower for follow in followers_qs],
        'following': [follow.following for follow in following_qs],
        'followers_count': followers_qs.count(),
        'following_count': following_qs.count(),
        'total_likes_received': total_likes_received,
        'saved_recipes_count': saved_recipes_count,
        'liked_recipes_count': liked_recipes_count,
    })

@login_required
def user_relations(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers_qs = Follow.objects.filter(following=profile_user).select_related('follower')
    following_qs = Follow.objects.filter(follower=profile_user).select_related('following')
    tab = request.GET.get('tab', 'all')
    return render(request, 'accountes/connections.html', {
        'profile_user': profile_user,
        'followers': [follow.follower for follow in followers_qs],
        'following': [follow.following for follow in following_qs],
        'followers_count': followers_qs.count(),
        'following_count': following_qs.count(),
        'tab': tab,
    })

@login_required
def toggle_follow(request, username):
    if request.method != 'POST':
        return redirect('user_profile', username=username)

    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return redirect('user_profile', username=username)

    follow_obj, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user
    )
    if created:
        messages.success(request, f'أنت الآن تتابع {target_user.username}.')
    else:
        follow_obj.delete()
        messages.success(request, f'تم إلغاء متابعة {target_user.username}.')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('user_relations', username=username)


def logout_view(request):
    logout(request)
    messages.info(request, 'لقد قمت بتسجيل الخروج بنجاح. نراك قريباً!')
    return redirect('home')

@login_required
def edit_profile(request):
    from .forms import CustomUserChangeForm
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات حسابك بنجاح!')
            return redirect('user_profile', username=request.user.username)
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'accountes/edit_profile.html', {'form': form})

def chef_list(request):
    chefs = User.objects.annotate(recipe_count=Count('recipes')).order_by('-recipe_count')
    return render(request, 'accountes/chefs.html', {'chefs': chefs})
