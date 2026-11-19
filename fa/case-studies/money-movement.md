---
order: 3
title: مدیریت تراکنش و جلوگیری از پرداخت تکراری
summary: اگر کاربر دو بار دکمهٔ «پرداخت» را بزند یا وسط تراکنش اینترنتش قطع شود، پول باید دقیقاً یک بار جابه‌جا شود.
companies: [Carbon OS, GSMPay]
company_about: همین مکانیزم‌ها در هر دو شرکت.
period: ۲۰۲۴ – اکنون
role: طراحی و پیاده‌سازی مکانیزم‌های کنترل تراکنش برای جلوگیری از پرداخت تکراری و مدیریت درخواست‌های هم‌زمان در سیستم‌های مالی.
mockup: once
stats:
  - value: فقط ۱ بار
    label: هر تراکنش دقیقاً یک بار ثبت می‌شود، حتی اگر درخواست دو بار برسد
  - value: "۰"
    label: اختلاف بین بدهکار و بستانکار — دفتر همیشه تراز است
  - value: "۲"
    label: شرکت که این مکانیزم‌ها را در پرداخت‌های کیف پولشان پیاده کردم
steps:
  - title: دو بار زدن «پرداخت»
    text: صفحه هنگ کرده و کاربر دوباره می‌زند.
  - title: درخواست اول انجام می‌شود
    text: کیف پول برای چند میلی‌ثانیه Lock می‌شود.
  - title: درخواست دوم شناسایی می‌شود
    text: کد پیگیری تکراری است، پس دوباره کسر نمی‌شود.
  - title: فقط یک بار کسر
    text: کاربر یک تراکنش درست می‌بیند.
stack: [PHP, Laravel, MySQL, Redis, PHPUnit]
---
## مشکل چه بود

فرض کنید دو پرداخت دقیقاً هم‌زمان از یک کیف پول انجام شود (Race Condition)، یا کاربر چون صفحه هنگ کرده دو بار «پرداخت» را بزند. بدون محافظت، هر دو درخواست ممکن است انجام شوند: موجودی کیف پول منفی شود، یا از کاربر دو بار پول کسر شود.

در یک شرکت پرداخت، هر کدام از این خطاها یعنی ضرر مالی واقعی — و کاربری که دیگر به اپ اعتماد نمی‌کند.

## چه ساختم

مکانیزم‌هایی که پرداخت‌های کیف پول در Carbon و GSMPay از آن‌ها عبور می‌کنند:

- **Lock روی کیف پول.** وقتی درخواست پرداخت به یک کیف پول می‌رسد، رکورد آن داخل تراکنش دیتابیس Lock می‌شود. درخواست دوم صبر می‌کند و موجودیِ به‌روز را می‌خواند.
- **Idempotency.** هر پرداخت یک کد پیگیری یکتا دارد. اگر همان کد دوباره برسد، سیستم نتیجهٔ قبلی را برمی‌گرداند و دوباره کسر نمی‌کند.
- **دفتر دوطرفه (Double-entry).** هر مبلغی که از یک حساب بدهکار می‌شود، به حساب دیگری بستانکار می‌شود؛ پس جمع‌ها همیشه با هم می‌خواند.
- **یکسان‌سازی ارز.** موجودی‌ها با ارزهای مختلف، قبل از بررسی به ریال تبدیل می‌شوند.

## نتیجه

حتی با Retry، اینترنت کند و درخواست‌های هم‌زمان زیاد، هر پرداخت فقط یک نتیجهٔ درست دارد — و دفتر همیشه تراز است.

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
