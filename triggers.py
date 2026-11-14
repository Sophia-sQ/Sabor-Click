"""Criação da trigger de baixa automática de estoque no banco (SQLite)."""

from sqlalchemy import text
from database import db


def criar_trigger_baixa_estoque() -> None:
    """Cria a view e as triggers de baixa de estoque e descarte de lotes.

    Monta a estrutura necessária para controlar o estoque quando um pedido é
    confirmado (abordagem A: estoque geral do ingrediente desacoplado dos
    lotes):
      1. view `consumo_ingrediente_pedido`: consolida o consumo de cada
         ingrediente por pedido (pratos e bebidas somados).
      2. trigger `baixa_estoque_pedido_confirmado`: ao mudar o status de um
         pedido para 'confirmado', valida o estoque comparando apenas
         `ingrediente.qtd` com o consumo total e, se houver saldo, dá baixa
         somente em `ingrediente.qtd`. Não consulta nem atualiza lotes.
      3. trigger `descartar_lotes_vencidos_ao_confirmar`: no mesmo evento,
         zera o `qtd_inicial` dos lotes vencidos (data_validade NÃO NULA e
         anterior a date('now')), marcando-os como descartados. Esse descarte
         TAMBÉM reduz `ingrediente.qtd`: para cada ingrediente com lotes
         vencidos, subtrai de `ingrediente.qtd` a soma do `qtd_inicial` dos
         lotes vencidos descartados, com clamp em zero (MAX(0, ...)) para não
         violar o CHECK `qtd >= 0 AND qtd_min >= 0` nem abortar a confirmação.
         A subtração em `ingrediente.qtd` ocorre ANTES de zerar o
         `lote.qtd_inicial`, senão a quantidade a subtrair já teria virado 0.
         Lotes sem validade (data_validade NULL) nunca vencem; lotes válidos
         permanecem intactos.

    A operação é idempotente (usa IF NOT EXISTS / DROP IF EXISTS) e executa
    dentro de uma transação com a engine do SQLAlchemy.
    """

    with db.engine.begin() as conexao:

        # Limpa a tabela auxiliar de distribuição por lote usada por versões
        # antigas da trigger (abordagem FEFO). A baixa não distribui mais por
        # lote, então a tabela deixa de existir.
        conexao.execute(text("DROP TABLE IF EXISTS baixa_lote_pedido"))

        # 1. Calcula o consumo total de cada ingrediente por pedido.
        # Inclui pratos e bebidas e soma ingredientes repetidos.
        conexao.execute(text("DROP VIEW IF EXISTS consumo_ingrediente_pedido"))
        conexao.execute(text("""
            CREATE VIEW consumo_ingrediente_pedido AS
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
                        ft.qtd_necessaria * cp.num_convidados
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

        # Remove a trigger de baixa antiga, se existir.
        conexao.execute(text("""
            DROP TRIGGER IF EXISTS baixa_estoque_pedido_confirmado
        """))

        # 2. Cria a trigger de baixa (abordagem A: só ingrediente.qtd).
        conexao.execute(text("""
            CREATE TRIGGER baixa_estoque_pedido_confirmado
            AFTER UPDATE OF status ON pedido
            FOR EACH ROW
            WHEN NEW.status = 'confirmado'
                 AND OLD.status <> 'confirmado'
            BEGIN

                -- VERIFICAÇÃO DO ESTOQUE GERAL DO INGREDIENTE.
                -- Reprova o pedido somente quando o estoque geral de algum
                -- ingrediente é menor que o consumo total do pedido. Não
                -- considera lotes.
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
                      AND i.qtd < c.qtd_total
                );

                -- ATUALIZA O ESTOQUE GERAL DOS INGREDIENTES.
                -- Decrementa ingrediente.qtd exatamente no consumo total do
                -- pedido para cada ingrediente consumido.
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

            END;
        """))

        # Remove a trigger de descarte antiga, se existir.
        conexao.execute(text("""
            DROP TRIGGER IF EXISTS descartar_lotes_vencidos_ao_confirmar
        """))

        # 3. Cria a trigger de descarte de lotes vencidos.
        # Reduz ingrediente.qtd pela soma do qtd_inicial dos lotes vencidos e,
        # em seguida, zera o qtd_inicial desses lotes com validade conhecida e
        # já vencida, marcando-os como descartados. Lotes sem validade
        # (data_validade NULL) nunca vencem; lotes ainda válidos permanecem
        # intactos. O UPDATE em ingrediente vem ANTES do UPDATE que zera
        # lote.qtd_inicial, senão a quantidade a subtrair já teria virado 0.
        conexao.execute(text("""
            CREATE TRIGGER descartar_lotes_vencidos_ao_confirmar
            AFTER UPDATE OF status ON pedido
            FOR EACH ROW
            WHEN NEW.status = 'confirmado'
                 AND OLD.status <> 'confirmado'
            BEGIN

                -- REDUZ O ESTOQUE GERAL PELO TOTAL VENCIDO DESCARTADO.
                -- Para cada ingrediente com lotes vencidos, subtrai de
                -- ingrediente.qtd a soma do qtd_inicial desses lotes, com
                -- clamp em zero (MAX) para não violar o CHECK nem abortar.
                -- Deve rodar ANTES de zerar lote.qtd_inicial.
                UPDATE ingrediente
                SET qtd = MAX(
                    0,
                    qtd - (
                        SELECT COALESCE(SUM(l.qtd_inicial), 0)
                        FROM lote l
                        WHERE l.id_ingrediente =
                              ingrediente.id_ingrediente
                          AND l.data_validade IS NOT NULL
                          AND l.data_validade < date('now')
                          AND l.qtd_inicial > 0
                    )
                )
                WHERE id_ingrediente IN (
                    SELECT l.id_ingrediente
                    FROM lote l
                    WHERE l.data_validade IS NOT NULL
                      AND l.data_validade < date('now')
                      AND l.qtd_inicial > 0
                );

                -- MARCA OS LOTES VENCIDOS COMO DESCARTADOS.
                UPDATE lote
                SET qtd_inicial = 0
                WHERE data_validade IS NOT NULL
                  AND data_validade < date('now')
                  AND qtd_inicial > 0;

            END;
        """))
