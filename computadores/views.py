import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

from .models import Computador, Manutencao


def computador_para_dict(pc):
    return {
        "id":          pc.id,
        "hostname":    pc.hostname,
        "modelo":      pc.modelo,
        "setor":       pc.setor,
        "responsavel": pc.responsavel,
        "specs": {
            "ram":         pc.ram,
            "ssd":         pc.ssd,
            "processador": pc.processador,
        },
        "historico": [manutencao_para_dict(m) for m in pc.historico.all()]
    }


def manutencao_para_dict(m):
    return {
        "id":        m.id,
        "tipo":      m.tipo,
        "descricao": m.descricao,
        "tecnico":   m.tecnico,
        "data":      m.data.strftime("%Y-%m-%d %H:%M"),
    }


# ── Listar e Cadastrar ─────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def computadores(request):
    if request.method == "GET":
        pcs = Computador.objects.all()
        return JsonResponse([computador_para_dict(pc) for pc in pcs], safe=False)

    data = json.loads(request.body)
    modelo = data.get("modelo", "").strip()
    if not modelo:
        return JsonResponse({"erro": "O campo 'modelo' é obrigatório."}, status=400)

    pc = Computador.objects.create(
        hostname    = data["hostname"].upper(),
        modelo      = modelo,
        setor       = data["setor"],
        responsavel = data["responsavel"],
        ram         = data["specs"]["ram"],
        ssd         = data["specs"]["ssd"],
        processador = data["specs"]["processador"],
    )
    return JsonResponse(computador_para_dict(pc), status=201)


# ── Buscar, Editar e Excluir por ID ───────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "PATCH", "DELETE"])
def computador_detalhe(request, pk):
    pc = get_object_or_404(Computador, pk=pk)

    if request.method == "GET":
        return JsonResponse(computador_para_dict(pc))

    if request.method == "PATCH":
        data = json.loads(request.body)
        modelo = data.get("modelo", pc.modelo).strip()
        if not modelo:
            return JsonResponse({"erro": "O campo 'modelo' não pode ser vazio."}, status=400)
        pc.hostname    = data.get("hostname", pc.hostname).upper()
        pc.modelo      = modelo
        pc.setor       = data.get("setor", pc.setor)
        pc.responsavel = data.get("responsavel", pc.responsavel)
        specs = data.get("specs", {})
        pc.ram         = specs.get("ram", pc.ram)
        pc.ssd         = specs.get("ssd", pc.ssd)
        pc.processador = specs.get("processador", pc.processador)
        pc.save()
        return JsonResponse(computador_para_dict(pc))

    pc.delete()
    return JsonResponse({"mensagem": f"Computador '{pc.hostname}' excluído."})


# ── Buscar por hostname ────────────────────────────────────────────────────────

@require_http_methods(["GET"])
def computador_por_hostname(request, hostname):
    pc = get_object_or_404(Computador, hostname=hostname.upper())
    return JsonResponse(computador_para_dict(pc))


# ── Histórico de manutenções ───────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["GET", "POST"])
def manutencoes(request, pk):
    pc = get_object_or_404(Computador, pk=pk)

    if request.method == "GET":
        registros = pc.historico.all().order_by("-data")
        return JsonResponse([manutencao_para_dict(m) for m in registros], safe=False)

    data = json.loads(request.body)
    specs = data.get("specs_atualizadas")
    if specs:
        pc.ram         = specs.get("ram", pc.ram)
        pc.ssd         = specs.get("ssd", pc.ssd)
        pc.processador = specs.get("processador", pc.processador)
        pc.save()

    tipos_validos = [t[0] for t in Manutencao.TIPOS]
    tipo = data.get("tipo", "Outro")
    if tipo not in tipos_validos:
        tipo = "Outro"

    m = Manutencao.objects.create(
        computador = pc,
        tipo       = tipo,
        descricao  = data["descricao"],
        tecnico    = data["tecnico"],
    )
    return JsonResponse(manutencao_para_dict(m), status=201)