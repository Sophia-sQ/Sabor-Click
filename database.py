from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from model.usuario_model import criar_usuario
from model.cargos import Cargo
from model.usuario_model import Usuario, NivelPermissao, criar_usuario
from model.servico_model import criar_servico, criar_bancada, criar_cardapio
from model.ficha_model import criar_prato, criar_ingrediente,criar_lote
from datetime import datetime, timedelta

from os import environ

#classe base: Não contém nada, pois utiliza o padrão do Python
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)



# ADMIN INICIAL CADASTRO
def criar_admin():
    # verifica se ja existe admin
    #email_admin = environ.get("ADMIN_EMAIL")
    admin_existente = Usuario.query.filter_by(id_permissao=Cargo.ADMIN.value).first()

    if not admin_existente:
        id_admin = criar_usuario(
            cpf="00000000000",
            nome="Admin",
            email=environ.get("ADMIN_EMAIL"),
            senha=environ.get("ADMIN_PASSWORD"),
            id_permissao=Cargo.ADMIN._value_
        )
        #print(f"Admin inicial criado com sucesso! (ID: {id_admin})")
    #else:
    #    print("Admin inicial já existe.")

    #admin = criar_usuario(
    #cpf="00000000000",
    #nome="Admin",
    #email="emailexemplo@gmail.com",
    #senha="senha-super-segura123",
    #id_permissao=Cargo.ADMIN
    #)        

#CRIAÇÃO DE CARGOS
def criar_cargos():
    admin_existente = Usuario.query.filter_by(id_permissao=Cargo.ADMIN.value).first()


# CRIAÇÃO DE SERVICOS
def adicionar_servico():
    criar_servico("Chef_em_casa", "Prepara a refeicao em pequenas comemoracoes e em ambiente domiciliar")
    criar_servico("Buffet", "Preparo o ambiente para grandes comemorações que envolvam pratos quentes")
    criar_servico("Bar", "Prepara bebidas escolhidas pelo cliente no balcao ")
    criar_servico("Mesa_de_salgados", "Prepara o ambiente dispor os salgados da melhor maneira para festas ")

# CRIAÇÃO DE BANCADAS 
def adicionar_bancada():
    criar_bancada("Rechauds", "Equipamento que mantem o alimento quente")
    criar_bancada("Kit_loucas", "Kit que contem o basico de mesa posta: Talheres, pratos e guardanapo de pano")
    criar_bancada("Chapa_hamburguer_portatil", "Equipamento utilizado para confeccao de lanches")
    criar_bancada("Bancada_bar_portatil", "Equipamento que organiza e prepara as bebidas")
    criar_bancada("Maquina_de_gelo", "Equipamento responsavel por fazer gelo")
    criar_bancada("Limpeza", "Equipamentos responsaveis pela limpeza final no evento")

# CRIAÇÃO DE CARDAPIO
def adicionar_cardapio():
    criar_cardapio("Feijoada_completa", " ", )
    criar_cardapio("Bobo_de_camarao ", " ", )
    criar_cardapio("File_de_tilapia_ao_molho_manteiga_e_alcaparras ", " ", )
    criar_cardapio("Strogonoff_de_file_Mignon ", " ", )
    criar_cardapio("Nhoque_ao_molho", " ", )
    criar_cardapio("Risoto_de_cogumelos_com_tiras_de_file_mignon", " ", )
    criar_cardapio("Escondinho_de_carne_seca_com_mandioca ", " ", )
    criar_cardapio("Raviolli_de_queijo_ao_molho_bolonhesa ", " ", )

    criar_cardapio("Salgados_completo ", " ", )
    criar_cardapio("Salgados_Reduzido", " ", )
    criar_cardapio("Hamburguer_tradicional ", " ", )
    criar_cardapio("Hamburguer_smash ", " ", )
    criar_cardapio("Hamburguer_mega_bacon ", " ", )
    criar_cardapio("Mexicano ", " ", )
    criar_cardapio("Boteco_brasileiro", " ", )

    criar_cardapio("Bebida_sem_alcool", " ", )
    criar_cardapio("Bebida_com_alcool", " ", )
    criar_cardapio("Bebida_mista", " ", )

