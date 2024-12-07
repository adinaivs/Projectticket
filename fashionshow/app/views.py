import secrets
import string
import uuid

from django.conf import settings
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView

from .models import CustomUser, Task, Token
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.generic.detail import DetailView
from django.utils.translation import gettext_lazy as _
from .forms import RegisterForm
from django.utils.timezone import now
from datetime import timedelta

def index(request):
    tasks = Task.objects.order_by('-id')
    return render(request, 'app/index.html', {'title': 'Главная страница сайта', 'tasks': tasks})


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]

        user, created = CustomUser.objects.get_or_create(email=email)
        if created:
            user.set_password(password)
            user.is_active = False
            user.save()

            # Генерация токена
            token = uuid.uuid4().hex
            expires_at = now() + timedelta(hours=24)  # Токен действует 24 часа
            Token.objects.create(token=token, user=user, expires_at=expires_at)

            # Ссылка для подтверждения
            confirm_link = self.request.build_absolute_uri(
                reverse_lazy("register_confirm", kwargs={"token": token})
            )

            # Отправка письма
            message = _(f"Follow this link: {confirm_link} to confirm your registration.")
            send_mail(
                subject=_("Please confirm your registration!"),
                message=message,
                from_email="amanbaevaadinaj676@gmail.com",
                recipient_list=[user.email],
            )
            messages.success(self.request, _("A confirmation email has been sent to your email address."))
        else:
            if not user.is_active:
                messages.warning(self.request, _("This email is registered but not confirmed. Please check your email."))
                return redirect("login")
            else:
                form.add_error("email", _("This email is already registered."))

        return super().form_valid(form)

def register_confirm(request, token):
    try:
        # Попытка получить токен из базы данных
        token_entry = Token.objects.get(token=token, expires_at__gt=now())

        # Если токен найден и не истек
        user = token_entry.user
        user.is_active = True  # Активируем пользователя
        user.save()

        # Удаляем токен после использования
        token_entry.delete()

        messages.success(request, _("Your account has been successfully activated."))
        return redirect(to=reverse_lazy("home"))
    except Token.DoesNotExist:
        messages.error(request, _("Invalid or expired token."))
        return redirect(to=reverse_lazy("signup"))



def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, _("Successfully logged in."))
                return redirect('home')
            else:
                messages.warning(request, _("Your account is not activated. Please check your email to confirm your registration."))
                return redirect('login')
        else:
            messages.warning(request, _("Incorrect username or password."))

    return render(request, 'registration/login.html')


class TaskDetailView(DetailView):
    model = Task
    template_name = 'app/task_detail.html'
    context_object_name = 'task'