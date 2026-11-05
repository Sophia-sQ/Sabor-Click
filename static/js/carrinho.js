const dialogo = document.getElementById('dialogo-endereco');
const endereco = document.getElementById('endereco-linha');
const cidade = document.getElementById('endereco-cidade');
const formulario = document.getElementById('formulario-endereco');
const campoEndereco = document.getElementById('novo-endereco');
const campoCidade = document.getElementById('nova-cidade');
const cep = document.getElementById('endereco-cep');
const bairro = document.getElementById('endereco-bairro');
const uf = document.getElementById('endereco-uf');
const numero = document.getElementById('endereco-numero');
const complemento = document.getElementById('endereco-complemento');
const statusCep = document.getElementById('status-cep');
let consulta;

document.getElementById('escolher-endereco')?.addEventListener('click', () => {
  dialogo.showModal();
  cep.focus();
});

cep.addEventListener('input', async () => {
  consulta?.abort();
  const digitos = cep.value.replace(/\D/g, '').slice(0, 8);
  cep.value = digitos.replace(/^(\d{5})(\d)/, '$1-$2');
  statusCep.textContent = 'Digite os 8 dígitos do CEP ou preencha o endereço manualmente.';
  if (digitos.length !== 8) return;
  const atual = new AbortController();
  consulta = atual;
  const limite = setTimeout(() => atual.abort(), 8000);
  statusCep.textContent = 'Buscando endereço…';
  try {
    const resposta = await fetch(`https://viacep.com.br/ws/${digitos}/json/`, { signal: atual.signal });
    if (!resposta.ok) throw new Error('Falha na consulta');
    const dados = await resposta.json();
    if (atual.signal.aborted || consulta !== atual) return;
    if (dados.erro) {
      statusCep.textContent = 'CEP não encontrado. Confira o CEP ou preencha os campos manualmente.';
      return;
    }
    campoEndereco.value = dados.logradouro || '';
    bairro.value = dados.bairro || '';
    campoCidade.value = dados.localidade || '';
    uf.value = dados.uf || '';
    statusCep.textContent = 'Endereço encontrado. Confira os campos e informe o número e complemento, se houver.';
  } catch (erro) {
    if (consulta !== atual) return;
    statusCep.textContent = 'Não foi possível consultar o CEP. Preencha o endereço manualmente.';
  } finally {
    clearTimeout(limite);
  }
});

dialogo.addEventListener('close', () => consulta?.abort());
document.getElementById('cancelar-endereco').addEventListener('click', () => dialogo.close());
formulario.addEventListener('submit', (evento) => {
  evento.preventDefault();
  if (!formulario.reportValidity()) return;
  consulta?.abort();
  endereco.textContent = `${campoEndereco.value.trim()}, ${numero.value.trim()}${complemento.value.trim() ? ' · ' + complemento.value.trim() : ''} • ${bairro.value.trim()}`;
  cidade.textContent = `${campoCidade.value.trim()} - ${uf.value.trim().toUpperCase()} • CEP ${cep.value}`;
  dialogo.close();
});

const finalizar = document.getElementById('finalizar-compra');
const sugestao = document.getElementById('sugestao-bebidas');
const catalogoCarrinho = window.SaborBebidas;
const avisoCarrinho = document.getElementById('aviso-carrinho');
function continuarCompra() {
  sugestao.close();
  const bebidas = catalogoCarrinho.ler();
  const pendentes = catalogoCarrinho.catalogo.some(b => bebidas[b.id] && b.preco === null);
  if (pendentes) {
    avisoCarrinho.textContent = 'Confirme os valores das bebidas antes de finalizar. Nenhum pedido foi enviado.';
    avisoCarrinho.hidden = false;
    return;
  }
  if (finalizar.dataset.checkout) {
    window.location.assign(finalizar.dataset.checkout);
    return;
  }
  avisoCarrinho.textContent = 'A finalização da compra ainda não está disponível. Nenhum pedido foi enviado.';
  avisoCarrinho.hidden = false;
}
function renderizarBebidasCarrinho() {
  const quantidades = catalogoCarrinho.ler();
  const selecionadas = catalogoCarrinho.catalogo.filter(b => quantidades[b.id]);
  const container = document.getElementById('bebidas-no-carrinho');
  container.replaceChildren();
  const criar = (tag, texto) => { const node = document.createElement(tag); node.textContent = texto; return node; };
  selecionadas.forEach(bebida => {
    const card = document.createElement('article');
    card.className = 'bebida-carrinho';
    const info = document.createElement('div');
    info.append(criar('p', 'BEBIDA À PARTE'), criar('h2', bebida.nome), criar('p', `${quantidades[bebida.id]} unidade(s)${bebida.volume_ml ? ' · ' + bebida.volume_ml + ' ml cada' : ''}`));
    const acoes = document.createElement('div');
    acoes.append(criar('strong', bebida.preco === null ? 'Valor a confirmar' : catalogoCarrinho.dinheiro(bebida.preco * quantidades[bebida.id])));
    const remover = criar('button', 'Remover');
    remover.type = 'button';
    remover.setAttribute('aria-label', `Remover ${bebida.nome} do carrinho`);
    remover.addEventListener('click', () => {
      const atuais = catalogoCarrinho.ler();
      delete atuais[bebida.id];
      try {
        catalogoCarrinho.salvar(atuais);
        renderizarBebidasCarrinho();
        avisoCarrinho.textContent = `${bebida.nome} removida do carrinho.`;
        avisoCarrinho.hidden = false;
        finalizar.focus();
      } catch {
        avisoCarrinho.textContent = 'Não foi possível remover a bebida. Verifique o armazenamento do navegador.';
        avisoCarrinho.hidden = false;
      }
    });
    acoes.append(remover);
    card.append(info, acoes);
    container.append(card);
  });
  const servicos = document.querySelectorAll('[data-servico]').length;
  document.getElementById('carrinho-vazio')?.toggleAttribute('hidden', selecionadas.length > 0);
  finalizar.disabled = !servicos && !selecionadas.length;
  const pendentes = selecionadas.some(b => b.preco === null);
  document.getElementById('aviso-precos').hidden = !pendentes;
  const total = Number(finalizar.dataset.totalBase) + selecionadas.reduce((s, b) => s + (bebidaPreco(b) * quantidades[b.id]), 0);
  document.querySelectorAll('[data-total-carrinho]').forEach(node => { node.textContent = pendentes ? 'A confirmar' : catalogoCarrinho.dinheiro(total); });
}
function bebidaPreco(bebida) { return bebida.preco === null ? 0 : bebida.preco; }
finalizar.addEventListener('click', () => {
  if (finalizar.disabled) return;
  const temBebidas = Object.keys(catalogoCarrinho.ler()).length > 0 || document.querySelector('[data-servico][data-inclui-bebidas="true"]');
  if (!temBebidas && catalogoCarrinho.catalogo.length) sugestao.showModal();
  else continuarCompra();
});
document.getElementById('fechar-sugestao').addEventListener('click', () => sugestao.close());
document.getElementById('continuar-sem-bebidas').addEventListener('click', continuarCompra);
window.addEventListener('pageshow', renderizarBebidasCarrinho);
window.addEventListener('storage', evento => { if (evento.key === 'sabor-click-bebidas-v1' || evento.key === null) renderizarBebidasCarrinho(); });
renderizarBebidasCarrinho();
