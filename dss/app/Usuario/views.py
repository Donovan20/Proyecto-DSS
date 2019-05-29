# Django
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Modelos
from app.Usuario.models import Dolar
from app.Usuario.models import PIB

# PDF
from app.Usuario.render import PIBRenderPdf, DolarRenderPdf
# Variables globales
dataP = {}
dataD = {}

import math
from operator import itemgetter
import base64
from io import BytesIO
# models



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
        if int(m) < 0:
            error['mmenor0'] = 'M debe ser mayor o igual a 0'
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
            dataD = []
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
            periodos.append('junio 2019')
            frecuencias.append(0)
            print(len(frecuencias))
            print(len(periodos))
            acumuladorPS = 0
            contador = 1
            ps = []
            eapsd = [] # errores absolutos
            k = int(k)
            j = int(j)
            m = int(m)
            for i in range(0, len(frecuencias) - 1):
                acumuladorPS = acumuladorPS + (dolar[i].frecuencia)
                ps.append(truncate((acumuladorPS / contador),5))
                resta = abs(float(dolar[i].frecuencia)-float((acumuladorPS / contador)))
                eapsd.append(truncate(resta, 5))
                contador += 1

            auxiliar = 0
            acumuladorPSM = 0
            pms = []
            eapms = [] # errores absolutos
            for x in range(int(k)+1, len(frecuencias)+1):
                auxiliar = x
                for i in range(((auxiliar-int(k))-1), auxiliar-1):
                    acumuladorPSM = acumuladorPSM + (dolar[i].frecuencia)
                pms.append(truncate((acumuladorPSM/int(k)),5))
                acumuladorPSM = 0

            auxiliarPMD = 0
            acumuladorPMD = 0
            pmd = []
            eapmd = [] # errores absolutos
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
            eapmda = [] # errores absolutos
            for x in range(1, len(pmd)):
                pmda.append(truncate((As[x-1] + Bs[x-1] * int(m)), 5))

            tmac = []
            for x in range(1, len(frecuencias)):
                tmac.append(truncate((((frecuencias[x]/frecuencias[x-1])-1)*100),5))
            
            ptmac = []
            eaptmac = []# errores absolutos
            for x in range(1, len(frecuencias) - 1):
                ptmac.append(truncate((float(frecuencias[x])+(float(frecuencias[x])*(tmac[x-1]/100))),5))
            
            psel = []
            eapsel = [] # errores absolutos
            if opcion == "ps":
                for x in range(1,len(frecuencias)-1):
                    res = float(ps[x])+(float(alfa)*(float(frecuencias[x]) - float(ps[x])))
                    psel.append(truncate(res,5))
                indicepse = len(frecuencias) - len(psel)
                for x in range(0, len(psel)):
                    resta = abs(frecuencias[indicepse]-psel[x])
                    eapsel.append(truncate(resta,5))
                    indicepse +=  1;
                for c in range(2):
                    psel.insert(0,0)
                    
            if opcion == "pmd":
                for x in range(k+j,len(frecuencias)):
                    psel.append(truncate(float(pmd[x-k-j])+(float(alfa)*(float(frecuencias[x]) - float(pmd[x-k-j]))),5))
                indicepse = len(frecuencias) - len(psel) + 1
                for x in range(0, len(psel) - 1):
                    resta = abs(frecuencias[indicepse]-psel[x])
                    eapsel.append(truncate(resta,5))
                    indicepse +=  1
                for c in range(j+k+1):
                    psel.insert(0,0)
            if opcion == "pms":
                for x in range(k,len(frecuencias)):
                    psel.append(truncate(float(pms[x-k])+(float(alfa)*(float(frecuencias[x]) - float(pms[x-k]))),5))
                indicepse = len(frecuencias) - len(psel) + 1
                for x in range(0, len(psel) - 1):
                    resta = abs(frecuencias[indicepse]-psel[x])
                    eapsel.append(truncate(resta,5))
                    indicepse +=  1
                for c in range(k+1):
                    psel.insert(0,0)
            if opcion == "pmda":
                for x in range(k+j,len(frecuencias)):
                    psel.append(truncate(float(pmda[x-k-j])+(float(alfa)*(float(frecuencias[x]) - float(pmda[x-k-j]))),5))
                indicepse = len(frecuencias) - len(psel) + 1
                for x in range(0, len(psel) - 1):
                    resta = abs(frecuencias[indicepse]-psel[x])
                    eapsel.append(truncate(resta,5))
                    indicepse +=  1
                for c in range(j+k+1):
                    psel.insert(0,0)

            indicepms = len(frecuencias) - len(pms)
            for x in range(0, len(pms)):
                resta = abs(frecuencias[indicepms]-pms[x])
                eapms.append(truncate(resta,5))
                indicepms +=  1;

            indicepmd = len(frecuencias) - len(pmd) + 1
            for x in range(0, len(pmd)-1):
                resta = abs(frecuencias[indicepmd]-pmd[x])
                eapmd.append(truncate(resta,5))
                indicepmd +=  1;
            
            indicepmda = len(frecuencias) - len(pmda)
            for x in range(0, len(pmda)):
                resta = abs(frecuencias[indicepmda]-pmda[x])
                eapmda.append(truncate(resta,5))
                indicepmda +=  1;

            indiceptmac = len(frecuencias) - len(ptmac) + 1
            for x in range(0, len(ptmac) - 1):
                resta = abs(frecuencias[indiceptmac]-ptmac[x])
                eaptmac.append(truncate(resta,5))
                indiceptmac +=  1;

            # Errores medios
            constadorerrps = 0
            for i in range(0, len(eapsd)):
                constadorerrps += eapsd[i]

            error_medio_ps = constadorerrps / len(eapsd)

            constadorerrpms = 0
            for i in range(0, len(eapms)):
                constadorerrpms += eapms[i]

            error_medio_pms = constadorerrpms / len(eapms)

            constadorerrpmd = 0
            for i in range(0, len(eapmd)):
                constadorerrpmd += eapmd[i]

            error_medio_pmd = constadorerrps / len(eapmd)

            constadorerrpmda = 0
            for i in range(0, len(eapmda)):
                constadorerrpmda += eapmda[i]

            error_medio_pmda = constadorerrpmda / len(eapmda)

            constadorerrptmac = 0
            for i in range(0, len(eaptmac)):
                constadorerrptmac += eaptmac[i]

            error_medio_ptmac = constadorerrptmac / len(eaptmac)

            constadorerrpse = 0
            for i in range(0, len(eapsel)):
                constadorerrpse += eapsel[i]

            error_medio_psel = constadorerrpse / len(eapsel)

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

            print(len(ps))
            print(len(pms))
            print(len(pmd))
            print(len(As))
            print(len(Bs))
            print(len(pmda))
            print(len(tmac))
            print(len(ptmac))
            print(len(psel))

            errores = [
                {'valor':error_medio_ps,'Nombre':'Promedio simple'},
                {'valor':error_medio_pms,'Nombre':'Promedio movil simple'},
                {'valor':error_medio_pmd,'Nombre':'Promedio  movil doble'},
                {'valor':error_medio_pmda,'Nombre':'Promedio movil doble ajustado'},
                {'valor':error_medio_ptmac,'Nombre':'P. Tasa de crecimiento anual'},
                {'valor':error_medio_psel,'Nombre':'Suavizacion exponencial'}
            ]
            minimo = min(errores, key=itemgetter("valor"))
            mejor = []
            if minimo["Nombre"] == "Promedio simple":
                mejor = ps
            elif minimo["Nombre"] == "Promedio movil simple":
                mejor = pms
            elif minimo["Nombre"] == "Promedio movil doble":
                mejor = pmd
            elif minimo["Nombre"] == "Promedio movil doble ajustado":
                mejor = pmda
            elif minimo["Nombre"] == "Suavizacion exponencial":
                mejor = psel
            elif minimo["Nombre"] == "P. Tasa de crecimiento anual":
                mejor = ptmac
            zipped = zip(periodos, frecuencias, ps, pms, pmd, As, Bs, pmda, tmac, ptmac, psel)
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
                    'mejor':minimo,
                    'mejor2':mejor
            }
            contexto = {
                'zipped': zipped,
                'values': values
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


def renderDolar(request):
    imagen = request.POST['input']
    imagen = imagen.split(',',1)
    imagen = str.encode(imagen[1])
    with open("graficaDolar.png", "wb") as fh:
        fh.write(base64.decodebytes(imagen))

    imagen2 = request.POST['input2']
    imagen2 = imagen2.split(',',1)
    imagen2 = str.encode(imagen2[1])
    with open("graficaDolar2.png", "wb") as fh:
        fh.write(base64.decodebytes(imagen2))
    global dataD
    p = dataD['p']
    f = dataD['f']
    ps = dataD['ps']
    pms = dataD['pms']
    pmd = dataD['pmd']
    As = dataD['as']
    Bs = dataD['bs']
    pmda = dataD['pmda']
    tmac = dataD['tmac']
    ptmac = dataD['ptmac']
    psel = dataD['psel']
    zipped = zip(p,f,ps,pms,pmd,As,Bs,pmda,tmac,ptmac,psel)
    return DolarRenderPdf.render('pdfDolar.html',{'zipped':zipped})


def renderPIB(request):
    imagen = request.POST['input']
    imagen = imagen.split(',',1)
    imagen = str.encode(imagen[1])
    with open("grafica.png", "wb") as fh:
        fh.write(base64.decodebytes(imagen))

    imagen2 = request.POST['input2']
    imagen2 = imagen2.split(',',1)
    imagen2 = str.encode(imagen2[1])
    with open("grafica2.png", "wb") as fh:
        fh.write(base64.decodebytes(imagen2))
    global dataP
    p = dataP['p']
    f = dataP['f']
    ps = dataP['ps']
    pms = dataP['pms']
    pmd = dataP['pmd']
    As = dataP['as']
    Bs = dataP['bs']
    pmda = dataP['pmda']
    tmac = dataP['tmac']
    ptmac = dataP['ptmac']
    psel = dataP['psel']

    zipped = zip(p,f,ps,pms,pmd,As,Bs,pmda,tmac,ptmac,psel)
    return PIBRenderPdf.render('pdfPIB.html',{'zipped':zipped})

@login_required
def configuraciones_pib(request,username):
    if request.method == 'GET':
        return render(request, 'configuraciones.html')
    elif request.method == 'POST':
        
        if 'pib' in request.POST:
            pib = PIB.objects.all()
            n = len(pib) - 1 
            k = int(request.POST['k'])
            j = int(request.POST['j'])
            opcion = request.POST['pse']
            alpha = float(request.POST['alpha'])
            m = int(request.POST['m'])
            error = {}
            if k < 0:
                error['kmenor0'] = 'K debe ser mayor a 0'
            if k >= n:
                error['kmenorn'] = 'K debe ser menor a N - 1'
            if j < 0:
                error['jmenor0'] = 'J debe ser mayor a 0'
            if j >= (int(n) - k - 1):
                error['jmenornk'] = 'J debe ser menor a (n - k - 1)'
            if float(alpha) < 0:
                error['alfamenor0'] = 'Alfa debe ser mayor o igual a 0'
            if float(alpha) > 1:
                error['alfamayor1'] = 'Alfa debe ser menor o igual a 1'
            if m < 0:
                error['mmenor0'] = 'M debe ser mayor o igual a 0'
            if len(error) > 0:
                values = {
                    'k': k,
                    'j': j,
                    'alpha': alpha,
                    'm': m
                }
                return render(request, 'configuraciones.html', {'errores': error, 'value': values})
            else:
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
                            eptmac=[]
                            As = []
                            Bs = []
                            epsel=[]
                            psel=[]
                            aeps = 0
                            aepms = 0
                            aepmd = 0
                            aepmda = 0
                            aeptmac = 0
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
                            
                            for x in range(2,len(pib)-1):
                                print(float(pib[x].frecuencia))
                                resta = abs(float(pib[x].frecuencia) - ptmac[x-2])
                                eptmac.append(truncate(resta,5))

                            for x in range(0, len(eptmac)):
                                aeptmac = aeptmac + eptmac[x]
                            aeptmac = aeptmac/(len(eptmac))

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
                            # epms[102] = 0
                            # eps[102] = 0
                            eptmac.insert(103,0)
                            ptmac.insert(0,0)
                            ptmac.insert(0,0)
                            eptmac.insert(0,0)
                            eptmac.insert(0,0)
                            errores = [
                                {'valor':aeps,'Nombre':'Promedio simple'},
                                {'valor':aepms,'Nombre':'Promedio movil simple'},
                                {'valor':aepmd,'Nombre':'Promedio  movil doble'},
                                {'valor':aepmda,'Nombre':'Promedio movil doble ajustado'},
                                {'valor':aeptmac,'Nombre':'P. Tasa de crecimiento anual'},
                                {'valor':aepsel,'Nombre':'Suavizacion exponencial'}
                            ]
                            minimo = min(errores, key=itemgetter("valor"))
                            mejor = []
                            if minimo["Nombre"] == "Promedio simple":
                                mejor = ps
                            elif minimo["Nombre"] == "Promedio movil simple":
                                mejor = pms
                            elif minimo["Nombre"] == "Promedio movil doble":
                                mejor = pmd
                            elif minimo["Nombre"] == "Promedio movil doble ajustado":
                                mejor = pmda
                            elif minimo["Nombre"] == "Suavizacion exponencial":
                                mejor = psel
                            elif minimo["Nombre"] == "P. Tasa de crecimiento anual":
                                mejor = ptmac
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
                                'mejor': minimo,
                                'mejor2':mejor
                            }
                            zipped = zip(p,f,ps,eps,pms,epms,pmd,epmd,As,Bs,pmda,epmda,tmac,ptmac,eptmac,psel,epsel)
                            contexto = {
                                'zipped':zipped
                            }
                    return render(request,'tablas.html',contexto)

@login_required
def acercade(request):
    return render(request, 'acerca.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('usuario:login')