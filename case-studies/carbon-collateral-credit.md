---
order: 1
title: Collateral-backed credit at Carbon
highlight: credit
company: Carbon OS
period: 2026 – present
role: Designed and shipped the credit system end to end
stack: [PHP 8.4, Laravel 13, Horizon, Redis, Elasticsearch, Prometheus]
diagram: credit-states
---
## Context

Carbon is a financial operating system for micro-businesses: payments, wallets and asset-backed credit through licensed partners.

## Problem

Users hold mutual funds, gold, silver and crypto. They need purchasing power now without selling those holdings, and the platform needs to stay protected when prices move against the collateral.

## Constraints

- Four brokerage APIs, each with its own order semantics and failure modes.
- Sell orders that settle on different schedules per fund.
- Balances that must never go negative under concurrent requests, across multiple currencies.
- A long-running credit-backing job that had already exhausted memory in production.

## Approach

An asset-preference ordering decides which holdings back credit first, and purchasing power is calculated per asset. Margin protection watches the position, and when it is breached the system submits deferred, per-fund sell orders instead of liquidating everything at once.

A broker order-handler strategy puts all four brokerage APIs behind one interface, so adding a broker does not touch the order flow. A single fund order can be paid from user wallets, organization accounts, online gateways and bank receipts in a defined precedence, with regression tests over every payment combination.

The monolithic credit-backing service was split into focused single-responsibility services, which removed the memory-exhaustion failure.

## Outcome

Users can borrow against their holdings without selling them, brokers are added without changes to the order flow, and loan-status and provider-credit metrics in Prometheus alert on Slack before allocatable credit falls below safe thresholds.
