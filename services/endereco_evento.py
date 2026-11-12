"""Validação e apresentação do endereço usado no carrinho e no checkout."""

UFS = set("AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split())


def validar_endereco_evento(dados):
    if not isinstance(dados, dict):
        raise ValueError("Informe os dados do endereço.")
    limites = {"rua": 150, "numero": 20, "complemento": 80, "bairro": 100, "cidade": 100, "cep": 9, "uf": 2}
    endereco = {}
    for campo, limite in limites.items():
        valor = dados.get(campo, "")
        if not isinstance(valor, str) or len(valor.strip()) > limite:
            raise ValueError("Confira os campos do endereço.")
        endereco[campo] = valor.strip()
    if any(not endereco[campo] for campo in ("rua", "numero", "bairro", "cidade")):
        raise ValueError("Preencha rua, número, bairro e cidade.")
    cep = endereco["cep"].replace("-", "")
    if len(cep) != 8 or not cep.isascii() or not cep.isdigit():
        raise ValueError("Informe um CEP com 8 números.")
    endereco["cep"] = cep[:5] + "-" + cep[5:]
    endereco["uf"] = endereco["uf"].upper()
    if endereco["uf"] not in UFS:
        raise ValueError("Informe uma UF válida, como SP.")
    return endereco


def apresentar_endereco_evento(endereco):
    complemento = f" · {endereco['complemento']}" if endereco["complemento"] else ""
    estado = f" - {endereco['uf']}" if endereco["uf"] else ""
    return {
        "endereco_evento": endereco,
        "endereco_linha": f"{endereco['rua']}, {endereco['numero']}{complemento} • {endereco['bairro']}",
        "endereco_cidade": f"{endereco['cidade']}{estado} • CEP {endereco['cep']}",
    }
