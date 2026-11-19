from django.db import models
from django.contrib.auth.models import User

class Despesa(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    descricao = models.CharField(max_length=255, verbose_name="Descrição")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    data = models.DateField(verbose_name="Data da Despesa")

    def __str__(self):
        return self.descricao

class Investimento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    descricao = models.CharField(max_length=255, verbose_name="Descrição do Investimento")
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Investido")
    data = models.DateField(verbose_name="Data do Investimento")

    def __str__(self):
        return self.descricao
        
class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    orcamento_mensal = models.DecimalField(max_digits=10, decimal_places=2, default=3000.00, verbose_name="Orçamento Mensal (R$)")
    nome_exibicao = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"   

class Feedback(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensagem = models.TextField(verbose_name="Comentário / Sugestão")
    data_envio = models.DateTimeField(auto_now_add=True, verbose_name="Data de Envio")

    class Meta:
        ordering = ['-data_envio'] # Mostra os mais recentes primeiro

    def __str__(self):
        return f"Feedback de {self.usuario.username} em {self.data_envio.strftime('%d/%m/%Y')}"