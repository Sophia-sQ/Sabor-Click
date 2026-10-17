"""Armazena todos os valores padrão do banco de dados"""

from datetime import datetime
from database import db


# ================================= Import ESTOQUE =================================

from model.servico_model import Servico, Bancada, Cardapio
from model.servico_model import (
    buscar_servico_por_nome,
    buscar_bancada_por_nome,
    buscar_cardapio_por_nome,
)

from model.ficha_model import Prato, Ingrediente, Lote
from model.ficha_model import (
    buscar_prato_por_nome,
    buscar_ingrediente_por_nome,
    buscar_lote_por_numero,
)

# ================================== Import CARGOS ==================================

from model.cargos import Cargo
from model.usuario_model import NivelPermissao
from model.usuario_model import buscar_permissao_por_nome, atualizar_permissao
from model.ficha_model import FichaTecnica

__all__ = ["iniciar_bancadas", "iniciar_servicos", "iniciar_cardapios", 
           "iniciar_pratos", "iniciar_ingredientes", "iniciar_lotes", 
           "iniciar_cargos", "iniciar_ficha_tecnica"]

# ================================= "Tabelas" ESTOQUE =================================

lista_servicos = [
    ("Chef_em_casa", "Prepara a refeição em pequenas comemorações e em ambiente domiciliar."),
    ("Buffet", "Prepara o ambiente para grandes comemorações que envolvam pratos quentes."),
    ("Bar", "Prepara bebidas escolhidas pelo cliente no balcão."),
    ("Mesa_de_salgados", "Organiza os salgados para festas."),
]

lista_bancadas = [
    ("Rechauds", "Equipamento que mantem o alimento quente"),
    ("Kit_loucas", "Kit que contem o basico de mesa posta: Talheres, pratos e guardanapo de pano"),
    ("Chapa_hamburguer_portatil", "Equipamento utilizado para confeccao de lanches"),
    ("Bancada_bar_portatil", "Equipamento que organiza e prepara as bebidas"),
    ("Maquina_de_gelo", "Equipamento responsavel por fazer gelo"),
    ("Limpeza", "Equipamentos responsaveis pela limpeza final no evento"),
]

cardapios_quentes=[
    ("Feijoada_completa", " ", 0),
    ("Bobo_de_camarao ", " ", 0),
    ("File_de_tilapia_ao_molho_manteiga_e_alcaparras ", " ", 0),
    ("Strogonoff_de_file_Mignon ", " ", 0),
    ("Nhoque_ao_molho", " ", 0),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", " ", 0),
    ("Escondinho_de_carne_seca_com_mandioca ", " ", 0),
    ("Raviolli_de_queijo_ao_molho_bolonhesa ", " ", 0),
]

cardapios_salgados=[
    ("Salgados_completo ", " ", 0),
    ("Salgados_Reduzido", " ", 0),
    ("Hamburguer_tradicional ", " ", 0),
    ("Hamburguer_smash ", " ", 0),
    ("Hamburguer_mega_bacon ", " ", 0),
    ("Mexicano ", " ", 0),
    ("Boteco_brasileiro", " ", 0),
]

cardapios_bebidas=[
    ("Bebida_sem_alcool", " ", 0),
    ("Bebida_com_alcool", " ", 0),
    ("Bebida_mista", " ", 0),

]

lista_cardapios = [
    # nome, descrição, preço base
    cardapios_quentes,
    cardapios_salgados,
    cardapios_bebidas
]

lista_pratos = [
    ("Mandioca_frita", "Pedacos de mandioca frita em oleo", "entrada", 40, True) #requer-preparo, pois tem que levar ela cozida e fritar no local,
    ("Tabua_de_frios", "Tabua contendo aperitivos: Salame, queijo, azeitona", "entrada", 15, False),
    ("Feijoada_completa", "Feijoada", "prato principal", 120, True),
    ("Arroz_branco", "Arroz cozido", "acompanhamento", 20, False),
    ("Couve_refogada", "Couve picada refogada", "acompanhamento", 10, False) # A colve comprada é picada ja,
    ("Farofa", "Farofa comprada", "acompanhamento", 0, False),
    ("Vinagrete", "Vinagrete completo: Ceblo, tomate, pimentao,cebolinha,vinagre", "acompanhamento", 15, True) #Levar cortado as coisas, e temperar no local,
    ("Molho_de_pimenta", "Molho de pimenta pronto", "acompanhamento", 0, False),
    ("Sorvete", "Sorvete comprado de maracuja e limao", "sobremesa", 0, False),
    ("Salada_fresca", "Salada de folhas hidroponicas e tomate cereja", "entrada", 5, True) #Lavar antes,
    ("Bobo_de_camarao", "Bobo de camarao completo", "prato principal", 120, True),
    ("Salada_de_fruta_fresca_com_creme", "Salada de frutas com creme de leite e leite condensado", "sobremesa", 0, False),
    ("Bruschetta", "Bruscretta de pao italiano, tomate e manjericao", "entrada", 5, False),
    ("File_de_tilapia", "File de tilapia grelhado", "prato principal", 30, True) #Limpar o file de tilapia,
    ("Molho_de_mateiga_com_alcaparras", "Molho de acompanhamento de manteiga e alcaparras", "Acomapanhamento", 10, False),
    ("Iorgute_Natural_com_morangos_e_mel", "Iorgute com pedacos de fruta e adocado com mel", "sobremesa", 5, False),
    ("Salada_ceaser", "Salada de alface, croutons e molho caesar", "entrada", 20, False),
    ("Stogonoff_de_file_mignon", "Strogonoff cremoso de filé mignon", "prato principal", 120, True),
    ("Batata_palha", "Batata palha crocante pronta", "acompanhamento", 0, False),
    ("Pudim_de_leite_condensado", "Pudim de leite tradicional com calda de caramelo", "sobremesa", 120, True),
    ("Nhoque_ao_molho", "Nhoque de batata ao molho de tomate", "prato principal", 120, True),
    ("Mousse_de_maracuja", "Mousse leve e aerada de maracujá", "sobremesa", 40, True),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Risoto cremoso de cogumelos acompanhado de filé mignon", "prato principal", 60, True),
    ("Brownie_de_chocolate", "Brownie caseiro de chocolate denso", "sobremesa", 60, True),
    ("Dadinho_de_tapioca", "Dadinhos de tapioca com queijo coalho fritos", "entrada", 40, True),
    ("Escondidinho_de_carne_seca_com_mandioca", "Escondidinho de carne seca com purê de mandioca", "prato principal", 180, True),
    ("Geleia_de_pimenta", "Geia doce e levemente picante de pimenta", "acompanhamento", 0, False),
    ("Cheesecake_de_frutas_vermelhas", "Cheesecake assado com calda de frutas vermelhas", "sobremesa", 60, True),
    ("Ravioli_de_queijo_ao_molho_bolanhesa", "Ravioli recheado com queijo ao molho bolonhesa", "prato principal", 120, True),
    ("Parmesao_ralado", "Queijo parmesão ralado fino", "acompanhamento", 0, False),
    ("Mousse_de_chocolate", "Mousse cremosa de chocolate meio amargo", "sobremesa", 40, True),
    ("Coxinha", "Salgado frito recheado com frango desfiado", "prato principal", 6, False),
    ("Risole", "Salgado frito em formato de meia-lua recheado", "prato principal", 6, False),
    ("Quibe", "Salgado de carne moída com trigo para quibe", "prato principal", 6, False),
    ("Bolinha_de_queijo", "Salgadinho frito recheado com queijo", "prato principal", 6, False),
    ("Empada", "Empada de massa podre recheada", "prato principal", 15, False),
    ("Croquete", "Croquete frito de carne temperada", "prato principal", 10, False),
    ("Batata_frita", "Porção de batata frita crocante", "prato principal", 15, False),
    ("Queijo", "Fatias ou cubos de queijo variados", "prato principal", 0, False),
    ("Embutido", "Porção de embutidos fatiados", "prato principal", 0, False),
    ("Pao", "Cesta de pães frescos fatiados", "prato principal", 0, False),
    ("Brigadeiro", "Docinho tradicional de chocolate com granulado", "prato principal", 30, True),
    ("Beijinho", "Docinho tradicional de coco com cravo", "prato principal", 30, True),
    ("Bolo", "Bolo caseiro fofinho", "prato principal", 240, True),
    ("Hamburguer_tradicional", "Hambúrguer artesanal de carne bovina", "prato principal", 25, False),
    ("Hamburguer_smash", "Hambúrguer prensado na chapa crocante", "prato principal", 25, False),
    ("Hamburguer_mega_bacon", "Hambúrguer de carne com extra de bacon crocante", "prato principal", 25, False),
    ("Tortilha_mexicana", "Tortilha recheada estilo mexicana", "prato principal", 30, False),
    ("Pastel_de_carne", "Pastel frito recheado com carne moída temperada", "prato principal", 6, False),
    ("Bolinho_de_bacalhau", "Bolinho tradicional de bacalhau e batata", "prato principal", 6, False),
    ("Liguica_acebolada", "Porção de linguiça frita com cebola", "prato principal", 10, False),
    ("Pastel_de_queijo", "Pastel frito recheado com queijo derretido", "prato principal", 6, False),
]

