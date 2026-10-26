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
});

const botaoCadastrar = document.querySelector('.cadastrar-item');
const cadastroItem = document.getElementById('cadastro-item');
botaoCadastrar.addEventListener('click', () => {
  cadastroItem.showModal();
});
document.getElementById('fechar-cadastro').addEventListener('click', () => {
  cadastroItem.close();
});
