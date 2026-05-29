import json
from django.test import TestCase, Client
from .models import Computador


def desktop(hostname="PC-01", setor="TI", responsavel="Gabriel",
            ram=8, ssd=256, processador="Intel i5"):
    return Computador.objects.create(
        hostname=hostname, modelo="Desktop", setor=setor,
        responsavel=responsavel, ram=ram, ssd=ssd, processador=processador
    )


def notebook(hostname="NOTE-01", modelo="Dell Inspiron 15", setor="RH",
             responsavel="Ana", ram=16, ssd=512, processador="Intel i7"):
    return Computador.objects.create(
        hostname=hostname, modelo=modelo, setor=setor,
        responsavel=responsavel, ram=ram, ssd=ssd, processador=processador
    )


class Base(TestCase):
    def setUp(self):
        self.client = Client()

    def post(self, url, data):
        return self.client.post(url, json.dumps(data), content_type="application/json")

    def patch(self, url, data):
        return self.client.patch(url, json.dumps(data), content_type="application/json")

    def json(self, response):
        return json.loads(response.content)


# ── GET /api/computadores/ e POST /api/computadores/ ──────────────────────────

class TestListarCadastrar(Base):
    def test_listar_vazio(self):
        r = self.client.get("/api/computadores/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.json(r), [])

    def test_listar_retorna_todos(self):
        desktop("PC-01")
        notebook("NOTE-01")
        r = self.client.get("/api/computadores/")
        self.assertEqual(len(self.json(r)), 2)

    def test_cadastrar_desktop(self):
        payload = {
            "hostname": "PC-01", "modelo": "Desktop", "setor": "TI",
            "responsavel": "Gabriel",
            "specs": {"ram": 8, "ssd": 256, "processador": "Intel i5"}
        }
        r = self.post("/api/computadores/", payload)
        self.assertEqual(r.status_code, 201)
        data = self.json(r)
        self.assertEqual(data["hostname"], "PC-01")
        self.assertEqual(data["modelo"], "Desktop")
        self.assertEqual(data["specs"]["ram"], 8)

    def test_cadastrar_notebook(self):
        payload = {
            "hostname": "NOTE-01", "modelo": "Dell Inspiron 15", "setor": "RH",
            "responsavel": "Ana",
            "specs": {"ram": 16, "ssd": 512, "processador": "Intel i7-1165G7"}
        }
        r = self.post("/api/computadores/", payload)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.json(r)["modelo"], "Dell Inspiron 15")

    def test_hostname_convertido_maiusculo(self):
        payload = {
            "hostname": "pc-gabriel", "modelo": "Desktop", "setor": "TI",
            "responsavel": "Gabriel",
            "specs": {"ram": 8, "ssd": 256, "processador": "Intel i5"}
        }
        r = self.post("/api/computadores/", payload)
        self.assertEqual(self.json(r)["hostname"], "PC-GABRIEL")

    def test_modelo_vazio_retorna_400(self):
        payload = {
            "hostname": "PC-01", "modelo": "", "setor": "TI",
            "responsavel": "Gabriel",
            "specs": {"ram": 8, "ssd": 256, "processador": "Intel i5"}
        }
        r = self.post("/api/computadores/", payload)
        self.assertEqual(r.status_code, 400)

    def test_cadastro_retorna_id(self):
        payload = {
            "hostname": "PC-01", "modelo": "Desktop", "setor": "TI",
            "responsavel": "Gabriel",
            "specs": {"ram": 8, "ssd": 256, "processador": "Intel i5"}
        }
        r = self.post("/api/computadores/", payload)
        data = self.json(r)
        self.assertIn("id", data)
        self.assertIsInstance(data["id"], int)

    def test_historico_inicializado_vazio(self):
        pc = desktop()
        r = self.client.get(f"/api/computadores/{pc.id}/manutencoes/")
        self.assertEqual(self.json(r), [])


# ── GET, PATCH, DELETE /api/computadores/<pk>/ ────────────────────────────────