ingredientes_carnes = [
        ('Pe_de_porco', 'g', 30, 9)
        ('Rabo_de_porco', 'g', 15, 4)
        ('Costelinha_suina_defumada', 'g', 24, 6)
        ('Bacon', 'g', 15, 3)
        ('Linguica_calabresa', 'g', 24, 6)
        ('Linguica_acebolada', 'g', 15, 3)
        ('Lombo_de_porco', 'g', 24, 6)
        ('Carne_seca', 'g', 24, 6)
        ('Camarao_medio_limpo', 'g', 15, 3)
        ('File_de_tilapia', 'g', 24, 6)
        ('File_mignon_bovino', 'g', 24, 6)
        ('Carne_moida_de_primeira', 'g', 30, 9)
        ('Carne_moida_blend_patinho_acem', 'g', 24, 6)
        ('Frango_grelhado', 'g', 24, 6)
        ('Frango_desfiado', 'g', 15, 3)
        ('Presunto', 'g', 9, 1)
        ('Bolinho_de_bacalhau', 'g', 15, 3)
        ('Salame', 'Kg', 10.0, 3.0)
]

ingredientes_carboidratos = [
        ('Feijao_preto', 'g', 45, 12)
        ('Arroz_branco', 'g', 60, 15)
        ('Arroz_arborio', 'g', 24, 6)
        ('Mandioca_in_natura', 'g', 30, 9)
        ('Farinha_de_mandioca', 'g', 24, 6)
        ('Batata', 'g', 60, 15)
        ('Batata_palha', 'g', 15, 3)
        ('Nhoque_de_batata_pronto', 'g', 15, 3)
        ('Ravioli_fresco_de_queijo', 'g', 15, 3)
        ('Pao_italiano', 'Kg', 20.0, 5.0)
        ('Pao_brioche', 'unidade', 30, 8)
        ('Pao_de_forma', 'pacote', 10.0, 2.0)
        ('Mini_paes', 'unidade', 100, 25)
        ('Tortilla_de_milho', 'unidade', 50, 10)
        ('Tortilla_de_trigo', 'unidade', 50, 10)
        ('Tapioca_granulada', 'g', 15, 3)
        ('Nachos', 'g', 15, 3)
        ('Biscoito_base', 'Kg', 15.0, 3.0)
        ('Coxinha', 'unidade', 100, 25)
        ('Risole', 'unidade', 100, 25)
        ('Quibe', 'unidade', 100, 25)
        ('Croquete', 'unidade', 100, 25)
        ('Empada', 'unidade', 100, 25)
        ('Bolinha_de_queijo', 'unidade', 100, 25)
        ('Pastel_de_carne', 'unidade', 100, 25)
        ('Pastel_de_queijo', 'unidade', 100, 25)
]

ingredientes_laticinios = [
        ('Manteiga', 'g', 15, 3)
        ('Queijo_mucarela', 'g', 24, 6)
        ('Queijo_prato', 'g', 15, 3)
        ('Queijo_cheddar', 'g', 12, 3)
        ('Queijo_coalho', 'g', 15, 3)
        ('Queijo_ralado', 'g', 6, 1)
        ('Parmesao_ralado', 'g', 9, 1)
        ('Creme_de_leite', 'mL', 24, 6)
        ('Leite_condensado', 'mL', 24, 6)
        ('Leite_integral', 'mL', 45, 12)
        ('Leite_de_coco', 'mL', 15, 3)
        ('Iogurte_natural', 'mL', 15, 3)
        ('Cream_cheese', 'g', 12, 3)
        ('Ovos', 'unidade', 180, 36)
]

ingredientes_vegetais = [
        ('Folhas_hidroponicas', 'g', 9, 2)
        ('Folhas_variadas', 'g', 9, 2)
        ('Alface_romana', 'unidade', 20, 5)
        ('Alface_americana', 'unidade', 20, 5)
        ('Couve_manteiga', 'g', 9, 2)
        ('Tomate', 'g', 30, 6)
        ('Tomate_cereja', 'g', 12, 3)
        ('Cebola', 'g', 30, 6)
        ('Cebola_caramelizada', 'g', 9, 1)
        ('Pimentao', 'g', 12, 3)
        ('Cebolinha', 'g', 3, 0)
        ('Alho', 'g', 9, 1)
        ('Manjericao', 'g', 1, 0)
        ('Salsinha', 'g', 3, 0)
        ('Limao', 'g', 24, 6)
        ('Laranja', 'g', 24, 6)
        ('Cogumelos_frescos', 'g', 9, 1)
        ('Champignon', 'g', 9, 1)
        ('Morango_fresco', 'g', 15, 3)
        ('Frutas_frescas_in_natura', 'g', 30, 6)
        ('Frutas_vermelhas_congeladas', 'g', 12, 3)
        ('Nozes', 'g', 6, 1)
]

ingredientes_temperos = [
        ('Oleo_de_soja', 'mL', 30, 6)
        ('Oleo_para_fritura', 'mL', 60, 15)
        ('Sal', 'g', 24, 6)
        ('Acucar', 'g', 24, 6)
        ('Temperos', 'g', 9, 1)
        ('Vinagre', 'mL', 15, 3)
        ('Azeite', 'mL', 15, 3)
        ('Azeite_de_dende', 'mL', 9, 1)
        ('Molho_de_pimenta', 'mL', 6, 1)
        ('Geleia_de_pimenta', 'g', 9, 1)
        ('Alcaparras', 'g', 3, 0)
        ('Molho_de_tomate', 'mL', 24, 6)
        ('Catchup', 'mL', 15, 3)
        ('Mostarda', 'mL', 9, 1)
        ('Molho_mostarda_e_mel', 'mL', 9, 1)
        ('Molho_Caesar', 'mL', 9, 1)
        ('Croutons', 'g', 6, 1)
        ('Maionese_temperada', 'mL', 15, 3)
        ('Molho_barbecue', 'mL', 9, 1)
        ('Vinho_branco', 'mL', 15, 3)
        ('Guacamole', 'g', 9, 1)
        ('Gelatina', 'g', 9, 1)
        ('Chocolate_meio_amargo', 'g', 15, 3)
        ('Mel', 'g', 9, 1)
        ('Azeitona', 'g', 9, 1)
]

