from re import match

def validar_senha_forte(senha:str = None) -> bool:
    """Valida se a senha atende aos requisitos mínimos de segurança.

    A senha deve ter no mínimo 5 caracteres e conter ao menos uma letra
    maiúscula, uma minúscula, um número e um caractere especial.

    Args:
        senha (str, optional): senha a ser validada.

    Returns:
        bool: True se a senha for forte; False caso contrário.
    """
    
    regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=!_*-]).{5,}$"
    
    if match(regex, senha):
        return True
    else:
        return False