(() => {
  'use strict';
  const input=document.getElementById('buscar-catalogo');
  const itens=[...document.querySelectorAll('.item-catalogo')];
  const normalizar=t=>t.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  input.addEventListener('input',()=>{let total=0;itens.forEach(item=>{item.hidden=!normalizar(item.dataset.nome).includes(normalizar(input.value.trim()));if(!item.hidden)total++;});document.getElementById('catalogo-vazio').hidden=total>0;});
  const link=document.getElementById('imagem-link');
  const imagem=document.getElementById('previa-imagem');
  const placeholder=document.getElementById('placeholder-imagem');
  const status=document.getElementById('status-imagem');
  const original=imagem.getAttribute('src');
  function mostrar(src){imagem.hidden=!src;placeholder.hidden=!!src; if(src)imagem.src=src;else imagem.removeAttribute('src');}
  link.addEventListener('input', () => {
    status.textContent = '';
    const valor = link.value.trim();
    mostrar(/^https?:\/\//i.test(valor) ? valor : original);
  });
  imagem.addEventListener('error', () => {
    status.textContent = 'Não foi possível visualizar a imagem. Confira o link.';
    imagem.hidden = true;
    placeholder.hidden = false;
  });
  imagem.addEventListener('load',()=>{status.textContent='';imagem.hidden=false;placeholder.hidden=true;});
  const dialogo=document.getElementById('confirmar-remocao');
  document.querySelectorAll('.remover-item').forEach(botao=>botao.addEventListener('click',()=>{
    document.getElementById('remover-id').value=botao.dataset.id;
    document.getElementById('remover-descricao').textContent=`“${botao.dataset.nome}” deixará de aparecer nas opções do cliente.`;
    dialogo.showModal();
  }));
  document.getElementById('cancelar-remocao').addEventListener('click',()=>dialogo.close());
})();