ingredientes_bebidas_sem_alcool = [
        ('Suco_de_limao', 'mL', 15, 3)
        ('Xarope_de_groselha_framboesa', 'mL', 9, 1)
        ('Agua_com_gas', 'mL', 60, 15)
        ('Xarope_simples_de_acucar', 'mL', 9, 1)
        ('Suco_de_abacaxi', 'mL', 24, 6)
        ('Xarope_de_maca_verde', 'mL', 6, 1)
        ('Polpa_de_frutas_vermelhas', 'g', 15, 3)
        ('Suco_de_laranja', 'mL', 30, 6)
        ('Refrigerante_de_guarana', 'mL', 60, 15)
        ('Cha_preto', 'g', 3, 0)
        ('Xarope_de_pessego', 'mL', 6, 1)
        ('Xarope_de_grenadine', 'mL', 6, 1)
        ('Agua_de_coco', 'mL', 24, 6)
        ('Suco_de_maracuja', 'mL', 24, 6)
        ('Xarope_de baunilha', 'mL', 6, 1)
        ('Suco_de_melancia', 'mL', 15, 3)
        ('Suco_de_gengibre', 'mL', 6, 1)
]

ingredientes_bebidas_alcoolicas = [
        ('Cachaca', 'mL', 15, 3)
        ('Tequila', 'mL', 9, 1)
        ('Cointreau_triple_sec', 'mL', 6, 1)
        ('Gin', 'mL', 15, 3)
        ('Campari', 'mL', 9, 1)
        ('Vermute_tinto', 'mL', 9, 1)
        ('Vodka', 'mL', 15, 3)
        ('Ginger_beer', 'mL', 24, 6)
        ('Suco_de_cranberry', 'mL', 15, 3)
        ('Rum_branco', 'mL', 9, 1)
        ('Rum_escuro', 'mL', 9, 1)
        ('Xarope_de_amendoa_orgeat', 'mL', 6, 1)
        ('Uisque_bourbon', 'mL', 9, 1)
        ('Angostura_bitters', 'ml', 500.0, 100.0)
        ('Uisque_de_centeio_rye', 'mL', 9, 1)
        ('Cereja_marasquino', 'g', 6, 1)
]

ingredientes_diversos = [
        ('Onion_rings', 'g', 15, 3)
        ('Brigadeiro', 'unidade', 100, 25)
        ('Beijinho', 'unidade', 100, 25)
        ('Bolo_comum_simples', 'g', 15, 3)
]

lista_ingredientes = [
    # nome, unidade de medida, estoque atual, estoque minimo
    ingredientes_carnes,
    ingredientes_carboidratos,
    ingredientes_laticinios,
    ingredientes_vegetais,
    ingredientes_temperos,
    ingredientes_bebidas_sem_alcool,
    ingredientes_bebidas_alcoolicas,
    ingredientes_diversos,
]

