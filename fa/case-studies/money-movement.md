---
order: 3
title: هیچ‌کس دو بار پول نمی‌دهد
summary: وقتی مشتری دو بار «پرداخت» را می‌زند، یا اینترنت وسط کار قطع می‌شود، پول باید باز هم دقیقاً یک بار جابه‌جا شود.
companies: [Carbon OS, GSMPay]
company_about: قوانین ایمنی یکسان، در هر دو شرکت.
period: ۲۰۲۴ – اکنون
role: قوانین ایمنی‌ای را ساختم که هر دو شرکت برای پرداخت‌های کیف پول از آن استفاده می‌کنند.
mockup: once
stats:
  - value: فقط ۱ بار
    label: هر پرداخت دقیقاً یک بار حساب می‌شود، حتی اگر دو بار برسد
  - value: "۰"
    label: اختلاف بین پول خارج‌شده و واردشده — دفترها همیشه تراز است
  - value: "۲"
    label: شرکت که این قوانین را در پرداخت‌های کیف پولشان ساختم
steps:
  - title: دو بار «پرداخت» را می‌زنید
    text: صفحه گیر کرده بود، پس مشتری دوباره زد.
  - title: اولی انجام می‌شود
    text: کیف پول برای کسری از ثانیه رزرو می‌شود.
  - title: دومی شناسایی می‌شود
    text: شمارهٔ رسید یکی است، پس دوباره پرداخت نمی‌شود.
  - title: فقط یک بار کم می‌شود
    text: مشتری یک پرداخت درست می‌بیند.
stack: [PHP, Laravel, MySQL, Redis, PHPUnit]
---
## مشکل چه بود

تصور کنید دو پرداخت دقیقاً در یک لحظه از یک کیف پول انجام شود، یا مشتری چون صفحه گیر کرده دو بار «پرداخت» را بزند. بدون محافظ، ممکن است هر دو انجام شوند: موجودی کیف پول منفی شود، یا از کسی دو بار پول کم شود.

در یک شرکت پرداخت، هر کدام از این اشتباه‌ها یعنی ضرر مالی واقعی — و مشتری‌ای که دیگر به اپ اعتماد نمی‌کند.

## چه ساختم

قوانینی ساده که پرداخت‌های کیف پول در Carbon و GSMPay از آن‌ها عبور می‌کنند:

- **یکی‌یکی.** وقتی پرداختی به یک کیف پول می‌رسد، آن کیف پول برای کسری از ثانیه رزرو می‌شود. پرداخت دوم منتظر نوبتش می‌ماند و موجودیِ به‌روز را می‌بیند.
- **تکراری‌ها نادیده گرفته می‌شوند.** هر پرداخت یک شمارهٔ رسید یکتا دارد. اگر همان شماره دوباره برسد، سیستم نتیجهٔ قبلی را نشان می‌دهد و دوباره پرداخت نمی‌کند.
- **ثبت دوطرفه.** مثل دفتر یک حسابدار، هر مبلغی که از یک حساب کم می‌شود به حساب دیگری اضافه می‌شود، پس جمع‌ها همیشه با هم می‌خواند.
- **یک واحد پول برای مقایسه.** موجودی‌ها با واحدهای پولی مختلف، پیش از بررسی به ریال تبدیل می‌شوند.

## نتیجه

حتی با تلاش‌های دوباره، اینترنت کند و درخواست‌های هم‌زمان زیاد، هر پرداخت به یک نتیجهٔ درست ختم می‌شود — و دفترها همیشه تراز است.

## جزئیات فنی

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
