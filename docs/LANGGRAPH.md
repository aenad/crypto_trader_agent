# گردش کار LangGraph

مسیرهای `/api/signals` و `/api/signals/{symbol}` اکنون `TradingAgent.run` را فراخوانی می‌کنند. تحلیل مستقیم از handlerهای API حذف شده است.

```text
START → load_memory → fetch_candles → analyze_strategy
      → execution_gate → record_decision → END
```

ابزارهای `get_candles`، `read_memory` و `analyze_market` با StructuredTool تعریف شده‌اند. گره‌ها فعلاً ابزارهای مشخص را مستقیم فراخوانی می‌کنند؛ چرخهٔ LLM/tool-calling و انتخاب ابزار توسط مدل هنوز فعال نیست. پس از ارائهٔ کانفیگ مدل، گره ارزیابی LLM و مسیر شرطی ابزارها قابل اضافه‌شدن است. استراتژی همان baseline موجود است.

## حافظه

- `MEMORY_DB_PATH`: یادداشت‌ها و لاگ ممیزی قبلی. گره load_memory این context را داخل State قرار می‌دهد؛ در baseline محاسباتی برای تغییر قواعد استفاده نمی‌شود.
- `GRAPH_DB_PATH`: checkpointهای StateGraph با AsyncSqliteSaver. پیش‌فرض `data/agent_checkpoints.sqlite3`.
- هر تحلیل تازه یک UUID به‌عنوان thread_id می‌گیرد. thread_id در لاگ تصمیم ذخیره می‌شود و از `/api/memory/events` قابل خواندن است.
- هر checkpoint می‌تواند کندل‌های ورودی و نتیجهٔ همان اجرا را نگه دارد. فایل checkpoint با افزایش اجراها بزرگ می‌شود و به سیاست نگهداری نیاز دارد.
- ثبت لاگ تصمیم بر اساس thread_id تکرارناپذیر است. این ویژگی به معنی جلوگیری از سفارش تکراری صرافی نیست.

checkpoint در فایل ذخیره می‌شود اما API ادامه‌دادن اجرای شکست‌خورده و زمان‌بند بازیابی خودکار هنوز اضافه نشده است. اجرای درخواست تازه همواره دادهٔ تازه می‌گیرد؛ از checkpoint قبلی به‌عنوان دادهٔ بازار فعلی استفاده نمی‌کند.

## اجرا

```powershell
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

LangGraph و SQLite checkpointer برای تحلیل لازم‌اند. در نبود وابستگی، API تحلیل خطای نصب می‌دهد؛ نسخهٔ بدل یا مسیر تحلیل مستقیم وجود ندارد. بخش health و API حافظه بدون LangGraph هم import می‌شوند.

## محدودیت اجرا

execution_gate فعلاً تنها `analysis_only` را ثبت می‌کند؛ مدیریت موجودی، اعتبارسنجی کامل ریسک و ارسال سفارش پیاده نشده‌اند. ابزار معامله به گراف داده نشده است. تنظیمات live به‌تنهایی این گراف را معامله‌گر نمی‌کند. ارتباط موجودی با سیگنال فروش و مدل LLM هم هنوز نیاز به تکمیل دارند.

در این محیط نصب LangGraph از index در دسترس موفق نشد؛ بنابراین اجرای واقعی گراف و ذخیرهٔ checkpoint هنوز آزمایش نشده است. بررسی syntax و ثبت یکتای لاگ با SQLite جداگانه انجام شده است.
