-- =====================================================================
-- Sabor & Clic — Esquema do banco de dados (SQLite)
-- Gerado a partir dos modelos em model/ e da trigger em triggers.py.
-- Reflete a estrutura criada por SQLAlchemy (db.create_all) + a trigger de
-- baixa automática de estoque.
-- =====================================================================

PRAGMA foreign_keys = ON;

-- ------------------------- Permissões e usuários -------------------------
CREATE TABLE IF NOT EXISTS nivel_permissao (
    id_permissao INTEGER PRIMARY KEY,
    nome VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    cpf_criptografado TEXT NOT NULL,
    cpf_hmac VARCHAR(64) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    email_criptografado TEXT NOT NULL,
    email_hmac VARCHAR(64) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT 1,
    criado_em DATETIME NOT NULL,
    id_permissao INTEGER NOT NULL REFERENCES nivel_permissao(id_permissao),
    salario INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS endereco (
    id_endereco INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER REFERENCES usuario(id_usuario),
    nome VARCHAR(150) NOT NULL,
    logradouro VARCHAR(150) NOT NULL,
    numero VARCHAR(20) NOT NULL,
    complemento VARCHAR(100),
    bairro VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    cep VARCHAR(9) NOT NULL
);

CREATE TABLE IF NOT EXISTS log_atividade (
    id_atividade INTEGER PRIMARY KEY AUTOINCREMENT,
    realizado_em DATETIME NOT NULL,
    acao VARCHAR(45) NOT NULL,
    descricao TEXT,
    id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario)
);

CREATE TABLE IF NOT EXISTS token (
    id_token INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_hash TEXT NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT 1,
    tentativas INTEGER NOT NULL DEFAULT 0,
    id_usuario INTEGER NOT NULL REFERENCES usuario(id_usuario),
    criado_em DATETIME NOT NULL
);

