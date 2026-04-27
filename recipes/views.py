import os
import uuid


from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recipe, Category, Ingredient, Step, Comment, Rating, Favorite, Like, Follow

# ─── views ────────────────────────────────────────────────────────────────────

def recipe_list(request):
    recipes = Recipe.objects.all()
    
    # التحقق من المفضلات
    favorite_ids = []
    following_ids = []
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('recipe_id', flat=True)
        following_ids = list(Follow.objects.filter(follower=request.user).values_list('following_id', flat=True))
    else:
        favorite_ids = request.session.get('guest_favorites', [])
    
    all_categories = Category.objects.all()
    
    return render(request, 'home.html', {
        'recipes': recipes,
        'favorite_ids': [str(id) for id in favorite_ids],
        'following_ids': following_ids,
        'all_categories': all_categories
    })

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    # التحقق مما إذا كانت الوصفة في المفضلة أو معجب بها
    is_favorite = False
    is_liked = False
    
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, recipe=recipe).exists()
        is_liked = Like.objects.filter(user=request.user, recipe=recipe).exists()
        is_following = Follow.objects.filter(follower=request.user, following=recipe.author).exists()
    else:
        # للزوار: التحقق من الجلسة
        guest_favs = request.session.get('guest_favorites', [])
        guest_likes = request.session.get('guest_likes', [])
        is_favorite = str(recipe.id) in guest_favs
        is_liked = str(recipe.id) in guest_likes
        is_following = False

    avg_rating = recipe.average_rating
    rating_count = Rating.objects.filter(recipe=recipe).count()
    comments = recipe.comments.filter(parent=None).order_by('-created_at')
    
    return render(request, 'recipes/recipe_new.html', {
        'recipe': recipe,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'is_favorite': is_favorite,
        'is_liked': is_liked,
        'comments': comments
    })

import re

@login_required
def recipe_add(request):
    if request.method == 'POST':
        def extract_number(text, default=0):
            if not text: return default
            nums = re.findall(r'\d+', str(text))
            return int(nums[0]) if nums else default

        title = request.POST.get('title') or request.POST.get('name')
        description = request.POST.get('description') or request.POST.get('summary')
        
        cook_time = extract_number(request.POST.get('cook_time') or request.POST.get('cooking_time'), 0)
        prep_time = extract_number(request.POST.get('prep_time'), 0)
        servings = extract_number(request.POST.get('servings'), 1)
        
        difficulty = request.POST.get('difficulty')
        category_id = request.POST.get('category')
        cuisine = request.POST.get('cuisine')
        image = request.FILES.get('image')

        try:
            # محاولة البحث كـ ID (رقم)
            cat_id = int(category_id)
            category = get_object_or_404(Category, id=cat_id)
        except (ValueError, TypeError):
            # إذا لم يكن رقماً (مثلاً نص مثل 'أطباق رئيسية')
            category = Category.objects.filter(name__icontains=category_id).first()
            if not category:
                # في أسوأ الحالات إذا لم يجد التصنيف بالاسم، نختار أول تصنيف متوفر حتى لا يظهر خطأ للمستخدم
                category = Category.objects.first()
        
        recipe = Recipe.objects.create(
            author=request.user,
            title=title,
            description=description,
            cook_time=cook_time,
            prep_time=prep_time,
            servings=servings,
            difficulty=difficulty,
            category=category,
            cuisine=cuisine,
            image=image
        )

        # إضافة المكونات
        names = request.POST.getlist('ingredient_name')
        amounts = request.POST.getlist('ingredient_amount')
        for n, a in zip(names, amounts):
            if n.strip():
                Ingredient.objects.create(recipe=recipe, name=n.strip(), quantity=a.strip())

        # إضافة الخطوات
        steps_raw = request.POST.get('instructions', '').strip().split('\n')
        for i, s in enumerate(steps_raw):
            if s.strip():
                Step.objects.create(recipe=recipe, order=i+1, description=s.strip())

        messages.success(request, 'تم إضافة الوصفة بنجاح! 🎉')
        return redirect('recipe_detail', recipe_id=recipe.id)

    categories = Category.objects.all()
    return render(request, 'recipes/recipe_add.html', {'categories': categories})

def recipe_result(request):
    """عرض الوصفة من الجلسة."""
    recipe = request.session.get('recipe_data')
    if not recipe:
        return redirect('recipe_add')
    return redirect('recipe_detail', recipe_id=recipe['id'])

def home(request):
    query = request.GET.get('q', '')
    recipes = Recipe.objects.filter(title__icontains=query)
    return render(request, 'recipes/recipes.html', {'recipes': recipes, 'query': query})

def add_comment(request, recipe_id):
    if request.method == 'POST' and request.user.is_authenticated:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        text = request.POST.get('comment')
        Comment.objects.create(user=request.user, recipe=recipe, text=text)
        messages.success(request, 'تم إضافة تعليقك!')
    return redirect('recipe_detail', recipe_id=recipe_id)

def add_reply(request, recipe_id, comment_id):
    if request.method == 'POST' and request.user.is_authenticated:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        parent_comment = get_object_or_404(Comment, id=comment_id)
        text = request.POST.get('reply')
        Comment.objects.create(user=request.user, recipe=recipe, text=text, parent=parent_comment)
        messages.success(request, 'تم إضافة ردك!')
    return redirect('recipe_detail', recipe_id=recipe_id)

