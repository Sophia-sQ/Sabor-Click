
# Importa text para executar comandos SQL pelo SQLAlchemy
from sqlalchemy import text

# Importa a conexão com o banco de dados do projeto
from database import db


def criar_trigger_baixa_estoque():
    # Comando SQL que cria a trigger no SQLite
    sql = """
    CREATE TRIGGER baixa_estoque_pedido_confirmado

    -- Aciona quando o status do pedido é atualizado
    AFTER UPDATE OF status ON pedido

    -- Executa para cada pedido atualizado
    FOR EACH ROW

    -- Só executa ao passar para confirmado
    WHEN NEW.status = 'confirmado'
         AND OLD.status <> 'confirmado'

    BEGIN

        -- ==========================================
        -- 1. VERIFICA SE EXISTE ESTOQUE SUFICIENTE
        -- ==========================================

        -- Interrompe a confirmação se faltar algum ingrediente
        SELECT RAISE(
            ABORT,
            'Estoque insuficiente para confirmar o pedido'
        )
        WHERE EXISTS (

            -- Soma o consumo de cada ingrediente,
            -- considerando pratos e bebidas
            SELECT 1
            FROM (
                SELECT
                    consumos.id_ingrediente,
                    SUM(consumos.qtd_total) AS qtd_total
                FROM (

                    -- CONSUMO DOS PRATOS
                    SELECT
                        ft.id_ingrediente,
                        SUM(
                            ft.qtd_necessaria * NEW.num_convidados
                        ) AS qtd_total
                    FROM cardapio_pedido cp

                    -- Encontra os pratos de cada cardápio
                    JOIN prato_cardapio pc
                        ON pc.id_cardapio = cp.id_cardapio

                    -- Encontra os ingredientes dos pratos
                    JOIN ficha_tecnica ft
                        ON ft.id_prato = pc.id_prato

                    -- Considera somente o pedido confirmado
                    WHERE cp.id_pedido = NEW.id_pedido

                    -- Agrupa as quantidades por ingrediente
                    GROUP BY ft.id_ingrediente

                    UNION ALL

                    -- CONSUMO DAS BEBIDAS
                    SELECT
                        ftb.id_ingrediente,
                        SUM(
                            ftb.qtd_necessaria * pb.qtd
                        ) AS qtd_total
                    FROM pedido_bebida pb

                    -- Encontra os ingredientes de cada bebida
                    JOIN ficha_tecnica_bebida ftb
                        ON ftb.id_bebida = pb.id_bebida

                    -- Considera somente as bebidas desse pedido
                    WHERE pb.id_pedido = NEW.id_pedido

                    -- Agrupa as quantidades por ingrediente
                    GROUP BY ftb.id_ingrediente

                ) AS consumos

                -- Soma também ingredientes repetidos
                -- entre diferentes pratos e bebidas
                GROUP BY consumos.id_ingrediente

            ) AS necessidades

            -- Compara o consumo calculado com o estoque atual
            JOIN ingrediente i
                ON i.id_ingrediente = necessidades.id_ingrediente

            -- Se o estoque for menor que o necessário, gera erro
            WHERE i.qtd < necessidades.qtd_total
        );


        -- ==========================================
        -- 2. DESCONTA OS INGREDIENTES DO ESTOQUE
        -- ==========================================

        UPDATE ingrediente

        -- Subtrai o consumo total da quantidade atual
        SET qtd = qtd - (

            -- Calcula o total usado de cada ingrediente
            SELECT SUM(consumos.qtd_total)
            FROM (

                -- INGREDIENTES DOS PRATOS
                SELECT
                    ft.id_ingrediente,
                    SUM(
                        ft.qtd_necessaria * NEW.num_convidados
                    ) AS qtd_total
                FROM cardapio_pedido cp

                JOIN prato_cardapio pc
                    ON pc.id_cardapio = cp.id_cardapio

                JOIN ficha_tecnica ft
                    ON ft.id_prato = pc.id_prato

                WHERE cp.id_pedido = NEW.id_pedido

                GROUP BY ft.id_ingrediente

                UNION ALL

                -- INGREDIENTES DAS BEBIDAS
                SELECT
                    ftb.id_ingrediente,
                    SUM(
                        ftb.qtd_necessaria * pb.qtd
                    ) AS qtd_total
                FROM pedido_bebida pb

                JOIN ficha_tecnica_bebida ftb
                    ON ftb.id_bebida = pb.id_bebida

                WHERE pb.id_pedido = NEW.id_pedido

                GROUP BY ftb.id_ingrediente

            ) AS consumos

            -- Seleciona apenas o ingrediente atualizado
            WHERE consumos.id_ingrediente =
                  ingrediente.id_ingrediente
        )

        -- Atualiza apenas ingredientes usados no pedido
        WHERE id_ingrediente IN (

            -- Lista os ingredientes dos pratos
            SELECT ft.id_ingrediente
            FROM cardapio_pedido cp
            JOIN prato_cardapio pc
                ON pc.id_cardapio = cp.id_cardapio
            JOIN ficha_tecnica ft
                ON ft.id_prato = pc.id_prato
            WHERE cp.id_pedido = NEW.id_pedido

            UNION

            -- Lista os ingredientes das bebidas
            SELECT ftb.id_ingrediente
            FROM pedido_bebida pb
            JOIN ficha_tecnica_bebida ftb
                ON ftb.id_bebida = pb.id_bebida
            WHERE pb.id_pedido = NEW.id_pedido
        );

    END;
    """

    # Abre uma transação com o banco
    with db.engine.begin() as conexao:

        # Remove a versão anterior, caso exista,
        # para que a versão atualizada seja instalada
        conexao.execute(text(
            "DROP TRIGGER IF EXISTS baixa_estoque_pedido_confirmado"
        ))

        # Cria a trigger com o código SQL acima
        conexao.execute(text(sql))

