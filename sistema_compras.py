# sistema_compras.py

import os


class SistemaCompras:
    def __init__(self, valor_minimo_frete_gratis: float = 100.0):
        self.valor_minimo_frete_gratis = valor_minimo_frete_gratis
        self.historico_compras = []
        self._proximo_id = 1

    def calcular_total(self, itens: list[dict]) -> float:
        """Calcula o valor total do carrinho de compras."""
        if not itens:
            raise ValueError("A lista de compras não pode estar vazia.")

        total = 0.0
        for item in itens:
            preco = item.get("preco")
            quantidade = item.get("quantidade")

            if preco is None or quantidade is None:
                raise ValueError("Cada item deve ter 'preco' e 'quantidade'.")
            if preco < 0 or quantidade <= 0:
                raise ValueError("Preço não pode ser negativo e quantidade deve ser maior que zero.")

            total += preco * quantidade

        return round(total, 2)

    def aplicar_desconto(self, valor_total: float, porcentagem_desconto: float) -> float:
        """Aplica desconto percentual sobre o valor total."""
        if valor_total < 0:
            raise ValueError("O valor total não pode ser negativo.")
        if porcentagem_desconto < 0 or porcentagem_desconto > 100:
            raise ValueError("A porcentagem de desconto deve estar entre 0% e 100%.")

        desconto = valor_total * (porcentagem_desconto / 100)
        return round(valor_total - desconto, 2)

    def verificar_frete_gratis(self, valor_final: float) -> bool:
        """Verifica elegibilidade para frete grátis."""
        if valor_final < 0:
            raise ValueError("O valor final não pode ser negativo.")

        return valor_final >= self.valor_minimo_frete_gratis

    def registrar_compra(self, carrinho: list[dict], valor_bruto: float, desconto: float, valor_final: float, frete_gratis: bool) -> int:
        """Salva a compra finalizada no histórico com ID autoincrementado."""
        id_compra = self._proximo_id
        registro = {
            "id": id_compra,
            "itens": [item.copy() for item in carrinho],
            "valor_bruto": valor_bruto,
            "desconto_pct": desconto,
            "valor_final": valor_final,
            "frete_gratis": frete_gratis
        }
        self.historico_compras.append(registro)
        self._proximo_id += 1
        return id_compra


# =====================================================================
# INTERFACE AMIGÁVEL COM O USUÁRIO (MENU INTERATIVO NO TERMINAL)
# =====================================================================

def limpar_tela():
    """Limpa o terminal compatível com Windows e Linux/macOS."""
    os.system('cls' if os.name == 'nt' else 'clear')


def solicitar_input(mensagem: str):
    """Lê uma entrada do usuário e permite cancelar se for digitado 'c' ou 'cancelar'."""
    entrada = input(mensagem).strip()
    if entrada.lower() in ['c', 'cancelar']:
        return None
    return entrada


def exibir_carrinho(carrinho: list[dict]):
    """Exibe o conteúdo do carrinho formatado."""
    if not carrinho:
        print("\n🛒 Carrinho atual: [ VAZIO ]")
        return

    print("\n" + "-"*50)
    print(" 🛒 CARRINHO DE COMPRAS ATUAL")
    print("-"*50)
    for idx, item in enumerate(carrinho, start=1):
        subtotal = item['preco'] * item['quantidade']
        print(f"{idx}. {item['nome']} - {item['quantidade']}x R$ {item['preco']:.2f} = R$ {subtotal:.2f}")
    print("-"*50)


