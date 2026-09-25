# Project charter — Meridian Freight Group delivery analytics platform

> **Note:** Meridian Freight Group is a fictional company created for this
> portfolio project. The business scenario is constructed; the engineering,
> data problems and platform are real.

## 1. Business context

Meridian Freight Group is an Australian logistics aggregator. Merchants book
shipments through Meridian, which allocates each consignment to one of several
carrier partners (parcel, express and general freight) and manages the delivery
through to the customer.

Meridian does not own the delivery fleet for most volume. It owns the
relationship, the booking, and the accountability when something goes wrong.

## 2. Business problem

Meridian's operational data is fragmented across three systems that were never
designed to talk to each other:

- The order management system knows what was booked.
- Carrier partners report scan events in their own formats, on their own schedules.
- Vehicle telematics report where drivers actually are.

No single system can answer the questions leadership asks. Carrier invoices are
reconciled manually. On-time performance is reported by the carriers themselves,
with no independent verification. Delivery failure patterns are discovered
anecdotally, weeks after the fact.

The business needs one reconciled view of the shipment journey.

## 3. Personas

| Persona | Role | Primary need |
|---|---|---|
| Carrier manager | Manages partner relationships and SLAs | Independent OTD performance by carrier |
| Operations lead | Runs daily delivery operations | Exceptions, stuck shipments, failure hotspots |
| Commercial analyst | Owns margin and carrier contracts | Cost per shipment, RTO cost, contract leverage |
| Data engineer (me) | Builds and runs the platform | Pipeline health, freshness, data quality |

## 4. Key questions the platform must answer

1. What is on-time delivery rate by carrier, independently verified?
2. Which merchants have the highest return-to-origin rate?
3. Which postcodes have the highest delivery failure rate?
4. Where do shipments stall in the journey, and for how long?
5. Do carrier scan events agree with telematics evidence?

## 5. KPIs

- On-time delivery rate (OTD %)
- Return-to-origin rate (RTO %)
- First-attempt delivery success rate
- Median and 90th-percentile transit time by lane
- Scan-to-telematics agreement rate
- Data freshness and pipeline success rate

## 6. Data sources (in scope)

| Source | System | Pattern | Format | Frequency |
|---|---|---|---|---|
| Orders | OMS (Azure SQL) | Change data capture | Relational | Continuous |
| Carrier scans | Partner feeds | Batch file ingestion | CSV / JSON | Several times daily |
| Telematics | Vehicle devices | Streaming | JSON events | ~30 seconds |
| Reference | ABS / Australia Post | API and batch | CSV / JSON | Infrequent |

Five further enterprise source systems are documented but explicitly out of
scope — see `01-enterprise-architecture.md`.

## 7. Deliberate data quality problems

The generated sources will contain, by design:

- Duplicate carrier scan events
- Out-of-order and late-arriving events
- Unmapped or carrier-specific status codes
- Missing and malformed postcodes
- Inconsistent timestamp formats and timezone handling
- Telemetry gaps (device offline)
- Orders with no corresponding scan events, and vice versa

## 8. Technical requirements

- Incremental processing; full reloads only where justified
- Idempotent pipelines — safe to re-run without duplication
- Schema evolution handled without pipeline failure
- Bad records quarantined, not silently dropped
- No credentials in source control
- Cost ceiling: under AUD $40/month

## 9. Out of scope

- Real-time intervention or alerting to drivers
- Machine learning / delay prediction
- Finance, CRM, fraud, marketing and WMS source systems
- Data migration from a legacy platform (planned as a separate project)

## 10. Architecture summary

Sources → Event Hubs (streaming) and batch ingestion → Azure Databricks
(bronze / silver / gold Delta) → Microsoft Fabric shortcut → Power BI.

Cross-cutting: Unity Catalog governance, GitHub Actions CI/CD, Azure Monitor
observability.

## 11. Portfolio deliverables

Beyond the platform itself, this project produces public-facing evidence:

- Power BI dashboard, published to web
- Vercel-hosted page embedding the live dashboard, publicly accessible
- Short screen-recorded walkthrough of the dashboard in use
- Architecture diagram and data model diagram
- Recruiter-facing README
- LinkedIn write-up

The hosted dashboard means reviewers can interact with the output rather than
only viewing screenshots.