### Trigger de baixa automática de estoque

#A trigger `baixa_estoque_pedido_confirmado` tem como objetivo controlar automaticamente a saída dos ingredientes utilizados nos pedidos do sistema Sabor & Clic. Ela é executada quando o status de um pedido muda para `confirmado`, permitindo que o estoque seja atualizado sem a necessidade de realizar a baixa manualmente.

#Para calcular o consumo dos pratos, a trigger consulta as tabelas `cardapio_pedido`, `prato_cardapio` e `ficha_tecnica`. A ficha técnica informa quais ingredientes são utilizados na preparação de cada prato e a quantidade necessária por pessoa. Essa quantidade é multiplicada pelo número de convidados registrado no pedido.

#Para calcular o consumo das bebidas, a trigger consulta as tabelas `pedido_bebida` e `ficha_tecnica_bebida`. A primeira informa quais bebidas foram solicitadas e suas respectivas quantidades, enquanto a segunda informa os ingredientes necessários para preparar cada bebida. Nesse caso, a quantidade de cada ingrediente é multiplicada pelo número de unidades da bebida solicitadas pelo cliente.

#Após calcular o consumo, a trigger agrupa as quantidades por ingrediente, somando também os ingredientes que aparecem em diferentes pratos ou bebidas. Em seguida, verifica se a quantidade disponível na coluna `qtd` da tabela `ingrediente` é suficiente para atender ao pedido.

#Caso algum ingrediente esteja em falta, a operação de confirmação é interrompida e uma mensagem de erro é gerada. Se houver estoque suficiente, a trigger desconta automaticamente as quantidades utilizadas, atualizando o estoque atual dos ingredientes.

#Dessa forma, a trigger contribui para a consistência dos dados, reduz a necessidade de atualizações manuais e ajuda a evitar que pedidos sejam confirmados quando não há ingredientes suficientes para sua preparação.