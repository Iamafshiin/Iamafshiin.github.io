---
order: 2
title: خرید اقساطی (BNPL)
summary: در GSMPay، مشتری‌ها در بیش از ۷٬۰۰۰ فروشگاه پذیرنده کالا را همان روز تحویل می‌گیرند و هزینه‌اش را قسطی پرداخت می‌کنند.
companies: [GSMPay]
company_about: خرید اقساطی (BNPL) در بیش از ۷٬۰۰۰ فروشگاه پذیرنده.
period: ۲۰۲۴ – ۲۰۲۶
role: هستهٔ اصلی فرایند وام را ساختم — ثبت درخواست، تأیید بانک، جدول اقساط و قرارداد.
mockup: installments
stats:
  - value: بیش از ۷٬۰۰۰
    label: فروشگاه پذیرنده
  - value: ۱۵ هزار میلیارد
    label: ریال اعتبار، فقط در نیمهٔ اول ۲۰۲۴ (بیش از این مقدار)
  - value: بیش از ۴۰
    label: API با مستندات Swagger و تست
steps:
  - title: انتخاب کالا
    text: در یکی از فروشگاه‌های پذیرنده.
  - title: ثبت درخواست در اپ
    text: آنلاین، بدون کاغذبازی.
  - title: استعلام و تأیید بانک
    text: خودکار؛ قرارداد هم خودکار صادر می‌شود.
  - title: پرداخت اقساط
    text: اپ تک‌تک قسط‌ها را پیگیری می‌کند.
stack: [PHP, Laravel, Microservices, MySQL, MongoDB, Docker, OpenAPI]
---
## مشکل چه بود

GSMPay خرید اقساطی (BNPL) را در بیش از ۷٬۰۰۰ فروشگاه پذیرنده ارائه می‌دهد. در هر وام، مشتری، فروشگاه، بانک عامل و تیم مالی GSMPay درگیرند — و کل فرایند باید برای همه بدون خطا کار کند.

## چه ساختم

هستهٔ اصلی فرایند وام را ساختم:

- **چرخهٔ وام.** ثبت درخواست، تأیید، صدور خودکار قرارداد (PDF)، جدول اقساط و پرداخت هر قسط.
- **استعلام‌های بانکی.** استعلام چک صیادی برای ضمانت، استعلام مالکیت شبا و اعتبارسنجی بانکی. این استعلام‌ها پشت یک لایهٔ Proxy هستند تا بشود بدون تغییر در اپ، Provider را عوض کرد.
- **مدیریت معوقات.** کیف پول مشتری‌هایی که قسطشان را پرداخت نمی‌کنند، مسدود می‌شود.
- **بیش از ۴۰ API** برای اپ مشتری، اپ فروشگاه و درگاه پرداخت — همه با مستندات Swagger و Feature Test.
- **گزارش‌های پنل ادمین.** خروجی پرداخت‌ها، گزارش‌های بانکی و فایل‌های Excel که تیم‌های مالی و عملیات هر روز از آن‌ها استفاده می‌کنند.

## نتیجه

سیستم وام در بیش از ۷٬۰۰۰ فروشگاه پذیرنده کار می‌کند، و تیم‌های مالی و عملیات GSMPay هر روز با گزارش‌های آن کار می‌کنند.

## جزئیات فنی

### Constraints

- Approval depends on partner banks and external checks: Sayad cheque inquiry for collateral, IBAN ownership verification and bank credit scoring.
- Several upstream providers for the same check, which can change.
- Money moves between services, so concurrent requests must not create race conditions.

### Approach

Core lending flows cover loan origination, installment scheduling and payment, chain-product orders with multi-installment settlement, contract PDF generation, and wallet suspension for delinquent borrowers.

Banking-rail checks sit behind a proxy abstraction that supports multiple upstream providers, feeding a partner-bank approval workflow. Business rules are modelled with domain-driven design on a microservices architecture, and concurrency controls guard money movement between services.

Customer, merchant and gateway apps use 40+ documented REST endpoints (OpenAPI/Swagger), each shipped with feature tests. Services are Dockerized, and slow SQL and MongoDB queries were tuned.
