/* Apenas IDs e quantidades são guardados; preços sempre vêm do catálogo da página. */
(() => {
  'use strict';
  const catalogo = JSON.parse(document.getElementById('catalogo-bebidas')?.textContent || '[]');
  const chave = 'sabor-click-bebidas-v1';
  const dinheiro = valor => valor.toLocaleString('pt-BR', {style:'currency', currency:'BRL'});
  const ler = () => {
    try {
      const dados = JSON.parse(localStorage.getItem(chave) || '{}');
      return Object.fromEntries(catalogo.filter(b => Number.isInteger(dados?.[b.id]) && dados[b.id] > 0 && dados[b.id] <= 99).map(b => [b.id, dados[b.id]]));
    } catch { return {}; }
  };
  const salvar = dados => localStorage.setItem(chave, JSON.stringify(dados));
  window.SaborBebidas = {catalogo, ler, salvar, dinheiro};
  if (!document.querySelector('.grade-bebidas')) return;
  const selecionadas = ler();
  const cards = [...document.querySelectorAll('.card-bebida')];
  const status = document.getElementById('status-bebidas');
  function atualizar() {
    const itens = catalogo.filter(b => selecionadas[b.id] > 0);
    const lista = document.getElementById('selecao-bebidas');
    lista.replaceChildren(...itens.map(b => {
      const li = document.createElement('li');
      li.textContent = `${selecionadas[b.id]} × ${b.nome}${b.volume_ml ? ' (' + b.volume_ml + ' ml)' : ''}${b.preco === null ? '' : ' · ' + dinheiro(b.preco * selecionadas[b.id])}`;
      return li;
    }));
    const pendentes = itens.some(b => b.preco === null);
    document.getElementById('total-bebidas').textContent = pendentes ? 'A confirmar' : dinheiro(itens.reduce((s,b) => s + b.preco * selecionadas[b.id], 0));
    document.getElementById('precos-pendentes').hidden = !pendentes;
    document.getElementById('selecao-vazia').hidden = itens.length > 0;
    document.getElementById('adicionar-bebidas').disabled = !itens.length || cards.some(c => !c.querySelector('input').validity.valid);
  }
  cards.forEach(card => {
    const input = card.querySelector('input');
    input.value = selecionadas[card.dataset.id] || 0;
    const mudar = () => {
      if (!input.validity.valid || !Number.isInteger(input.valueAsNumber)) { atualizar(); return; }
      selecionadas[card.dataset.id] = input.valueAsNumber;
      atualizar();
    };
    input.addEventListener('input', mudar);
    card.querySelectorAll('[data-delta]').forEach(botao => botao.addEventListener('click', () => {
      input.value = Math.min(99, Math.max(0, (Number(input.value) || 0) + Number(botao.dataset.delta)));
      mudar();
    }));
  });
  const normalizar = texto => texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const busca = document.getElementById('buscar-bebida');
  const categoria = document.getElementById('categoria-bebida');
  function filtrar() {
    let total = 0;
    cards.forEach(card => {
      card.hidden = !(normalizar(card.dataset.nome).includes(normalizar(busca.value.trim())) && (!categoria.value || card.dataset.categoria === categoria.value));
      if (!card.hidden) total++;
    });
    document.getElementById('bebidas-sem-resultado').hidden = total !== 0;
    status.textContent = `${total} ${total === 1 ? 'bebida disponível' : 'bebidas disponíveis'}`;
  }
  document.querySelector('.filtros-bebidas').addEventListener('submit', e => e.preventDefault());
  busca.addEventListener('input', filtrar);
  categoria.addEventListener('change', filtrar);
  document.getElementById('adicionar-bebidas').addEventListener('click', () => {
    if (document.getElementById('adicionar-bebidas').disabled) return;
    try { salvar(selecionadas); location.assign(document.querySelector('.voltar-carrinho').href); }
    catch { status.textContent = 'Não foi possível salvar sua seleção. Permita o armazenamento do navegador e tente novamente.'; }
  });
  atualizar();
  filtrar();
})();
