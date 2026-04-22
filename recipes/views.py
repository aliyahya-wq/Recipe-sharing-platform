import base64
import os
import uuid

from django.conf import settings
from django.shortcuts import render, redirect


# ─── helpers ──────────────────────────────────────────────────────────────────

def _save_image(image_file):
    """حفظ الصورة في MEDIA_ROOT وإرجاع المسار النسبي (للعرض)."""
    if not image_file:
        return None
    ext = os.path.splitext(image_file.name)[-1].lower()
    filename = f"{uuid.uuid4().hex}{ext}"
    media_dir = os.path.join(settings.MEDIA_ROOT, 'recipe_images')
    os.makedirs(media_dir, exist_ok=True)
    path = os.path.join(media_dir, filename)
    with open(path, 'wb+') as f:
        for chunk in image_file.chunks():
            f.write(chunk)
    return f"/media/recipe_images/{filename}"


def _build_recipe(request):
    """بناء قاموس الوصفة من POST + ملف الصورة."""
    names   = request.POST.getlist('ingredient_name')
    amounts = request.POST.getlist('ingredient_amount')
    ingredients = [
        {'name': n.strip(), 'amount': a.strip()}
        for n, a in zip(names, amounts)
        if n.strip()
    ]

    steps_raw = request.POST.get('instructions', '').strip().split('\n')
    steps = [s.strip() for s in steps_raw if s.strip()]

    image_url = _save_image(request.FILES.get('image'))

    from datetime import datetime
    now = datetime.now()
    created_at = now.strftime("%Y/%m/%d - %H:%M")

    return {
        'id':           uuid.uuid4().hex[:8],
        'name':         request.POST.get('name', '').strip(),
        'summary':      request.POST.get('summary', '').strip(),
        'category':     request.POST.get('category', '').strip(),
        'cooking_time': request.POST.get('cooking_time', '').strip(),
        'prep_time':    request.POST.get('prep_time', '').strip(),
        'servings':     request.POST.get('servings', '').strip(),
        'difficulty':   request.POST.get('difficulty', 'متوسط'),
        'ingredients':  ingredients,
        'instructions': steps,
        'show_table':   True,
        'comments':     [],
        'image':        image_url,
        'created_at':   created_at,
    }


# ─── views ────────────────────────────────────────────────────────────────────

def recipe_list(request):
    all_recipes = request.session.get('all_recipes', [])
    return render(request, 'recipes/recipes.html', {'recipes': all_recipes})


def recipe_detail(request, recipe_id):
    all_recipes = request.session.get('all_recipes', [])
    # البحث عن الوصفة المطلوبة
    recipe = next((r for r in all_recipes if r['id'] == recipe_id), None)
    
    if not recipe:
        # إذا لم يجدها في الكل، ربما هي الوصفة الافتراضية للتعمية
        recipe = {
            'id': 'default',
            'name': 'وصفة الدجاج بالكاري',
            'summary': 'وصفة شهية للدجاج بالكاري مع الأرز، مثالية للعائلة.',
            'category': 'غداء',
            'ingredients': [
                {'name': 'دجاج',         'amount': '500 جرام'},
                {'name': 'كاري مسحوق',  'amount': '2 ملعقة كبيرة'},
                {'name': 'بصل',          'amount': '1 حبة'},
                {'name': 'ثوم',          'amount': '2 فص'},
                {'name': 'زيت',          'amount': '3 ملعقة كبيرة'},
            ],
            'instructions': ['سخن الزيت', 'أضف البصل والثوم ثم الدجاج والكاري', 'اطبخ لمدة 30 دقيقة'],
            'cooking_time': '45 دقيقة',
            'prep_time': '15 دقيقة',
            'servings': '4 أشخاص',
            'difficulty': 'متوسط',
            'show_table': True,
            'image': None,
            'comments': [
                {'user': 'أحمد', 'avatar': 'أ', 'text': 'رائعة جداً!', 'date': 'منذ يوم',
                 'replies': [{'user': 'فاطمة', 'avatar': 'ف', 'text': 'شكراً!', 'date': 'منذ ساعة'}]},
                {'user': 'سارة', 'avatar': 'س', 'text': 'أحببتها.', 'date': 'منذ يومين', 'replies': []},
            ],
        }
    if recipe:
        favorites = request.session.get('favorites', [])
        recipe['is_favorite'] = recipe['id'] in favorites
    return render(request, 'recipes/recipe_new.html', {'recipe': recipe})


