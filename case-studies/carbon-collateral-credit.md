---
order: 1
title: Borrow money without selling your savings
summary: At Carbon, people who own gold, silver, crypto or investment funds can use them as a guarantee and get spending money right away — without selling anything.
companies: [Carbon OS]
company_about: A financial app for small businesses — payments, wallets and credit.
period: 2026 – now
role: I designed and built the whole credit system, from start to finish.
mockup: credit
stats:
  - value: "4"
    label: investment platforms connected through one system
  - value: "4"
    label: ways to pay for a single purchase, mixed in any combination
  - value: Early
    label: warning on Slack before the money available for loans runs low
steps:
  - title: You own savings
    text: Gold, silver, crypto or investment funds.
  - title: The app shows your limit
    text: It works out how much you can safely spend against them.
  - title: You buy now
    text: Your savings stay invested — nothing is sold.
  - title: If prices drop
    text: Only a small part is sold, just enough to keep the loan safe.
stack: [PHP 8.4, Laravel 13, Horizon, Redis, Elasticsearch, Prometheus]
---
## The problem

Many people keep their savings in gold, silver, crypto or investment funds. When their business needs cash, the usual option is to sell — and miss out if prices go up later.

Carbon wanted to let them borrow against those savings instead. That is risky for the company: if prices fall, the savings might no longer cover the loan.

## What I built

I designed and built the credit system from start to finish:

- **"How much can I spend?"** The system looks at everything a person owns and works out how much they can safely borrow, using the safest savings first.
- **"What if prices fall?"** It keeps an eye on prices. If the savings get too close to the loan amount, it sells only what is needed, one fund at a time — not everything at once.
- **Many ways to pay.** One purchase can be paid from a mix of the person's wallet, their company account, an online card payment and a bank receipt, in a fixed order. I tested every possible combination.
- **Connected to 4 investment platforms** through one shared design, so adding a fifth one doesn't mean rebuilding the system.

## The result

People can get spending money without selling their savings. New investment platforms can be added without touching how orders work, and the team gets a Slack warning before the money available for loans runs low.

Along the way I also fixed a crash in the live system (one big part was running out of memory) by splitting it into smaller, focused pieces.

## Technical details

### Constraints

- Four brokerage APIs, each with its own order semantics and failure modes.
- Sell orders that settle on different schedules per fund.
- Balances that must never go negative under concurrent requests, across multiple currencies.
- A long-running credit-backing job that had already exhausted memory in production.

### Approach

An asset-preference ordering decides which holdings back credit first, and purchasing power is calculated per asset. Margin protection watches the position, and when it is breached the system submits deferred, per-fund sell orders instead of liquidating everything at once.

A broker order-handler strategy puts all four brokerage APIs behind one interface, so adding a broker does not touch the order flow. A single fund order can be paid from user wallets, organization accounts, online gateways and bank receipts in a defined precedence, with regression tests over every payment combination.

The monolithic credit-backing service was split into focused single-responsibility services, which removed the memory-exhaustion failure. Loan-status and provider-credit metrics in Prometheus alert on Slack before allocatable credit falls below safe thresholds.
