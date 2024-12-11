from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import RegisterView, user_login, TaskDetailView
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = [
    path('', views.index, name='home'),

    path('admin/', admin.site.urls),

    path('task/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('comment/<int:pk>/toggle/', views.toggle_comment_publish, name='comment_toggle_publish'),
    path('comment/delete/<int:pk>/', views.delete_comment, name='delete_comment'),

    path('login', user_login, name="login"),
    path('signup', RegisterView.as_view(), name="signup"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/confirm/<str:token>/', views.register_confirm, name='register_confirm'),  # Добавьте эту строку

    path('about/', views.about, name='about'),  # Исправлено: изменен путь на '/about/'
]

# Обработка медиафайлов
if settings.DEBUG:  # Только в режиме разработки
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
