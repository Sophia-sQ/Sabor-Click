/* Registros demonstrativos locais; o período filtra os mesmos registros em todos os gráficos. */
(() => {
  'use strict';
  const form = document.getElementById('form-periodo');
  if (!form) return;
  const seletor = document.getElementById('periodo-opcao');
  const inicio = document.getElementById('periodo-inicio');
  const fim = document.getElementById('periodo-fim');
  const erro = document.getElementById('erro-periodo');
  const hoje = new Date(); hoje.setHours(0, 0, 0, 0);
  const deslocar = (data, dias) => { const d = new Date(data); d.setDate(d.getDate() + dias); return d; };
  const iso = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  const lerData = valor => { const [ano, mes, dia] = valor.split('-').map(Number); return new Date(ano, mes-1, dia); };
  const moeda = v => v.toLocaleString('pt-BR', {style:'currency',currency:'BRL',maximumFractionDigits:0});
  const dataCurta = d => d.toLocaleDateString('pt-BR', {day:'2-digit',month:'2-digit'});
  const nomes = ['aguardando confirmação','em preparo','concluídos','cancelados'];
  const cores = ['#c49b5b','#a36748','#798869','#b7ada0'];
  // Últimas seis semanas reproduzem os totais da prévia original.
  const registros = [];
  for (let semana=0; semana<26; semana++) {
    const receita = [22000,17000,12000,14000,11000,8000][semana%6];
    const itens = [0,2,4,6].map((dia, i) => {
      const indice = (semana*4+i)%24;
      const status = indice<8 ? 0 : indice<14 ? 1 : indice<21 ? 2 : 3;
      return {data:deslocar(hoje,-semana*7-dia),status};
    });
    const ativos = itens.filter(i => i.status!==3).length;
    itens.forEach(i => { i.receita = i.status===3 ? 0 : receita/ativos; i.custo=i.receita*52/84; registros.push(i); });
  }
  inicio.value=iso(deslocar(hoje,-41)); fim.value=iso(hoje);
  seletor.addEventListener('change', () => {
    const customizado=seletor.value==='personalizado';
    document.getElementById('datas-periodo').hidden=!customizado;
    inicio.required=customizado; fim.required=customizado;
    erro.hidden=true;
  });
  function aplicar(event) {
    event?.preventDefault();
    let de, ate=new Date(hoje);
    if (seletor.value==='personalizado') {
      if (!inicio.value || !fim.value) return;
      de=lerData(inicio.value); ate=lerData(fim.value);
    } else if (seletor.value==='mes') de=new Date(hoje.getFullYear(),hoje.getMonth(),1);
    else if (seletor.value==='anterior') { de=new Date(hoje.getFullYear(),hoje.getMonth()-1,1); ate=new Date(hoje.getFullYear(),hoje.getMonth(),0); }
    else de=deslocar(hoje,1-Number(seletor.value));
    if (de>ate) { erro.textContent='A data final deve ser igual ou posterior à inicial.'; erro.hidden=false; return; }
    erro.hidden=true;
    const itens=registros.filter(i=>i.data>=de && i.data<=ate);
    const receita=itens.reduce((n,i)=>n+i.receita,0);
    const custo=itens.reduce((n,i)=>n+i.custo,0);
    const contagens=nomes.map((_,s)=>itens.filter(i=>i.status===s).length);
    document.querySelector('.cartao-escuro>strong').textContent=moeda(receita);
    document.querySelector('.cartao-escuro .cartao-base>span').textContent=`${itens.length-contagens[3]} pedidos ativos ou concluídos`;
    document.querySelector('.custo-resumo strong').textContent=moeda(custo);
    document.querySelectorAll('.lista-status strong').forEach((el,i)=>el.textContent=String(contagens[i]).padStart(2,'0'));
    const rosca=document.querySelector('.grafico-rosca');
    rosca.querySelector('strong').textContent=itens.length;
    rosca.classList.toggle('sem-dados',!itens.length);
    let acumulado=0;
    rosca.style.background=itens.length ? `conic-gradient(${contagens.map((n,i)=>{const a=acumulado;acumulado+=n/itens.length*100;return `${cores[i]} ${a}% ${acumulado}%`;}).join(',')})` : '#e3d9cb';
    rosca.setAttribute('aria-label',`${itens.length} pedidos: ${contagens.map((n,i)=>`${n} ${nomes[i]}`).join(', ')}.`);
    const rotulo=seletor.value==='personalizado' ? `${dataCurta(de)} – ${dataCurta(ate)}` : seletor.selectedOptions[0].textContent;
    document.getElementById('periodo-atual').textContent=rotulo;
    document.querySelector('.selo-periodo').textContent=rotulo;
    const dias=Math.round((Date.UTC(ate.getFullYear(),ate.getMonth(),ate.getDate())-Date.UTC(de.getFullYear(),de.getMonth(),de.getDate()))/86400000)+1;
    const grupos=Math.min(6,dias);
    const limites=Array.from({length:grupos},(_,i)=>({de:deslocar(de,Math.floor(i*dias/grupos)),ate:deslocar(de,Math.floor((i+1)*dias/grupos)-1),valor:0}));
    itens.forEach(item=>{ const g=limites.find(g=>item.data>=g.de&&item.data<=g.ate); if(g) g.valor+=item.receita; });
    const maximo=Math.max(1,...limites.map(g=>g.valor));
    const grafico=document.querySelector('.grafico-barras');
    document.getElementById('titulo-evolucao').textContent='Receita no período';
    grafico.replaceChildren();
    if (!itens.length) {
      const p=document.createElement('p');p.className='grafico-vazio';p.textContent='Nenhum pedido ilustrativo neste período.';grafico.append(p);
    } else limites.forEach(g=>{
      const coluna=document.createElement('div');coluna.className='coluna-grafico';
      const valor=document.createElement('span');valor.textContent=moeda(g.valor);
      const trilho=document.createElement('div');trilho.className='trilho-barra';
      const barra=document.createElement('div');barra.style.height=`${g.valor/maximo*100}%`;trilho.append(barra);
      const label=document.createElement('small');label.textContent=dataCurta(g.de);label.title=`${dataCurta(g.de)} a ${dataCurta(g.ate)}`;
      coluna.append(valor,trilho,label);grafico.append(coluna);
    });
    grafico.setAttribute('aria-label',`Receitas ilustrativas: ${limites.map(g=>`${dataCurta(g.de)} a ${dataCurta(g.ate)}: ${moeda(g.valor)}`).join('; ')}.`);
    if (event) document.querySelector('.seletor-periodo').open=false;
  }
  form.addEventListener('submit',aplicar);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'){document.querySelector('.seletor-periodo').open=false;document.querySelector('.seletor-periodo summary').focus();}});
  document.addEventListener('click',e=>{if(!e.target.closest('.seletor-periodo'))document.querySelector('.seletor-periodo').open=false;});
  aplicar();
})();
