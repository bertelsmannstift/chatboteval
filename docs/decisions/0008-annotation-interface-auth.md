# 0008: Annotation Authentication Interface

Status: Accepted


## Decision

- Use Argilla's built-in username/password authentication for v1.0. 
- OAuth2 and LDAP deferred to v1.x+.
- Account creation and workspace membership is Owner-role managed. 

## Rationale

**Small user scale**: manual credential distribution is acceptable at fewer than 10 users; no external identity provider or email server required.

**Argilla built-in Role-Based Access Control (RBAC)**: Owner / Admin / Annotator roles are included in free tier, stored in Argilla's PostgreSQL backend, w/ password reset via admin interface. 

**Pluggable architecture**: Argilla supports multiple authentication backends (built-in, OAuth2, LDAP); migration later is possible without data loss.

>## Alternatives considered
>
>**OAuth2** (HuggingFace, Google, GitHub): Argilla v2 supports OAuth2 natively via `oauth.yaml` config and `ARGILLA_AUTH_OAUTH_CFG` environment variable. Viable for v1.x+ if annotators have Google (or less likely HF) accounts — no separate IdP setup required. Deferred as adds config overhead unjustified at fewer than 10 users, and workspace assignment still requires owner action regardless.
>
>**LDAP / enterprise SSO**: adds infrastructure dependency (external IdP or directory server); unjustified at pilot scale. Inferior to OAuth2.
>
>**Self-managed identity layer**: signif implementation overhead with no benefit over Argilla's built-in RBAC at pilot scale.

## Role Mapping

| Role | Who | Permissions |
|------|-----|-------------|
| **Owner** | Project admin (1 person) | Full system access: create users, assign workspace membership, manage all datasets. Holds API key for import/export scripts. |
| **Annotator** | Domain experts + junior annotators | Labelling only within assigned workspaces; no API key, no management access. |

> **Admin role (unused in v1.0):** Argilla also provides an Admin role - can manage datasets within assigned workspaces, but cannot create users or assign workspace membership. Useful at scale when a dedicated dataset manager layer is needed between the system owner and annotators. For v1.0 (<10 users, one tech lead), this is over-engineering — all dataset setup is done once at deployment via SDK scripts. Admin role support is deferred; it may be exposed in a later release alongside OAuth2 to reduce credential management overhead.

See [User Management design doc](../design/user-management.md) for account creation, API key handling, and password reset workflow.


## Consequences

- No external identity provider or email server required for v1.0
- Functions that perform workspace or dataset management require an Argilla API key with Owner privileges; the package accepts a pre-configured Argilla client, or credentials may be passed explicitly or loaded from environment variables (recommended for CI/production)
- Annotators access via web UI only - no API key needed
- password resets are owner-operated (manual)
- Migration to external RBACs such as OAuth2 possible without data loss if required later
