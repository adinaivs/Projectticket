from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import RegisterView, user_login, TaskDetailView, profile_view, seat_pr
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),

    path('task/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('comment/<int:pk>/toggle/', views.toggle_comment_publish, name='comment_toggle_publish'),
    path('comment/delete/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('task/<int:pk>/seats/', seat_pr, name='seat_pr'),

    path('profile/', profile_view, name='profile'),
    path('about/', views.about, name='about'),  # Исправлено: изменен путь на '/about/'

    path('login', user_login, name="login"),
    path('signup', RegisterView.as_view(), name="signup"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/confirm/<str:token>/', views.register_confirm, name='register_confirm'),  # Добавьте эту строку
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'), name='password_reset'),
    path('reset-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('payment/', views.payment_view, name='payment'),
    path('payment/form/', views.payment_form_view, name='payment_form'),

]

# Обработка медиафайлов
if settings.DEBUG:  # Только в режиме разработки
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
