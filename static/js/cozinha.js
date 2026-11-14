/* Tela da cozinha (chef): lê a fila do bloco JSON e conversa com o backend
   real para aceitar pedidos e avançar o status por transições válidas. */
(() => {
    'use strict';

    const el = id => document.getElementById(id);
    const criar = (tag, texto, classe) => {
        const node = document.createElement(tag);
        if (texto !== undefined && texto !== null) node.textContent = texto;
        if (classe) node.className = classe;
        return node;
    };
    const numero = valor => new Intl.NumberFormat('pt-BR', {maximumFractionDigits: 3}).format(valor);

    // Rótulos amigáveis de status e a próxima transição válida do fluxo do chef.
    const estados = {
        aguardando: 'Aguardando chef',
        confirmado: 'Aceito',
        'em preparo': 'Em preparo',
        concluido: 'Concluído',
        cancelado: 'Cancelado',
    };
    // confirmado -> em preparo -> concluido (somente transições válidas).
    const proximoStatus = {confirmado: 'em preparo', 'em preparo': 'concluido'};
    const rotuloAvancar = {confirmado: 'Iniciar preparo', 'em preparo': 'Concluir preparo', concluido: 'Preparo concluído'};
    const ajudaStatus = {
        confirmado: 'Separe os ingredientes e inicie o preparo quando estiver pronto.',
        'em preparo': 'Conclua quando todos os itens do pedido estiverem prontos.',
        concluido: 'Este pedido já saiu da fila de preparo.',
    };

    // Fila de pedidos aguardando, lida do bloco JSON renderizado pelo servidor.
    let fila = [];
    try {
        fila = JSON.parse(el('pedidos-cozinha').textContent) || [];
    } catch (erro) {
        fila = [];
    }

    // Pedido que está na bancada do chef (vindo de GET /pedido/preparo).
    let atual = null;
    const separados = new Set();

    function definirMensagem(texto) {
        el('mensagem-cozinha').textContent = texto || '';
    }

    // ------- FILA (pedidos aguardando) -------
    function renderizarFila() {
        const container = el('fila-pedidos');
        container.replaceChildren();

        if (!fila.length) {
            const vazio = criar('p', 'Nenhum pedido aguardando no momento.', 'vazio');
            container.append(vazio);
        } else {
            fila.forEach(pedido => {
                const card = criar('article', undefined, 'card pedido-cozinha');
                card.append(criar('span', estados.aguardando, 'status'));
                if (pedido.criado_em) card.append(criar('span', pedido.criado_em, 'pedido-momento'));
                card.append(criar('h3', `Pedido #${pedido.id_pedido}`));
                if (Array.isArray(pedido.itens) && pedido.itens.length) {
                    card.append(criar('p', pedido.itens.join(' · ')));
                }
                const detalhes = [];
                if (pedido.num_convidados) detalhes.push(`${pedido.num_convidados} convidado(s)`);
                if (pedido.data_evento) detalhes.push(pedido.data_evento);
                if (pedido.valor_total) detalhes.push(pedido.valor_total);
                if (detalhes.length) card.append(criar('p', detalhes.join(' · '), 'muted'));
                if (pedido.observacao) card.append(criar('p', pedido.observacao, 'muted'));

                const botao = criar('button', 'Aceitar pedido');
                botao.type = 'button';
                botao.setAttribute('aria-label', `Aceitar pedido #${pedido.id_pedido}`);
                botao.setAttribute('aria-controls', 'preparo-conteudo');
                botao.addEventListener('click', () => aceitarPedido(pedido.id_pedido, botao));
                card.append(botao);

                container.append(card);
            });
        }
        atualizarContadores();
    }

    function atualizarContadores() {
        el('total-aguardando').textContent = fila.length;
        el('total-preparo').textContent = (atual && ['confirmado', 'em preparo'].includes(atual.status)) ? 1 : 0;
        el('total-concluido').textContent = (atual && atual.status === 'concluido') ? 1 : 0;
    }

    // ------- BANCADA DE PREPARO (pedido atual do chef) -------
    function ingredientesAgregados(pedido) {
        const soma = new Map();
        const acumular = ficha => (ficha || []).forEach(ingrediente => {
            const nome = ingrediente.nome || ingrediente.ingrediente || 'Ingrediente';
            const unidade = ingrediente.unidade || '';
            const chave = `${ingrediente.id_ingrediente}:${unidade}`;
            const qtd = Number(ingrediente.qtd_necessaria) || 0;
            if (!soma.has(chave)) soma.set(chave, {nome, unidade, quantidade: 0});
            soma.get(chave).quantidade += qtd;
        });
        (pedido.cardapios || []).forEach(cardapio => (cardapio.pratos || []).forEach(prato => acumular(prato.ficha_tecnica)));
        (pedido.bebidas || []).forEach(bebida => acumular(bebida.ficha_tecnica));
        return [...soma.values()].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
    }

    function itensDoPedido(pedido) {
        const itens = [];
        (pedido.cardapios || []).forEach(cardapio => (cardapio.pratos || []).forEach(prato => {
            itens.push(`${prato.qtd || 1} × ${prato.nome || 'Prato'}`);
        }));
        (pedido.bebidas || []).forEach(bebida => {
            itens.push(`${bebida.qtd || 1} × ${bebida.nome || 'Bebida'}`);
        });
        return itens;
    }

    // Bancadas (estações de trabalho) dos serviços em que o pedido foi
    // contratado. Vêm já deduplicadas e apenas ativas do backend; aqui só
    // renderizamos no mesmo padrão de "Itens do pedido". Sem bancadas, a seção
    // fica oculta (como a bancada vazia) em vez de mostrar um bloco vazio.
    function renderizarBancadas(pedido) {
        const secao = el('bancadas-preparo');
        const lista = el('lista-bancadas');
        const bancadas = Array.isArray(pedido.bancadas) ? pedido.bancadas : [];
        if (!bancadas.length) {
            lista.replaceChildren();
            secao.hidden = true;
            return;
        }
        lista.replaceChildren(...bancadas.map(bancada => {
            const item = criar('li');
            item.append(criar('span', bancada.nome || 'Bancada'));
            if (bancada.descricao) item.append(criar('span', bancada.descricao, 'muted'));
            return item;
        }));
        secao.hidden = false;
    }

    function mostrarBancadaVazia() {
        el('preparo-vazio').hidden = false;
        el('preparo-conteudo').hidden = true;
        atualizarContadores();
    }

    function renderizarPreparo() {
        if (!atual) {
            mostrarBancadaVazia();
            return;
        }
        el('preparo-vazio').hidden = true;
        el('preparo-conteudo').hidden = false;

        el('pedido-selecionado').textContent = `Pedido #${atual.id_pedido}`;
        el('resumo-preparo').textContent = `${estados[atual.status] || atual.status} · Responsável: você`;
        el('observacao-preparo').textContent = atual.observacao ? `Observação: ${atual.observacao}` : '';

        el('itens-pedido').replaceChildren(...itensDoPedido(atual).map(texto => criar('li', texto)));

        renderizarBancadas(atual);

        const ingredientes = ingredientesAgregados(atual);
        const container = el('ingredientes-preparo');
        container.replaceChildren();
        ingredientes.forEach(ingrediente => {
            const chave = `${ingrediente.nome}:${ingrediente.unidade}`;
            const linha = criar('div', undefined, 'ingrediente-preparo');
            const label = criar('label');
            const check = criar('input');
            check.type = 'checkbox';
            check.checked = separados.has(chave);
            check.disabled = atual.status !== 'confirmado';
            check.addEventListener('change', () => {
                if (check.checked) separados.add(chave);
                else separados.delete(chave);
                atualizarProgresso(ingredientes.length);
            });
            label.append(check, criar('span', ingrediente.nome));
            linha.append(label, criar('strong', `${numero(ingrediente.quantidade)} ${ingrediente.unidade}`.trim()));
            container.append(linha);
        });

        el('avancar-preparo').textContent = rotuloAvancar[atual.status] || 'Avançar';
        el('ajuda-status').textContent = ajudaStatus[atual.status] || '';
        atualizarProgresso(ingredientes.length);
        atualizarContadores();
    }

    function atualizarProgresso(total) {
        el('progresso-separacao').textContent = `${separados.size} de ${total} separados`;
        const avancar = el('avancar-preparo');
        if (!atual || !proximoStatus[atual.status]) {
            avancar.disabled = true;
            return;
        }
        // Só libera iniciar o preparo quando todos os ingredientes forem separados.
        avancar.disabled = atual.status === 'confirmado' && separados.size !== total;
    }

    // Rebusca a fila de 'aguardando' do servidor e re-renderiza os cards.
    // Usado após concluir um pedido, quando a bancada é liberada e novos
    // pedidos da fila voltam a poder ser aceitos.
    async function carregarFila() {
        try {
            const resposta = await fetch('/pedido/cozinha/fila', {headers: {Accept: 'application/json'}});
            if (resposta.redirected || !resposta.headers.get('content-type')?.includes('application/json')) {
                throw new Error('Sua sessão expirou. Entre na sua conta e tente novamente.');
            }
            if (!resposta.ok) throw new Error('Não foi possível atualizar a fila de pedidos.');
            fila = await resposta.json() || [];
            renderizarFila();
        } catch (erro) {
            definirMensagem(erro.message || 'Não foi possível atualizar a fila de pedidos.');
        }
    }

    async function carregarPreparo() {
        try {
            const resposta = await fetch('/pedido/preparo', {headers: {Accept: 'application/json'}});
            if (resposta.status === 404) {
                atual = null;
                mostrarBancadaVazia();
                return;
            }
            if (resposta.redirected || !resposta.headers.get('content-type')?.includes('application/json')) {
                throw new Error('Sua sessão expirou. Entre na sua conta e tente novamente.');
            }
            if (!resposta.ok) throw new Error('Não foi possível carregar o pedido atual.');
            atual = await resposta.json();
            separados.clear();
            renderizarPreparo();
        } catch (erro) {
            atual = null;
            mostrarBancadaVazia();
            definirMensagem(erro.message || 'Não foi possível carregar o pedido atual.');
        }
    }

    // ------- AÇÕES (aceitar / avançar) -------
    async function aceitarPedido(idPedido, botao) {
        if (botao) botao.disabled = true;
        definirMensagem('');
        try {
            const resposta = await fetch('/pedido/aceitar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: idPedido}),
            });
            if (resposta.redirected || !resposta.headers.get('content-type')?.includes('application/json')) {
                throw new Error('Sua sessão expirou. Entre na sua conta e tente novamente.');
            }
            const dados = await resposta.json();
            if (!resposta.ok || !dados.ok) {
                throw new Error(dados.erro || 'Não foi possível aceitar o pedido.');
            }
            // Remove da fila local e recarrega a bancada a partir do servidor.
            fila = fila.filter(pedido => pedido.id_pedido !== idPedido);
            renderizarFila();
            await carregarPreparo();
            definirMensagem(`Pedido #${idPedido} aceito. Confira os itens necessários.`);
            el('pedido-selecionado').focus();
        } catch (erro) {
            definirMensagem(erro.message || 'Não foi possível aceitar o pedido.');
            if (botao) botao.disabled = false;
        }
    }

    async function avancarPreparo() {
        if (!atual) return;
        const alvo = proximoStatus[atual.status];
        if (!alvo) return;
        const botao = el('avancar-preparo');
        botao.disabled = true;
        definirMensagem('');
        try {
            const resposta = await fetch('/pedido/atualizar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: atual.id_pedido, status: alvo}),
            });
            if (resposta.redirected || !resposta.headers.get('content-type')?.includes('application/json')) {
                throw new Error('Sua sessão expirou. Entre na sua conta e tente novamente.');
            }
            const dados = await resposta.json();
            if (!resposta.ok || !dados.ok) {
                throw new Error(dados.erro || 'Não foi possível atualizar o pedido.');
            }
            const statusFinal = dados.status || alvo;
            if (statusFinal === 'em preparo') separados.clear();
            if (statusFinal === 'concluido') {
                // Pedido concluído: libera a bancada e rebusca a fila do servidor
                // para que novos pedidos 'aguardando' voltem a poder ser aceitos.
                const idConcluido = atual.id_pedido;
                atual = null;
                separados.clear();
                mostrarBancadaVazia();
                definirMensagem(`Pedido #${idConcluido}: ${(estados[statusFinal] || statusFinal).toLowerCase()}.`);
                await carregarFila();
            } else {
                atual.status = statusFinal;
                definirMensagem(`Pedido #${atual.id_pedido}: ${(estados[statusFinal] || statusFinal).toLowerCase()}.`);
                renderizarPreparo();
            }
        } catch (erro) {
            definirMensagem(erro.message || 'Não foi possível atualizar o pedido.');
            renderizarPreparo();
        }
    }

    el('avancar-preparo').addEventListener('click', avancarPreparo);

    renderizarFila();
    carregarPreparo();
})();