# CRIAÇÃO DE PRATOS
def adicionar_prato():
    #nome: str, descricao: str, tipo_prato: str, tempo_preparo: int, requer_pre_preparo: bool = False
    criar_prato("Mandioca_frita", "Pedacos de mandioca frita em oleo", "Entrada", 40, True) #requer-preparo, pois tem que levar ela cozida e fritar no local
    criar_prato("Tabua_de_frios", "Tabua contendo aperitivos: Salame, queijo, azeitona", "Entrada", 15, False)
    criar_prato("Feijoada_completa", "Feijoada", "Prato principal", 120, True)
    criar_prato("Arroz_branco", "Arroz cozido", "Acompanhamento", 20, False)
    criar_prato("Couve_refogada", "Couve picada refogada", "Acompanhamento", 10, False) # A colve comprada é picada ja
    criar_prato("Farofa", "Farofa comprada", "Acompanhamento", 0, False)
    criar_prato("Vinagrete", "Vinagrete completo: Ceblo, tomate, pimentao,cebolinha,vinagre", "Acompanhamento", 15, True) #Levar cortado as coisas, e temperar no local
    criar_prato("Molho_de_pimenta", "Molho de pimenta pronto", "Acompanhamento", 0, False)
    criar_prato("Sorvete", "Sorvete comprado de maracuja e limao", "Sobremesa", 0, False)
    criar_prato("Salada_fresca", "Salada de folhas hidroponicas e tomate cereja", "Entrada", 5, True) #Lavar antes
    criar_prato("Bobo_de_camarao", "Bobo de camarao completo", "Prato principal", 120, True)
    criar_prato("Salada_de_fruta_fresca_com_creme", "Salada de frutas com creme de leite e leite condensado", "Sobremesa", 0, False)
    criar_prato("Bruschetta", "Bruscretta de pao italiano, tomate e manjericao", "Entrada", 5, False)
    criar_prato("File_de_tilapia", "File de tilapia grelhado", "Prato principal", 30, True) #Limpar o file de tilapia
    criar_prato("Molho_de_mateiga_com_alcaparras", "Molho de acompanhamento de manteiga e alcaparras", "Acomapanhamento", 10, False)
    criar_prato("Iorgute_Natural_com_morangos_e_mel", "Iorgute com pedacos de fruta e adocado com mel", "Sobremesa", 5, False)
    criar_prato("Salada_ceaser", "Salada de alface, croutons e molho caesar", "Entrada", 20, False)
    criar_prato("Stogonoff_de_file_mignon", "Strogonoff cremoso de filé mignon", "Prato principal", 120, True)
    criar_prato("Batata_palha", "Batata palha crocante pronta", "Acompanhamento", 0, False)
    criar_prato("Pudim_de_leite_condensado", "Pudim de leite tradicional com calda de caramelo", "Sobremesa", 120, True)
    criar_prato("Nhoque_ao_molho", "Nhoque de batata ao molho de tomate", "Prato principal", 120, True)
    criar_prato("Mousse_de_maracuja", "Mousse leve e aerada de maracujá", "Sobremesa", 40, True)
    criar_prato("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Risoto cremoso de cogumelos acompanhado de filé mignon", "Prato principal", 60, True)
    criar_prato("Brownie_de_chocolate", "Brownie caseiro de chocolate denso", "Sobremesa", 60, True)
    criar_prato("Dadinho_de_tapioca", "Dadinhos de tapioca com queijo coalho fritos", "Entrada", 40, True)
    criar_prato("Escondidinho_de_carne_seca_com_mandioca", "Escondidinho de carne seca com purê de mandioca", "Prato principal", 180, True)
    criar_prato("Geleia_de_pimenta", "Geia doce e levemente picante de pimenta", "Acompanhamento", 0, False)
    criar_prato("Cheesecake_de_frutas_vermelhas", "Cheesecake assado com calda de frutas vermelhas", "Sobremesa", 60, True)
    criar_prato("Ravioli_de_queijo_ao_molho_bolanhesa", "Ravioli recheado com queijo ao molho bolonhesa", "Prato principal", 120, True)
    criar_prato("Parmesao_ralado", "Queijo parmesão ralado fino", "Acompanhamento", 0, False)
    criar_prato("Mousse_de_chocolate", "Mousse cremosa de chocolate meio amargo", "Sobremesa", 40, True)
    criar_prato("Coxinha", "Salgado frito recheado com frango desfiado", "Prato principal", 6, False)
    criar_prato("Risole", "Salgado frito em formato de meia-lua recheado", "Prato principal", 6, False)
    criar_prato("Quibe", "Salgado de carne moída com trigo para quibe", "Prato principal", 6, False)
    criar_prato("Bolinha_de_queijo", "Salgadinho frito recheado com queijo", "Prato principal", 6, False)
    criar_prato("Empada", "Empada de massa podre recheada", "Prato principal", 15, False)
    criar_prato("Croquete", "Croquete frito de carne temperada", "Prato principal", 10, False)
    criar_prato("Batata_frita", "Porção de batata frita crocante", "Prato principal", 15, False)
    criar_prato("Queijo", "Fatias ou cubos de queijo variados", "Prato principal", 0, False)
    criar_prato("Embutido", "Porção de embutidos fatiados", "Prato principal", 0, False)
    criar_prato("Pao", "Cesta de pães frescos fatiados", "Prato principal", 0, False)
    criar_prato("Brigadeiro", "Docinho tradicional de chocolate com granulado", "Prato principal", 30, True)
    criar_prato("Beijinho", "Docinho tradicional de coco com cravo", "Prato principal", 30, True)
    criar_prato("Bolo", "Bolo caseiro fofinho", "Prato principal", 240, True)
    criar_prato("Hamburguer_tradicional", "Hambúrguer artesanal de carne bovina", "Prato principal", 25, False)
    criar_prato("Hamburguer_smash", "Hambúrguer prensado na chapa crocante", "Prato principal", 25, False)
    criar_prato("Hamburguer_mega_bacon", "Hambúrguer de carne com extra de bacon crocante", "Prato principal", 25, False)
    criar_prato("Tortilha_mexicana", "Tortilha recheada estilo mexicana", "Prato principal", 30, False)
    criar_prato("Pastel_de_carne", "Pastel frito recheado com carne moída temperada", "Prato principal", 6, False)
    criar_prato("Bolinho_de_bacalhau", "Bolinho tradicional de bacalhau e batata", "Prato principal", 6, False)
    criar_prato("Liguica_acebolada", "Porção de linguiça frita com cebola", "Prato principal", 10, False)
    criar_prato("Pastel_de_queijo", "Pastel frito recheado com queijo derretido", "Prato principal", 6, False)
  
    
