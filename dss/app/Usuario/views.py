# Django
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Modelos
from app.Usuario.models import Dolar

# Variables globales
dataP = {}
dataD = {}

import math
from operator import itemgetter

# models
from app.Usuario.models import PIB


# Create your views here.

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
            return redirect('usuario:pib', username=username)

@login_required
def config_dolar(request, username):    
    if request.method == 'GET':
        return render(request, 'configuracionesDolar.html')
    elif request.method == 'POST':
        k = request.POST['k']
        j = request.POST['j']
        alfa = request.POST['alfa']
        opcion = request.POST['pse']
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
                'pse': opcion,
                'm': m
            }
            return render(request, 'configuracionesDolar.html', {'errores': error, 'value': values})
        else:
            global dataD

            values = {
                'k': k,
                'j': j,
                'alfa': alfa,
                'pse': opcion,
                'm': m
            }
            dolar = Dolar.objects.all()
            periodos = []
            frecuencias = []
            for d in dolar:
                periodos.append(d.periodo)
                frecuencias.append(float(d.frecuencia))

            acumuladorPS = 0
            contador = 1
            ps = []
            k = int(k)
            j = int(j)
            m = int(m)
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
            if opcion == "ps":
                for x in range(1,len(frecuencias)):
                    res = float(ps[x])+(float(alfa)*(float(frecuencias[x]) - float(ps[x])))
                    psel.append(truncate(res,5))

                for c in range(2):
                    psel.insert(0,0)
                    
            if opcion == "pmd":
                for x in range(k+j,len(frecuencias)):
                    psel.append(truncate(float(pmd[x-k-j])+(float(alfa)*(float(frecuencias[x]) - float(pmd[x-k-j]))),5))
                for c in range(j+k+1):
                    psel.insert(0,0)
            if opcion == "pms":
                for x in range(k,len(frecuencias)):
                    psel.append(truncate(float(pms[x-k])+(float(alfa)*(float(frecuencias[x]) - float(pms[x-k]))),5))
                for c in range(k+1):
                    psel.insert(0,0)
            if opcion == "pmda":
                for x in range(k+j,len(frecuencias)):
                    psel.append(truncate(float(pmda[x-k-j])+(float(alfa)*(float(frecuencias[x]) - float(pmda[x-k-j]))),5))
                for c in range(j+k+1):
                    psel.insert(0,0)
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

            zipped = zip(periodos, frecuencias, ps, pms, pmd, As, Bs, pmda, tmac, ptmac, psel)
            contexto = {
                'zipped': zipped,
                'values': values
            }
            dataD = {
                    'p': periodos,
                    'f': frecuencias,
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
    messages.success(request, 'ok')
    global dataD
    return render(request, 'graficaDolar.html',dataD)


@login_required
def calculos_pib(request, username):
    if request.method == 'GET':
        messages.success(request, 'ok')
        global dataP
        return render(request,'grafica.html', dataP)


@login_required
def configuraciones_pib(request,username):
    if request.method == 'GET':
        return render(request, 'configuraciones.html')
    elif request.method == 'POST':
        if 'pib' in request.POST:
            pib = PIB.objects.all()
            n = len(pib) - 1 
            k = int(request.POST['k'])
            print(k)
            j = int(request.POST['j'])
            opcion = request.POST['pse']
            print(opcion)
            alpha = float(request.POST['alpha'])
            m = int(request.POST['m'])
            if k > 0 & k < n:
                o = len(pib) - k - 1
                if j > 0 & j < o:
                    if 1==1:
                        aps = 0
                        apms = 0
                        apmd = 0
                        vi = 0
                        vf = 0
                        tmac = []
                        a = 0
                        b = 0
                        p = []
                        f = []
                        ps= []
                        eps= []
                        pms = []
                        epms=[]
                        pmd = []
                        epmd = []
                        pmda=[]
                        epmda=[]
                        ptmac=[]
                        As = []
                        Bs = []
                        epsel=[]
                        psel=[]
                        aeps = 0
                        aepms = 0
                        aepmd = 0
                        aepmda = 0
                        aepsel = 0
                        ps.append(0)
                        eps.append(0)
                        for x in range (1,len(pib)):    
                            aps = aps + pib[x-1].frecuencia
                            res = float(aps)/x
                            resta = abs(float(pib[x].frecuencia)-res)
                            eps.append(truncate(resta,5))
                            ps.append(truncate(res,5))
                        for x in range(1, len(eps)-1):
                            aeps = aeps + eps[x]
                        aeps = aeps/(len(eps)-2)
                        for x in range(k+1,len(pib)+1):
                            y = x 
                            for i in range(((y-k)-1),y-1):
                                apms = apms + pib[i].frecuencia
                            res = float(apms)/k
                            resta = abs(float(pib[x-1].frecuencia)-res)
                            pms.append(truncate(res,5))
                            epms.append(truncate(resta,5))
                            apms =0
                        for x in range(0, len(epms)-1):
                            aepms = aepms + epms[x]
                        aepms = aepms/(len(epms)-1)
                        for x in range(j+1,len(pms)+2):
                            y = x 
                            for i in range(((y-j)-1),y-1):
                                apmd = apmd + pms[i]
                            res = apmd/j
                            pmd.append(truncate(res,5))
                            apmd =0
                        for x in range(1,len(pmd)):
                            a = (2*float(pms[x+1])) - float(pmd[x-1])
                            b = (2*((float(pms[x+1]) - float(pmd[x-1]))*-1    )) / (len(pib) - 1)
                            As.append(truncate(a,5))
                            Bs.append(truncate(b,5))
                            res = a+(b*m)
                            pmda.append(truncate(res,5))

                        for x in range(k+j+1,len(pib)):
                            resta = abs(float(pib[x-1].frecuencia) - pmd[x-k-j-1])
                            epmd.append(truncate(resta,5))
                        
                        for x in range(0, len(epmd)):
                            aepmd = aepmd + epmd[x]
                        aepmd = aepmd/(len(epmd))
                        
                        for x in range(k+j+1,len(pib)):
                            resta = abs(float(pib[x-1].frecuencia) - pmda[x-k-j-1])
                            epmda.append(truncate(resta,5))
                        
                        for x in range(0, len(epmda)):
                            aepmda = aepmda + epmda[x]
                        aepmda = aepmda/(len(epmda))
                        for x in range (1,len(pib)-1):
                            vi = float(pib[x-1].frecuencia)
                            vf = float(pib[x].frecuencia)
                            tmac.append(truncate(((vf/vi) -1) * 100,5))
                        for x in range(1, len(pib)-1):
                            vf = float(pib[x].frecuencia)
                            ptmac.append(truncate((float(tmac[x-1])/100)*vf+vf,5))
                        for x in range(0,len(pib)):
                            p.append(str(pib[x].periodo))
                            f.append(float(pib[x].frecuencia))
                        if opcion == "ps":
                            for x in range(1,len(f)):
                                res = float(ps[x])+(alpha*(float(f[x]) - float(ps[x])))
                                psel.append(truncate(res,5))
                            for x in range(2,len(f)-1):
                                resta = abs(f[x] - psel[x-2])
                                epsel.append(truncate(resta,5))
                            
                            for x in range(0, len(epsel)):
                                aepsel = aepsel + epsel[x]
                            aepsel = aepsel/(len(epsel))
                            print(aepsel)

                            for c in range(2):
                                psel.insert(0,0)
                                epsel.insert(0,0)
                        if opcion == "pmd":
                            for x in range(k+j,len(f)):
                                psel.append(truncate(float(pmd[x-k-j])+(alpha*(float(f[x]) - float(pmd[x-k-j]))),5))
                            for x in range(k+j+1,len(f)-1):
                                resta = abs(f[x] - psel[x-k-j-1])
                                epsel.append(truncate(resta,5))
                            for x in range(0, len(epsel)):
                                aepsel = aepsel + epsel[x]
                            aepsel = aepsel/(len(epsel))
                            print(aepsel)
                            for c in range(j+k+1):
                                psel.insert(0,0)
                                epsel.insert(0,0)
                        if opcion == "pms":
                            for x in range(k,len(f)):
                                psel.append(truncate(float(pms[x-k])+(alpha*(float(f[x]) - float(pms[x-k]))),5))
                            for x in range(k+1,len(f)-1):
                                print(psel[x-k-1])
                                resta = abs(f[x] - psel[x-k-1])
                                epsel.append(truncate(resta,5))
                            for x in range(0, len(epsel)):
                                aepsel = aepsel + epsel[x]
                            aepsel = aepsel/(len(epsel))
                            print(aepsel)
                            for c in range(k+1):
                                psel.insert(0,0)
                                epsel.insert(0,0)
                        if opcion == "pmda":
                            for x in range(k+j,len(f)):
                                psel.append(truncate(float(pmda[x-k-j])+(alpha*(float(f[x]) - float(pmda[x-k-j]))),5))
                            for x in range(k+j+1,len(f)-1):
                                resta = abs(f[x] - psel[x-k-j-1])
                                epsel.append(truncate(resta,5))
                            for x in range(0, len(epsel)):
                                aepsel = aepsel + epsel[x]
                            aepsel = aepsel/(len(epsel))
                            print(aepsel)
                            for c in range(j+k+1):
                                psel.insert(0,0)
                                epsel.insert(0,0)
                        ## Llenado de 0's
                        for c in range(0,k):
                            pms.insert(0,0)
                            epms.insert(0,0)
                        for c in range(0,k):
                            pmd.insert(0,0)
                            epmd.insert(0,0)
                        for c in range(0,j):
                            pmd.insert(0,0)
                            epmd.insert(0,0)
                        for c in range(0,k):
                            As.insert(0,0)
                        for c in range(0,j):
                            As.insert(0,0)
                        for c in range(0,k):
                            Bs.insert(0,0)
                        for c in range(0,j):
                            Bs.insert(0,0)
                        for c in range(0,k):
                            pmda.insert(0,0)
                            epmda.insert(0,0)
                        for c in range(0,j):
                            pmda.insert(0,0)
                            epmda.insert(0,0)
                        tmac.insert(0,0)
                        tmac.insert(103,0)
                        epmda.insert(103,0)
                        epsel.insert(103,0)
                        epmd.insert(103,0)
                        epms[102] = 0
                        eps[102] = 0
                        ptmac.insert(0,0)
                        ptmac.insert(0,0)
                        errores = [
                            {'valor':aeps,'Nombre':'Promedio simple'},
                            {'valor':aepms,'Nombre':'Promedio movil simple'},
                            {'valor':aepmd,'Nombre':'Promedio  movil doble'},
                            {'valor':aepmda,'Nombre':'Promedio movil doble ajustado'},
                            {'valor':aepsel,'Nombre':'Suavizacion exponencial'}
                        ]
                        minimo = min(errores, key=itemgetter("valor"))
                        global dataP
                        dataP = {
                            'p': p,
                            'f': f,
                            'ps': ps,
                            'pms': pms,
                            'pmd': pmd,
                            'as': As,
                            'bs': Bs,
                            'pmda': pmda,
                            'tmac': tmac,
                            'ptmac': ptmac,
                            'psel': psel,
                            'mejor': minimo
                        }
                        zipped = zip(p,f,ps,eps,pms,epms,pmd,epmd,As,Bs,pmda,epmda,tmac,ptmac,psel,epsel)
                        contexto = {
                            'zipped':zipped
                        }
                return render(request,'tablas.html',contexto)

@login_required
def logout_view(request):
    logout(request)
    return redirect('usuario:login')