lista_lotes = [
    # código, fornecedor, data_entrada, quantidade, nome_ingrediente, data_validade

    ("LOTE-ING-001", "Pamplona", datetime(2026, 10, 12), 5.0, "Pe_de_porco", datetime(2028, 1, 1)),

    ("LOTE-ING-002", "Pamplona", datetime(2026, 10, 12), 3.0, "Rabo_de_porco", datetime(2028, 1, 2)),

    ("LOTE-ING-003", "Seara", datetime(2026, 10, 12), 4.0, "Costelinha_suina_defumada", datetime(2028, 1, 3)),

    ("LOTE-ING-004", "Sadia", datetime(2026, 10, 12), 2.0, "Bacon", datetime(2028, 1, 4)),

    ("LOTE-ING-005", "Perdigão", datetime(2026, 10, 12), 3.0, "Linguica_calabresa", datetime(2028, 1, 5)),

    ("LOTE-ING-006", "Aurora", datetime(2026, 10, 12), 2.0, "Linguica_acebolada", datetime(2028, 1, 6)),

    ("LOTE-ING-007", "Sadia", datetime(2026, 10, 12), 3.0, "Lombo_de_porco", datetime(2028, 1, 7)),

    ("LOTE-ING-008", "Friboi", datetime(2026, 10, 12), 4.0, "Carne_seca", datetime(2028, 1, 8)),

    ("LOTE-ING-009", "Copacol", datetime(2026, 10, 12), 2.0, "Camarao_medio_limpo", datetime(2028, 1, 9)),

    ("LOTE-ING-010", "Copacol", datetime(2026, 10, 12), 3.0, "File_de_tilapia", datetime(2028, 1, 10)),

    ("LOTE-ING-011", "Friboi", datetime(2026, 10, 12), 2.0, "File_mignon_bovino", datetime(2028, 1, 11)),

    ("LOTE-ING-012", "Friboi", datetime(2026, 10, 12), 3.0, "Carne_moida_de_primeira", datetime(2028, 1, 12)),

    ("LOTE-ING-013", "Swift", datetime(2026, 10, 12), 3.0, "Carne_moida_blend_patinho_acem", datetime(2028, 1, 13)),

    ("LOTE-ING-014", "Sadia", datetime(2026, 10, 12), 4.0, "Frango_grelhado", datetime(2028, 1, 14)),

    ("LOTE-ING-015", "Seara", datetime(2026, 10, 12), 3.0, "Frango_desfiado", datetime(2028, 1, 15)),

    ("LOTE-ING-016", "Sadia", datetime(2026, 10, 12), 2.0, "Presunto", datetime(2028, 1, 16)),

    ("LOTE-ING-017", "Copacol", datetime(2026, 10, 12), 2.0, "Bolinho_de_bacalhau", datetime(2028, 1, 17)),

    # Grãos, massas, pães e salgados

    ("LOTE-ING-018", "Camil", datetime(2026, 10, 12), 5.0, "Feijao_preto", datetime(2028, 1, 18)),

    ("LOTE-ING-019", "Camil", datetime(2026, 10, 12), 10.0, "Arroz_branco", datetime(2028, 1, 19)),

    ("LOTE-ING-020", "Tio João", datetime(2026, 10, 12), 5.0, "Arroz_arborio", datetime(2028, 1, 20)),

    ("LOTE-ING-021", "De Marchi", datetime(2026, 10, 12), 5.0, "Mandioca_in_natura", datetime(2028, 1, 21)),

    ("LOTE-ING-022", "Yoki", datetime(2026, 10, 12), 3.0, "Farinha_de_mandioca", datetime(2028, 1, 22)),

    ("LOTE-ING-023", "Bem Brasil", datetime(2026, 10, 12), 5.0, "Batata", datetime(2028, 1, 23)),

    ("LOTE-ING-024", "Yoki", datetime(2026, 10, 12), 2.0, "Batata_palha", datetime(2028, 1, 24)),

    ("LOTE-ING-025", "Nico", datetime(2026, 10, 12), 3.0, "Nhoque_de_batata_pronto", datetime(2028, 1, 25)),

    ("LOTE-ING-026", "Massa Leve", datetime(2026, 10, 12), 3.0, "Ravioli_fresco_de_queijo", datetime(2028, 1, 26)),

    ("LOTE-ING-027", "Wickbold", datetime(2026, 10, 12), 4.0, "Pao_italiano", datetime(2028, 1, 27)),

    ("LOTE-ING-028", "Pullman", datetime(2026, 10, 12), 3.0, "Pao_brioche", datetime(2028, 1, 28)),

    ("LOTE-ING-029", "Wickbold", datetime(2026, 10, 12), 3.0, "Pao_de_forma", datetime(2028, 1, 29)),

    ("LOTE-ING-030", "Seven Boys", datetime(2026, 10, 12), 2.0, "Mini_paes", datetime(2028, 1, 30)),

    ("LOTE-ING-031", "Rap10", datetime(2026, 10, 12), 3.0, "Tortilla_de_milho", datetime(2028, 1, 31)),

    ("LOTE-ING-032", "Rap10", datetime(2026, 10, 12), 3.0, "Tortilla_de_trigo", datetime(2028, 2, 1)),

    ("LOTE-ING-033", "Yoki", datetime(2026, 10, 12), 2.0, "Tapioca_granulada", datetime(2028, 2, 2)),

    ("LOTE-ING-034", "Doritos", datetime(2026, 10, 12), 2.0, "Nachos", datetime(2028, 2, 3)),

    ("LOTE-ING-035", "Marilan", datetime(2026, 10, 12), 2.0, "Biscoito_base", datetime(2028, 2, 4)),

    ("LOTE-ING-036", "Seara", datetime(2026, 10, 12), 3.0, "Coxinha", datetime(2028, 2, 5)),

    ("LOTE-ING-037", "Seara", datetime(2026, 10, 12), 3.0, "Risole", datetime(2028, 2, 6)),

    ("LOTE-ING-038", "Seara", datetime(2026, 10, 12), 3.0, "Quibe", datetime(2028, 2, 7)),

    ("LOTE-ING-039", "Seara", datetime(2026, 10, 12), 3.0, "Croquete", datetime(2028, 2, 8)),

    ("LOTE-ING-040", "Forno de Minas", datetime(2026, 10, 12), 2.0, "Empada", datetime(2028, 2, 9)),

    ("LOTE-ING-041", "Seara", datetime(2026, 10, 12), 3.0, "Bolinha_de_queijo", datetime(2028, 2, 10)),

    ("LOTE-ING-042", "Aurora", datetime(2026, 10, 12), 3.0, "Pastel_de_carne", datetime(2028, 2, 11)),

    # Laticínios e ovos

    ("LOTE-ING-043", "Qualy", datetime(2026, 10, 12), 2.0, "Manteiga", datetime(2028, 2, 12)),

    ("LOTE-ING-044", "Tirolez", datetime(2026, 10, 12), 3.0, "Queijo_mucarela", datetime(2028, 2, 13)),

    ("LOTE-ING-045", "President", datetime(2026, 10, 12), 2.0, "Queijo_prato", datetime(2028, 2, 14)),

    ("LOTE-ING-046", "Polenghi", datetime(2026, 10, 12), 2.0, "Queijo_cheddar", datetime(2028, 2, 15)),

    ("LOTE-ING-047", "Tirolez", datetime(2026, 10, 12), 2.0, "Queijo_coalho", datetime(2028, 2, 16)),

    ("LOTE-ING-048", "Vigor", datetime(2026, 10, 12), 1.0, "Queijo_ralado", datetime(2028, 2, 17)),

    ("LOTE-ING-049", "Faixa Azul", datetime(2026, 10, 12), 1.0, "Parmesao_ralado", datetime(2028, 2, 18)),

    ("LOTE-ING-050", "Nestlé", datetime(2026, 10, 12), 3.0, "Creme_de_leite", datetime(2028, 2, 19)),

    ("LOTE-ING-051", "Moça", datetime(2026, 10, 12), 3.0, "Leite_condensado", datetime(2028, 2, 20)),

    ("LOTE-ING-052", "Italac", datetime(2026, 10, 12), 5.0, "Leite_integral", datetime(2028, 2, 21)),

    ("LOTE-ING-053", "Sococo", datetime(2026, 10, 12), 3.0, "Leite_de_coco", datetime(2028, 2, 22)),

    ("LOTE-ING-054", "Nestlé", datetime(2026, 10, 12), 2.0, "Iogurte_natural", datetime(2028, 2, 23)),

    ("LOTE-ING-055", "Philadelphia", datetime(2026, 10, 12), 2.0, "Cream_cheese", datetime(2028, 2, 24)),

    ("LOTE-ING-056", "Mantiqueira", datetime(2026, 10, 12), 5.0, "Ovos", datetime(2028, 2, 25)),

    # Verduras, legumes, frutas e cogumelos

    ("LOTE-ING-057", "Fazenda local", datetime(2026, 10, 12), 2.0,
     "Folhas_hidroponicas", datetime(2028, 2, 26)),

    ("LOTE-ING-058", "Fazenda local", datetime(2026, 10, 12), 3.0,
     "Folhas_variadas", datetime(2028, 2, 27)),

    ("LOTE-ING-059", "Hortifruti", datetime(2026, 10, 12), 2.0,
     "Alface_romana", datetime(2028, 2, 28)),

    ("LOTE-ING-060", "Hortifruti", datetime(2026, 10, 12), 2.0,
     "Alface_americana", datetime(2028, 2, 29)),

    ("LOTE-ING-061", "Hortifruti", datetime(2026, 10, 12), 2.0,
     "Couve_manteiga", datetime(2028, 3, 1)),

    ("LOTE-ING-062", "Hortifruti", datetime(2026, 10, 12), 4.0,
     "Tomate", datetime(2028, 3, 2)),

    ("LOTE-ING-063", "Hortifruti", datetime(2026, 10, 12), 2.0,
     "Tomate_cereja", datetime(2028, 3, 3)),

    ("LOTE-ING-064", "Hortifruti", datetime(2026, 10, 12), 3.0,
     "Cebola", datetime(2028, 3, 4)),

    ("LOTE-ING-065", "Predilecta", datetime(2026, 10, 12), 2.0,
     "Cebola_caramelizada", datetime(2028, 3, 5)),

    ("LOTE-ING-066", "Hortifruti", datetime(2026, 10, 12), 2.0,
     "Pimentao", datetime(2028, 3, 6)),

    ("LOTE-ING-067", "Hortifruti", datetime(2026, 10, 12), 1.0,
     "Cebolinha", datetime(2028, 3, 7)),

    ("LOTE-ING-068", "Hortifruti", datetime(2026, 10, 12), 1.0,
     "Alho", datetime(2028, 3, 8)),

    ("LOTE-ING-069", "Hortifruti", datetime(2026, 10, 12), 1.0,
     "Manjericao", datetime(2028, 3, 9)),

    ("LOTE-ING-070", "Hortifruti", datetime(2026, 10, 12), 1.0,
     "Salsinha", datetime(2028, 3, 10)),

    ("LOTE-ING-071", "Hortifruti", datetime(2026, 10, 12), 2.0,
     "Limao", datetime(2028, 3, 11)),

    ("LOTE-ING-072", "Hortifruti", datetime(2026, 10, 12), 3.0,
     "Laranja", datetime(2028, 3, 12)),

    ("LOTE-ING-073", "Fazenda local", datetime(2026, 10, 12), 2.0,
     "Cogumelos_frescos", datetime(2028, 3, 13)),

    ("LOTE-ING-074", "Raiola", datetime(2026, 10, 12), 2.0,
     "Champignon", datetime(2028, 3, 14)),

    ("LOTE-ING-075", "Hortifruti", datetime(2026, 10, 12), 2.0,
     "Morango_fresco", datetime(2028, 3, 15)),

    ("LOTE-ING-076", "Hortifruti", datetime(2026, 10, 12), 4.0,
     "Frutas_frescas_in_natura", datetime(2028, 3, 16)),

    ("LOTE-ING-077", "De Marchi", datetime(2026, 10, 12), 2.0,
     "Frutas_vermelhas_congeladas", datetime(2028, 3, 17)),

    ("LOTE-ING-078", "Agtal", datetime(2026, 10, 12), 1.0,
     "Nozes", datetime(2028, 3, 18)),

    # Óleos, temperos, molhos e outros produtos

    ("LOTE-ING-079", "Liza", datetime(2026, 10, 12), 5.0,
     "Oleo_de_soja", datetime(2028, 3, 19)),

    ("LOTE-ING-080", "Soya", datetime(2026, 10, 12), 10.0,
     "Oleo_para_fritura", datetime(2028, 3, 20)),

    ("LOTE-ING-081", "Cisne", datetime(2026, 10, 12), 2.0,
     "Sal", datetime(2028, 3, 21)),

    ("LOTE-ING-082", "Kitano", datetime(2026, 10, 12), 1.0,
     "Temperos", datetime(2028, 3, 22)),

    ("LOTE-ING-083", "Castelo", datetime(2026, 10, 12), 2.0,
     "Vinagre", datetime(2028, 3, 23)),

    ("LOTE-ING-084", "Gallo", datetime(2026, 10, 12), 3.0,
     "Azeite", datetime(2028, 3, 24)),

    ("LOTE-ING-085", "Cepêra", datetime(2026, 10, 12), 2.0,
     "Azeite_de_dende", datetime(2028, 3, 25)),

    ("LOTE-ING-086", "Tabasco", datetime(2026, 10, 12), 1.0,
     "Molho_de_pimenta", datetime(2028, 3, 26)),

    ("LOTE-ING-087", "Queensberry", datetime(2026, 10, 12), 2.0,
     "Geleia_de_pimenta", datetime(2028, 3, 27)),

    ("LOTE-ING-088", "La Pastina", datetime(2026, 10, 12), 1.0,
     "Alcaparras", datetime(2028, 3, 28)),

    ("LOTE-ING-089", "Pomarola", datetime(2026, 10, 12), 4.0,
     "Molho_de_tomate", datetime(2028, 3, 29)),

    ("LOTE-ING-090", "Heinz", datetime(2026, 10, 12), 2.0,
     "Catchup", datetime(2028, 3, 30)),

    ("LOTE-ING-091", "Hemmer", datetime(2026, 10, 12), 2.0,
     "Mostarda", datetime(2028, 3, 31)),

    ("LOTE-ING-092", "Hellmann's", datetime(2026, 10, 12), 2.0,
     "Molho_mostarda_e_mel", datetime(2028, 4, 1)),

    ("LOTE-ING-093", "Hellmann's", datetime(2026, 10, 12), 2.0,
     "Molho_Caesar", datetime(2028, 4, 2)),

    ("LOTE-ING-094", "Marilan", datetime(2026, 10, 12), 1.0,
     "Croutons", datetime(2028, 4, 3)),

    ("LOTE-ING-095", "Hellmann's", datetime(2026, 10, 12), 2.0,
     "Maionese_temperada", datetime(2028, 4, 4)),

    ("LOTE-ING-096", "Hunt's", datetime(2026, 10, 12), 2.0,
     "Molho_barbecue", datetime(2028, 4, 5)),

    ("LOTE-ING-097", "Aurora", datetime(2026, 10, 12), 2.0,
     "Vinho_branco", datetime(2028, 4, 6)),

    ("LOTE-ING-098", "Sadia", datetime(2026, 10, 12), 2.0,
     "Guacamole", datetime(2028, 4, 7)),

    ("LOTE-ING-099", "Dr. Oetker", datetime(2026, 10, 12), 2.0,
     "Gelatina", datetime(2028, 4, 8)),

    ("LOTE-ING-100", "Nestlé", datetime(2026, 10, 12), 2.0,
     "Chocolate_meio_amargo", datetime(2028, 4, 9)),

    ("LOTE-ING-101", "Mel Santa Bárbara", datetime(2026, 10, 12), 1.0,
     "Mel", datetime(2028, 4, 10)),

    ("LOTE-ING-102", "Raiola", datetime(2026, 10, 12), 2.0,
     "Azeitona", datetime(2028, 4, 11)),

    # Bebidas sem álcool e xaropes

    ("LOTE-ING-103", "Sucos Massa", datetime(2026, 10, 12), 2.0,
     "Suco_de_limao", datetime(2028, 4, 12)),

    ("LOTE-ING-104", "Monin", datetime(2026, 10, 12), 1.0,
     "Xarope_de_groselha_framboesa", datetime(2028, 4, 13)),

    ("LOTE-ING-105", "Schweppes", datetime(2026, 10, 12), 6.0,
     "Agua_com_gas", datetime(2028, 4, 14)),

    ("LOTE-ING-106", "Finest Call", datetime(2026, 10, 12), 1.0,
     "Xarope_simples_de_acucar", datetime(2028, 4, 15)),

    ("LOTE-ING-107", "Maguary", datetime(2026, 10, 12), 3.0,
     "Suco_de_abacaxi", datetime(2028, 4, 16)),

    ("LOTE-ING-108", "Monin", datetime(2026, 10, 12), 1.0,
     "Xarope_de_maca_verde", datetime(2028, 4, 17)),

    ("LOTE-ING-109", "De Marchi", datetime(2026, 10, 12), 2.0,
     "Polpa_de_frutas_vermelhas", datetime(2028, 4, 18)),

    ("LOTE-ING-110", "Del Valle", datetime(2026, 10, 12), 3.0,
     "Suco_de_laranja", datetime(2028, 4, 19)),

    ("LOTE-ING-111", "Guaraná Antarctica", datetime(2026, 10, 12), 6.0,
     "Refrigerante_de_guarana", datetime(2028, 4, 20)),

    ("LOTE-ING-112", "Lipton", datetime(2026, 10, 12), 2.0,
     "Cha_preto", datetime(2028, 4, 21)),

    ("LOTE-ING-113", "Monin", datetime(2026, 10, 12), 1.0,
     "Xarope_de_pessego", datetime(2028, 4, 22)),

    ("LOTE-ING-114", "Monin", datetime(2026, 10, 12), 1.0,
     "Xarope_de_grenadine", datetime(2028, 4, 23)),

    ("LOTE-ING-115", "Sococo", datetime(2026, 10, 12), 3.0,
     "Agua_de_coco", datetime(2028, 4, 24)),

    ("LOTE-ING-116", "Maguary", datetime(2026, 10, 12), 3.0,
     "Suco_de_maracuja", datetime(2028, 4, 25)),

    ("LOTE-ING-117", "Monin", datetime(2026, 10, 12), 1.0,
     "Xarope_de baunilha", datetime(2028, 4, 26)),

    ("LOTE-ING-118", "Maguary", datetime(2026, 10, 12), 2.0,
     "Suco_de_melancia", datetime(2028, 4, 27)),

    ("LOTE-ING-119", "Maguary", datetime(2026, 10, 12), 1.0,
     "Suco_de_gengibre", datetime(2028, 4, 28)),

    # Bebidas alcoólicas e ingredientes de coquetelaria

    ("LOTE-ING-120", "Cachaça 51", datetime(2026, 10, 12), 2.0,
     "Cachaca", datetime(2028, 4, 29)),

    ("LOTE-ING-121", "José Cuervo", datetime(2026, 10, 12), 1.0,
     "Tequila", datetime(2028, 4, 30)),

    ("LOTE-ING-122", "Cointreau", datetime(2026, 10, 12), 1.0,
     "Cointreau_triple_sec", datetime(2028, 5, 1)),

    ("LOTE-ING-123", "Tanqueray", datetime(2026, 10, 12), 2.0,
     "Gin", datetime(2028, 5, 2)),

    ("LOTE-ING-124", "Campari", datetime(2026, 10, 12), 1.0,
     "Campari", datetime(2028, 5, 3)),

    ("LOTE-ING-125", "Martini", datetime(2026, 10, 12), 1.0,
     "Vermute_tinto", datetime(2028, 5, 4)),

    ("LOTE-ING-126", "Absolut", datetime(2026, 10, 12), 2.0,
     "Vodka", datetime(2028, 5, 5)),

    ("LOTE-ING-127", "Fever-Tree", datetime(2026, 10, 12), 3.0, "Ginger_beer", datetime(2028, 5, 6)),

    ("LOTE-ING-128", "Ocean Spray", datetime(2026, 10, 12), 2.0, "Suco_de_cranberry", datetime(2028, 5, 7)),

    ("LOTE-ING-129", "Bacardi", datetime(2026, 10, 12), 1.0, "Rum_branco", datetime(2028, 5, 8)),

    ("LOTE-ING-130", "Bacardi", datetime(2026, 10, 12), 1.0, "Rum_escuro", datetime(2028, 5, 9)),

    ("LOTE-ING-131", "Monin", datetime(2026, 10, 12), 1.0, "Xarope_de_amendoa_orgeat", datetime(2028, 5, 10)),

    ("LOTE-ING-132", "Jim Beam", datetime(2026, 10, 12), 1.0, "Uisque_bourbon", datetime(2028, 5, 11)),

    ("LOTE-ING-133", "Angostura", datetime(2026, 10, 12), 1.0, "Angostura_bitters", datetime(2028, 5, 12)),

    ("LOTE-ING-134", "Bulleit", datetime(2026, 10, 12), 1.0, "Uisque_de_centeio_rye", datetime(2028, 5, 13)),

    ("LOTE-ING-135", "Luxardo", datetime(2026, 10, 12), 1.0, "Cereja_marasquino", datetime(2028, 5, 14)),

    # Outros itens

    ("LOTE-ING-136", "McCain", datetime(2026, 10, 12), 3.0, "Onion_rings", datetime(2028, 5, 15)),

    ("LOTE-ING-137", "Nestlé", datetime(2026, 10, 12), 2.0, "Brigadeiro", datetime(2028, 5, 16)),

    ("LOTE-ING-138", "Nestlé", datetime(2026, 10, 12), 2.0, "Beijinho", datetime(2028, 5, 17)),

    ("LOTE-ING-139", "Pullman", datetime(2026, 10, 12), 2.0, "Bolo_comum_simples", datetime(2028, 5, 18)),
    
    ("LOTE-ING-140", "Sadia", datetime(2026, 10, 12), 3.0, "Pastel_de_queijo", datetime(2028, 6, 20)),

    ("LOTE-ING-141", "Sadia", datetime(2026, 10, 12), 2.0, "Salame", datetime(2028, 7, 15)),
]

