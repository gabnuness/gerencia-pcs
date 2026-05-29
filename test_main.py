import unittest
from unittest.mock import patch
import os
import tempfile

import main


def pc(hostname="PC-TESTE", modelo="Desktop", setor="TI",
       responsavel="Gabriel", ram="8GB", ssd="256GB SSD",
       processador="Intel i5", historico=None):
    return {
        "hostname": hostname,
        "modelo": modelo,
        "setor": setor,
        "responsavel": responsavel,
        "specs": {"ram": ram, "ssd": ssd, "processador": processador},
        "historico": historico or []
    }


class BaseTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        main.ARQUIVO = self.tmp.name

    def tearDown(self):
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def msgs(self, mock_print):
        return " ".join(str(c) for c in mock_print.call_args_list)


# ── carregar / salvar ──────────────────────────────────────────────────────────

class TestPersistencia(BaseTest):
    def test_carregar_arquivo_inexistente(self):
        self.assertEqual(main.carregar_dados(), {})

    def test_salvar_e_carregar(self):
        dados = {"PC-01": pc("PC-01")}
        main.salvar_dados(dados)
        self.assertEqual(main.carregar_dados(), dados)

    def test_salvar_preserva_encoding(self):
        dados = {"PC-01": pc("PC-01", responsavel="João Müller", setor="Ação")}
        main.salvar_dados(dados)
        carregado = main.carregar_dados()
        self.assertEqual(carregado["PC-01"]["responsavel"], "João Müller")


# ── cadastrar ─────────────────────────────────────────────────────────────────

