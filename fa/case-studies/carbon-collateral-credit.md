---
order: 1
title: زیرساخت اعتبار با پشتوانه دارایی
summary: "در Carbon مفهومی به نام «قدرت خرید» هست: کاربر با دارایی‌های غیرنقدی‌اش مثل طلا، نقره، صندوق درآمد ثابت و رمزارز مستقیماً از فروشگاه‌ها خرید می‌کند — بدون اینکه اول آن‌ها را نقد کند."
companies: [Carbon OS]
company_about: سیستم عامل مالی برای کسب‌وکارهای خُرد — پرداخت، کیف پول و قدرت خرید با طلا، نقره و رمزارز.
period: ۲۰۲۶ – اکنون
role: طراحی و پیاده‌سازی زیرساخت اعتباردهی با پشتوانه طلا، نقره و رمزارز؛ از مدیریت وثیقه و محاسبه اعتبار قابل استفاده تا اتصال به کارگزاری‌ها و مدیریت عملیات مالی.
mockup: credit
image: /assets/work/carbon-app.webp
image_w: 600
image_h: 1133
image_alt: "اپ Carbon: پرداخت به فروشگاه هم‌زمان از کیف نقدی کربن، کیف قدرت خرید طلا و نقره و اعتبار تجمیعی تسهیلاتیاران"
image_caption: "اپ Carbon — تصویر از سایت carbon.ir"
stats:
  - value: "۴"
    label: کارگزاری، پشت یک Interface مشترک
  - value: "۴"
    label: روش پرداخت برای یک سفارش — کیف پول، حساب سازمانی، درگاه و فیش بانکی
  - value: Slack
    label: هشدار خودکار وقتی اعتبار قابل تخصیص از حد مجاز پایین‌تر برود
steps:
  - title: کاربر دارایی دارد
    text: طلا، نقره، رمزارز یا واحد صندوق.
  - title: سقف اعتبار محاسبه می‌شود
    text: بر اساس ارزش دارایی‌ها و اولویت آن‌ها.
  - title: پرداخت با همان دارایی
    text: لازم نیست اول دارایی را نقد کنید؛ موقع پرداخت مستقیماً از آن استفاده می‌شود.
  - title: Margin Call
    text: اگر قیمت‌ها افت کند، فقط به اندازهٔ لازم فروخته می‌شود.
stack: [PHP 8.4, Laravel 13, Horizon, Redis, Elasticsearch, Prometheus]
---
## مشکل چه بود

خیلی‌ها پس‌اندازشان را به شکل طلا، نقره، رمزارز یا واحد صندوق نگه می‌دارند. وقتی به نقدینگی نیاز دارند، معمولاً مجبورند دارایی را بفروشند — و اگر بعداً قیمت بالا برود، ضرر کرده‌اند.

Carbon می‌خواست کاربران به‌جای فروش، همین دارایی را وثیقه بگذارند و اعتبار بگیرند. ریسکش برای شرکت این است که اگر قیمت‌ها افت کند، ارزش وثیقه دیگر کافیِ اعتبار نباشد.

## چه ساختم

سیستم اعتبار را از ابتدا تا انتها طراحی و پیاده‌سازی کردم:

- **محاسبهٔ قدرت خرید.** سیستم همهٔ دارایی‌های کاربر را بررسی می‌کند و بر اساس اولویت دارایی‌ها، سقف اعتبار را حساب می‌کند.
- **Margin Call و فروش تدریجی.** قیمت‌ها پایش می‌شود و اگر ارزش وثیقه بیش از حد به مبلغ اعتبار نزدیک شود، سفارش فروش فقط به اندازهٔ لازم و به تفکیک هر صندوق ثبت می‌شود — نه فروش کل دارایی یک‌جا.
- **پرداخت چندمنبعی.** یک سفارش را می‌شود با ترکیبی از کیف پول کاربر، حساب سازمانی، درگاه آنلاین و فیش بانکی، با اولویت مشخص پرداخت کرد. برای همهٔ ترکیب‌های ممکن تست نوشتم.
- **اتصال به API چهار کارگزاری** با Strategy Pattern؛ برای اضافه کردن کارگزاری پنجم، روند ثبت سفارش تغییری نمی‌کند.

## نتیجه

کاربران بدون فروش دارایی، اعتبار خرید می‌گیرند. کارگزاری جدید بدون تغییر در روند سفارش اضافه می‌شود، و با مانیتورینگ Prometheus، تیم قبل از کم شدن اعتبار قابل تخصیص در Slack هشدار می‌گیرد.

در همین مسیر، مشکل Memory Exhaustion در Production را هم حل کردم؛ با شکستن یک سرویس بزرگ به چند سرویس کوچک‌تر و تک‌مسئولیتی.

## جزئیات فنی

### Constraints

- Four brokerage APIs, each with its own order semantics and failure modes.
- Sell orders that settle on different schedules per fund.
- Balances that must never go negative under concurrent requests, across multiple currencies.
- A long-running credit-backing job that had already exhausted memory in production.

### Approach

An asset-preference ordering decides which holdings back credit first, and purchasing power is calculated per asset. Margin protection watches the position, and when it is breached the system submits deferred, per-fund sell orders instead of liquidating everything at once.

A broker order-handler strategy puts all four brokerage APIs behind one interface, so adding a broker does not touch the order flow. A single fund order can be paid from user wallets, organization accounts, online gateways and bank receipts in a defined precedence, with regression tests over every payment combination.

The monolithic credit-backing service was split into focused single-responsibility services, which removed the memory-exhaustion failure. Loan-status and provider-credit metrics in Prometheus alert on Slack before allocatable credit falls below safe thresholds.
