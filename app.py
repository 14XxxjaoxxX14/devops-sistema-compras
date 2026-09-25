from flask import Flask, render_template, request, redirect, url_for, session, flash
from sistema_compras import SistemaCompras

app = Flask(__name__)
app.secret_key = "chave_secreta_super_segura_para_sessoes"

sistema = SistemaCompras(valor_minimo_frete_gratis=100.0)

@app.route('/')
def index():
    if 'carrinho' not in session:
        session['carrinho'] = []
    if 'desconto' not in session:
        session['desconto'] = 0.0

    carrinho = session['carrinho']
    desconto_pct = session['desconto']

    valor_bruto = 0.0
    valor_final = 0.0
    frete_gratis = False

    if carrinho:
        try:
            valor_bruto = sistema.calcular_total(carrinho)
            valor_final = sistema.aplicar_desconto(valor_bruto, desconto_pct)
            frete_gratis = sistema.verificar_frete_gratis(valor_final)
        except ValueError as e:
            flash(str(e), "erro")

    return render_template(
        'index.html',
        carrinho=carrinho,
        valor_bruto=valor_bruto,
        desconto_pct=desconto_pct,
        valor_final=valor_final,
        frete_gratis=frete_gratis,
        historico=sistema.historico_compras
    )

@app.route('/adicionar', methods=['POST'])
def adicionar_item():
    nome = request.form.get('nome', '').strip()
    try:
        preco = float(request.form.get('preco', 0))
        quantidade = int(request.form.get('quantidade', 0))

        if not nome:
            flash("O nome do produto é obrigatório.", "erro")
            return redirect(url_for('index'))

        # Validação através do sistema
        sistema.calcular_total([{"preco": preco, "quantidade": quantidade}])

        carrinho = session.get('carrinho', [])
        carrinho.append({"nome": nome, "preco": preco, "quantidade": quantidade})
        session['carrinho'] = carrinho
        flash(f"'{nome}' adicionado ao carrinho!", "sucesso")
    except ValueError as e:
        flash(f"Erro ao adicionar item: {e}", "erro")

    return redirect(url_for('index'))

@app.route('/remover/<int:idx>', methods=['POST'])
def remover_item(idx):
    carrinho = session.get('carrinho', [])
    if 0 <= idx < len(carrinho):
        removido = carrinho.pop(idx)
        session['carrinho'] = carrinho
        flash(f"'{removido['nome']}' foi removido do carrinho.", "sucesso")
    return redirect(url_for('index'))

@app.route('/desconto', methods=['POST'])
def aplicar_desconto():
    try:
        pct = float(request.form.get('desconto', 0))
        if 0 <= pct <= 100:
            session['desconto'] = pct
            flash(f"Desconto de {pct}% aplicado!", "sucesso")
        else:
            flash("A porcentagem de desconto deve ser entre 0% e 100%.", "erro")
    except ValueError:
        flash("Porcentagem de desconto inválida.", "erro")
    
    return redirect(url_for('index'))

@app.route('/limpar', methods=['POST'])
def limpar_carrinho():
    session['carrinho'] = []
    session['desconto'] = 0.0
    flash("Carrinho esvaziado.", "sucesso")
    return redirect(url_for('index'))

@app.route('/finalizar', methods=['POST'])
def finalizar_compra():
    carrinho = session.get('carrinho', [])
    desconto_pct = session.get('desconto', 0.0)

    if not carrinho:
        flash("Seu carrinho está vazio!", "erro")
        return redirect(url_for('index'))

    try:
        valor_bruto = sistema.calcular_total(carrinho)
        valor_final = sistema.aplicar_desconto(valor_bruto, desconto_pct)
        frete_gratis = sistema.verificar_frete_gratis(valor_final)

        id_compra = sistema.registrar_compra(
            carrinho=carrinho,
            valor_bruto=valor_bruto,
            desconto=desconto_pct,
            valor_final=valor_final,
            frete_gratis=frete_gratis
        )

        session['carrinho'] = []
        session['desconto'] = 0.0
        flash(f"Compra #{id_compra} registrada com sucesso!", "sucesso")
    except ValueError as e:
        flash(f"Erro ao finalizar compra: {e}", "erro")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)