const previa = document.body.dataset.previa === 'true';
const retorno = document.querySelector('#retorno');
const modal = document.querySelector('#modal-endereco');
const formEndereco = document.querySelector('#form-endereco');
document.querySelectorAll('.fechar').forEach(botao => botao.addEventListener('click', () => botao.closest('dialog').close()));
document.querySelector('#novo-endereco').addEventListener('click', () => {
  formEndereco.reset(); formEndereco.action = formEndereco.dataset.criar;
  document.querySelector('#titulo-endereco').textContent = 'Adicionar endereço'; modal.showModal();
});
document.querySelectorAll('.editar').forEach(botao => botao.addEventListener('click', () => {
  const endereco = JSON.parse(botao.dataset.endereco); formEndereco.reset();
  const campos = {nome:'nome',cep:'cep',num:'numero',logadouro:'logradouro',compl:'complemento',bairro:'bairro',cidade:'cidade'};
  Object.entries(campos).forEach(([campo,chave]) => {formEndereco.elements.namedItem(campo).value = endereco[chave] ?? '';});
  formEndereco.action = `/home/endereco/atualizar/${endereco.id_endereco}`;
  document.querySelector('#titulo-endereco').textContent = 'Editar endereço'; modal.showModal();
}));
document.querySelectorAll('.excluir').forEach(botao => botao.addEventListener('click', () => {
  document.querySelector('#descricao-excluir').textContent = `O endereço “${botao.dataset.nome}” será removido da sua conta.`;
  document.querySelector('#form-excluir').action = `/home/endereco/deletar/${botao.dataset.id}`;
  document.querySelector('#modal-excluir').showModal();
}));
const senha = document.querySelector('#senha'); const confirmacao = document.querySelector('#confirmacao');
function conferirSenha(){confirmacao.setCustomValidity(confirmacao.value === senha.value ? '' : 'As senhas precisam ser iguais.');}
senha.addEventListener('input', conferirSenha); confirmacao.addEventListener('input', conferirSenha);
document.querySelector('#mostrar').addEventListener('change', evento => {[senha,confirmacao].forEach(campo => {campo.type = evento.target.checked ? 'text' : 'password';});});
document.querySelectorAll('input[name="cpf"],input[name="cep"]').forEach(campo => campo.addEventListener('input', () => {
  const cpf = campo.name === 'cpf'; const valor = campo.value.replace(/\D/g,'').slice(0,cpf ? 11 : 8);
  campo.value = cpf ? valor.replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d{1,2})$/,'$1-$2') : valor.replace(/(\d{5})(\d)/,'$1-$2');
}));
document.querySelectorAll('form').forEach(form => form.addEventListener('submit', evento => {
  form.querySelectorAll('input:not([type="password"]):not([type="checkbox"])').forEach(campo => {campo.value = campo.value.trim();});
  if (!form.reportValidity()){evento.preventDefault();return;}
  if(previa){evento.preventDefault();form.closest('dialog')?.close();retorno.textContent='Formulário conferido. Esta é uma prévia: nenhuma alteração foi salva.';retorno.hidden=false;retorno.focus();}
}));
document.querySelectorAll('.lateral nav a').forEach(link => link.addEventListener('click', () => {document.querySelectorAll('.lateral nav a').forEach(item => item.classList.remove('selecionado'));link.classList.add('selecionado');}));

const modalSair = document.querySelector('#modal-sair');
document.querySelector('#abrir-sair').addEventListener('click', () => modalSair.showModal());
modalSair.addEventListener('click', evento => {
  const area = modalSair.getBoundingClientRect();
  if (evento.target === modalSair && (evento.clientX < area.left || evento.clientX > area.right || evento.clientY < area.top || evento.clientY > area.bottom)) modalSair.close();
});

