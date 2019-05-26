# Djnago
from django.urls import path

# Modelos
from app.Usuario.views import login_sistema
from app.Usuario.views import logout_view

app_name='usuario'
urlpatterns = [
    path('', login_sistema, name='login'),
    path('logout_view',logout_view,name="logout"),    

]