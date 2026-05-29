# Gerência de PCs

API REST para gerenciamento de computadores e notebooks corporativos, desenvolvida em Django com SQLite.

## Funcionalidades

- Cadastro de desktops e notebooks com especificações técnicas
- Edição parcial de dados via PATCH
- Exclusão de registros
- Busca por ID ou hostname
- Registro de manutenções, upgrades e formatações com atualização automática de specs

## Tecnologias

- Python 3.14
- Django 6.0
- SQLite

## Como rodar localmente

```bash
# Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows

# Instalar dependências
pip install django

# Aplicar migrações
python manage.py migrate

# Iniciar o servidor
python manage.py runserver
```

## Endpoints

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/computadores/` | Lista todos os computadores |
| POST | `/api/computadores/` | Cadastra novo computador |
| GET | `/api/computadores/<id>/` | Busca por ID |
| PATCH | `/api/computadores/<id>/` | Edita campos específicos |
| DELETE | `/api/computadores/<id>/` | Exclui computador |
| GET | `/api/computadores/hostname/<hostname>/` | Busca por hostname |
| GET | `/api/computadores/<id>/manutencoes/` | Lista histórico de manutenções |
| POST | `/api/computadores/<id>/manutencoes/` | Registra manutenção |

## Exemplo de cadastro

```json
POST /api/computadores/

{
    "hostname": "PC-01",
    "modelo": "Desktop",
    "setor": "TI",
    "responsavel": "Gabriel",
    "specs": {
        "ram": 16,
        "ssd": 512,
        "processador": "Intel i5-12400"
    }
}
```

## Exemplo de manutenção com atualização de specs

```json
POST /api/computadores/1/manutencoes/

{
    "tipo": "Upgrade",
    "descricao": "Adicionado pente de 8GB RAM",
    "tecnico": "Gabriel",
    "specs_atualizadas": {
        "ram": 16
    }
}
```
