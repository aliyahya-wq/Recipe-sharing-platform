from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'experience_years')
        labels = {
            'bio': 'نبذة تعريفية عنك (Bio)',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'أخبرنا قليلاً عن شغفك بالطبخ...'}),
        }