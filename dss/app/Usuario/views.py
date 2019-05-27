# Django
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from rest_framework.renderers import JSONRenderer
# Modelos
from app.Usuario.models import Dolar

# Variables globales
data = {}

# Create your views here.
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

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
            return redirect('usuario:config_dolar', username=username)
        elif 'pib' in request.POST:
            print('pib')

@login_required
def config_dolar(request, username):    
    if request.method == 'GET':
        return render(request, 'configuracionesDolar.html')
    elif request.method == 'POST':
        k = request.POST['k']
        j = request.POST['j']
        alfa = request.POST['alfa']
        pse = request.POST['pse']
        m = request.POST['m']
        n = Dolar.objects.all().count()
        error = {}
        if int(k) < 0:
            error['kmenor0'] = 'K debe ser mayor a 0'
        if int(k) >= n:
            error['kmenorn'] = 'K debe ser menor a N - 1'
        if int(j) < 0:
            error['jmenor0'] = 'J debe ser mayor a 0'
        if int(j) >= (int(n) - int(k) - 1):
            error['jmenornk'] = 'J debe ser menor a (n - k - 1)'
        if float(alfa) < 0:
            error['alfamenor0'] = 'Alfa debe ser mayor o igual a 0'
        if float(alfa) > 1:
            error['alfamayor1'] = 'Alfa debe ser menor o igual a 1'
        
        if len(error) > 0:
            values = {
                'k': k,
                'j': j,
                'alfa': alfa,
                'pse': pse,
                'm': m
            }
            return render(request, 'configuracionesDolar.html', {'errores': error, 'value': values})
        else:
            global data

            values = {
                'k': k,
                'j': j,
                'alfa': alfa,
                'pse': pse,
                'm': m
            }
            dolar = Dolar.objects.all()
            periodos = []
            frecuencias = []
            for d in dolar:
                periodos.append(d.periodo)
                frecuencias.append(d.frecuencia)

            acumuladorPS = 0
            contador = 1
            ps = []
            for i in range(1, int(n)+1):
                acumuladorPS = acumuladorPS + (dolar[i - 1].frecuencia)
                ps.append(truncate((acumuladorPS / contador),5))
                contador += 1

            auxiliar = 0
            acumuladorPSM = 0
            pms = []
            for x in range(int(k)+1, int(n)+1):
                auxiliar = x
                for i in range(((auxiliar-int(k))-1), auxiliar-1):
                    acumuladorPSM = acumuladorPSM + (dolar[i].frecuencia)
                pms.append(truncate((acumuladorPSM/int(k)),5))
                acumuladorPSM = 0

            auxiliarPMD = 0
            acumuladorPMD = 0
            pmd = []
            for x in range(int(j)+1, len(pms)+2):
                auxiliarPMD = x
                for i in range(((auxiliarPMD-int(j))-1), auxiliarPMD-1):
                    acumuladorPMD = acumuladorPMD + (pms[i])
                pmd.append(truncate((acumuladorPMD/int(j)), 5))
                acumuladorPMD = 0
            
            auxiliarAs = int(j)
            As = []
            for x in range(1, len(pmd)):
                As.append(truncate(((2*pms[auxiliarAs])-pmd[x-1]),5))
                auxiliarAs += 1

            auxiliarBs = int(j)
            Bs = []
            for x in range(1, len(pmd)):
                Bs.append(truncate((((2*(abs(pms[auxiliarBs]-pmd[x-1]))))/(len(frecuencias)-1)),5))
                auxiliarBs += 1

            pmda = []
            for x in range(1, len(pmd)):
                pmda.append(truncate((As[x-1] + Bs[x-1] * int(m)), 5))

            tmac = []
            for x in range(1, len(frecuencias)):
                tmac.append(truncate((((frecuencias[x]/frecuencias[x-1])-1)*100),5))
            
            ptmac = []
            for x in range(1, len(frecuencias)):
                ptmac.append(truncate((float(frecuencias[x])+(float(frecuencias[x])*(tmac[x-1]/100))),5))
            
            psel = []
            for x in range(1, len(frecuencias)):
                psel.append(truncate((float(ps[x-1])+(float(alfa)*(float(frecuencias[x])-float(ps[x-1])))),5))

            # Insertar 0's al principio dependiendo de k y j
            for c in range(1):
                ps.insert(0,0)
            for c in range(0,int(k)):
                pms.insert(0,0) 
            for c in range(0,int(k)):
                pmd.insert(0,0)
            for c in range(0,int(j)):
                pmd.insert(0,0)
            for c in range(0,int(k)):
                As.insert(0,0)
            for c in range(0,int(j)):
                As.insert(0,0)
            for c in range(0,int(k)):
                Bs.insert(0,0)
            for c in range(0,int(j)):
                Bs.insert(0,0)
            for c in range(0,int(k)):
                pmda.insert(0,0)
            for c in range(0,int(j)):
                pmda.insert(0,0)
            for c in range(1):
                tmac.insert(0,0)
            for c in range(2):
                ptmac.insert(0,0)
            for c in range(2):
                psel.insert(0,0)

            zipped = zip(periodos, frecuencias, ps, pms, pmd, As, Bs, pmda, tmac, ptmac, psel)
            contexto = {
                'zipped': zipped,
                'values': values
            }
            data = {
                    'frecuencias': frecuencias,
                    'ps': ps,
                    'pms': pms,
                    'pmd': pmd,
                    'as': As,
                    'bs': Bs,
                    'pmda': pmda,
                    'tmac': tmac,
                    'ptmac': ptmac,
                    'psel': psel,
            }
            return render(request, 'tablasDolar.html', contexto)

@login_required
def grafica_dolar(request, username):
    return render(request, 'graficaDolar.html')

@csrf_exempt
def obtener_data(request):
    if request.method == 'GET':
        global data
        print(data)
        return JSONResponse(data, status=200)


@login_required
def calculos_pib(request, username):
    pass

@login_required
def logout_view(request):
    logout(request)
    return redirect('usuario:login')