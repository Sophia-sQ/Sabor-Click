(() => {
  'use strict';
  const input = document.getElementById('buscar-catalogo');
  const itens = [...document.querySelectorAll('.item-catalogo')];
  const normalizar = t => t.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  if (input) {
    input.addEventListener('input', () => {
      let total = 0;
      itens.forEach(item => {
        item.hidden = !normalizar(item.dataset.nome).includes(normalizar(input.value.trim()));
        if (!item.hidden) total++;
      });
      const vazio = document.getElementById('catalogo-vazio');
      if (vazio) vazio.hidden = total > 0;
    });
  }

  // Prévia da imagem a partir do input de arquivo (o formulário real usa upload
  // de arquivo, não link). Guardas evitam null-deref quando os elementos da
  // prévia não existem na página.
  const arquivo = document.getElementById('imagem-arquivo');
  const imagem = document.getElementById('previa-imagem');
  const placeholder = document.getElementById('placeholder-imagem');
  const status = document.getElementById('status-imagem');
  if (arquivo && imagem && placeholder) {
    let urlAtual = null;
    arquivo.addEventListener('change', () => {
      if (status) status.textContent = '';
      if (urlAtual) { URL.revokeObjectURL(urlAtual); urlAtual = null; }
      const ficheiro = arquivo.files && arquivo.files[0];
      if (!ficheiro) return;
      if (!/^image\/(png|jpeg|webp)$/i.test(ficheiro.type)) {
        if (status) status.textContent = 'Envie uma imagem PNG, JPG ou WebP.';
        return;
      }
      urlAtual = URL.createObjectURL(ficheiro);
      imagem.src = urlAtual;
      imagem.hidden = false;
      placeholder.hidden = true;
    });
  }

  // Diálogo de confirmação de remoção (soft delete). Cada botão carrega a URL
  // exata da rota de desativação em data-action (gerada por url_for com o id
  // real do item), então o formulário aponta direto para ela -- sem reescrever
  // a URL por regex.
  const dialogo = document.getElementById('confirmar-remocao');
  const formRemocao = document.getElementById('form-remocao');
  if (dialogo && formRemocao) {
    document.querySelectorAll('.remover-item').forEach(botao => botao.addEventListener('click', () => {
      const id = botao.dataset.id;
      const campoId = document.getElementById('remover-id');
      if (campoId) campoId.value = id;
      if (botao.dataset.action) formRemocao.action = botao.dataset.action;
      const descricao = document.getElementById('remover-descricao');
      if (descricao) descricao.textContent = `“${botao.dataset.nome}” deixará de aparecer nas opções do cliente.`;
      dialogo.showModal();
    }));
    const cancelar = document.getElementById('cancelar-remocao');
    if (cancelar) cancelar.addEventListener('click', () => dialogo.close());
  }
})();
