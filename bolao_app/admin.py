from django.contrib import admin

# importacao do models para poder registrar e aparecer na area administrativa do sistema
from bolao_app.models import Apostador, Aposta, Selecao, Partida, Bolao, ApostadorVencedorBolao


# C:\git-repositorios\python\projetos_pyc - C:\git-repositorios\python\projetos_pyc\ve_s -
# criacao de classes auxiliares para personalizar o formulario do crud do Djando Admin para nosso models
class ApostadorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'credito', 'premiacao_ganha','qtd_vitorias')  # campos que desejamos exibir na listagem
    list_display_links = ('usuario',)  # campos que podemos clicar para abrir o elemento para edicao
    #list_filter = ('usuario',)  # campos que podem ser filtrados
    list_editable = ('credito',)
    search_fields = ('usuario',)  # insere campo de busca pelo camos informados na tupla
    list_per_page = 25  # qtd de registros por pagina


class SelecaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'qtd_titulos',)
    list_display_links = ('nome',)
    #list_filter = ('nome',)
    list_per_page = 25


class PartidaAdmin(admin.ModelAdmin):
    list_display = ('selecao_desafiante', 'gols_desafiante', 'selecao_visitante', 'gols_visitante', 'estadio' ,'finalizada',)
    list_display_links = ('selecao_desafiante', 'selecao_visitante',)
    #list_filter = ('selecao_desafiante', 'selecao_visitante', 'estadio',)
    list_editable = ('finalizada','gols_desafiante', 'gols_visitante',)
    list_per_page = 25


class BolaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'partida', 'premiacao', 'valor_disputado','esta_ativo',)
    list_display_links = ('nome',)
    list_editable = ('valor_disputado','premiacao', 'esta_ativo',)
    #list_filter = ('nome', 'partida')
    list_per_page = 25


class ApostaAdmin(admin.ModelAdmin):
    list_display = ('id', 'apostador', 'bolao', 'qtd_gols_desafiante', 'qtd_gols_visitante', 'valor',)
    list_display_links = ('id', 'apostador',)
    #list_filter = ('apostador', 'bolao',)
    list_per_page = 25


# Registro dos models criados para mostrar na area administrativa
admin.site.register(Apostador, ApostadorAdmin)
admin.site.register(Aposta, ApostaAdmin)
admin.site.register(Selecao, SelecaoAdmin)
admin.site.register(Partida, PartidaAdmin)
admin.site.register(Bolao, BolaoAdmin)
admin.site.register(ApostadorVencedorBolao)
