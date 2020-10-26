"""bolao URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('login/', views.login, name='login'),
    path('accounts/login/', views.login, name='login'), #para redirecionar quando o usuário fizer logoff no sistema
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    #path('dashboard/shotresult', views.shotresult, name='shotresult'),
    path('dashboard/ranking/', views.ranking, name='ranking'),
    path('dashboard/bets/', views.bets, name='bets'),
    #path('dashboard/bets_result/', views.bets_result, name='bets_result'),
    path('dashboard/add_credit/', views.add_credit, name='add_credit'),
    path('dashboard/admin_register_result/', views.admin_register_result, name='admin_register_result'), # TODO: so mostar esta pagina para usuários que são administradores do site
]
