const categoria = document.querySelector('#filtro-categoria');
const busca = document.querySelector('#filtro-busca');
const pratos = [...document.querySelectorAll('.prato')];
const normalizar = texto => texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
function filtrar() {
  let total = 0;
  pratos.forEach(prato => {
    const mostrar = (!categoria.value || prato.dataset.categoria === categoria.value) && normalizar(prato.dataset.busca).includes(normalizar(busca.value.trim()));
    prato.hidden = !mostrar;
    if (mostrar) total++;
  });
  document.querySelector('#menu-contagem').textContent = `${total} ${total === 1 ? 'opção para seu evento' : 'opções para seu evento'}`;
  document.querySelector('.menu-vazio').hidden = total !== 0;
}
categoria.addEventListener('change', filtrar);
busca.addEventListener('input', filtrar);
document.querySelector('.menu-filtros').addEventListener('reset', () => { categoria.value = ''; busca.value = ''; filtrar(); });
const modal = document.querySelector('#menu-detalhe');
const dinheiro = centavos => (centavos / 100).toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'});
const detalheQuantidade = document.querySelector('#detalhe-pessoas');
let pratoSelecionado = null;
function quantidadeValida(campo) {
  return campo.validity.valid && Number.isInteger(campo.valueAsNumber) && campo.valueAsNumber >= 10 && campo.valueAsNumber <= 500;
}
function atualizarTotal(prato) {
  const campo = prato.querySelector('.quantidade-pessoas');
  if (!campo) return;
  const total = prato.querySelector('.total-menu');
  if (!quantidadeValida(campo)) {
    total.textContent = 'Informe uma quantidade inteira de 10 a 500 pessoas.';
    return;
  }
  const valor = document.createElement('strong');
  valor.className = 'total-valor';
  valor.textContent = dinheiro(Number(prato.dataset.precoCentavos) * campo.valueAsNumber);
  total.replaceChildren(document.createTextNode(`Total para ${campo.valueAsNumber} pessoas: `), valor);
}
pratos.forEach(prato => {
  prato.querySelector('.quantidade-pessoas')?.addEventListener('input', () => atualizarTotal(prato));
});
function atualizarDetalhe() {
  if (!pratoSelecionado) return;
  const total = document.querySelector('#detalhe-total');
  if (!quantidadeValida(detalheQuantidade)) {
    total.textContent = 'Informe uma quantidade inteira de 10 a 500 pessoas.';
    return;
  }
  const campo = pratoSelecionado.querySelector('.quantidade-pessoas');
  campo.value = detalheQuantidade.valueAsNumber;
  atualizarTotal(pratoSelecionado);
  total.textContent = `Total para ${campo.valueAsNumber} pessoas: ${dinheiro(Number(pratoSelecionado.dataset.precoCentavos) * campo.valueAsNumber)}`;
}
detalheQuantidade.addEventListener('input', atualizarDetalhe);
document.querySelectorAll('.ver-menu').forEach(botao => botao.addEventListener('click', () => {
  pratoSelecionado = botao.closest('.prato');
  const campo = pratoSelecionado.querySelector('.quantidade-pessoas');
  if (campo && !quantidadeValida(campo)) { campo.reportValidity(); return; }
  document.querySelector('#detalhe-orcamento').hidden = !campo;
  document.querySelector('#detalhe-sem-preco').hidden = Boolean(campo);
  if (campo) {
    document.querySelector('#detalhe-preco').textContent = dinheiro(Number(pratoSelecionado.dataset.precoCentavos));
    detalheQuantidade.value = campo.value;
    atualizarDetalhe();
  }
  document.querySelector('#detalhe-nome').textContent = botao.dataset.nome;
  document.querySelector('#detalhe-descricao').textContent = botao.dataset.descricao;
  document.querySelector('#detalhe-tipo').textContent = botao.dataset.tipo;
  modal.showModal();
}));
document.querySelector('.fechar-modal').addEventListener('click', () => modal.close());
modal.addEventListener('click', evento => { if (evento.target === modal) { const r = modal.getBoundingClientRect(); if (evento.clientX < r.left || evento.clientX > r.right || evento.clientY < r.top || evento.clientY > r.bottom) modal.close(); } });
filtrar();