def menu_gerenciar_carrinho(sistema: SistemaCompras, carrinho: list[dict]):
    """Menu para adicionar, editar e remover itens do carrinho."""
    while True:
        limpar_tela()
        exibir_carrinho(carrinho)
        print("\nOpções do Carrinho:")
        print("1. Adicionar produto")
        print("2. Editar item (Nome, Preço ou Quantidade)")
        print("3. Excluir item")
        print("4. Finalizar compra e ir para o pagamento")
        print("0. Esvaziar todo o carrinho e voltar ao Menu Principal")

        opcao = input("\nEscolha uma opção: ").strip()

        # --- 1. ADICIONAR PRODUTO ---
        if opcao == '1':
            limpar_tela()
            print("--- ADICIONAR PRODUTO (Digite 'c' para cancelar) ---\n")
            
            nome = solicitar_input("Nome do produto: ")
            if nome is None:
                print("\n🚫 Adição cancelada. O produto não foi adicionado.")
                input("\nPressione [ENTER] para continuar...")
                continue
            if not nome:
                print("\n⚠️ O nome do produto não pode ser vazio.")
                input("\nPressione [ENTER] para continuar...")
                continue

            str_preco = solicitar_input(f"Preço unitário de '{nome}' (R$): ")
            if str_preco is None:
                print("\n🚫 Adição cancelada. O produto não foi adicionado.")
                input("\nPressione [ENTER] para continuar...")
                continue

            str_qtd = solicitar_input(f"Quantidade de '{nome}': ")
            if str_qtd is None:
                print("\n🚫 Adição cancelada. O produto não foi adicionado.")
                input("\nPressione [ENTER] para continuar...")
                continue

            try:
                preco = float(str_preco)
                quantidade = int(str_qtd)
                sistema.calcular_total([{"preco": preco, "quantidade": quantidade}])
                carrinho.append({"nome": nome, "preco": preco, "quantidade": quantidade})
                print(f"\n✅ '{nome}' adicionado ao carrinho com sucesso!")
            except ValueError as err:
                print(f"\n❌ Entrada inválida: {err}")
            input("\nPressione [ENTER] para continuar...")

        # --- 2. EDITAR ITEM ---
        elif opcao == '2':
            if not carrinho:
                print("\n⚠️ O carrinho está vazio. Nada para editar.")
                input("\nPressione [ENTER] para continuar...")
                continue
            
            str_num = solicitar_input("\nDigite o número do item que deseja editar (ou 'c' para cancelar): ")
            if str_num is None:
                print("\n🚫 Edição cancelada.")
                input("\nPressione [ENTER] para continuar...")
                continue

            try:
                num = int(str_num)
                if 1 <= num <= len(carrinho):
                    item = carrinho[num - 1]
                    print(f"\nEditando: '{item['nome']}' | R$ {item['preco']:.2f} | Qtd: {item['quantidade']}")
                    print("(Pressione [ENTER] sem digitar nada para manter o valor atual ou 'c' para cancelar)")

                    novo_nome = solicitar_input(f"Novo nome [{item['nome']}]: ")
                    if novo_nome is None:
                        print("\n🚫 Edição cancelada. O item permanece sem alterações.")
                        input("\nPressione [ENTER] para continuar...")
                        continue
                    nome_final = novo_nome if novo_nome != "" else item['nome']

                    str_novo_preco = solicitar_input(f"Novo preço [{item['preco']:.2f}]: ")
                    if str_novo_preco is None:
                        print("\n🚫 Edição cancelada. O item permanece sem alterações.")
                        input("\nPressione [ENTER] para continuar...")
                        continue
                    preco_final = float(str_novo_preco) if str_novo_preco != "" else item['preco']

                    str_nova_qtd = solicitar_input(f"Nova quantidade [{item['quantidade']}]: ")
                    if str_nova_qtd is None:
                        print("\n🚫 Edição cancelada. O item permanece sem alterações.")
                        input("\nPressione [ENTER] para continuar...")
                        continue
                    qtd_final = int(str_nova_qtd) if str_nova_qtd != "" else item['quantidade']

                    sistema.calcular_total([{"preco": preco_final, "quantidade": qtd_final}])
                    item['nome'] = nome_final
                    item['preco'] = preco_final
                    item['quantidade'] = qtd_final
                    print(f"\n✅ Item atualizado com sucesso!")
                else:
                    print("\n⚠️ Número do item inválido.")
            except ValueError as err:
                print(f"\n❌ Erro na alteração: {err}")
            input("\nPressione [ENTER] para continuar...")

        # --- 3. EXCLUIR ITEM ---
        elif opcao == '3':
            if not carrinho:
                print("\n⚠️ O carrinho está vazio. Nada para excluir.")
                input("\nPressione [ENTER] para continuar...")
                continue
            
            str_num = solicitar_input("\nDigite o número do item que deseja excluir (ou 'c' para cancelar): ")
            if str_num is None:
                print("\n🚫 Remoção cancelada.")
                input("\nPressione [ENTER] para continuar...")
                continue

            try:
                num = int(str_num)
                if 1 <= num <= len(carrinho):
                    removido = carrinho.pop(num - 1)
                    print(f"\n🗑️ Item '{removido['nome']}' removido do carrinho com sucesso!")
                else:
                    print("\n⚠️ Número do item inválido.")
            except ValueError:
                print("\n❌ Por favor, digite um número válido.")
            input("\nPressione [ENTER] para continuar...")

        # --- 4. IR PARA O PAGAMENTO ---
        elif opcao == '4':
            if not carrinho:
                print("\n⚠️ Seu carrinho está vazio! Adicione pelo menos um item antes de finalizar.")
                input("\nPressione [ENTER] para continuar...")
                continue
            break

        # --- 0. ESVAZIAR CARRINHO E SAIR ---
        elif opcao == '0':
            carrinho.clear()
            print("\n🗑️ O carrinho foi completamente esvaziado. Retornando ao Menu Principal...")
            input("\nPressione [ENTER] para continuar...")
            return False

        else:
            print("\n⚠️ Opção inválida. Digite um número de 0 a 4.")
            input("\nPressione [ENTER] para continuar...")

    return True


