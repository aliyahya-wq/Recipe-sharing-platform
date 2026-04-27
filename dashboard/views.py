from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
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
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'اسم المستخدم موجود بالفعل.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني موجود بالفعل.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            if role == 'superuser':
                user.is_superuser = True
                user.is_staff = True
            elif role == 'staff':
                user.is_staff = True
            user.save()
            
            UserActivity.objects.create(
                user=request.user,
                action='staff_add',
                details=f'تم إضافة مشرف جديد: {username} بصلاحية {role}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, f'تم إضافة المشرف {username} بنجاح.')
            return redirect('dashboard:user_list')

    return render(request, 'dashboard/user_form.html', {'is_add': True})

@user_passes_test(is_admin, login_url='dashboard:login')
def edit_user(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'

        target_user.username = username
        target_user.email = email
        target_user.is_active = is_active

        if role == 'superuser':
            target_user.is_superuser = True
            target_user.is_staff = True
        elif role == 'staff':
            target_user.is_superuser = False
            target_user.is_staff = True
        else:
            target_user.is_superuser = False
            target_user.is_staff = False

        if password:
            target_user.set_password(password)

        target_user.save()
        
        UserActivity.objects.create(
            user=request.user,
            action='user_edit',
            details=f'تم تعديل بيانات المستخدم: {username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'تم تحديث بيانات {username} بنجاح.')
        return redirect('dashboard:user_list')

    return render(request, 'dashboard/user_form.html', {'is_add': False, 'target_user': target_user})

@user_passes_test(is_admin, login_url='dashboard:login')
def delete_user(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, 'لا يمكنك حذف حسابك الخاص!')
    else:
        target_user.delete() # Soft delete
        UserActivity.objects.create(
            user=request.user,
            action='user_delete',
            details=f'تم حذف المستخدم: {target_user.username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, f'تم نقل المستخدم {target_user.username} إلى سلة المحذوفات.')
    return redirect('dashboard:user_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def toggle_user_status(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user == request.user:
        messages.error(request, 'لا يمكنك تعطيل حسابك الخاص!')
    else:
        target_user.is_active = not target_user.is_active
        target_user.save()
        status = "تنشيط" if target_user.is_active else "تعطيل"
        UserActivity.objects.create(
            user=request.user,
            action='user_toggle',
            details=f'تم {status} حساب {target_user.username}',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        messages.success(request, f'تم {status} حساب {target_user.username} بنجاح.')
    return redirect('dashboard:user_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'dashboard/category_list.html', {'categories': categories})

@user_passes_test(is_admin, login_url='dashboard:login')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        icon = request.FILES.get('icon')
        if Category.objects.filter(name=name).exists():
            messages.error(request, 'هذا التصنيف موجود بالفعل.')
        else:
            Category.objects.create(name=name, icon=icon)
            UserActivity.objects.create(
                user=request.user,
                action='category_add',
                details=f'تم إضافة تصنيف جديد: {name}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f'تم إضافة التصنيف {name} بنجاح.')
            return redirect('dashboard:category_list')
    return render(request, 'dashboard/category_form.html')

@user_passes_test(is_admin, login_url='dashboard:login')
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete() # Soft delete
    UserActivity.objects.create(
        user=request.user,
        action='category_delete',
        details=f'تم حذف التصنيف: {category.name}',
        ip_address=request.META.get('REMOTE_ADDR')
    )
    messages.success(request, f'تم نقل التصنيف {category.name} إلى سلة المحذوفات.')
    return redirect('dashboard:category_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def recipe_list(request):
    recipes = Recipe.objects.all().order_by('-created_at')
    return render(request, 'dashboard/recipe_list.html', {'recipes': recipes})

@user_passes_test(is_admin, login_url='dashboard:login')
def edit_recipe(request, pk):
    # نستخدم نفس منطق التعديل من تطبيق recipes ولكن مع صلاحيات المدير
    from recipes.views import edit_recipe as original_edit_recipe
    return original_edit_recipe(request, pk)

@user_passes_test(is_admin, login_url='dashboard:login')
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    recipe.delete() # Soft delete
    messages.success(request, f'تم نقل الوصفة {recipe.title} إلى سلة المحذوفات.')
    return redirect('dashboard:recipe_list')

@user_passes_test(is_admin, login_url='dashboard:login')
def comment_list(request):
    comments = Comment.objects.all().order_by('-created_at')
    return render(request, 'dashboard/comment_list.html', {'comments': comments})

@user_passes_test(is_admin, login_url='dashboard:login')
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete() # Soft delete
    messages.success(request, 'تم حذف التعليق بنجاح.')
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
    model_map = {
        'user': User,
        'recipe': Recipe,
        'category': Category,
        'comment': Comment,
    }
    model = model_map.get(item_type)
    if model:
        item = get_object_or_404(model.all_objects, pk=pk)
        item.restore()
        messages.success(request, f'تم استعادة {item_type} بنجاح.')
    return redirect('dashboard:recycle_bin')

@user_passes_test(is_admin, login_url='dashboard:login')
def purge_item(request, item_type, pk):
    model_map = {
        'user': User,
        'recipe': Recipe,
        'category': Category,
        'comment': Comment,
    }
    model = model_map.get(item_type)
    if model:
        item = get_object_or_404(model.all_objects, pk=pk)
        item.hard_delete()
        messages.success(request, f'تم حذف {item_type} نهائياً من قاعدة البيانات.')
    return redirect('dashboard:recycle_bin')

@user_passes_test(is_admin, login_url='dashboard:login')
def activity_log(request):
    activities = UserActivity.objects.all().order_by('-timestamp')[:50]
    return render(request, 'dashboard/activity_log.html', {'activities': activities})
