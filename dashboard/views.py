from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from accountes.models import User, UserActivity
from recipes.models import Recipe, Category, Comment
import json

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin, login_url='dashboard:login')
def home(request):
    total_users = User.objects.count()
    total_recipes = Recipe.objects.count()
    total_comments = Comment.objects.count()

    popular_recipes = Recipe.objects.annotate(total_likes=Count('likes')).order_by('-total_likes')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]

    categories = Category.objects.annotate(recipe_count=Count('recipes'))
    category_labels = [c.name for c in categories]
    category_data = [c.recipe_count for c in categories]

    stats = {
        'total_users': total_users,
        'total_recipes': total_recipes,
        'total_comments': total_comments,
        'popular_recipes': popular_recipes,
        'recent_users': recent_users,
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
    }

    return render(request, 'dashboard/home.html', {'stats': stats})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    return redirect('dashboard:home')
                else:
                    return render(request, 'dashboard/login.html', {'error': 'عذراً، ليس لديك صلاحية الدخول كمدير.'})
            else:
                return render(request, 'dashboard/login.html', {'error': 'البريد الإلكتروني أو كلمة المرور غير صحيحة.'})
        except User.DoesNotExist:
            return render(request, 'dashboard/login.html', {'error': 'لا يوجد حساب مرتبط بهذا البريد الإلكتروني.'})
    return render(request, 'dashboard/login.html')

def logout_view(request):
    logout(request)
    return redirect('dashboard:login')

@user_passes_test(is_admin, login_url='dashboard:login')
def user_list(request):
    staff_users = User.objects.filter(is_staff=True).order_by('-date_joined')
    regular_users = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, 'dashboard/user_list.html', {
        'staff_users': staff_users,
        'regular_users': regular_users
    })

@user_passes_test(is_admin, login_url='dashboard:login')
def user_detail(request, pk):
    user = User.objects.get(pk=pk)
    return render(request, 'dashboard/user_detail.html', {'target_user': user})

@user_passes_test(is_admin, login_url='dashboard:login')
def add_staff_user(request):
    return redirect('dashboard:user_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def edit_user(request, pk):
    return redirect('dashboard:user_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def delete_user(request, pk):
    return redirect('dashboard:user_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def toggle_user_status(request, pk):
    return redirect('dashboard:user_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})

@user_passes_test(is_admin, login_url='dashboard:login')
def add_category(request):
    return redirect('dashboard:category_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def delete_category(request, pk):
    return redirect('dashboard:category_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def recipe_list(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    return render(request, 'dashboard/recipe_list.html', {'recipes': recipes})

@user_passes_test(is_admin, login_url='dashboard:login')
def edit_recipe(request, pk):
    return redirect('dashboard:recipe_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def delete_recipe(request, pk):
    return redirect('dashboard:recipe_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def comment_list(request):
    comments = Comment.objects.all().order_by('-created_at')
    return render(request, 'dashboard/comment_list.html', {'comments': comments})

@user_passes_test(is_admin, login_url='dashboard:login')
def delete_comment(request, pk):
    return redirect('dashboard:comment_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def reports(request):
    return render(request, 'dashboard/reports.html')

@user_passes_test(is_admin, login_url='dashboard:login')
def recycle_bin(request):
    deleted_users = User.objects.filter(is_deleted=True)
    deleted_recipes = Recipe.objects.filter(is_deleted=True)
    return render(request, 'dashboard/recycle_bin.html', {'deleted_users': deleted_users, 'deleted_recipes': deleted_recipes})

@user_passes_test(is_admin, login_url='dashboard:login')
def restore_item(request, item_type, pk):
    return redirect('dashboard:recycle_bin')

@user_passes_test(is_admin, login_url='dashboard:login')
def purge_item(request, item_type, pk):
    return redirect('dashboard:recycle_bin')

@user_passes_test(is_admin, login_url='dashboard:login')
def activity_log(request):
    activities = UserActivity.objects.all().order_by('-timestamp')[:50]
    return render(request, 'dashboard/activity_log.html', {'activities': activities})
