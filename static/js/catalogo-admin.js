(() => {
  'use strict';
  const input=document.getElementById('buscar-catalogo');
  const itens=[...document.querySelectorAll('.item-catalogo')];
  const normalizar=t=>t.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  input.addEventListener('input',()=>{let total=0;itens.forEach(item=>{item.hidden=!normalizar(item.dataset.nome).includes(normalizar(input.value.trim()));if(!item.hidden)total++;});document.getElementById('catalogo-vazio').hidden=total>0;});
  const arquivo=document.getElementById('imagem-arquivo');
  const link=document.getElementById('imagem-link');
  const imagem=document.getElementById('previa-imagem');
  const placeholder=document.getElementById('placeholder-imagem');
  const status=document.getElementById('status-imagem');
  const original=imagem.getAttribute('src');
  let objeto;
  function mostrar(src){imagem.hidden=!src;placeholder.hidden=!!src; if(src)imagem.src=src;else imagem.removeAttribute('src');}
  arquivo.addEventListener('change',()=>{
    status.textContent='';arquivo.setCustomValidity('');
    if(objeto){URL.revokeObjectURL(objeto);objeto=null;}
    const foto=arquivo.files[0];
    if(!foto){mostrar(original);return;}
    if(foto.size>5*1024*1024 || !['image/png','image/jpeg','image/webp'].includes(foto.type)){
      arquivo.setCustomValidity('Escolha uma imagem PNG, JPG ou WebP de até 5 MB.');status.textContent=arquivo.validationMessage;mostrar(original);return;
    }
    link.value='';objeto=URL.createObjectURL(foto);mostrar(objeto);
  });
  link.addEventListener('input',()=>{status.textContent='';if(objeto){URL.revokeObjectURL(objeto);objeto=null;}arquivo.value='';arquivo.setCustomValidity(''); const valor=link.value.trim();mostrar(/^https?:\/\//i.test(valor)?valor:original);});
  imagem.addEventListener('error',()=>{status.textContent='Não foi possível visualizar a imagem. Confira o arquivo ou link.';imagem.hidden=true;placeholder.hidden=false;});
  imagem.addEventListener('load',()=>{status.textContent='';imagem.hidden=false;placeholder.hidden=true;});
  const dialogo=document.getElementById('confirmar-remocao');
  document.querySelectorAll('.remover-item').forEach(botao=>botao.addEventListener('click',()=>{
    document.getElementById('remover-id').value=botao.dataset.id;
    document.getElementById('remover-descricao').textContent=`“${botao.dataset.nome}” deixará de aparecer nas opções do cliente.`;
    dialogo.showModal();
  }));
  document.getElementById('cancelar-remocao').addEventListener('click',()=>dialogo.close());
})();