def visualizar_historico(sistema: SistemaCompras):
    """Exibe as compras salvas ordenadas pelo ID autoincrementado."""
    limpar_tela()
    print("="*50)
    print(" 📜 HISTÓRICO DE ÚLTIMAS COMPRAS")
    print("="*50)

    if not sistema.historico_compras:
        print("\nNenhuma compra foi registrada até o momento.")
    else:
        for compra in sistema.historico_compras:
            print(f"\n📦 COMPRA #{compra['id']}")
            print("-" * 30)
            for item in compra['itens']:
                subtotal = item['preco'] * item['quantidade']
                print(f" • {item['nome']}: {item['quantidade']}x R$ {item['preco']:.2f} = R$ {subtotal:.2f}")
            print(f" • Valor Bruto: R$ {compra['valor_bruto']:.2f}")
            print(f" • Desconto Aplicado: {compra['desconto_pct']}%")
            print(f" • Valor Final Pago: R$ {compra['valor_final']:.2f}")
            print(f" • Frete Grátis: {'SIM' if compra['frete_gratis'] else 'NÃO'}")

    print("\n" + "="*50)
    input("\nPressione [ENTER] para voltar ao Menu Principal...")


def menu_interativo():
    sistema = SistemaCompras(valor_minimo_frete_gratis=100.0)

    while True:
        limpar_tela()
        print("="*45)
        print(" 🛒 SISTEMA DE COMPRAS - MENU PRINCIPAL")
        print("="*45)
        print("1. Iniciar Nova Compra / Gerenciar Carrinho")
        print("2. Visualizar Histórico de Compras (IDs)")
        print("0. Encerrar Aplicação")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '0':
            limpar_tela()
            print("\n👋 Obrigado por utilizar o Sistema de Compras! Até logo!\n")
            break

        elif opcao == '2':
            visualizar_historico(sistema)

        elif opcao == '1':
            carrinho = []
            
            while True:
                # Etapa 1: Gerenciamento do Carrinho
                avancar = menu_gerenciar_carrinho(sistema, carrinho)
                if not avancar or not carrinho:
                    break  # Sai do loop de compra e volta ao menu principal

                # Etapa 2: Cálculo e aplicação de Desconto
                limpar_tela()
                print("="*45)
                print(" 🎟️ APURAÇÃO E DESCONTO")
                print("="*45)
                total_bruto = sistema.calcular_total(carrinho)
                print(f"\n💰 Valor Total Bruto: R$ {total_bruto:.2f}")

                pct_desconto = 0.0
                cancelou_pagamento = False

                while True:
                    opc_desconto = solicitar_input("\nDeseja aplicar um cupom de desconto? (s/n ou 'c' para voltar ao carrinho): ")
                    if opc_desconto is None:
                        print("\n🔄 Processo de pagamento interrompido. Seus itens continuam no carrinho!")
                        input("\nPressione [ENTER] para voltar ao carrinho...")
                        cancelou_pagamento = True
                        break

                    opc_desconto = opc_desconto.lower()
                    if opc_desconto == 's':
                        str_pct = solicitar_input("Digite a porcentagem de desconto (0 a 100% ou 'c' para cancelar): ")
                        if str_pct is None:
                            print("\n🔄 Processo de pagamento interrompido. Seus itens continuam no carrinho!")
                            input("\nPressione [ENTER] para voltar ao carrinho...")
                            cancelou_pagamento = True
                            break
                        try:
                            pct_desconto = float(str_pct)
                            valor_final = sistema.aplicar_desconto(total_bruto, pct_desconto)
                            print(f"🎉 Desconto de {pct_desconto}% aplicado com sucesso!")
                            break
                        except ValueError as err:
                            print(f"❌ Erro ao aplicar desconto: {err}. Tente novamente.")
                    else:
                        valor_final = total_bruto
                        break

                if cancelou_pagamento:
                    continue  # Retorna ao loop do carrinho sem apagar os itens!

                # Etapa 3: Verificação de Frete e Finalização
                tem_frete_gratis = sistema.verificar_frete_gratis(valor_final)

                print("\n" + "="*45)
                print(" 💳 FECHAMENTO DO PEDIDO")
                print("="*45)
                print(f"💵 Valor Final a Pagar: R$ {valor_final:.2f}")
                if tem_frete_gratis:
                    print("🚚 Frete: GRATUITO! (Compra a partir de R$ 100,00)")
                else:
                    print("🚚 Frete: PAGO (Adicione mais itens para atingir R$ 100,00 e ter frete grátis)")
                print("="*45)
                
                # Registra a compra e limpa a sessão local
                id_gerado = sistema.registrar_compra(
                    carrinho=carrinho,
                    valor_bruto=total_bruto,
                    desconto=pct_desconto,
                    valor_final=valor_final,
                    frete_gratis=tem_frete_gratis
                )
                print(f"\n✅ Pagamento realizado com sucesso! Compra registrada sob o ID #{id_gerado}.")

                input("\nPressione [ENTER] para retornar ao Menu Principal...")
                break

        else:
            print("\n⚠️ Opção inválida! Escolha 1, 2 ou 0.")
            input("\nPressione [ENTER] para continuar...")


if __name__ == "__main__":
    menu_interativo()