def rate_recipe(request, recipe_id):
    if request.method == 'POST' and request.user.is_authenticated:
        recipe = get_object_or_404(Recipe, id=recipe_id)
        val = request.POST.get('rating')
        if val:
            Rating.objects.update_or_create(
                user=request.user, recipe=recipe,
                defaults={'score': int(val)}
            )
            messages.success(request, 'شكراً لتقييمك!')
    return redirect('recipe_detail', recipe_id=recipe_id)

def toggle_favorite(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.user.is_authenticated:
        favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
        if not created:
            favorite.delete()
            messages.info(request, 'تم إزالة الوصفة من المحفوظات.')
        else:
            messages.success(request, 'تم حفظ الوصفة في المفضلات! 🔖')
    else:
        # للزوار: استخدام الجلسة
        guest_favs = request.session.get('guest_favorites', [])
        recipe_id_str = str(recipe.id)
        
        if recipe_id_str in guest_favs:
            guest_favs.remove(recipe_id_str)
            messages.info(request, 'تم إزالة الوصفة من المحفوظات.')
        else:
            guest_favs.append(recipe_id_str)
            messages.success(request, 'تم حفظ الوصفة في المفضلات! 🔖')
        
        request.session['guest_favorites'] = guest_favs
        request.session.modified = True
        
    return redirect('recipe_detail', recipe_id=recipe_id)

def toggle_like(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    if request.user.is_authenticated:
        like, created = Like.objects.get_or_create(user=request.user, recipe=recipe)
        if not created:
            like.delete()
            messages.info(request, 'تم إزالة الإعجاب.')
        else:
            messages.success(request, 'تم إضافة الإعجاب! ❤️')
    else:
        # للزوار: استخدام الجلسة
        guest_likes = request.session.get('guest_likes', [])
        recipe_id_str = str(recipe.id)
        
        if recipe_id_str in guest_likes:
            guest_likes.remove(recipe_id_str)
            messages.info(request, 'تم إزالة الإعجاب.')
        else:
            guest_likes.append(recipe_id_str)
            messages.success(request, 'تم إضافة الإعجاب! ❤️')
        
        request.session['guest_likes'] = guest_likes
        request.session.modified = True
        
    return redirect('recipe_detail', recipe_id=recipe_id)

def favorites_list(request):
    if request.user.is_authenticated:
        favorites = Favorite.objects.filter(user=request.user)
        recipes = [f.recipe for f in favorites]
    else:
        guest_favs = request.session.get('guest_favorites', [])
        recipes = Recipe.objects.filter(id__in=guest_favs)
        
    return render(request, 'recipes/recipes.html', {
        'recipes': recipes,
        'title': '🔖 وصفاتي المحفوظة'
    })

def user_liked_recipes(request):
    if request.user.is_authenticated:
        likes = Like.objects.filter(user=request.user)
        recipes = [like.recipe for like in likes]
    else:
        guest_likes = request.session.get('guest_likes', [])
        recipes = Recipe.objects.filter(id__in=guest_likes)
        
    return render(request, 'recipes/recipes.html', {
        'recipes': recipes,
        'title': '❤️ وصفات أعجبتني'
    })

@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if request.method == 'POST':
        # Same logic as recipe_add could be used, or just a model form
        recipe.title = request.POST.get('title') or request.POST.get('recipe_name', '')
        recipe.description = request.POST.get('description', '')
        # Handle category
        cat_id_or_name = request.POST.get('category_id') or request.POST.get('category', '')
        if cat_id_or_name:
            if str(cat_id_or_name).isdigit():
                category = Category.objects.filter(id=int(cat_id_or_name)).first()
            else:
                category, _ = Category.objects.get_or_create(name=cat_id_or_name)
            if category:
                recipe.category = category
        # Parse numbers
        import re
        def extract_number(val):
            if val:
                nums = re.findall(r'\d+', str(val))
                if nums:
                    return int(nums[0])
            return 0
        recipe.prep_time = extract_number(request.POST.get('prep_time') or request.POST.get('preparation_time'))
        recipe.cook_time = extract_number(request.POST.get('cook_time'))
        recipe.servings = extract_number(request.POST.get('servings'))
        
        if 'image' in request.FILES:
            recipe.image = request.FILES['image']
            
        recipe.save()

        # تحديث المكونات (حذف القديم وإضافة الجديد)
        recipe.ingredients.all().delete()
        names = request.POST.getlist('ingredient_name')
        amounts = request.POST.getlist('ingredient_amount')
        for n, a in zip(names, amounts):
            if n.strip():
                Ingredient.objects.create(recipe=recipe, name=n.strip(), quantity=a.strip())

        # تحديث الخطوات (حذف القديم وإضافة الجديد)
        recipe.steps.all().delete()
        steps_raw = request.POST.get('instructions', '').strip().split('\n')
        for i, s in enumerate(steps_raw):
            if s.strip():
                Step.objects.create(recipe=recipe, order=i+1, description=s.strip())

        messages.success(request, 'تم تعديل الوصفة بنجاح!')
        return redirect('recipe_detail', recipe_id=recipe.id)
    
    categories = Category.objects.all()
    return render(request, 'recipes/recipe_add.html', {'categories': categories, 'recipe': recipe})

@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'تم حذف الوصفة بنجاح.')
        return redirect('user_profile', username=request.user.username)
    return render(request, 'recipes/delete_recipe_confirm.html', {'recipe': recipe})

def admin_home(request):
    return render(request, 'baes.html')
