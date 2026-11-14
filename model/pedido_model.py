"""Modelos e operações de pedidos, bebidas e suas associações."""

from datetime import datetime
from zoneinfo import ZoneInfo

from model.usuario_model import registrar_log

from database import db, Base
from sqlalchemy.exc import  SQLAlchemyError
from sqlalchemy import extract, func


# Mapeia o nome lógico da coluna de data aceito pelas consultas de relatório
# para o atributo real do modelo Pedido. Permite que os relatórios escolham o
# critério de data (confirmado_em para financeiro, criado_em para volume) sem
# expor o modelo diretamente ao chamador.
_COLUNAS_DATA_PEDIDO = {
    "data_evento": lambda: Pedido.data_evento,
    "confirmado_em": lambda: Pedido.confirmado_em,
    "criado_em": lambda: Pedido.criado_em,
}


def _resolver_coluna_data(coluna_data: str):
    """Resolve o nome lógico de uma coluna de data para o atributo do Pedido.

    Args:
        coluna_data (str): 'data_evento', 'confirmado_em' ou 'criado_em'.

    Returns:
        O atributo de coluna correspondente, ou None se o nome for inválido.
    """
    fabrica = _COLUNAS_DATA_PEDIDO.get(coluna_data)
    if fabrica is None:
        return None
    return fabrica()


# TABELAS
class Pedido(db.Model):
    """Pedido de um cliente, com status, datas, valor e vínculos de cliente/endereço/chefe."""
    __tablename__ = "pedido"

    id_pedido = db.Column(db.Integer, primary_key=True, autoincrement=True)
    observacao = db.Column(db.Text, nullable=True)  # Opcional
    status = db.Column(
        db.Enum("aguardando", "confirmado", "em preparo", "concluido", "cancelado", name="status_pedido"),default="aguardando",nullable=False)
    confirmado_em = db.Column(db.DateTime, nullable=True)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    data_evento = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)

    id_cliente = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False)
    id_endereco = db.Column(db.Integer, db.ForeignKey("endereco.id_endereco"), nullable=False)
    id_chefe = db.Column(db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=True)
    #id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), nullable=False)
    #id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), nullable=False)

    __table_args__ = (
        db.CheckConstraint("valor_total >= 0", name="ck_pedido_valor"),
    )

class Bebida(db.Model):
    """Bebida que pode compor um pedido."""
    __tablename__ = "bebida"

    id_bebida = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    # slug usado para resolver a imagem da bebida em docs/imagens-bebidas.json;
    # None quando a bebida não tem imagem enviada pelo admin (as avulsas seed
    # continuam resolvíveis via fallback por nome em services.bebidas_data).
    imagem_slug = db.Column(db.String(120), nullable=True)
    # Soft delete: bebidas "removidas" ficam ativo=False e somem das listagens do
    # cliente (listar_bebidas_ativas), preservando a integridade referencial.
    ativo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.text("1"))

    __table_args__ = (
        db.CheckConstraint("valor_unitario >= 0", name="ck_bebida_valor"),
    )
    
    def __init__(self, nome: str, descricao: str, valor_unitario, imagem_slug=None, ativo=True):
        self.nome = nome
        self.descricao = descricao
        self.valor_unitario = valor_unitario
        self.imagem_slug = imagem_slug
        self.ativo = ativo


class PedidoBebida(db.Model):
    """Associação entre pedido e bebida, com quantidade e valor total."""
    __tablename__ = "pedido_bebida"


    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), primary_key=True)
    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_bebida"), primary_key=True)

    qtd = db.Column(db.Integer, nullable=False)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        db.CheckConstraint("qtd > 0", name="ck_pedido_bebida_qtd"),
    )
    
    def __init__(self, id_pedido: int, id_bebida: int, qtd: int, valor_total):
        self.id_pedido = id_pedido
        self.id_bebida = id_bebida
        self.qtd = qtd
        self.valor_total = valor_total
    
# Tabela de associação entre cardápio e bebida

class BebidaCardapio(db.Model):
    """Associação entre bebida e cardápio."""
    __tablename__ = "bebida_cardapio"

    id_bebida = db.Column(db.Integer, db.ForeignKey("bebida.id_bebida"), primary_key=True)
    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)