def add_comment(request, recipe_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment', '').strip()
        if comment_text:
            all_recipes = request.session.get('all_recipes', [])
            for r in all_recipes:
                if r['id'] == recipe_id:
                    if 'comments' not in r:
                        r['comments'] = []
                    r['comments'].append({
                        'user': 'زائر',
                        'avatar': 'ز',
                        'text': comment_text,
                        'date': 'الآن',
                        'replies': []
                    })
                    break
            request.session['all_recipes'] = all_recipes
            request.session.modified = True
            
            # تحديث recipe_data أيضاً إذا كانت هي نفس الوصفة
            recipe_data = request.session.get('recipe_data')
            if recipe_data and recipe_data['id'] == recipe_id:
                if 'comments' not in recipe_data:
                    recipe_data['comments'] = []
                recipe_data['comments'].append({
                    'user': 'زائر',
                    'avatar': 'ز',
                    'text': comment_text,
                    'date': 'الآن',
                    'replies': []
                })
                request.session['recipe_data'] = recipe_data

    return redirect('recipe_detail', recipe_id=recipe_id)


def add_reply(request, recipe_id, comment_index):
    if request.method == 'POST':
        reply_text = request.POST.get('reply', '').strip()
        if reply_text:
            all_recipes = request.session.get('all_recipes', [])
            for r in all_recipes:
                if r['id'] == recipe_id:
                    if 'comments' in r and len(r['comments']) > comment_index:
                        r['comments'][comment_index]['replies'].append({
                            'user': 'زائر',
                            'avatar': 'ز',
                            'text': reply_text,
                            'date': 'الآن'
                        })
                    break
            request.session['all_recipes'] = all_recipes
            request.session.modified = True
    return redirect('recipe_detail', recipe_id=recipe_id)


def rate_recipe(request, recipe_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        if rating:
            all_recipes = request.session.get('all_recipes', [])
            for r in all_recipes:
                if r['id'] == recipe_id:
                    r['user_rating'] = int(rating)
                    break
            request.session['all_recipes'] = all_recipes
            request.session.modified = True
    return redirect('recipe_detail', recipe_id=recipe_id)


def toggle_favorite(request, recipe_id):
    favorites = request.session.get('favorites', [])
    if recipe_id in favorites:
        favorites.remove(recipe_id)
    else:
        favorites.append(recipe_id)
    request.session['favorites'] = favorites
    request.session.modified = True
    return redirect('recipe_detail', recipe_id=recipe_id)


def favorites_list(request):
    favorites = request.session.get('favorites', [])
    all_recipes = request.session.get('all_recipes', [])
    favorite_recipes = [r for r in all_recipes if r['id'] in favorites]
    return render(request, 'recipes/recipes.html', {
        'recipes': favorite_recipes, 
        'is_favorites_page': True,
        'page_title': 'وصفاتي المفضلة'
    })


def recipe_add(request):
    """صفحة نموذج إدخال الوصفة."""
    if request.method == 'POST':
        recipe = _build_recipe(request)

        # حفظ الوصفة الحالية في الجلسة
        request.session['recipe_data'] = recipe

        # إضافة الوصفة لقائمة الكل (للصفحة الرئيسية)
        all_recipes = request.session.get('all_recipes', [])
        all_recipes.insert(0, recipe)  # حفظ الوصفة كاملة
        request.session['all_recipes'] = all_recipes
        request.session.modified = True

        return redirect('recipe_result')

    return render(request, 'recipes/recipe_add.html')


def recipe_result(request):
    """عرض الوصفة من الجلسة."""
    recipe = request.session.get('recipe_data')
    if not recipe:
        return redirect('recipe_add')
    return redirect('recipe_detail', recipe_id=recipe['id'])
