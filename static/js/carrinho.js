const dialogo = document.getElementById('dialogo-endereco');
const endereco = document.getElementById('endereco-linha');
const cidade = document.getElementById('endereco-cidade');
const formulario = document.getElementById('formulario-endereco');
const campoEndereco = document.getElementById('novo-endereco');
const campoCidade = document.getElementById('nova-cidade');
const cep = document.getElementById('endereco-cep');
const bairro = document.getElementById('endereco-bairro');
const uf = document.getElementById('endereco-uf');
const numero = document.getElementById('endereco-numero');
const complemento = document.getElementById('endereco-complemento');
const statusCep = document.getElementById('status-cep');
let consulta;

document.getElementById('escolher-endereco')?.addEventListener('click', () => {
  dialogo.showModal();
  cep.focus();
});

cep.addEventListener('input', async () => {
  consulta?.abort();
  const digitos = cep.value.replace(/\D/g, '').slice(0, 8);
  cep.value = digitos.replace(/^(\d{5})(\d)/, '$1-$2');
  statusCep.textContent = 'Digite os 8 dígitos do CEP ou preencha o endereço manualmente.';
  if (digitos.length !== 8) return;
  const atual = new AbortController();
  consulta = atual;
  const limite = setTimeout(() => atual.abort(), 8000);
  statusCep.textContent = 'Buscando endereço…';
  try {
    const resposta = await fetch(`https://viacep.com.br/ws/${digitos}/json/`, { signal: atual.signal });
    if (!resposta.ok) throw new Error('Falha na consulta');
    const dados = await resposta.json();
    if (atual.signal.aborted || consulta !== atual) return;
    if (dados.erro) {
      statusCep.textContent = 'CEP não encontrado. Confira o CEP ou preencha os campos manualmente.';
      return;
    }
    campoEndereco.value = dados.logradouro || '';
    bairro.value = dados.bairro || '';
    campoCidade.value = dados.localidade || '';
    uf.value = dados.uf || '';
    statusCep.textContent = 'Endereço encontrado. Confira os campos e informe o número e complemento, se houver.';
  } catch (erro) {
    if (consulta !== atual) return;
    statusCep.textContent = 'Não foi possível consultar o CEP. Preencha o endereço manualmente.';
  } finally {
    clearTimeout(limite);
  }
});

dialogo.addEventListener('close', () => consulta?.abort());
document.getElementById('cancelar-endereco').addEventListener('click', () => dialogo.close());
formulario.addEventListener('submit', (evento) => {
  evento.preventDefault();
  if (!formulario.reportValidity()) return;
  consulta?.abort();
  endereco.textContent = `${campoEndereco.value.trim()}, ${numero.value.trim()}${complemento.value.trim() ? ' · ' + complemento.value.trim() : ''} • ${bairro.value.trim()}`;
  cidade.textContent = `${campoCidade.value.trim()} - ${uf.value.trim().toUpperCase()} • CEP ${cep.value}`;
  dialogo.close();
});

document.getElementById('finalizar-compra')?.addEventListener('click', () => {
  const aviso = document.getElementById('aviso-carrinho');
  aviso.textContent = 'A finalização da compra ainda não está disponível. Nenhum pedido foi enviado.';
  aviso.hidden = false;
});
