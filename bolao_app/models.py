from django.db import models
from django.contrib.auth.models import User
from django import forms
from datetime import date, datetime
from django.utils import timezone
from decimal import Decimal

class Apostador(models.Model):
    # Representa um apostador que pode realizar apostas no bolao 
    class Meta:
        verbose_name_plural = "Apostadores"

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='apostadorusuario',  # renomei a chave para evitar erros na hora da migracao
    )
    credito = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=10.00,
        editable=True,
    )  # não exibe valor da ser ajustado
    premiacao_ganha = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        editable=True,
    )  # não exibe valor da ser ajustado

    qtd_vitorias = models.PositiveSmallIntegerField(
        editable=True,
        default=0,
        blank=True,
    )

    def __str__(self):
        # Retorna uma representacao de um apostador
        return "%s" % self.usuario

    def apostar_valor(self, valor=5.00):
        """ Abatate valor da aposta realizada no credito do apostador  """
        self.credito -= Decimal(valor)

    def adicionar_credito(self, credito):
        """ Adiciona credito na conta do apostador  """
        self.credito += Decimal(credito)
        self.save()

class Selecao(models.Model):
    """  """

    class Meta:
        verbose_name_plural = "Seleções"  # Nome que de fato sera exibido no site para a tabela no plural
        ordering = ["nome"]  # odenacao que sera realizada, pode ser mais de um campo (- ordem decrescente)

    # id pk
    nome = models.CharField(
        max_length=200,
    )
    qtd_titulos = models.PositiveSmallIntegerField()

    def __str__(self):
        """  """
        return self.nome


class Partida(models.Model):
    """  """

    # id pk - id_pa = models.IntegerField(primary_key=True)
    class Meta:
        ordering = ["-data_hora_inicio"]

    selecao_desafiante = models.ForeignKey(
        Selecao,
        on_delete=models.CASCADE,
        related_name='selecaodesafiante',
    )
    selecao_visitante = models.ForeignKey(
        Selecao,
        on_delete=models.CASCADE,
        related_name='selecaovisitante',
    )
    gols_desafiante = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        editable=True,
    )  # não exibe valor da ser ajustado
    gols_visitante = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        editable=True,
    )  # não exibe valor da ser ajustado
    estadio = models.CharField(
        max_length=200,
    )
    
    data_hora_inicio = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
    )
    
    data_hora_fim = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
    )

    finalizada = models.BooleanField(
        default=False,
        editable=True,
    )  # não exibe valor da ser ajustado

    def __str__(self):
        """  """
        return "%s x %s" % (self.selecao_desafiante, self.selecao_visitante)
    
    def finalizar_partida(self):
        if not self.data_hora_fim >= timezone.now(): #datetime.now():
            self.finalizada = True
            self.save()

    def definir_resultado(self, gols_desaf, gols_visit):
        self.gols_desafiante = gols_desaf
        self.gols_visitante = gols_visit
        self.save()


