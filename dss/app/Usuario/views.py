# Django
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.
def login_sistema(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('usuario:variables', username=username)
        else:
            return render(request, 'index.html', {'error': 'Usuario o contraseña incorrectos.'})

@login_required
def variables_view(request, username):
    return render(request, 'variables.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('usuario:login')