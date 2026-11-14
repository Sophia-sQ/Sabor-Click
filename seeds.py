"""Armazena todos os valores padrão do banco de dados"""

from datetime import datetime, time

from database import db


# ================================= Import ESTOQUE =================================

from model.pedido_model import Bebida, BebidaCardapio

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
from model.usuario_model import NivelPermissao, Usuario, Endereco, LogAtividade, Token
from model.usuario_model import buscar_permissao_por_nome, atualizar_permissao
from model.pedido_model import buscar_bebida_por_nome
from model.pedido_model import Pedido, PedidoBebida, CardapioPedido
from model.servico_model import ServicoBancada, ServicoCardapio
from model.ficha_model import FichaTecnica, FichaTecnica_bebida, PratoCardapio

from utils import moeda_para_centavos, formatar_moeda, formatar_nome

# ================================= "Tabelas" ESTOQUE =================================

#nome, descrição
lista_servicos = [
    ("Chef_em_casa", "Prepara a refeição em pequenas comemorações e em ambiente domiciliar."),
    ("Buffet", "Prepara o ambiente para grandes comemorações que envolvam pratos quentes."),
    ("Bar", "Prepara bebidas escolhidas pelo cliente no balcão."),
    ("Mesa_de_salgados", "Organiza os salgados para festas."),
]

#nome, descrição
lista_bancadas = [
    ("Rechauds", "Equipamento que mantem o alimento quente"),
    ("Kit_loucas", "Kit que contem o basico de mesa posta: Talheres, pratos e guardanapo de pano"),
    ("Chapa_hamburguer_portatil", "Equipamento utilizado para confeccao de lanches"),
    ("Bancada_bar_portatil", "Equipamento que organiza e prepara as bebidas"),
    ("Maquina_de_gelo", "Equipamento responsavel por fazer gelo"),
    ("Limpeza", "Equipamentos responsaveis pela limpeza final no evento"),
    ("Fritadeira", "Equipamento para fritar salgados")
]

#nome servico, nome bancada
lista_servicos_bancadas = [
    ("Chef_em_casa", "Kit_loucas"),
    ("Chef_em_casa","Limpeza"),
    ("Chef_em_casa","Maquina_de_gelo"),
    ("Buffet","Rechauds"),
    ("Buffet","Kit_loucas"),
    ("Buffet","Maquina_de_gelo"),
    ("Buffet","Limpeza"),
    ("Bar","Kit_loucas"),
    ("Bar"," Bancada_bar_portatil"),
    ("Bar","Maquina_de_gelo"),
    ("Bar","Limpeza"),
    ("Mesa_de_salgados","Kit_loucas"),
    ("Mesa_de_salgados","Fritadeira"),
    ("Mesa_de_salgados","Chapa_hamburguer_portatil"),
    ("Mesa_de_salgados","Limpeza")
    


]

#nome, descrição, preco base
cardapios_quentes = [
    ("Feijoada_completa", "Feijoada com arroz branco, couve refogada, farofa, vinagrete e molho de pimenta. Acompanha tábua de frios e mandioca frita. Sobremesa incluída: sorvete de maracujá e limão.", 14990),
    ("Bobo_de_camarao ", "Bobó de camarão com arroz branco e salada fresca. Sobremesa incluída: salada de frutas com creme.", 13990),
    ("File_de_tilapia_ao_molho_manteiga_e_alcaparras ", "Filé de tilápia ao molho de manteiga e alcaparras, com arroz branco e bruschetta. Sobremesa incluída: iogurte natural com morangos e mel.", 12990),
    ("Strogonoff_de_file_Mignon ", "Strogonoff de filé-mignon com arroz branco, batata palha e salada Caesar. Sobremesa incluída: pudim de leite condensado.", 12990),
    ("Nhoque_ao_molho", "Nhoque ao molho bolonhesa ou de queijo, acompanhado de mix de folhas. Sobremesa incluída: mousse de maracujá.", 11990),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Risoto de cogumelos com tiras de filé-mignon e bruschetta. Sobremesa incluída: brownie de chocolate.", 13990),
    ("Escondinho_de_carne_seca_com_mandioca ", "Escondidinho de carne-seca com purê de mandioca, acompanhado de dadinhos de tapioca e geleia de pimenta. Sobremesa incluída: cheesecake de frutas vermelhas.", 12990),
    ("Raviolli_de_queijo_ao_molho_bolonhesa ", "Ravioli de queijo ao molho bolonhesa, com parmesão ralado e tábua de frios. Sobremesa incluída: mousse de chocolate.", 12990),
]

#nome, descrição, preco base
cardapios_salgados = [
    ("Salgados_completo ", "Coxinha, risole, quibe, bolinha de queijo, empada e croquete, com batata frita, queijo, embutidos e pães. Doces incluídos: brigadeiro, beijinho e bolo.", 12990),
    ("Salgados_Reduzido", "Coxinha, risole e bolinha de queijo, com batata frita, queijo e presunto. Doces incluídos: brigadeiro e bolo simples.", 9990),
    ("Hamburguer_tradicional ", "Pão brioche, carne bovina, cheddar, alface, tomate, cebola caramelizada, maionese temperada e barbecue. Acompanha batata frita, molho mostarda e mel e onion rings.", 7990),
    ("Hamburguer_smash ", "Pão brioche, blend de carnes, queijo picado, cheddar, maionese temperada, manteiga e cebola caramelizada. Acompanha batata frita e onion rings.", 8990),
    ("Hamburguer_mega_bacon ", "Pão brioche, carne bovina, quatro fatias de cheddar, alface, cebola caramelizada, maionese temperada e barbecue. Acompanha batata frita, molho mostarda e mel e onion rings.", 9990),
    ("Mexicano ", "Tortillas de milho com carne moída temperada, alface, tomate e queijo ralado. Acompanha nachos, guacamole e quesadilla com tortilla de trigo, frango ou queijo e pimentão.", 8990),
    ("Boteco_brasileiro", "Coxinha, pastel de carne, bolinho de bacalhau, linguiça acebolada, batata palha e pastel de queijo. Sobremesa incluída: iogurte natural com morangos e mel.", 6990),
]

#nome, descrição, preco base
cardapios_bebidas = [
    ("Bebida_sem_alcool", "Uma seleção de sucos, refrigerantes, águas e bebidas sem álcool.", 16990),
    ("Bebida_com_alcool", "Uma seleção de bebidas alcoólicas e coquetéis para o evento.", 18990),
    ("Bebida_mista", "Opções com e sem álcool para diferentes preferências.", 17990),
]

# nome, descrição, preço base
lista_cardapios = [
    cardapios_quentes,
    cardapios_salgados,
    cardapios_bebidas
]

#nome servico, nome cardapios
lista_servicos_cardapios = [
    # SERVIÇO CHEF EM CASA - PRATOS QUENTES
    ("Chef_em_casa", "Feijoada_completa"),
    ("Chef_em_casa", "Bobo_de_camarao"),
    ("Chef_em_casa", "File_de_tilapia_ao_molho_manteiga_e_alcaparras"),
    ("Chef_em_casa", "Strogonoff_de_file_Mignon"),
    ("Chef_em_casa", "Nhoque_ao_molho"),
    ("Chef_em_casa", "Risoto_de_cogumelos_com_tiras_de_file_mignon"),
    ("Chef_em_casa", "Escondinho_de_carne_seca_com_mandioca"),
    ("Chef_em_casa", "Raviolli_de_queijo_ao_molho_bolonhesa"),

    # SERVIÇO BUFFET - PRATOS QUENTES
    ("Buffet", "Feijoada_completa"),
    ("Buffet", "Bobo_de_camarao"),
    ("Buffet", "File_de_tilapia_ao_molho_manteiga_e_alcaparras"),
    ("Buffet", "Strogonoff_de_file_Mignon"),
    ("Buffet", "Nhoque_ao_molho"),
    ("Buffet", "Risoto_de_cogumelos_com_tiras_de_file_mignon"),
    ("Buffet", "Escondinho_de_carne_seca_com_mandioca"),
    ("Buffet", "Raviolli_de_queijo_ao_molho_bolonhesa"),

    # SERVIÇO BAR - BEBIDAS
    ("Bar", "Bebida_sem_alcool"),
    ("Bar", "Bebida_com_alcool"),
    ("Bar", "Bebida_mista"),

    # SERVIÇO MESA DE SALGADOS - CARDÁPIOS DE SALGADOS
    ("Mesa_de_salgados", "Salgados_completo"),
    ("Mesa_de_salgados", "Salgados_Reduzido"),
    ("Mesa_de_salgados", "Hamburguer_tradicional"),
    ("Mesa_de_salgados", "Hamburguer_smash"),
    ("Mesa_de_salgados", "Hamburguer_mega_bacon"),
    ("Mesa_de_salgados", "Mexicano"),
    ("Mesa_de_salgados", "Boteco_brasileiro"),
]

