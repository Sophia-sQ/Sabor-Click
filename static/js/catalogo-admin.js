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

  // Ficha técnica do prato (FEAT-002): habilita/desabilita o input de quantidade
  // conforme o checkbox do ingrediente. Apenas UX; a validação final é no
  // servidor. Guardas (só ativa onde os elementos existem) evitam qualquer
  // efeito nas outras páginas que compartilham este arquivo.
  const linhasIngrediente = document.querySelectorAll('.ingredientes-catalogo .linha-ingrediente');
  linhasIngrediente.forEach(linha => {
    const marcador = linha.querySelector('input[type="checkbox"][name="ingredientes"]');
    const quantidade = linha.querySelector('input[type="number"]');
    if (!marcador || !quantidade) return;
    const sincronizar = () => {
      quantidade.disabled = !marcador.checked;
      if (!marcador.checked) quantidade.value = '';
    };
    marcador.addEventListener('change', sincronizar);
  });

  // Ficha técnica da bebida (FEAT-003): o preço por porção só faz sentido quando
  // a bebida é AVULSA, ou seja, tem exatamente 1 ingrediente selecionado.
  // Mostra/esconde o campo de preço conforme o nº de ingredientes marcados.
  // Progressive enhancement: a validação final é no servidor. Guardas (só ativa
  // quando o wrapper do preço de bebida existe) impedem efeito nas outras
  // páginas que compartilham este arquivo.
  const campoPrecoBebida = document.getElementById('campo-preco-bebida');
  if (campoPrecoBebida) {
    const marcadoresBebida = document.querySelectorAll(
      '.ingredientes-catalogo input[type="checkbox"][name="ingredientes"]');
    const precoBebida = campoPrecoBebida.querySelector('input[name="valor_unitario"]');
    const atualizarPreco = () => {
      let total = 0;
      marcadoresBebida.forEach(m => { if (m.checked) total++; });
      const avulsa = total === 1;
      campoPrecoBebida.hidden = !avulsa;
      if (precoBebida && !avulsa) precoBebida.value = '';
    };
    marcadoresBebida.forEach(m => m.addEventListener('change', atualizarPreco));
    atualizarPreco();
  }
})();
