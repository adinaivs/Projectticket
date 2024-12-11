from .models import CustomUser, Task, Token, Comment
import uuid
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.generic.detail import DetailView
from django.utils.translation import gettext_lazy as _
from .forms import RegisterForm, CommentForm
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Q

def index(request):
    query = request.GET.get('q')  # Получение строки поиска
    location_filter = request.GET.get('location')  # Фильтр по месту проведения

    # Фильтрация мероприятий
    tasks = Task.objects.all()
    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(task__icontains=query))
    if location_filter:
        tasks = tasks.filter(location__icontains=location_filter)

    tasks = tasks.order_by('-id')

    return render(request, 'app/index.html', {
        'title': 'Главная страница сайта',
        'tasks': tasks,
        'query': query,
        'location_filter': location_filter,
    })

class TaskDetailView(DetailView):
    model = Task
    template_name = 'app/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()

        # Получаем все опубликованные комментарии, отсортированные по дате
        context['comments'] = Comment.objects.filter(task=task, is_published=True).order_by('-created_at')

        # Добавляем форму для добавления комментария
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()

        # Проверка, авторизован ли пользователь
        if not request.user.is_authenticated:
            messages.warning(request, _('Вы не авторизованы. Чтобы добавить комментарий, нужно войти в систему.'))
            return redirect('task_detail', pk=task.pk)

        # Проверяем, что форма прошла валидацию
        form = CommentForm(request.POST)
        if form.is_valid():
            # Если форма валидна, сохраняем новый комментарий
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user  # Привязываем комментарий к текущему пользователю
            comment.save()

            # Перенаправляем на ту же страницу, чтобы отобразить новый комментарий
            return redirect('task_detail', pk=task.pk)

        # Если форма невалидна, возвращаем тот же шаблон с ошибками
        context = self.get_context_data(**kwargs)
        context['comment_form'] = form
        return self.render_to_response(context)


# Функция для переключения публикации комментария
def toggle_comment_publish(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # Проверяем, что текущий пользователь — автор комментария или администратор
    if not request.user.is_authenticated:
        messages.warning(request, _('Вы не авторизованы. Для изменения комментария необходимо войти в систему.'))
        return redirect('task_detail', pk=comment.task.pk)

    if comment.user == request.user or request.user.is_staff:
        comment.is_published = not comment.is_published
        comment.save()
        messages.success(request, _('Комментарий обновлен.'))
    else:
        messages.error(request, _('У вас нет прав для изменения этого комментария.'))

    return redirect('task_detail', pk=comment.task.pk)

@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    # Проверяем, что пользователь может удалить комментарий
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
        messages.success(request, _('Комментарий был удалён.'))
    else:
        messages.error(request, _('У вас нет прав для удаления этого комментария.'))

    return redirect('task_detail', pk=comment.task.pk)

def index(request):
    # Получаем поисковый запрос из строки запроса
    query = request.GET.get('q', '')  # 'q' - это имя поля в форме поиска
    if query:
        # Выполняем фильтрацию задач по названию или описанию
        tasks = Task.objects.filter(
            Q(title__icontains=query) | Q(task__icontains=query)
        ).order_by('-id')
    else:
        # Если поисковый запрос не указан, выводим все задачи
        tasks = Task.objects.order_by('-id')

    # Передаём данные в шаблон
    return render(request, 'app/index.html', {
        'title': 'Главная страница сайта',
        'tasks': tasks,
        'query': query,  # Передаём запрос для отображения в форме
    })


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

# The about function is excluded as per your instructions


# Теперь метод about должен быть вне класса TaskDetailView
def about(request):
    return render(request, 'app/about.html')

