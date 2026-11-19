from django import forms
from .models import Despesa, Investimento
from .models import Despesa, Investimento, Perfil
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegistroUsuarioForm(UserCreationForm):
    # Adicionamos o campo de email e marcamos como obrigatório
    email = forms.EmailField(required=True, label="E-mail")

    class Meta:
        model = User
        # O UserCreationForm já trata das passwords automaticamente.
        # Nós só precisamos de dizer quais os campos extra a mostrar:
        fields = ['username', 'email']

class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = ['descricao', 'valor', 'data']
        # Isto garante que o campo de data abra aquele calendário bonitinho do navegador
        widgets = {'data': forms.DateInput(attrs={'type': 'date'})}

class InvestimentoForm(forms.ModelForm):
    class Meta:
        model = Investimento
        fields = ['descricao', 'valor', 'data']
        widgets = {'data': forms.DateInput(attrs={'type': 'date'})} 

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['orcamento_mensal']      
        