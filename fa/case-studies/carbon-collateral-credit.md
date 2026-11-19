---
order: 1
title: وام بگیرید، بدون فروختن پس‌اندازتان
summary: در Carbon، کسانی که طلا، نقره، رمزارز یا صندوق سرمایه‌گذاری دارند می‌توانند همان را پشتوانه کنند و فوراً پول خرج کردنی بگیرند — بدون اینکه چیزی بفروشند.
companies: [Carbon OS]
company_about: اپ مالی برای کسب‌وکارهای کوچک — پرداخت، کیف پول و اعتبار.
period: ۲۰۲۶ – اکنون
role: کل سیستم اعتبار را از صفر تا صد طراحی کردم و ساختم.
mockup: credit
stats:
  - value: "۴"
    label: سکوی سرمایه‌گذاری، متصل از طریق یک سیستم واحد
  - value: "۴"
    label: روش پرداخت برای یک خرید، با هر ترکیبی
  - value: زودهنگام
    label: هشدار در اسلک، پیش از آنکه پولِ در دسترس برای وام کم شود
steps:
  - title: پس‌انداز دارید
    text: طلا، نقره، رمزارز یا صندوق سرمایه‌گذاری.
  - title: اپ سقف خرید را نشان می‌دهد
    text: حساب می‌کند با پشتوانهٔ آن‌ها چقدر می‌توانید با خیال راحت خرج کنید.
  - title: همین حالا می‌خرید
    text: پس‌اندازتان سرمایه‌گذاری‌شده می‌ماند — چیزی فروخته نمی‌شود.
  - title: اگر قیمت‌ها پایین بیاید
    text: فقط بخش کوچکی فروخته می‌شود؛ همان‌قدر که وام امن بماند.
stack: [PHP 8.4, Laravel 13, Horizon, Redis, Elasticsearch, Prometheus]
---
## مشکل چه بود

خیلی‌ها پس‌اندازشان را به شکل طلا، نقره، رمزارز یا صندوق سرمایه‌گذاری نگه می‌دارند. وقتی کسب‌وکارشان به پول نقد نیاز دارد، معمولاً تنها راه فروختن است — و اگر بعداً قیمت بالا برود، ضرر کرده‌اند.

Carbon می‌خواست به‌جای فروش، بتوانند با پشتوانهٔ همین پس‌انداز وام بگیرند. این برای شرکت ریسک دارد: اگر قیمت‌ها پایین بیاید، ممکن است پس‌انداز دیگر کافیِ وام نباشد.

## چه ساختم

سیستم اعتبار را از ابتدا تا انتها طراحی کردم و ساختم:

- **«چقدر می‌توانم خرج کنم؟»** سیستم به همهٔ دارایی‌های هر نفر نگاه می‌کند و حساب می‌کند چقدر می‌تواند با خیال راحت قرض بگیرد؛ اول از امن‌ترین دارایی‌ها.
- **«اگر قیمت‌ها پایین بیاید چه؟»** سیستم قیمت‌ها را زیر نظر دارد. اگر ارزش پس‌انداز بیش از حد به مبلغ وام نزدیک شود، فقط همان مقداری که لازم است را می‌فروشد، صندوق به صندوق — نه همه را یک‌جا.
- **چند روش پرداخت.** یک خرید را می‌شود با ترکیبی از کیف پول شخص، حساب شرکتش، پرداخت آنلاین و فیش بانکی، به ترتیبی مشخص پرداخت کرد. همهٔ ترکیب‌های ممکن را تست کردم.
- **اتصال به ۴ سکوی سرمایه‌گذاری** با یک طراحی مشترک؛ برای اضافه کردن سکوی پنجم لازم نیست سیستم از نو ساخته شود.

## نتیجه

مردم می‌توانند بدون فروختن پس‌اندازشان پول خرج کردنی بگیرند. سکوهای سرمایه‌گذاری جدید بدون دست زدن به روند سفارش‌ها اضافه می‌شوند، و تیم پیش از کم شدن پولِ در دسترس برای وام، در اسلک هشدار می‌گیرد.

در همین مسیر، یک خرابی در سیستمِ در حال اجرا را هم برطرف کردم (یک بخش بزرگ حافظه کم می‌آورد)؛ با شکستن آن به چند بخش کوچک‌تر و متمرکز.

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
