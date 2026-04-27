from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'profile_picture', 'first_name', 'last_name', 'bio', 'experience_years')
        labels = {
            'bio': 'نبذة تعريفية عنك (Bio)',
            'profile_picture': 'الصورة الشخصية (اختياري)',
            'experience_years': 'مدة الخبرة (مثلاً: سنتين، 6 أشهر)',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'أخبرنا قليلاً عن شغفك بالطبخ...'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
            'experience_years': forms.TextInput(attrs={'placeholder': 'مثلاً: سنتين أو 6 أشهر'}),
        }

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'profile_picture', 'bio', 'experience_years')
        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
            'bio': 'نبذة تعريفية عنك (Bio)',
            'profile_picture': 'تحديث الصورة الشخصية',
            'experience_years': 'مدة الخبرة (مثلاً: سنتين، 6 أشهر)',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'تحديث نبذتك...'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
            'experience_years': forms.TextInput(attrs={'placeholder': 'مثلاً: سنتين أو 6 أشهر'}),
        }