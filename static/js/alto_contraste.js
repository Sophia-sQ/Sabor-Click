
const botaoContraste = document.getElementById(
    "botao-alto-contraste"
);

const CHAVE_CONTRASTE = "saborClickAltoContraste";

function aplicarAltoContraste(ativado) {
    document.body.classList.toggle(
        "alto-contraste",
        ativado
    );

    botaoContraste.setAttribute(
        "aria-pressed",
        String(ativado)
    );

    botaoContraste.textContent = ativado
        ? "Desativar alto contraste"
        : "Ativar alto contraste";

    localStorage.setItem(
        CHAVE_CONTRASTE,
        String(ativado)
    );
}

if (botaoContraste) {

    // Recupera a preferência salva
    const contrasteSalvo =
        localStorage.getItem(CHAVE_CONTRASTE) === "true";

    aplicarAltoContraste(contrasteSalvo);

    // Alterna o modo ao clicar
    botaoContraste.addEventListener("click", () => {

        const ativado =
            !document.body.classList.contains("alto-contraste");

        aplicarAltoContraste(ativado);

    });
}
