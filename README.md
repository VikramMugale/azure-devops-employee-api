# Azure DevOps Employee API

A complete, interview-ready DevOps project: **FastAPI + NeonDB + Docker + GitHub Actions + Azure + Terraform**.

End-to-end flow from `git push` → CI quality gates → Docker image → Azure Container Registry → Azure App Service → NeonDB PostgreSQL, with Infrastructure as Code and secret management via Key Vault + Managed Identity.

---

## Architecture

```
                         DEVELOPER
                             │
                             │ git push
                             ▼
                    ┌─────────────────┐
                    │     GitHub      │
                    │   Repository    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ GitHub Actions  │
                    └────────┬────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
          ┌─────────────┐        ┌─────────────┐
          │     CI      │        │     CD      │
          └──────┬──────┘        └──────┬──────┘
                 │                       │
        Lint · Tests · Security       Docker Build
                                         │
                                         ▼
                                  Azure Container
                                      Registry
                                         │
                                         ▼
                                  Azure App Service
                                         │
                                         ▼
                                  FastAPI Container
                                         │
                                         │ DATABASE_URL
                                         ▼
                                      NeonDB
                                   PostgreSQL
```

Terraform provisions:

```
Terraform
   ├── Resource Group
   ├── Container Registry (ACR)
   ├── App Service Plan + Linux Web App
   ├── Key Vault
   ├── User-assigned Managed Identity
   └── Application Insights
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Pydantic, SQLAlchemy |
| Database | NeonDB (PostgreSQL) |
| Migrations | Alembic |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Cloud | Azure App Service, ACR, Key Vault |
| IaC | Terraform (azurerm) |
| Quality | Ruff, pytest, pytest-cov, pip-audit |

---

## Project Structure

```
azure-devops-employee-api/
├── .github/workflows/
│   ├── ci.yml              # Lint, test, coverage, pip-audit, Docker build
│   └── cd.yml              # Build → ACR → App Service
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── logging_config.py
│   ├── models/employee.py
│   ├── schemas/employee.py
│   ├── routes/{health,employees}.py
│   └── services/employee_service.py
├── alembic/                # Database migrations
├── tests/                  # pytest suite
├── scripts/{run,test}.sh
├── infrastructure/terraform/
├── security/README.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness/readiness probe |
| GET | `/employees/` | List all employees |
| GET | `/employees/{id}` | Get employee by ID |
| POST | `/employees/` | Create employee |
| PUT | `/employees/{id}` | Update employee |
| DELETE | `/employees/{id}` | Delete employee |

Interactive docs: `http://localhost:8000/docs`

---

## Local Development

### 1. Clone and set up

```bash
git clone https://github.com/VikramMugale/azure-devops-employee-api.git
cd azure-devops-employee-api

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env → set your NeonDB DATABASE_URL
```

### 2. NeonDB

1. Create a free project at [neon.tech](https://neon.tech)
2. Copy the connection string
3. Put it in `.env`:

```
DATABASE_URL=postgresql://user:pass@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
```

### 3. Run the API

```bash
./scripts/run.sh
# or
uvicorn app.main:app --reload
```

### 4. Migrations (optional – tables are also created on startup)

```bash
alembic upgrade head
```

---

## Testing

```bash
./scripts/test.sh
# or
ruff check app tests
pytest --cov=app --cov-report=term-missing
```

Tests use an in-memory SQLite database so CI does not need Neon credentials.

Covered cases: CRUD success paths, 404, 409 (duplicate email), 422 (validation).

---

## Docker

### Build and run with Compose

```bash
# Ensure .env has DATABASE_URL
docker compose up --build
```

API: `http://localhost:8000/health`

### Build only

```bash
docker build -t employee-api:local .
docker run --env-file .env -p 8000:8000 employee-api:local
```

---

## GitHub Actions

### CI (`.github/workflows/ci.yml`)

On every push/PR to `main`:

1. Checkout + setup Python 3.12  
2. Install dependencies  
3. **Ruff** lint  
4. **Pytest** + coverage  
5. **pip-audit** dependency scan  
6. **Docker build** (no push)

### CD (`.github/workflows/cd.yml`)

On push to `main` (or manual dispatch):

1. Azure login (`AZURE_CREDENTIALS` secret)  
2. ACR login  
3. Build & push `employee-api:<git-sha>` and `:latest`  
4. Deploy to App Service  

#### Required GitHub configuration

| Name | Type | Source |
|------|------|--------|
| `AZURE_CREDENTIALS` | Secret | `az ad sp create-for-rbac --sdk-auth` JSON |
| `ACR_NAME` | Variable | ACR name (no `.azurecr.io`) |
| `APP_NAME` | Variable | App Service name |

```bash
# Example service principal (Contributor on the resource group)
az ad sp create-for-rbac \
  --name "github-actions-employee-api" \
  --role contributor \
  --scopes /subscriptions/<SUB_ID>/resourceGroups/rg-employee-api \
  --sdk-auth
```

Paste the JSON output into the GitHub secret `AZURE_CREDENTIALS`.

---

## Terraform

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars – fill CHANGE_ME values (globally unique names)

az login
terraform init
terraform plan
terraform apply
```

Resources created:

- Resource Group  
- User-assigned Managed Identity  
- Azure Container Registry  
- App Service Plan + Linux Web App (container)  
- Key Vault + `database-url` secret placeholder  
- Application Insights  

After apply, set the real Neon connection string:

```bash
az keyvault secret set \
  --vault-name <key_vault_name> \
  --name database-url \
  --value "postgresql://..."
```

Then wire the App Service setting (Key Vault reference):

```bash
az webapp config appsettings set \
  --name <app_name> \
  --resource-group <rg> \
  --settings \
    DATABASE_URL="@Microsoft.KeyVault(SecretUri=https://<kv>.vault.azure.net/secrets/database-url/)"
```

---

## Secrets & Identity

See [security/README.md](security/README.md) for:

- Key Vault + Managed Identity flow  
- Least privilege roles  
- Dependency and container scanning  
- Credential handling checklist  

---

## Monitoring

- App Service health check path: `/health`  
- Application Insights is provisioned by Terraform  
- Application logs stream via:

```bash
az webapp log tail --name <app_name> --resource-group <rg>
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `DATABASE_URL` not set | Copy `.env.example` → `.env` and set Neon URL |
| Tests fail on import | Ensure `DATABASE_URL` is set (tests default to SQLite) |
| Docker build fails | Check `.dockerignore`; run `docker build` with `--no-cache` |
| CD cannot login to Azure | Verify `AZURE_CREDENTIALS` secret and SP permissions |
| App Service cannot pull image | Confirm Managed Identity has `AcrPull` on ACR |
| 422 on POST | Check Pydantic validation (name ≥ 2 chars, valid email) |
| 409 on POST | Email already exists (unique constraint) |

---

## Learning outcomes

After completing this project you can explain:

> I built a FastAPI employee management API backed by PostgreSQL on NeonDB.  
> I containerized it with Docker, added Alembic migrations, automated testing,  
> linting, and dependency scanning in GitHub Actions. CI validates the app and  
> builds the image; CD pushes to Azure Container Registry and deploys to Azure  
> App Service. Infrastructure is provisioned with Terraform; secrets use Azure  
> Key Vault and managed identity.

---

## License

MIT – see [LICENSE](LICENSE).
