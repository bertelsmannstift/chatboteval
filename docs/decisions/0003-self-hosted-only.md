# 0003 Self-Hosted Only Deployment

Status: Accepted


## Decision

Cloud-hosted deployment is out of scope. The framework is self-hosted only.


## Context

GDPR and data sensitivity requirements necessitate full control over data residency. Annotation data may contain proprietary or sensitive information that cannot be transmitted to third-party cloud services.


## Rationale

- Self-hosted approach gives users full control over data location and access
- Complies with GDPR and organisational data sensitivity policies
- Avoids vendor lock-in and third-party data processing agreements
- Reduces operational risk associated with cloud service availability and pricing changes


## Consequences

- Users must provision and maintain their own infrastructure
- Deployment complexity is higher compared to managed cloud offerings
- No recurring SaaS costs, but higher upfront setup effort
- Documentation must include comprehensive self-hosting guides
