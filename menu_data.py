"""Dados estáticos dos cardápios de apresentação da home/menu.

    Baseado em docs/documentos/Cardapio.md. Define a estrutura `categorias`,
    uma lista de categorias (pratos quentes, salgados e bebidas), cada uma com
    seus itens.
    """
    
categorias = [
    {'id': 'quentes', 'nome': 'Pratos quentes', 'resumo': 'Receitas que acolhem, sabores que ficam.', 'itens': [
        ('Feijoada completa', 'Feijoada com arroz branco, couve refogada, farofa, vinagrete e molho de pimenta. Acompanha tábua de frios e mandioca frita. Sobremesa incluída: sorvete de maracujá e limão.', 'quentes', 0),
        ('Bobó de camarão', 'Bobó de camarão com arroz branco e salada fresca. Sobremesa incluída: salada de frutas com creme.', 'quentes', 1),
        ('Tilápia com alcaparras', 'Filé de tilápia ao molho de manteiga e alcaparras, com arroz branco e bruschetta. Sobremesa incluída: iogurte natural com morangos e mel.', 'quentes', 2),
        ('Strogonoff de filé-mignon', 'Strogonoff de filé-mignon com arroz branco, batata palha e salada Caesar. Sobremesa incluída: pudim de leite condensado.', 'quentes', 3),
        ('Nhoque ao molho', 'Nhoque ao molho bolonhesa ou de queijo, acompanhado de mix de folhas. Sobremesa incluída: mousse de maracujá.', 'quentes', 4),
        ('Risoto de cogumelos', 'Risoto de cogumelos com tiras de filé-mignon e bruschetta. Sobremesa incluída: brownie de chocolate.', 'quentes', 5),
        ('Escondidinho de carne-seca', 'Escondidinho de carne-seca com purê de mandioca, acompanhado de dadinhos de tapioca e geleia de pimenta. Sobremesa incluída: cheesecake de frutas vermelhas.', 'quentes', 6),
        ('Ravioli de queijo', 'Ravioli de queijo ao molho bolonhesa, com parmesão ralado e tábua de frios. Sobremesa incluída: mousse de chocolate.', 'quentes', 7),
    ]},
    {'id': 'salgados', 'nome': 'Salgados & encontros', 'resumo': 'Para compartilhar e celebrar à sua maneira.', 'itens': [
        ('Salgados completo', 'Coxinha, risole, quibe, bolinha de queijo, empada e croquete, com batata frita, queijo, embutidos e pães. Doces incluídos: brigadeiro, beijinho e bolo.', 'extras', 0),
        ('Salgados reduzido', 'Coxinha, risole e bolinha de queijo, com batata frita, queijo e presunto. Doces incluídos: brigadeiro e bolo simples.', 'extras', 0),
        ('Hambúrguer tradicional', 'Pão brioche, carne bovina, cheddar, alface, tomate, cebola caramelizada, maionese temperada e barbecue. Acompanha batata frita, molho mostarda e mel e onion rings.', 'extras', 1),
        ('Hambúrguer smash', 'Pão brioche, blend de carnes, queijo picado, cheddar, maionese temperada, manteiga e cebola caramelizada. Acompanha batata frita e onion rings.', 'extras', 1),
        ('Hambúrguer mega bacon', 'Pão brioche, carne bovina, quatro fatias de cheddar, alface, cebola caramelizada, maionese temperada e barbecue. Acompanha batata frita, molho mostarda e mel e onion rings.', 'extras', 1),
        ('Mexicano', 'Tortillas de milho com carne moída temperada, alface, tomate e queijo ralado. Acompanha nachos, guacamole e quesadilla com tortilla de trigo, frango ou queijo e pimentão.', 'extras', 2),
        ('Boteco brasileiro', 'Coxinha, pastel de carne, bolinho de bacalhau, linguiça acebolada, batata palha e pastel de queijo. Sobremesa incluída: iogurte natural com morangos e mel.', 'extras', 3),
    ]},
    {'id': 'bebidas', 'nome': 'Bebidas para brindar', 'resumo': 'Do primeiro refresco ao último brinde.', 'itens': [
        ('Sem álcool', 'Uma seleção de sucos, refrigerantes, águas e bebidas sem álcool.', 'extras', 4),
        ('Com álcool', 'Uma seleção de bebidas alcoólicas e coquetéis para o evento.', 'extras', 5),
        ('Misto', 'Opções com e sem álcool para diferentes preferências.', 'extras', 6),
    ]},
]
