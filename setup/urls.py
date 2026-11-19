from django.contrib import admin
from django.urls import path
from gastos import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='gastos/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('registrar/', views.registrar, name='registrar'),
    path('editar-despesa/<int:id>/', views.editar_despesa, name='editar_despesa'),
    path('editar-investimento/<int:id>/', views.editar_investimento, name='editar_investimento'),
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/senha/', views.alterar_senha, name='alterar_senha'), 
    path('feedback/', views.enviar_feedback, name='enviar_feedback'),
    # Rotas para apagar registos
    path('deletar-despesa/<int:id>/', views.deletar_despesa, name='deletar_despesa'),
    path('deletar-investimento/<int:id>/', views.deletar_investimento, name='deletar_investimento'),
    path('definir-orcamento/', views.definir_orcamento, name='definir_orcamento'),
    path('exportar-csv/', views.exportar_csv, name='exportar_csv'),    
]
