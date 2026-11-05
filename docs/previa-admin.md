# Prévia da página administrativa

Execute `.venv\Scripts\python.exe previa_admin.py` na raiz do projeto e abra http://127.0.0.1:8080/admin. A variável PREVIEW_PORT permite escolher outra porta.

O dashboard usa dados demonstrativos e permite selecionar o período. Cardápio e Bebidas permitem adicionar, editar e remover opções, com imagem por arquivo (PNG, JPG ou WebP de até 5 MB) ou link HTTP/HTTPS. Os cadastros são salvos em `instance/catalogo-previa.json`; uploads ficam em `static/images/catalogo/`. Esses dados locais não devem entrar no Git.

A prévia usa apenas o endereço local, sem autenticação, e não deve ser publicada como servidor de produção. Ela é independente do app principal e de seu banco; mudanças feitas aqui não alteram o banco principal. O acesso ao carrinho nesse iniciador retorna ao menu: checkout não faz parte desta prévia administrativa.
