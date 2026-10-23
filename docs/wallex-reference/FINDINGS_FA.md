# یافته‌های مهم از مستندات والکس

این یادداشت بازنویسی اطلاعات فنی است؛ کد اجرایی یا مجوز معامله نیست.

## احراز هویت حساب اعتباری

حساب اصلی و هر حساب اعتباری، کلید مخصوص خود دارند. هنگام ساخت کلید باید همان حساب انتخاب شود. مجوز خواندن، معامله و برداشت مستقل‌اند و انقضای کلید باید بررسی شود.

منبع: [ساخت API-Key](https://developers.wallex.ir/docs/create-api-key).

برای اسپات حساب اعتباری، مستندات این دو جزء را لازم می‌دانند:

- کلید API مخصوص همان حساب اعتباری؛
- هدر `sub-account-client-id` با شناسهٔ همان حساب.

مسیر `GET /sub-accounts` و فیلد `clientId` برای فهرست حساب‌ها معرفی شده‌اند. مثال روایی result را object نشان می‌دهد، ولی پاسخ خصوصی قبلی پروژه array بود؛ این تفاوت باید در parser بررسی شود.

منابع: [معرفی اسپات](https://developers.wallex.ir/docs/spot-intro)، [فهرست حساب‌ها](https://developers.wallex.ir/docs/trade-credit-active-sub-account-list).

Swagger اعتبار نیز هدر `sub-account-client-id` را برای `GET /v1/account/balances-detail` و `GET /v1/prop/user/packages/active` اعلام می‌کند. جزئیات در [قراردادهای فنی](API_CONTRACTS.md) ذخیره شده است.

این یافته، روش REST را مستند می‌کند؛ انتقال هدر از MCP به API هنوز بررسی نشده و علت قطعیِ خطای 401 قبلی یا اعتبار کلید فعلی اثبات نشده است.

## تفاوت قراردادهای لغو

دو شکل در Swagger آمده است:

- `DELETE /v1/account/orders` با body شامل `clientOrderId`؛
- `DELETE /v1/account/orders/{client_id}` با شناسه در path.

صفحهٔ روایی لغو، مسیر دوم را معرفی می‌کند. آداپتر فعلی پروژه قرارداد query قدیمی دارد؛ اصلاح آن کار جداگانه است و در این خزش انجام نشده.

منابع: [لغو سفارش](https://developers.wallex.ir/docs/spot-cancel-order)، [قراردادهای استخراج‌شده](API_CONTRACTS.md).

## سفارش، بازار و واحدهای مالی

نوع‌های سفارش موجود در مستندات الزاماً در QuantPilot فعال نیستند. بازارهای طرح اعتباری باید با `unavailableMarkets` و whitelist پروژه بررسی شوند. حفظ Decimal و حسابداری TMN سیاست پروژه است؛ این خزش هیچ مسیر معاملاتی جدیدی فعال نمی‌کند.

منابع: [اسپات](https://developers.wallex.ir/docs/spot-intro)، [پکیج‌های اعتباری](https://developers.wallex.ir/docs/trade-credit-active-packages).

## وب‌سوکت

مستندات Centrifugo و آدرس جدید `wss://api.wallex.ir/connection/websocket` را معرفی می‌کنند. مسیر قدیمی `wss://api.wallex.ir/ws` نیز در راهنمای سازگاری آمده است. نمونه‌های نسخه‌های مختلف را بدون بررسی قرارداد ترکیب نکنید.

منبع: [وب‌سوکت](https://developers.wallex.ir/docs/socket-intro).

## پوشش و محدودیت‌ها

- هر ۱۱۴ صفحهٔ کشف‌شده از sitemap و لینک‌های داخلی خوانده شد؛ صف باقی‌مانده و خطای نهایی صفر است.
- پنج فایل Swagger رسمی خوانده شد و ۵۳ عملیات HTTP از آن‌ها استخراج شد.
- متن روایی کامل، تصاویر و مقادیر نمونهٔ حساب‌ها بازنشر نشده‌اند.
- HTML بدون اجرای JavaScript خوانده شد؛ schemaهای رسمی، جزئیات فرم‌های API را تکمیل می‌کنند.
- description، summary و example از نسخه‌های فنیِ ذخیره‌شدهٔ schema حذف شده‌اند؛ فایل‌های اصلی عیناً mirror نشده‌اند.
- صفحات بدون لینک و خارج از sitemap تضمین نمی‌شوند.
- هیچ API خصوصی، کلید، سفارش، لغو، انتقال وجه یا فعال‌سازی طرح در این خزش استفاده نشد.
- APIهای تعهدی و برداشت فقط برای پوشش مرجع ثبت شدند و در برنامه فعال نشده‌اند.

گزارش‌ها: [صفحات](manifest.json)، [schemaها](swagger-manifest.json)، [پوشش](COVERAGE.md).
