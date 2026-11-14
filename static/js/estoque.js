// ===================== Edição de ingrediente =====================
// O formulário POSTa para /admin/servicos/ingredientes/atualizar/<id>. A ação é
// definida a partir do data-url do botão clicado e os campos são pré-preenchidos
// pelos data-* da linha; o envio é real (PRG no backend), sem mock no cliente.
const dialogoItem = document.getElementById("editar-item");
const formItem = document.getElementById("form-editar-item");
const nomeItem = document.getElementById("editar-nome");
const quantidadeItem = document.getElementById("editar-quantidade");
const minimoItem = document.getElementById("editar-minimo");
const unidadeItem = document.getElementById("editar-unidade");

document.querySelectorAll(".editar-estoque").forEach((botao) => {
  botao.addEventListener("click", () => {
    const linha = botao.closest("tr");
    formItem.action = botao.dataset.url || "";
    nomeItem.value = linha.dataset.nome || "";
    quantidadeItem.value = linha.dataset.qtd || "";
    minimoItem.value = linha.dataset.min || "";
    unidadeItem.value = linha.dataset.unidade || "kg";
    dialogoItem.showModal();
  });
});

document.getElementById("cancelar-edicao").addEventListener("click", () => dialogoItem.close());
nomeItem.addEventListener("input", () => nomeItem.setCustomValidity(""));
formItem.addEventListener("submit", () => {
  nomeItem.setCustomValidity(nomeItem.value.trim() ? "" : "Informe o nome do item.");
  if (!formItem.reportValidity()) return;
  // Sem preventDefault: o formulário é submetido de verdade ao backend.
});

// ===================== Edição de bebida =====================
// POSTa para /admin/servicos/bebidas/atualizar/<id> com nome/descricao/valor_unitario.
const dialogoBebida = document.getElementById("editar-bebida");
const formBebida = document.getElementById("form-editar-bebida");
const nomeBebida = document.getElementById("editar-bebida-nome");
const descricaoBebida = document.getElementById("editar-bebida-descricao");
const valorBebida = document.getElementById("editar-bebida-valor");

document.querySelectorAll(".editar-bebida").forEach((botao) => {
  botao.addEventListener("click", () => {
    const linha = botao.closest("tr");
    formBebida.action = botao.dataset.url || "";
    nomeBebida.value = linha.dataset.nome || "";
    descricaoBebida.value = linha.dataset.descricao || "";
    valorBebida.value = linha.dataset.valor || "";
    dialogoBebida.showModal();
  });
});

document.getElementById("cancelar-edicao-bebida").addEventListener("click", () => dialogoBebida.close());

const botaoCadastrar = document.querySelector('.cadastrar-item');
const cadastroItem = document.getElementById('cadastro-item');
botaoCadastrar.addEventListener('click', () => {
  cadastroItem.showModal();
});
document.getElementById('fechar-cadastro').addEventListener('click', () => {
  cadastroItem.close();
});

const botaoCadastrarCardapio = document.querySelector('.cadastrar-cardapio');
const cadastroCardapio = document.getElementById('cadastro-cardapio');
botaoCadastrarCardapio.addEventListener('click', () => {
  cadastroCardapio.showModal();
});
document.getElementById('fechar-cadastro-cardapio').addEventListener('click', () => {
  cadastroCardapio.close();
});

const entidadeEstoque = document.getElementById('estoque-entidade');
const buscaEstoque = document.getElementById('estoque-busca');
const situacaoEstoque = document.getElementById('estoque-situacao');
const normalizarEstoque = texto => texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
function filtrarEstoque() {
  const entidade = entidadeEstoque.value;
  const insumos = ['todos', 'ingrediente', 'bebida'].includes(entidade);
  document.getElementById('tabela-insumos').hidden = !insumos;
  document.getElementById('tabela-pratos').hidden = entidade !== 'prato';
  document.getElementById('tabela-lotes').hidden = entidade !== 'lote';
  document.getElementById('grupo-situacao').hidden = !insumos;
  situacaoEstoque.disabled = !insumos;
  botaoCadastrar.hidden = !insumos;
  document.getElementById('titulo-entidade').textContent = entidadeEstoque.selectedOptions[0].textContent;
  buscaEstoque.placeholder = entidade === 'lote' ? 'Número do lote, item ou marca' : entidade === 'prato' ? 'Nome ou tipo do prato' : 'Nome do item';
  const tabela = document.getElementById(entidade === 'prato' ? 'tabela-pratos' : entidade === 'lote' ? 'tabela-lotes' : 'tabela-insumos');
  let total = 0;
  tabela.querySelectorAll('tbody tr').forEach(linha => {
    const tipoCorreto = !insumos || entidade === 'todos' || linha.dataset.entidade === entidade;
    const texto = insumos ? linha.cells[0].textContent : linha.textContent;
    const situacao = linha.querySelector('.status')?.textContent.trim();
    const mostrar = tipoCorreto && normalizarEstoque(texto).includes(normalizarEstoque(buscaEstoque.value.trim())) && (!insumos || !situacaoEstoque.value || situacao === situacaoEstoque.value);
    linha.hidden = !mostrar;
    if (mostrar) total++;
  });
  document.getElementById('estoque-contagem').textContent = `${total} ${total === 1 ? 'registro encontrado' : 'registros encontrados'}`;
  document.getElementById('estoque-vazio').hidden = total > 0;
}
entidadeEstoque.addEventListener('change', filtrarEstoque);
buscaEstoque.addEventListener('input', filtrarEstoque);
situacaoEstoque.addEventListener('change', filtrarEstoque);
document.querySelector('.filtros-estoque').addEventListener('reset', () => { entidadeEstoque.value = 'todos'; buscaEstoque.value = ''; situacaoEstoque.value = ''; filtrarEstoque(); });
filtrarEstoque();
