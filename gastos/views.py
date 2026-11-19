from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from .models import Despesa, Investimento
from .forms import DespesaForm, InvestimentoForm
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from datetime import datetime
from .models import Despesa, Investimento, Perfil
from .forms import DespesaForm, InvestimentoForm, PerfilForm
import csv
from django.http import HttpResponse
from django.db.models import Sum
import json
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import RegistroUsuarioForm
from .forms import RegistroUsuarioForm, PerfilForm
from django.core.paginator import Paginator
from .models import Despesa, Investimento, Perfil, Feedback




@login_required(login_url='/login/')
def home(request):
    if request.method == 'POST':
        if 'btn_despesa' in request.POST:
            form = DespesaForm(request.POST)
            if form.is_valid():
                nova = form.save(commit=False)
                nova.usuario = request.user
                nova.save()
                return redirect('home')
                
        elif 'btn_investimento' in request.POST:
            form = InvestimentoForm(request.POST)
            if form.is_valid():
                novo = form.save(commit=False)
                novo.usuario = request.user
                novo.save()
                return redirect('home')

    hoje = datetime.now()
    mes_atual = request.GET.get('mes', hoje.month)
    ano_atual = request.GET.get('ano', hoje.year)

   # === NOVA LÓGICA DE PESQUISA ===
    termo_pesquisa = request.GET.get('pesquisa', '')

    if termo_pesquisa:
        # Se houver pesquisa, ignora o mês e procura em todo o histórico do utilizador
        despesas = Despesa.objects.filter(usuario=request.user, descricao__icontains=termo_pesquisa).order_by('-data')
        investimentos = Investimento.objects.filter(usuario=request.user, descricao__icontains=termo_pesquisa).order_by('-data')
    else:
        # Se não houver pesquisa, mantém o seu filtro original de mês e ano
        despesas = Despesa.objects.filter(usuario=request.user, data__month=mes_atual, data__year=ano_atual).order_by('-data')
        investimentos = Investimento.objects.filter(usuario=request.user, data__month=mes_atual, data__year=ano_atual).order_by('-data')
    # ===============================
    # --- AGRUPAMENTO PARA OS GRÁFICOS DE BARRAS ---
    # Agrupa por descrição, soma os valores e ordena do maior para o menor
    despesas_agrupadas = despesas.values('descricao').annotate(total=Sum('valor')).order_by('-total')
    investimentos_agrupados = investimentos.values('descricao').annotate(total=Sum('valor')).order_by('-total')

    # Transforma em listas e converte para JSON para o JavaScript ler
    labels_despesas = json.dumps([d['descricao'] for d in despesas_agrupadas])
    valores_despesas = json.dumps([float(d['total']) for d in despesas_agrupadas])
    
    labels_invest = json.dumps([i['descricao'] for i in investimentos_agrupados])
    valores_invest = json.dumps([float(i['total']) for i in investimentos_agrupados])

    total_despesas = despesas.aggregate(Sum('valor'))['valor__sum'] or 0
    total_investimentos = investimentos.aggregate(Sum('valor'))['valor__sum'] or 0

    # --- LÓGICA DO ORÇAMENTO ---
    # Vai buscar o perfil do utilizador. Se não existir, cria um automaticamente com os 3000 por defeito.
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    limite_orcamento = float(perfil.orcamento_mensal)
    percentual_gasto = 0
    alerta_orcamento = False
    
    if total_despesas > 0:
        percentual_gasto = (float(total_despesas) / limite_orcamento) * 100
        if percentual_gasto >= 100:
            percentual_gasto = 100
            alerta_orcamento = True

            # --- NOVO CÓDIGO DE PAGINAÇÃO 
    paginator = Paginator(despesas, 10) 
    numero_pagina = request.GET.get('page')
    page_obj = paginator.get_page(numero_pagina)
    # -------------------------------------------------------------

    # --- NOVO: MOTOR PARA OS INVESTIMENTOS ---
    paginator_inv = Paginator(investimentos, 10) 
    numero_pagina_inv = request.GET.get('page_inv') # Nome diferente para não chocar!
    page_obj_inv = paginator_inv.get_page(numero_pagina_inv)
    # -----------------------------------------

    contexto = {
        'despesas': page_obj,
        'investimentos': page_obj_inv,
        'form_despesa': DespesaForm(),
        'form_investimento': InvestimentoForm(),
        'total_despesas': total_despesas,
        'total_investimentos': total_investimentos,
        'mes_atual': int(mes_atual),
        'ano_atual': int(ano_atual),
        'limite_orcamento': limite_orcamento,
        'percentual_gasto': percentual_gasto,
        'alerta_orcamento': alerta_orcamento,
        'labels_despesas': labels_despesas,
        'valores_despesas': valores_despesas,
        'labels_invest': labels_invest,
        'valores_invest': valores_invest,
    }
    return render(request, 'gastos/home.html', contexto)