lista_cargos = [
    (1, "cliente"),
    (2, "chefe"),
    (3, "admin"),
]

# LISTA FICHA TECNICA
lista_ficha_tecnica = [

    # prato, ingrediente, quantidade
    # Mandioca frita
    ("Mandioca_frita", "Mandioca_in_natura", 0.077),
    ("Mandioca_frita", "Oleo_para_fritura", 0.005),
    ("Mandioca_frita", "Sal", 0.002),

    # Tábua de frios
    ("Tabua_de_frios", "Salame", 0.050),
    ("Tabua_de_frios", "Queijo_prato", 0.050),
    ("Tabua_de_frios", "Azeitona", 0.032),

    # Feijoada completa
    ("Feijoada_completa", "Feijao_preto", 0.133),
    ("Feijoada_completa", "Pe_de_porco", 0.020),
    ("Feijoada_completa", "Rabo_de_porco", 0.015),
    ("Feijoada_completa", "Costelinha_suina_defumada", 0.020),
    ("Feijoada_completa", "Bacon", 0.015),
    ("Feijoada_completa", "Linguica_calabresa", 0.020),
    ("Feijoada_completa", "Lombo_de_porco", 0.019),
    ("Feijoada_completa", "Temperos", 0.002),

    # Arroz branco
    ("Arroz_branco", "Arroz_branco", 0.132),

    # Couve refogada
    ("Couve_refogada", "Couve_manteiga", 0.040),
    ("Couve_refogada", "Alho", 0.002),
    ("Couve_refogada", "Azeite", 0.002),

    # Farofa
    ("Farofa", "Farinha_de_mandioca", 0.035),
    ("Farofa", "Manteiga", 0.008),
    ("Farofa", "Bacon", 0.008),
    ("Farofa", "Cebola", 0.004),

    # Vinagrete
    ("Vinagrete", "Tomate", 0.035),
    ("Vinagrete", "Cebola", 0.022),
    ("Vinagrete", "Pimentao", 0.018),
    ("Vinagrete", "Cebolinha", 0.004),
    ("Vinagrete", "Vinagre", 0.006),
    ("Vinagrete", "Azeite", 0.003),

    # Molho de pimenta
    ("Molho_de_pimenta", "Molho_de_pimenta", 0.022),

    
    ("Salada_fresca", "Folhas_hidroponicas", 0.090),
    ("Salada_fresca", "Tomate_cereja", 0.035),
    ("Salada_fresca", "Azeite", 0.007),

    # Bobó de camarão
    ("Bobo_de_camarao", "Camarao_medio_limpo", 0.123),
    ("Bobo_de_camarao", "Mandioca_in_natura", 0.108),
    ("Bobo_de_camarao", "Leite_de_coco", 0.046),
    ("Bobo_de_camarao", "Azeite_de_dende", 0.015),
    ("Bobo_de_camarao", "Temperos", 0.016),

    # Salada de frutas frescas com creme
    ("Salada_de_fruta_fresca_com_creme", "Frutas_frescas_in_natura", 0.095),
    ("Salada_de_fruta_fresca_com_creme", "Creme_de_leite", 0.040),
    ("Salada_de_fruta_fresca_com_creme", "Leite_condensado", 0.0225),

    # Bruschetta
    ("Bruschetta", "Pao_italiano", 0.090),
    ("Bruschetta", "Tomate", 0.025),
    ("Bruschetta", "Manjericao", 0.003),
    ("Bruschetta", "Azeite", 0.003),

    # Filé de tilápia
    ("File_de_tilapia", "File_de_tilapia", 0.198),

    # Molho de manteiga com alcaparras
    ("Molho_de_mateiga_com_alcaparras", "Manteiga", 0.025),
    ("Molho_de_mateiga_com_alcaparras", "Alcaparras", 0.010),
    ("Molho_de_mateiga_com_alcaparras", "Limao", 0.007),
    ("Molho_de_mateiga_com_alcaparras", "Salsinha", 0.002),

    # Iogurte natural com morangos e mel
    ("Iorgute_Natural_com_morangos_e_mel", "Iogurte_natural", 0.082),
    ("Iorgute_Natural_com_morangos_e_mel", "Morango_fresco", 0.041),
    ("Iorgute_Natural_com_morangos_e_mel", "Mel", 0.0135),

    # Salada Caesar
    ("Salada_ceaser", "Alface_romana", 0.070),
    ("Salada_ceaser", "Frango_grelhado", 0.035),
    ("Salada_ceaser", "Parmesao_ralado", 0.010),
    ("Salada_ceaser", "Molho_Caesar", 0.020),
    ("Salada_ceaser", "Croutons", 0.008),

    # Strogonoff de filé mignon
    ("Stogonoff_de_file_mignon", "File_mignon_bovino", 0.133),
    ("Stogonoff_de_file_mignon", "Creme_de_leite", 0.060),
    ("Stogonoff_de_file_mignon", "Champignon", 0.036),
    ("Stogonoff_de_file_mignon", "Catchup", 0.0065),
    ("Stogonoff_de_file_mignon", "Mostarda", 0.0065),
    ("Stogonoff_de_file_mignon", "Arroz_branco", 0.198),
    ("Stogonoff_de_file_mignon", "Batata_palha", 0.055),

    # Nhoque ao molho — versão bolonhesa
    ("Nhoque_ao_molho", "Nhoque_de_batata_pronto", 0.275),
    ("Nhoque_ao_molho", "Carne_moida_de_primeira", 0.099),
    ("Nhoque_ao_molho", "Molho_de_tomate", 0.110),
    ("Nhoque_ao_molho", "Temperos", 0.011),

    # Salada que acompanha o nhoque
    ("Nhoque_ao_molho", "Folhas_variadas", 0.075),
    ("Nhoque_ao_molho", "Tomate_cereja", 0.030),
    ("Nhoque_ao_molho", "Azeite", 0.005),

    # Mousse de maracujá
    ("Mousse_de_maracuja", "Suco_de_maracuja", 0.0385),
    ("Mousse_de_maracuja", "Leite_condensado", 0.044),
    ("Mousse_de_maracuja", "Creme_de_leite", 0.0385),
    ("Mousse_de_maracuja", "Gelatina", 0.00605),

    # Risoto de cogumelos com tiras de filé mignon
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Arroz_arborio", 0.158),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Cogumelos_frescos", 0.106),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Parmesao_ralado", 0.035),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Vinho_branco", 0.035),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Manteiga", 0.018),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "File_mignon_bovino", 0.165),

    # Brownie de chocolate
    ("Brownie_de_chocolate", "Chocolate_meio_amargo", 0.040),
    ("Brownie_de_chocolate", "Manteiga", 0.025),
    ("Brownie_de_chocolate", "Ovos", 0.5),
    ("Brownie_de_chocolate", "Nozes", 0.015),

    # Dadinho de tapioca
    ("Dadinho_de_tapioca", "Tapioca_granulada", 0.070),
    ("Dadinho_de_tapioca", "Queijo_coalho", 0.035),

    # Escondidinho de carne-seca com mandioca
    ("Escondidinho_de_carne_seca_com_mandioca", "Carne_seca", 0.207),
    ("Escondidinho_de_carne_seca_com_mandioca", "Mandioca_in_natura", 0.248),
    ("Escondidinho_de_carne_seca_com_mandioca", "Queijo_mucarela", 0.074),

    # Geleia de pimenta
    ("Geleia_de_pimenta", "Geleia_de_pimenta", 0.022),

    # Cheesecake de frutas vermelhas
    ("Cheesecake_de_frutas_vermelhas", "Cream_cheese", 0.055),
    ("Cheesecake_de_frutas_vermelhas", "Biscoito_base", 0.034),
    ("Cheesecake_de_frutas_vermelhas", "Frutas_vermelhas_congeladas", 0.048),

    # Ravioli de queijo ao molho bolonhesa
    ("Ravioli_de_queijo_ao_molho_bolanhesa", "Ravioli_fresco_de_queijo", 0.286),
    ("Ravioli_de_queijo_ao_molho_bolanhesa", "Carne_moida_de_primeira", 0.089),
    ("Ravioli_de_queijo_ao_molho_bolanhesa", "Molho_de_tomate", 0.099),
    ("Ravioli_de_queijo_ao_molho_bolanhesa", "Temperos", 0.010),
    ("Ravioli_de_queijo_ao_molho_bolanhesa", "Parmesao_ralado", 0.011),

    # Mousse de chocolate
    ("Mousse_de_chocolate", "Chocolate_meio_amargo", 0.046),
    ("Mousse_de_chocolate", "Creme_de_leite", 0.040),
    ("Mousse_de_chocolate", "Ovos", 0.5),


    # Sorvete
    ("Sorvete", "Leite_condensado", 0.055),
    ("Sorvete", "Creme_de_leite", 0.055),

    # Pudim
    ("Pudim_de_leite_condensado", "Leite_condensado", 0.110),
    ("Pudim_de_leite_condensado", "Leite_integral", 0.110),
    ("Pudim_de_leite_condensado", "Ovos", 1.1),
    ("Pudim_de_leite_condensado", "Acucar", 0.02),

    # Salgados
    ("Coxinha", "Coxinha", 3.3),
    ("Risole", "Risole", 3.3),
    ("Quibe", "Quibe", 3.3),
    ("Bolinha_de_queijo", "Bolinha_de_queijo", 3.3),
    ("Empada", "Empada", 3.3),
    ("Croquete", "Croquete", 3.3),

    # Batata frita.
    ("Batata_frita", "Batata", 0.220),
    ("Batata_frita", "Oleo_para_fritura", 0.0055),
    ("Batata_frita", "Sal", 0.0022),

    # Mesa de salgados
    ("Queijo", "Queijo_prato", 0.055),

    # Embutidos: estimativa de 50 g por pessoa + 10%.
    ("Embutido", "Salame", 0.055),

    # Pão: estimativa de 2 mini pães por pessoa + 10%.
    ("Pao", "Mini_paes", 2.2),

    # Doces: estimativa de 2 unidades por pessoa + 10%.
    ("Brigadeiro", "Brigadeiro", 2.2),
    ("Beijinho", "Beijinho", 2.2),

    # Bolo: estimativa de 100 g por pessoa + 10%.
    ("Bolo", "Bolo_comum_simples", 0.110),

    # Hambúrguer tradicional: quantidades do cardápio + 10%.
    ("Hamburguer_tradicional", "Pao_brioche", 1.1),
    ("Hamburguer_tradicional", "Carne_moida_blend_patinho_acem", 0.198),
    ("Hamburguer_tradicional", "Queijo_cheddar", 0.022),
    ("Hamburguer_tradicional", "Alface_americana", 0.0165),
    ("Hamburguer_tradicional", "Tomate", 0.022),
    ("Hamburguer_tradicional", "Cebola_caramelizada", 0.033),
    ("Hamburguer_tradicional", "Maionese_temperada", 0.0165),
    ("Hamburguer_tradicional", "Molho_barbecue", 0.0165),
    ("Hamburguer_tradicional", "Manteiga", 0.0055),
    ("Hamburguer_tradicional", "Batata", 0.220),
    ("Hamburguer_tradicional", "Molho_mostarda_e_mel", 0.0165),
    ("Hamburguer_tradicional", "Onion_rings", 0.110),

    # Hambúrguer smash: quantidades do cardápio + 10%.
    ("Hamburguer_smash", "Pao_brioche", 1.1),
    ("Hamburguer_smash", "Carne_moida_blend_patinho_acem", 0.099),
    ("Hamburguer_smash", "Queijo_prato", 0.0077),
    ("Hamburguer_smash", "Queijo_cheddar", 0.022),
    ("Hamburguer_smash", "Maionese_temperada", 0.0165),
    ("Hamburguer_smash", "Manteiga", 0.0055),
    ("Hamburguer_smash", "Cebola_caramelizada", 0.022),
    ("Hamburguer_smash", "Batata", 0.220),
    ("Hamburguer_smash", "Onion_rings", 0.110),

    # Hambúrguer mega bacon
    ("Hamburguer_mega_bacon", "Pao_brioche", 1.1),
    ("Hamburguer_mega_bacon", "Carne_moida_blend_patinho_acem", 0.396),
    ("Hamburguer_mega_bacon", "Bacon", 0.033),
    ("Hamburguer_mega_bacon", "Queijo_cheddar", 0.088),
    ("Hamburguer_mega_bacon", "Alface_americana", 0.0165),
    ("Hamburguer_mega_bacon", "Cebola_caramelizada", 0.0385),
    ("Hamburguer_mega_bacon", "Maionese_temperada", 0.022),
    ("Hamburguer_mega_bacon", "Molho_barbecue", 0.0165),
    ("Hamburguer_mega_bacon", "Manteiga", 0.0055),
    ("Hamburguer_mega_bacon", "Batata", 0.220),
    ("Hamburguer_mega_bacon", "Molho_mostarda_e_mel", 0.0165),
    ("Hamburguer_mega_bacon", "Onion_rings", 0.110),

    # Tortilha mexicana
    ("Tortilha_mexicana", "Tortilla_de_milho", 3.3),
    ("Tortilha_mexicana", "Carne_moida_de_primeira", 0.165),
    ("Tortilha_mexicana", "Alface_americana", 0.033),
    ("Tortilha_mexicana", "Tomate", 0.033),
    ("Tortilha_mexicana", "Queijo_ralado", 0.033),
    ("Tortilha_mexicana", "Nachos", 0.110),
    ("Tortilha_mexicana", "Guacamole", 0.055),
    ("Tortilha_mexicana", "Tortilla_de_trigo", 1.1),
    ("Tortilha_mexicana", "Frango_desfiado", 0.088),
    ("Tortilha_mexicana", "Pimentao", 0.022),

    # Pastel de carne: estimativa de 3 unidades + 10%.
    ("Pastel_de_carne", "Pastel_de_carne", 3.3),

    # Bolinho de bacalhau: estimativa de 3 unidades + 10%.
    ("Bolinho_de_bacalhau", "Bolinho_de_bacalhau", 3.3),

    # Linguiça acebolada:
    ("Liguica_acebolada", "Linguica_acebolada", 0.110),
    ("Liguica_acebolada", "Cebola", 0.033),


    #Pastel de queijo:

    ("Pastel_de_queijo", "Pastel_de_queijo", 3.3),
]


