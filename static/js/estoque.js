const dialogoItem = document.getElementById("editar-item");
const formItem = document.getElementById("form-editar-item");
const nomeItem = document.getElementById("editar-nome");
const quantidadeItem = document.getElementById("editar-quantidade");
const minimoItem = document.getElementById("editar-minimo");
const unidadeItem = document.getElementById("editar-unidade");
let linhaItem;
let botaoItem;

document.querySelectorAll(".editar-estoque").forEach((botao) => {
  botao.addEventListener("click", () => {
    botaoItem = botao;
    linhaItem = botao.closest("tr");
    const celulas = linhaItem.cells;
    nomeItem.value = celulas[0].textContent.trim();
    quantidadeItem.value = parseFloat(celulas[1].textContent.replace(/\./g, "").replace(",", "."));
    minimoItem.value = parseFloat(celulas[2].textContent.replace(/\./g, "").replace(",", "."));
    unidadeItem.value = celulas[1].textContent.trim().split(/\s+/).pop();
    dialogoItem.showModal();
  });
});

document.getElementById("cancelar-edicao").addEventListener("click", () => dialogoItem.close());
nomeItem.addEventListener("input", () => nomeItem.setCustomValidity(""));
formItem.addEventListener("submit", (evento) => {
  evento.preventDefault();
  nomeItem.setCustomValidity(nomeItem.value.trim() ? "" : "Informe o nome do item.");
  if (!formItem.reportValidity()) return;
  const qtd = Number(quantidadeItem.value);
  const minimo = Number(minimoItem.value);
  const celulas = linhaItem.cells;
  celulas[0].textContent = nomeItem.value.trim();
  celulas[1].textContent = `${qtd.toLocaleString("pt-BR")} ${unidadeItem.value}`;
  celulas[2].textContent = `${minimo.toLocaleString("pt-BR")} ${unidadeItem.value}`;
  const status = celulas[3].querySelector(".status");
  status.textContent = qtd < minimo ? "Repor" : "Regular";
  status.classList.toggle("verde", qtd >= minimo);
  botaoItem.setAttribute("aria-label", `Editar ${nomeItem.value.trim()}`);
  dialogoItem.close();
  filtrarEstoque();
});

const botaoCadastrar = document.querySelector('.cadastrar-item');
const cadastroItem = document.getElementById('cadastro-item');
botaoCadastrar.addEventListener('click', () => {
  cadastroItem.showModal();
});
document.getElementById('fechar-cadastro').addEventListener('click', () => {
  cadastroItem.close();
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
