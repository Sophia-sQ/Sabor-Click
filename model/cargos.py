"""Enumeração dos níveis de permissão (cargos) dos usuários."""

from enum import IntEnum

class Cargo(IntEnum):
    """Níveis de permissão dos usuários (ordem crescente de privilégio).

    Valores: CLIENTE=1, CHEFE=2, ADMIN=3. Devem coincidir com os ids gravados na
    tabela nivel_permissao.
    """
    CLIENTE = 1
    CHEFE = 2
    ADMIN = 3
