from sqlalchemy import text
from database import db


def criar_trigger_baixa_estoque():
    with db.engine.begin() as conexao:

        # 1. Calcula o consumo total de cada ingrediente por pedido.
        # Inclui pratos e bebidas e soma ingredientes repetidos.
        conexao.execute(text("""
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
                consumos.id_ingrediente
        """))

        # 2. Guarda temporariamente a distribuição da baixa
        # entre os lotes de cada pedido.
        conexao.execute(text("""
            CREATE TABLE IF NOT EXISTS baixa_lote_pedido (
                id_pedido INTEGER NOT NULL,
                id_lote INTEGER NOT NULL,
                qtd_baixada NUMERIC(10, 3) NOT NULL,
                PRIMARY KEY (id_pedido, id_lote)
            )
        """))

        # Remove a trigger antiga, se existir.
        conexao.execute(text("""
            DROP TRIGGER IF EXISTS baixa_estoque_pedido_confirmado
        """))

        # 3. Cria a nova trigger.
        conexao.execute(text("""
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

            END;
        """))