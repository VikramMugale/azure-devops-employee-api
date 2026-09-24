# Security

This document describes the security controls in the Azure DevOps Employee API project.

## Secrets management

| Secret | Where it lives | How the app gets it |
|--------|----------------|---------------------|
| `DATABASE_URL` | Azure Key Vault | App Service Key Vault reference + Managed Identity |
| Azure credentials for CI/CD | GitHub Secrets (`AZURE_CREDENTIALS`) | GitHub Actions `azure/login` |
| ACR credentials | Managed Identity (AcrPull) | App Service pulls images without admin password |

**Never** commit `.env`, `terraform.tfvars`, or real connection strings.

## Environment variables

Application configuration is injected at runtime:

- `DATABASE_URL` – NeonDB PostgreSQL connection string
- `APP_ENV` – `development` | `production`
- `APP_VERSION` – semantic version / git SHA
- `PORT` – listening port (Azure sets this)

## Dependency scanning

CI runs `pip-audit` against `requirements.txt` to surface known CVEs in Python packages.

## Container scanning

CI builds the Docker image. For production hardening, add a step such as:

```yaml
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: employee-api:ci
    severity: CRITICAL,HIGH
    exit-code: "1"
```

## Least privilege

- App Service uses a **user-assigned managed identity**.
- That identity has:
  - `AcrPull` on the Container Registry
  - `Get` / `List` secrets on Key Vault
- No long-lived passwords are stored in the application or image.

## Managed identity flow

```
App Service
    │  "I am identity X"
    ▼
Azure AD
    │
    ▼
Key Vault  ──►  database-url secret
```

## HTTPS

App Service is configured with `https_only = true`.

## Input validation

- Pydantic models enforce types, length, and email format.
- Duplicate emails return HTTP 409.
- Invalid payloads return HTTP 422.

## Database security

- NeonDB requires SSL (`sslmode=require`).
- Connection string is never baked into the image.
- SQLAlchemy uses parameterized queries (no raw SQL in app code).

## Credential handling checklist

- [ ] `.env` is in `.gitignore`
- [ ] `terraform.tfvars` is in `.gitignore`
- [ ] GitHub secret `AZURE_CREDENTIALS` is a service principal with Contributor on the resource group only
- [ ] Key Vault access policies limited to deploy identity + app identity
- [ ] ACR admin user disabled once Managed Identity is confirmed working
