from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import RegisterView  
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='/'), name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('signup/', RegisterView.as_view(), name='users-register'), 


    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)