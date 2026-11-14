// Alterna, por pedido, o painel de detalhes renderizado pelo servidor.
// Cada botão .abrir-pedido controla, via aria-controls, o painel real
// (#detalhes-pedido-<id>) daquele pedido. Não há dados fictícios: o conteúdo
// exibido vem do HTML gerado a partir do banco.
const botoesPedidos = document.querySelectorAll(".abrir-pedido");
const paineisPedidos = document.querySelectorAll(".detalhes-pedido");

botoesPedidos.forEach((botao) => {
  botao.addEventListener("click", () => {
    const painel = document.getElementById(botao.getAttribute("aria-controls"));
    if (!painel) return;

    const abrir = botao.getAttribute("aria-expanded") !== "true";

    // Fecha todos os painéis e recolhe todos os botões antes de abrir o alvo.
    botoesPedidos.forEach((item) => item.setAttribute("aria-expanded", "false"));
    paineisPedidos.forEach((item) => { item.hidden = true; });

    if (!abrir) return;

    botao.setAttribute("aria-expanded", "true");
    painel.hidden = false;
    painel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
});
