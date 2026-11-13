(() => {
  const bebidas = window.SaborBebidas;
  if (document.getElementById('limpar-bebidas')) {
    try { bebidas.salvar({}); } catch { /* O navegador pode bloquear o armazenamento. */ }
  }

  const formulario = document.getElementById('formulario-pedido');
  if (!formulario) return;
  const confirmar = document.getElementById('confirmar-pedido');
  const aviso = document.getElementById('aviso-pedido');
  const total = document.getElementById('total-pedido');
  const quantidades = bebidas.ler();
  let centavos = Number(total.dataset.centavos);
  let pendente = false;
  for (const bebida of bebidas.catalogo) {
    const qtd = quantidades[bebida.id];
    if (!qtd) continue;
    const linha = document.createElement('div');
    const nome = document.createElement('dt');
    const valor = document.createElement('dd');
    nome.textContent = `${qtd} × ${bebida.nome}`;
    pendente ||= bebida.preco === null;
    const subtotal = Math.round(bebida.preco * 100) * qtd;
    centavos += subtotal;
    valor.textContent = bebida.preco === null ? 'A confirmar' : bebidas.dinheiro(subtotal / 100);
    linha.append(nome, valor);
    total.before(linha);
  }
  total.querySelector('dd').textContent = pendente ? 'A confirmar' : bebidas.dinheiro(centavos / 100);
  const vazio = !document.getElementById('resumo-pedido').querySelector('div:not(.total)');
  aviso.textContent = vazio ? 'Adicione itens ao carrinho para continuar.' : 'Confirme os valores das bebidas no carrinho.';
  aviso.hidden = !pendente && !vazio;
  confirmar.disabled = pendente || vazio;
  formulario.elements.bebidas.value = JSON.stringify(quantidades);
  formulario.addEventListener('submit', evento => {
    if (confirmar.disabled) evento.preventDefault();
    else confirmar.disabled = true;
  });
  window.addEventListener('pageshow', evento => {
    if (evento.persisted) window.location.reload();
  });
})();