#CRIAÇÃO DE ingredientes
def adicionar_ingrediente():    
# Carnes, aves, peixes e embutidos
    criar_ingrediente("Pe_de_porco", "kg", 10.0, 3.0)
    criar_ingrediente("Rabo_de_porco", "kg", 5.0, 1.5)
    criar_ingrediente("Costelinha_suina_defumada", "kg", 8.0, 2.0)
    criar_ingrediente("Bacon", "kg", 5.0, 1.0)
    criar_ingrediente("Linguica_calabresa", "kg", 8.0, 2.0)
    criar_ingrediente("Linguica_acebolada", "kg", 5.0, 1.0)
    criar_ingrediente("Lombo_de_porco", "kg", 8.0, 2.0)
    criar_ingrediente("Carne_seca", "kg", 8.0, 2.0)
    criar_ingrediente("Camarao_medio_limpo", "kg", 5.0, 1.0)
    criar_ingrediente("File_de_tilapia", "kg", 8.0, 2.0)
    criar_ingrediente("File_mignon_bovino", "kg", 8.0, 2.0)
    criar_ingrediente("Carne_moida_de_primeira", "kg", 10.0, 3.0)
    criar_ingrediente("Carne_moida_blend_patinho_acem", "kg", 8.0, 2.0)
    criar_ingrediente("Frango_grelhado", "kg", 8.0, 2.0)
    criar_ingrediente("Frango_desfiado", "kg", 5.0, 1.0)
    criar_ingrediente("Presunto", "kg", 3.0, 0.5)
    criar_ingrediente("Bolinho_de_bacalhau", "kg", 5.0, 1.0)

    # Cereais, massas e carboidratos
    criar_ingrediente("Feijao_preto", "kg", 15.0, 4.0)
    criar_ingrediente("Arroz_branco", "kg", 20.0, 5.0)
    criar_ingrediente("Arroz_arborio", "kg", 8.0, 2.0)
    criar_ingrediente("Mandioca_in_natura", "kg", 10.0, 3.0)
    criar_ingrediente("Farinha_de_mandioca", "kg", 8.0, 2.0)
    criar_ingrediente("Batata", "kg", 20.0, 5.0)
    criar_ingrediente("Batata_palha", "kg", 5.0, 1.0)
    criar_ingrediente("Nhoque_de_batata_pronto", "kg", 5.0, 1.0)
    criar_ingrediente("Ravioli_fresco_de_queijo", "kg", 5.0, 1.0)
    criar_ingrediente("Pao_italiano", "unidade", 20.0, 5.0)
    criar_ingrediente("Pao_brioche", "unidade", 30.0, 8.0)
    criar_ingrediente("Pao_de_forma", "pacote", 10.0, 2.0)
    criar_ingrediente("Mini_paes", "unidade", 100.0, 25.0)
    criar_ingrediente("Tortilla_de_milho", "unidade", 50.0, 10.0)
    criar_ingrediente("Tortilla_de_trigo", "unidade", 50.0, 10.0)
    criar_ingrediente("Tapioca_granulada", "kg", 5.0, 1.0)
    criar_ingrediente("Nachos", "kg", 5.0, 1.0)
    criar_ingrediente("Biscoito_base", "pacote", 15.0, 3.0)
    criar_ingrediente("Coxinha", "unidade", 100.0, 25.0)
    criar_ingrediente("Risole", "unidade", 100.0, 25.0)
    criar_ingrediente("Quibe", "unidade", 100.0, 25.0)
    criar_ingrediente("Croquete", "unidade", 100.0, 25.0)
    criar_ingrediente("Empada", "unidade", 100.0, 25.0)
    criar_ingrediente("Bolinha_de_queijo", "unidade", 100.0, 25.0)
    criar_ingrediente("Pastel_de_carne", "unidade", 100.0, 25.0)

    # Laticínios e ovos
    criar_ingrediente("Manteiga", "kg", 5.0, 1.0)
    criar_ingrediente("Queijo_mucarela", "kg", 8.0, 2.0)
    criar_ingrediente("Queijo_prato", "kg", 5.0, 1.0)
    criar_ingrediente("Queijo_cheddar", "kg", 4.0, 1.0)
    criar_ingrediente("Queijo_coalho", "kg", 5.0, 1.0)
    criar_ingrediente("Queijo_ralado", "kg", 2.0, 0.5)
    criar_ingrediente("Parmesao_ralado", "kg", 3.0, 0.5)
    criar_ingrediente("Creme_de_leite", "L", 8.0, 2.0)
    criar_ingrediente("Leite_condensado", "L", 8.0, 2.0)
    criar_ingrediente("Leite_integral", "L", 15.0, 4.0)
    criar_ingrediente("Leite_de_coco", "L", 5.0, 1.0)
    criar_ingrediente("Iogurte_natural", "L", 5.0, 1.0)
    criar_ingrediente("Cream_cheese", "kg", 4.0, 1.0)
    criar_ingrediente("Ovos", "unidade", 180.0, 36.0)

    # Vegetais, ervas e frutas
    criar_ingrediente("Folhas_hidroponicas", "kg", 3.0, 0.8)
    criar_ingrediente("Folhas_variadas", "kg", 3.0, 0.8)
    criar_ingrediente("Alface_romana", "unidade", 20.0, 5.0)
    criar_ingrediente("Alface_americana", "unidade", 20.0, 5.0)
    criar_ingrediente("Couve_manteiga", "kg", 3.0, 0.8)
    criar_ingrediente("Tomate", "kg", 10.0, 2.0)
    criar_ingrediente("Tomate_cereja", "kg", 4.0, 1.0)
    criar_ingrediente("Cebola", "kg", 10.0, 2.0)
    criar_ingrediente("Cebola_caramelizada", "kg", 3.0, 0.5)
    criar_ingrediente("Pimentao", "kg", 4.0, 1.0)
    criar_ingrediente("Cebolinha", "kg", 1.0, 0.2)
    criar_ingrediente("Alho", "kg", 3.0, 0.5)
    criar_ingrediente("Manjericao", "kg", 0.5, 0.1)
    criar_ingrediente("Salsinha", "kg", 1.0, 0.2)
    criar_ingrediente("Limao", "kg", 8.0, 2.0)
    criar_ingrediente("Laranja", "kg", 8.0, 2.0)
    criar_ingrediente("Cogumelos_frescos", "kg", 3.0, 0.5)
    criar_ingrediente("Champignon", "kg", 3.0, 0.5)
    criar_ingrediente("Morango_fresco", "kg", 5.0, 1.0)
    criar_ingrediente("Frutas_frescas_in_natura", "kg", 10.0, 2.0)
    criar_ingrediente("Frutas_vermelhas_congeladas", "kg", 4.0, 1.0)
    criar_ingrediente("Nozes", "kg", 2.0, 0.5)

    # Molhos, condimentos e temperos
    criar_ingrediente("Oleo_de_soja", "L", 10.0, 2.0)
    criar_ingrediente("Oleo_para_fritura", "L", 20.0, 5.0)
    criar_ingrediente("Sal", "kg", 8.0, 2.0)
    criar_ingrediente("Temperos", "kg", 3.0, 0.5)
    criar_ingrediente("Vinagre", "L", 5.0, 1.0)
    criar_ingrediente("Azeite", "L", 5.0, 1.0)
    criar_ingrediente("Azeite_de_dende", "L", 3.0, 0.5)
    criar_ingrediente("Molho_de_pimenta", "L", 2.0, 0.5)
    criar_ingrediente("Geleia_de_pimenta", "kg", 3.0, 0.5)
    criar_ingrediente("Alcaparras", "kg", 1.0, 0.2)
    criar_ingrediente("Molho_de_tomate", "L", 8.0, 2.0)
    criar_ingrediente("Catchup", "L", 5.0, 1.0)
    criar_ingrediente("Mostarda", "L", 3.0, 0.5)
    criar_ingrediente("Molho_mostarda_e_mel", "L", 3.0, 0.5)
    criar_ingrediente("Molho_Caesar", "L", 3.0, 0.5)
    criar_ingrediente("Croutons", "kg", 2.0, 0.5)
    criar_ingrediente("Maionese_temperada", "L", 5.0, 1.0)
    criar_ingrediente("Molho_barbecue", "L", 3.0, 0.5)
    criar_ingrediente("Vinho_branco", "L", 5.0, 1.0)
    criar_ingrediente("Guacamole", "kg", 3.0, 0.5)
    criar_ingrediente("Gelatina", "kg", 3.0, 0.5)
    criar_ingrediente("Chocolate_meio_amargo", "kg", 5.0, 1.0)
    criar_ingrediente("Mel", "kg", 3.0, 0.5)
    criar_ingrediente("Azeitona", "kg", 3.0, 0.5)

    # Bebidas sem álcool e xaropes
    criar_ingrediente("Suco_de_limao", "L", 5.0, 1.0)
    criar_ingrediente("Xarope_de_groselha_framboesa", "L", 3.0, 0.5)
    criar_ingrediente("Agua_com_gas", "L", 20.0, 5.0)
    criar_ingrediente("Xarope_simples_de_acucar", "L", 3.0, 0.5)
    criar_ingrediente("Suco_de_abacaxi", "L", 8.0, 2.0)
    criar_ingrediente("Xarope_de_maca_verde", "L", 2.0, 0.5)
    criar_ingrediente("Polpa_de_frutas_vermelhas", "kg", 5.0, 1.0)
    criar_ingrediente("Suco_de_laranja", "L", 10.0, 2.0)
    criar_ingrediente("Refrigerante_de_guarana", "L", 20.0, 5.0)
    criar_ingrediente("Cha_preto", "kg", 1.0, 0.2)
    criar_ingrediente("Xarope_de_pessego", "L", 2.0, 0.5)
    criar_ingrediente("Xarope_de_grenadine", "L", 2.0, 0.5)
    criar_ingrediente("Agua_de_coco", "L", 8.0, 2.0)
    criar_ingrediente("Suco_de_maracuja", "L", 8.0, 2.0)
    criar_ingrediente("Xarope_de baunilha", "L", 2.0, 0.5)
    criar_ingrediente("Suco_de_melancia", "L", 5.0, 1.0)
    criar_ingrediente("Suco_de_gengibre", "L", 2.0, 0.5)

    # Bebidas alcoólicas
    criar_ingrediente("Cachaca", "L", 5.0, 1.0)
    criar_ingrediente("Tequila", "L", 3.0, 0.5)
    criar_ingrediente("Cointreau_triple_sec", "L", 2.0, 0.5)
    criar_ingrediente("Gin", "L", 5.0, 1.0)
    criar_ingrediente("Campari", "L", 3.0, 0.5)
    criar_ingrediente("Vermute_tinto", "L", 3.0, 0.5)
    criar_ingrediente("Vodka", "L", 5.0, 1.0)
    criar_ingrediente("Ginger_beer", "L", 8.0, 2.0)
    criar_ingrediente("Suco_de_cranberry", "L", 5.0, 1.0)
    criar_ingrediente("Rum_branco", "L", 3.0, 0.5)
    criar_ingrediente("Rum_escuro", "L", 3.0, 0.5)
    criar_ingrediente("Xarope_de_amendoa_orgeat", "L", 2.0, 0.5)
    criar_ingrediente("Uisque_bourbon", "L", 3.0, 0.5)
    criar_ingrediente("Angostura_bitters", "ml", 500.0, 100.0)
    criar_ingrediente("Uisque_de_centeio_rye", "L", 3.0, 0.5)
    criar_ingrediente("Cereja_marasquino", "kg", 2.0, 0.5)

    # Diversos e acompanhamentos
    criar_ingrediente("Onion_rings", "kg", 5.0, 1.0)
    criar_ingrediente("Brigadeiro", "unidade", 100.0, 25.0)
    criar_ingrediente("Beijinho", "unidade", 100.0, 25.0)
    criar_ingrediente("Bolo_comum_simples", "kg", 5.0, 1.0)