class CardapioPedido(db.Model):
    """Associação entre cardápio, pedido e serviço, com o nº de convidados do cardápio."""
    __tablename__ = "cardapio_pedido"

    id_cardapio = db.Column(db.Integer, db.ForeignKey("cardapio.id_cardapio"), primary_key=True)
    id_pedido = db.Column(db.Integer, db.ForeignKey("pedido.id_pedido"), primary_key=True)
    id_servico = db.Column(db.Integer, db.ForeignKey("servico.id_servico"), primary_key=True)
    num_convidados = db.Column(db.Integer, nullable=False, default=1)

    __table_args__ = (
        db.CheckConstraint("num_convidados > 0", name="ck_cardapio_pedido_convidados"),
    )

    def __init__(self, id_cardapio: int, id_pedido: int, id_servico: int, num_convidados: int = 1):
        self.id_cardapio = id_cardapio
        self.id_pedido = id_pedido
        self.id_servico = id_servico
        self.num_convidados = num_convidados

# ======================================================

# CRUD BEBIDA
def criar_bebida(nome: str, descricao: str, valor_unitario: float, imagem_slug=None) -> Bebida:
    """Cria uma bebida e registra o log da operação.

    Args:
        nome (str): nome da bebida.
        descricao (str): descrição da bebida.
        valor_unitario (float): valor unitário.
        imagem_slug (str | None, optional): slug da imagem em
            docs/imagens-bebidas.json; None quando a bebida é criada sem imagem.

    Returns:
        Bebida: a bebida criada.
    """
    bebida = Bebida(nome=nome, descricao=descricao, valor_unitario=valor_unitario, imagem_slug=imagem_slug)
    db.session.add(bebida)
    db.session.commit()
    registrar_log("CRIACAO BEBIDA", f"Usuário criou a bebida {bebida.nome}")
    return bebida

def buscar_bebida_por_id(id_bebida: int) -> Bebida | None:
    """Busca uma bebida pelo id. Retorna None se não existir."""
    return db.session.get(Bebida, id_bebida)

def buscar_bebida_por_nome(nome_bebida: str) -> Bebida | None:
    """Busca uma bebida pelo nome exato. Retorna None se não existir."""
    bebida = db.session.execute(
        db.select(Bebida).where(Bebida.nome == nome_bebida),
    ).scalar_one_or_none()

    if bebida:
        return bebida
    return None

def listar_bebidas() -> list[Bebida]:
    """Lista todas as bebidas cadastradas."""
    return db.session.query(Bebida).all()

def buscar_bebidas(busca: str = "") -> list:
    """Busca bebidas por nome (correspondência parcial).

    Args:
        busca (str, optional): termo de busca. Padrão: "".

    Returns:
        list: bebidas encontradas, ordenadas por nome (vazia se não houver).
    """
    stmt = db.select(Bebida)
    termo = busca.strip()
    if termo:
        stmt = stmt.where(Bebida.nome.like(f"%{termo}%"))
    stmt = stmt.order_by(Bebida.nome)
    return db.session.execute(stmt).scalars().all()


def atualizar_bebida(id_bebida: int, nome=None, descricao=None, valor_unitario=None, imagem_slug=None, ativo=None) -> bool:
    """Atualiza os dados de uma bebida (campos None não são alterados).

    Args:
        id_bebida (int): identificador da bebida.
        nome (str | None, optional): novo nome.
        descricao (str | None, optional): nova descrição.
        valor_unitario (float | None, optional): novo valor unitário.
        imagem_slug (str | None, optional): novo slug de imagem; só é alterado
            quando fornecido (não-None).
        ativo (bool | None, optional): novo estado de ativação; só é alterado
            quando fornecido (não-None).

    Returns:
        bool: True se atualizada; False se a bebida não existir.
    """
    bebida = db.session.get(Bebida, id_bebida)

    if not bebida:
        return False

    if nome is not None:
        bebida.nome = nome
    if descricao is not None:
        bebida.descricao = descricao
    if valor_unitario is not None:
        bebida.valor_unitario = valor_unitario
    if imagem_slug is not None:
        bebida.imagem_slug = imagem_slug
    if ativo is not None:
        bebida.ativo = ativo
    db.session.commit()
    registrar_log("ATUALIZACAO BEBIDA", f"Usuário atualizou a bebida {id_bebida}")
    return True

