import pandas as pd
import ast
import pyautogui as pg
import pyperclip as pc



def gerar_mensagens(df):
    """
    Recebe o DataFrame da planilha e retorna duas listas:
    telefones (str) e mensagens (str).
    """
    lista_telefones = []
    lista_mensagens = []

    # --- Funções Internas de Apoio ---
    def calcular_valor(row):
        try: t_dict = ast.literal_eval(row['Tamanhos'])
        except: t_dict = {'camisa': [], 'calça': [], 'top': []}
        
        pedido_orig = str(row['Pedidos'])
        gestao = str(row['Gestao']).lower() == 'sim'
        
        p_camisa, p_calca, p_top = (60, 80, 40) if gestao else (75, 100, 55)
        n_cam, n_cal = len(t_dict.get('camisa', [])), len(t_dict.get('calça', []))
        n_top = 1 if "Top" in pedido_orig or "Kit Top" in pedido_orig else 0
        
        total = 0
        if not gestao:
            if "Calça" in pedido_orig and "Camisa" in pedido_orig and "Kit" in pedido_orig:
                total += 165
                n_cam -= 1; n_cal -= 1
            elif "Calça" in pedido_orig and "Kit" in pedido_orig and "Camisa" not in pedido_orig:
                total += 145
                n_cal -= 1; n_top -= 1
        
        total += (max(0, n_cam) * p_camisa) + (max(0, n_cal) * p_calca) + (max(0, n_top) * p_top)
        return total

    def formatar_tamanhos(row, pedido_nome):
        try:
            t_dict = ast.literal_eval(row['Tamanhos'])
            partes = []
            if t_dict.get('camisa'): partes.append(f"Camisa: {', '.join(t_dict['camisa'])}")
            if t_dict.get('calça'): partes.append(f"Calça: {', '.join(t_dict['calça'])}")
            if "Top" in pedido_nome: partes.append("Top: não informado")
            return " | ".join(partes)
        except: return "Não informado"

    def ajustar_nome(p):
        p = str(p)
        if "Calça" in p and "Camisa" in p and "Kit" in p: return "Kit Camisa com Calça"
        if "Calça" in p and "Kit" in p and "Camisa" not in p: return "Kit Top com Calça"
        return p

    def limpar_listas(v):
        try:
            if isinstance(v, list):
                lista = v
            else:
                lista = ast.literal_eval(str(v))

            nova_lista = []
            for x in lista:
                x_str = str(x).strip()

                if x_str != "":
                    try:
                        x_str = str(int(float(x_str)))  # remove .0
                    except:
                        pass

                    nova_lista.append(x_str)

            return nova_lista

        except:
            return []

    # --- Processamento das Linhas ---
    for _, row in df.iterrows():
        pedido_nome = ajustar_nome(row['Pedidos'])
        valor = calcular_valor(row)
        tamanhos = formatar_tamanhos(row, pedido_nome)
        nomes = limpar_listas(row['Nomes na Camisa'])
        nums = limpar_listas(row['Números na Camisa'])
        
        # Pagamento
        forma = str(row['Forma de Pagamento']).upper()
        if "PIX" in forma:
            pag_info = "🔑 *Chave PIX:* freneticaufcat@gmail.com\n*(Favor enviar o comprovante para este contato Alfredo -> +55 64 9948-5869)*"
        elif "CARTAO" in forma or "CARTÃO" in forma:
            pag_info = f"💳 *Pagamento no Cartão:* Receberemos por link de pagamento.\n(Favor enviar mensagem para esse número *+55 64 9948-5869 -> Alfredo*)\n Envie esta mensagem: Meu nome é *{row['Cliente']}* e gostaria do meu link de pagamento no valor de *R$ {valor:.2f}*"
        else:
            pag_info = f"💳 *Pagamento:* {row['Forma de Pagamento']}"

        # Personalização
        perso = ""
        if "Camisa" in pedido_nome:
            if nomes or nums:
                n_t, nm_t = (", ".join(nomes) if nomes else "Sem nome"), (", ".join(nums) if nums else "Sem número")
                perso = f"✍️ *Personalização da Camisa:* Confirmar Nome: *{n_t}* e Número: *{nm_t}*?"
            else:
                perso = "⚠️ *Atenção:* Notei que seu pedido inclui camisa, mas não informou nome/número. *Quais deseja colocar?*"

        # Montagem do Template
        msg = f"""*CONFIRMAÇÃO DE PEDIDO - ATLÉTICA FRENÉTICA* 🐾

Olá, *{row['Cliente']}*! Conferimos aqui o seu pedido:

✅ *Itens:* {pedido_nome}
📏 *Tamanhos:* {tamanhos}
🎨 *Cor da Camisa:* Branca ou Azul?
💰 *Valor Total:* R$ {valor:.2f}

{pag_info}

{perso}

Está tudo correto? Caso precise mudar algo, nos avise! 🚀"""
        
        # Limpa o telefone para conter apenas números
        tel = "".join(filter(str.isdigit, str(row['Telefone'])))
        
        lista_telefones.append(tel)
        lista_mensagens.append(msg)

    return lista_telefones, lista_mensagens


def enviar_mensagem(telefone,mensagem):
    pg.PAUSE = 0.5 # Tempo de pausa entre os comandos, pode ser ajustado conforme necessário
    pg.press('win')
    pg.write('WhatsApp')
    pg.sleep(1)
    pg.press('enter')
    pg.sleep(1)

    pg.sleep(1)
    pg.hotkey('ctrl', 'n') # Abre uma nova conversa
    pg.sleep(2.5)
    pg.write(telefone, interval=0.1)
    pg.sleep(2.5)
    pg.press('tab')
    pg.sleep(0.5)
    pg.press('tab')
    pg.sleep(0.5)
    pg.press('tab')
    pg.sleep(0.5)
    pg.press('enter')
    pg.sleep(0.5)
    pc.copy(mensagem) # Copia a mensagem para a área de transferência
    pg.hotkey('ctrl', 'v') # Cola a mensagem no campo de texto
    pc.copy('') # Limpa a área de transferência
    pg.sleep(0.5)
    pg.press('enter') # Envia a mensagem
    pg.sleep(0.5)
    pg.hotkey('ctrl', 'w') # Fecha a aba do WhatsApp
    pg.sleep(0.5)
    pg.hotkey('alt', 'f4') # Fecha WhatsApp


def enviar_lote(telefones, mensagens, df):
    enviados = []
    erros = []

    for i, (t, m) in enumerate(zip(telefones, mensagens)):
        cliente = df.iloc[i]['Cliente']

        try:
            enviar_mensagem(t, m)
            print(f"✅ {cliente}")
            enviados.append(cliente)

        except Exception as e:
            print(f"❌ {cliente} -> {e}")
            erros.append(cliente)

    return enviados, erros


