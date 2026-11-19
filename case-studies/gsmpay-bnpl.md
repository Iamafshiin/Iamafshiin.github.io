---
order: 2
title: Buy now, pay in monthly installments
summary: At GSMPay, people buy phones and accessories in installments — online or in person, at 7,000+ partner stores in 500+ cities.
companies: [GSMPay]
company_about: A lendtech for the mobile phone market — phones and accessories in installments at 7,000+ partner stores.
period: 2024 – 2026
role: I built the core of the loan process — applying, bank approval, the payment schedule and the contract.
mockup: installments
image: /assets/work/gsmpay-credit.webp
image_w: 358
image_h: 855
image_alt: "GSMPay credit request: choose an amount, a 12- or 24-month plan and a bank, then see each installment"
image_caption: "Credit request on GSMPay — image from gsmpay.ir"
stats:
  - value: 7,000+
    label: partner stores in more than 500 cities
  - value: 7.9T toman
    label: in credit granted so far, according to gsmpay.ir
  - value: 40+
    label: app features I built, each one documented and tested
steps:
  - title: Sign up
    text: Identity details are checked automatically with banking services.
  - title: Credit check
    text: The bank's credit scoring runs in the background.
  - title: Choose a plan
    text: Amount, 12 or 24 months, and the lending bank.
  - title: Buy and pay monthly
    text: Online or in store; every installment is tracked.
stack: [PHP, Laravel, Microservices, MySQL, MongoDB, Docker, OpenAPI]
---
## The problem

GSMPay is a lendtech for the mobile phone market: people buy phones and accessories in installments, online or in person, at more than 7,000 partner stores in 500+ cities. Every loan involves the customer, the store, a partner bank and GSMPay's own finance team — and all of them need it to simply work, every time.

## What I built

I built the core of the loan process:

- **The loan journey.** Applying, approval, an automatically generated contract (PDF), the monthly payment schedule, and paying each installment — plus chain-credit orders for stores, settled over several installments.
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