# ================================= Inicialização ESTOQUE ================================= 

def iniciar_servicos() -> list[Servico]:
    """Inicializa todos os serviços padrão que não constam no banco no momento da inicialização.

    Returns:
        list[Servico]: todos os objetos Servico a ser inicializados.
    """
    servicos=[]
    
    for nome, descricao in lista_servicos:
        if buscar_servico_por_nome(nome):
            continue
        
        servico = Servico(
            nome=nome,
            descricao=descricao
        )
        servicos.append(servico)
    
    return servicos

def iniciar_bancadas() -> list[Bancada]:
    """Inicializa todos as bancadas padrão que não constam no banco no momento da inicialização.
    
    Returns:
        list[Bancada]: todos os objetos Bancada a ser inicializados.
    """
        
    bancadas=[]
    
    for nome, descricao in lista_bancadas:
        if buscar_bancada_por_nome(nome):
            continue
        
        bancada = Bancada(
            nome=nome,
            descricao=descricao
        )
        bancadas.append(bancada)
    
    return bancadas

def iniciar_cardapios() -> list[Cardapio]:
    """Inicializa todos os cardápios padrão que não constam no banco no momento da inicialização.
    
    Returns:
        list[Cardapio]: todos os objetos Cardapio a ser inicializados.
    """
        
    cardapios=[]
    
    for tipo_cardapio in lista_cardapios:
        for nome, descricao, preco_base in tipo_cardapio:
            if buscar_cardapio_por_nome(nome):
                continue
            
            cardapio = Cardapio(
                nome=nome,
                descricao=descricao,
                preco_base=preco_base
            )
            cardapios.append(cardapio)
    
    return cardapios

