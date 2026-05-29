from django.urls import path
from . import views

urlpatterns = [
    path("computadores/",                      views.computadores,             name="computadores"),
    path("computadores/<int:pk>/",             views.computador_detalhe,       name="computador-detalhe"),
    path("computadores/<int:pk>/manutencoes/", views.manutencoes,              name="manutencoes"),
    path("computadores/hostname/<str:hostname>/", views.computador_por_hostname, name="computador-por-hostname"),
]