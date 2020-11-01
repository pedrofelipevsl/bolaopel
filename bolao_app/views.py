from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from decimal import Decimal

from .models import FormUsuarios, Apostador, Selecao, Bolao, Aposta, Partida, ApostadorVencedorBolao



def landingpage(request):
    return render(request,
                  'bolao_app/landingpage.html',
                  )

def logout(request):
    auth.logout(request)
    return render(request,
                  'bolao_app/landingpage.html',
                  )

def login(request):
    if request.method != 'POST':
        return render(request, 'bolao_app/login.html')

    usuario = request.POST.get('usuario')
    senha = request.POST.get('senha')

    if not usuario or not senha:
        messages.error(request, "Informe  usuário e senha para realizar o login no sistema!")
        return render(request, 'bolao_app/login.html')

    user = auth.authenticate(request, username=usuario, password=senha)

    if not user:
        messages.error(request, 'Usuário ou senha inválidos.')
        return render(request, 'bolao_app/login.html')
    else:
        auth.login(request, user)
        messages.success(request, 'Você fez login com sucesso.')
        return redirect('dashboard')

# TODO: Para estudar e aplicar depois
def register_jango(request):
        formulario = FormUsuarios()
        return render(
            request,
            'bolao_app/register.html',
            { 'formulario': formulario }
        )

def register(request):
    if request.method != 'POST':
        return render(request, 'bolao_app/register.html')

    nome = request.POST.get('nome')
    sobrenome = request.POST.get('sobrenome')
    email = request.POST.get('email')
    usuario = request.POST.get('usuario')
    senha = request.POST.get('senha')
    senha2 = request.POST.get('senha2')

    if not nome or not sobrenome or not email or not usuario or not senha \
            or not senha2:
        messages.error(request, 'Nenhum campo pode estar vazio.')
        return render(request, 'bolao_app/register.html')

    try:
        validate_email(email)
    except:
        messages.error(request, 'Email inválido.')
        return render(request, 'bolao_app/register.html')

    if len(senha) < 6:
        messages.error(request, 'Senha precisa ter 6 caracteres ou mais.')
        return render(request, 'bolao_app/register.html')

    if len(usuario) < 6:
        messages.error(request, 'Usuário precisa ter 6 caracteres ou mais.')
        return render(request, 'bolao_app/register.html')

    if senha != senha2:
        messages.error(request, 'Senhas não conferem.')
        return render(request, 'bolao_app/register.html')

    if User.objects.filter(username=usuario).exists():
        messages.error(request, 'Usuário já existe.')
        return render(request, 'bolao_app/register.html')

    if User.objects.filter(email=email).exists():
        messages.error(request, 'E-mail já existe.')
        return render(request, 'bolao_app/register.html')

    user = User.objects.create_user(username=usuario, 
                                    email=email,
                                    password=senha, 
                                    first_name=nome,
                                    last_name=sobrenome
                                    )
    # cria um apostador e o associa a o usuario cadastrado no sistema
    apostador = Apostador()
    apostador.usuario = user
    user.save()
    apostador.save()

    messages.success(request, 'Registrado com sucesso! Agora faça login.')

    #TODO: mudar para que o usuario apos cadastrado ja esteja logado no sistema e va para a dashboard
    return redirect('login')

# >>>>>> DASHBOARD <<<<<<<<
@login_required(redirect_field_name='login')
def dashboard(request):
    
    """ qry_bolao_aposta_apostador = ""

    boloes_2 = Bolao.objects.raw(qry_bolao_aposta_apostador, [id_apostador]) """
    
    #Filtra a relacao de apostadores baseado no usuario logado do sistema e passa como item de dicionario para a template exibir o saldo de credito
    apostador_credito = Apostador.objects.filter(usuario_id=request.user.id).first()

    boloes = Bolao.objects.filter(esta_ativo=True).order_by('id').all()
    partidas = Partida.objects.filter(finalizada=False).order_by('id').all()
    
    #Verificar se o bolao pode continua ativo para aposta se não desativa (colocar aqui)
    for partida in partidas:
        for bolao in boloes:
            partida.finalizar_partida() # finaliza primeiro a partida depois o bolao
            if partida == bolao.partida: # filtra as partidas do respectovo bolao para desativálo
                bolao.desativar_bolao(partida)

    
    boloes = Bolao.objects.filter(esta_ativo=True).order_by('id').all()

    if request.method != 'POST':
        return render(request,
                  'bolao_app/dashboard.html',
                   {
                       'boloes': boloes,
                       'apostador_credito': apostador_credito,
                   })
  

    apostador_id = int(request.POST.get("apostador"))
    boloao_id = int(request.POST.get("bolao"))
    qtd_gols_desafiante = int(request.POST.get("gols_desaf"))
    qtd_gols_visitante = int(request.POST.get("gols_visit"))
    
    apostador_credito = Apostador.objects.filter(usuario_id=request.user.id).first()

    if Aposta.objects.filter(apostador_id=apostador_id).filter(bolao_id=boloao_id).exists():
        messages.error(request, 'Você já possui uma aposta para este bolão! É permitido apostar apenas uma vez por bolão!')
        return render(request,
                    'bolao_app/dashboard.html',
                    {'boloes': boloes,
                     'apostador_credito': apostador_credito,
                    },
                    )

    # cria uma nova aposta com as informacoes recebidas apenas na memoria
    aposta = Aposta(qtd_gols_desafiante=qtd_gols_desafiante,
                    qtd_gols_visitante=qtd_gols_visitante,
                    bolao_id=boloao_id,
                    apostador_id=apostador_id 
                    )
    # Traz para a memoria o bolao selecionado pelo usurario para fazer a aposta
    boloa1 = Bolao.objects.filter(id=boloao_id).first()

    try:
        # verificar se o usuario tem saldo
        # abater valor da aposta do credito do apostador
        # salva a aposta realizada, salva o valor do premio do bolao, salva o novo saldo do apostador
        boloa1.adicionar_aposta(aposta)
        # informa o sucesso na gravacao da aposta
        messages.success(request, 'Aposra realizada com sucesso! ')
    except ValueError as erro:
        # informa que o apostador não possui saldo suficiente
        messages.error(request, erro)
    
    apostador_credito = Apostador.objects.filter(usuario_id=request.user.id).first()
    return render(request,
                  'bolao_app/dashboard.html',
                  {'boloes': boloes,
                   'apostador_credito': apostador_credito,
                  },
                  )