-- ------------------------- Serviços e cardápios -------------------------
CREATE TABLE IF NOT EXISTS bancada (
    id_bancada INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(60) NOT NULL,
    descricao TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS servico (
    id_servico INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(60) NOT NULL UNIQUE,
    descricao TEXT NOT NULL,
    slug VARCHAR(120) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS servico_bancada (
    id_servico INTEGER NOT NULL REFERENCES servico(id_servico),
    id_bancada INTEGER NOT NULL REFERENCES bancada(id_bancada),
    PRIMARY KEY (id_servico, id_bancada)
);

CREATE TABLE IF NOT EXISTS cardapio (
    id_cardapio INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(60) NOT NULL,
    descricao TEXT NOT NULL,
    preco_base NUMERIC(10, 2) NOT NULL,
    CONSTRAINT ck_cardapio_preco CHECK (preco_base >= 0)
);

CREATE TABLE IF NOT EXISTS servico_cardapio (
    id_servico INTEGER NOT NULL REFERENCES servico(id_servico),
    id_cardapio INTEGER NOT NULL REFERENCES cardapio(id_cardapio),
    PRIMARY KEY (id_servico, id_cardapio)
);

-- ------------------------- Pratos, ingredientes, fichas, lotes -------------------------
CREATE TABLE IF NOT EXISTS prato (
    id_prato INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(60) NOT NULL,
    descricao TEXT NOT NULL,
    tipo_prato VARCHAR(16) NOT NULL
        CHECK (tipo_prato IN ('entrada', 'acompanhamento', 'prato principal', 'sobremesa')),
    tempo_preparo INTEGER NOT NULL,
    requer_pre_preparo BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS prato_cardapio (
    id_prato INTEGER NOT NULL REFERENCES prato(id_prato),
    id_cardapio INTEGER NOT NULL REFERENCES cardapio(id_cardapio),
    qtd INTEGER NOT NULL,
    descricao TEXT,
    PRIMARY KEY (id_prato, id_cardapio)
);

CREATE TABLE IF NOT EXISTS ingrediente (
    id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(60) NOT NULL,
    unidade VARCHAR(10) NOT NULL,
    qtd NUMERIC(10, 3) NOT NULL DEFAULT 0,
    qtd_min NUMERIC(10, 3) NOT NULL DEFAULT 0,
    CONSTRAINT ck_ingrediente_qtd CHECK (qtd >= 0 AND qtd_min >= 0)
);

CREATE TABLE IF NOT EXISTS ficha_tecnica (
    id_prato INTEGER NOT NULL REFERENCES prato(id_prato),
    id_ingrediente INTEGER NOT NULL REFERENCES ingrediente(id_ingrediente),
    qtd_necessaria NUMERIC(10, 3) NOT NULL,
    PRIMARY KEY (id_prato, id_ingrediente),
    CONSTRAINT ck_ficha_qtd CHECK (qtd_necessaria > 0)
);

CREATE TABLE IF NOT EXISTS bebida (
    id_bebida INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(60) NOT NULL,
    descricao TEXT NOT NULL,
    valor_unitario NUMERIC(10, 2) NOT NULL,
    CONSTRAINT ck_bebida_valor CHECK (valor_unitario >= 0)
);

CREATE TABLE IF NOT EXISTS ficha_tecnica_bebida (
    id_bebida INTEGER NOT NULL REFERENCES bebida(id_bebida),
    id_ingrediente INTEGER NOT NULL REFERENCES ingrediente(id_ingrediente),
    qtd_necessaria INTEGER NOT NULL,
    PRIMARY KEY (id_bebida, id_ingrediente),
    CONSTRAINT ck_ficha_bebida_qtd CHECK (qtd_necessaria > 0)
);

CREATE TABLE IF NOT EXISTS bebida_cardapio (
    id_bebida INTEGER NOT NULL REFERENCES bebida(id_bebida),
    id_cardapio INTEGER NOT NULL REFERENCES cardapio(id_cardapio),
    PRIMARY KEY (id_bebida, id_cardapio)
);

CREATE TABLE IF NOT EXISTS lote (
    id_lote INTEGER PRIMARY KEY AUTOINCREMENT,
    num_lote VARCHAR(60) NOT NULL,
    marca VARCHAR(60) NOT NULL,
    data_recebimento DATETIME NOT NULL,
    data_validade DATE,
    qtd_inicial NUMERIC(10, 3) NOT NULL,
    id_ingrediente INTEGER REFERENCES ingrediente(id_ingrediente)
);

-- ------------------------- Pedidos -------------------------
CREATE TABLE IF NOT EXISTS pedido (
    id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    observacao TEXT,
    status VARCHAR(12) NOT NULL DEFAULT 'aguardando'
        CHECK (status IN ('aguardando', 'confirmado', 'em preparo', 'concluido', 'cancelado')),
    confirmado_em DATETIME,
    criado_em DATETIME NOT NULL,
    num_convidados INTEGER NOT NULL DEFAULT 1,
    valor_total NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    data_evento DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    id_cliente INTEGER NOT NULL REFERENCES usuario(id_usuario),
    id_endereco INTEGER NOT NULL REFERENCES endereco(id_endereco),
    id_chefe INTEGER REFERENCES usuario(id_usuario),
    CONSTRAINT ck_pedido_convidados CHECK (num_convidados > 0),
    CONSTRAINT ck_pedido_valor CHECK (valor_total >= 0)
);

CREATE TABLE IF NOT EXISTS pedido_bebida (
    id_pedido INTEGER NOT NULL REFERENCES pedido(id_pedido),
    id_bebida INTEGER NOT NULL REFERENCES bebida(id_bebida),
    qtd INTEGER NOT NULL,
    valor_total NUMERIC(10, 2) NOT NULL,
    PRIMARY KEY (id_pedido, id_bebida),
    CONSTRAINT ck_pedido_bebida_qtd CHECK (qtd > 0)
);

CREATE TABLE IF NOT EXISTS cardapio_pedido (
    id_cardapio INTEGER NOT NULL REFERENCES cardapio(id_cardapio),
    id_pedido INTEGER NOT NULL REFERENCES pedido(id_pedido),
    id_servico INTEGER NOT NULL REFERENCES servico(id_servico),
    PRIMARY KEY (id_cardapio, id_pedido, id_servico)
);

-- ------------------------- Baixa automática de estoque -------------------------
-- View, tabela auxiliar e trigger (gerado a partir de triggers.py).

CREATE VIEW IF NOT EXISTS consumo_ingrediente_pedido AS
            SELECT
                consumos.id_pedido,
                consumos.id_ingrediente,
                SUM(consumos.qtd_total) AS qtd_total
            FROM (
                -- Consumo dos pratos
                SELECT
                    cp.id_pedido,
                    ft.id_ingrediente,
                    SUM(
                        ft.qtd_necessaria * p.num_convidados
                    ) AS qtd_total
                FROM pedido p
                JOIN cardapio_pedido cp
                    ON cp.id_pedido = p.id_pedido
                JOIN prato_cardapio pc
                    ON pc.id_cardapio = cp.id_cardapio
                JOIN ficha_tecnica ft
                    ON ft.id_prato = pc.id_prato
                GROUP BY
                    cp.id_pedido,
                    ft.id_ingrediente

                UNION ALL

                -- Consumo das bebidas
                SELECT
                    pb.id_pedido,
                    ftb.id_ingrediente,
                    SUM(
                        ftb.qtd_necessaria * pb.qtd
                    ) AS qtd_total
                FROM pedido_bebida pb
                JOIN ficha_tecnica_bebida ftb
                    ON ftb.id_bebida = pb.id_bebida
                GROUP BY
                    pb.id_pedido,
                    ftb.id_ingrediente
            ) AS consumos
            GROUP BY
                consumos.id_pedido,
                consumos.id_ingrediente;

CREATE TABLE IF NOT EXISTS baixa_lote_pedido (
                id_pedido INTEGER NOT NULL,
                id_lote INTEGER NOT NULL,
                qtd_baixada NUMERIC(10, 3) NOT NULL,
                PRIMARY KEY (id_pedido, id_lote)
            );

DROP TRIGGER IF EXISTS baixa_estoque_pedido_confirmado;

CREATE TRIGGER baixa_estoque_pedido_confirmado
            AFTER UPDATE OF status ON pedido
            FOR EACH ROW
            WHEN NEW.status = 'confirmado'
                 AND OLD.status <> 'confirmado'
            BEGIN

                -- VERIFICAÇÃO DO ESTOQUE GERAL E DOS LOTES
                SELECT RAISE(
                    ABORT,
                    'Estoque insuficiente para confirmar o pedido'
                )
                WHERE EXISTS (
                    SELECT 1
                    FROM consumo_ingrediente_pedido c
                    JOIN ingrediente i
                        ON i.id_ingrediente = c.id_ingrediente
                    WHERE c.id_pedido = NEW.id_pedido
                      AND (
                          i.qtd < c.qtd_total
                          OR COALESCE((
                              SELECT SUM(l.qtd_inicial)
                              FROM lote l
                              WHERE l.id_ingrediente =
                                    c.id_ingrediente
                                AND l.qtd_inicial > 0
                                AND (
                                    l.data_validade IS NULL
                                    OR l.data_validade >= date('now')
                                )
                          ), 0) < c.qtd_total
                      )
                );

                -- LIMPA EVENTUAIS REGISTROS ANTERIORES
                DELETE FROM baixa_lote_pedido
                WHERE id_pedido = NEW.id_pedido;

                -- DISTRIBUI A QUANTIDADE ENTRE OS LOTES.
                -- Lotes com validade conhecida vêm primeiro,
                -- em ordem crescente de vencimento.
                -- Lotes sem validade ficam por último.
                INSERT INTO baixa_lote_pedido (
                    id_pedido,
                    id_lote,
                    qtd_baixada
                )
                SELECT
                    id_pedido,
                    id_lote,
                    qtd_baixada
                FROM (
                    SELECT
                        NEW.id_pedido AS id_pedido,
                        l.id_lote AS id_lote,
                        MIN(
                            l.qtd_inicial,
                            MAX(
                                0,
                                c.qtd_total - (
                                    SUM(l.qtd_inicial) OVER (
                                        PARTITION BY l.id_ingrediente
                                        ORDER BY
                                            (l.data_validade IS NULL),
                                            l.data_validade,
                                            l.data_recebimento,
                                            l.id_lote
                                        ROWS BETWEEN
                                            UNBOUNDED PRECEDING
                                            AND CURRENT ROW
                                    ) - l.qtd_inicial
                                )
                            )
                        ) AS qtd_baixada
                    FROM lote l
                    JOIN consumo_ingrediente_pedido c
                        ON c.id_ingrediente = l.id_ingrediente
                    WHERE c.id_pedido = NEW.id_pedido
                      AND l.qtd_inicial > 0
                      AND (
                          l.data_validade IS NULL
                          OR l.data_validade >= date('now')
                      )
                )
                WHERE qtd_baixada > 0;

                -- ATUALIZA A QUANTIDADE RESTANTE DE CADA LOTE
                UPDATE lote
                SET qtd_inicial = qtd_inicial - COALESCE((
                    SELECT SUM(b.qtd_baixada)
                    FROM baixa_lote_pedido b
                    WHERE b.id_pedido = NEW.id_pedido
                      AND b.id_lote = lote.id_lote
                ), 0)
                WHERE id_lote IN (
                    SELECT id_lote
                    FROM baixa_lote_pedido
                    WHERE id_pedido = NEW.id_pedido
                );

                -- ATUALIZA O ESTOQUE GERAL DOS INGREDIENTES
                UPDATE ingrediente
                SET qtd = qtd - (
                    SELECT c.qtd_total
                    FROM consumo_ingrediente_pedido c
                    WHERE c.id_pedido = NEW.id_pedido
                      AND c.id_ingrediente =
                          ingrediente.id_ingrediente
                )
                WHERE id_ingrediente IN (
                    SELECT id_ingrediente
                    FROM consumo_ingrediente_pedido
                    WHERE id_pedido = NEW.id_pedido
                );

                -- LIMPA A TABELA AUXILIAR APÓS A BAIXA
                DELETE FROM baixa_lote_pedido
                WHERE id_pedido = NEW.id_pedido;

            END;;
