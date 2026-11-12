"""Pacote de serviços: envio de e-mails, geração de relatórios e endereço do evento."""

from .enviar_email import enviar_email_nao_responda
from .relatorios import pedidos_quantidade, pedidos_tipo, pedidos_status, faturamento_periodo, ticket_medio_periodo, faturamento_semanal
from .endereco_evento import apresentar_endereco_evento, validar_endereco_evento
from .bebidas_data import formatar_bebidas, catalogo_previa
