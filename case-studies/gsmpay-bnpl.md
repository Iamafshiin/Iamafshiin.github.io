---
order: 2
title: BNPL lending at GSMPay
highlight: lending
company: GSMPay
period: 2024 – 2026
role: Built core lending flows and banking-rail integrations
stack: [PHP, Laravel, Microservices, MySQL, MongoDB, Docker, OpenAPI]
---
## Context

GSMPay is a mobile-focused buy-now-pay-later lendtech. It works with 7,000+ partner stores and issued more than IRR 15 trillion in credit in the first half of 2024.

## Problem

A consumer BNPL product needs the full credit lifecycle — from application through partner-bank approval to installments — to be reliable for customers, merchants and the finance team at the same time.

## Constraints

- Approval depends on partner banks and external checks: cheque inquiry for collateral, IBAN ownership verification and bank credit scoring.
- Several upstream providers for the same check, which can change.
- Money moves between services, so concurrent requests must not create race conditions.
- Finance and operations need exports and reports they can rely on every day.

## Approach

Core lending flows cover loan origination, installment scheduling and payment, chain-product orders with multi-installment settlement, contract PDF generation, and wallet suspension for delinquent borrowers.

Banking-rail checks sit behind a proxy abstraction that supports multiple upstream providers, feeding a partner-bank approval workflow. Business rules are modelled with domain-driven design, and concurrency controls guard money movement between services.

Customer, merchant and gateway apps use 40+ documented REST endpoints (OpenAPI/Swagger), each shipped with feature tests.

## Outcome

The lending flows serve a platform with 7,000+ partner stores, and finance and operations use the back-office exports and reports daily.
