from django.db import models


class Computador(models.Model):
    hostname    = models.CharField(max_length=100, unique=True)
    modelo      = models.CharField(max_length=100)
    setor       = models.CharField(max_length=100)
    responsavel = models.CharField(max_length=100)
    ram         = models.IntegerField(help_text="Em GB")
    ssd         = models.IntegerField(help_text="Em GB")
    processador = models.CharField(max_length=100)

    def __str__(self):
        return self.hostname


class Manutencao(models.Model):
    TIPOS = [
        ('Manutenção',    'Manutenção'),
        ('Upgrade',       'Upgrade'),
        ('Formatação',    'Formatação'),
        ('Troca de peça', 'Troca de peça'),
        ('Outro',         'Outro'),
    ]

    computador = models.ForeignKey(Computador, on_delete=models.CASCADE, related_name='historico')
    tipo       = models.CharField(max_length=20, choices=TIPOS)
    descricao  = models.TextField()
    tecnico    = models.CharField(max_length=100)
    data       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.computador.hostname} — {self.tipo} ({self.data:%Y-%m-%d})"