@login_required(redirect_field_name='login')
def ranking(request):
    usuarios = User.objects.order_by('-apostadorusuario__premiacao_ganha').all()
    return render(request,
                  'bolao_app/dashboard_ranking.html',
                  {'usuarios': usuarios},
                  )

@login_required(redirect_field_name='login')
def bets(request):
    
    apostas = Aposta.objects.filter(apostador_id=request.user.id).all()
    
    return render(request,
                  'bolao_app/dashboard_bets.html',
                  {'apostas': apostas},
                  )

@login_required(redirect_field_name='login')
def add_credit(request):
    apostador_credito = Apostador.objects.filter(usuario_id=request.user.id).first()
    
    if request.method != 'POST':
        return render(request,
                    'bolao_app/dashboard_add_credit.html',
                    {'apostador_credito': apostador_credito},
                    )
    
    credito = request.POST.get('valor_adicional')
    apostador_credito.adicionar_credito(credito)
    
    messages.success(request, 'Credito adiconado com sucesso.')
    apostador_credito = Apostador.objects.filter(usuario_id=request.user.id).first()
    return render(request,
                    'bolao_app/dashboard_add_credit.html',
                    {'apostador_credito': apostador_credito},
                    )

@login_required(redirect_field_name='login')
def admin_register_result(request):
    
    # Verifica as partidas que estao sem placar e que ainda nao foram finalizadas pelo sistema com base no horario de termino
    partidas = Partida.objects.filter(gols_desafiante=None).filter(gols_visitante=None).all()

    # Verificar se exitem partidas que devem ser finalizadas pelo horário de termino
    for partida in partidas:
        partida.finalizar_partida()

    # Verifica as partidas que estao sem placar e que já foram finalizadas pelo sistema com base no horario de termino
    partidas = Partida.objects.filter(gols_desafiante=None).filter(gols_visitante=None).filter(finalizada=True).all()

    if request.method != 'POST':
        return render(request,
                    'bolao_app/dashboard_admin_register_result.html',
                    {'partidas': partidas},
                    )
    
    id_partida = int(request.POST.get('id_partida'))
    #id_bolao = int(request.POST.get('id_bolao')) # na verdade e mais uma vez o id da partida
    gols_desaf = int(request.POST.get('gols_desaf'))
    gols_visit = int(request.POST.get('gols_visit'))

    #encontra a partida e seta o resultado
    partida = Partida.objects.filter(id=id_partida).first()
    partida.definir_resultado(gols_desaf, gols_visit)
    messages.success(request, 'Placar da partida registrada com sucesso.')

    #verificar e registar vencedores e distribuir premiacao >>>>> ver depois pois um bolao pode estar em varias partidas
    bolao = Bolao.objects.filter(partida_id=id_partida).first() #TODO: gambi
    id_bolao = bolao.id
    apostas = Aposta.objects.filter(bolao_id=id_bolao).all()
    vencedores = []
    
    # verifica os possíveis vencedores e distribue o premio
    bolao.verificar_vencedores(apostas, vencedores)
    
    #apos definir o resultado atualiza al lista de partidas verifica as partidas que estao sem placar e que já foram finalizadas pelo sistema com base no horario de termino
    partidas = Partida.objects.filter(gols_desafiante=None).filter(gols_visitante=None).filter(finalizada=True).all()
    return render(request,
                    'bolao_app/dashboard_admin_register_result.html',
                    {'partidas': partidas},
                    )

#TODO: se nao for usado retirer no final
@login_required(redirect_field_name='login')
def shotresult(request):
    return render(request,
                  'bolao_app/dashboard_shot_result.html',
                  {'boloes': boloes},
                  )
