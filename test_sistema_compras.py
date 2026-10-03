# test_sistema_compras.py

import pytest
from unittest.mock import patch
from sistema_compras import SistemaCompras, solicitar_input, exibir_carrinho

# =====================================================================
# FIXTURES E CONFIGURAÇÕES DE TESTE
# =====================================================================

@pytest.fixture
def sistema():
    """Instancia a classe principal do sistema antes de cada teste."""
    return SistemaCompras(valor_minimo_frete_gratis=100.0)


@pytest.fixture
def carrinho_exemplo():
    """Fornece um carrinho pronto para testes de cálculo e histórico."""
    return [
        {"nome": "Mouse Gamer", "preco": 50.0, "quantidade": 2},
        {"nome": "Teclado Mecânico", "preco": 150.0, "quantidade": 1}
    ]


# =====================================================================
# 1. TESTES DE CÁLCULO DE TOTAL (calcular_total)
# =====================================================================

def test_calcular_total_com_sucesso(sistema, carrinho_exemplo):
    """Garante o cálculo correto da soma de itens do carrinho."""
    # (50.0 * 2) + (150.0 * 1) = 250.0
    total = sistema.calcular_total(carrinho_exemplo)
    assert total  250.0


def test_calcular_total_carrinho_vazio_lanca_excecao(sistema):
    """Verifica se lança erro ao tentar calcular total de um carrinho vazio."""
    with pytest.raises(ValueError, match="A lista de compras não pode estar vazia."):
        sistema.calcular_total([])


def test_calcular_total_preco_negativo_lanca_excecao(sistema):
    """Garante validação para preços negativos."""
    itens_invalidos = [{"nome": "Item Inválido", "preco": -10.0, "quantidade": 1}]
    with pytest.raises(ValueError, match="Preço não pode ser negativo e quantidade deve ser maior que zero."):
        sistema.calcular_total(itens_invalidos)


def test_calcular_total_quantidade_invalida_lanca_excecao(sistema):
    """Garante validação para quantidades menores ou iguais a zero."""
    itens_invalidos = [{"nome": "Item Inválido", "preco": 10.0, "quantidade": 0}]
    with pytest.raises(ValueError, match="Preço não pode ser negativo e quantidade deve ser maior que zero."):
        sistema.calcular_total(itens_invalidos)


def test_calcular_total_chaves_ausentes_lanca_excecao(sistema):
    """Garante erro caso a estrutura do dicionário esteja incompleta."""
    itens_incompletos = [{"nome": "Sem Preço", "quantidade": 1}]
    with pytest.raises(ValueError, match="Cada item deve ter 'preco' e 'quantidade'."):
        sistema.calcular_total(itens_incompletos)


# =====================================================================
# 2. TESTES DE APLICAÇÃO DE DESCONTO (aplicar_desconto)
# =====================================================================

def test_aplicar_desconto_sucesso(sistema):
    """Verifica aplicação correta de porcentagem de desconto."""
    # R$ 200.00 com 10% de desconto = R$ 180.00
    assert sistema.aplicar_desconto(200.0, 10.0) == 180.0


def test_aplicar_desconto_zero_porcento(sistema):
    """Testa desconto de 0% mantendo o valor original."""
    assert sistema.aplicar_desconto(100.0, 0.0) == 100.0


def test_aplicar_desconto_cem_porcento(sistema):
    """Testa desconto máximo de 100% zera o valor total."""
    assert sistema.aplicar_desconto(100.0, 100.0) == 0.0


def test_aplicar_desconto_valor_total_negativo_lanca_excecao(sistema):
    """Impede aplicação de desconto sobre totais negativos."""
    with pytest.raises(ValueError, match="O valor total não pode ser negativo."):
        sistema.aplicar_desconto(-50.0, 10.0)


