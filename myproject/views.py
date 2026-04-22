from django.shortcuts import render

def home(request):
    recipes = request.session.get('all_recipes', [])
    
    # قائمة التصنيفات الأساسية المتوفرة في الموقع
    base_categories = {'حلويات', 'أطباق رئيسية', 'عشاء', 'سلطات', 'مشروبات', 'مقبلات', 'فطور', 'غداء'}
    
    # إضافة أي تصنيفات جديدة قد يكون المستخدم أضافها في وصفاته
    user_categories = set(r.get('category').strip() for r in recipes if r.get('category'))
    
    # دمج المجموعتين لحساب الإجمالي
    total_categories = base_categories.union(user_categories)
    category_count = len(total_categories)
    
    return render(request, 'home.html', {
        'recipes': recipes, 
        'category_count': category_count
    })

def recipes(request):
    return render(request, 'recipes.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')