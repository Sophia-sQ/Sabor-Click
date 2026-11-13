/* Prévia do frontend: dados ilustrativos em memória, sem chamadas ao backend. */
(() => {
    'use strict';
    const fichas = {
        arroz: {nome: 'Arroz branco', tempo: 25, prePreparo: false, ingredientes: [
            {id: 1, nome: 'Arroz', unidade: 'g', quantidade: 100},
            {id: 2, nome: 'Água', unidade: 'ml', quantidade: 200}
        ]},
        frango: {nome: 'Frango grelhado', tempo: 30, prePreparo: true, ingredientes: [
            {id: 3, nome: 'Filé de frango', unidade: 'g', quantidade: 150},
            {id: 4, nome: 'Azeite', unidade: 'ml', quantidade: 10}
        ]},
        suco: {nome: 'Suco de laranja', tempo: 10, prePreparo: false, ingredientes: [
            {id: 5, nome: 'Laranja', unidade: 'un', quantidade: 3}
        ]}
    };
    const pedidos = [
        {id: 104, recebido: '12h00', status: 'aguardando', observacao: 'Enviar talheres.', itens: [{ficha: 'arroz', quantidade: 2}, {ficha: 'frango', quantidade: 2}, {ficha: 'suco', quantidade: 2}]},
        {id: 105, recebido: '12h10', status: 'aguardando', observacao: 'Sem observações.', itens: [{ficha: 'arroz', quantidade: 3}, {ficha: 'frango', quantidade: 3}]},
        {id: 106, recebido: '12h15', status: 'aguardando', observacao: 'Sem observações.', itens: [{ficha: 'suco', quantidade: 4}]}
    ];
    const estados = {aguardando: 'Aguardando chef', confirmado: 'Aceito', 'em preparo': 'Em preparo', concluido: 'Concluído'};
    const separados = new Map();
    let selecionado = null;
    const el = id => document.getElementById(id);
    const criar = (tag, texto, classe) => {
        const node = document.createElement(tag);
        if (texto !== undefined) node.textContent = texto;
        if (classe) node.className = classe;
        return node;
    };
    const numero = valor => new Intl.NumberFormat('pt-BR', {maximumFractionDigits: 3}).format(valor);
    const chave = ingrediente => `${ingrediente.id}:${ingrediente.unidade}`;
    const totais = pedido => {
        const soma = new Map();
        pedido.itens.forEach(item => fichas[item.ficha].ingredientes.forEach(ingrediente => {
            const id = chave(ingrediente);
            if (!soma.has(id)) soma.set(id, {...ingrediente, quantidade: 0});
            soma.get(id).quantidade += ingrediente.quantidade * item.quantidade;
        }));
        return [...soma.values()].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));
    };
    function renderizarFila() {
        el('fila-pedidos').replaceChildren();
        pedidos.forEach(pedido => {
            const card = criar('article', undefined, `card pedido-cozinha${pedido === selecionado ? ' selecionado' : ''}`);
            card.append(criar('span', estados[pedido.status], `status${pedido.status === 'concluido' ? ' verde' : ''}`), criar('span', pedido.recebido, 'pedido-momento'), criar('h3', `Pedido #${pedido.id}`));
            card.append(criar('p', pedido.itens.map(item => `${item.quantidade} × ${fichas[item.ficha].nome}`).join(' · ')), criar('p', pedido.observacao, 'muted'));
            const botao = criar('button', pedido.status === 'aguardando' ? 'Aceitar pedido' : 'Ver ficha de preparo', pedido.status === 'aguardando' ? '' : 'ver-ficha');
            botao.type = 'button';
            botao.setAttribute('aria-label', `${botao.textContent} #${pedido.id}`);
            botao.setAttribute('aria-controls', 'preparo-conteudo');
            botao.addEventListener('click', () => {
                if (pedido.status === 'aguardando') {
                    pedido.status = 'confirmado';
                    separados.set(pedido.id, new Set());
                    el('mensagem-cozinha').textContent = `Pedido #${pedido.id} aceito nesta prévia. Confira os itens necessários.`;
                }
                selecionado = pedido;
                renderizarFila();
                renderizarPreparo();
                el('pedido-selecionado').focus();
            });
            card.append(botao);
            el('fila-pedidos').append(card);
        });
        el('total-aguardando').textContent = pedidos.filter(p => p.status === 'aguardando').length;
        el('total-preparo').textContent = pedidos.filter(p => ['confirmado', 'em preparo'].includes(p.status)).length;
        el('total-concluido').textContent = pedidos.filter(p => p.status === 'concluido').length;
    }
    function atualizarProgresso() {
        const total = totais(selecionado).length;
        const marcados = separados.get(selecionado.id).size;
        el('progresso-separacao').textContent = `${marcados} de ${total} separados`;
        el('avancar-preparo').disabled = selecionado.status === 'concluido' || (selecionado.status === 'confirmado' && marcados !== total);
    }
    function renderizarPreparo() {
        const pedido = selecionado;
        el('preparo-vazio').hidden = true;
        el('preparo-conteudo').hidden = false;
        el('pedido-selecionado').textContent = `Pedido #${pedido.id}`;
        el('resumo-preparo').textContent = `${estados[pedido.status]} · Recebido às ${pedido.recebido} · Responsável: você (prévia)`;
        el('observacao-preparo').textContent = `Observação: ${pedido.observacao}`;
        el('itens-pedido').replaceChildren(...pedido.itens.map(item => criar('li', `${item.quantidade} × ${fichas[item.ficha].nome}`)));
        el('ingredientes-preparo').replaceChildren();
        totais(pedido).forEach(ingrediente => {
            const linha = criar('div', undefined, 'ingrediente-preparo');
            const label = criar('label');
            const check = criar('input');
            check.type = 'checkbox';
            check.checked = separados.get(pedido.id).has(chave(ingrediente));
            check.disabled = pedido.status !== 'confirmado';
            check.addEventListener('change', () => {
                const marcados = separados.get(pedido.id);
                if (check.checked) marcados.add(chave(ingrediente));
                else marcados.delete(chave(ingrediente));
                atualizarProgresso();
            });
            label.append(check, criar('span', ingrediente.nome));
            linha.append(label, criar('strong', `${numero(ingrediente.quantidade)} ${ingrediente.unidade}`));
            el('ingredientes-preparo').append(linha);
        });
        el('avancar-preparo').textContent = {confirmado: 'Iniciar preparo', 'em preparo': 'Concluir preparo', concluido: 'Preparo concluído'}[pedido.status];
        el('ajuda-status').textContent = {confirmado: 'Separe todos os ingredientes para iniciar o preparo.', 'em preparo': 'Conclua quando todos os itens do pedido estiverem prontos.', concluido: 'Este pedido já saiu da fila de preparo.'}[pedido.status];
        atualizarProgresso();
    }
    el('avancar-preparo').addEventListener('click', () => {
        if (!selecionado || el('avancar-preparo').disabled) return;
        selecionado.status = selecionado.status === 'confirmado' ? 'em preparo' : 'concluido';
        el('mensagem-cozinha').textContent = `Pedido #${selecionado.id}: ${estados[selecionado.status].toLowerCase()} nesta prévia.`;
        renderizarFila();
        renderizarPreparo();
        el('pedido-selecionado').focus();
    });
    renderizarFila();
})();