def desativar_bebida(id_bebida: int) -> bool:
    """Desativa uma bebida (soft delete): seta ativo=False e persiste.

    Mantém o registro no banco (preservando vínculos como pedidos antigos) e
    apenas o esconde das listagens voltadas ao cliente.

    Args:
        id_bebida (int): identificador da bebida.

    Returns:
        bool: True se desativada; False se a bebida não existir.
    """
    bebida = db.session.get(Bebida, id_bebida)
    if not bebida:
        return False
    bebida.ativo = False
    db.session.commit()
    registrar_log("DESATIVACAO BEBIDA", f"Usuario desativou bebida {bebida.nome}")
    return True

def listar_bebidas_ativas() -> list[Bebida]:
    """Lista apenas as bebidas ativas (ativo==True)."""
    return db.session.execute(
        db.select(Bebida).where(Bebida.ativo == True),  # noqa: E712
    ).scalars().all()

def deletar_bebida(id_bebida: int) -> bool:
    """Remove uma bebida pelo id. Retorna False se não existir."""
    bebida = db.session.get(Bebida, id_bebida)
    if not bebida:
        return False
    db.session.delete(bebida)
    db.session.commit()
    registrar_log("REMOCAO BEBIDA", f"Usuario deletou bebida {bebida.nome}")

    return True

def associar_bebida_cardapio(id_bebida: int, id_cardapio: int) -> tuple[int, int]:
    """Associa uma bebida a um cardápio.

    Args:
        id_bebida (int): identificador da bebida.
        id_cardapio (int): identificador do cardápio.

    Returns:
        tuple[int, int]: par (id_bebida, id_cardapio) associado.
    """
    novo_item = BebidaCardapio(id_bebida=id_bebida,id_cardapio=id_cardapio,
    )
    db.session.add(novo_item)
    db.session.commit()
    registrar_log("CRIACAO BEBIDA_CARDAPIO", f"Usuário associou a bebida {id_bebida} ao cardápio {id_cardapio}")
    return (id_bebida, id_cardapio)

# CRUD - PEDIDO
def criar_pedido(id_cliente: int, id_endereco: int, valor_total: float, data_evento: str, hora_inicio: str, hora_fim: str, cardapios: list[dict], observacao: str | None = None, bebidas: list[dict] | None = None) -> Pedido | None:
    """Cria um pedido e associa seus cardápios e bebidas (quando houver).

    Persiste o pedido e seus vínculos em uma única transação.

    Args:
        id_cliente (int): identificador do cliente.
        id_endereco (int): identificador do endereço de entrega.
        valor_total (float): valor total do pedido.
        data_evento (str): data do evento.
        hora_inicio (str): hora de início.
        hora_fim (str): hora de término.
        cardapios (list[dict]): cardápios do pedido (cada item com 'id_cardapio',
            'id_servico' e 'qtd' - o nº de convidados daquele cardápio).
        observacao (str | None, optional): observação do pedido.
        bebidas (list[dict] | None, optional): bebidas do pedido (cada item com
            'id_bebida', 'qtd' e 'valor_total').

    Returns:
        Pedido | None: o pedido criado; None em caso de violação de integridade.
    """
    novo_pedido = Pedido(
        id_cliente=id_cliente,
        id_endereco=id_endereco,
        #id_servico=id_servico,
        #id_cardapio=id_cardapio,
        valor_total=valor_total,
        data_evento=data_evento,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
        observacao=observacao,

    )
    try:
        db.session.add(novo_pedido)
        db.session.flush()

        for cardapio in cardapios:
            p_c = CardapioPedido(
                id_cardapio=cardapio["id_cardapio"],
                id_pedido=novo_pedido.id_pedido,
                id_servico=cardapio["id_servico"],
                num_convidados=cardapio["qtd"],
            )
            db.session.add(p_c)

        db.session.flush()
        #verifica se o pedido tem bebida, se tiver adiciona
        if bebidas:
            for item in bebidas:
                # PedidoBebida espera valor_total. Usa item["valor_total"]
                # quando disponível; caso contrário calcula a partir do
                # valor_unitario multiplicado pela quantidade.
                valor_total_bebida = item.get("valor_total")
                if valor_total_bebida is None:
                    valor_total_bebida = item["valor_unitario"] * item["qtd"]
                p_b = PedidoBebida(
                    id_pedido=novo_pedido.id_pedido,
                    id_bebida=item["id_bebida"],
                    qtd=item["qtd"],
                    valor_total=valor_total_bebida,
                )
                db.session.add(p_b)

        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return None

    registrar_log("PEDIDO", f"Pedido {novo_pedido.id_pedido} criado.")
    return novo_pedido