// ===== Pedidos: carrega o pedido em andamento do cliente =====
const pedidosConteudo = document.querySelector('#pedidos-conteudo');
function criar(tag, texto, classe) {
  const elemento = document.createElement(tag);
  if (classe) elemento.className = classe;
  if (texto !== undefined && texto !== null) elemento.textContent = texto;
  return elemento;
}
function pedidoVazio() {
  const vazio = criar('div', null, 'vazio');
  const simbolo = criar('span', '✦'); simbolo.setAttribute('aria-hidden', 'true');
  vazio.append(simbolo, criar('h3', 'Nenhum pedido em andamento.'),
    criar('p', 'Monte o seu evento pelo cardápio para ver o pedido aqui.'));
  return vazio;
}
function textoData(iso) {
  if (!iso) return '';
  const partes = iso.split('-');
  return partes.length === 3 ? `${partes[2]}/${partes[1]}/${partes[0]}` : iso;
}
function textoHora(iso) { return iso ? iso.slice(0, 5) : ''; }
function renderizarPedido(dados) {
  const pedido = dados.pedido;
  const artigo = criar('article', null, 'pedido');

  const topo = criar('div', null, 'pedido-topo');
  topo.append(criar('h3', `Pedido nº ${pedido.id}`));
  const sucesso = pedido.status === 'concluido' || pedido.status === 'confirmado';
  const badge = criar('span', pedido.status.charAt(0).toUpperCase() + pedido.status.slice(1),
    sucesso ? 'status verde' : 'status');
  topo.append(badge);
  artigo.append(topo);

  const total = criar('p', null, 'pedido-total');
  total.append(criar('span', 'Total do evento '), criar('strong', pedido.valor_total));
  artigo.append(total);

  if (pedido.data_evento || pedido.hora_inicio) {
    const data = textoData(pedido.data_evento);
    const horas = [textoHora(pedido.hora_inicio), textoHora(pedido.hora_fim)].filter(Boolean).join(' às ');
    artigo.append(criar('p', [data, horas].filter(Boolean).join(' · ')));
  }

  const servicos = dados.servicos || {};
  const nomesServicos = Object.keys(servicos);
  if (nomesServicos.length) {
    artigo.append(criar('h4', 'Cardápios'));
    const lista = criar('ul', null, 'pedido-itens');
    nomesServicos.forEach(nome => {
      const [cardapio, valor] = servicos[nome];
      const item = criar('li');
      item.append(criar('span', cardapio), criar('span', valor));
      lista.append(item);
    });
    artigo.append(lista);
  }

  const bebidas = (dados.bebidas && dados.bebidas.itens) || [];
  if (bebidas.length) {
    artigo.append(criar('h4', 'Bebidas'));
    const lista = criar('ul', null, 'pedido-itens');
    bebidas.forEach(bebida => {
      const item = criar('li');
      item.append(criar('span', `${bebida.qtd} × ${bebida.nome}`));
      lista.append(item);
    });
    artigo.append(lista);
  }

  if (dados.endereco) {
    const endereco = dados.endereco;
    artigo.append(criar('h4', 'Endereço do evento'));
    const bloco = criar('div', null, 'pedido-endereco');
    if (endereco.nome) bloco.append(criar('p', endereco.nome));
    const complemento = endereco.complemento ? ` · ${endereco.complemento}` : '';
    bloco.append(criar('p', `${endereco.logradouro}, ${endereco.numero}${complemento}`));
    bloco.append(criar('p', `${endereco.bairro} · ${endereco.cidade}`));
    if (endereco.cep) bloco.append(criar('p', `CEP ${endereco.cep}`));
    artigo.append(bloco);
  }

  if (pedido.status === 'aguardando') {
    const form = criar('form');
    form.method = 'post';
    form.action = `/home/cancelar_pedido/${pedido.id}`;
    form.className = 'pedido-acoes';
    const botao = criar('button', 'Cancelar pedido', 'secundario');
    botao.type = 'submit';
    form.append(botao);
    artigo.append(form);
  }

  return artigo;
}
if (pedidosConteudo && !previa) {
  fetch('/home/perfil/dados', { headers: { Accept: 'application/json' } })
    .then(resposta => resposta.ok ? resposta.json() : null)
    .then(dados => {
      pedidosConteudo.replaceChildren();
      if (dados && dados.pedido) pedidosConteudo.append(renderizarPedido(dados));
      else pedidosConteudo.append(pedidoVazio());
    })
    .catch(() => {
      pedidosConteudo.replaceChildren();
      pedidosConteudo.append(pedidoVazio());
    });
}