def iniciar_pratos() -> list[Prato]:
    """Inicializa todos os pratos padrão que não constam no banco no momento da inicialização.

    Returns:
        list[Prato]: todos os objetos Prato a ser inicializados.
    """

    pratos=[]

    for nome, descricao, tipo_prato, tempo_preparo, requer_pre_preparo in lista_pratos:
        if buscar_prato_por_nome(nome):
            continue
        
        prato = Prato(
            nome=nome,
            descricao=descricao,
            tipo_prato=tipo_prato, 
            tempo_preparo=tempo_preparo, 
            requer_pre_preparo=requer_pre_preparo,
        )
        pratos.append(prato)

    return pratos

def iniciar_ingredientes() -> list[Ingrediente]:
    """Inicializa todos os ingredientes padrão que não constam no banco no momento da inicialização.
    
    Returns:
        list[Ingrediente]: todos os objetos Ingrediente a ser inicializados.
    """
        
    ingredientes=[]
    
    for tipo_ingrediente in lista_ingredientes:
        for nome, unidade, quantidade, quantidade_minima in tipo_ingrediente:
            if buscar_ingrediente_por_nome(nome):
                continue
            
            ingrediente = Ingrediente(
                nome,
                unidade,
                quantidade,
                quantidade_minima,
            )
            ingredientes.append(ingrediente)
    
    return ingredientes

