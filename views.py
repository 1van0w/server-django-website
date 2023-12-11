from django.shortcuts import render, redirect
from django.http import JsonResponse
import openai

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

openai_api_key = 'KEY'
openai.api_key = openai_api_key


def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Твоя личная нейросеть."},
            {"role": "user", "content": message},
        ]
    )

    answer = response.choices[0].message.content.strip()
    return answer


def chatbot(request):
    chats = Chat.objects.filter(user=request.user.id)

    if request.method == 'POST':
        message = request.POST.get('Сообщение')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'Сообщение': message, 'Ответ': response})
    return render(request, 'chat-gpt-bot.html', {'Чаты': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['Имя']
        password = request.POST['Пароль']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chat-gpt-bot')
        else:
            error_message = 'Неверное имя или пароль'
            return render(request, 'login.html', {'Ошибка': error_message})
    else:
        return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['Имя']
        email = request.POST['Почта']
        password1 = request.POST['Пароль-1']
        password2 = request.POST['Пароль-2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chat-gpt-bot')
            except:
                error_message = 'Произошла ошибка при создании аккаунта'
                return render(request, 'register.html', {'Ошибка': error_message})
        else:
            error_message = 'Пароль не совпадает'
            return render(request, 'register.html', {'Ошибка': error_message})
    return render(request, 'register.html')


def logout(request):
    auth.logout(request)
    return redirect('login')