class TestDetalhe(Base):
    def test_buscar_por_id(self):
        pc = desktop("PC-01", setor="TI")
        r = self.client.get(f"/api/computadores/{pc.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.json(r)["hostname"], "PC-01")

    def test_buscar_id_inexistente_retorna_404(self):
        r = self.client.get("/api/computadores/999/")
        self.assertEqual(r.status_code, 404)

    def test_patch_atualiza_setor(self):
        pc = desktop("PC-01", setor="TI")
        r = self.patch(f"/api/computadores/{pc.id}/", {"setor": "Financeiro"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.json(r)["setor"], "Financeiro")

    def test_patch_atualiza_responsavel(self):
        pc = desktop("PC-01", responsavel="Gabriel")
        r = self.patch(f"/api/computadores/{pc.id}/", {"responsavel": "Ana"})
        self.assertEqual(self.json(r)["responsavel"], "Ana")

    def test_patch_atualiza_specs(self):
        pc = desktop("PC-01", ram=8, ssd=256)
        r = self.patch(f"/api/computadores/{pc.id}/", {"specs": {"ram": 16, "ssd": 512}})
        data = self.json(r)
        self.assertEqual(data["specs"]["ram"], 16)
        self.assertEqual(data["specs"]["ssd"], 512)

    def test_patch_mantem_campos_nao_enviados(self):
        pc = desktop("PC-01", setor="TI", responsavel="Gabriel", ram=8)
        self.patch(f"/api/computadores/{pc.id}/", {"setor": "Financeiro"})
        pc.refresh_from_db()
        self.assertEqual(pc.responsavel, "Gabriel")
        self.assertEqual(pc.ram, 8)

    def test_patch_modelo_vazio_retorna_400(self):
        pc = desktop("PC-01")
        r = self.patch(f"/api/computadores/{pc.id}/", {"modelo": ""})
        self.assertEqual(r.status_code, 400)

    def test_patch_desktop_para_notebook(self):
        pc = desktop("PC-01")
        r = self.patch(f"/api/computadores/{pc.id}/", {"modelo": "Dell XPS 15"})
        self.assertEqual(self.json(r)["modelo"], "Dell XPS 15")

    def test_patch_notebook_para_desktop(self):
        pc = notebook("NOTE-01")
        r = self.patch(f"/api/computadores/{pc.id}/", {"modelo": "Desktop"})
        self.assertEqual(self.json(r)["modelo"], "Desktop")

    def test_delete_remove_computador(self):
        pc = desktop("PC-01")
        r = self.client.delete(f"/api/computadores/{pc.id}/")
        self.assertEqual(r.status_code, 200)
        self.assertFalse(Computador.objects.filter(pk=pc.id).exists())

    def test_delete_nao_afeta_outros(self):
        pc1 = desktop("PC-01")
        pc2 = desktop("PC-02")
        self.client.delete(f"/api/computadores/{pc1.id}/")
        self.assertTrue(Computador.objects.filter(pk=pc2.id).exists())

    def test_delete_id_inexistente_retorna_404(self):
        r = self.client.delete("/api/computadores/999/")
        self.assertEqual(r.status_code, 404)


# ── GET /api/computadores/hostname/<hostname>/ ────────────────────────────────

class TestBuscaPorHostname(Base):
    def test_buscar_hostname_existente(self):
        desktop("PC-GABRIEL")
        r = self.client.get("/api/computadores/hostname/PC-GABRIEL/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.json(r)["hostname"], "PC-GABRIEL")

    def test_buscar_hostname_case_insensitive(self):
        desktop("PC-GABRIEL")
        r = self.client.get("/api/computadores/hostname/pc-gabriel/")
        self.assertEqual(r.status_code, 200)

    def test_buscar_hostname_inexistente_retorna_404(self):
        r = self.client.get("/api/computadores/hostname/PC-FANTASMA/")
        self.assertEqual(r.status_code, 404)


# ── GET, POST /api/computadores/<pk>/manutencoes/ ─────────────────────────────

class TestManutencoes(Base):
    def test_historico_vazio(self):
        pc = desktop()
        r = self.client.get(f"/api/computadores/{pc.id}/manutencoes/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(self.json(r), [])

    def test_todos_os_tipos(self):
        tipos = ["Manutenção", "Upgrade", "Formatação", "Troca de peça", "Outro"]
        for tipo in tipos:
            pc = desktop(hostname=f"PC-{tipo[:3].upper()}")
            payload = {"tipo": tipo, "descricao": "Teste", "tecnico": "Gabriel"}
            r = self.post(f"/api/computadores/{pc.id}/manutencoes/", payload)
            self.assertEqual(r.status_code, 201)
            self.assertEqual(self.json(r)["tipo"], tipo, f"Falhou para tipo: {tipo}")

    def test_tipo_invalido_vira_outro(self):
        pc = desktop()
        payload = {"tipo": "Inventado", "descricao": "Teste", "tecnico": "Gabriel"}
        r = self.post(f"/api/computadores/{pc.id}/manutencoes/", payload)
        self.assertEqual(self.json(r)["tipo"], "Outro")

    def test_registrar_sem_atualizar_specs(self):
        pc = desktop(ram=8)
        payload = {"tipo": "Manutenção", "descricao": "Limpeza", "tecnico": "Gabriel"}
        self.post(f"/api/computadores/{pc.id}/manutencoes/", payload)
        pc.refresh_from_db()
        self.assertEqual(pc.ram, 8)

    def test_registrar_atualizando_specs(self):
        pc = desktop(ram=8, ssd=256)
        payload = {
            "tipo": "Upgrade", "descricao": "Upgrade de RAM", "tecnico": "Gabriel",
            "specs_atualizadas": {"ram": 16}
        }
        self.post(f"/api/computadores/{pc.id}/manutencoes/", payload)
        pc.refresh_from_db()
        self.assertEqual(pc.ram, 16)
        self.assertEqual(pc.ssd, 256)

    def test_multiplos_registros_acumulam(self):
        pc = desktop()
        for i in range(3):
            payload = {"tipo": "Manutenção", "descricao": f"Registro {i}", "tecnico": "Gabriel"}
            self.post(f"/api/computadores/{pc.id}/manutencoes/", payload)
        r = self.client.get(f"/api/computadores/{pc.id}/manutencoes/")
        self.assertEqual(len(self.json(r)), 3)

    def test_historico_ordenado_mais_recente_primeiro(self):
        pc = desktop()
        for desc in ["Primeiro", "Segundo", "Terceiro"]:
            self.post(f"/api/computadores/{pc.id}/manutencoes/",
                      {"tipo": "Manutenção", "descricao": desc, "tecnico": "Gabriel"})
        r = self.client.get(f"/api/computadores/{pc.id}/manutencoes/")
        registros = self.json(r)
        self.assertEqual(registros[0]["descricao"], "Terceiro")

    def test_historico_contem_data(self):
        pc = desktop()
        payload = {"tipo": "Manutenção", "descricao": "Teste", "tecnico": "Gabriel"}
        r = self.post(f"/api/computadores/{pc.id}/manutencoes/", payload)
        self.assertIn("data", self.json(r))

    def test_manutencao_pc_inexistente_retorna_404(self):
        payload = {"tipo": "Manutenção", "descricao": "Teste", "tecnico": "Gabriel"}
        r = self.post("/api/computadores/999/manutencoes/", payload)
        self.assertEqual(r.status_code, 404)

    def test_manutencao_notebook(self):
        pc = notebook("NOTE-01", modelo="Dell Inspiron 15", ram=8)
        payload = {
            "tipo": "Upgrade", "descricao": "Upgrade de RAM", "tecnico": "Gabriel",
            "specs_atualizadas": {"ram": 16}
        }
        self.post(f"/api/computadores/{pc.id}/manutencoes/", payload)
        pc.refresh_from_db()
        self.assertEqual(pc.ram, 16)
        self.assertEqual(pc.modelo, "Dell Inspiron 15")