def iniciar_lotes() -> list[Lote]:
    """Inicializa todos os lotes padrão que não constam no banco no momento da inicialização.
    
    Returns:
        list[Lote]: todos os objetos lote a ser inicializados.
    """
        
    lotes=[]
    
    for numero, marca, data_recebimento, quantidade_inicial, nome_ingrediente, data_validade in lista_lotes:
        if buscar_lote_por_numero(numero):
            continue
        
        lote = Lote(
            numero,
            marca,
            data_recebimento,
            data_validade,
            quantidade_inicial,
            buscar_ingrediente_por_nome(nome_ingrediente).id
        )
        lotes.append(lote)
    
    return lotes

# ================================== Inicialização CARGOS ================================== 

def iniciar_cargos() -> list[NivelPermissao]:
    """Inicializa todos os cargos padrão que não constam no banco no momento da inicialização e 
    corrige seus ids caso estejam em divergência.

    Returns:
        list[NivelPermissao]: todos os objetos nivelPermissao a ser inicializados.
    """

    cargos=[]

    for id_cargo, nome in lista_cargos:
        cargo = buscar_permissao_por_nome(nome)
    
        if cargo:
            cargo_valido = (
                cargo.id_permissao in Cargo._value2member_map_
                and cargo.nome.upper() in Cargo.__members__
            )
    
            if not cargo_valido:
                cargo=atualizar_permissao(id_cargo, nome.lower())
        cargos.append(cargo)
        
    return cargos
# ================================== Inicialização FICHA TECNICA ================================== 

def iniciar_ficha_tecnica() -> list[FichaTecnica]:
    """Inicializa todas as fichas técnicas padrão que não constam no banco no momento da inicialização.

    Returns:
        list[FichaTecnica]: todos os objetos FichaTecnica a serem inicializados.
    """

    fichas_tecnicas = []

    for nome_prato, nome_ingrediente, qtd_necessaria in lista_ficha_tecnica:
        prato = buscar_prato_por_nome(nome_prato)
        ingrediente = buscar_ingrediente_por_nome(nome_ingrediente)

        if not prato or not ingrediente:
            continue

        if db.session.get(
            FichaTecnica,
            (prato.id_prato, ingrediente.id_ingrediente)
        ):
            continue

        ficha = FichaTecnica(
            prato.id_prato,
            ingrediente.id_ingrediente,
            qtd_necessaria
        )

        fichas_tecnicas.append(ficha)

    return fichas_tecnicas