import os, time, json
from datetime import datetime

ARQUIVO = "computadores.json"

# Aqui ele valida se o arquivo existe, se não, cria
def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_dados(dados):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def cadastrar_computador(dados):
    print("\n--- Cadastrar Computador ---")
    hostname = input("Hostname: ").strip().upper()

    if hostname in dados:
        print(f"Computador '{hostname}' já está cadastrado!")
        return

    tipo = input("Tipo (notebook/desktop): ").strip().lower()
    if tipo == "notebook":
        while True:
            modelo = input("Modelo do notebook (ex: Dell Inspiron 15): ").strip()
            if modelo:
                break
            print("O modelo é obrigatório para notebooks. Tente novamente.")
    else:
        modelo = "Desktop"

    setor      = input("Setor: ").strip()
    responsavel = input("Responsável: ").strip()
    ram        = input("RAM (ex: 16GB): ").strip()
    ssd        = input("SSD/HD (ex: 512GB SSD): ").strip()
    processador = input("Processador (ex: Intel i5-12400): ").strip()

    dados[hostname] = {
        "hostname": hostname,
        "modelo": modelo,
        "setor": setor,
        "responsavel": responsavel,
        "specs": {
            "ram": ram,
            "ssd": ssd,
            "processador": processador
        },
        "historico": []
    }

    salvar_dados(dados)
    print(f"\nComputador '{hostname}' cadastrado com sucesso!")


def editar_computador(dados):
    if not dados:
        print("\nNenhum computador cadastrado.")
        return

    print("\n--- Editar Computador ---")
    hostname = input("Hostname do computador a editar: ").strip().upper()

    if hostname not in dados:
        print(f"Computador '{hostname}' não encontrado!")
        return

    pc = dados[hostname]
    print(f"\nEditando: {hostname}  (deixe em branco para manter o valor atual)")

    tipo = input(f"Tipo [atual: {'notebook' if pc['modelo'] != 'Desktop' else 'desktop'}]: ").strip().lower()
    if tipo == "notebook":
        while True:
            modelo = input(f"Modelo [atual: {pc['modelo']}]: ").strip()
            if modelo:
                break
            print("O modelo é obrigatório para notebooks. Tente novamente.")
    elif tipo == "desktop":
        modelo = "Desktop"
    else:
        modelo = pc["modelo"]

    setor       = input(f"Setor [atual: {pc['setor']}]: ").strip()             or pc["setor"]
    responsavel = input(f"Responsável [atual: {pc['responsavel']}]: ").strip() or pc["responsavel"]
    ram         = input(f"RAM [atual: {pc['specs']['ram']}]: ").strip()        or pc["specs"]["ram"]
    ssd         = input(f"SSD/HD [atual: {pc['specs']['ssd']}]: ").strip()     or pc["specs"]["ssd"]
    processador = input(f"Processador [atual: {pc['specs']['processador']}]: ").strip() or pc["specs"]["processador"]

    dados[hostname].update({
        "modelo": modelo,
        "setor": setor,
        "responsavel": responsavel,
        "specs": {"ram": ram, "ssd": ssd, "processador": processador}
    })

    salvar_dados(dados)
    print(f"\nComputador '{hostname}' atualizado com sucesso!")


def excluir_computador(dados):
    if not dados:
        print("\nNenhum computador cadastrado.")
        return

    print("\n--- Excluir Computador ---")
    hostname = input("Hostname do computador a excluir: ").strip().upper()

    if hostname not in dados:
        print(f"Computador '{hostname}' não encontrado!")
        return

    confirmacao = input(f"Tem certeza que deseja excluir '{hostname}'? (s/n): ").strip().lower()
    if confirmacao == "s":
        del dados[hostname]
        salvar_dados(dados)
        print(f"Computador '{hostname}' excluído com sucesso!")
    else:
        print("Operação cancelada.")


def listar_computadores(dados):
    if not dados:
        print("\nNenhum computador cadastrado.")
        return

    print(f"\n{'='*60}")
    print(f"{'LISTA DE COMPUTADORES':^60}")
    print(f"{'='*60}")

    for pc in dados.values():
        print(f"\nHostname:     {pc['hostname']}")
        print(f"Modelo:       {pc['modelo']}")
        print(f"Setor:        {pc['setor']}")
        print(f"Responsável:  {pc['responsavel']}")
        print(f"Processador:  {pc['specs']['processador']}")
        print(f"RAM:          {pc['specs']['ram']}")
        print(f"SSD/HD:       {pc['specs']['ssd']}")
        print(f"Manutenções:  {len(pc['historico'])} registro(s)")
        print(f"{'-'*60}")


