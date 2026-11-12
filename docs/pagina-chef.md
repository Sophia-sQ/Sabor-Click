# Página do chef

Execute `.venv\Scripts\python.exe -m services.previa.previa_admin` e acesse `http://127.0.0.1:8080/cozinha` ou `/previas/cozinha.html`. A porta pode ser alterada pela variável PREVIEW_PORT.

A tela mostra a fila em ordem de chegada. Aceitar um pedido abre os itens, a lista total de ingredientes e as fichas de preparo. O checklist é independente por pedido. Após separar os ingredientes, o chef pode iniciar e concluir o preparo.

Esta entrega é de frontend. Os dados são ilustrativos e ficam em memória; recarregar reinicia a demonstração. Não existe persistência nem baixa de estoque nesta prévia.

## Referências e integração em Python

- O administrador consulta os pedidos e o responsável. O aceite fica na página da cozinha e deve vincular o chef logado na integração com o backend.
- `model/ficha_model.py`: `FichaTecnica`, `FichaTecnica_bebida`, `Ingrediente`, `Prato`, `PratoCardapio`.
- `model/pedido_model.py`: `Pedido`, `CardapioPedido`, `PedidoBebida`.
- `triggers.py`: consumo de pratos por `num_convidados` e de bebidas por `PedidoBebida.qtd`; ingredientes repetidos são somados.

O backend deve calcular e retornar as quantidades, usando os IDs de ingredientes e suas unidades, sem confiar nos números do navegador. A prévia usa porções explícitas de exemplo. É necessário alinhar o significado de `PratoCardapio.qtd` antes da integração, pois a fórmula atual da trigger não usa esse campo. Não converter unidades diferentes implicitamente.

Fluxo previsto: `aguardando` → `confirmado` → `em preparo` → `concluido`. O aceite deve validar sessão e cargo, garantir que o pedido ainda está disponível e vincular o usuário da sessão em uma transação. Somente o responsável deve atualizar seu preparo; o backend precisa rejeitar aceite duplicado ou concorrente. O checklist é um auxílio visual, não uma baixa de estoque.

As rotas existentes são POST `/pedido/aceitar` e GET/POST `/pedido/atualizar`. Ainda precisam de integração: o controller hoje referencia um template inexistente (`pagina de pedidos.html`), o e-mail usa atributos que não existem em `Pedido`/`Usuario` e a chamada de `render_template` usa argumentos posicionais. A trigger é instalada depois da confirmação; esse ponto precisa ser corrigido na integração para aplicar a política de estoque antes da alteração de status. Não ligar os botões da prévia a essas rotas sem tratar esses pontos.

A API deverá fornecer os pedidos disponíveis e os do chef logado, itens com quantidades, observações, status e responsável, ingredientes totais e fichas por prato/bebida. Fichas ausentes devem aparecer como pendência, sem inventar receitas ou liberar o preparo silenciosamente.
