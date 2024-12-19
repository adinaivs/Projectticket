from .models import CustomUser, Task, Token, Comment, Seat, TaskClassType
import uuid
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.views.generic.detail import DetailView
from django.utils.translation import gettext_lazy as _
from .forms import RegisterForm, CommentForm, ProfileForm
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.http import HttpResponse

from django.http import HttpResponse
from django.shortcuts import render

def payment_view(request):
    # Получаем ID выбранных мест из параметров URL
    seats = request.GET.get('seats', '')  # Параметр seats из URL
    total_price = request.GET.get('total_price', 0)  # Параметр total_price из URL

    if seats:
        seats_list = seats.split(',')
        # Преобразуем total_price в целое число, если это нужно
        try:
            total_price = float(total_price)  # Если нужно работать с числами с плавающей точкой
        except ValueError:
            total_price = 0  # Если преобразование не удалось, установим 0

        # Передаем выбранные места и сумму в шаблон
        return render(request, 'booking/payment.html', {'seats': seats_list, 'total_price': total_price})
    else:
        # Если места не указаны, возвращаем сообщение об ошибке
        return HttpResponse('Не выбраны места для оплаты.', status=400)

def payment_form_view(request):
    # Логика для обработки формы с картой
    if request.method == 'POST':
        card_number = request.POST.get('cardNumber')
        card_holder = request.POST.get('cardHolder')
        # Здесь можно добавить обработку данных карты
    return render(request, 'booking/payment_form.html')

def seat_pr(request, pk):
    # Получаем задачу по её ID (primary key)
    task = get_object_or_404(Task, pk=pk)

    # Получаем все классы для этой задачи
    task_class_types = TaskClassType.objects.filter(task=task)

    # Для каждого типа класса получаем все сиденья, связанные с ним
    seats = []
    for task_class_type in task_class_types:
        seats.extend(Seat.objects.filter(task_class_type=task_class_type))

    # Передаем данные в шаблон
    return render(request, 'booking/event_seats.html', {
        'task': task,
        'task_class_types': task_class_types,
        'seats': seats,
    })


@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully."))
            return redirect('profile')
    else:
        form = ProfileForm(instance=user)

    return render(request, 'app/profile.html', {'form': form, 'user': user})


def home(request):
    title = request.GET.get('title', '').strip()
    location = request.GET.get('location', '').strip()
    event_date = request.GET.get('event_date', '').strip()

    tasks = Task.objects.all()

    if title:
        tasks = tasks.filter(title__icontains=title)
    if location:
        tasks = tasks.filter(location__icontains=location)
    if event_date:
        tasks = tasks.filter(event_date__date=event_date)

    locations = Task.objects.values_list('location', flat=True).distinct()

    return render(request, 'app/index.html', {
        'tasks': tasks,
        'locations': locations,
        'title_label': _('Title'),
        'location_label': _('Location'),
        'date_label': _('Event Date'),
    })


class TaskDetailView(DetailView):
    model = Task
    template_name = 'app/task_detail.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.get_object()
        context['comments'] = Comment.objects.filter(task=task, is_published=True).order_by('-created_at')
        context['comment_form'] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        task = self.get_object()
        if not request.user.is_authenticated:
            messages.warning(request, _('You need to log in to post a comment.'))
            return redirect('task_detail', pk=task.pk)

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            messages.success(request, _('Comment added successfully.'))
            return redirect('task_detail', pk=task.pk)

        context = self.get_context_data(**kwargs)
        context['comment_form'] = form
        return self.render_to_response(context)


def toggle_comment_publish(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if not request.user.is_authenticated:
        messages.warning(request, _('You need to log in to modify a comment.'))
        return redirect('task_detail', pk=comment.task.pk)

    if comment.user == request.user or request.user.is_staff:
        comment.is_published = not comment.is_published
        comment.save()
        messages.success(request, _('Comment status updated.'))
    else:
        messages.error(request, _('You do not have permission to modify this comment.'))

    return redirect('task_detail', pk=comment.task.pk)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
        messages.success(request, _('Comment deleted successfully.'))
    else:
        messages.error(request, _('You do not have permission to delete this comment.'))

    return redirect('task_detail', pk=comment.task.pk)


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
            token = uuid.uuid4().hex
            expires_at = now() + timedelta(hours=24)
            Token.objects.create(token=token, user=user, expires_at=expires_at)

            confirm_link = self.request.build_absolute_uri(reverse_lazy("register_confirm", kwargs={"token": token}))
            message = _(f"Follow this link: {confirm_link} to confirm your registration.")
            send_mail(
                subject=_("Please confirm your registration!"),
                message=message,
                from_email="example@example.com",
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



