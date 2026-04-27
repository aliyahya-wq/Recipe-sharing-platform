from django.shortcuts import render, redirect
from django.contrib import messages
from recipes.models import ContactMessage, Recipe, Category, Favorite

def home(request):
    # جلب آخر 6 وصفات تمت إضافتها
    recent_recipes = Recipe.objects.all().order_by('-created_at')[:6]
    
    # جلب قائمة المفضلات والمتابعات للمستخدم الحالي
    favorite_ids = []
    following_ids = []
    if request.user.is_authenticated:
        favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('recipe_id', flat=True))
        from recipes.models import Follow
        following_ids = list(Follow.objects.filter(follower=request.user).values_list('following_id', flat=True))
    else:
        # تحويل القيم في الجلسة إلى أرقام (أو نصوص حسب طريقة التخزين) للتوافق
        guest_favs = request.session.get('guest_favorites', [])
        favorite_ids = [int(fid) if str(fid).isdigit() else fid for fid in guest_favs]

    # وسم كل وصفة إذا كانت في المفضلة أم لا
    for recipe in recent_recipes:
        recipe.is_favorited = recipe.id in favorite_ids or str(recipe.id) in [str(x) for x in favorite_ids]
    
    all_categories = Category.objects.all()
    total_recipes = Recipe.objects.count()
    
    return render(request, 'home.html', {
        'recipes': recent_recipes, 
        'total_recipes_count': total_recipes,
        'category_count': all_categories.count(),
        'all_categories': all_categories,
        'following_ids': following_ids
    })

def recipes(request):
    return render(request, 'recipes.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'تم إرسال رسالتك بنجاح! شكراً لتواصلك معنا.')
            return redirect('contact')
            
    return render(request, 'contact.html')