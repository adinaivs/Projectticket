from django.db.models.functions import datetime

from .models import CustomUser, Task, Token, Comment, Seat
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
from django.db.models import Q
from django.utils.translation import gettext as _

def event_booking(request, pk):
    task = get_object_or_404(Task, pk=pk)
    seats = Seat.objects.filter(task_class_type__task=task).select_related('task_class_type__class_type')
    class_types = task.task_class_types.all()
    filtered_seats = {class_type: seats.filter(task_class_type__class_type=class_type.class_type) for class_type in class_types}

    context = {
        "task": task,
        "seats": filtered_seats,
    }

    return render(request, "booking/event_booking.html", context)


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