#FALTA ARRUMAR OS IDS BEBIDA 
def adicionar_lote():
    
    # Carnes e proteínas
    criar_lote("LOTE-ING-001", "Pamplona", datetime(2026, 10, 12), 5.0, id_ingrediente=1, id_bebida=None, data_validade=datetime(2028, 1, 1))
    criar_lote("LOTE-ING-002", "Pamplona", datetime(2026, 10, 12), 3.0, id_ingrediente=2, id_bebida=None, data_validade=datetime(2028, 1, 2))
    criar_lote("LOTE-ING-003", "Seara", datetime(2026, 10, 12), 4.0, id_ingrediente=3, id_bebida=None, data_validade=datetime(2028, 1, 3))
    criar_lote("LOTE-ING-004", "Sadia", datetime(2026, 10, 12), 2.0, id_ingrediente=4, id_bebida=None, data_validade=datetime(2028, 1, 4))
    criar_lote("LOTE-ING-005", "Perdigão", datetime(2026, 10, 12), 3.0, id_ingrediente=5, id_bebida=None, data_validade=datetime(2028, 1, 5))
    criar_lote("LOTE-ING-006", "Aurora", datetime(2026, 10, 12), 2.0, id_ingrediente=6, id_bebida=None, data_validade=datetime(2028, 1, 6))
    criar_lote("LOTE-ING-007", "Sadia", datetime(2026, 10, 12), 3.0, id_ingrediente=7, id_bebida=None, data_validade=datetime(2028, 1, 7))
    criar_lote("LOTE-ING-008", "Friboi", datetime(2026, 10, 12), 4.0, id_ingrediente=8, id_bebida=None, data_validade=datetime(2028, 1, 8))
    criar_lote("LOTE-ING-009", "Copacol", datetime(2026, 10, 12), 2.0, id_ingrediente=9, id_bebida=None, data_validade=datetime(2028, 1, 9))
    criar_lote("LOTE-ING-010", "Copacol", datetime(2026, 10, 12), 3.0, id_ingrediente=10, id_bebida=None, data_validade=datetime(2028, 1, 10))
    criar_lote("LOTE-ING-011", "Friboi", datetime(2026, 10, 12), 2.0, id_ingrediente=11, id_bebida=None, data_validade=datetime(2028, 1, 11))
    criar_lote("LOTE-ING-012", "Friboi", datetime(2026, 10, 12), 3.0, id_ingrediente=12, id_bebida=None, data_validade=datetime(2028, 1, 12))
    criar_lote("LOTE-ING-013", "Swift", datetime(2026, 10, 12), 3.0, id_ingrediente=13, id_bebida=None, data_validade=datetime(2028, 1, 13))
    criar_lote("LOTE-ING-014", "Sadia", datetime(2026, 10, 12), 4.0, id_ingrediente=14, id_bebida=None, data_validade=datetime(2028, 1, 14))
    criar_lote("LOTE-ING-015", "Seara", datetime(2026, 10, 12), 3.0, id_ingrediente=15, id_bebida=None, data_validade=datetime(2028, 1, 15))
    criar_lote("LOTE-ING-016", "Sadia", datetime(2026, 10, 12), 2.0, id_ingrediente=16, id_bebida=None, data_validade=datetime(2028, 1, 16))
    criar_lote("LOTE-ING-017", "Copacol", datetime(2026, 10, 12), 2.0, id_ingrediente=17, id_bebida=None, data_validade=datetime(2028, 1, 17))

    # Grãos, massas, pães e salgados
    criar_lote("LOTE-ING-018", "Camil", datetime(2026, 10, 12), 5.0, id_ingrediente=18, id_bebida=None, data_validade=datetime(2028, 1, 18))
    criar_lote("LOTE-ING-019", "Camil", datetime(2026, 10, 12), 10.0, id_ingrediente=19, id_bebida=None, data_validade=datetime(2028, 1, 19))
    criar_lote("LOTE-ING-020", "Tio João", datetime(2026, 10, 12), 5.0, id_ingrediente=20, id_bebida=None, data_validade=datetime(2028, 1, 20))
    criar_lote("LOTE-ING-021", "De Marchi", datetime(2026, 10, 12), 5.0, id_ingrediente=21, id_bebida=None, data_validade=datetime(2028, 1, 21))
    criar_lote("LOTE-ING-022", "Yoki", datetime(2026, 10, 12), 3.0, id_ingrediente=22, id_bebida=None, data_validade=datetime(2028, 1, 22))
    criar_lote("LOTE-ING-023", "Bem Brasil", datetime(2026, 10, 12), 5.0, id_ingrediente=23, id_bebida=None, data_validade=datetime(2028, 1, 23))
    criar_lote("LOTE-ING-024", "Yoki", datetime(2026, 10, 12), 2.0, id_ingrediente=24, id_bebida=None, data_validade=datetime(2028, 1, 24))
    criar_lote("LOTE-ING-025", "Nico", datetime(2026, 10, 12), 3.0, id_ingrediente=25, id_bebida=None, data_validade=datetime(2028, 1, 25))
    criar_lote("LOTE-ING-026", "Massa Leve", datetime(2026, 10, 12), 3.0, id_ingrediente=26, id_bebida=None, data_validade=datetime(2028, 1, 26))
    criar_lote("LOTE-ING-027", "Wickbold", datetime(2026, 10, 12), 4.0, id_ingrediente=27, id_bebida=None, data_validade=datetime(2028, 1, 27))
    criar_lote("LOTE-ING-028", "Pullman", datetime(2026, 10, 12), 3.0, id_ingrediente=28, id_bebida=None, data_validade=datetime(2028, 1, 28))
    criar_lote("LOTE-ING-029", "Wickbold", datetime(2026, 10, 12), 3.0, id_ingrediente=29, id_bebida=None, data_validade=datetime(2028, 1, 29))
    criar_lote("LOTE-ING-030", "Seven Boys", datetime(2026, 10, 12), 2.0, id_ingrediente=30, id_bebida=None, data_validade=datetime(2028, 1, 30))
    criar_lote("LOTE-ING-031", "Rap10", datetime(2026, 10, 12), 3.0, id_ingrediente=31, id_bebida=None, data_validade=datetime(2028, 1, 31))
    criar_lote("LOTE-ING-032", "Rap10", datetime(2026, 10, 12), 3.0, id_ingrediente=32, id_bebida=None, data_validade=datetime(2028, 2, 1))
    criar_lote("LOTE-ING-033", "Yoki", datetime(2026, 10, 12), 2.0, id_ingrediente=33, id_bebida=None, data_validade=datetime(2028, 2, 2))
    criar_lote("LOTE-ING-034", "Doritos", datetime(2026, 10, 12), 2.0, id_ingrediente=34, id_bebida=None, data_validade=datetime(2028, 2, 3))
    criar_lote("LOTE-ING-035", "Marilan", datetime(2026, 10, 12), 2.0, id_ingrediente=35, id_bebida=None, data_validade=datetime(2028, 2, 4))
    criar_lote("LOTE-ING-036", "Seara", datetime(2026, 10, 12), 3.0, id_ingrediente=36, id_bebida=None, data_validade=datetime(2028, 2, 5))
    criar_lote("LOTE-ING-037", "Seara", datetime(2026, 10, 12), 3.0, id_ingrediente=37, id_bebida=None, data_validade=datetime(2028, 2, 6))
    criar_lote("LOTE-ING-038", "Seara", datetime(2026, 10, 12), 3.0, id_ingrediente=38, id_bebida=None, data_validade=datetime(2028, 2, 7))
    criar_lote("LOTE-ING-039", "Seara", datetime(2026, 10, 12), 3.0, id_ingrediente=39, id_bebida=None, data_validade=datetime(2028, 2, 8))
    criar_lote("LOTE-ING-040", "Forno de Minas", datetime(2026, 10, 12), 2.0, id_ingrediente=40, id_bebida=None, data_validade=datetime(2028, 2, 9))
    criar_lote("LOTE-ING-041", "Seara", datetime(2026, 10, 12), 3.0, id_ingrediente=41, id_bebida=None, data_validade=datetime(2028, 2, 10))
    criar_lote("LOTE-ING-042", "Aurora", datetime(2026, 10, 12), 3.0, id_ingrediente=42, id_bebida=None, data_validade=datetime(2028, 2, 11))

    # Laticínios e ovos
    criar_lote("LOTE-ING-043", "Qualy", datetime(2026, 10, 12), 2.0, id_ingrediente=43, id_bebida=None, data_validade=datetime(2028, 2, 12))
    criar_lote("LOTE-ING-044", "Tirolez", datetime(2026, 10, 12), 3.0, id_ingrediente=44, id_bebida=None, data_validade=datetime(2028, 2, 13))
    criar_lote("LOTE-ING-045", "President", datetime(2026, 10, 12), 2.0, id_ingrediente=45, id_bebida=None, data_validade=datetime(2028, 2, 14))
    criar_lote("LOTE-ING-046", "Polenghi", datetime(2026, 10, 12), 2.0, id_ingrediente=46, id_bebida=None, data_validade=datetime(2028, 2, 15))
    criar_lote("LOTE-ING-047", "Tirolez", datetime(2026, 10, 12), 2.0, id_ingrediente=47, id_bebida=None, data_validade=datetime(2028, 2, 16))
    criar_lote("LOTE-ING-048", "Vigor", datetime(2026, 10, 12), 1.0, id_ingrediente=48, id_bebida=None, data_validade=datetime(2028, 2, 17))
    criar_lote("LOTE-ING-049", "Faixa Azul", datetime(2026, 10, 12), 1.0, id_ingrediente=49, id_bebida=None, data_validade=datetime(2028, 2, 18))
    criar_lote("LOTE-ING-050", "Nestlé", datetime(2026, 10, 12), 3.0, id_ingrediente=50, id_bebida=None, data_validade=datetime(2028, 2, 19))
    criar_lote("LOTE-ING-051", "Moça", datetime(2026, 10, 12), 3.0, id_ingrediente=51, id_bebida=None, data_validade=datetime(2028, 2, 20))
    criar_lote("LOTE-ING-052", "Italac", datetime(2026, 10, 12), 5.0, id_ingrediente=52, id_bebida=None, data_validade=datetime(2028, 2, 21))
    criar_lote("LOTE-ING-053", "Sococo", datetime(2026, 10, 12), 3.0, id_ingrediente=53, id_bebida=None, data_validade=datetime(2028, 2, 22))
    criar_lote("LOTE-ING-054", "Nestlé", datetime(2026, 10, 12), 2.0, id_ingrediente=54, id_bebida=None, data_validade=datetime(2028, 2, 23))
    criar_lote("LOTE-ING-055", "Philadelphia", datetime(2026, 10, 12), 2.0, id_ingrediente=55, id_bebida=None, data_validade=datetime(2028, 2, 24))
    criar_lote("LOTE-ING-056", "Mantiqueira", datetime(2026, 10, 12), 5.0, id_ingrediente=56, id_bebida=None, data_validade=datetime(2028, 2, 25))

    # Verduras, legumes, frutas e cogumelos
    criar_lote("LOTE-ING-057", "Fazenda local", datetime(2026, 10, 12), 2.0, id_ingrediente=57, id_bebida=None, data_validade=datetime(2028, 2, 26))
    criar_lote("LOTE-ING-058", "Fazenda local", datetime(2026, 10, 12), 3.0, id_ingrediente=58, id_bebida=None, data_validade=datetime(2028, 2, 27))
    criar_lote("LOTE-ING-059", "Hortifruti", datetime(2026, 10, 12), 2.0, id_ingrediente=59, id_bebida=None, data_validade=datetime(2028, 2, 28))
    criar_lote("LOTE-ING-060", "Hortifruti", datetime(2026, 10, 12), 2.0, id_ingrediente=60, id_bebida=None, data_validade=datetime(2028, 2, 29))
    criar_lote("LOTE-ING-061", "Hortifruti", datetime(2026, 10, 12), 2.0, id_ingrediente=61, id_bebida=None, data_validade=datetime(2028, 3, 1))
    criar_lote("LOTE-ING-062", "Hortifruti", datetime(2026, 10, 12), 4.0, id_ingrediente=62, id_bebida=None, data_validade=datetime(2028, 3, 2))
    criar_lote("LOTE-ING-063", "Hortifruti", datetime(2026, 10, 12), 2.0, id_ingrediente=63, id_bebida=None, data_validade=datetime(2028, 3, 3))
    criar_lote("LOTE-ING-064", "Hortifruti", datetime(2026, 10, 12), 3.0, id_ingrediente=64, id_bebida=None, data_validade=datetime(2028, 3, 4))
    criar_lote("LOTE-ING-065", "Predilecta", datetime(2026, 10, 12), 2.0, id_ingrediente=65, id_bebida=None, data_validade=datetime(2028, 3, 5))
    criar_lote("LOTE-ING-066", "Hortifruti", datetime(2026, 10, 12), 2.0, id_ingrediente=66, id_bebida=None, data_validade=datetime(2028, 3, 6))
    criar_lote("LOTE-ING-067", "Hortifruti", datetime(2026, 10, 12), 1.0, id_ingrediente=67, id_bebida=None, data_validade=datetime(2028, 3, 7))
    criar_lote("LOTE-ING-068", "Hortifruti", datetime(2026, 10, 12), 1.0, id_ingrediente=68, id_bebida=None, data_validade=datetime(2028, 3, 8))
    criar_lote("LOTE-ING-069", "Hortifruti", datetime(2026, 10, 12), 1.0, id_ingrediente=69, id_bebida=None, data_validade=datetime(2028, 3, 9))
    criar_lote("LOTE-ING-070", "Hortifruti", datetime(2026, 10, 12), 1.0, id_ingrediente=70, id_bebida=None, data_validade=datetime(2028, 3, 10))
    criar_lote("LOTE-ING-071", "Hortifruti", datetime(2026, 10, 12), 2.0, id_ingrediente=71, id_bebida=None, data_validade=datetime(2028, 3, 11))
    criar_lote("LOTE-ING-072", "Hortifruti", datetime(2026, 10, 12), 3.0, id_ingrediente=72, id_bebida=None, data_validade=datetime(2028, 3, 12))
    criar_lote("LOTE-ING-073", "Fazenda local", datetime(2026, 10, 12), 2.0, id_ingrediente=73, id_bebida=None, data_validade=datetime(2028, 3, 13))
    criar_lote("LOTE-ING-074", "Raiola", datetime(2026, 10, 12), 2.0, id_ingrediente=74, id_bebida=None, data_validade=datetime(2028, 3, 14))
    criar_lote("LOTE-ING-075", "Hortifruti", datetime(2026, 10, 12), 2.0, id_ingrediente=75, id_bebida=None, data_validade=datetime(2028, 3, 15))
    criar_lote("LOTE-ING-076", "Hortifruti", datetime(2026, 10, 12), 4.0, id_ingrediente=76, id_bebida=None, data_validade=datetime(2028, 3, 16))
    criar_lote("LOTE-ING-077", "De Marchi", datetime(2026, 10, 12), 2.0, id_ingrediente=77, id_bebida=None, data_validade=datetime(2028, 3, 17))
    criar_lote("LOTE-ING-078", "Agtal", datetime(2026, 10, 12), 1.0, id_ingrediente=78, id_bebida=None, data_validade=datetime(2028, 3, 18))

    # Óleos, temperos, molhos e outros produtos
    criar_lote("LOTE-ING-079", "Liza", datetime(2026, 10, 12), 5.0, id_ingrediente=79, id_bebida=None, data_validade=datetime(2028, 3, 19))
    criar_lote("LOTE-ING-080", "Soya", datetime(2026, 10, 12), 10.0, id_ingrediente=80, id_bebida=None, data_validade=datetime(2028, 3, 20))
    criar_lote("LOTE-ING-081", "Cisne", datetime(2026, 10, 12), 2.0, id_ingrediente=81, id_bebida=None, data_validade=datetime(2028, 3, 21))
    criar_lote("LOTE-ING-082", "Kitano", datetime(2026, 10, 12), 1.0, id_ingrediente=82, id_bebida=None, data_validade=datetime(2028, 3, 22))
    criar_lote("LOTE-ING-083", "Castelo", datetime(2026, 10, 12), 2.0, id_ingrediente=83, id_bebida=None, data_validade=datetime(2028, 3, 23))
    criar_lote("LOTE-ING-084", "Gallo", datetime(2026, 10, 12), 3.0, id_ingrediente=84, id_bebida=None, data_validade=datetime(2028, 3, 24))
    criar_lote("LOTE-ING-085", "Cepêra", datetime(2026, 10, 12), 2.0, id_ingrediente=85, id_bebida=None, data_validade=datetime(2028, 3, 25))
    criar_lote("LOTE-ING-086", "Tabasco", datetime(2026, 10, 12), 1.0, id_ingrediente=86, id_bebida=None, data_validade=datetime(2028, 3, 26))
    criar_lote("LOTE-ING-087", "Queensberry", datetime(2026, 10, 12), 2.0, id_ingrediente=87, id_bebida=None, data_validade=datetime(2028, 3, 27))
    criar_lote("LOTE-ING-088", "La Pastina", datetime(2026, 10, 12), 1.0, id_ingrediente=88, id_bebida=None, data_validade=datetime(2028, 3, 28))
    criar_lote("LOTE-ING-089", "Pomarola", datetime(2026, 10, 12), 4.0, id_ingrediente=89, id_bebida=None, data_validade=datetime(2028, 3, 29))
    criar_lote("LOTE-ING-090", "Heinz", datetime(2026, 10, 12), 2.0, id_ingrediente=90, id_bebida=None, data_validade=datetime(2028, 3, 30))
    criar_lote("LOTE-ING-091", "Hemmer", datetime(2026, 10, 12), 2.0, id_ingrediente=91, id_bebida=None, data_validade=datetime(2028, 3, 31))
    criar_lote("LOTE-ING-092", "Hellmann's", datetime(2026, 10, 12), 2.0, id_ingrediente=92, id_bebida=None, data_validade=datetime(2028, 4, 1))
    criar_lote("LOTE-ING-093", "Hellmann's", datetime(2026, 10, 12), 2.0, id_ingrediente=93, id_bebida=None, data_validade=datetime(2028, 4, 2))
    criar_lote("LOTE-ING-094", "Marilan", datetime(2026, 10, 12), 1.0, id_ingrediente=94, id_bebida=None, data_validade=datetime(2028, 4, 3))
    criar_lote("LOTE-ING-095", "Hellmann's", datetime(2026, 10, 12), 2.0, id_ingrediente=95, id_bebida=None, data_validade=datetime(2028, 4, 4))
    criar_lote("LOTE-ING-096", "Hunt's", datetime(2026, 10, 12), 2.0, id_ingrediente=96, id_bebida=None, data_validade=datetime(2028, 4, 5))
    criar_lote("LOTE-ING-097", "Aurora", datetime(2026, 10, 12), 2.0, id_ingrediente=97, id_bebida=None, data_validade=datetime(2028, 4, 6))
    criar_lote("LOTE-ING-098", "Sadia", datetime(2026, 10, 12), 2.0, id_ingrediente=98, id_bebida=None, data_validade=datetime(2028, 4, 7))
    criar_lote("LOTE-ING-099", "Dr. Oetker", datetime(2026, 10, 12), 2.0, id_ingrediente=99, id_bebida=None, data_validade=datetime(2028, 4, 8))
    criar_lote("LOTE-ING-100", "Nestlé", datetime(2026, 10, 12), 2.0, id_ingrediente=100, id_bebida=None, data_validade=datetime(2028, 4, 9))
    criar_lote("LOTE-ING-101", "Mel Santa Bárbara", datetime(2026, 10, 12), 1.0, id_ingrediente=101, id_bebida=None, data_validade=datetime(2028, 4, 10))
    criar_lote("LOTE-ING-102", "Raiola", datetime(2026, 10, 12), 2.0, id_ingrediente=102, id_bebida=None, data_validade=datetime(2028, 4, 11))

    # Bebidas sem álcool e xaropes
    criar_lote("LOTE-ING-103", "Sucos Massa", datetime(2026, 10, 12), 2.0, id_ingrediente=103, id_bebida=None, data_validade=datetime(2028, 4, 12))
    criar_lote("LOTE-ING-104", "Monin", datetime(2026, 10, 12), 1.0, id_ingrediente=104, id_bebida=None, data_validade=datetime(2028, 4, 13))
    criar_lote("LOTE-ING-105", "Schweppes", datetime(2026, 10, 12), 6.0, id_ingrediente=105, id_bebida=None, data_validade=datetime(2028, 4, 14))
    criar_lote("LOTE-ING-106", "Finest Call", datetime(2026, 10, 12), 1.0, id_ingrediente=106, id_bebida=None, data_validade=datetime(2028, 4, 15))
    criar_lote("LOTE-ING-107", "Maguary", datetime(2026, 10, 12), 3.0, id_ingrediente=107, id_bebida=None, data_validade=datetime(2028, 4, 16))
    criar_lote("LOTE-ING-108", "Monin", datetime(2026, 10, 12), 1.0, id_ingrediente=108, id_bebida=None, data_validade=datetime(2028, 4, 17))
    criar_lote("LOTE-ING-109", "De Marchi", datetime(2026, 10, 12), 2.0, id_ingrediente=109, id_bebida=None, data_validade=datetime(2028, 4, 18))
    criar_lote("LOTE-ING-110", "Del Valle", datetime(2026, 10, 12), 3.0, id_ingrediente=110, id_bebida=None, data_validade=datetime(2028, 4, 19))
    criar_lote("LOTE-ING-111", "Guaraná Antarctica", datetime(2026, 10, 12), 6.0, id_ingrediente=111, id_bebida=None, data_validade=datetime(2028, 4, 20))
    criar_lote("LOTE-ING-112", "Lipton", datetime(2026, 10, 12), 2.0, id_ingrediente=112, id_bebida=None, data_validade=datetime(2028, 4, 21))
    criar_lote("LOTE-ING-113", "Monin", datetime(2026, 10, 12), 1.0, id_ingrediente=113, id_bebida=None, data_validade=datetime(2028, 4, 22))
    criar_lote("LOTE-ING-114", "Monin", datetime(2026, 10, 12), 1.0, id_ingrediente=114, id_bebida=None, data_validade=datetime(2028, 4, 23))
    criar_lote("LOTE-ING-115", "Sococo", datetime(2026, 10, 12), 3.0, id_ingrediente=115, id_bebida=None, data_validade=datetime(2028, 4, 24))
    criar_lote("LOTE-ING-116", "Maguary", datetime(2026, 10, 12), 3.0, id_ingrediente=116, id_bebida=None, data_validade=datetime(2028, 4, 25))
    criar_lote("LOTE-ING-117", "Monin", datetime(2026, 10, 12), 1.0, id_ingrediente=117, id_bebida=None, data_validade=datetime(2028, 4, 26))
    criar_lote("LOTE-ING-118", "Maguary", datetime(2026, 10, 12), 2.0, id_ingrediente=118, id_bebida=None, data_validade=datetime(2028, 4, 27))
    criar_lote("LOTE-ING-119", "Maguary", datetime(2026, 10, 12), 1.0, id_ingrediente=119, id_bebida=None, data_validade=datetime(2028, 4, 28))

    # Bebidas alcoólicas e ingredientes de coquetelaria
    criar_lote("LOTE-ING-120", "Cachaça 51", datetime(2026, 10, 12), 2.0, id_ingrediente=120, id_bebida=None, data_validade=datetime(2028, 4, 29))
    criar_lote("LOTE-ING-121", "José Cuervo", datetime(2026, 10, 12), 1.0, id_ingrediente=121, id_bebida=None, data_validade=datetime(2028, 4, 30))
    criar_lote("LOTE-ING-122", "Cointreau", datetime(2026, 10, 12), 1.0, id_ingrediente=122, id_bebida=None, data_validade=datetime(2028, 5, 1))
    criar_lote("LOTE-ING-123", "Tanqueray", datetime(2026, 10, 12), 2.0, id_ingrediente=123, id_bebida=None, data_validade=datetime(2028, 5, 2))
    criar_lote("LOTE-ING-124", "Campari", datetime(2026, 10, 12), 1.0, id_ingrediente=124, id_bebida=None, data_validade=datetime(2028, 5, 3))
    criar_lote("LOTE-ING-125", "Martini", datetime(2026, 10, 12), 1.0, id_ingrediente=125, id_bebida=None, data_validade=datetime(2028, 5, 4))
    criar_lote("LOTE-ING-126", "Absolut", datetime(2026, 10, 12), 2.0, id_ingrediente=126, id_bebida=None, data_validade=datetime(2028, 5, 5))
    criar_lote("LOTE-ING-127", "Fever-Tree", datetime(2026, 10, 12), 3.0, id_ingrediente=127, id_bebida=None, data_validade=datetime(2028, 5, 6))
    criar_lote("LOTE-ING-128", "Ocean Spray", datetime(2026, 10, 12), 2.0, id_ingrediente=128, id_bebida=None, data_validade=datetime(2028, 5, 7))
    criar_lote("LOTE-ING-129", "Bacardi", datetime(2026, 10, 12), 1.0, id_ingrediente=129, id_bebida=None, data_validade=datetime(2028, 5, 8))
    criar_lote("LOTE-ING-130", "Bacardi", datetime(2026, 10, 12), 1.0, id_ingrediente=130, id_bebida=None, data_validade=datetime(2028, 5, 9))
    criar_lote("LOTE-ING-131", "Monin", datetime(2026, 10, 12), 1.0, id_ingrediente=131, id_bebida=None, data_validade=datetime(2028, 5, 10))
    criar_lote("LOTE-ING-132", "Jim Beam", datetime(2026, 10, 12), 1.0, id_ingrediente=132, id_bebida=None, data_validade=datetime(2028, 5, 11))
    criar_lote("LOTE-ING-133", "Angostura", datetime(2026, 10, 12), 1.0, id_ingrediente=133, id_bebida=None, data_validade=datetime(2028, 5, 12))
    criar_lote("LOTE-ING-134", "Bulleit", datetime(2026, 10, 12), 1.0, id_ingrediente=134, id_bebida=None, data_validade=datetime(2028, 5, 13))
    criar_lote("LOTE-ING-135", "Luxardo", datetime(2026, 10, 12), 1.0, id_ingrediente=135, id_bebida=None, data_validade=datetime(2028, 5, 14))

    # Outros itens
    criar_lote("LOTE-ING-136", "McCain", datetime(2026, 10, 12), 3.0, id_ingrediente=136, id_bebida=None, data_validade=datetime(2028, 5, 15))
    criar_lote("LOTE-ING-137", "Nestlé", datetime(2026, 10, 12), 2.0, id_ingrediente=137, id_bebida=None, data_validade=datetime(2028, 5, 16))
    criar_lote("LOTE-ING-138", "Nestlé", datetime(2026, 10, 12), 2.0, id_ingrediente=138, id_bebida=None, data_validade=datetime(2028, 5, 17))
    criar_lote("LOTE-ING-139", "Pullman", datetime(2026, 10, 12), 2.0, id_ingrediente=139, id_bebida=None, data_validade=datetime(2028, 5, 18))


    # Inicializa o banco
def init_app(app):
    db.init_app(app)
    
    # Cria automaticamente todas as tabelas no arquivo do banco se elas não existirem
    with app.app_context():
        db.create_all()
        criar_admin()

