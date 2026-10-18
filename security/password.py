from re import match

def validar_senha_forte(senha:str = None) -> bool:
    """Verifica se a senha tem no mínimo 5 caracteres. Entre eles devem existir 
    pelo menos um maiúsculo, um minúsculo, um número e um caracter especial.
    
    Retorna True em caso positivo e False em caso negativo."""
    
    regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=!_*-]).{5,}$"
    
    if match(senha, regex):
        return True
    else:
        False