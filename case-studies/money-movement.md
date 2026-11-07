---
order: 3
title: Money movement that stays correct
highlight: stays correct
company: Carbon OS · GSMPay
period: 2024 – present
role: Designed the concurrency and idempotency guards for wallet and lending flows
stack: [PHP, Laravel, MySQL, Redis, PHPUnit]
---
## Context

Both Carbon and GSMPay move money between wallets, organization accounts, gateways and banks. These are the patterns used at both.

## Problem

Under concurrency, two requests can read the same balance and both spend it. Retries and duplicate callbacks can apply the same payment twice. Either failure loses real money.

## Constraints

- Requests for the same wallet arrive concurrently from apps, gateways and background jobs.
- Upstream callbacks and client retries repeat with the same tracking code.
- Balances span multiple currencies and must normalize to one unit.

## Approach

Wallet payment requests lock the rows they change with pessimistic locking inside one database transaction, so a second request waits instead of reading a stale balance. Idempotency guards reject duplicate deposit tracking codes, so a replay returns the original result rather than posting again. Postings follow double-entry rules: every movement debits one account and credits another by the same amount.

```php
return DB::transaction(function () use ($req) {
    $wallet = Wallet::whereKey($req->walletId)->lockForUpdate()->firstOrFail();
    if (Posting::where('idempotency_key', $req->key)->exists()) {
        return Result::replayed();
    }
    $wallet->debit($req->amount);
});
```

## Outcome

Concurrent requests and retries settle to one correct result, and debits always equal credits.