class Bolao(models.Model):
    """  """

    class Meta:
        verbose_name_plural = "Bolões"
        ordering = ["nome"]

    # id pk
    nome = models.CharField(
        max_length=200,
    )
    partida = models.ForeignKey(
        Partida,
        on_delete=models.CASCADE,
    )  # fk
    premiacao = models.FloatField(
        default=0.0,
        editable=True,
    )  # não exibe valor da ser ajustado
    valor_disputado = models.FloatField(
        default=0.0,
        editable=True,
    )  # não exibe valor da ser ajustado
    esta_ativo = models.BooleanField(
        default=True,
        editable=True,
    )  # não exibe valor da ser ajustado
    
    def __str__(self):
        return self.nome

    #TODO: corrigir erro aqui
    def desativar_bolao(self, partida):
        if not partida.data_hora_inicio >= timezone.now(): #datetime.now():
            self.esta_ativo = False
            self.save()

    def adicionar_aposta(self, aposta):
        """ Adiciona aposta ao bolao """
        apostador = Apostador.objects.filter(usuario_id=aposta.apostador_id).first()
        
        if apostador.credito >= aposta.valor: # so permite que a aposta seja efetivada caso o credito do apostador seja maior ou igual ao valor da aposta
            #self.apostas.append(aposta)
            self.valor_disputado += aposta.valor # amplia o valor em disputa do bolao
            apostador.apostar_valor(aposta.valor) # reduz o valor do credito do apostador
            apostador.save() #salva o apostador
            self.save() #salva o bolao
            aposta.save() #salva a aposta
        else:
            raise ValueError("Seu crédito atual é de >> R$ " + str(aposta.apostador.credito) + " << insuficiente para realizar uma aposta!")
    
    def remover_aposta(self, aposta):
        """ Remove uma aposta do bolao """
        #self.apostas.remove(aposta)
        #TODO: colocar aqui o codigo sobre a remocao da aposta
        self.valor_disputado -= aposta.valor_aposta
        aposta.apostador.adicionar_credito(aposta.valor_aposta) # devolve o valor da  aposta no credito do apostador

    def set_premiacao(self, apostadores, vencedores):
        """ Processa e define a premiacao ou nao do bolao, coso nao haja vencedor devolve o credito ao apstador """
        #TODO: fazer um filtro apenas para os vencedores do bolao atual, verificar a pertinencia
        if vencedores: # se a lista nao estiver vazia divide o valor disputado pela quantidade de vencedores seta a premiacao
            self.premiacao = (self.valor_disputado/len(vencedores))
            self.save()
            for ven in vencedores: # distribui a premiacao para os vencedores
                apostador = Apostador.objects.filter(usuario_id=ven.apostador_id).first()
                apostador.premiacao_ganha += Decimal(self.premiacao)
                apostador.qtd_vitorias += 1
                apostador.save()
                apostador.adicionar_credito(self.premiacao) # converte a premiacao em credito
        else: # se nao houver vencedores devolve o credito para o apostador
            for apostador in apostadores: 
                apostador.adicionar_credito(5.00) #depois ajustar

    def verificar_vencedores(self, apostas, vencedores):
        """ Processa e define os vencedores ou nao do bolao  """
        
        # relacao de apostadores no caso de devolucao de valores
        apostadores = []

        for ap in apostas: # verifica quem acertou o bolao pelo resultado identico do placar 
            if ap.bolao.partida.gols_desafiante == ap.qtd_gols_desafiante and ap.bolao.partida.gols_visitante == ap.qtd_gols_visitante:
                # registra o(s) vencedor(es) do baolao
                vencedor = ApostadorVencedorBolao() 
                vencedor.apostador = ap.apostador
                vencedor.bolao = ap.bolao
                vencedor.save()
                vencedores.append(vencedor)

                #TODO: colocar aqui o codigo sobre as insercao de vencedores
                #vencedores.append(ap.apostador)
        
        if not vencedores: # se ninguem tiver acetado o placar verifica quem ACERTOU A VITORIA DO DESAFIANTE
            for ap in apostas:
                if ap.bolao.partida.gols_desafiante > ap.bolao.partida.gols_visitante and ap.qtd_gols_desafiante > ap.qtd_gols_visitante:
                    vencedor = ApostadorVencedorBolao() 
                    vencedor.apostador = ap.apostador
                    vencedor.bolao = ap.bolao
                    vencedor.save()
                    vencedores.append(vencedor)
                    #TODO: colocar aqui o codigo sobre as insercao de vencedores
                    #vencedores.append(ap.apostador)

        if not vencedores: # se ninguem tiver acetado o placar verifica quem ACERTOU A VITORIA DO VISITANTE
            for ap in apostas:
                if ap.bolao.partida.gols_desafiante < ap.bolao.partida.gols_visitante and ap.qtd_gols_desafiante < ap.qtd_gols_visitante:
                    vencedor = ApostadorVencedorBolao() 
                    vencedor.apostador = ap.apostador
                    vencedor.bolao = ap.bolao
                    vencedor.save()
                    vencedores.append(vencedor)
                    #TODO: colocar aqui o codigo sobre as insercao de vencedores
                    #vencedores.append(ap.apostador)

        if not vencedores: # se ninguem tiver acetado o placar verifica quem ACERTOU O EMPATE ENTRE AS SELECOES
            for ap in apostas:
                if ap.bolao.partida.gols_desafiante == ap.bolao.partida.gols_visitante and ap.qtd_gols_desafiante == ap.qtd_gols_visitante:
                    vencedor = ApostadorVencedorBolao() 
                    vencedor.apostador = ap.apostador
                    vencedor.bolao = ap.bolao
                    vencedor.save()
                    vencedores.append(vencedor)
                    #TODO: colocar aqui o codigo sobre as insercao de vencedores
                    #vencedores.append(ap.apostador)
        
        #relaciona todos os apostadores
        for ap in apostas:
            apostador = Apostador()
            apostador = ap.apostador
            apostadores.append(apostador)

        #TODO: não exite a variavel apostafores aqui dentro que seria justamente a relacao de todas as pessoa que fizeram apostas, vamos ver o que fazer
        self.set_premiacao(apostadores, vencedores) # ao final calcula a premiacao

class ApostadorVencedorBolao(models.Model):
    class Meta:
        unique_together = (('apostador', 'bolao'),)  # cria a relacao semelhante a de chave composta no Django
        verbose_name_plural = "Apostador(es) vencedor(es) bolões"

    # id chave composta por apostador e bolao
    apostador = models.ForeignKey(
        Apostador,
        on_delete=models.CASCADE,
    )  # fk e pk
    bolao = models.ForeignKey(
        Bolao,
        on_delete=models.CASCADE,
    )  # fk e pk

    def __str__(self):
        return self.apostador.__str__() + " << vemcedor >> " + self.bolao.nome.__str__()


class Aposta(models.Model):
    class Meta:
        unique_together = (('apostador', 'bolao'),)

    # id chave composta por apostador e bolao
    apostador = models.ForeignKey(
        Apostador,
        on_delete=models.CASCADE,
    )  # fk e pk
    bolao = models.ForeignKey(
        Bolao,
        on_delete=models.CASCADE,
    )  # fk e pk
    qtd_gols_desafiante = models.PositiveSmallIntegerField()
    qtd_gols_visitante = models.PositiveSmallIntegerField()
    valor = models.FloatField(
        default=5.00,
        editable=False,
    )  # não exibe valor da aposta para se ajustado

    def __str__(self):
        return self.apostador.__str__() + " << aposta >> " + self.bolao.partida.__str__()

# TODO: nao irei usar desta vez, so depois de ajustar, mas eh bastante pratico e auxilia na construcao de formularios dinamicos
class FormUsuarios(forms.ModelForm): # gera o formulario de cadastro de usuarios de forma automatica ESTUDAR PARA APLICAR
    class Meta:
        model = User
        # exclude = (
        #     'last_login ',
        #     'is_superuser ',
        #     'last_login ',
        #     'id',
        #     'is_superuser ',
        #     'is_staff ',
        #     'is_active ',
        #     'date_joined',
        # )
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        )
        widgets = {
            'password': forms.PasswordInput(), # permite ver a senha
            'email': forms.EmailInput() # checa se o e-mail eh valido
        }
