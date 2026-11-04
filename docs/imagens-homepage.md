# Imagens da homepage

Os arquivos ficam em `static/images/`. As imagens do Figma já estão incluídas.
Para trocar uma imagem, substitua o arquivo mantendo exatamente o nome e a extensão.

| Local | Arquivo | Proporção exibida no desktop |
| --- | --- | --- |
| Imagem principal, ao lado do título | `home-principal.png` | 650 × 560 |
| Seção Sobre, chef na cozinha | `home-sobre.png` | 530 × 432 |
| Serviço Buffet para eventos | `home-buffet.jpg` | 644 × 240 |
| Serviço Chef em casa | `home-chef.jpg` | 644 × 240 |
| Serviço Salgados para eventos | `home-salgados.jpg` | 644 × 240 |
| Serviço Bebidas | `home-bebidas.jpg` | 644 × 240 |
| Símbolo da marca no cabeçalho | `home-logo.svg` | 38 × 38 |

As fotos usam `object-fit: cover`, mantendo a proporção e recortando as bordas
quando necessário. Prefira fotos maiores com o assunto principal centralizado.

## Prévia

Na pasta do projeto, execute:

```powershell
.\.venv\Scripts\python.exe tmp\preview_paginas.py
```

Abra `http://127.0.0.1:5001/`. Se a prévia já estava aberta, pare com Ctrl + C
e execute novamente para carregar a nova rota.

Os links Início, Sobre e Serviços navegam pela homepage. Conhecer o menu e
Planejar meu evento levam ao login enquanto as respectivas telas não existem.
A seção de feedback e seus links foram retirados conforme solicitado.

## Fotos dos serviços em alta resolução

Versões `home-buffet-hd.jpg`, `home-chef-hd.jpg`, `home-salgados-hd.jpg` e `home-bebidas-hd.jpg` (1536 × 1024), geradas com a ferramenta integrada imagegen a partir dos originais, que foram preservados.

Prompt usado em cada foto: restaurar e ampliar a fotografia original, preservar assunto, composição, cores e objetos; reduzir desfoque e compressão; recuperar detalhes naturais sem nitidez artificial; preservar identidade e pose no retrato; sem textos ou marcas.
