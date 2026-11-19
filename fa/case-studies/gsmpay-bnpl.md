---
order: 2
title: الان بخرید، ماهانه قسط بدهید
summary: در GSMPay، خریداران در بیش از ۷٬۰۰۰ فروشگاه همکار کالا را همین امروز می‌برند و هزینه‌اش را در چند ماه پرداخت می‌کنند.
companies: [GSMPay]
company_about: الان بخر، بعداً پرداخت کن؛ در بیش از ۷٬۰۰۰ فروشگاه همکار.
period: ۲۰۲۴ – ۲۰۲۶
role: هستهٔ اصلی فرایند وام را ساختم — درخواست، تأیید بانک، جدول اقساط و قرارداد.
mockup: installments
stats:
  - value: بیش از ۷٬۰۰۰
    label: فروشگاه همکار که مشتری‌ها در آن‌ها از این سیستم استفاده می‌کنند
  - value: ۱۵ هزار میلیارد
    label: ریال اعتبار، فقط در نیمهٔ اول ۲۰۲۴ (بیش از این مقدار)
  - value: بیش از ۴۰
    label: قابلیت در اپ‌ها که ساختم؛ همه مستند و تست‌شده
steps:
  - title: کالا را انتخاب کنید
    text: در هر کدام از بیش از ۷٬۰۰۰ فروشگاه همکار.
  - title: در اپ درخواست بدهید
    text: با چند لمس، به‌جای کاغذبازی.
  - title: بررسی‌ها خودکار انجام می‌شود
    text: بانک تأیید می‌کند و قرارداد ساخته می‌شود.
  - title: ماهانه قسط بدهید
    text: اپ تک‌تک قسط‌ها را پیگیری می‌کند.
stack: [PHP, Laravel, Microservices, MySQL, MongoDB, Docker, OpenAPI]
---
## مشکل چه بود

GSMPay به خریداران اجازه می‌دهد در بیش از ۷٬۰۰۰ فروشگاه همکار، الان بخرند و بعداً پرداخت کنند. در هر وام، مشتری، فروشگاه، یک بانک همکار و تیم مالی خود GSMPay درگیرند — و همه می‌خواهند کار هر بار بی‌دردسر انجام شود.

## چه ساختم

هستهٔ اصلی فرایند وام را ساختم:

- **مسیر وام.** درخواست، تأیید، قراردادی که خودکار ساخته می‌شود (PDF)، جدول اقساط ماهانه و پرداخت هر قسط.
- **استعلام‌های بانکی، خودکار.** بررسی چک مشتری (که به‌عنوان ضمانت استفاده می‌شود)، اطمینان از اینکه حساب بانکی واقعاً متعلق به خود اوست، و گرفتن امتیاز اعتباری. بدون تغییر در اپ می‌شود بین ارائه‌دهندگان مختلف این استعلام‌ها جابه‌جا شد.
- **رسیدگی به قسط‌های پرداخت‌نشده.** کیف پول مشتری‌هایی که پرداخت را متوقف می‌کنند، موقتاً غیرفعال می‌شود.
- **بیش از ۴۰ قابلیت** که اپ مشتری، اپ فروشگاه و سیستم پرداخت از آن‌ها استفاده می‌کنند — همه مستند و تست‌شده.
- **گزارش برای دفتر.** خروجی پرداخت‌ها، گزارش‌های بانکی و فایل‌های اکسل که تیم‌های مالی و عملیات هر روز از آن‌ها استفاده می‌کنند.

## نتیجه

سیستم وام در بیش از ۷٬۰۰۰ فروشگاه همکار کار می‌کند، و تیم‌های مالی و عملیات GSMPay هر روز به این گزارش‌ها تکیه می‌کنند.

## جزئیات فنی

### Constraints

- Approval depends on partner banks and external checks: Sayad cheque inquiry for collateral, IBAN ownership verification and bank credit scoring.
- Several upstream providers for the same check, which can change.
- Money moves between services, so concurrent requests must not create race conditions.

### Approach

Core lending flows cover loan origination, installment scheduling and payment, chain-product orders with multi-installment settlement, contract PDF generation, and wallet suspension for delinquent borrowers.

Banking-rail checks sit behind a proxy abstraction that supports multiple upstream providers, feeding a partner-bank approval workflow. Business rules are modelled with domain-driven design on a microservices architecture, and concurrency controls guard money movement between services.

Customer, merchant and gateway apps use 40+ documented REST endpoints (OpenAPI/Swagger), each shipped with feature tests. Services are Dockerized, and slow SQL and MongoDB queries were tuned.