def registrar_manutencao(dados):
    if not dados:
        print("\nNenhum computador cadastrado.")
        return

    print("\n--- Registrar Manutenção/Upgrade ---")
    hostname = input("Hostname do computador: ").strip().upper()

    if hostname not in dados:
        print(f"Computador '{hostname}' não encontrado!")
        return

    print("\nTipo do registro:")
    print("1 - Manutenção")
    print("2 - Upgrade")
    print("3 - Formatação")
    print("4 - Troca de peça")
    print("5 - Outro")

    tipos = {"1": "Manutenção", "2": "Upgrade", "3": "Formatação", "4": "Troca de peça", "5": "Outro"}
    tipo_opcao = input("Tipo: ").strip()
    tipo = tipos.get(tipo_opcao, "Outro")

    descricao = input("Descrição: ").strip()
    tecnico   = input("Técnico responsável: ").strip()

    dados[hostname]["historico"].append({
        "data": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "tipo": tipo,
        "descricao": descricao,
        "tecnico": tecnico
    })

    atualizar = input("\nDeseja atualizar as especificações técnicas do computador? (s/n): ").strip().lower()
    if atualizar == "s":
        specs = dados[hostname]["specs"]
        print("(Deixe em branco para manter o valor atual)")
        ram         = input(f"RAM [atual: {specs['ram']}]: ").strip()         or specs["ram"]
        ssd         = input(f"SSD/HD [atual: {specs['ssd']}]: ").strip()      or specs["ssd"]
        processador = input(f"Processador [atual: {specs['processador']}]: ").strip() or specs["processador"]
        dados[hostname]["specs"] = {"ram": ram, "ssd": ssd, "processador": processador}
        print("Especificações atualizadas.")

    salvar_dados(dados)
    print(f"\nRegistro adicionado ao histórico de '{hostname}' com sucesso!")


def visualizar_historico(dados):
    if not dados:
        print("\nNenhum computador cadastrado.")
        return

    print("\n--- Visualizar Histórico ---")
    hostname = input("Hostname do computador (ou ENTER para ver todos): ").strip().upper()

    if hostname and hostname not in dados:
        print(f"Computador '{hostname}' não encontrado!")
        return

    maquinas = {hostname: dados[hostname]} if hostname else dados

    for nome, pc in maquinas.items():
        print(f"\n{'='*60}")
        print(f"Histórico: {nome}  |  {pc['modelo']}  |  {pc['setor']}")
        print(f"{'='*60}")

        if not pc["historico"]:
            print("Sem registros de manutenção.")
            continue

        for i, reg in enumerate(pc["historico"], 1):
            print(f"\n  [{i}] {reg['data']}  —  {reg['tipo']}")
            print(f"       Descrição : {reg['descricao']}")
            print(f"       Técnico   : {reg['tecnico']}")

        print(f"\n  Total: {len(pc['historico'])} registro(s)")


def menu():
    print(f"\n{'='*40}")
    print("As seguintes opções estão disponíveis:")
    print("  1 - Cadastrar computador")
    print("  2 - Editar computador")
    print("  3 - Excluir computador")
    print("  4 - Listar computadores")
    print("  5 - Registrar Manutenção/Upgrade")
    print("  6 - Visualizar Histórico")
    print("  7 - Sair")
    print(f"{'='*40}")


if __name__ == "__main__":
    # ── Inicialização ──────────────────────────────────────────
    nome = input("Digite seu nome: ")
    os.system("cls")
    time.sleep(1)
    print(f"Olá {nome}, seja bem-vindo ao software de gestão de computadores!\n")

    dados = carregar_dados()

    # ── Loop principal ─────────────────────────────────────────
    while True:
        menu()
        opcao = input("Digite a opção desejada: ").strip()

        if opcao == "1":
            cadastrar_computador(dados)
        elif opcao == "2":
            editar_computador(dados)
        elif opcao == "3":
            excluir_computador(dados)
        elif opcao == "4":
            listar_computadores(dados)
        elif opcao == "5":
            registrar_manutencao(dados)
        elif opcao == "6":
            visualizar_historico(dados)
        elif opcao == "7":
            print("\nAté logo!")
            break
        else:
            print("Opção inválida! Digite um número de 1 a 7.")