def buscar_pedido_por_id(id_pedido: int) -> Pedido | None:
    """Busca um pedido pelo id. Retorna None se não existir."""
    return db.session.get(Pedido, id_pedido)

def listar_pedidos_por_cliente(id_cliente: int) -> list[Pedido]:
    """Lista todos os pedidos realizados por um cliente."""
    return db.session.query(Pedido).filter_by(id_cliente=id_cliente).all()

def listar_pedidos_periodo(ano, mes, dia, status=None, coluna_data="data_evento") -> list[Pedido] | None:
    """Retorna os pedidos de um status até certo dia de um mês/ano específicos.

    Args:
        ano (int | str): ano de referência (deve ser numérico).
        mes (int | str): mês de referência (deve ser numérico, 1 a 12).
        dia (int | str): dia de referência (deve ser numérico, 1 a 31).
        status (str | None, optional): status para filtragem. Padrão: None.
        coluna_data (str, optional): coluna de data usada no filtro:
            'data_evento', 'confirmado_em' ou 'criado_em'. Padrão: 'data_evento'.
            Como confirmado_em/criado_em são DateTime, o filtro por mês/ano/dia
            usa extract(), que compara apenas o componente de data e portanto
            cobre o dia inteiro independentemente do horário. Pedidos cuja coluna
            escolhida seja NULL (ex.: confirmado_em de um pedido não confirmado)
            ficam naturalmente de fora.

    Returns:
        list[Pedido] | None: lista de pedidos no período (vazia se não houver);
        None se algum parâmetro for inválido.
    """
    try:
        ano=int(ano)
        mes=int(mes)
        dia=int(dia)
    except (ValueError, TypeError):
        return None

    if not 1 <= mes <= 12 or not 1 <= dia <= 31:
        return None

    coluna = _resolver_coluna_data(coluna_data)
    if coluna is None:
        return None

    return db.session.execute(
        db.select(Pedido).where(
            Pedido.status==status,
            extract("month", coluna) == mes,
            extract("year", coluna) == ano,
            extract("day", coluna) <= dia,
        ),
    ).scalars().all()

def listar_pedidos_entre_datas(ano, mes, dia, ano_final=None, mes_final=None, dia_final=None, status="concluido", coluna_data="data_evento") -> list[Pedido] | None:
    """Retorna os pedidos de um status entre duas datas (inclusive).

    Quando a data final não é informada, assume a data de hoje.

    Args:
        ano (int | str): ano da data inicial.
        mes (int | str): mês da data inicial (1 a 12).
        dia (int | str): dia da data inicial.
        ano_final (int | str | None, optional): ano da data final.
        mes_final (int | str | None, optional): mês da data final.
        dia_final (int | str | None, optional): dia da data final.
        status (str, optional): status para filtragem. Padrão: "concluido".
        coluna_data (str, optional): coluna de data usada no filtro:
            'data_evento', 'confirmado_em' ou 'criado_em'. Padrão: 'data_evento'.
            Como confirmado_em/criado_em são DateTime e os limites são datas, o
            limite superior é comparado via func.date(coluna) <= data_fim para
            cobrir o dia inteiro (não deixando de fora pedidos com horário após
            00:00 no dia final). Pedidos cuja coluna escolhida seja NULL ficam de
            fora naturalmente.

    Returns:
        list[Pedido] | None: pedidos no intervalo (vazia se não houver); None se
        os parâmetros forem inválidos ou a data final for anterior à inicial.
    """
    from utils import hoje, para_data

    if not (ano_final or mes_final or dia_final):
        ano_final=hoje().year
        mes_final=hoje().month
        dia_final=hoje().day

    try:
        # para_data espera (dia, mes, ano); passar na ordem (ano, mes, dia)
        # montava datas inválidas (ex.: dia=2026) e fazia a função sempre
        # retornar None, zerando os relatórios que dependem dela.
        data_inicio = para_data(int(dia), int(mes), int(ano))
        data_fim = para_data(int(dia_final), int(mes_final), int(ano_final))
    except (ValueError, TypeError):
        return None

    if data_fim < data_inicio:
        return None

    coluna = _resolver_coluna_data(coluna_data)
    if coluna is None:
        return None

    return db.session.execute(
        db.select(Pedido).where(
            Pedido.status == status,
            func.date(coluna) >= data_inicio,
            func.date(coluna) <= data_fim,
        ),
    ).scalars().all()

