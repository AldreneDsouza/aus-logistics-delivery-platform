# Environment setup

## Azure resources — dev environment

| Resource | Name |
|---|---|
| Resource group | rg-meridian-freight-dev |
| Storage account | stmeridianfreightdev |
| Containers | bronze, silver, gold, quarantine, archive |
| Key Vault | kv-meridian-freight-dev |
| Databricks workspace | dbw-meridian-freight-dev |

## Cost controls
- Budget alert set at USD $50, email at 80%
- Databricks serverless compute — pay per execution only
- LRS replication on storage — cheapest tier