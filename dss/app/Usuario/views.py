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
    if  request.method == 'GET':
        return render(request, 'variables.html')
    elif request.method == 'POST':
        if 'dolar' in request.POST:
            print('dolar')
        elif 'pib' in request.POST:
            print('pib')

@login_required
def calculos_dolar(request, username):
    pass

@login_required
def calculos_pib(request, username):
    pass

@login_required
def logout_view(request):
    logout(request)
    return redirect('usuario:login')