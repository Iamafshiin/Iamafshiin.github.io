---
order: 3
title: Making sure nobody is charged twice
summary: When a customer taps "Pay" twice, or the internet drops halfway through, the money must still move exactly once.
companies: [Carbon OS, GSMPay]
company_about: The same safety rules, used at both companies.
period: 2024 – now
role: I built the safety rules both companies use for wallet payments.
mockup: once
stats:
  - value: 1×
    label: every payment counted exactly once, even if it arrives twice
  - value: "0"
    label: difference between money out and money in — the books always balance
  - value: "2"
    label: companies where I built these rules into wallet payments
steps:
  - title: Tap "Pay" twice
    text: The screen froze, so the customer tapped again.
  - title: The first one goes through
    text: The wallet is reserved for a split second.
  - title: The second is recognised
    text: Same receipt number, so it is not paid again.
  - title: Charged once
    text: The customer sees one correct payment.
stack: [PHP, Laravel, MySQL, Redis, PHPUnit]
---
## The problem

Imagine two payments leaving the same wallet at exactly the same moment, or a customer tapping "Pay" twice because the screen froze. Without safeguards, both could go through: the wallet goes below zero, or someone is charged twice.

In a payments company, each of those mistakes is real money lost — and a customer who stops trusting the app.

## What I built

Simple rules that wallet payments at Carbon and GSMPay go through:

- **One at a time.** When a payment touches a wallet, the wallet is reserved for a split second. A second payment waits its turn and sees the up-to-date balance.
- **Duplicates are ignored.** Every payment carries a unique receipt number. If the same number arrives again, the system shows the original result instead of paying again.
- **Two-sided records.** Like an accountant's book, every amount taken from one account is added to another, so the totals always match.
- **One currency for comparing.** Balances in different currencies are converted to rials before they are checked.

## The result

Even with retries, slow internet and many requests at the same time, every payment ends with one correct result — and the books always balance.

## Technical details

### Constraints

- Requests for the same wallet arrive concurrently from apps, gateways and background jobs.
- Upstream callbacks and client retries repeat with the same tracking code.
- Balances span multiple currencies and must normalize to one unit.

### Approach

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