def listar_pedido_por_status(status: str = "aguardando") -> list[Pedido]:
    """Lista os pedidos de um determinado status.

    Args:
        status (str, optional): status desejado. Padrão: "aguardando".

    Returns:
        list[Pedido]: pedidos encontrados com o status informado.
    """
    
    return db.session.query(Pedido).filter_by(status=status).all()

def listar_pedidos_em_andamento() -> list[Pedido]:
    """Lista os pedidos em andamento (ativos sendo trabalhados).

    Considera "em andamento" os pedidos cujo status é 'confirmado' ou
    'em preparo': já aceitos pela cozinha e ainda não encerrados. Pedidos
    'aguardando' continuam na fila (ainda não aceitos) e 'concluido'/'cancelado'
    já estão finalizados, por isso ficam de fora. A ordenação prioriza a data do
    evento mais próxima e, em empate, a ordem de criação.

    Returns:
        list[Pedido]: pedidos em andamento ordenados por data do evento e criação.
    """

    return (
        db.session.query(Pedido)
        .filter(Pedido.status.in_(("confirmado", "em preparo")))
        .order_by(Pedido.data_evento.asc(), Pedido.criado_em.asc())
        .all()
    )

def buscar_pedido_por_chefe(id_chefe: int) -> Pedido | None:
    """Monta a consulta dos pedidos atribuídos a um chefe.

    Args:
        id_chefe (int): identificador do chefe responsável.

    Returns:
        Pedido: Pedido vinculado ao chefe.
    """
    
    return db.session.query(Pedido).filter_by(id_chefe=id_chefe).first()


def buscar_pedido_ativo_por_chefe(id_chefe: int) -> Pedido | None:
    """Retorna o pedido ATIVO mais recente atribuído a um chefe.

    Diferente de ``buscar_pedido_por_chefe`` (que devolve o primeiro pedido sem
    ordenação nem filtro de status), esta consulta ignora pedidos já encerrados
    ('concluido'/'cancelado') e, havendo mais de um ativo, prioriza o mais
    recente (``criado_em``/``id_pedido`` desc). Assim um chefe que já concluiu um
    pedido antigo não fica preso a ele nem o vê na bancada de preparo.

    Args:
        id_chefe (int): identificador do chefe responsável.

    Returns:
        Pedido | None: pedido ativo mais recente do chefe; None se não houver.
    """

    return (
        db.session.query(Pedido)
        .filter(Pedido.id_chefe == id_chefe)
        .filter(Pedido.status.notin_(("concluido", "cancelado")))
        .order_by(Pedido.criado_em.desc(), Pedido.id_pedido.desc())
        .first()
    )
    
def atualizar_pedido(id_pedido: int, status=None, confirmado_em=None, id_chefe=None, observacao=None, valor_total=None) -> bool:
    """Atualiza dados cadastrais e de status de um pedido (campos None são ignorados).

    Args:
        id_pedido (int): identificador do pedido.
        status (str | None, optional): novo status.
        confirmado_em (datetime | None, optional): data/hora de confirmação.
        id_chefe (int | None, optional): identificador do chefe responsável.
        observacao (str | None, optional): nova observação.
        valor_total (float | None, optional): novo valor total.

    Returns:
        bool: True se atualizado; False se o pedido não existir.

    Raises:
        SQLAlchemyError: quando o commit falha (ex.: a trigger de baixa de
            estoque aborta o pedido via RAISE(ABORT, 'Estoque insuficiente
            para confirmar o pedido'), que chega como OperationalError, ou
            qualquer outra violação de integridade). A sessão sofre rollback
            antes do re-lançamento para não deixar a transação em estado sujo.
            Antes esta função engolia o erro e retornava None, o que impedia o
            chamador de distinguir o abort de estoque de outras falhas; agora o
            erro é propagado para o chamador decidir a mensagem/status.
    """
    pedido = db.session.get(Pedido, id_pedido)
    if not pedido:
        return False

    if status is not None:
        pedido.status = status
    if confirmado_em is not None:
        pedido.confirmado_em = confirmado_em
    if id_chefe is not None:
        pedido.id_chefe = id_chefe
    if observacao is not None:
        pedido.observacao = observacao
    if valor_total is not None:
        pedido.valor_total = valor_total

    try:
        db.session.commit()
    except SQLAlchemyError:
        # Desfaz a transação pendente e propaga o erro. O chamador inspeciona
        # a exceção (ou sua .orig) para distinguir o abort de estoque dos
        # demais erros e devolver a mensagem/status corretos.
        db.session.rollback()
        raise

    registrar_log("ATUALIZACAO PEDIDO", f"Dados do pedido {id_pedido} atualizados.")
    return True

