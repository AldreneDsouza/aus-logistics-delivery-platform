# Enterprise data architecture — Meridian Freight Group

> **Note:** Meridian Freight Group is a fictional company. This document
> describes the source-system landscape an aggregator of this type would
> operate, and records which systems this project implements and why.

## 1. Purpose

A logistics aggregator runs many operational systems, each owned by a
different business group and each holding part of the truth about a shipment.
No single system can answer the questions leadership asks, because the
questions span systems.

This document maps that landscape, then states the scope of this project
explicitly. Scoping is a deliberate decision, not an omission.

## 2. Source system landscape

### 2.1 Order management system (OMS)

- **Owner:** Merchant Operations, Seller Onboarding
- **Upstream:** merchant dashboard, e-commerce platform APIs
- **Key data:** order ID, merchant ID, pickup and delivery addresses, SKU
  detail, declared value, service level, payment type
- **Analytical value:** order volume, merchant performance, revenue, regional
  demand
- **Status:** IN SCOPE

### 2.2 Carrier integrations

- **Owner:** Carrier Management
- **Upstream:** partner carrier APIs and file feeds
- **Key data:** scan events, pickup and delivery timestamps, attempt counts,
  failure reasons, return-to-origin events
- **Analytical value:** on-time delivery, SLA monitoring, carrier comparison,
  RTO analysis
- **Status:** IN SCOPE

### 2.3 Vehicle telematics / GPS

- **Owner:** Fleet Operations
- **Upstream:** simulated in-vehicle devices and driver app
- **Key data:** position events, stop events, route adherence, delivery
  attempt geolocation
- **Analytical value:** independent verification of carrier scans, dwell time,
  failure hotspots
- **Status:** IN SCOPE

### 2.4 Weather

- **Owner:** External — Open-Meteo public API
- **Upstream:** Open-Meteo REST API, queried by postcode and delivery region
- **Key data:** temperature, precipitation, wind speed, weather condition code
- **Analytical value:** correlation between weather conditions and delivery
  failure rates, regional performance adjustment
- **Status:** IN SCOPE

### 2.5 Reference and master data

- **Owner:** Data / Operations
- **Upstream:** ABS geography, Australia Post postcode data, internal carrier
  and service-level master lists
- **Key data:** postcode to locality to state mapping, remoteness
  classification, carrier and service code lists
- **Analytical value:** consistent geography for aggregation; decoding
  carrier-specific status codes
- **Status:** IN SCOPE

### 2.6 Warehouse management system (WMS)

- **Owner:** Fulfilment Operations
- **Key data:** inventory levels, pick and pack times, dispatch timestamps,
  damage records
- **Analytical value:** fulfilment efficiency, inventory ageing
- **Status:** OUT OF SCOPE

### 2.7 Payments and finance

- **Owner:** Finance, Reconciliation
- **Key data:** carrier invoices, merchant payouts, commission revenue,
  refunds
- **Analytical value:** margin per shipment, invoice reconciliation,
  profitability
- **Status:** OUT OF SCOPE

### 2.8 Customer support / CRM

- **Owner:** Customer Support, Merchant Support
- **Key data:** tickets, complaint categories, resolution times, escalations
- **Analytical value:** support load driven by delivery failure, SLA
  compliance
- **Status:** OUT OF SCOPE

### 2.9 Risk and fraud

- **Owner:** Risk and Compliance
- **Key data:** high-RTO merchants, suspicious address patterns, blacklists
- **Analytical value:** merchant quality scoring, risk models
- **Status:** OUT OF SCOPE

### 2.10 Marketing

- **Owner:** Marketing, Growth
- **Key data:** campaign spend, merchant acquisition, conversion, CAC
- **Analytical value:** acquisition ROI
- **Status:** OUT OF SCOPE

## 3. Scope decision

Five sources are implemented; five are documented and excluded.

**Why these five:** together they are sufficient to reconstruct the shipment
journey end to end and answer the delivery-performance questions in the
charter. They exercise four genuinely different ingestion patterns:
- Change data capture (orders)
- Batch file ingestion (carrier scans)
- Streaming (GPS telemetry)
- REST API with incremental loading (weather)

**Why the rest are excluded:** finance, CRM, risk and marketing answer
different questions and would add breadth without adding depth. WMS is
closest to in scope but Meridian does not operate warehousing for the
majority of its volume.

**What a real programme would do:** deliver the delivery-performance domain
first, prove the platform, then extend to finance reconciliation — the
highest-value next domain.

## 4. Ownership model

Each source system has a business owner accountable for its data. The platform
team owns ingestion, modelling and serving, not the source data itself.
Data quality issues originating upstream are raised with the owning group
rather than silently corrected in the pipeline.