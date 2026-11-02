const previa = document.body.dataset.previa === 'true';
const retorno = document.querySelector('#retorno');
const modal = document.querySelector('#modal-endereco');
const formEndereco = document.querySelector('#form-endereco');
document.querySelectorAll('.fechar').forEach(botao => botao.addEventListener('click', () => botao.closest('dialog').close()));
document.querySelector('#novo-endereco').addEventListener('click', () => {
  formEndereco.reset(); formEndereco.action = formEndereco.dataset.criar;
  document.querySelector('#titulo-endereco').textContent = 'Adicionar endereço'; modal.showModal();
});
document.querySelectorAll('.editar').forEach(botao => botao.addEventListener('click', () => {
  const endereco = JSON.parse(botao.dataset.endereco); formEndereco.reset();
  const campos = {nome:'nome',cep:'cep',num:'numero',logadouro:'logradouro',compl:'complemento',bairro:'bairro',cidade:'cidade'};
  Object.entries(campos).forEach(([campo,chave]) => {formEndereco.elements.namedItem(campo).value = endereco[chave] ?? '';});
  formEndereco.action = `/home/endereco/atualizar/${endereco.id_endereco}`;
  document.querySelector('#titulo-endereco').textContent = 'Editar endereço'; modal.showModal();
}));
document.querySelectorAll('.excluir').forEach(botao => botao.addEventListener('click', () => {
  document.querySelector('#descricao-excluir').textContent = `O endereço “${botao.dataset.nome}” será removido da sua conta.`;
  document.querySelector('#form-excluir').action = `/home/endereco/deletar/${botao.dataset.id}`;
  document.querySelector('#modal-excluir').showModal();
}));
const senha = document.querySelector('#senha'); const confirmacao = document.querySelector('#confirmacao');
function conferirSenha(){confirmacao.setCustomValidity(confirmacao.value === senha.value ? '' : 'As senhas precisam ser iguais.');}
senha.addEventListener('input', conferirSenha); confirmacao.addEventListener('input', conferirSenha);
document.querySelector('#mostrar').addEventListener('change', evento => {[senha,confirmacao].forEach(campo => {campo.type = evento.target.checked ? 'text' : 'password';});});
document.querySelectorAll('input[name="cpf"],input[name="cep"]').forEach(campo => campo.addEventListener('input', () => {
  const cpf = campo.name === 'cpf'; const valor = campo.value.replace(/\D/g,'').slice(0,cpf ? 11 : 8);
  campo.value = cpf ? valor.replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d)/,'$1.$2').replace(/(\d{3})(\d{1,2})$/,'$1-$2') : valor.replace(/(\d{5})(\d)/,'$1-$2');
}));
document.querySelectorAll('form').forEach(form => form.addEventListener('submit', evento => {
  form.querySelectorAll('input:not([type="password"]):not([type="checkbox"])').forEach(campo => {campo.value = campo.value.trim();});
  if (!form.reportValidity()){evento.preventDefault();return;}
  if(previa){evento.preventDefault();form.closest('dialog')?.close();retorno.textContent='Formulário conferido. Esta é uma prévia: nenhuma alteração foi salva.';retorno.hidden=false;retorno.focus();}
}));
document.querySelectorAll('.lateral nav a').forEach(link => link.addEventListener('click', () => {document.querySelectorAll('.lateral nav a').forEach(item => item.classList.remove('selecionado'));link.classList.add('selecionado');}));

const modalSair = document.querySelector('#modal-sair');
document.querySelector('#abrir-sair').addEventListener('click', () => modalSair.showModal());
modalSair.addEventListener('click', evento => {
  const area = modalSair.getBoundingClientRect();
  if (evento.target === modalSair && (evento.clientX < area.left || evento.clientX > area.right || evento.clientY < area.top || evento.clientY > area.bottom)) modalSair.close();
});
