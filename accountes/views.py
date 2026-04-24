from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
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

def logout_view(request):
    logout(request)
    messages.info(request, 'لقد قمت بتسجيل الخروج بنجاح. نراك قريباً!')
    return redirect('home')
