---
order: 2
title: زیرساخت خرید اقساطی (BNPL)
summary: در GSMPay، مشتری‌ها گوشی و لوازم جانبی را آنلاین یا حضوری، در بیش از ۷٬۰۰۰ فروشگاه همکار در بیش از ۵۰۰ شهر، قسطی می‌خرند.
companies: [GSMPay]
company_about: لندتک تخصصی حوزهٔ موبایل — خرید اقساطی موبایل و لوازم جانبی در بیش از ۷٬۰۰۰ فروشگاه همکار.
period: ۲۰۲۴ – ۲۰۲۶
role: توسعه هسته اصلی فرایند خرید اقساطی؛ شامل ثبت درخواست اعتبار، ارتباط با بانک‌ها، مدیریت قراردادها، محاسبه اقساط و پیگیری بازپرداخت.
mockup: installments
image: /assets/work/gsmpay-credit.webp
image_w: 358
image_h: 855
image_alt: "درخواست اعتبار در GSMPay: انتخاب مبلغ، دورهٔ ۱۲ یا ۲۴ ماهه و بانک، و دیدن مبلغ هر قسط"
image_caption: "درخواست اعتبار در GSMPay — تصویر از سایت gsmpay.ir"
stats:
  - value: بیش از ۷٬۰۰۰
    label: فروشگاه همکار در بیش از ۵۰۰ شهر
  - value: ۷٫۹ همت
    label: تسهیلات اعطاشده تا امروز، طبق سایت gsmpay.ir
  - value: بیش از ۴۰
    label: API با مستندات Swagger و تست
steps:
  - title: ثبت‌نام و احراز هویت
    text: اطلاعات هویتی با سرویس‌های بانکی صحت‌سنجی می‌شود.
  - title: اعتبارسنجی
    text: اعتبارسنجی بانکی به‌صورت خودکار انجام می‌شود.
  - title: انتخاب طرح
    text: مبلغ، دورهٔ ۱۲ یا ۲۴ ماهه و بانک عامل.
  - title: خرید و پرداخت اقساط
    text: آنلاین یا حضوری؛ تک‌تک قسط‌ها پیگیری می‌شود.
stack: [PHP, Laravel, Microservices, MySQL, MongoDB, Docker, OpenAPI]
---
## مشکل چه بود

GSMPay لندتک تخصصی حوزهٔ موبایل است: مشتری‌ها گوشی و لوازم جانبی را آنلاین یا حضوری، در بیش از ۷٬۰۰۰ فروشگاه همکار در بیش از ۵۰۰ شهر، قسطی می‌خرند. در هر وام، مشتری، فروشگاه، بانک عامل و تیم مالی GSMPay درگیرند — و کل فرایند باید برای همه بدون خطا کار کند.

## چه ساختم

هستهٔ اصلی فرایند وام را ساختم:

- **چرخهٔ وام.** ثبت درخواست، تأیید، صدور خودکار قرارداد (PDF)، جدول اقساط و پرداخت هر قسط — به‌علاوهٔ سفارش‌های «اعتبار زنجیره‌ای» فروشگاه‌ها با تسویهٔ چندقسطی.
- **استعلام‌های بانکی.** استعلام چک صیادی برای ضمانت، استعلام مالکیت شبا و اعتبارسنجی بانکی. این استعلام‌ها پشت یک لایهٔ Proxy هستند تا بشود بدون تغییر در اپ، Provider را عوض کرد.
- **مدیریت معوقات.** کیف پول مشتری‌هایی که قسطشان را پرداخت نمی‌کنند، مسدود می‌شود.
- **بیش از ۴۰ API** برای اپ مشتری، اپ فروشگاه و درگاه پرداخت — همه با مستندات Swagger و Feature Test.
- **گزارش‌های پنل ادمین.** خروجی پرداخت‌ها، گزارش‌های بانکی و فایل‌های Excel که تیم‌های مالی و عملیات هر روز از آن‌ها استفاده می‌کنند.

## نتیجه

سیستم وام در بیش از ۷٬۰۰۰ فروشگاه همکار کار می‌کند، و تیم‌های مالی و عملیات GSMPay هر روز با گزارش‌های آن کار می‌کنند.

## جزئیات فنی

### Constraints

- Approval depends on partner banks and external checks: Sayad cheque inquiry for collateral, IBAN ownership verification and bank credit scoring.
- Several upstream providers for the same check, which can change.
- Money moves between services, so concurrent requests must not create race conditions.

### Approach

Core lending flows cover loan origination, installment scheduling and payment, chain-product orders with multi-installment settlement, contract PDF generation, and wallet suspension for delinquent borrowers.

Banking-rail checks sit behind a proxy abstraction that supports multiple upstream providers, feeding a partner-bank approval workflow. Business rules are modelled with domain-driven design on a microservices architecture, and concurrency controls guard money movement between services.

Customer, merchant and gateway apps use 40+ documented REST endpoints (OpenAPI/Swagger), each shipped with feature tests. Services are Dockerized, and slow SQL and MongoDB queries were tuned.