class TestCadastrar(BaseTest):
    def test_desktop(self):
        dados = {}
        with patch('builtins.input', side_effect=["PC-01", "desktop", "TI", "Gabriel", "8GB", "256GB SSD", "Intel i5"]), \
             patch('builtins.print'):
            main.cadastrar_computador(dados)
        self.assertIn("PC-01", dados)
        self.assertEqual(dados["PC-01"]["modelo"], "Desktop")
        self.assertEqual(dados["PC-01"]["specs"]["ram"], "8GB")

    def test_notebook(self):
        dados = {}
        with patch('builtins.input', side_effect=["NOTE-01", "notebook", "Dell Inspiron 15", "RH", "Ana", "16GB", "512GB SSD", "Intel i7"]), \
             patch('builtins.print'):
            main.cadastrar_computador(dados)
        self.assertEqual(dados["NOTE-01"]["modelo"], "Dell Inspiron 15")

    def test_notebook_modelo_obrigatorio_retry(self):
        dados = {}
        with patch('builtins.input', side_effect=["NOTE-02", "notebook", "", "Dell Vostro 14", "Financeiro", "Carla", "8GB", "256GB SSD", "Intel i3"]), \
             patch('builtins.print') as mock_print:
            main.cadastrar_computador(dados)
        self.assertEqual(dados["NOTE-02"]["modelo"], "Dell Vostro 14")
        self.assertIn("obrigatório", self.msgs(mock_print))

    def test_hostname_duplicado(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', return_value="PC-01"), \
             patch('builtins.print') as mock_print:
            main.cadastrar_computador(dados)
        self.assertEqual(len(dados), 1)
        self.assertIn("já está cadastrado", self.msgs(mock_print))

    def test_historico_inicializado_vazio(self):
        dados = {}
        with patch('builtins.input', side_effect=["PC-01", "desktop", "TI", "Gabriel", "8GB", "256GB", "Intel i5"]), \
             patch('builtins.print'):
            main.cadastrar_computador(dados)
        self.assertEqual(dados["PC-01"]["historico"], [])


# ── editar ────────────────────────────────────────────────────────────────────

class TestEditar(BaseTest):
    def test_sem_computadores(self):
        with patch('builtins.print') as mock_print:
            main.editar_computador({})
        self.assertIn("Nenhum", self.msgs(mock_print))

    def test_hostname_inexistente(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', return_value="PC-FANTASMA"), \
             patch('builtins.print') as mock_print:
            main.editar_computador(dados)
        self.assertIn("não encontrado", self.msgs(mock_print))

    def test_manter_todos_os_valores(self):
        dados = {"PC-01": pc("PC-01", setor="TI", ram="8GB")}
        with patch('builtins.input', side_effect=["PC-01", "", "", "", "", "", ""]), \
             patch('builtins.print'):
            main.editar_computador(dados)
        self.assertEqual(dados["PC-01"]["setor"], "TI")
        self.assertEqual(dados["PC-01"]["specs"]["ram"], "8GB")

    def test_atualizar_setor(self):
        dados = {"PC-01": pc("PC-01", setor="TI")}
        with patch('builtins.input', side_effect=["PC-01", "", "Financeiro", "", "", "", ""]), \
             patch('builtins.print'):
            main.editar_computador(dados)
        self.assertEqual(dados["PC-01"]["setor"], "Financeiro")

    def test_atualizar_responsavel(self):
        dados = {"PC-01": pc("PC-01", responsavel="Gabriel")}
        with patch('builtins.input', side_effect=["PC-01", "", "", "Ana", "", "", ""]), \
             patch('builtins.print'):
            main.editar_computador(dados)
        self.assertEqual(dados["PC-01"]["responsavel"], "Ana")

    def test_desktop_para_notebook(self):
        dados = {"PC-01": pc("PC-01", modelo="Desktop")}
        with patch('builtins.input', side_effect=["PC-01", "notebook", "Dell Inspiron 15", "", "", "", "", ""]), \
             patch('builtins.print'):
            main.editar_computador(dados)
        self.assertEqual(dados["PC-01"]["modelo"], "Dell Inspiron 15")

    def test_notebook_para_desktop(self):
        dados = {"NOTE-01": pc("NOTE-01", modelo="Dell Inspiron 15")}
        with patch('builtins.input', side_effect=["NOTE-01", "desktop", "", "", "", "", ""]), \
             patch('builtins.print'):
            main.editar_computador(dados)
        self.assertEqual(dados["NOTE-01"]["modelo"], "Desktop")

    def test_notebook_modelo_obrigatorio_retry(self):
        dados = {"NOTE-01": pc("NOTE-01", modelo="Dell Inspiron 15")}
        with patch('builtins.input', side_effect=["NOTE-01", "notebook", "", "Dell XPS 13", "", "", "", "", ""]), \
             patch('builtins.print') as mock_print:
            main.editar_computador(dados)
        self.assertEqual(dados["NOTE-01"]["modelo"], "Dell XPS 13")
        self.assertIn("obrigatório", self.msgs(mock_print))

    def test_atualizar_specs(self):
        dados = {"PC-01": pc("PC-01", ram="8GB", ssd="256GB SSD", processador="Intel i5")}
        with patch('builtins.input', side_effect=["PC-01", "", "", "", "32GB", "1TB SSD", "Intel i9"]), \
             patch('builtins.print'):
            main.editar_computador(dados)
        self.assertEqual(dados["PC-01"]["specs"]["ram"], "32GB")
        self.assertEqual(dados["PC-01"]["specs"]["ssd"], "1TB SSD")
        self.assertEqual(dados["PC-01"]["specs"]["processador"], "Intel i9")


# ── excluir ───────────────────────────────────────────────────────────────────

class TestExcluir(BaseTest):
    def test_sem_computadores(self):
        with patch('builtins.print') as mock_print:
            main.excluir_computador({})
        self.assertIn("Nenhum", self.msgs(mock_print))

    def test_hostname_inexistente(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', return_value="PC-FANTASMA"), \
             patch('builtins.print') as mock_print:
            main.excluir_computador(dados)
        self.assertIn("não encontrado", self.msgs(mock_print))

    def test_excluir_confirmado(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', side_effect=["PC-01", "s"]), patch('builtins.print'):
            main.excluir_computador(dados)
        self.assertNotIn("PC-01", dados)

    def test_excluir_cancelado(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', side_effect=["PC-01", "n"]), patch('builtins.print'):
            main.excluir_computador(dados)
        self.assertIn("PC-01", dados)

    def test_excluir_nao_afeta_outros(self):
        dados = {"PC-01": pc("PC-01"), "PC-02": pc("PC-02")}
        with patch('builtins.input', side_effect=["PC-01", "s"]), patch('builtins.print'):
            main.excluir_computador(dados)
        self.assertNotIn("PC-01", dados)
        self.assertIn("PC-02", dados)


# ── listar ────────────────────────────────────────────────────────────────────

class TestListar(BaseTest):
    def test_sem_computadores(self):
        with patch('builtins.print') as mock_print:
            main.listar_computadores({})
        self.assertIn("Nenhum", self.msgs(mock_print))

    def test_exibe_todos(self):
        dados = {"PC-01": pc("PC-01", setor="TI"), "NOTE-01": pc("NOTE-01", modelo="Dell Inspiron 15", setor="RH")}
        output = []
        with patch('builtins.print', side_effect=lambda *a: output.append(str(a))):
            main.listar_computadores(dados)
        texto = " ".join(output)
        self.assertIn("PC-01", texto)
        self.assertIn("NOTE-01", texto)
        self.assertIn("Dell Inspiron 15", texto)

    def test_exibe_specs(self):
        dados = {"PC-01": pc("PC-01", ram="16GB", ssd="512GB SSD", processador="Intel i7")}
        output = []
        with patch('builtins.print', side_effect=lambda *a: output.append(str(a))):
            main.listar_computadores(dados)
        texto = " ".join(output)
        self.assertIn("16GB", texto)
        self.assertIn("512GB SSD", texto)
        self.assertIn("Intel i7", texto)

    def test_exibe_contagem_manutencoes(self):
        h = [{"data": "2026-05-27 10:00", "tipo": "Upgrade", "descricao": "RAM", "tecnico": "Gabriel"}]
        dados = {"PC-01": pc("PC-01", historico=h)}
        output = []
        with patch('builtins.print', side_effect=lambda *a: output.append(str(a))):
            main.listar_computadores(dados)
        self.assertIn("1", " ".join(output))


# ── manutenção ────────────────────────────────────────────────────────────────

class TestManutencao(BaseTest):
    def test_sem_computadores(self):
        with patch('builtins.print') as mock_print:
            main.registrar_manutencao({})
        self.assertIn("Nenhum", self.msgs(mock_print))

    def test_hostname_inexistente(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', return_value="PC-FANTASMA"), \
             patch('builtins.print') as mock_print:
            main.registrar_manutencao(dados)
        self.assertIn("não encontrado", self.msgs(mock_print))

    def test_todos_os_tipos(self):
        mapa = [("1", "Manutenção"), ("2", "Upgrade"), ("3", "Formatação"),
                ("4", "Troca de peça"), ("5", "Outro")]
        for opcao, esperado in mapa:
            dados = {"PC-01": pc("PC-01")}
            with patch('builtins.input', side_effect=["PC-01", opcao, "Desc", "Técnico", "n"]), \
                 patch('builtins.print'):
                main.registrar_manutencao(dados)
            self.assertEqual(dados["PC-01"]["historico"][0]["tipo"], esperado,
                             f"Falhou para tipo {esperado}")

    def test_opcao_invalida_vira_outro(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', side_effect=["PC-01", "9", "Desc", "Técnico", "n"]), \
             patch('builtins.print'):
            main.registrar_manutencao(dados)
        self.assertEqual(dados["PC-01"]["historico"][0]["tipo"], "Outro")

    def test_atualizar_specs_sim(self):
        dados = {"PC-01": pc("PC-01", ram="8GB", ssd="256GB SSD", processador="Intel i5")}
        with patch('builtins.input', side_effect=["PC-01", "2", "Upgrade de RAM", "Gabriel", "s", "16GB", "", ""]), \
             patch('builtins.print'):
            main.registrar_manutencao(dados)
        self.assertEqual(dados["PC-01"]["specs"]["ram"], "16GB")
        self.assertEqual(dados["PC-01"]["specs"]["ssd"], "256GB SSD")     # mantido
        self.assertEqual(dados["PC-01"]["specs"]["processador"], "Intel i5")  # mantido

    def test_atualizar_specs_nao(self):
        dados = {"PC-01": pc("PC-01", ram="8GB")}
        with patch('builtins.input', side_effect=["PC-01", "2", "Upgrade", "Gabriel", "n"]), \
             patch('builtins.print'):
            main.registrar_manutencao(dados)
        self.assertEqual(dados["PC-01"]["specs"]["ram"], "8GB")

    def test_atualizar_specs_formatacao(self):
        dados = {"PC-01": pc("PC-01", ssd="256GB SSD")}
        with patch('builtins.input', side_effect=["PC-01", "3", "Formatação + novo SSD", "Gabriel", "s", "", "512GB SSD", ""]), \
             patch('builtins.print'):
            main.registrar_manutencao(dados)
        self.assertEqual(dados["PC-01"]["specs"]["ssd"], "512GB SSD")

    def test_atualizar_specs_manutencao(self):
        dados = {"PC-01": pc("PC-01", ram="8GB")}
        with patch('builtins.input', side_effect=["PC-01", "1", "Troca pente RAM queimado", "Gabriel", "s", "4GB", "", ""]), \
             patch('builtins.print'):
            main.registrar_manutencao(dados)
        self.assertEqual(dados["PC-01"]["specs"]["ram"], "4GB")

    def test_multiplos_registros_acumulam(self):
        dados = {"PC-01": pc("PC-01")}
        for i in range(3):
            with patch('builtins.input', side_effect=["PC-01", "1", f"Registro {i}", "Técnico", "n"]), \
                 patch('builtins.print'):
                main.registrar_manutencao(dados)
        self.assertEqual(len(dados["PC-01"]["historico"]), 3)

    def test_data_registrada_automaticamente(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', side_effect=["PC-01", "1", "Desc", "Técnico", "n"]), \
             patch('builtins.print'):
            main.registrar_manutencao(dados)
        self.assertIn("data", dados["PC-01"]["historico"][0])
        self.assertTrue(len(dados["PC-01"]["historico"][0]["data"]) > 0)


# ── histórico ─────────────────────────────────────────────────────────────────

class TestHistorico(BaseTest):
    def test_sem_computadores(self):
        with patch('builtins.print') as mock_print:
            main.visualizar_historico({})
        self.assertIn("Nenhum", self.msgs(mock_print))

    def test_hostname_inexistente(self):
        dados = {"PC-01": pc("PC-01")}
        with patch('builtins.input', return_value="PC-FANTASMA"), \
             patch('builtins.print') as mock_print:
            main.visualizar_historico(dados)
        self.assertIn("não encontrado", self.msgs(mock_print))

    def test_sem_registros(self):
        dados = {"PC-01": pc("PC-01")}
        output = []
        with patch('builtins.input', return_value="PC-01"), \
             patch('builtins.print', side_effect=lambda *a: output.append(str(a))):
            main.visualizar_historico(dados)
        self.assertIn("Sem registros", " ".join(output))

    def test_exibe_registro(self):
        h = [{"data": "2026-05-27 10:00", "tipo": "Upgrade", "descricao": "Troca de RAM", "tecnico": "Gabriel"}]
        dados = {"PC-01": pc("PC-01", historico=h)}
        output = []
        with patch('builtins.input', return_value="PC-01"), \
             patch('builtins.print', side_effect=lambda *a: output.append(str(a))):
            main.visualizar_historico(dados)
        texto = " ".join(output)
        self.assertIn("Troca de RAM", texto)
        self.assertIn("Gabriel", texto)
        self.assertIn("Upgrade", texto)

    def test_historico_todos_enter(self):
        h = [{"data": "2026-05-27 10:00", "tipo": "Manutenção", "descricao": "Limpeza", "tecnico": "Ana"}]
        dados = {"PC-01": pc("PC-01", historico=h), "PC-02": pc("PC-02", historico=h)}
        output = []
        with patch('builtins.input', return_value=""), \
             patch('builtins.print', side_effect=lambda *a: output.append(str(a))):
            main.visualizar_historico(dados)
        texto = " ".join(output)
        self.assertIn("PC-01", texto)
        self.assertIn("PC-02", texto)

    def test_historico_multiplos_registros(self):
        h = [
            {"data": "2026-05-01 09:00", "tipo": "Manutenção", "descricao": "Limpeza", "tecnico": "Ana"},
            {"data": "2026-05-15 14:00", "tipo": "Upgrade", "descricao": "RAM 16GB", "tecnico": "Carlos"},
        ]
        dados = {"PC-01": pc("PC-01", historico=h)}
        output = []
        with patch('builtins.input', return_value="PC-01"), \
             patch('builtins.print', side_effect=lambda *a: output.append(str(a))):
            main.visualizar_historico(dados)
        texto = " ".join(output)
        self.assertIn("Limpeza", texto)
        self.assertIn("RAM 16GB", texto)
        self.assertIn("2", texto)  # total: 2 registros


if __name__ == "__main__":
    unittest.main(verbosity=2)
