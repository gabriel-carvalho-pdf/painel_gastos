from django.contrib import admin
from .models import Despesa
from django.contrib import admin
from .models import Feedback 
admin.site.register(Despesa)


@admin.register(Feedback) 
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'data_envio', 'mensagem')
    list_filter = ('data_envio', 'usuario')
    search_fields = ('usuario__username', 'mensagem')
    readonly_fields = ('usuario', 'mensagem', 'data_envio') # Impede edição acidental