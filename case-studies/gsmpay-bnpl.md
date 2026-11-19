---
order: 2
title: Buy now, pay in monthly installments
summary: At GSMPay, shoppers at 7,000+ partner stores take a product home today and pay for it over several months.
company: GSMPay
company_about: Buy now, pay later at 7,000+ partner stores.
period: 2024 – 2026
role: I built the core of the loan process — applying, bank approval, the payment schedule and the contract.
mockup: installments
stats:
  - value: 7,000+
    label: partner stores where customers use it
  - value: 15T+ IRR
    label: in credit given out in the first half of 2024 alone
  - value: 40+
    label: app features I built, each one documented and tested
steps:
  - title: Pick a product
    text: At any of the 7,000+ partner stores.
  - title: Apply in the app
    text: A few taps instead of paperwork.
  - title: Checks happen automatically
    text: The bank approves, the contract is generated.
  - title: Pay monthly
    text: The app tracks every installment.
stack: [PHP, Laravel, Microservices, MySQL, MongoDB, Docker, OpenAPI]
---
## The problem

GSMPay lets shoppers buy now and pay later at more than 7,000 partner stores. Every loan involves the customer, the store, a partner bank and GSMPay's own finance team — and all of them need it to simply work, every time.

## What I built

I built the core of the loan process:

- **The loan journey.** Applying, approval, an automatically generated contract (PDF), the monthly payment schedule, and paying each installment.
- **Bank checks, done automatically.** Checking the customer's cheque (used as a guarantee), confirming the bank account really belongs to them, and getting a credit score. It can switch between different check providers without changes to the app.
- **Handling missed payments.** Customers who stop paying have their wallet paused.
- **40+ features** used by the customer app, the store app and the payment system — each one documented and tested.
- **Reports for the office.** Payment exports, bank reports and Excel files that the finance and operations teams use every day.

## The result

The loan system runs at 7,000+ partner stores, and GSMPay's finance and operations teams rely on the reports every day.

## Technical details

### Constraints

- Approval depends on partner banks and external checks: Sayad cheque inquiry for collateral, IBAN ownership verification and bank credit scoring.
- Several upstream providers for the same check, which can change.
- Money moves between services, so concurrent requests must not create race conditions.

### Approach

Core lending flows cover loan origination, installment scheduling and payment, chain-product orders with multi-installment settlement, contract PDF generation, and wallet suspension for delinquent borrowers.

Banking-rail checks sit behind a proxy abstraction that supports multiple upstream providers, feeding a partner-bank approval workflow. Business rules are modelled with domain-driven design on a microservices architecture, and concurrency controls guard money movement between services.

Customer, merchant and gateway apps use 40+ documented REST endpoints (OpenAPI/Swagger), each shipped with feature tests. Services are Dockerized, and slow SQL and MongoDB queries were tuned.
