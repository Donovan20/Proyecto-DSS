# Djnago
from django.urls import path

# Modelos
from app.Usuario.views import login_sistema
from app.Usuario.views import logout_view
from app.Usuario.views import variables_view
from app.Usuario.views import config_dolar
from app.Usuario.views import grafica_dolar
from app.Usuario.views import obtener_data

app_name='usuario'
urlpatterns = [
    path('', login_sistema, name='login'),
    path('logout_view/',logout_view,name="logout"),    
    path('<username>/variables/',variables_view,name="variables"),    
    path('<username>/configuracion_dolar/',config_dolar,name="config_dolar"),    
    path('<username>/grafica_dolar/',grafica_dolar,name="grafica_dolar"),    
    path('obtener_data/',obtener_data,name="obtener_data"),    
]