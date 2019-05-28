# Djnago
from django.urls import path

# Modelos
from app.Usuario.views import login_sistema
from app.Usuario.views import logout_view
from app.Usuario.views import variables_view
from app.Usuario.views import configuraciones_pib
from app.Usuario.views import calculos_pib

app_name='usuario'
urlpatterns = [
    path('', login_sistema, name='login'),
    path('logout_view/',logout_view,name="logout"),    
    path('<username>/variables/',variables_view,name="variables"),
    path('<username>/configuracion/',configuraciones_pib,name="pib"),
    path('<username>/tablas/',calculos_pib,name="calculos_pib"),
    path('<username>/graficas/',calculos_pib,name="graficas_pib"),
]