# --- NOVAS FUNÇÕES DE EDIÇÃO ---
@login_required(login_url='/login/')
def editar_despesa(request, id):
    despesa = get_object_or_404(Despesa, id=id, usuario=request.user)
    if request.method == 'POST':
        form = DespesaForm(request.POST, instance=despesa)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = DespesaForm(instance=despesa)
    return render(request, 'gastos/editar.html', {'form': form, 'titulo': 'Editar Despesa'})

@login_required(login_url='/login/')
def editar_investimento(request, id):
    invest = get_object_or_404(Investimento, id=id, usuario=request.user)
    if request.method == 'POST':
        form = InvestimentoForm(request.POST, instance=invest)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = InvestimentoForm(instance=invest)
    return render(request, 'gastos/editar.html', {'form': form, 'titulo': 'Editar Investimento'})

@login_required(login_url='/login/')
def deletar_despesa(request, id):
    despesa = get_object_or_404(Despesa, id=id, usuario=request.user)
    despesa.delete()
    return redirect('home')

@login_required(login_url='/login/')
def deletar_investimento(request, id):
    invest = get_object_or_404(Investimento, id=id, usuario=request.user)
    invest.delete()
    return redirect('home')

def registrar(request):
    # Se o utilizador já tiver sessão iniciada, não precisa de se registar
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Faz o login automático logo após criar a conta
            return redirect('home')
    else:
        form = RegistroUsuarioForm()
        
    return render(request, 'gastos/registrar.html', {'form': form})

@login_required(login_url='/login/')
def definir_orcamento(request):
    perfil, created = Perfil.objects.get_or_create(usuario=request.user)
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PerfilForm(instance=perfil)
    return render(request, 'gastos/editar.html', {'form': form, 'titulo': 'Definir Orçamento'})    

@login_required(login_url='/login/')
def exportar_csv(request):
    mes = request.GET.get('mes', datetime.now().month)
    ano = request.GET.get('ano', datetime.now().year)

    # Configura o ficheiro para ser descarregado automaticamente
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="relatorio_financeiro_{mes}_{ano}.csv"'

    # Usamos ponto e vírgula para o Excel reconhecer as colunas corretamente no formato PT/BR
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Tipo', 'Descricao', 'Valor (R$)', 'Data'])

    # Vai buscar os dados apenas do mês e utilizador selecionados
    despesas = Despesa.objects.filter(usuario=request.user, data__month=mes, data__year=ano)
    investimentos = Investimento.objects.filter(usuario=request.user, data__month=mes, data__year=ano)

    # Escreve as despesas no ficheiro
    for d in despesas:
        writer.writerow(['Despesa', d.descricao, str(d.valor).replace('.', ','), d.data.strftime('%d/%m/%Y')])

    # Escreve os investimentos no ficheiro
    for i in investimentos:
        writer.writerow(['Investimento', i.descricao, str(i.valor).replace('.', ','), i.data.strftime('%d/%m/%Y')])

    return response    

    from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def perfil(request):
    if request.method == 'POST':
        # 1. Mantém a sua lógica original para atualizar e guardar o e-mail
        request.user.email = request.POST.get('email', '')
        request.user.save()

        # 2. Guarda o Nome de Exibição diretamente no Perfil
        novo_nome = request.POST.get('nome_exibicao', '')
        request.user.perfil.nome_exibicao = novo_nome
        request.user.perfil.save()
        
        return redirect('perfil')

    return render(request, 'gastos/perfil.html')
@login_required
def alterar_senha(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Esta linha é magia: atualiza a sessão para que o utilizador 
            # não seja "expulso" e deslogado após mudar a senha
            update_session_auth_hash(request, user)  
            return redirect('perfil')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'gastos/alterar_senha.html', {'form': form})

@login_required(login_url='/login/')
def enviar_feedback(request):
    if request.method == 'POST':
        mensagem = request.POST.get('mensagem', '').strip()
        if mensagem:
            Feedback.objects.create(usuario=request.user, mensagem=mensagem)
    return redirect('home')
    