def deletar_pedido(id_pedido: int) -> bool:
    """Remove um pedido pelo id. Retorna False se não existir."""
    pedido = db.session.get(Pedido, id_pedido)
    if not pedido:
        return False

    db.session.delete(pedido)
    db.session.commit()
    registrar_log("REMOCAO PEDIDO", f"Pedido {id_pedido} removido do sistema.")
    return True



#PEDIDO_BEBIDA
def adicionar_bebida_ao_pedido(id_pedido: int, id_bebida: int, qtd: int, valor_unitario: float) -> bool:
    """Adiciona uma bebida a um pedido ou soma a quantidade, se já existir.

    Args:
        id_pedido (int): identificador do pedido.
        id_bebida (int): identificador da bebida.
        qtd (int): quantidade a adicionar.
        valor_unitario (float): valor unitário da bebida.

    Returns:
        bool: True se adicionada/atualizada; False se o pedido ou a bebida não
        existirem.
    """
    pedido = db.session.get(Pedido, id_pedido)
    bebida = db.session.get(Bebida, id_bebida)
    if not pedido or not bebida:
        return False

    item = db.session.get(PedidoBebida, (id_pedido, id_bebida))
    if item:
        item.qtd += qtd
    else:
        # PedidoBebida espera valor_total: valor_unitario * qtd.
        item = PedidoBebida(
            id_pedido=id_pedido,
            id_bebida=id_bebida,
            qtd=qtd,
            valor_total=valor_unitario * qtd,
        )
        db.session.add(item)

    db.session.commit()
    return True

def remover_bebida_do_pedido(id_pedido: int, id_bebida: int) -> bool:
    """Remove uma bebida de um pedido. Retorna False se o vínculo não existir."""
    item = db.session.get(PedidoBebida, (id_pedido, id_bebida))
    if not item:
        return False

    db.session.delete(item)
    db.session.commit()
    return True

def listar_bebidas_do_pedido(id_pedido: int) -> list[PedidoBebida]:
    """Busca todas as bebidas separadas de um determinado pedido"""
    itens = db.session.query(PedidoBebida).filter_by(id_pedido=id_pedido).all()
    if itens:
        return itens
    return None

# CRUD CardapioPedido
def criar_cardapio_pedido(id_cardapio: int, id_pedido: int, id_servico: int, num_convidados: int = 1) -> CardapioPedido | None:
    """Relaciona um cardápio a um pedido (e serviço).

    Args:
        id_cardapio (int): identificador do cardápio.
        id_pedido (int): identificador do pedido.
        id_servico (int): identificador do serviço.
        num_convidados (int, optional): nº de convidados do cardápio. Padrão: 1.

    Returns:
        CardapioPedido | None: a associação criada; None em caso de violação de
        integridade.
    """

    cardapio_pedido=CardapioPedido(id_cardapio, id_pedido, id_servico, num_convidados)

    db.session.add(cardapio_pedido)

    try:
        db.session.commit()
        return cardapio_pedido
    except SQLAlchemyError:
        db.session.rollback()
        return None

def buscar_cardapios_pedido(id_pedido: int) -> list[CardapioPedido]:
    """Retorna todas as associações cardápio-pedido de um pedido."""
    """Retorna todos os cardápios relacionados a um pedido."""
    return db.session.execute(
        db.select(CardapioPedido).where(
    CardapioPedido.id_pedido == id_pedido,
        ),
    ).scalars().all()

def deletar_cardapios_pedido(id_pedido: int) -> bool:
    """Remove todas as associações de cardápio de um pedido.

    Args:
        id_pedido (int): identificador do pedido.

    Returns:
        bool: True se a remoção ocorreu; False em caso de violação de integridade.
    """
    try:
        db.session.execute(
            db.delete(CardapioPedido).where(
                CardapioPedido.id_pedido == id_pedido,
            ),
        )
        db.session.commit()
        return True

    except SQLAlchemyError:
        db.session.rollback()
        return False
