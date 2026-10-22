# نُوا — موتور معاملاتی پایتون با رابط وب

گردش کار تحلیل به LangGraph منتقل شده است؛ ابزارهای تحلیل/MCP و حافظه در گره‌ها استفاده می‌شوند و checkpointها در SQLite ذخیره می‌شوند. [راهنمای LangGraph و محدودیت‌های فعلی](docs/LANGGRAPH.md).

حافظهٔ پایدار SQLite برای تصمیم‌ها، درخواست‌های ردشده و یادداشت‌ها اضافه شده است. جزئیات API و محدودیت‌ها در [راهنمای حافظه](docs/MEMORY.md) آمده است.

پروژه اکنون دو بخش دارد:

- رابط React/Vite برای نمایش اتصال، بازارهای قابل بررسی و سیگنال‌ها.
- بک‌اند FastAPI/Python که به‌عنوان **MCP client** به MCP بازار شما وصل می‌شود، ابزارهایش را کشف می‌کند، دادهٔ کندل را می‌خواند و تحلیل توضیح‌پذیر EMA/RSI/حجم تولید می‌کند.

## اجرای محلی

یک ترمینال برای بک‌اند:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

در ترمینال دیگر، UI را اجرا کنید:

```powershell
npm.cmd install
npm.cmd run dev
```

رابط روی آدرس Vite باز می‌شود و `/api` را به Python روی پورت ۸۰۰۰ پروکسی می‌کند. مستند API در `http://127.0.0.1:8000/docs` است.

## اتصال به MCP دادهٔ شما

بک‌اند Python یک MCP client استاندارد است. در `.env` یکی از این transportها را تنظیم کنید:

### MCP با Streamable HTTP

```dotenv
MCP_TRANSPORT=streamable_http
MCP_URL=https://api.wallex.ir/mcp
WALLEX_API_KEY=your-secret-key
```

### MCP با stdio

طبق راهنمای راه‌اندازی والکس، ابزارهای عمومی کلید نمی‌خواهند و برای ابزارهای خصوصی مقدار `WALLEX_API_KEY` در هدر `X-API-Key` ارسال می‌شود. کلید را فقط در `.env` محلی وارد کنید؛ این فایل در gitignore است. پس از تغییر کلید، بک‌اند را ری‌استارت کنید. تنظیم کلید به‌تنهایی مشکل اتصال شبکه را برطرف نمی‌کند و اجرای سفارش را فعال نمی‌کند.

```dotenv
MCP_TRANSPORT=stdio
MCP_COMMAND=python
MCP_ARGS=["path/to/your_mcp_server.py"]
MCP_ENV_JSON={}
```

بعد از اجرا، `GET /api/mcp/tools` ابزارهای قابل دسترسی را فهرست و بر اساس نام/توضیح برای نقش‌های بازار، ticker، candles، balance و orders دسته‌بندی می‌کند. اگر بیش از یک ابزار برای یک نقش match شود، نام ابزار دقیق را در متغیر مربوطه مشخص کنید؛ برای مثال:

```dotenv
MCP_TOOLS_MARKETS=list_markets
MCP_TOOLS_TICKER=get_ticker
MCP_TOOLS_CANDLES=get_ohlcv
MCP_TOOLS_BALANCE=get_account_balance
MCP_TOOLS_ORDERS=create_order
```

### قرارداد دادهٔ پیشنهادی MCP

بک‌اند برای هر نقش نام ابزار را کشف می‌کند؛ پارامترها را با نام‌های رایج `symbol`, `interval`, `limit` می‌فرستد. ابزار کندل بهتر است این شکل را برگرداند:

```json
{"candles":[{"timestamp":"2026-10-21T10:00:00Z","open":100,"high":104,"low":99,"close":103,"volume":1250}]}
```

یا آرایهٔ OHLCV استاندارد `[timestamp, open, high, low, close, volume]`. ابزار بازار می‌تواند آرایهٔ symbolها یا شیء `{"markets":[{"symbol":"BTC/USDT"}]}` بدهد. اگر schema ابزار شما با این قرارداد فرق دارد، adapter در `backend/market_data.py` را مطابق schema همان MCP تنظیم کنید؛ نام پارامتر ابزارهای MCP از خود schema استخراج و خودکار بازنویسی نمی‌شود.

## APIهای بک‌اند

- `GET /api/health` — وضعیت اتصال MCP و حالت معامله.
- `GET /api/mcp/tools` — ابزارها و نقش‌های کشف‌شده.
- `GET /api/markets` — فهرست بازار و بررسی denylist.
- `GET /api/signals?limit=30` — تحلیل بازارهای مجاز.
- `GET /api/signals/{symbol}` — تحلیل یک بازار.
- `GET /api/balance` — خواندن موجودی از MCP، اگر ابزار موجود باشد.
- `POST /api/orders` — fail-closed: در حالت فعلی سفارش زنده ارسال نمی‌کند.

## بازار و محدودیت چالش

- خرید و فروش فقط اسپات است؛ لوریج پشتیبانی نمی‌شود.
- فهرست ۳۴۴ بازار غیرفعال ارسالی در `src/marketRules.js` قرار دارد و بک‌اند همان فهرست را مستقیم می‌خواند.
- بازارهای مجاز نهایی باید با پاسخ جاری MCP/والکس هم تطبیق داده شوند؛ خارج بودن از denylist به‌تنهایی مجاز بودن بازار را ثابت نمی‌کند.
- کلیدهای API و MCP فقط در `.env` سمت سرور باشند. `.env` در gitignore است.

## وضعیت اجرای معامله

این نسخه به دادهٔ MCP وصل می‌شود و نقطهٔ ورود/خروج پیشنهادی را همراه با دلیل ارائه می‌کند. سفارش واقعی **عمداً پیاده‌سازی/فعال نشده** است: نام و schema ابزار سفارش MCP شما هنوز در پروژه معلوم نیست. `POST /api/orders` در پیکربندی فعلی فقط درخواست را امن رد می‌کند. بعد از دیدن خروجی `GET /api/mcp/tools` و schema ابزار سفارش می‌توان adapter آن را دقیق نوشت؛ تا آن زمان `LIVE_TRADING_ENABLED=false` باقی بماند.

استراتژی فعلی baseline قطعی EMA12/EMA26، RSI14 و نسبت حجم است، نه تضمین «بیشترین سود». قبل از هر سرمایهٔ واقعی به بک‌تست با کارمزد، slippage، تقسیم داده خارج از نمونه، تست سایه، محدودیت افت روزانه، سقف اندازهٔ سفارش و کلید توقف اضطراری نیاز است.
