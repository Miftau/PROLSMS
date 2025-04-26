"""
URL configuration for django_progress_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from lsms.views import index_view, signup_view, activate_account

from . import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),

    # Django’s built-in auth (login, logout, password reset, etc.)
    path('', include('django.contrib.auth.urls')),

    # custom signup
    path('accounts/signup/', signup_view, name='signup'),
    path(
        'activate/<uidb64>/<token>/',
        activate_account,
        name='activate'
    ),

    # API and frontend routes
    path('api/', include('lsms.api_urls')),
    path('', index_view, name='index'),
    path('', include('lsms.urls')),
    
    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