#nome, descrição, tipo, tempo preparo (em min), requer pre preparo
lista_pratos = [
    ("Mandioca_frita", "Pedacos de mandioca frita em oleo", "entrada", 40, True), #requer-preparo, pois tem que levar ela cozida e fritar no local,
    ("Tabua_de_frios", "Tabua contendo aperitivos: Salame, queijo, azeitona", "entrada", 15, False),
    ("Feijoada_completa", "Feijoada", "prato principal", 120, True),
    ("Arroz_branco", "Arroz cozido", "acompanhamento", 20, False),
    ("Couve_refogada", "Couve picada refogada", "acompanhamento", 10, False), # A colve comprada é picada ja,
    ("Farofa", "Farofa comprada", "acompanhamento", 0, False),
    ("Vinagrete", "Vinagrete completo: Ceblo, tomate, pimentao,cebolinha,vinagre", "acompanhamento", 15, True), #Levar cortado as coisas, e temperar no local,
    ("Molho_de_pimenta", "Molho de pimenta pronto", "acompanhamento", 0, False),
    ("Sorvete", "Sorvete comprado de maracuja e limao", "sobremesa", 0, False),
    ("Salada_fresca", "Salada de folhas hidroponicas e tomate cereja", "entrada", 5, True), #Lavar antes,
    ("Bobo_de_camarao", "Bobo de camarao completo", "prato principal", 120, True),
    ("Salada_de_fruta_fresca_com_creme", "Salada de frutas com creme de leite e leite condensado", "sobremesa", 0, False),
    ("Bruschetta", "Bruscretta de pao italiano, tomate e manjericao", "entrada", 5, False),
    ("File_de_tilapia", "File de tilapia grelhado", "prato principal", 30, True), #Limpar o file de tilapia,
    ("Molho_de_mateiga_com_alcaparras", "Molho de acompanhamento de manteiga e alcaparras", "acompanhamento", 10, False),
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

#Nome, descrição, preco base (0 quando em cardapio) 
lista_bebida = [
    #BEBIDAS DE ESCOLHA SEM SER DO BAR 
    ('Agua_com_gas','Agua_com_gas', 7),
    ('Suco_de_abacaxi','Suco_de_abacaxi', 15),
    ('Refrigerante_de_guarana','Refrigerante_de_guarana', 10),
    ('Cha_preto','Cha_preto',7),
    ('Agua_de_coco','Agua_de_coco', 12),
    ('Suco_de_melancia','Suco_de_melancia',15),
    ('Gin','Gin', 17),
    ('Uisque_de_centeio_rye','Uisque_de_centeio_rye',20),
    #SEM ALCOOL - BAR
    ("Pink Lemonade", "Bebida sem álcool feita com suco de limão-siciliano, xarope de groselha ou framboesa, água com gás, gelo e suco de limão-tahiti.", 0),
    ("Mojito Sem Álcool", "Bebida sem álcool preparada com folhas de hortelã, xarope simples de açúcar, água com gás e gelo.", 0),
    ("Piña Colada Zero", "Bebida sem álcool feita com suco de abacaxi, leite de coco, leite condensado e gelo triturado.", 0),
    ("Soda Italiana de Maçã Verde", "Bebida sem álcool preparada com xarope de maçã verde, água com gás, suco de limão e gelo.", 0),
    ("Coquetel de Frutas Vermelhas", "Bebida sem álcool feita com polpa ou purê de frutas vermelhas, suco de laranja, refrigerante de guaraná ou soda e gelo.", 0),
    ("Iced Tea de Pêssego e Limão", "Bebida sem álcool preparada com chá preto gelado, xarope ou suco concentrado de pêssego, suco de limão e gelo.", 0),
    ("Sunrise de Laranja e Grenadine", "Bebida sem álcool feita com suco de laranja natural e xarope de grenadine ou groselha.", 0),
    ("Coquetel Tropical de Coco", "Bebida sem álcool preparada com água de coco, suco de maracujá, xarope de baunilha e gelo.", 0),
    ("Lemonade de Extrato de Manjericão", "Bebida sem álcool feita com suco de limão-tahiti, folhas frescas de manjericão, xarope de açúcar e água filtrada gelada.", 0),
    ("Refresco de Melancia e Gengibre", "Bebida sem álcool preparada com suco de melancia fresco, suco de gengibre, açúcar e gelo picado.", 0),
    # COM ALCOOL - BAR
    ("Caipirinha", "Drink alcoólico preparado com cachaça, limão e gelo.", 0),
    ("Margarita", "Drink alcoólico feito com tequila, Cointreau, suco de limão, sal e gelo.", 0),
    ("Negroni", "Drink alcoólico preparado com gin, Campari, vermute tinto, gelo e casca de laranja.", 0),
    ("Moscow Mule", "Drink alcoólico feito com vodka, suco de limão, ginger beer, gelo e rodela de limão.", 0),
    ("Cosmopolitan", "Drink alcoólico preparado com vodka, Cointreau, suco de cranberry, suco de limão e gelo.", 0),
    ("Mai Tai", "Drink alcoólico feito com rum branco, rum escuro, Cointreau, xarope de amêndoa e suco de limão.", 0),
    ("Old Fashioned", "Drink alcoólico preparado com uísque bourbon, açúcar, Angostura bitters, gelo e casca de laranja.", 0),
    ("Manhattan", "Drink alcoólico feito com uísque de centeio, vermute tinto, Angostura bitters, gelo e cereja marasquino.", 0),
    ("Piña Colada", "Drink alcoólico preparado com rum branco, suco de abacaxi, leite de coco e gelo.", 0)
]

#nome, unidade, qtd, qtd min
ingredientes_carnes = [
        ('Pe_de_porco', 'g', 6000, 1500),
        ('Rabo_de_porco', 'g', 4500, 900),
        ('Costelinha_suina_defumada', 'g', 6000, 1500),
        ('Bacon', 'g', 10000, 2000),
        ('Linguica_calabresa', 'g', 6000, 1500),
        ('Linguica_acebolada', 'g', 33000, 7000),
        ('Lombo_de_porco', 'g', 6000, 1500),
        ('Carne_seca', 'g', 63000, 13000),
        ('Camarao_medio_limpo', 'g', 37000, 7500),
        ('File_de_tilapia', 'g', 60000, 12000),
        ('File_mignon_bovino', 'g', 50000, 10000),
        ('Carne_moida_de_primeira', 'g', 50000, 10000),
        ('Carne_moida_blend_patinho_acem', 'g', 120000, 24000),
        ('Frango_grelhado', 'g', 11000, 2500),
        ('Frango_desfiado', 'g', 27000, 5500),
        ('Presunto', 'g', 2000, 400),
        ('Bolinho_de_bacalhau', 'g', 50000, 10000),
        ('Salame', 'g', 17000, 3500),
]

#nome, unidade, qtd, qtd min
ingredientes_carboidratos = [
        ('Feijao_preto', 'g', 40000, 8000),
        ('Arroz_branco', 'g', 90000, 18000),
        ('Arroz_arborio', 'g', 48000, 10000),
        ('Mandioca_in_natura', 'g', 75000, 15000),
        ('Farinha_de_mandioca', 'g', 11000, 2500),
        ('Batata', 'g', 66000, 14000),
        ('Batata_palha', 'g', 17000, 3500),
        ('Nhoque_de_batata_pronto', 'g', 83000, 17000),
        ('Ravioli_fresco_de_queijo', 'g', 86000, 18000),
        ('Pao_italiano', 'g', 27000, 5500),
        ('Pao_brioche', 'unidade', 300, 60),
        ('Pao_de_forma', 'unidade', 100, 20),
        ('Mini_paes', 'unidade', 600, 150),
        ('Tortilla_de_milho', 'unidade', 900, 200),
        ('Tortilla_de_trigo', 'unidade', 300, 60),
        ('Tapioca_granulada', 'g', 21000, 4500),
        ('Nachos', 'g', 33000, 7000),
        ('Biscoito_base', 'g', 11000, 2500),
        ('Coxinha', 'unidade', 900, 200),
        ('Risole', 'unidade', 900, 200),
        ('Quibe', 'unidade', 900, 200),
        ('Croquete', 'unidade', 900, 200),
        ('Empada', 'unidade', 900, 200),
        ('Bolinha_de_queijo', 'unidade', 900, 200),
        ('Pastel_de_carne', 'unidade', 900, 200),
        ('Pastel_de_queijo', 'unidade', 900, 200),
]

#nome, unidade, qtd, qtd min
ingredientes_laticinios = [
        ('Manteiga', 'g', 15000, 3000),
        ('Queijo_mucarela', 'g', 23000, 5000),
        ('Queijo_prato', 'g', 17000, 3500),
        ('Queijo_cheddar', 'g', 27000, 5500),
        ('Queijo_coalho', 'g', 11000, 2500),
        ('Queijo_ralado', 'g', 10000, 2000),
        ('Parmesao_ralado', 'g', 11000, 2500),
        ('Creme_de_leite', 'ml', 18000, 4000),
        ('Leite_condensado', 'ml', 33000, 7000),
        ('Leite_integral', 'ml', 33000, 7000),
        ('Leite_de_coco', 'ml', 14000, 3000),
        ('Iogurte_natural', 'ml', 25000, 5000),
        ('Cream_cheese', 'g', 17000, 3500),
        ('Ovos', 'unidade', 300, 60),
]

#nome, unidade, qtd, qtd min
ingredientes_vegetais = [
        ('Folhas_hidroponicas', 'g', 27000, 5500),
        ('Folhas_variadas', 'g', 23000, 5000),
        ('Alface_romana', 'unidade', 100, 20),
        ('Alface_americana', 'unidade', 100, 20),
        ('Couve_manteiga', 'g', 12000, 2500),
        ('Tomate', 'g', 11000, 2500),
        ('Tomate_cereja', 'g', 20000, 4000),
        ('Cebola', 'g', 10000, 2000),
        ('Cebola_caramelizada', 'g', 12000, 2500),
        ('Pimentao', 'g', 7000, 1500),
        ('Cebolinha', 'g', 2000, 400),
        ('Alho', 'g', 2000, 400),
        ('Manjericao', 'g', 2000, 400),
        ('Salsinha', 'g', 2000, 400),
        ('Limao', 'g', 4000, 800),
        ('Laranja', 'g', 2000, 400),
        ('Cogumelos_frescos', 'g', 32000, 6500),
        ('Champignon', 'g', 11000, 2500),
        ('Morango_fresco', 'g', 13000, 3000),
        ('Frutas_frescas_in_natura', 'g', 29000, 6000),
        ('Frutas_vermelhas_congeladas', 'g', 15000, 3000),
        ('Nozes', 'g', 4500, 900),    
]

#nome, unidade, qtd, qtd min
ingredientes_temperos = [
    ('Oleo_de_soja', 'ml', 2000, 400),
    ('Oleo_para_fritura', 'ml', 2000, 400),
    ('Sal', 'g', 2000, 400),
    ('Acucar', 'g', 6000, 1500),
    ('Temperos', 'g', 5000, 1000),
    ('Vinagre', 'ml', 2000, 400),
    ('Azeite', 'ml', 2500, 500),
    ('Azeite_de_dende', 'ml', 4500, 900),
    ('Molho_de_pimenta', 'ml', 7000, 1500),
    ('Geleia_de_pimenta', 'g', 7000, 1500),
    ('Alcaparras', 'g', 3000, 600),
    ('Molho_de_tomate', 'ml', 33000, 7000),
    ('Catchup', 'ml', 2000, 400),
    ('Mostarda', 'ml', 2000, 400),
    ('Molho_mostarda_e_mel', 'ml', 5000, 1000),
    ('Molho_Caesar', 'ml', 6000, 1500),
    ('Croutons', 'g', 2500, 500),
    ('Maionese_temperada', 'ml', 7000, 1500),
    ('Molho_barbecue', 'ml', 5000, 1000),
    ('Vinho_branco', 'ml', 11000, 2500),
    ('Guacamole', 'g', 17000, 3500),
    ('Gelatina', 'g', 2000, 400),
    ('Chocolate_meio_amargo', 'g', 14000, 3000),
    ('Mel', 'g', 4500, 900),
    ('Azeitona', 'g', 10000, 2000),
    ('Folha_de_hortela', 'unidade', 750, 150),
]

#nome, unidade, qtd, qtd min
ingredientes_bebidas_sem_alcool = [
        ('Suco_de_limao', 'ml', 4000, 800),
        ('Xarope_de_groselha_framboesa', 'ml', 2000, 400),
        ('Agua_com_gas', 'ml', 15000, 3000),
        ('Xarope_simples_de_acucar', 'ml', 2000, 400),
        ('Suco_de_abacaxi', 'ml', 15000, 3000),
        ('Xarope_de_maca_verde', 'ml', 2500, 500),
        ('Polpa_de_frutas_vermelhas', 'g', 4000, 800),
        ('Suco_de_laranja', 'ml', 14000, 3000),
        ('Refrigerante_de_guarana', 'ml', 15000, 3000),
        ('Cha_preto', 'ml', 15000, 3000),
        ('Xarope_de_pessego', 'ml', 3000, 600),
        ('Xarope_de_grenadine', 'ml', 2000, 400),
        ('Agua_de_coco', 'ml', 15000, 3000),
        ('Suco_de_maracuja', 'ml', 12000, 2500),
        ('Xarope_de baunilha', 'ml', 2000, 400),
        ('Suco_de_melancia', 'ml', 15000, 3000),
        ('Suco_de_gengibre', 'ml', 2000, 400),
]

#nome, unidade, qtd, qtd min
ingredientes_bebidas_alcoolicas = [
        ('Cachaca', 'ml', 4000, 800),
        ('Tequila', 'ml', 4000, 800),
        ('Cointreau_triple_sec', 'ml', 2000, 400),
        ('Gin', 'ml', 5500, 1500),
        ('Campari', 'ml', 2500, 500),
        ('Vermute_tinto', 'ml', 2500, 500),
        ('Vodka', 'ml', 4000, 800),
        ('Ginger_beer', 'ml', 9000, 2000),
        ('Suco_de_cranberry', 'ml', 2500, 500),
        ('Rum_branco', 'ml', 4000, 800),
        ('Rum_escuro', 'ml', 2000, 400),
        ('Xarope_de_amendoa_orgeat', 'ml', 2000, 400),
        ('Uisque_bourbon', 'ml', 4500, 900),
        ('Angostura_bitters', 'ml', 2000, 400),
        ('Uisque_de_centeio_rye', 'ml', 5500, 1500),
        ('Cereja_marasquino', 'g', 2000, 400),
]

#nome, unidade, qtd, qtd min
ingredientes_diversos = [
        ('Onion_rings', 'g', 33000, 7000),
        ('Brigadeiro', 'unidade', 600, 150),
        ('Beijinho', 'unidade', 600, 150),
        ('Bolo_comum_simples', 'g', 33000, 7000),
]

# nome, unidade de medida, estoque atual, estoque minimo
lista_ingredientes = [
    ingredientes_carnes,
    ingredientes_carboidratos,
    ingredientes_laticinios,
    ingredientes_vegetais,
    ingredientes_temperos,
    ingredientes_bebidas_sem_alcool,
    ingredientes_bebidas_alcoolicas,
    ingredientes_diversos,
]

# código, fornecedor, data_entrada, quantidade, nome_ingrediente, data_validade
lista_lotes = [

    ("LOTE-ING-001", "Pamplona", datetime(2026, 10, 12), 6000, "Pe_de_porco", datetime(2028, 1, 1)),

    ("LOTE-ING-002", "Pamplona", datetime(2026, 10, 12), 4500, "Rabo_de_porco", datetime(2028, 1, 2)),

    ("LOTE-ING-003", "Seara", datetime(2026, 10, 12), 6000, "Costelinha_suina_defumada", datetime(2028, 1, 3)),

    ("LOTE-ING-004", "Sadia", datetime(2026, 10, 12), 10000, "Bacon", datetime(2028, 1, 4)),

    ("LOTE-ING-005", "Perdigão", datetime(2026, 10, 12), 6000, "Linguica_calabresa", datetime(2028, 1, 5)),

    ("LOTE-ING-006", "Aurora", datetime(2026, 10, 12), 33000, "Linguica_acebolada", datetime(2028, 1, 6)),

    ("LOTE-ING-007", "Sadia", datetime(2026, 10, 12), 6000, "Lombo_de_porco", datetime(2028, 1, 7)),

    ("LOTE-ING-008", "Friboi", datetime(2026, 10, 12), 63000, "Carne_seca", datetime(2028, 1, 8)),

    ("LOTE-ING-009", "Copacol", datetime(2026, 10, 12), 37000, "Camarao_medio_limpo", datetime(2028, 1, 9)),

    ("LOTE-ING-010", "Copacol", datetime(2026, 10, 12), 60000, "File_de_tilapia", datetime(2028, 1, 10)),

    ("LOTE-ING-011", "Friboi", datetime(2026, 10, 12), 50000, "File_mignon_bovino", datetime(2028, 1, 11)),

    ("LOTE-ING-012", "Friboi", datetime(2026, 10, 12), 50000, "Carne_moida_de_primeira", datetime(2028, 1, 12)),

    ("LOTE-ING-013", "Swift", datetime(2026, 10, 12), 120000, "Carne_moida_blend_patinho_acem", datetime(2028, 1, 13)),

    ("LOTE-ING-014", "Sadia", datetime(2026, 10, 12), 11000, "Frango_grelhado", datetime(2028, 1, 14)),

    ("LOTE-ING-015", "Seara", datetime(2026, 10, 12), 27000, "Frango_desfiado", datetime(2028, 1, 15)),

    ("LOTE-ING-016", "Sadia", datetime(2026, 10, 12), 2000, "Presunto", datetime(2028, 1, 16)),

    ("LOTE-ING-017", "Copacol", datetime(2026, 10, 12), 50000, "Bolinho_de_bacalhau", datetime(2028, 1, 17)),

    # Grãos, massas, pães e salgados

    ("LOTE-ING-018", "Camil", datetime(2026, 10, 12), 40000, "Feijao_preto", datetime(2028, 1, 18)),

    ("LOTE-ING-019", "Camil", datetime(2026, 10, 12), 90000, "Arroz_branco", datetime(2028, 1, 19)),

    ("LOTE-ING-020", "Tio João", datetime(2026, 10, 12), 48000, "Arroz_arborio", datetime(2028, 1, 20)),

    ("LOTE-ING-021", "De Marchi", datetime(2026, 10, 12), 75000, "Mandioca_in_natura", datetime(2028, 1, 21)),

    ("LOTE-ING-022", "Yoki", datetime(2026, 10, 12), 11000, "Farinha_de_mandioca", datetime(2028, 1, 22)),

    ("LOTE-ING-023", "Bem Brasil", datetime(2026, 10, 12), 66000, "Batata", datetime(2028, 1, 23)),

    ("LOTE-ING-024", "Yoki", datetime(2026, 10, 12), 17000, "Batata_palha", datetime(2028, 1, 24)),

    ("LOTE-ING-025", "Nico", datetime(2026, 10, 12), 83000, "Nhoque_de_batata_pronto", datetime(2028, 1, 25)),

    ("LOTE-ING-026", "Massa Leve", datetime(2026, 10, 12), 86000, "Ravioli_fresco_de_queijo", datetime(2028, 1, 26)),

    ("LOTE-ING-027", "Wickbold", datetime(2026, 10, 12), 27000, "Pao_italiano", datetime(2028, 1, 27)),

    ("LOTE-ING-028", "Pullman", datetime(2026, 10, 12), 300, "Pao_brioche", datetime(2028, 1, 28)),

    ("LOTE-ING-029", "Wickbold", datetime(2026, 10, 12), 100, "Pao_de_forma", datetime(2028, 1, 29)),

    ("LOTE-ING-030", "Seven Boys", datetime(2026, 10, 12), 600, "Mini_paes", datetime(2028, 1, 30)),

    ("LOTE-ING-031", "Rap10", datetime(2026, 10, 12), 900, "Tortilla_de_milho", datetime(2028, 1, 31)),

    ("LOTE-ING-032", "Rap10", datetime(2026, 10, 12), 300, "Tortilla_de_trigo", datetime(2028, 2, 1)),

    ("LOTE-ING-033", "Yoki", datetime(2026, 10, 12), 21000, "Tapioca_granulada", datetime(2028, 2, 2)),

    ("LOTE-ING-034", "Doritos", datetime(2026, 10, 12), 33000, "Nachos", datetime(2028, 2, 3)),

    ("LOTE-ING-035", "Marilan", datetime(2026, 10, 12), 11000, "Biscoito_base", datetime(2028, 2, 4)),

    ("LOTE-ING-036", "Seara", datetime(2026, 10, 12), 900, "Coxinha", datetime(2028, 2, 5)),

    ("LOTE-ING-037", "Seara", datetime(2026, 10, 12), 900, "Risole", datetime(2028, 2, 6)),

    ("LOTE-ING-038", "Seara", datetime(2026, 10, 12), 900, "Quibe", datetime(2028, 2, 7)),

    ("LOTE-ING-039", "Seara", datetime(2026, 10, 12), 900, "Croquete", datetime(2028, 2, 8)),

    ("LOTE-ING-040", "Forno de Minas", datetime(2026, 10, 12), 900, "Empada", datetime(2028, 2, 9)),

    ("LOTE-ING-041", "Seara", datetime(2026, 10, 12), 900, "Bolinha_de_queijo", datetime(2028, 2, 10)),

    ("LOTE-ING-042", "Aurora", datetime(2026, 10, 12), 900, "Pastel_de_carne", datetime(2028, 2, 11)),

    # Laticínios e ovos

    ("LOTE-ING-043", "Qualy", datetime(2026, 10, 12), 15000, "Manteiga", datetime(2028, 2, 12)),

    ("LOTE-ING-044", "Tirolez", datetime(2026, 10, 12), 23000, "Queijo_mucarela", datetime(2028, 2, 13)),

    ("LOTE-ING-045", "President", datetime(2026, 10, 12), 17000, "Queijo_prato", datetime(2028, 2, 14)),

    ("LOTE-ING-046", "Polenghi", datetime(2026, 10, 12), 27000, "Queijo_cheddar", datetime(2028, 2, 15)),

    ("LOTE-ING-047", "Tirolez", datetime(2026, 10, 12), 11000, "Queijo_coalho", datetime(2028, 2, 16)),

    ("LOTE-ING-048", "Vigor", datetime(2026, 10, 12), 10000, "Queijo_ralado", datetime(2028, 2, 17)),

    ("LOTE-ING-049", "Faixa Azul", datetime(2026, 10, 12), 11000, "Parmesao_ralado", datetime(2028, 2, 18)),

    ("LOTE-ING-050", "Nestlé", datetime(2026, 10, 12), 18000, "Creme_de_leite", datetime(2028, 2, 19)),

    ("LOTE-ING-051", "Moça", datetime(2026, 10, 12), 33000, "Leite_condensado", datetime(2028, 2, 20)),

    ("LOTE-ING-052", "Italac", datetime(2026, 10, 12), 33000, "Leite_integral", datetime(2028, 2, 21)),

    ("LOTE-ING-053", "Sococo", datetime(2026, 10, 12), 14000, "Leite_de_coco", datetime(2028, 2, 22)),

    ("LOTE-ING-054", "Nestlé", datetime(2026, 10, 12), 25000, "Iogurte_natural", datetime(2028, 2, 23)),

    ("LOTE-ING-055", "Philadelphia", datetime(2026, 10, 12), 17000, "Cream_cheese", datetime(2028, 2, 24)),

    ("LOTE-ING-056", "Mantiqueira", datetime(2026, 10, 12), 300, "Ovos", datetime(2028, 2, 25)),

    # Verduras, legumes, frutas e cogumelos

    ("LOTE-ING-057", "Fazenda local", datetime(2026, 10, 12), 27000, "Folhas_hidroponicas", datetime(2028, 2, 26)),

    ("LOTE-ING-058", "Fazenda local", datetime(2026, 10, 12), 23000, "Folhas_variadas", datetime(2028, 2, 27)),

    ("LOTE-ING-059", "Hortifruti", datetime(2026, 10, 12), 100, "Alface_romana", datetime(2028, 2, 28)),

    ("LOTE-ING-060", "Hortifruti", datetime(2026, 10, 12), 100, "Alface_americana", datetime(2028, 2, 29)),

    ("LOTE-ING-061", "Hortifruti", datetime(2026, 10, 12), 12000, "Couve_manteiga", datetime(2028, 3, 1)),

    ("LOTE-ING-062", "Hortifruti", datetime(2026, 10, 12), 11000, "Tomate", datetime(2028, 3, 2)),

    ("LOTE-ING-063", "Hortifruti", datetime(2026, 10, 12), 20000, "Tomate_cereja", datetime(2028, 3, 3)),

    ("LOTE-ING-064", "Hortifruti", datetime(2026, 10, 12), 10000, "Cebola", datetime(2028, 3, 4)),

    ("LOTE-ING-065", "Predilecta", datetime(2026, 10, 12), 12000, "Cebola_caramelizada", datetime(2028, 3, 5)),

    ("LOTE-ING-066", "Hortifruti", datetime(2026, 10, 12), 7000, "Pimentao", datetime(2028, 3, 6)),

    ("LOTE-ING-067", "Hortifruti", datetime(2026, 10, 12), 2000, "Cebolinha", datetime(2028, 3, 7)),

    ("LOTE-ING-068", "Hortifruti", datetime(2026, 10, 12), 2000, "Alho", datetime(2028, 3, 8)),

    ("LOTE-ING-069", "Hortifruti", datetime(2026, 10, 12), 2000, "Manjericao", datetime(2028, 3, 9)),

    ("LOTE-ING-070", "Hortifruti", datetime(2026, 10, 12), 2000, "Salsinha", datetime(2028, 3, 10)),

    ("LOTE-ING-071", "Hortifruti", datetime(2026, 10, 12), 4000, "Limao", datetime(2028, 3, 11)),

    ("LOTE-ING-072", "Hortifruti", datetime(2026, 10, 12), 2000, "Laranja", datetime(2028, 3, 12)),

    ("LOTE-ING-073", "Fazenda local", datetime(2026, 10, 12), 32000, "Cogumelos_frescos", datetime(2028, 3, 13)),

    ("LOTE-ING-074", "Raiola", datetime(2026, 10, 12), 11000, "Champignon", datetime(2028, 3, 14)),

    ("LOTE-ING-075", "Hortifruti", datetime(2026, 10, 12), 13000, "Morango_fresco", datetime(2028, 3, 15)),

    ("LOTE-ING-076", "Hortifruti", datetime(2026, 10, 12), 29000, "Frutas_frescas_in_natura", datetime(2028, 3, 16)),

    ("LOTE-ING-077", "De Marchi", datetime(2026, 10, 12), 15000, "Frutas_vermelhas_congeladas", datetime(2028, 3, 17)),

    ("LOTE-ING-078", "Agtal", datetime(2026, 10, 12), 4500, "Nozes", datetime(2028, 3, 18)),

    # Óleos, temperos, molhos e outros produtos

    ("LOTE-ING-079", "Liza", datetime(2026, 10, 12), 2000, "Oleo_de_soja", datetime(2028, 3, 19)),

    ("LOTE-ING-080", "Soya", datetime(2026, 10, 12), 2000, "Oleo_para_fritura", datetime(2028, 3, 20)),

    ("LOTE-ING-081", "Cisne", datetime(2026, 10, 12), 2000, "Sal", datetime(2028, 3, 21)),

    ("LOTE-ING-082", "Kitano", datetime(2026, 10, 12), 5000, "Temperos", datetime(2028, 3, 22)),

    ("LOTE-ING-083", "Castelo", datetime(2026, 10, 12), 2000, "Vinagre", datetime(2028, 3, 23)),

    ("LOTE-ING-084", "Gallo", datetime(2026, 10, 12), 2500, "Azeite", datetime(2028, 3, 24)),

    ("LOTE-ING-085", "Cepêra", datetime(2026, 10, 12), 4500, "Azeite_de_dende", datetime(2028, 3, 25)),

    ("LOTE-ING-086", "Tabasco", datetime(2026, 10, 12), 7000, "Molho_de_pimenta", datetime(2028, 3, 26)),

    ("LOTE-ING-087", "Queensberry", datetime(2026, 10, 12), 7000, "Geleia_de_pimenta", datetime(2028, 3, 27)),

    ("LOTE-ING-088", "La Pastina", datetime(2026, 10, 12), 3000, "Alcaparras", datetime(2028, 3, 28)),

    ("LOTE-ING-089", "Pomarola", datetime(2026, 10, 12), 33000, "Molho_de_tomate", datetime(2028, 3, 29)),

    ("LOTE-ING-090", "Heinz", datetime(2026, 10, 12), 2000, "Catchup", datetime(2028, 3, 30)),

    ("LOTE-ING-091", "Hemmer", datetime(2026, 10, 12), 2000, "Mostarda", datetime(2028, 3, 31)),

    ("LOTE-ING-092", "Hellmann's", datetime(2026, 10, 12), 5000, "Molho_mostarda_e_mel", datetime(2028, 4, 1)),

    ("LOTE-ING-093", "Hellmann's", datetime(2026, 10, 12), 6000, "Molho_Caesar", datetime(2028, 4, 2)),

    ("LOTE-ING-094", "Marilan", datetime(2026, 10, 12), 2500, "Croutons", datetime(2028, 4, 3)),

    ("LOTE-ING-095", "Hellmann's", datetime(2026, 10, 12), 7000, "Maionese_temperada", datetime(2028, 4, 4)),

    ("LOTE-ING-096", "Hunt's", datetime(2026, 10, 12), 5000, "Molho_barbecue", datetime(2028, 4, 5)),

    ("LOTE-ING-097", "Aurora", datetime(2026, 10, 12), 11000, "Vinho_branco", datetime(2028, 4, 6)),

    ("LOTE-ING-098", "Sadia", datetime(2026, 10, 12), 17000, "Guacamole", datetime(2028, 4, 7)),

    ("LOTE-ING-099", "Dr. Oetker", datetime(2026, 10, 12), 2000, "Gelatina", datetime(2028, 4, 8)),

    ("LOTE-ING-100", "Nestlé", datetime(2026, 10, 12), 14000, "Chocolate_meio_amargo", datetime(2028, 4, 9)),

    ("LOTE-ING-101", "Mel Santa Bárbara", datetime(2026, 10, 12), 4500, "Mel", datetime(2028, 4, 10)),

    ("LOTE-ING-102", "Raiola", datetime(2026, 10, 12), 10000, "Azeitona", datetime(2028, 4, 11)),

    # Bebidas sem álcool e xaropes

    ("LOTE-ING-103", "Sucos Massa", datetime(2026, 10, 12), 4000, "Suco_de_limao", datetime(2028, 4, 12)),

    ("LOTE-ING-104", "Monin", datetime(2026, 10, 12), 2000, "Xarope_de_groselha_framboesa", datetime(2028, 4, 13)),

    ("LOTE-ING-105", "Schweppes", datetime(2026, 10, 12), 15000, "Agua_com_gas", datetime(2028, 4, 14)),

    ("LOTE-ING-106", "Finest Call", datetime(2026, 10, 12), 2000, "Xarope_simples_de_acucar", datetime(2028, 4, 15)),

    ("LOTE-ING-107", "Maguary", datetime(2026, 10, 12), 15000, "Suco_de_abacaxi", datetime(2028, 4, 16)),

    ("LOTE-ING-108", "Monin", datetime(2026, 10, 12), 2500, "Xarope_de_maca_verde", datetime(2028, 4, 17)),

    ("LOTE-ING-109", "De Marchi", datetime(2026, 10, 12), 4000, "Polpa_de_frutas_vermelhas", datetime(2028, 4, 18)),

    ("LOTE-ING-110", "Del Valle", datetime(2026, 10, 12), 14000, "Suco_de_laranja", datetime(2028, 4, 19)),

    ("LOTE-ING-111", "Guaraná Antarctica", datetime(2026, 10, 12), 15000, "Refrigerante_de_guarana", datetime(2028, 4, 20)),

    ("LOTE-ING-112", "Lipton", datetime(2026, 10, 12), 15000, "Cha_preto", datetime(2028, 4, 21)),

    ("LOTE-ING-113", "Monin", datetime(2026, 10, 12), 3000, "Xarope_de_pessego", datetime(2028, 4, 22)),

    ("LOTE-ING-114", "Monin", datetime(2026, 10, 12), 2000, "Xarope_de_grenadine", datetime(2028, 4, 23)),

    ("LOTE-ING-115", "Sococo", datetime(2026, 10, 12), 15000, "Agua_de_coco", datetime(2028, 4, 24)),

    ("LOTE-ING-116", "Maguary", datetime(2026, 10, 12), 12000, "Suco_de_maracuja", datetime(2028, 4, 25)),

    ("LOTE-ING-117", "Monin", datetime(2026, 10, 12), 2000, "Xarope_de baunilha", datetime(2028, 4, 26)),

    ("LOTE-ING-118", "Maguary", datetime(2026, 10, 12), 15000, "Suco_de_melancia", datetime(2028, 4, 27)),

    ("LOTE-ING-119", "Maguary", datetime(2026, 10, 12), 2000, "Suco_de_gengibre", datetime(2028, 4, 28)),

    # Bebidas alcoólicas e ingredientes de coquetelaria

    ("LOTE-ING-120", "Cachaça 51", datetime(2026, 10, 12), 4000, "Cachaca", datetime(2028, 4, 29)),

    ("LOTE-ING-121", "José Cuervo", datetime(2026, 10, 12), 4000, "Tequila", datetime(2028, 4, 30)),

    ("LOTE-ING-122", "Cointreau", datetime(2026, 10, 12), 2000, "Cointreau_triple_sec", datetime(2028, 5, 1)),

    ("LOTE-ING-123", "Tanqueray", datetime(2026, 10, 12), 5500, "Gin", datetime(2028, 5, 2)),

    ("LOTE-ING-124", "Campari", datetime(2026, 10, 12), 2500, "Campari", datetime(2028, 5, 3)),

    ("LOTE-ING-125", "Martini", datetime(2026, 10, 12), 2500, "Vermute_tinto", datetime(2028, 5, 4)),

    ("LOTE-ING-126", "Absolut", datetime(2026, 10, 12), 4000, "Vodka", datetime(2028, 5, 5)),

    ("LOTE-ING-127", "Fever-Tree", datetime(2026, 10, 12), 9000, "Ginger_beer", datetime(2028, 5, 6)),

    ("LOTE-ING-128", "Ocean Spray", datetime(2026, 10, 12), 2500, "Suco_de_cranberry", datetime(2028, 5, 7)),

    ("LOTE-ING-129", "Bacardi", datetime(2026, 10, 12), 4000, "Rum_branco", datetime(2028, 5, 8)),

    ("LOTE-ING-130", "Bacardi", datetime(2026, 10, 12), 2000, "Rum_escuro", datetime(2028, 5, 9)),

    ("LOTE-ING-131", "Monin", datetime(2026, 10, 12), 2000, "Xarope_de_amendoa_orgeat", datetime(2028, 5, 10)),

    ("LOTE-ING-132", "Jim Beam", datetime(2026, 10, 12), 4500, "Uisque_bourbon", datetime(2028, 5, 11)),

    ("LOTE-ING-133", "Angostura", datetime(2026, 10, 12), 2000, "Angostura_bitters", datetime(2028, 5, 12)),

    ("LOTE-ING-134", "Bulleit", datetime(2026, 10, 12), 5500, "Uisque_de_centeio_rye", datetime(2028, 5, 13)),

    ("LOTE-ING-135", "Luxardo", datetime(2026, 10, 12), 2000, "Cereja_marasquino", datetime(2028, 5, 14)),

    # Outros itens

    ("LOTE-ING-136", "McCain", datetime(2026, 10, 12), 33000, "Onion_rings", datetime(2028, 5, 15)),

    ("LOTE-ING-137", "Nestlé", datetime(2026, 10, 12), 600, "Brigadeiro", datetime(2028, 5, 16)),

    ("LOTE-ING-138", "Nestlé", datetime(2026, 10, 12), 600, "Beijinho", datetime(2028, 5, 17)),

    ("LOTE-ING-139", "Pullman", datetime(2026, 10, 12), 33000, "Bolo_comum_simples", datetime(2028, 5, 18)),
    
    ("LOTE-ING-140", "Sadia", datetime(2026, 10, 12), 900, "Pastel_de_queijo", datetime(2028, 6, 20)),

    ("LOTE-ING-141", "Sadia", datetime(2026, 10, 12), 17000, "Salame", datetime(2028, 7, 15)),

    ("LOTE-ING-142", "Nature", datetime(2026, 10, 11), 750, "Folha_de_hortela", datetime(2028,4,1))
]

#id, nome
lista_cargos = [
    (1, "cliente"),
    (2, "chefe"),
    (3, "admin"),
]

# ================================= "Tabelas" USUARIOS / PEDIDOS =================================

# Usuários adicionais (além do admin, que é criado por iniciar_admin()).
# Cada CPF e e-mail é distinto do admin (00000000000 / ADMIN_EMAIL) e entre si,
# pois cpf_hmac e email_hmac são UNIQUE. A senha é sempre colocada em hash.
# nome, cpf, email, senha, cargo (Cargo enum)
lista_usuarios = [
    ("Ana Clara Souza", "11144477735", "ana.souza@exemplo.com", "SenhaCliente1!", Cargo.CLIENTE),
    ("Bruno Henrique Lima", "22255588846", "bruno.lima@exemplo.com", "SenhaCliente2!", Cargo.CLIENTE),
    ("Carla Regina Nunes", "33366699957", "carla.nunes@exemplo.com", "SenhaCliente3!", Cargo.CLIENTE),
    ("Diego Martins Rocha", "44477700012", "diego.rocha@exemplo.com", "SenhaChefe1!", Cargo.CHEFE),
    ("Eduarda Alves Pinto", "55588811123", "eduarda.pinto@exemplo.com", "SenhaChefe2!", Cargo.CHEFE),
]

# ------------------------------------------------------------------------------
# Expansão programática de clientes, chefes e endereços.
#
# Para que os relatórios do admin mostrem faturamento em vários meses, o seed
# precisa de uma base ampla e determinística de clientes (quem faz os pedidos),
# chefes (quem os atende) e endereços (local do evento). Os dados são gerados
# por compreensões a partir de listas fixas, de modo que rodar o seed sempre
# produz exatamente os mesmos registros (idempotência preservada pelas funções
# iniciar_*, que pulam CPF/e-mail já existentes).
#
# Regras respeitadas:
#   - Apenas Cargo.CLIENTE e Cargo.CHEFE (NENHUM novo ADMIN; o admin é criado só
#     por iniciar_admin()).
#   - CPF é string de 11 dígitos, único entre si e distinto de '00000000000'.
#   - E-mails são únicos.
#   - Cada endereço gerado abaixo pertence a um cliente existente, e cada par
#     (email_cliente, nome_endereco) usado em lista_pedidos existe aqui.
# ------------------------------------------------------------------------------

# Clientes adicionais: (primeiro_nome, sobrenome, apelido_email). O apelido vira
# o local-part do e-mail e um prefixo estável para os CPFs/endereços.
_clientes_extra = [
    ("Fernanda", "Oliveira Castro", "fernanda.castro"),
    ("Gabriel", "Teixeira Ramos", "gabriel.ramos"),
    ("Helena", "Barbosa Dias", "helena.dias"),
    ("Igor", "Carvalho Melo", "igor.melo"),
    ("Juliana", "Ferreira Pires", "juliana.pires"),
    ("Kleber", "Azevedo Lopes", "kleber.lopes"),
    ("Larissa", "Moreira Campos", "larissa.campos"),
    ("Marcelo", "Nogueira Freitas", "marcelo.freitas"),
    ("Natália", "Ribeiro Gomes", "natalia.gomes"),
    ("Otávio", "Cardoso Batista", "otavio.batista"),
    ("Patrícia", "Mendes Araújo", "patricia.araujo"),
    ("Rafael", "Santana Peixoto", "rafael.peixoto"),
]

# Chefes adicionais atendem os pedidos; variam o vínculo cliente/chefe.
_chefes_extra = [
    ("Sofia", "Cunha Vasconcelos", "sofia.vasconcelos"),
    ("Thiago", "Moraes Barros", "thiago.barros"),
    ("Vivian", "Antunes Rocha", "vivian.rocha"),
    ("William", "Siqueira Nunes", "william.nunes"),
]


def _cpf_fake(prefixo: str, indice: int) -> str:
    """Gera um CPF fictício determinístico de 11 dígitos distinto do admin.

    Não há validação de dígito verificador no caminho do seed; o requisito é
    apenas que o CPF tenha 11 dígitos, seja único e diferente de '00000000000'.

    Args:
        prefixo (str): prefixo numérico estável (clientes/chefes usam faixas
            diferentes para nunca colidir).
        indice (int): posição do usuário na sua lista.

    Returns:
        str: CPF com exatamente 11 dígitos.
    """
    numero = f"{prefixo}{indice:06d}"
    return numero[:11].ljust(11, "0")


# Clientes extra viram tuplas no mesmo formato de lista_usuarios.
lista_usuarios += [
    (f"{nome} {sobrenome}", _cpf_fake("701", i), f"{apelido}@exemplo.com",
     f"SenhaCliente{i + 10}!", Cargo.CLIENTE)
    for i, (nome, sobrenome, apelido) in enumerate(_clientes_extra, start=1)
]

# Chefes extra (faixa de CPF distinta da dos clientes para garantir unicidade).
lista_usuarios += [
    (f"{nome} {sobrenome}", _cpf_fake("809", i), f"{apelido}@exemplo.com",
     f"SenhaChefe{i + 10}!", Cargo.CHEFE)
    for i, (nome, sobrenome, apelido) in enumerate(_chefes_extra, start=1)
]

# E-mails dos clientes/chefes (usados para gerar endereços e pedidos).
_emails_clientes = [
    "ana.souza@exemplo.com",
    "bruno.lima@exemplo.com",
    "carla.nunes@exemplo.com",
] + [f"{apelido}@exemplo.com" for _, _, apelido in _clientes_extra]

_emails_chefes = [
    "diego.rocha@exemplo.com",
    "eduarda.pinto@exemplo.com",
] + [f"{apelido}@exemplo.com" for _, _, apelido in _chefes_extra]

# Endereços vinculados aos clientes seed (resolvidos por e-mail do dono).
# Variados: cidades/UFs diferentes, alguns com complemento e outros sem.
# email_dono, nome, logradouro, numero, complemento, bairro, cidade, cep, uf
lista_enderecos = [
    ("ana.souza@exemplo.com", "Casa", "Rua das Acácias", "120", "Apto 34", "Jardim Primavera", "São Paulo", "01234-567", "SP"),
    ("ana.souza@exemplo.com", "Trabalho", "Avenida Paulista", "1500", "Sala 802", "Bela Vista", "São Paulo", "01310-100", "SP"),
    ("bruno.lima@exemplo.com", "Casa", "Rua do Sol", "45", None, "Centro", "Belo Horizonte", "30110-000", "MG"),
    ("carla.nunes@exemplo.com", "Casa", "Travessa das Flores", "9", "Fundos", "Boa Viagem", "Recife", "51020-000", "PE"),
    ("carla.nunes@exemplo.com", "Sítio", "Estrada do Vale", "s/n", None, "Zona Rural", "Gravatá", "55640-000", "PE"),
]

# Catálogo fixo de cidades/UF/bairro/logradouro usado para gerar endereços
# variados de forma determinística (indexado pela posição do cliente/endereço).
_locais_endereco = [
    ("São Paulo", "SP", "Vila Mariana", "Rua Domingos de Morais", "01000-100"),
    ("Rio de Janeiro", "RJ", "Copacabana", "Avenida Atlântica", "22000-200"),
    ("Belo Horizonte", "MG", "Savassi", "Rua Pernambuco", "30100-300"),
    ("Curitiba", "PR", "Batel", "Avenida do Batel", "80400-400"),
    ("Porto Alegre", "RS", "Moinhos de Vento", "Rua Padre Chagas", "90500-500"),
    ("Salvador", "BA", "Barra", "Avenida Oceânica", "40140-600"),
    ("Recife", "PE", "Boa Viagem", "Avenida Boa Viagem", "51020-700"),
    ("Fortaleza", "CE", "Meireles", "Avenida Beira Mar", "60165-800"),
    ("Brasília", "DF", "Asa Sul", "SQS 108 Bloco B", "70347-900"),
    ("Florianópolis", "SC", "Centro", "Rua Felipe Schmidt", "88010-000"),
]

# Para cada cliente extra geramos 2 endereços ("Casa" e "Festa"), variando
# cidade/UF/bairro e alternando complemento preenchido/None. Como iniciar_pedidos
# resolve o endereço por (id_usuario, nome), esses nomes são reutilizados abaixo.
for _idx_cli, _email_cli in enumerate(_emails_clientes[3:], start=0):
    _l_casa = _locais_endereco[_idx_cli % len(_locais_endereco)]
    _l_festa = _locais_endereco[(_idx_cli + 3) % len(_locais_endereco)]
    lista_enderecos.append(
        (_email_cli, "Casa", _l_casa[3], str(100 + _idx_cli),
         (f"Apto {10 + _idx_cli}" if _idx_cli % 2 == 0 else None),
         _l_casa[2], _l_casa[0], _l_casa[4], _l_casa[1]),
    )
    lista_enderecos.append(
        (_email_cli, "Festa", _l_festa[3], str(500 + _idx_cli),
         (None if _idx_cli % 2 == 0 else f"Salão {_idx_cli}"),
         _l_festa[2], _l_festa[0], _l_festa[4], _l_festa[1]),
    )

# Pedidos seed, cobrindo os cinco status do enum.
# Resolvem cliente/chefe por e-mail e endereço pelo nome do endereço do cliente.
# O trigger de baixa de estoque é AFTER UPDATE OF status, portanto inserir um
# pedido já com status 'confirmado'/'em preparo'/'concluido' NÃO o dispara.
#
# FORMATO (13 campos):
#   chave, email_cliente, nome_endereco, email_chefe (ou None), status,
#     dias_evento, hora_inicio, hora_fim, valor_total, observacao, confirmado,
#     dias_criado, dias_confirmado
#
# Novidade do FEAT-002: além de dias_evento (offset em dias para data_evento,
# que PODE SER NEGATIVO para eventos no passado), cada pedido declara:
#   - dias_criado: quantos dias ATRÁS o pedido foi criado (criado_em = hoje() -
#     dias_criado). Define em qual mês o pedido entra nos relatórios de volume
#     (pedidos_quantidade/pedidos_status usam criado_em).
#   - dias_confirmado: quantos dias ATRÁS o pedido foi confirmado (confirmado_em
#     = hoje() - dias_confirmado), ou None quando não confirmado. Define em qual
#     mês o pedido entra nos relatórios financeiros (faturamento usa
#     confirmado_em). Deve ser preenchido quando confirmado=True e None quando
#     confirmado=False, mantendo a coerência status/confirmado_em.
# Todas as datas derivam de utils.hoje(), portanto permanecem determinísticas e
# relativas à execução; _pedidos_por_chave() recomputa a MESMA data_evento com a
# mesma fórmula para preservar a idempotência da dedup.
lista_pedidos = [
    ("pedido_aguardando", "ana.souza@exemplo.com", "Casa", None,
     "aguardando", 30, time(18, 0), time(23, 0), 1499.00,
     "Aniversário de 30 anos, preferência por pratos quentes.", False, 2, None),
    ("pedido_confirmado", "ana.souza@exemplo.com", "Trabalho", "diego.rocha@exemplo.com",
     "confirmado", 45, time(12, 0), time(16, 0), 2599.90,
     "Confraternização da equipe.", True, 5, 3),
    ("pedido_em_preparo", "bruno.lima@exemplo.com", "Casa", "eduarda.pinto@exemplo.com",
     "em preparo", 20, time(19, 30), time(23, 30), 3250.00,
     None, True, 8, 6),
    ("pedido_concluido", "carla.nunes@exemplo.com", "Casa", "diego.rocha@exemplo.com",
     "concluido", -5, time(11, 0), time(15, 0), 1890.50,
     "Casamento na praia.", True, 20, 6),
    ("pedido_cancelado", "carla.nunes@exemplo.com", "Sítio", None,
     "cancelado", 60, time(13, 0), time(18, 0), 0.00,
     "Cliente cancelou por mudança de data.", False, 40, None),
]

# ------------------------------------------------------------------------------
# Expansão programática de pedidos distribuídos por ~12 meses no passado.
#
# Gera dezenas de pedidos determinísticos para que os relatórios financeiros do
# admin exibam faturamento em vários meses distintos. A grande maioria é
# 'concluido' com confirmado_em espalhado mês a mês (valor_total realista e
# variado, > 0); há também 'cancelado' (valor 0.00) e, no mês corrente, alguns
# recentes em 'aguardando'/'confirmado'/'em preparo'.
#
# Para cada um dos 12 meses passados (1 a 12 meses atrás) criamos pedidos
# concluídos; os offsets em dias derivam do índice do mês (determinístico). A
# dedup de iniciar_pedidos() usa (id_cliente, data_evento, hora_inicio,
# hora_fim); como variamos cliente/horários por pedido, cada chave é única.
# ------------------------------------------------------------------------------

# Horários de evento variados (todos com hora_fim > hora_inicio).
_horarios_evento = [
    (time(11, 0), time(15, 0)),
    (time(12, 30), time(16, 30)),
    (time(18, 0), time(22, 0)),
    (time(19, 30), time(23, 30)),
    (time(10, 0), time(14, 0)),
]

# Valores base realistas (em reais) ciclados para dar variação ao faturamento.
_valores_concluido = [1290.00, 1875.50, 2340.00, 3180.75, 2765.40, 4120.00,
                      1990.90, 3505.25, 2450.00, 5230.80]

# Observações variadas para os pedidos concluídos.
_observacoes_concluido = [
    "Festa de aniversário concluída com sucesso.",
    "Evento corporativo atendido pela equipe.",
    "Confraternização de fim de ano.",
    "Casamento no salão de festas.",
    "Almoço de família no fim de semana.",
    None,
]


def _gerar_pedidos_passados() -> list[tuple]:
    """Gera, de forma determinística, os pedidos seed do passado.

    Produz pedidos 'concluido' espalhados ao longo de 12 meses (usando
    dias_confirmado/dias_criado proporcionais ao mês), alguns 'cancelado' e um
    punhado de pedidos recentes em outros status. Retorna tuplas no mesmo
    formato de lista_pedidos (13 campos).

    Returns:
        list[tuple]: pedidos adicionais a serem concatenados em lista_pedidos.
    """
    gerados: list[tuple] = []

    n_clientes = len(_emails_clientes)
    n_chefes = len(_emails_chefes)

    # --- Pedidos CONCLUÍDOS: 4 por mês, de 1 a 12 meses atrás. ---
    # Para cada mês usamos dias de referência = mes * 30 (aprox.), ajustando por
    # pequenos deslocamentos para espalhar dentro do mês. confirmado_em e
    # criado_em caem no mesmo mês; data_evento fica próxima da confirmação (no
    # passado), coerente com um evento já realizado.
    contador = 0
    for mes in range(1, 13):
        base_dias = mes * 30
        for k in range(4):
            offset_dia = k * 6  # espalha 4 pedidos dentro do mês
            dias_confirmado = base_dias - offset_dia
            dias_criado = dias_confirmado + 7  # criado ~1 semana antes de confirmar
            dias_evento = -(dias_confirmado - 1)  # evento ~1 dia após a confirmação (ainda no passado)

            email_cliente = _emails_clientes[contador % n_clientes]
            nome_endereco = "Casa" if (contador % 2 == 0) else "Festa"
            # Os três primeiros clientes legados só têm os nomes de endereço
            # originais ("Casa"/"Trabalho"/"Sítio"); para eles usamos "Casa".
            if email_cliente in ("bruno.lima@exemplo.com", "carla.nunes@exemplo.com"):
                nome_endereco = "Casa"
            elif email_cliente == "ana.souza@exemplo.com":
                nome_endereco = "Casa" if (contador % 2 == 0) else "Trabalho"

            email_chefe = _emails_chefes[contador % n_chefes]
            hora_inicio, hora_fim = _horarios_evento[contador % len(_horarios_evento)]
            valor = _valores_concluido[contador % len(_valores_concluido)]
            observacao = _observacoes_concluido[contador % len(_observacoes_concluido)]

            gerados.append((
                f"concluido_m{mes:02d}_{k}", email_cliente, nome_endereco, email_chefe,
                "concluido", dias_evento, hora_inicio, hora_fim, valor,
                observacao, True, dias_criado, dias_confirmado,
            ))
            contador += 1

    # --- Pedidos CANCELADOS: 1 a cada 2 meses (valor 0.00, não confirmado). ---
    for mes in range(1, 13, 2):
        base_dias = mes * 30 - 3
        email_cliente = _emails_clientes[contador % n_clientes]
        nome_endereco = "Casa"
        if email_cliente not in ("ana.souza@exemplo.com", "bruno.lima@exemplo.com",
                                 "carla.nunes@exemplo.com"):
            nome_endereco = "Festa" if (contador % 2 == 0) else "Casa"
        hora_inicio, hora_fim = _horarios_evento[contador % len(_horarios_evento)]
        gerados.append((
            f"cancelado_m{mes:02d}", email_cliente, nome_endereco, None,
            "cancelado", -(base_dias - 2), hora_inicio, hora_fim, 0.00,
            "Pedido cancelado pelo cliente.", False, base_dias, None,
        ))
        contador += 1

    # --- Pedidos RECENTES no mês corrente, cobrindo os demais status. ---
    # data_evento futura para aguardando/confirmado/em preparo (eventos por vir);
    # passada para os concluídos recentes. Os offsets de criado_em/confirmado_em
    # são pequenos (1 a 12 dias) para cair no mês corrente, alimentando os
    # relatórios de volume (pedidos_quantidade/pedidos_tipo usam criado_em) e o
    # faturamento do mês atual (confirmado_em). Formato de cada item:
    # (status, dias_evento, valor, obs, confirmado, dias_criado, dias_confirmado)
    recentes = [
        ("aguardando", 25, 1290.00, "Orçamento em análise pelo cliente.", False, 1, None),
        ("aguardando", 18, 2140.00, "Aguardando confirmação de data.", False, 3, None),
        ("confirmado", 28, 3360.00, "Evento confirmado para o próximo mês.", True, 4, 2),
        ("confirmado", 15, 2580.50, "Pagamento de entrada efetuado.", True, 6, 4),
        ("em preparo", 9, 4190.00, "Equipe montando o cardápio.", True, 10, 8),
        ("em preparo", 6, 1760.25, "Compras de insumos em andamento.", True, 12, 9),
        # Concluídos recentes (criados e confirmados no mês corrente): dão volume
        # a pedidos_quantidade (concluídos por criado_em) e pedidos_tipo.
        ("concluido", -2, 2890.00, "Evento concluído nesta semana.", True, 7, 3),
        ("concluido", -4, 3640.50, "Buffet entregue com sucesso.", True, 9, 5),
        ("concluido", -1, 1980.00, "Jantar executivo finalizado.", True, 2, 1),
    ]
    for j, (status, dias_evento, valor, obs, confirmado, dias_criado, dias_conf) in enumerate(recentes):
        email_cliente = _emails_clientes[contador % n_clientes]
        nome_endereco = "Casa"
        if email_cliente not in ("ana.souza@exemplo.com", "bruno.lima@exemplo.com",
                                 "carla.nunes@exemplo.com"):
            nome_endereco = "Festa" if (j % 2 == 0) else "Casa"
        email_chefe = _emails_chefes[contador % n_chefes] if confirmado else None
        hora_inicio, hora_fim = _horarios_evento[j % len(_horarios_evento)]
        gerados.append((
            f"recente_{status.replace(' ', '_')}_{j}", email_cliente, nome_endereco,
            email_chefe, status, dias_evento, hora_inicio, hora_fim, valor,
            obs, confirmado, dias_criado, dias_conf,
        ))
        contador += 1

    return gerados


# Gera a lista UMA ÚNICA VEZ e reutiliza (em lista_pedidos, nas associações de
# cardápio e nas bebidas avulsas). Isso evita recomputar a lista a cada uso e,
# acima de tudo, garante que as CHAVES de pedido sejam idênticas entre os três
# consumidores, preservando o casamento das associações (cardapio_pedido /
# pedido_bebida) com os pedidos de lista_pedidos.
_pedidos_gerados = _gerar_pedidos_passados()

lista_pedidos += _pedidos_gerados

# Cardápios de cada pedido. (nome_servico, nome_cardapio) precisa existir em
# lista_servicos_cardapios para que (id_cardapio, id_servico) seja consistente.
# chave_pedido, nome_servico, nome_cardapio, num_convidados
lista_cardapio_pedido = [
    ("pedido_aguardando", "Chef_em_casa", "Feijoada_completa", 30),
    ("pedido_confirmado", "Buffet", "Strogonoff_de_file_Mignon", 80),
    ("pedido_confirmado", "Bar", "Bebida_com_alcool", 80),
    ("pedido_em_preparo", "Mesa_de_salgados", "Salgados_completo", 120),
    ("pedido_em_preparo", "Bar", "Bebida_mista", 120),
    ("pedido_concluido", "Buffet", "Feijoada_completa", 60),
    ("pedido_cancelado", "Mesa_de_salgados", "Hamburguer_tradicional", 200),
]

# Pares (serviço, cardápio) válidos ciclados para os pedidos gerados. Todos
# existem em lista_servicos_cardapios, logo (id_cardapio, id_servico) é
# consistente. Cada tupla é (nome_servico, nome_cardapio).
_pares_servico_cardapio = [
    ("Chef_em_casa", "Feijoada_completa"),
    ("Buffet", "Strogonoff_de_file_Mignon"),
    ("Chef_em_casa", "Bobo_de_camarao"),
    ("Buffet", "Risoto_de_cogumelos_com_tiras_de_file_mignon"),
    ("Mesa_de_salgados", "Salgados_completo"),
    ("Mesa_de_salgados", "Hamburguer_smash"),
    ("Bar", "Bebida_sem_alcool"),
    ("Chef_em_casa", "Raviolli_de_queijo_ao_molho_bolonhesa"),
    ("Buffet", "Feijoada_completa"),
    ("Mesa_de_salgados", "Boteco_brasileiro"),
]


def _gerar_cardapio_pedido() -> list[tuple]:
    """Associa um cardápio válido a cada pedido gerado programaticamente.

    Usa SOMENTE pares presentes em lista_servicos_cardapios (via
    _pares_servico_cardapio) e num_convidados > 0. Pedidos 'concluido'/recentes
    com serviço de comida também ganham um cardápio de Bar quando par é de Bar.

    Returns:
        list[tuple]: tuplas (chave_pedido, nome_servico, nome_cardapio,
        num_convidados) para os pedidos gerados.
    """
    assoc: list[tuple] = []
    for i, pedido in enumerate(_pedidos_gerados):
        chave = pedido[0]
        num_convidados = 30 + (i % 8) * 15  # 30..135, sempre > 0
        servico, cardapio = _pares_servico_cardapio[i % len(_pares_servico_cardapio)]
        assoc.append((chave, servico, cardapio, num_convidados))
        # A cada 3 pedidos, acrescenta um cardápio de Bar para dar variedade de
        # serviço nos relatórios por tipo.
        if i % 3 == 0:
            assoc.append((chave, "Bar", "Bebida_mista", num_convidados))
    return assoc


lista_cardapio_pedido += _gerar_cardapio_pedido()

# Bebidas avulsas de alguns pedidos. valor_total = valor_unitario * qtd (resolvido
# dinamicamente no inicializador a partir da bebida). chave_pedido, nome_bebida, qtd
lista_pedido_bebida = [
    ("pedido_aguardando", "Agua_com_gas", 30),
    ("pedido_aguardando", "Suco_de_abacaxi", 15),
    ("pedido_confirmado", "Refrigerante_de_guarana", 50),
    ("pedido_concluido", "Agua_de_coco", 40),
]

# Bebidas avulsas para parte dos pedidos gerados (apenas bebidas existentes em
# lista_bebida; qtd > 0).
_bebidas_avulsas = ["Agua_com_gas", "Suco_de_abacaxi", "Refrigerante_de_guarana",
                    "Agua_de_coco", "Cha_preto", "Suco_de_melancia"]

lista_pedido_bebida += [
    (pedido[0], _bebidas_avulsas[i % len(_bebidas_avulsas)], 10 + (i % 5) * 10)
    for i, pedido in enumerate(_pedidos_gerados)
    if i % 2 == 0  # bebida avulsa em metade dos pedidos gerados
]

# Logs de auditoria seed, espelhando as ações usadas pelos controllers.
# email_usuario, acao, descricao
lista_logs = [
    ("ana.souza@exemplo.com", "LOGIN", "Usuário efetuou login no sistema."),
    ("ana.souza@exemplo.com", "NOVO ENDERECO", "Novo endereço cadastrado pelo cliente."),
    ("ana.souza@exemplo.com", "PEDIDO", "Cliente realizou um novo pedido."),
    ("bruno.lima@exemplo.com", "LOGIN", "Usuário efetuou login no sistema."),
    ("carla.nunes@exemplo.com", "REMOCAO PEDIDO", "Cliente cancelou um pedido."),
    ("diego.rocha@exemplo.com", "LOGIN", "Chefe efetuou login no sistema."),
]

# Tokens de verificação seed. O codigo_hash é o HMAC-SHA256 do código, com a
# mesma chave (TOKEN_SHA) usada em security/token_auth.py; nunca em texto puro.
# email_usuario, codigo, ativo, tentativas
lista_tokens = [
    ("ana.souza@exemplo.com", "123456", True, 0),
    ("bruno.lima@exemplo.com", "654321", False, 3),
]

# prato, ingrediente, quantidade (na unidade especifica)
lista_ficha_tecnica = [

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

#prato, cardapio, quantidade (em g), descrição técnica
lista_prato_cardapio = [
    # FEIJOADA COMPLETA
    ("Mandioca_frita", "Feijoada_completa", 77, "77 g por pessoa"),
    ("Tabua_de_frios", "Feijoada_completa", 88, "88 g por pessoa"),
    ("Feijoada_completa", "Feijoada_completa", 242, "242 g por pessoa"),
    ("Arroz_branco", "Feijoada_completa", 132, "132 g por pessoa"),
    ("Couve_refogada", "Feijoada_completa", 44, "44 g por pessoa"),
    ("Farofa", "Feijoada_completa", 55, "55 g por pessoa"),
    ("Vinagrete", "Feijoada_completa", 88, "88 g por pessoa"),
    ("Molho_de_pimenta", "Feijoada_completa", 22, "22 g por pessoa"),
    ("Sorvete", "Feijoada_completa", 1, "Sobremesa por porção"),

    # BOBÓ DE CAMARÃO
    ("Salada_fresca", "Bobo_de_camarao", 132, "132 g por pessoa"),
    ("Bobo_de_camarao", "Bobo_de_camarao", 308, "308 g por pessoa"),
    ("Arroz_branco", "Bobo_de_camarao", 187, "187 g por pessoa"),
    ("Salada_de_fruta_fresca_com_creme", "Bobo_de_camarao", 158, "Aproximadamente 158 g por pessoa"),

    # FILÉ DE TILÁPIA
    ("Bruschetta", "File_de_tilapia_ao_molho_manteiga_e_alcaparras", 121, "121 g por pessoa"),
    ("File_de_tilapia", "File_de_tilapia_ao_molho_manteiga_e_alcaparras", 198, "198 g por pessoa"),
    ("Arroz_branco", "File_de_tilapia_ao_molho_manteiga_e_alcaparras", 220, "220 g por pessoa"),
    ("Molho_de_mateiga_com_alcaparras", "File_de_tilapia_ao_molho_manteiga_e_alcaparras", 44, "44 g por pessoa"),
    ("Iorgute_Natural_com_morangos_e_mel", "File_de_tilapia_ao_molho_manteiga_e_alcaparras", 137, "Aproximadamente 137 g por pessoa"),

    # STROGONOFF
    ("Salada_ceaser", "Strogonoff_de_file_Mignon", 143, "143 g por pessoa"),
    ("Stogonoff_de_file_mignon", "Strogonoff_de_file_Mignon", 242, "242 g por pessoa"),
    ("Arroz_branco", "Strogonoff_de_file_Mignon", 198, "198 g por pessoa"),
    ("Batata_palha", "Strogonoff_de_file_Mignon", 55, "55 g por pessoa"),
    ("Pudim_de_leite_condensado", "Strogonoff_de_file_Mignon", 120, "120 g por pessoa"),

    # NHOQUE
    ("Salada_fresca", "Nhoque_ao_molho", 110, "110 g por pessoa"),
    ("Nhoque_ao_molho", "Nhoque_ao_molho", 275, "275 g por pessoa"),
    ("Mousse_de_maracuja", "Nhoque_ao_molho", 116, "Aproximadamente 116 g por pessoa"),

    # RISOTO
    ("Bruschetta", "Risoto_de_cogumelos_com_tiras_de_file_mignon", 121, "121 g por pessoa"),
    ("Risoto_de_cogumelos_com_tiras_de_file_mignon", "Risoto_de_cogumelos_com_tiras_de_file_mignon", 352, "352 g por pessoa"),
    ("Brownie_de_chocolate", "Risoto_de_cogumelos_com_tiras_de_file_mignon", 105, "105 g por pessoa"),

    # ESCONDIDINHO
    ("Dadinho_de_tapioca", "Escondinho_de_carne_seca_com_mandioca", 110, "110 g por pessoa"),
    ("Escondidinho_de_carne_seca_com_mandioca", "Escondinho_de_carne_seca_com_mandioca", 495, "495 g por pessoa"),
    ("Geleia_de_pimenta", "Escondinho_de_carne_seca_com_mandioca", 22, "22 g por pessoa"),
    ("Cheesecake_de_frutas_vermelhas", "Escondinho_de_carne_seca_com_mandioca", 137, "Aproximadamente 137 g por pessoa"),

    # RAVIOLI
    ("Tabua_de_frios", "Raviolli_de_queijo_ao_molho_bolonhesa", 132, "132 g por pessoa"),
    ("Ravioli_de_queijo_ao_molho_bolanhesa", "Raviolli_de_queijo_ao_molho_bolonhesa", 286, "286 g por pessoa"),
    ("Parmesao_ralado", "Raviolli_de_queijo_ao_molho_bolonhesa", 11, "11 g por pessoa"),
    ("Mousse_de_chocolate", "Raviolli_de_queijo_ao_molho_bolonhesa", 116, "Aproximadamente 116 g por pessoa"),
]

#bebida, cardapio
lista_bebida_cardapio = [
    # BEBIDAS SEM ÁLCOOL
    ("Agua_com_gas", "Bebida_sem_alcool"),
    ("Suco_de_abacaxi", "Bebida_sem_alcool"),
    ("Refrigerante_de_guarana", "Bebida_sem_alcool"),
    ("Cha_preto", "Bebida_sem_alcool"),
    ("Agua_de_coco", "Bebida_sem_alcool"),
    ("Suco_de_melancia", "Bebida_sem_alcool"),

    # DRINKS SEM ÁLCOOL
    ("Pink Lemonade", "Bebida_sem_alcool"),
    ("Mojito Sem Álcool", "Bebida_sem_alcool"),
    ("Piña Colada Zero", "Bebida_sem_alcool"),
    ("Soda Italiana de Maçã Verde", "Bebida_sem_alcool"),
    ("Coquetel de Frutas Vermelhas", "Bebida_sem_alcool"),
    ("Iced Tea de Pêssego e Limão", "Bebida_sem_alcool"),
    ("Sunrise de Laranja e Grenadine", "Bebida_sem_alcool"),
    ("Coquetel Tropical de Coco", "Bebida_sem_alcool"),
    ("Lemonade de Extrato de Manjericão", "Bebida_sem_alcool"),
    ("Refresco de Melancia e Gengibre", "Bebida_sem_alcool"),

    # BEBIDAS COM ÁLCOOL
    ("Gin", "Bebida_com_alcool"),
    ("Uisque_de_centeio_rye", "Bebida_com_alcool"),
    ("Caipirinha", "Bebida_com_alcool"),
    ("Margarita", "Bebida_com_alcool"),
    ("Negroni", "Bebida_com_alcool"),
    ("Moscow Mule", "Bebida_com_alcool"),
    ("Cosmopolitan", "Bebida_com_alcool"),
    ("Mai Tai", "Bebida_com_alcool"),
    ("Old Fashioned", "Bebida_com_alcool"),
    ("Manhattan", "Bebida_com_alcool"),
    ("Piña Colada", "Bebida_com_alcool"),

    # BEBIDAS MISTAS
    
    ("Suco_de_abacaxi", "Bebida_mista"),
    ("Refrigerante_de_guarana", "Bebida_mista"),
    ("Agua_de_coco", "Bebida_mista"),
    ("Suco_de_melancia", "Bebida_mista"),
    ("Gin", "Bebida_mista"),
    ("Uisque_de_centeio_rye", "Bebida_mista"),
    ("Pink Lemonade", "Bebida_mista"),
    ("Mojito Sem Álcool", "Bebida_mista"),
    ("Piña Colada Zero", "Bebida_mista"),
    ("Soda Italiana de Maçã Verde", "Bebida_mista"),
    ("Caipirinha", "Bebida_mista"),
    ("Margarita", "Bebida_mista"),
    ("Negroni", "Bebida_mista"),
    ("Moscow Mule", "Bebida_mista"),
    ("Cosmopolitan", "Bebida_mista"),
    ("Mai Tai", "Bebida_mista"),
    ("Old Fashioned", "Bebida_mista"),
    ("Manhattan", "Bebida_mista"),
   
]

#nome, descrição, quantidade (em ml)
ficha_bebidas = [
    #BEBIDAS QUE O CLIENTE ESCOLHE SEM SER DO BAR
   
    ("Agua_com_gas", "Agua_com_gas", 200),
    ("Suco_de_abacaxi", "Suco_de_abacaxi", 200),
    ("Refrigerante_de_guarana", "Refrigerante_de_guarana", 200),
    ("Cha_preto", "Cha_preto", 200),
    ("Agua_de_coco", "Agua_de_coco", 200),
    ("Suco_de_melancia", "Suco_de_melancia", 200),
    ("Gin", "Gin", 70),
    ("Uisque_de_centeio_rye", "Uisque_de_centeio_rye", 70),

    # SEM ÁLCOOL - BAR

    # Pink Lemonade
    ("Pink Lemonade", "Suco_de_limao", 50),
    ("Pink Lemonade", "Xarope_de_groselha_framboesa", 20),
    ("Pink Lemonade", "Agua_com_gas", 150),

    # Mojito Sem Álcool
    ("Mojito Sem Álcool", "Suco_de_limao", 30),
    ("Mojito Sem Álcool", "Xarope_simples_de_acucar", 20),
    ("Mojito Sem Álcool", "Agua_com_gas", 150),
     ("Mojito Sem Álcool", "Folha_de_hortela", 10),


    # Piña Colada Zero
    ("Piña Colada Zero", "Suco_de_abacaxi", 120),
    ("Piña Colada Zero", "Leite_de_coco", 50),
    ("Piña Colada Zero", "Leite_condensado", 30),

    # Soda Italiana de Maçã Verde
    ("Soda Italiana de Maçã Verde", "Xarope_de_maca_verde", 30),
    ("Soda Italiana de Maçã Verde", "Agua_com_gas", 180),
    ("Soda Italiana de Maçã Verde", "Suco_de_limao", 10),

    # Coquetel de Frutas Vermelhas
    ("Coquetel de Frutas Vermelhas", "Polpa_de_frutas_vermelhas", 50),
    ("Coquetel de Frutas Vermelhas", "Suco_de_laranja", 50),
    ("Coquetel de Frutas Vermelhas", "Refrigerante_de_guarana", 100),

    # Iced Tea de Pêssego e Limão
    ("Iced Tea de Pêssego e Limão", "Cha_preto", 150),
    ("Iced Tea de Pêssego e Limão", "Xarope_de_pessego", 40),
    ("Iced Tea de Pêssego e Limão", "Suco_de_limao", 15),

    # Sunrise de Laranja e Grenadine
    ("Sunrise de Laranja e Grenadine", "Suco_de_laranja", 180),
    ("Sunrise de Laranja e Grenadine", "Xarope_de_grenadine", 20),

    # Coquetel Tropical de Coco
    ("Coquetel Tropical de Coco", "Agua_de_coco", 100),
    ("Coquetel Tropical de Coco", "Suco_de_maracuja", 50),
    ("Coquetel Tropical de Coco", "Xarope_de baunilha", 15),

    # Lemonade de Extrato de Manjericão
    ("Lemonade de Extrato de Manjericão", "Suco_de_limao", 40),
    ("Lemonade de Extrato de Manjericão", "Manjericao", 1),
    ("Lemonade de Extrato de Manjericão", "Xarope_simples_de_acucar", 25),

    # Refresco de Melancia e Gengibre
    ("Refresco de Melancia e Gengibre", "Suco_de_melancia", 150),
    ("Refresco de Melancia e Gengibre", "Suco_de_gengibre", 5),
    ("Refresco de Melancia e Gengibre", "Acucar", 25),

    # COM ÁLCOOL - BAR

    # Caipirinha
    ("Caipirinha", "Cachaca", 50),
    ("Caipirinha", "Limao", 50),
    ("Caipirinha", "Acucar", 25),

    # Margarita
    ("Margarita", "Tequila", 50),
    ("Margarita", "Cointreau_triple_sec", 25),
    ("Margarita", "Suco_de_limao", 25),
    ("Margarita", "Sal", 1),

    # Negroni
    ("Negroni", "Gin", 30),
    ("Negroni", "Campari", 30),
    ("Negroni", "Vermute_tinto", 30),
    ("Negroni", "Laranja", 5),

    # Moscow Mule
    ("Moscow Mule", "Vodka", 50),
    ("Moscow Mule", "Suco_de_limao", 15),
    ("Moscow Mule", "Ginger_beer", 120),

    # Cosmopolitan
    ("Cosmopolitan", "Vodka", 40),
    ("Cosmopolitan", "Cointreau_triple_sec", 15),
    ("Cosmopolitan", "Suco_de_cranberry", 30),
    ("Cosmopolitan", "Suco_de_limao", 15),

    # Mai Tai
    ("Mai Tai", "Rum_branco", 40),
    ("Mai Tai", "Rum_escuro", 20),
    ("Mai Tai", "Cointreau_triple_sec", 15),
    ("Mai Tai", "Xarope_de_amendoa_orgeat", 15),
    ("Mai Tai", "Suco_de_limao", 10),

    # Old Fashioned
    ("Old Fashioned", "Uisque_bourbon", 60),
    ("Old Fashioned", "Acucar", 4),
    ("Old Fashioned", "Angostura_bitters", 1),
    ("Old Fashioned", "Laranja", 5),

    # Manhattan
    ("Manhattan", "Uisque_de_centeio_rye", 60),
    ("Manhattan", "Vermute_tinto", 30),
    ("Manhattan", "Angostura_bitters", 1),
    ("Manhattan", "Cereja_marasquino", 6),

    # Piña Colada
    ("Piña Colada", "Rum_branco", 50),
    ("Piña Colada", "Suco_de_abacaxi", 90),
    ("Piña Colada", "Leite_de_coco", 30),
]

# ================================= Inicialização ESTOQUE ================================= 

def iniciar_servicos() -> list[Servico]:
    """Inicializa todos os serviços padrão que não constam no banco no momento da inicialização.

    Returns:
        list[Servico]: todos os objetos Servico a ser inicializados.
    """
    servicos=[]
    
    for nome, descricao in lista_servicos:
        nome = formatar_nome(nome)
        
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
        nome = formatar_nome(nome)
        
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

    # Slugs de imagem na ordem fixa dos seeds (quentes + salgados + bebidas).
    # Casa com _CARDAPIO_POR_ID (ids 1..18) no controller do cliente, tornando o
    # banco também fonte de verdade da imagem para os cardápios seed.
    slugs_imagem = [
        "feijoada", "bobo-camarao", "tilapia", "strogonoff", "nhoque",
        "risoto", "escondidinho", "ravioli",
        "salgados-completo", "salgados-reduzido", "hamburguer", "smash",
        "bacon", "mexicano", "boteco",
        "sem-alcool", "com-alcool", "misto",
    ]

    indice = 0
    for tipo_cardapio in lista_cardapios:
        for nome, descricao, preco_base in tipo_cardapio:
            nome = formatar_nome(nome)

            imagem_slug = slugs_imagem[indice] if indice < len(slugs_imagem) else None
            indice += 1

            if buscar_cardapio_por_nome(nome):
                continue
            
            cardapio = Cardapio(
                nome=nome,
                descricao=descricao,
                preco_base=preco_base,
                imagem_slug=imagem_slug
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
        nome = formatar_nome(nome)
        tipo_prato = tipo_prato.lower()
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

def iniciar_bebidas() -> list[Bebida]:
    """Inicializa todos os pratos padrão que não constam no banco no momento da inicialização.

    Returns:
        list[Prato]: todos os objetos Prato a ser inicializados.
    """

    bebidas=[]

    for nome, descricao, valor_unitario in lista_bebida:
        nome = formatar_nome(nome)
        
        if buscar_bebida_por_nome(nome):
            continue
        
        bebida = Bebida(
            nome=nome,
            descricao=descricao,
            valor_unitario=valor_unitario
        )
        bebidas.append(bebida)

    return bebidas

def iniciar_ingredientes() -> list[Ingrediente]:
    """Inicializa todos os ingredientes padrão que não constam no banco no momento da inicialização.
    
    Returns:
        list[Ingrediente]: todos os objetos Ingrediente a ser inicializados.
    """
        
    ingredientes=[]
    
    for tipo_ingrediente in lista_ingredientes:
        for nome, unidade, quantidade, quantidade_minima in tipo_ingrediente:
            nome = formatar_nome(nome)
            
            if buscar_ingrediente_por_nome(nome):
                continue
            
            ingrediente = Ingrediente(
                nome=nome,
                unidade=unidade,
                qtd=quantidade,
                qtd_min=quantidade_minima,
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
        nome_ingrediente = formatar_nome(nome_ingrediente)
        
        if buscar_lote_por_numero(numero):
            continue
        
        lote = Lote(
            num_lote=numero,
            marca=marca,
            data_recebimento=data_recebimento,
            data_validade=data_validade,
            qtd_inicial=quantidade_inicial,
            id_ingrediente=buscar_ingrediente_por_nome(nome_ingrediente).id_ingrediente
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

    cargos = []

    for id_cargo, nome in lista_cargos:
        cargo = buscar_permissao_por_nome(nome)

        if cargo is None:
            cargo = NivelPermissao(id_permissao=id_cargo, nome=nome.lower())
        else:
            cargo_valido = (
                cargo.id_permissao in Cargo._value2member_map_
                and cargo.nome.upper() in Cargo.__members__
            )
            
            if not cargo_valido:
                atualizado = atualizar_permissao(id_cargo, nome.lower())
                if atualizado is not None:
                    cargo = atualizado

        if cargo is not None:
            cargos.append(cargo)
    return cargos

def iniciar_admin() -> Usuario | None:
    """Cria o usuário administrador padrão quando ainda não existe.

    Lê as credenciais do admin das variáveis de ambiente (ADMIN_EMAIL,
    ADMIN_PASSWORD), criptografando os dados sensíveis.

    Returns:
        Usuario: o administrador a ser inicializado; None se já existir um admin.
    """
    
    import security
    from os import environ
    from werkzeug.security import generate_password_hash

    admin_existente = Usuario.query.filter_by(id_permissao=Cargo.ADMIN.value).first()

    if admin_existente:
        return None

    return Usuario(
        cpf_criptografado=security.criptografar("00000000000"),
        cpf_hmac=security.gerar_hmac(cpf="00000000000"),
        nome="Admin",
        email_criptografado=security.criptografar(environ.get("ADMIN_EMAIL")),
        email_hmac=security.gerar_hmac(email=environ.get("ADMIN_EMAIL")),
        senha_hash=generate_password_hash(environ.get("ADMIN_PASSWORD")),
        id_permissao=Cargo.ADMIN.value,
    )

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
        
        if ingrediente.unidade == "unidade":
            qtd_necessaria = int(qtd_necessaria)
        elif ingrediente.unidade == "g" or ingrediente.unidade == "ml":
            qtd_necessaria *= 10**3
        
        ficha = FichaTecnica(
            prato.id_prato,
            ingrediente.id_ingrediente,
            qtd_necessaria
        )

        fichas_tecnicas.append(ficha)

    return fichas_tecnicas

def iniciar_ficha_tecnica_bebida() -> list[FichaTecnica_bebida]:
    """Inicializa todas as fichas técnicas de bebidas padrão que não constam no banco no momento da inicialização.

    Returns:
        list[FichaTecnica_bebida]: todos os objetos FichaTecnica_bebida a serem inicializados.
    """

    fichas_tecnicas_bebidas = []

    for nome_bebida, nome_ingrediente, qtd_necessaria in ficha_bebidas:
        nome_bebida = formatar_nome(nome_bebida)
        nome_ingrediente = formatar_nome(nome_ingrediente)
        
        bebida = buscar_bebida_por_nome(nome_bebida)
        ingrediente = buscar_ingrediente_por_nome(nome_ingrediente)

        if not bebida or not ingrediente:
            continue

        if db.session.get(
            FichaTecnica_bebida,
            (bebida.id_bebida, ingrediente.id_ingrediente)
        ):
            continue

        ficha = FichaTecnica_bebida(
            id_bebida=bebida.id_bebida,
            id_ingrediente=ingrediente.id_ingrediente,
            qtd_necessaria=qtd_necessaria
        )

        fichas_tecnicas_bebidas.append(ficha)

    return fichas_tecnicas_bebidas 

def iniciar_servico_bancada() -> list[ServicoBancada]:
    """Inicializa a associacao servico bancada. Responsável por associar a bancada a seus devidos servicos
    """

    associacao_servico_bancada = []

    for nome_servico, nome_bancada in lista_servicos_bancadas:
        nome_servico = formatar_nome(nome_servico)
        nome_bancada = formatar_nome(nome_bancada)
        
        servico = buscar_servico_por_nome(nome_servico)
        bancada = buscar_bancada_por_nome(nome_bancada)

        if not servico or not bancada:
            continue

        if db.session.get(
            ServicoBancada,
            (servico.id_servico, bancada.id_bancada)
        ):
            continue

        associacao = ServicoBancada(
            servico.id_servico,
            bancada.id_bancada
        )

        associacao_servico_bancada.append(associacao)

    return associacao_servico_bancada

def iniciar_servico_cardapio() -> list[ServicoCardapio]:
    """Inicializa a associacao servico cardapio. Responsável por associar a cardapio a seus devidos servicos
    """

    associacao_servico_cardapio = []

    for nome_servico, nome_cardapio in lista_servicos_cardapios:
        nome_servico = formatar_nome(nome_servico)
        nome_cardapio = formatar_nome(nome_cardapio)
        
        servico = buscar_servico_por_nome(nome_servico)
        cardapio = buscar_cardapio_por_nome(nome_cardapio)

        if not servico or not cardapio:
            continue

        if db.session.get(
            ServicoCardapio,
            (servico.id_servico, cardapio.id_cardapio)
        ):
            continue

        associacao = ServicoCardapio(
            servico.id_servico,
            cardapio.id_cardapio
            
        )

        associacao_servico_cardapio.append(associacao)

    return associacao_servico_cardapio

def iniciar_prato_cardapio() -> list[PratoCardapio]:
    """Inicializa a associacao prato cardapio. Responsável por associar a cardapio a seus devidos servicos
    """

    associacao_prato_cardapio = []

    for nome_prato, nome_cardapio, qtd, descricao in lista_prato_cardapio:
        nome_prato = formatar_nome(nome_prato)
        nome_cardapio = formatar_nome(nome_cardapio)
        
        prato = buscar_servico_por_nome(nome_prato)
        cardapio = buscar_cardapio_por_nome(nome_cardapio)

        if not prato or not cardapio:
            continue

        if db.session.get(
            PratoCardapio,
            (prato.id_prato, cardapio.id_cardapio)
        ):
            continue

        associacao = PratoCardapio(
            prato.id_prato,
            cardapio.id_cardapio,
            qtd,
            descricao
        )

        associacao_prato_cardapio.append(associacao)

    return associacao_prato_cardapio

def iniciar_bebida_cardapio() -> list[BebidaCardapio]:
    """Inicializa a associacao prato cardapio. Responsável por associar a cardapio a seus devidos servicos
    """

    associacao_bebida_cardapio = []

    for nome_bebida, nome_cardapio in lista_bebida_cardapio:
        nome_bebida = formatar_nome(nome_bebida)
        nome_cardapio = formatar_nome(nome_cardapio)
        
        bebida = buscar_bebida_por_nome(nome_bebida)
        cardapio = buscar_cardapio_por_nome(nome_cardapio)

        if not bebida or not cardapio:
            continue

        if db.session.get(
            BebidaCardapio,
            (bebida.id_bebida, cardapio.id_cardapio)
        ):
            continue

        associacao = BebidaCardapio(
            id_bebida=bebida.id_bebida,
            id_cardapio=cardapio.id_cardapio
            
        )

        associacao_bebida_cardapio.append(associacao)

    return associacao_bebida_cardapio


# ================================== Inicialização USUARIOS / PEDIDOS ==================================

def _buscar_usuario_por_cpf(cpf: str) -> Usuario | None:
    """Busca um usuário pelo CPF em texto puro usando o índice HMAC.

    Usuários armazenam o CPF criptografado, então a busca é feita pelo mesmo
    HMAC determinístico gerado em iniciar_admin()/criar_usuario().

    Args:
        cpf (str): CPF em texto puro.

    Returns:
        Usuario | None: o usuário encontrado ou None.
    """
    import security

    return db.session.execute(
        db.select(Usuario).where(Usuario.cpf_hmac == security.gerar_hmac(cpf=cpf)),
    ).scalar_one_or_none()


def _buscar_usuario_por_email(email: str) -> Usuario | None:
    """Busca um usuário pelo e-mail em texto puro usando o índice HMAC.

    Args:
        email (str): e-mail em texto puro.

    Returns:
        Usuario | None: o usuário encontrado ou None.
    """
    import security

    return db.session.execute(
        db.select(Usuario).where(Usuario.email_hmac == security.gerar_hmac(email=email)),
    ).scalar_one_or_none()


def iniciar_usuarios() -> list[Usuario]:
    """Inicializa os usuários padrão (clientes e chefes) ainda inexistentes.

    Segue iniciar_admin() para os campos sensíveis: criptografa CPF/e-mail,
    gera seus HMACs de busca (UNIQUE) e aplica hash na senha. Pula usuários já
    existentes (busca por cpf_hmac/email_hmac) para manter a idempotência.

    Returns:
        list[Usuario]: todos os objetos Usuario a serem inicializados.
    """

    import security
    from werkzeug.security import generate_password_hash

    usuarios = []

    for nome, cpf, email, senha, cargo in lista_usuarios:
        if _buscar_usuario_por_cpf(cpf) or _buscar_usuario_por_email(email):
            continue

        usuario = Usuario(
            cpf_criptografado=security.criptografar(cpf),
            cpf_hmac=security.gerar_hmac(cpf=cpf),
            nome=nome,
            email_criptografado=security.criptografar(email),
            email_hmac=security.gerar_hmac(email=email),
            senha_hash=generate_password_hash(senha),
            id_permissao=cargo.value,
        )
        usuarios.append(usuario)

    return usuarios


def iniciar_enderecos() -> list[Endereco]:
    """Inicializa os endereços padrão vinculados aos clientes seed.

    Resolve o dono pelo e-mail (via HMAC) e evita duplicar endereços já
    cadastrados (mesmo dono, logradouro e número).

    Returns:
        list[Endereco]: todos os objetos Endereco a serem inicializados.
    """

    enderecos = []

    for email_dono, nome, logradouro, numero, complemento, bairro, cidade, cep, uf in lista_enderecos:
        dono = _buscar_usuario_por_email(email_dono)

        if not dono:
            continue

        existente = db.session.execute(
            db.select(Endereco).where(
                Endereco.id_usuario == dono.id_usuario,
                Endereco.logradouro == logradouro,
                Endereco.numero == str(numero),
            ),
        ).scalar_one_or_none()

        if existente:
            continue

        endereco = Endereco(
            id_usuario=dono.id_usuario,
            nome=nome,
            logradouro=logradouro,
            numero=str(numero),
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            cep=cep,
            uf=uf,
        )
        enderecos.append(endereco)

    return enderecos


def _pedidos_por_chave() -> dict:
    """Mapeia a chave lógica de cada pedido seed ao objeto Pedido persistido.

    Identifica o pedido seed pela combinação de cliente, endereço, data do
    evento e horários, todos definidos em lista_pedidos.

    Returns:
        dict: {chave_pedido: Pedido} para os pedidos seed já existentes.
    """
    from utils import hoje
    from datetime import timedelta

    mapa = {}

    for (chave, email_cliente, nome_endereco, _email_chefe, _status,
         dias, hora_inicio, hora_fim, _valor, _obs, _confirmado,
         _dias_criado, _dias_confirmado) in lista_pedidos:
        cliente = _buscar_usuario_por_email(email_cliente)
        if not cliente:
            continue

        # Mesma fórmula usada em iniciar_pedidos() para casar a dedup por
        # (id_cliente, data_evento, hora_inicio, hora_fim).
        data_evento = (hoje() + timedelta(days=dias)).date()

        pedido = db.session.execute(
            db.select(Pedido).where(
                Pedido.id_cliente == cliente.id_usuario,
                Pedido.data_evento == data_evento,
                Pedido.hora_inicio == hora_inicio,
                Pedido.hora_fim == hora_fim,
            ),
        ).scalars().first()

        if pedido:
            mapa[chave] = pedido

    return mapa


def iniciar_pedidos() -> list[Pedido]:
    """Inicializa pedidos padrão cobrindo todos os status do enum.

    Resolve cliente e chefe pelo e-mail (via HMAC) e o endereço pelo nome
    (garantindo que pertence ao cliente). As datas de evento são futuras e
    hora_fim > hora_inicio. Como o trigger de baixa de estoque é AFTER UPDATE OF
    status, inserir pedidos já confirmados não o dispara. Pula pedidos já
    existentes para manter a idempotência.

    Returns:
        list[Pedido]: todos os objetos Pedido a serem inicializados.
    """
    from utils import hoje
    from datetime import timedelta

    pedidos = []

    for (chave, email_cliente, nome_endereco, email_chefe, status,
         dias, hora_inicio, hora_fim, valor, observacao, confirmado,
         dias_criado, dias_confirmado) in lista_pedidos:
        cliente = _buscar_usuario_por_email(email_cliente)
        if not cliente:
            continue

        endereco = db.session.execute(
            db.select(Endereco).where(
                Endereco.id_usuario == cliente.id_usuario,
                Endereco.nome == nome_endereco,
            ),
        ).scalars().first()

        if not endereco:
            continue

        data_evento = (hoje() + timedelta(days=dias)).date()

        # Idempotência: não recria um pedido idêntico já existente.
        existente = db.session.execute(
            db.select(Pedido).where(
                Pedido.id_cliente == cliente.id_usuario,
                Pedido.data_evento == data_evento,
                Pedido.hora_inicio == hora_inicio,
                Pedido.hora_fim == hora_fim,
            ),
        ).scalars().first()

        if existente:
            continue

        id_chefe = None
        if email_chefe:
            chefe = _buscar_usuario_por_email(email_chefe)
            if chefe:
                id_chefe = chefe.id_usuario

        # criado_em e confirmado_em derivam de hoje() menos N dias, mantendo-se
        # SEMPRE no passado relativo à execução (determinístico e idempotente).
        # confirmado_em só é preenchido para pedidos confirmados (dias_confirmado
        # não-None), em DateTime no fuso America/Sao_Paulo (padrão de hoje()).
        agora = hoje()
        criado_em = agora - timedelta(days=dias_criado)
        confirmado_em = None
        if confirmado and dias_confirmado is not None:
            confirmado_em = agora - timedelta(days=dias_confirmado)

        pedido = Pedido(
            id_cliente=cliente.id_usuario,
            id_endereco=endereco.id_endereco,
            id_chefe=id_chefe,
            status=status,
            valor_total=valor,
            data_evento=data_evento,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim,
            observacao=observacao,
            criado_em=criado_em,
            confirmado_em=confirmado_em,
        )
        pedidos.append(pedido)

    return pedidos


def iniciar_cardapio_pedido() -> list[CardapioPedido]:
    """Inicializa as associações cardápio-pedido (com nº de convidados).

    Resolve o pedido pela chave lógica e o par (cardápio, serviço) pelos nomes,
    mantendo a consistência com as associações serviço-cardápio existentes. Pula
    associações já existentes.

    Returns:
        list[CardapioPedido]: todos os objetos CardapioPedido a inicializar.
    """
    mapa_pedidos = _pedidos_por_chave()

    associacoes = []

    for chave_pedido, nome_servico, nome_cardapio, num_convidados in lista_cardapio_pedido:
        pedido = mapa_pedidos.get(chave_pedido)
        if not pedido:
            continue

        servico = buscar_servico_por_nome(formatar_nome(nome_servico))
        cardapio = buscar_cardapio_por_nome(formatar_nome(nome_cardapio))

        if not servico or not cardapio:
            continue

        if db.session.get(
            CardapioPedido,
            (cardapio.id_cardapio, pedido.id_pedido, servico.id_servico),
        ):
            continue

        associacoes.append(
            CardapioPedido(
                id_cardapio=cardapio.id_cardapio,
                id_pedido=pedido.id_pedido,
                id_servico=servico.id_servico,
                num_convidados=num_convidados,
            ),
        )

    return associacoes


def iniciar_pedido_bebida() -> list[PedidoBebida]:
    """Inicializa as bebidas avulsas de alguns pedidos.

    Resolve o pedido pela chave lógica e a bebida pelo nome; calcula o
    valor_total como valor_unitario * qtd. Pula vínculos já existentes.

    Returns:
        list[PedidoBebida]: todos os objetos PedidoBebida a inicializar.
    """
    mapa_pedidos = _pedidos_por_chave()

    associacoes = []

    for chave_pedido, nome_bebida, qtd in lista_pedido_bebida:
        pedido = mapa_pedidos.get(chave_pedido)
        if not pedido:
            continue

        bebida = buscar_bebida_por_nome(formatar_nome(nome_bebida))
        if not bebida:
            continue

        if db.session.get(PedidoBebida, (pedido.id_pedido, bebida.id_bebida)):
            continue

        associacoes.append(
            PedidoBebida(
                id_pedido=pedido.id_pedido,
                id_bebida=bebida.id_bebida,
                qtd=qtd,
                valor_total=bebida.valor_unitario * qtd,
            ),
        )

    return associacoes


def iniciar_logs() -> list[LogAtividade]:
    """Inicializa registros de auditoria seed para os usuários criados.

    Resolve o usuário pelo e-mail (via HMAC). Pula logs já existentes
    (mesmo usuário, ação e descrição) para manter a idempotência.

    Returns:
        list[LogAtividade]: todos os objetos LogAtividade a inicializar.
    """

    logs = []

    for email_usuario, acao, descricao in lista_logs:
        usuario = _buscar_usuario_por_email(email_usuario)
        if not usuario:
            continue

        existente = db.session.execute(
            db.select(LogAtividade).where(
                LogAtividade.id_usuario == usuario.id_usuario,
                LogAtividade.acao == acao,
                LogAtividade.descricao == descricao,
            ),
        ).scalars().first()

        if existente:
            continue

        logs.append(
            LogAtividade(
                acao=acao,
                id_usuario=usuario.id_usuario,
                descricao=descricao,
            ),
        )

    return logs


def iniciar_tokens() -> list[Token]:
    """Inicializa tokens de verificação seed para os usuários criados.

    O codigo_hash é o HMAC-SHA256 do código com a chave TOKEN_SHA, exatamente
    como security/token_auth.py gera e valida os tokens (nunca em texto puro).
    Pula a criação quando a chave TOKEN_SHA não está configurada ou quando o
    usuário já possui tokens (idempotência).

    Returns:
        list[Token]: todos os objetos Token a inicializar.
    """

    import hashlib
    import hmac
    from os import environ as env

    chave = env.get("TOKEN_SHA")

    # security/token_auth.py lança RuntimeError quando TOKEN_SHA não está
    # configurada. Aqui a ausência da chave apenas pula os tokens, pois a
    # seed não deve ser fatal quando a variável opcional não existe.
    if not chave:
        return []

    tokens = []

    for email_usuario, codigo, ativo, tentativas in lista_tokens:
        usuario = _buscar_usuario_por_email(email_usuario)
        if not usuario:
            continue

        ja_tem_token = db.session.execute(
            db.select(Token).where(Token.id_usuario == usuario.id_usuario),
        ).scalars().first()

        if ja_tem_token:
            continue

        codigo_hash = hmac.new(
            chave.encode("utf-8"),
            codigo.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        tokens.append(
            Token(
                codigo_hash=codigo_hash,
                id_usuario=usuario.id_usuario,
                ativo=ativo,
                tentativas=tentativas,
            ),
        )

    return tokens