@pytest.mark.parametrize("desconto_invalido", [-5.0, 105.0])
def test_aplicar_desconto_porcentagem_fora_dos_limites(sistema, desconto_invalido):
    """Garante erro se desconto for menor que 0% ou maior que 100%."""
    with pytest.raises(ValueError, match="A porcentagem de desconto deve estar entre 0% e 100%."):
        sistema.aplicar_desconto(100.0, desconto_invalido)


# =====================================================================
# 3. TESTES DE ELEGIBILIDADE DE FRETE (verificar_frete_gratis)
# =====================================================================

def test_verificar_frete_gratis_elegivel(sistema):
    """Verifica se valores acima do mínimo recebem frete grátis."""
    assert sistema.verificar_frete_gratis(150.0) is True


def test_verificar_frete_gratis_limite_exato(sistema):
    """Verifica no limite exato da regra (R$ 100.00)."""
    assert sistema.verificar_frete_gratis(100.0) is True


def test_verificar_frete_gratis_nao_elegivel(sistema):
    """Verifica valores abaixo do limite de frete grátis."""
    assert sistema.verificar_frete_gratis(99.99) is False


def test_verificar_frete_gratis_valor_negativo_lanca_excecao(sistema):
    """Garante erro para valores finais negativos."""
    with pytest.raises(ValueError, match="O valor final não pode ser negativo."):
        sistema.verificar_frete_gratis(-10.0)


# =====================================================================
# 4. TESTES DE HISTÓRICO E ID AUTOINCREMENTADO (registrar_compra)
# =====================================================================

def test_registrar_compra_autoincremento_id(sistema, carrinho_exemplo):
    """Garante que cada nova compra recebe um ID incremental (1, 2, 3...)."""
    id1 = sistema.registrar_compra(carrinho_exemplo, 250.0, 0.0, 250.0, True)
    id2 = sistema.registrar_compra(carrinho_exemplo, 250.0, 10.0, 225.0, True)

    assert id1 == 1
    assert id2 == 2
    assert len(sistema.historico_compras) == 2


def test_registrar_compra_copia_independente_do_carrinho(sistema, carrinho_exemplo):
    """Garante que a alteração do carrinho local não afeta a compra no histórico."""
    sistema.registrar_compra(carrinho_exemplo, 250.0, 0.0, 250.0, True)
    
    # Modifica o carrinho local após salvar
    carrinho_exemplo[0]["nome"] = "Nome Alterado"

    # O histórico deve preservar os dados da época do registro
    assert sistema.historico_compras[0]["itens"][0]["nome"] == "Mouse Gamer"


# =====================================================================
# 5. TESTES DE FUNÇÕES UTILITÁRIAS DA INTERFACE (INPUTS E CANCELAMENTO)
# =====================================================================

@pytest.mark.parametrize("comando_cancelar", ["c", "C", "cancelar", "CANCELAR"])
def test_solicitar_input_retorna_none_ao_cancelar(comando_cancelar):
    """Garante que 'c' ou 'cancelar' acionam a sinalização de cancelamento (None)."""
    with patch("builtins.input", return_value=comando_cancelar):
        resultado = solicitar_input("Digite o nome: ")
        assert resultado is None


def test_solicitar_input_retorna_string_valida():
    """Garante que dados válidos inseridos retornam normalmente."""
    with patch("builtins.input", return_value=" Monitor LED "):
        resultado = solicitar_input("Digite o nome: ")
        assert resultado == "Monitor LED"


def test_exibir_carrinho_vazio_e_com_itens(capsys, carrinho_exemplo):
    """Garante que a saída formatada do carrinho não lança exceções."""
    # Teste de renderização vazio
    exibir_carrinho([])
    captured_vazio = capsys.readouterr()
    assert "🛒 Carrinho atual: [ VAZIO ]" in captured_vazio.out

    # Teste de renderização preenchido
    exibir_carrinho(carrinho_exemplo)
    captured_cheio = capsys.readouterr()
    assert "Mouse Gamer" in captured_cheio.out
    assert "Teclado Mecânico" in captured_cheio.out