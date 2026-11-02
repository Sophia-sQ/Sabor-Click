const detalhes = document.getElementById("detalhes-pedido");
const tituloPedido = document.getElementById("titulo-pedido");
const etapas = detalhes.querySelector(".etapas-pedido");
const botoesPedidos = document.querySelectorAll(".abrir-pedido");

document.querySelectorAll(".assumir-pedido").forEach((botao) => {
  botao.addEventListener("click", () => {
    const celula = botao.closest(".chefe-pedido");
    celula.textContent = "Você";
    celula.setAttribute("tabindex", "-1");
    celula.focus();
  });
});

botoesPedidos.forEach((botao) => {
  botao.addEventListener("click", () => {
    const fechar = botao.getAttribute("aria-expanded") === "true";
    botoesPedidos.forEach((item) => item.setAttribute("aria-expanded", "false"));
    detalhes.hidden = fechar;
    if (fechar) return;

    botao.setAttribute("aria-expanded", "true");
    tituloPedido.textContent = `Pedido #${botao.dataset.pedido}`;
    const concluido = botao.dataset.pedido === "02";
    const nomes = ["Pedido recebido", "Em preparo", "Aguardando entrega"];
    if (concluido) nomes.push("Concluído");
    etapas.replaceChildren(...nomes.map((nome, indice) => {
      const item = document.createElement("li");
      if (indice === (concluido ? 3 : 1)) {
        item.setAttribute("aria-current", "step");
        const destaque = document.createElement("strong");
        destaque.textContent = nome;
        item.append(destaque);
      } else {
        item.textContent = nome;
      }
      return item;
    }));
    detalhes.scrollIntoView({ behavior: "smooth", block: "nearest" });
  });
});
