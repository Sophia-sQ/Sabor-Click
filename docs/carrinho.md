# Carrinho e bebidas avulsas

## Visualização local

Execute `.venv\Scripts\python.exe -m services.previa.previa_admin` e abra:

- `/carrinho`: carrinho vazio ou com bebidas já selecionadas neste navegador.
- `/carrinho?exemplo=sem-bebidas`: serviço ilustrativo para testar o card na finalização.
- `/carrinho?exemplo=com-bar`: serviço ilustrativo de Bar; dispensa a sugestão.
- `/bebidas`: catálogo avulso, filtros e seleção de quantidades.

O servidor usa `http://127.0.0.1:8080`. Os parâmetros de exemplo existem apenas no servidor de prévias.

## Regra da sugestão

Um carrinho vazio mantém a finalização desabilitada. Um carrinho com itens, sem bebidas avulsas e sem serviço que inclua bebidas, apresenta o card “Que tal uma bebida para acompanhar?”. A pessoa pode escolher bebidas, continuar sem bebidas ou fechar o card. Esc também fecha o diálogo.

O template recebe `itens_carrinho` com `numero`, `nome`, `descricao`, `imagem`, `subtotal` e `inclui_bebidas`. O backend deve informar `inclui_bebidas=True` para Bar e outros serviços com bebidas. O campo `tipo` (`bar`, `bebidas`, `bebida`) também é reconhecido. A coluna de serviços e o subtotal continuam usando os itens recebidos do servidor.

## Origem do catálogo

`services/bebidas_data.py` formata o catálogo avulso a partir dos registros de `Bebida` do banco. As oito bebidas avulsas (as que o cliente escolhe fora do serviço de Bar) e seus volumes estão embutidos no módulo como constantes de dados; coquetéis do serviço de Bar não entram nessa tela.

Na aplicação principal, GET `/home/bebidas` consulta `listar_bebidas()` e formata os registros reais de `Bebida` via `formatar_bebidas`. O carrinho em `/home/carrinho` recebe esse mesmo catálogo.

Na prévia, a mesma formatação é reutilizada: `catalogo_previa` recebe os registros já consultados pelo chamador e, quando não há dados, usa os nomes do cadastro e mostra “Valor a confirmar”. Nenhum acesso direto a `instance/banco.db` é feito.

## Seleção e limites

IDs e quantidades ficam em `localStorage`, na chave `sabor-click-bebidas-v1`. O carrinho resolve nome e preço a partir do catálogo atual, sem armazenar preços fornecidos pelo navegador. Aceita quantidades inteiras de 0 a 99 por bebida; zero remove a bebida da seleção. Permite remover bebidas no carrinho. Busca desconsidera acentos e o filtro separa bebidas com e sem álcool.

Valores ausentes exibem “A confirmar” e impedem avançar ao checkout com essas bebidas. A seleção é local: ainda não cria `PedidoBebida`, não debita estoque e não envia pedidos. O backend de checkout deverá receber IDs/quantidades, validar disponibilidade, recalcular preços no banco e persistir o pedido. O controller existente de serviços ainda precisa montar `itens_carrinho` a partir da sessão; essa integração anterior continua pendente.

O endereço continua como formulário visual. A prévia não envia pedidos nem possui checkout integrado.

## Fotos e volumes

Os cartões usam imagens locais do catálogo. Imagens e dados alterados no painel administrativo aparecem na prévia; o catálogo da aplicação principal ainda vem do banco.

Os volumes são lidos de `ficha_bebidas` em `seeds.py`: 200 ml por porção de água com gás, suco de abacaxi, refrigerante de guaraná, chá preto, água de coco e suco de melancia; 70 ml por dose de gin e uísque de centeio. O resumo de seleção e os itens do carrinho também mostram o volume unitário. As fotos ilustram as bebidas; as marcas e os recipientes das fotos não alteram a ficha do projeto.
