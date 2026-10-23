# Wallex API — مرجع فنی مستندات

مبدأ: https://developers.wallex.ir/docs
زمان دریافت (UTC): 2026-10-23T14:27:41.942278+00:00

این سند بازنویسی و استخراج اطلاعات فنی صفحات است، نه بازنشر کامل متن سایت.
فراخوانی API، سفارش، انتقال وجه یا استفاده از کلید حساب در این خزش انجام نشده است.

## پوشش

- صفحات کشف‌شده: 114
- صفحات خوانده‌شده: 114
- خطاها: 0
- صف باقی‌مانده: 0

کشف از sitemap و لینک‌های داخلی انجام شده؛ صفحات بدون لینک و بدون ورودی sitemap تضمین نمی‌شوند.
پارامترهای استخراج‌شده و مثال‌ها باید با schema رسمی تطبیق داده شوند؛ نبود یک فیلد در این مرجع، نبود آن در API را ثابت نمی‌کند.

## نکات اتصال حساب اعتباری

- در صفحهٔ ساخت کلید، حساب اصلی و هر حساب اعتباری دارای کلید مخصوص خود معرفی شده‌اند.
- برای اسپاتِ حساب اعتباری، صفحهٔ معرفی اسپات علاوه بر کلید همان حساب، هدر `sub-account-client-id` را لازم می‌داند.
- صفحهٔ فهرست زیرحساب‌ها، شناسهٔ حساب را با فیلد `clientId` در مثال معرفی می‌کند؛ شکل واقعی پاسخ باید مستقل بررسی شود.
- این شواهد روش اتصال را مستند می‌کنند؛ علت خطای قبلی 401 یا اعتبار کلید فعلی را ثابت نمی‌کنند.

منابع: [ساخت کلید](https://developers.wallex.ir/docs/create-api-key)، [اسپات](https://developers.wallex.ir/docs/spot-intro)، [فهرست حساب‌ها](https://developers.wallex.ir/docs/trade-credit-active-sub-account-list).

## فهرست صفحات

- [مقدمه](pages/index.md) — [منبع](https://developers.wallex.ir/docs)
- [سرویس های پایه والکس](pages/basic-services.md) — [منبع](https://developers.wallex.ir/docs/basic-services)
- [سطح کاربری و کارمزد](pages/basic-services-account-fee.md) — [منبع](https://developers.wallex.ir/docs/basic-services-account-fee)
- [اضافه کردن شماره شبا بانکی](pages/basic-services-add-iban.md) — [منبع](https://developers.wallex.ir/docs/basic-services-add-iban)
- [کندل ها (آمار OHLC بازارها)](pages/basic-services-candles.md) — [منبع](https://developers.wallex.ir/docs/basic-services-candles)
- [دریافت شماره های کارت بانکی](pages/basic-services-card-numbers.md) — [منبع](https://developers.wallex.ir/docs/basic-services-card-numbers)
- [دریافت آدرس کیف پول رمزارز](pages/basic-services-coin-wallets.md) — [منبع](https://developers.wallex.ir/docs/basic-services-coin-wallets)
- [عمق بازارها](pages/basic-services-depth.md) — [منبع](https://developers.wallex.ir/docs/basic-services-depth)
- [دریافت شماره های شبای بانکی](pages/basic-services-iban-numbers.md) — [منبع](https://developers.wallex.ir/docs/basic-services-iban-numbers)
- [لیست معاملات انجام شده](pages/basic-services-latest-trades.md) — [منبع](https://developers.wallex.ir/docs/basic-services-latest-trades)
- [دریافت موجودی کیف پول حساب اصلی](pages/basic-services-main-wallet.md) — [منبع](https://developers.wallex.ir/docs/basic-services-main-wallet)
- [مارکت های والکس](pages/basic-services-markets.md) — [منبع](https://developers.wallex.ir/docs/basic-services-markets)
- [ثبت درخواست برداشت تومان](pages/basic-services-withdraw-toman.md) — [منبع](https://developers.wallex.ir/docs/basic-services-withdraw-toman)
- [ساخت API-Key](pages/create-api-key.md) — [منبع](https://developers.wallex.ir/docs/create-api-key)
- [Activate User Package](pages/generated__activate-user-package.md) — [منبع](https://developers.wallex.ir/docs/generated/activate-user-package)
- [Active Sub Accounts List](pages/generated__active-sub-accounts-list.md) — [منبع](https://developers.wallex.ir/docs/generated/active-sub-accounts-list)
- [Active User Package Details](pages/generated__active-user-package-details.md) — [منبع](https://developers.wallex.ir/docs/generated/active-user-package-details)
- [Active User Packages Overview](pages/generated__active-user-packages-overview.md) — [منبع](https://developers.wallex.ir/docs/generated/active-user-packages-overview)
- [افزودن شماره شبا جدید به حساب](pages/generated__add-account-iban.md) — [منبع](https://developers.wallex.ir/docs/generated/add-account-iban)
- [calculate min, max Collateral and loan](pages/generated__calculate-loan.md) — [منبع](https://developers.wallex.ir/docs/generated/calculate-loan)
- [Cancel User Package](pages/generated__cancel-user-package.md) — [منبع](https://developers.wallex.ir/docs/generated/cancel-user-package)
- [Get historical market data (candles)](pages/generated__candle-history.md) — [منبع](https://developers.wallex.ir/docs/generated/candle-history)
- [Check Prop Package Availability](pages/generated__check-prop-package-availability.md) — [منبع](https://developers.wallex.ir/docs/generated/check-prop-package-availability)
- [Close a margin position](pages/generated__close-position-id.md) — [منبع](https://developers.wallex.ir/docs/generated/close-position-id)
- [درخواست برداشت وجه از حساب](pages/generated__create-money-withdrawal.md) — [منبع](https://developers.wallex.ir/docs/generated/create-money-withdrawal)
- [Create Transfer To Sub Account](pages/generated__create-transfer-to-sub-account.md) — [منبع](https://developers.wallex.ir/docs/generated/create-transfer-to-sub-account)
- [Cancel an existing order](pages/generated__delete-account-orders.md) — [منبع](https://developers.wallex.ir/docs/generated/delete-account-orders)
- [Cancel an order by path parameter](pages/generated__delete-orders-client.md) — [منبع](https://developers.wallex.ir/docs/generated/delete-orders-client)
- [info a margin position before creation](pages/generated__detailed-information.md) — [منبع](https://developers.wallex.ir/docs/generated/detailed-information)
- [Disable Connect To Wallet](pages/generated__disable-connect-to-wallet.md) — [منبع](https://developers.wallex.ir/docs/generated/disable-connect-to-wallet)
- [Update margin positions collateral](pages/generated__edit-colateral.md) — [منبع](https://developers.wallex.ir/docs/generated/edit-colateral)
- [Update stop-loss and take-profit prices](pages/generated__edit-sltp.md) — [منبع](https://developers.wallex.ir/docs/generated/edit-sltp)
- [Enable Connect To Wallet](pages/generated__enable-connect-to-wallet.md) — [منبع](https://developers.wallex.ir/docs/generated/enable-connect-to-wallet)
- [Enable User Package Renew](pages/generated__enable-user-package-renew.md) — [منبع](https://developers.wallex.ir/docs/generated/enable-user-package-renew)
- [Get account balances](pages/generated__get-account-balances.md) — [منبع](https://developers.wallex.ir/docs/generated/get-account-balances)
- [دریافت شماره کارت‌های بانکی حساب](pages/generated__get-account-card-numbers.md) — [منبع](https://developers.wallex.ir/docs/generated/get-account-card-numbers)
- [دریافت کارمزدهای حساب](pages/generated__get-account-fees.md) — [منبع](https://developers.wallex.ir/docs/generated/get-account-fees)
- [دریافت لیست شماره شباهای حساب](pages/generated__get-account-ibans.md) — [منبع](https://developers.wallex.ir/docs/generated/get-account-ibans)
- [دریافت آدرس کیف‌پول کاربر برای نماد مشخص](pages/generated__get-account-wallet-by-symbol.md) — [منبع](https://developers.wallex.ir/docs/generated/get-account-wallet-by-symbol)
- [Get all markets depth](pages/generated__get-depth.md) — [منبع](https://developers.wallex.ir/docs/generated/get-depth)
- [دریافت معاملات اخیر](pages/generated__get-latest-trades.md) — [منبع](https://developers.wallex.ir/docs/generated/get-latest-trades)
- [margin trade user levels](pages/generated__get-levels.md) — [منبع](https://developers.wallex.ir/docs/generated/get-levels)
- [margin trade user levels](pages/generated__get-levels-market.md) — [منبع](https://developers.wallex.ir/docs/generated/get-levels-market)
- [دریافت عمق بازار](pages/generated__get-market-depth.md) — [منبع](https://developers.wallex.ir/docs/generated/get-market-depth)
- [Get all markets](pages/generated__get-markets.md) — [منبع](https://developers.wallex.ir/docs/generated/get-markets)
- [List active orders](pages/generated__get-open-order.md) — [منبع](https://developers.wallex.ir/docs/generated/get-open-order)
- [List margin orders](pages/generated__get-orders.md) — [منبع](https://developers.wallex.ir/docs/generated/get-orders)
- [Get order details](pages/generated__get-orders-client.md) — [منبع](https://developers.wallex.ir/docs/generated/get-orders-client)
- [get otc markets](pages/generated__get-otc-markets.md) — [منبع](https://developers.wallex.ir/docs/generated/get-otc-markets)
- [get otc price](pages/generated__get-otc-price.md) — [منبع](https://developers.wallex.ir/docs/generated/get-otc-price)
- [User PNL](pages/generated__get-pnl.md) — [منبع](https://developers.wallex.ir/docs/generated/get-pnl)
- [Get a margin position](pages/generated__get-position-id.md) — [منبع](https://developers.wallex.ir/docs/generated/get-position-id)
- [List margin positions](pages/generated__get-positions.md) — [منبع](https://developers.wallex.ir/docs/generated/get-positions)
- [Open a margin position](pages/generated__open-position.md) — [منبع](https://developers.wallex.ir/docs/generated/open-position)
- [create otc trade](pages/generated__place-easy-trade-order.md) — [منبع](https://developers.wallex.ir/docs/generated/place-easy-trade-order)
- [Submit a new trading order](pages/generated__post-account-orders.md) — [منبع](https://developers.wallex.ir/docs/generated/post-account-orders)
- [Calculate](pages/generated__profit-position-id.md) — [منبع](https://developers.wallex.ir/docs/generated/profit-position-id)
- [Prop Package Details](pages/generated__prop-package-details.md) — [منبع](https://developers.wallex.ir/docs/generated/prop-package-details)
- [Prop Packages List](pages/generated__prop-packages-list.md) — [منبع](https://developers.wallex.ir/docs/generated/prop-packages-list)
- [Positions Ratio of long and short](pages/generated__public-ratio.md) — [منبع](https://developers.wallex.ir/docs/generated/public-ratio)
- [Spot](pages/generated__spot.md) — [منبع](https://developers.wallex.ir/docs/generated/spot)
- [Sub Account Balances Details](pages/generated__sub-account-balances-details.md) — [منبع](https://developers.wallex.ir/docs/generated/sub-account-balances-details)
- [List Sub Account Transfers](pages/generated__sub-account-transfer.md) — [منبع](https://developers.wallex.ir/docs/generated/sub-account-transfer)
- [trade-credit](pages/generated__trade-credit.md) — [منبع](https://developers.wallex.ir/docs/generated/trade-credit)
- [User Package History Details](pages/generated__user-package-history-details.md) — [منبع](https://developers.wallex.ir/docs/generated/user-package-history-details)
- [User Package History List](pages/generated__user-package-history-list.md) — [منبع](https://developers.wallex.ir/docs/generated/user-package-history-list)
- [Wallex Margin-trade API](pages/generated__wallex-margin-trade-api.md) — [منبع](https://developers.wallex.ir/docs/generated/wallex-margin-trade-api)
- [مارکت های فعال](pages/margin-active-markets.md) — [منبع](https://developers.wallex.ir/docs/margin-active-markets)
- [محاسبه میزان حداقل و حداکثر وثیقه](pages/margin-calculate-loan.md) — [منبع](https://developers.wallex.ir/docs/margin-calculate-loan)
- [بستن موقعیت تعهدی](pages/margin-close-position.md) — [منبع](https://developers.wallex.ir/docs/margin-close-position)
- [مشاهده اطلاعات موقعیت مارجین قبل از ایجاد](pages/margin-dry-run.md) — [منبع](https://developers.wallex.ir/docs/margin-dry-run)
- [ویرایش وثیقه موقعیت تعهدی](pages/margin-edit-collateral.md) — [منبع](https://developers.wallex.ir/docs/margin-edit-collateral)
- [دریافت موقعیت‌های تعهدی](pages/margin-get-positions.md) — [منبع](https://developers.wallex.ir/docs/margin-get-positions)
- [معامله تعهدی چیست ؟](pages/margin-intro.md) — [منبع](https://developers.wallex.ir/docs/margin-intro)
- [ایجاد موقعیت مارجین](pages/margin-open-position.md) — [منبع](https://developers.wallex.ir/docs/margin-open-position)
- [ویرایش حد سود و حد ضرر موقعیت تعهدی](pages/margin-sltp-edit.md) — [منبع](https://developers.wallex.ir/docs/margin-sltp-edit)
- [اصطلاحات معامله تعهدی](pages/margin-types.md) — [منبع](https://developers.wallex.ir/docs/margin-types)
- [ثبت سفارش در بازار آنی](pages/otc-create-order.md) — [منبع](https://developers.wallex.ir/docs/otc-create-order)
- [خرید و فروش در بازار معاملاتی آنی چیست ؟](pages/otc-intro.md) — [منبع](https://developers.wallex.ir/docs/otc-intro)
- [مارکت های فعال](pages/otc-markets.md) — [منبع](https://developers.wallex.ir/docs/otc-markets)
- [دریافت قیمت ها در بازار آنی](pages/otc-price.md) — [منبع](https://developers.wallex.ir/docs/otc-price)
- [دریافت قیمت لحظه‌ای همه بازارها](pages/socket-all-price.md) — [منبع](https://developers.wallex.ir/docs/socket-all-price)
- [دریافت عمق بازار خرید (buyDepth)](pages/socket-buy-depth.md) — [منبع](https://developers.wallex.ir/docs/socket-buy-depth)
- [دریافت به‌روزرسانی کندل‌های نمودار](pages/socket-candle.md) — [منبع](https://developers.wallex.ir/docs/socket-candle)
- [اتصال و عضویت](pages/socket-connection.md) — [منبع](https://developers.wallex.ir/docs/socket-connection)
- [دریافت قیمت منصفانه](pages/socket-fair-price.md) — [منبع](https://developers.wallex.ir/docs/socket-fair-price)
- [مقدمه](pages/socket-intro.md) — [منبع](https://developers.wallex.ir/docs/socket-intro)
- [راهنمای مهاجرت](pages/socket-migration.md) — [منبع](https://developers.wallex.ir/docs/socket-migration)
- [رویدادهای خصوصی کاربران](pages/socket-private-channel.md) — [منبع](https://developers.wallex.ir/docs/socket-private-channel)
- [اتصال بدون SDK](pages/socket-raw-protocol.md) — [منبع](https://developers.wallex.ir/docs/socket-raw-protocol)
- [دریافت عمق بازار فروش (sellDepth)](pages/socket-sell-depth.md) — [منبع](https://developers.wallex.ir/docs/socket-sell-depth)
- [توکن اتصال خصوصی](pages/socket-token.md) — [منبع](https://developers.wallex.ir/docs/socket-token)
- [دریافت معاملات انجام‌شده](pages/socket-trade.md) — [منبع](https://developers.wallex.ir/docs/socket-trade)
- [مارکت های فعال](pages/spot-active-markets.md) — [منبع](https://developers.wallex.ir/docs/spot-active-markets)
- [لیست سفارشات فعال](pages/spot-active-orders.md) — [منبع](https://developers.wallex.ir/docs/spot-active-orders)
- [لغو سفارش](pages/spot-cancel-order.md) — [منبع](https://developers.wallex.ir/docs/spot-cancel-order)
- [ثبت سفارش](pages/spot-create-order.md) — [منبع](https://developers.wallex.ir/docs/spot-create-order)
- [معامله اسپات چیست؟](pages/spot-intro.md) — [منبع](https://developers.wallex.ir/docs/spot-intro)
- [دریافت لیست سفارش‌ها](pages/spot-order-list.md) — [منبع](https://developers.wallex.ir/docs/spot-order-list)
- [دریافت جزئیات سفارش](pages/spot-single-order-detail.md) — [منبع](https://developers.wallex.ir/docs/spot-single-order-detail)
- [انواع سفارش در معاملات اسپات](pages/spot-types.md) — [منبع](https://developers.wallex.ir/docs/spot-types)
- [فعال کردن پکیج اعتبار معاملاتی](pages/trade-credit-activate-sub-account.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-activate-sub-account)
- [پکیج های فعال اعتبار معاملاتی والکس](pages/trade-credit-active-packages.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-active-packages)
- [لیست حساب های اعتبار معاملاتی](pages/trade-credit-active-sub-account-list.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-active-sub-account-list)
- [بستن اکانت اعتبار معاملاتی](pages/trade-credit-close-sub-account.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-close-sub-account)
- [بررسی شرایط کاربر برای دریافت اعتبار معاملاتی](pages/trade-credit-condition-check.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-condition-check)
- [اتصال کیف پول اصلی به اکانت اعتبار معاملاتی](pages/trade-credit-connect-wallet.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-connect-wallet)
- [قطع اتصال کیف پول اصلی از اکانت اعتبار معاملاتی](pages/trade-credit-disconnect-wallet.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-disconnect-wallet)
- [اعتبار معاملاتی چیست؟](pages/trade-credit-intro.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-intro)
- [دریافت جزیيات پکیج و لیست بازارهای غیر فعال](pages/trade-credit-package-details.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-package-details)
- [دریافت تاریخچه طرح های اعتبار معاملاتی](pages/trade-credit-sub-account-history.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-sub-account-history)
- [trade-credit-sub-account-transfer](pages/trade-credit-sub-account-transfer.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-sub-account-transfer)
- [اصطلاحات اعتبار معاملاتی](pages/trade-credit-types.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-types)
- [trade-credit-wallet](pages/trade-credit-wallet.md) — [منبع](https://developers.wallex.ir/docs/trade-credit-wallet)

## محتوای فنی همهٔ صفحات

---

# مقدمه

Source: https://developers.wallex.ir/docs

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Header names appearing in this page

`Content-Type`

## Documented protocol addresses (not called)

- `https://api.wallex.ir`

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# سرویس های پایه والکس

Source: https://developers.wallex.ir/docs/basic-services

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Official schema downloads

- https://developers.wallex.ir/assets/files/basic-services-89626420b5f06e4d7a2dc9206cdeb192.json

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# سطح کاربری و کارمزد

Source: https://developers.wallex.ir/docs/basic-services-account-fee

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/fee`

## JSON field names in documented examples

`SHIBTMN`, `makerFeeRate`, `recent_days_sum`, `result`, `takerFeeRate`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# اضافه کردن شماره شبا بانکی

Source: https://developers.wallex.ir/docs/basic-services-add-iban

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/account/ibans`

## JSON field names in documented examples

`bank_details`, `bank_name`, `code`, `iban`, `id`, `is_available`, `is_default`, `label`, `message`, `owners`, `result`, `status`, `success`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# کندل ها (آمار OHLC بازارها)

Source: https://developers.wallex.ir/docs/basic-services-candles

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/udf/history`

## JSON field names in documented examples

`c`, `h`, `l`, `o`, `s`, `t`, `v`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت شماره های کارت بانکی

Source: https://developers.wallex.ir/docs/basic-services-card-numbers

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/card-numbers`

## JSON field names in documented examples

`bank_details`, `card_number`, `code`, `count`, `id`, `is_default`, `label`, `message`, `owners`, `page`, `per_page`, `result`, `result_info`, `status`, `success`, `total_count`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت آدرس کیف پول رمزارز

Source: https://developers.wallex.ir/docs/basic-services-coin-wallets

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/wallets/{symbol}`

## JSON field names in documented examples

`address`, `coin_type`, `deposit_availability`, `deposit_unavailability_reason`, `expire_at`, `id`, `key`, `memo`, `message`, `min_confirmation`, `min_deposit_value`, `min_withdrawal_value`, `name`, `name_en`, `network`, `result`, `success`, `transaction_fee`, `type`, `wallets`, `withdrawal_availability`, `withdrawal_unavailability_reason`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# عمق بازارها

Source: https://developers.wallex.ir/docs/basic-services-depth

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/depth`

## JSON field names in documented examples

`ask`, `bid`, `message`, `price`, `quantity`, `result`, `success`, `sum`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت شماره های شبای بانکی

Source: https://developers.wallex.ir/docs/basic-services-iban-numbers

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/ibans`

## JSON field names in documented examples

`bank_details`, `bank_name`, `code`, `count`, `iban`, `id`, `is_available`, `is_default`, `label`, `message`, `owners`, `page`, `per_page`, `result`, `result_info`, `status`, `success`, `total_count`, `withdraw_available_amount`, `withdraw_daily_amount`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# لیست معاملات انجام شده

Source: https://developers.wallex.ir/docs/basic-services-latest-trades

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/trades`

## JSON field names in documented examples

`isBuyOrder`, `latestTrades`, `message`, `price`, `quantity`, `result`, `success`, `sum`, `symbol`, `timestamp`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت موجودی کیف پول حساب اصلی

Source: https://developers.wallex.ir/docs/basic-services-main-wallet

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`asset`, `asset_png_icon`, `asset_svg_icon`, `balances`, `faName`, `fiat`, `is_digital_gold`, `is_dust`, `locked`, `message`, `result`, `success`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# مارکت های والکس

Source: https://developers.wallex.ir/docs/basic-services-markets

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /hector/web/v1/markets`

## JSON field names in documented examples

`amount_precision`, `base_asset`, `categories`, `change_24h`, `change_7D`, `created_at`, `en_base_asset`, `en_quote_asset`, `fa_base_asset`, `fa_quote_asset`, `flags`, `is_margin`, `is_new`, `is_otc`, `is_spot`, `is_tmn_based`, `is_usdt_based`, `is_zero_fee`, `leverage_step`, `markets`, `max_leverage`, `message`, `otc_is_new`, `price`, `price_precision`, `quote_asset`, `quote_volume_24h`, `result`, `spot_is_new`, `success`, `symbol`, `volume_24h`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# ثبت درخواست برداشت تومان

Source: https://developers.wallex.ir/docs/basic-services-withdraw-toman

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/account/money-withdrawal`

## JSON field names in documented examples

`amount`, `bank_details`, `bank_name`, `code`, `created_at`, `details`, `fee`, `iban`, `id`, `is_available`, `is_default`, `label`, `message`, `owners`, `result`, `status`, `success`, `tracking_code`, `value`, `withdraw_available_amount`, `withdraw_daily_amount`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# ساخت API-Key

Source: https://developers.wallex.ir/docs/create-api-key

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Activate User Package

Source: https://developers.wallex.ir/docs/generated/activate-user-package

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/prop/user/packages`

## JSON field names in documented examples

`clientId`, `createdAt`, `darkAvatarUrl`, `isActive`, `isSuspend`, `lightAvatarUrl`, `message`, `result`, `success`, `title`, `type`, `userId`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Active Sub Accounts List

Source: https://developers.wallex.ir/docs/generated/active-sub-accounts-list

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /sub-accounts`

## JSON field names in documented examples

`clientId`, `count`, `createdAt`, `darkAvatarUrl`, `isActive`, `isSuspend`, `lightAvatarUrl`, `message`, `page`, `per_page`, `result`, `result_info`, `success`, `title`, `total_count`, `type`, `userId`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Active User Package Details

Source: https://developers.wallex.ir/docs/generated/active-user-package-details

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/user/packages/active`

## Header names appearing in this page

`Sub-Account-Client-id`

## JSON field names in documented examples

`BTC`, `TMN`, `USDT`, `alertsData`, `assurance`, `balancesHistory`, `connectToWallet`, `createdAt`, `currency`, `cyclesCount`, `dailyFee`, `dailyFeeAfterDiscount`, `dailyFeeDiscount`, `darkImageUrl`, `debtCyclesCount`, `destination_currency`, `expireAt`, `expireDays`, `finalFee`, `finalFeeAfterDiscount`, `finalPayableFeeAmount`, `finalPayback`, `id`, `lightImageUrl`, `liquidityLimit`, `loan`, `message`, `openDays`, `packageDetail`, `paidCyclesCount`, `perDay`, `profit`, `profitPercentage`, `result`, `startBalance`, `status`, `success`, `title`, `total`, `totalDays`, `type`, `userPackageDetail`, `warningLimit`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Active User Packages Overview

Source: https://developers.wallex.ir/docs/generated/active-user-packages-overview

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/user/packages/overview`

## JSON field names in documented examples

`BTC`, `TMN`, `USDT`, `aggregatedDetail`, `assurance`, `balancesHistory`, `createdAt`, `currency`, `darkImageUrl`, `expireAt`, `expireDays`, `id`, `lightImageUrl`, `loan`, `message`, `packageDetail`, `perDay`, `profit`, `profitPercentage`, `result`, `status`, `subAccountClientId`, `success`, `title`, `total`, `userPackageDetail`, `userPackages`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# افزودن شماره شبا جدید به حساب

Source: https://developers.wallex.ir/docs/generated/add-account-iban

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/account/ibans`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# calculate min, max Collateral and loan

Source: https://developers.wallex.ir/docs/generated/calculate-loan

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /margin-trade/v1/public/loan`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Cancel User Package

Source: https://developers.wallex.ir/docs/generated/cancel-user-package

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `DELETE /v1/prop/user/packages`

## Header names appearing in this page

`Sub-Account-Client-id`

## JSON field names in documented examples

`client_id`, `currency`, `final_balance`, `final_balance_without_transfers`, `message`, `prop_package_id`, `result`, `start_balance`, `success`, `user_id`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Get historical market data (candles)

Source: https://developers.wallex.ir/docs/generated/candle-history

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/udf/history`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Check Prop Package Availability

Source: https://developers.wallex.ir/docs/generated/check-prop-package-availability

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/user/packages/:id/check-availability`
- `GET /v1/prop/user/packages/{id}/check-availability`

## JSON field names in documented examples

`isValid`, `key`, `message`, `result`, `success`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Close a margin position

Source: https://developers.wallex.ir/docs/generated/close-position-id

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `PATCH /margin-trade/v1/positions/:id/close`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# درخواست برداشت وجه از حساب

Source: https://developers.wallex.ir/docs/generated/create-money-withdrawal

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/account/money-withdrawal`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Create Transfer To Sub Account

Source: https://developers.wallex.ir/docs/generated/create-transfer-to-sub-account

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /sub-accounts/transfers`

## JSON field names in documented examples

`clientId`, `code`, `createdAt`, `currency`, `darkAvatarUrl`, `isActive`, `isSuspend`, `lightAvatarUrl`, `message`, `result`, `success`, `title`, `type`, `userId`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Cancel an existing order

Source: https://developers.wallex.ir/docs/generated/delete-account-orders

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `DELETE /v1/account/orders`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/delete-account-orders](pages/generated__delete-account-orders.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/get-depth](pages/generated__get-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-open-order](pages/generated__get-open-order.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-orders-client](pages/generated__get-orders-client.md)
- [/generated/post-account-orders](pages/generated__post-account-orders.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Cancel an order by path parameter

Source: https://developers.wallex.ir/docs/generated/delete-orders-client

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `DELETE /v1/account/orders/:client_id`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/delete-account-orders](pages/generated__delete-account-orders.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/get-depth](pages/generated__get-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-open-order](pages/generated__get-open-order.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-orders-client](pages/generated__get-orders-client.md)
- [/generated/post-account-orders](pages/generated__post-account-orders.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# info a margin position before creation

Source: https://developers.wallex.ir/docs/generated/detailed-information

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /margin-trade/v1/public/dry-run`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Disable Connect To Wallet

Source: https://developers.wallex.ir/docs/generated/disable-connect-to-wallet

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `DELETE /v1/prop/user/packages/connect-to-wallet`

## Header names appearing in this page

`Sub-Account-Client-id`

## JSON field names in documented examples

`message`, `result`, `success`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Update margin positions collateral

Source: https://developers.wallex.ir/docs/generated/edit-colateral

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `PATCH /margin-trade/v1/positions/:id/collateral`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Update stop-loss and take-profit prices

Source: https://developers.wallex.ir/docs/generated/edit-sltp

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `PATCH /margin-trade/v1/positions/:id/sltp`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Enable Connect To Wallet

Source: https://developers.wallex.ir/docs/generated/enable-connect-to-wallet

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/prop/user/packages/connect-to-wallet`

## Header names appearing in this page

`Sub-Account-Client-id`

## JSON field names in documented examples

`credit`, `currency`, `message`, `result`, `status`, `success`, `usageCount`, `usedCount`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Enable User Package Renew

Source: https://developers.wallex.ir/docs/generated/enable-user-package-renew

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/prop/user/packages/enable-renew`

## Header names appearing in this page

`Sub-Account-Client-id`

## JSON field names in documented examples

`message`, `result`, `success`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Get account balances

Source: https://developers.wallex.ir/docs/generated/get-account-balances

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/balances`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت شماره کارت‌های بانکی حساب

Source: https://developers.wallex.ir/docs/generated/get-account-card-numbers

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/card-numbers`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت کارمزدهای حساب

Source: https://developers.wallex.ir/docs/generated/get-account-fees

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/fee`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت لیست شماره شباهای حساب

Source: https://developers.wallex.ir/docs/generated/get-account-ibans

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/ibans`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت آدرس کیف‌پول کاربر برای نماد مشخص

Source: https://developers.wallex.ir/docs/generated/get-account-wallet-by-symbol

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/wallets/:symbol`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Get all markets depth

Source: https://developers.wallex.ir/docs/generated/get-depth

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /depth/all`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/delete-account-orders](pages/generated__delete-account-orders.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/get-depth](pages/generated__get-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-open-order](pages/generated__get-open-order.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-orders-client](pages/generated__get-orders-client.md)
- [/generated/post-account-orders](pages/generated__post-account-orders.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت معاملات اخیر

Source: https://developers.wallex.ir/docs/generated/get-latest-trades

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/trades`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# margin trade user levels

Source: https://developers.wallex.ir/docs/generated/get-levels

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/user/levels`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# margin trade user levels

Source: https://developers.wallex.ir/docs/generated/get-levels-market

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/user/levels/:market`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت عمق بازار

Source: https://developers.wallex.ir/docs/generated/get-market-depth

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/depth`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Get all markets

Source: https://developers.wallex.ir/docs/generated/get-markets

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /hector/web/v1/markets`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/basic-services-account-fee](pages/basic-services-account-fee.md)
- [/basic-services-add-iban](pages/basic-services-add-iban.md)
- [/basic-services-candles](pages/basic-services-candles.md)
- [/basic-services-card-numbers](pages/basic-services-card-numbers.md)
- [/basic-services-coin-wallets](pages/basic-services-coin-wallets.md)
- [/basic-services-depth](pages/basic-services-depth.md)
- [/basic-services-iban-numbers](pages/basic-services-iban-numbers.md)
- [/basic-services-latest-trades](pages/basic-services-latest-trades.md)
- [/basic-services-main-wallet](pages/basic-services-main-wallet.md)
- [/basic-services-markets](pages/basic-services-markets.md)
- [/basic-services-withdraw-toman](pages/basic-services-withdraw-toman.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/add-account-iban](pages/generated__add-account-iban.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/create-money-withdrawal](pages/generated__create-money-withdrawal.md)
- [/generated/delete-account-orders](pages/generated__delete-account-orders.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-account-balances](pages/generated__get-account-balances.md)
- [/generated/get-account-card-numbers](pages/generated__get-account-card-numbers.md)
- [/generated/get-account-fees](pages/generated__get-account-fees.md)
- [/generated/get-account-ibans](pages/generated__get-account-ibans.md)
- [/generated/get-account-wallet-by-symbol](pages/generated__get-account-wallet-by-symbol.md)
- [/generated/get-depth](pages/generated__get-depth.md)
- [/generated/get-latest-trades](pages/generated__get-latest-trades.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-market-depth](pages/generated__get-market-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-open-order](pages/generated__get-open-order.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-orders-client](pages/generated__get-orders-client.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/post-account-orders](pages/generated__post-account-orders.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# List active orders

Source: https://developers.wallex.ir/docs/generated/get-open-order

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/openOrders`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/delete-account-orders](pages/generated__delete-account-orders.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/get-depth](pages/generated__get-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-open-order](pages/generated__get-open-order.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-orders-client](pages/generated__get-orders-client.md)
- [/generated/post-account-orders](pages/generated__post-account-orders.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# List margin orders

Source: https://developers.wallex.ir/docs/generated/get-orders

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/orders`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/delete-account-orders](pages/generated__delete-account-orders.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-depth](pages/generated__get-depth.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-open-order](pages/generated__get-open-order.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-orders-client](pages/generated__get-orders-client.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/post-account-orders](pages/generated__post-account-orders.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Get order details

Source: https://developers.wallex.ir/docs/generated/get-orders-client

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/orders/:client_id`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/delete-account-orders](pages/generated__delete-account-orders.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/get-depth](pages/generated__get-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-open-order](pages/generated__get-open-order.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-orders-client](pages/generated__get-orders-client.md)
- [/generated/post-account-orders](pages/generated__post-account-orders.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# get otc markets

Source: https://developers.wallex.ir/docs/generated/get-otc-markets

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/otc/markets`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-otc-markets](pages/generated__get-otc-markets.md)
- [/generated/get-otc-price](pages/generated__get-otc-price.md)
- [/generated/place-easy-trade-order](pages/generated__place-easy-trade-order.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-create-order](pages/otc-create-order.md)
- [/otc-intro](pages/otc-intro.md)
- [/otc-markets](pages/otc-markets.md)
- [/otc-price](pages/otc-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# get otc price

Source: https://developers.wallex.ir/docs/generated/get-otc-price

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/otc/price`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-otc-markets](pages/generated__get-otc-markets.md)
- [/generated/get-otc-price](pages/generated__get-otc-price.md)
- [/generated/place-easy-trade-order](pages/generated__place-easy-trade-order.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-create-order](pages/otc-create-order.md)
- [/otc-intro](pages/otc-intro.md)
- [/otc-markets](pages/otc-markets.md)
- [/otc-price](pages/otc-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# User PNL

Source: https://developers.wallex.ir/docs/generated/get-pnl

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/user/pnl`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Get a margin position

Source: https://developers.wallex.ir/docs/generated/get-position-id

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/positions/:id`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# List margin positions

Source: https://developers.wallex.ir/docs/generated/get-positions

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/positions`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Open a margin position

Source: https://developers.wallex.ir/docs/generated/open-position

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /margin-trade/v1/positions`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# create otc trade

Source: https://developers.wallex.ir/docs/generated/place-easy-trade-order

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/account/easy-trade/orders`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-otc-markets](pages/generated__get-otc-markets.md)
- [/generated/get-otc-price](pages/generated__get-otc-price.md)
- [/generated/place-easy-trade-order](pages/generated__place-easy-trade-order.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-create-order](pages/otc-create-order.md)
- [/otc-intro](pages/otc-intro.md)
- [/otc-markets](pages/otc-markets.md)
- [/otc-price](pages/otc-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Submit a new trading order

Source: https://developers.wallex.ir/docs/generated/post-account-orders

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/account/orders`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/delete-account-orders](pages/generated__delete-account-orders.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/get-depth](pages/generated__get-depth.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-open-order](pages/generated__get-open-order.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-orders-client](pages/generated__get-orders-client.md)
- [/generated/post-account-orders](pages/generated__post-account-orders.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Calculate

Source: https://developers.wallex.ir/docs/generated/profit-position-id

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /margin-trade/v1/positions/:id/profit`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Prop Package Details

Source: https://developers.wallex.ir/docs/generated/prop-package-details

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/packages/:id`

## JSON field names in documented examples

`assurance`, `currency`, `daily_fee`, `daily_fee_after_discount`, `daily_fee_discount`, `dark_image_url`, `destination_currency`, `detail`, `expire_days`, `faq`, `final_fee`, `final_fee_after_discount`, `final_fee_discount`, `id`, `light_image_url`, `liquidity_limit`, `loan`, `message`, `result`, `status`, `success`, `title`, `unavailableMarkets`, `warning_limit`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Prop Packages List

Source: https://developers.wallex.ir/docs/generated/prop-packages-list

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/packages`

## JSON field names in documented examples

`assurance`, `currency`, `daily_fee`, `daily_fee_after_discount`, `daily_fee_discount`, `dark_image_url`, `destination_currency`, `expire_days`, `final_fee`, `final_fee_after_discount`, `final_fee_discount`, `id`, `light_image_url`, `liquidity_limit`, `loan`, `message`, `result`, `status`, `success`, `title`, `warning_limit`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Positions Ratio of long and short

Source: https://developers.wallex.ir/docs/generated/public-ratio

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/public/ratio/:market`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/calculate-loan](pages/generated__calculate-loan.md)
- [/generated/close-position-id](pages/generated__close-position-id.md)
- [/generated/detailed-information](pages/generated__detailed-information.md)
- [/generated/edit-colateral](pages/generated__edit-colateral.md)
- [/generated/edit-sltp](pages/generated__edit-sltp.md)
- [/generated/get-levels](pages/generated__get-levels.md)
- [/generated/get-levels-market](pages/generated__get-levels-market.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/generated/get-position-id](pages/generated__get-position-id.md)
- [/generated/get-positions](pages/generated__get-positions.md)
- [/generated/open-position](pages/generated__open-position.md)
- [/generated/profit-position-id](pages/generated__profit-position-id.md)
- [/generated/public-ratio](pages/generated__public-ratio.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# Spot

Source: https://developers.wallex.ir/docs/generated/spot

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Header names appearing in this page

`x-api-key`

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/generated/spot](pages/generated__spot.md)

---

# Sub Account Balances Details

Source: https://developers.wallex.ir/docs/generated/sub-account-balances-details

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/balances-detail`

## JSON field names in documented examples

`BTC`, `TMN`, `USDT`, `available`, `baseMarketName`, `changePercentage`, `estimatedValue`, `freeze`, `last24HoursEstimatedValueChange`, `message`, `result`, `stats`, `success`, `symbol`, `total`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# List Sub Account Transfers

Source: https://developers.wallex.ir/docs/generated/sub-account-transfer

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /sub-accounts/transfers`

## JSON field names in documented examples

`count`, `createdAt`, `currency`, `destination_client_id`, `destination_client_title`, `destination_user_type`, `fa_destination_user_type`, `fa_source_user_type`, `message`, `page`, `per_page`, `reason`, `result`, `result_info`, `source_client_id`, `source_client_title`, `source_user_type`, `success`, `total_count`, `unique_id`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# trade-credit

Source: https://developers.wallex.ir/docs/generated/trade-credit

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Header names appearing in this page

`x-api-key`

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/generated/trade-credit](pages/generated__trade-credit.md)

---

# User Package History Details

Source: https://developers.wallex.ir/docs/generated/user-package-history-details

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/user/packages/history/:subAccountClientId`
- `GET /v1/prop/user/packages/history/{subAccountClientId}`

## JSON field names in documented examples

`applicable_daily_fee`, `applicable_daily_fee_after_discount`, `applicable_daily_fee_discount`, `assurance`, `client_id`, `close_reason`, `created_at`, `currency`, `daily_fee`, `daily_fee_after_discount`, `daily_fee_discount`, `dark_image_url`, `destination_currency`, `expire_at`, `expire_days`, `final_assurance`, `final_balance`, `final_balance_without_transfers`, `final_fee`, `final_fee_after_discount`, `final_fee_discount`, `final_payBack`, `finished_at`, `light_image_url`, `liquidity_limit`, `loan`, `message`, `open_days`, `package_title`, `profit`, `profit_percentage`, `result`, `start_balance`, `status`, `success`, `total_days`, `user_id`, `warning_limit`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# User Package History List

Source: https://developers.wallex.ir/docs/generated/user-package-history-list

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/user/packages/history`

## JSON field names in documented examples

`count`, `createdAt`, `currency`, `destination_client_id`, `destination_client_title`, `destination_user_type`, `fa_destination_user_type`, `fa_source_user_type`, `message`, `page`, `per_page`, `reason`, `result`, `result_info`, `source_client_id`, `source_client_title`, `source_user_type`, `success`, `total_count`, `unique_id`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/activate-user-package](pages/generated__activate-user-package.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/active-user-package-details](pages/generated__active-user-package-details.md)
- [/generated/active-user-packages-overview](pages/generated__active-user-packages-overview.md)
- [/generated/cancel-user-package](pages/generated__cancel-user-package.md)
- [/generated/check-prop-package-availability](pages/generated__check-prop-package-availability.md)
- [/generated/create-transfer-to-sub-account](pages/generated__create-transfer-to-sub-account.md)
- [/generated/disable-connect-to-wallet](pages/generated__disable-connect-to-wallet.md)
- [/generated/enable-connect-to-wallet](pages/generated__enable-connect-to-wallet.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/prop-package-details](pages/generated__prop-package-details.md)
- [/generated/prop-packages-list](pages/generated__prop-packages-list.md)
- [/generated/sub-account-balances-details](pages/generated__sub-account-balances-details.md)
- [/generated/sub-account-transfer](pages/generated__sub-account-transfer.md)
- [/generated/user-package-history-details](pages/generated__user-package-history-details.md)
- [/generated/user-package-history-list](pages/generated__user-package-history-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# Wallex Margin-trade API

Source: https://developers.wallex.ir/docs/generated/wallex-margin-trade-api

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Header names appearing in this page

`x-api-key`

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/generated/wallex-margin-trade-api](pages/generated__wallex-margin-trade-api.md)

---

# مارکت های فعال

Source: https://developers.wallex.ir/docs/margin-active-markets

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/public/markets`

## JSON field names in documented examples

`base`, `liquidity_margin`, `max_age`, `max_risk_coef`, `min_risk_coef`, `quote`, `risk_coef_step`, `symbol`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# محاسبه میزان حداقل و حداکثر وثیقه

Source: https://developers.wallex.ir/docs/margin-calculate-loan

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /margin-trade/v1/public/loan`

## JSON field names in documented examples

`collateral`, `currency`, `loan`, `max`, `min`, `result`, `success`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# بستن موقعیت تعهدی

Source: https://developers.wallex.ir/docs/margin-close-position

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `PATCH /margin-trade/v1/positions/{id}/close`

## JSON field names in documented examples

`call_price`, `close_filled_price`, `close_price`, `close_reason`, `closed_at`, `collateral`, `created_at`, `currency`, `expires_at`, `extend_time`, `first_order_filled`, `id`, `interest`, `is_called`, `liquidity_price`, `loan`, `market`, `max_age`, `open_filled_price`, `open_price`, `opened_at`, `profit`, `profit_percentage`, `result`, `risk_coef`, `side`, `state`, `stop_loss`, `success`, `take_profit`, `updated_at`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# مشاهده اطلاعات موقعیت مارجین قبل از ایجاد

Source: https://developers.wallex.ir/docs/margin-dry-run

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /margin-trade/v1/public/dry-run`

## JSON field names in documented examples

`call_price`, `collateral`, `currency`, `extend_fee`, `extend_time`, `liquidity_price`, `loan`, `market`, `max_age`, `open_fee`, `open_price`, `risk_coef`, `side`, `stop_loss`, `success`, `take_profit`, `trade_fee`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# ویرایش وثیقه موقعیت تعهدی

Source: https://developers.wallex.ir/docs/margin-edit-collateral

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `PATCH /margin-trade/v1/positions/{id}/collateral`

## JSON field names in documented examples

`call_price`, `close_filled_price`, `close_price`, `close_reason`, `closed_at`, `collateral`, `created_at`, `currency`, `expires_at`, `extend_time`, `first_order_filled`, `id`, `interest`, `is_called`, `liquidity_price`, `loan`, `market`, `max_age`, `open_filled_price`, `open_price`, `opened_at`, `profit`, `profit_percentage`, `result`, `risk_coef`, `side`, `state`, `stop_loss`, `success`, `take_profit`, `updated_at`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت موقعیت‌های تعهدی

Source: https://developers.wallex.ir/docs/margin-get-positions

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /margin-trade/v1/positions`

## JSON field names in documented examples

`call_price`, `close_filled_price`, `close_price`, `close_reason`, `closed_at`, `collateral`, `created_at`, `currency`, `expires_at`, `extend_time`, `first_order_filled`, `id`, `interest`, `is_called`, `liquidity_price`, `loan`, `market`, `max_age`, `open_filled_price`, `open_price`, `opened_at`, `profit`, `profit_percentage`, `result`, `risk_coef`, `side`, `state`, `stop_loss`, `success`, `take_profit`, `updated_at`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# معامله تعهدی چیست ؟

Source: https://developers.wallex.ir/docs/margin-intro

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Official schema downloads

- https://developers.wallex.ir/assets/files/margin-c709e1f52cb44387a2e35ffd678c6dfa.json

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/delete-orders-client](pages/generated__delete-orders-client.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# ایجاد موقعیت مارجین

Source: https://developers.wallex.ir/docs/margin-open-position

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /margin-trade/v1/positions`

## JSON field names in documented examples

`call_price`, `close_reason`, `collateral`, `created_at`, `expires_at`, `extend_time`, `first_order_filled`, `id`, `interest`, `is_called`, `liquidity_price`, `loan`, `market`, `max_age`, `open_filled_price`, `open_price`, `opened_at`, `profit`, `result`, `risk_coef`, `side`, `state`, `success`, `updated_at`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# ویرایش حد سود و حد ضرر موقعیت تعهدی

Source: https://developers.wallex.ir/docs/margin-sltp-edit

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `PATCH /margin-trade/v1/positions/{id}/sltp`

## JSON field names in documented examples

`call_price`, `close_filled_price`, `close_price`, `close_reason`, `closed_at`, `collateral`, `created_at`, `currency`, `expires_at`, `extend_time`, `first_order_filled`, `id`, `interest`, `is_called`, `liquidity_price`, `loan`, `market`, `max_age`, `open_filled_price`, `open_price`, `opened_at`, `profit`, `profit_percentage`, `result`, `risk_coef`, `side`, `state`, `stop_loss`, `success`, `take_profit`, `updated_at`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# اصطلاحات معامله تعهدی

Source: https://developers.wallex.ir/docs/margin-types

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-orders](pages/generated__get-orders.md)
- [/margin-active-markets](pages/margin-active-markets.md)
- [/margin-calculate-loan](pages/margin-calculate-loan.md)
- [/margin-close-position](pages/margin-close-position.md)
- [/margin-dry-run](pages/margin-dry-run.md)
- [/margin-edit-collateral](pages/margin-edit-collateral.md)
- [/margin-get-positions](pages/margin-get-positions.md)
- [/margin-intro](pages/margin-intro.md)
- [/margin-open-position](pages/margin-open-position.md)
- [/margin-sltp-edit](pages/margin-sltp-edit.md)
- [/margin-types](pages/margin-types.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# ثبت سفارش در بازار آنی

Source: https://developers.wallex.ir/docs/otc-create-order

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/account/easy-trade/orders`

## JSON field names in documented examples

`active`, `clientOrderId`, `destinationMarket`, `executedPercent`, `executedPrice`, `executedQty`, `executedSum`, `fee`, `feeAsset`, `feeCoefficient`, `fills`, `isBuyer`, `makerFeeCoefficient`, `origQty`, `price`, `quantity`, `side`, `sourceMarket`, `status`, `sum`, `symbol`, `takerFeeCoefficient`, `timestamp`, `transactTime`, `type`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-otc-markets](pages/generated__get-otc-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-create-order](pages/otc-create-order.md)
- [/otc-intro](pages/otc-intro.md)
- [/otc-markets](pages/otc-markets.md)
- [/otc-price](pages/otc-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# خرید و فروش در بازار معاملاتی آنی چیست ؟

Source: https://developers.wallex.ir/docs/otc-intro

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Official schema downloads

- https://developers.wallex.ir/assets/files/otc-8e321a32f4509cbf103b3127bf7c9918.json

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/enable-user-package-renew](pages/generated__enable-user-package-renew.md)
- [/generated/get-otc-markets](pages/generated__get-otc-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-create-order](pages/otc-create-order.md)
- [/otc-intro](pages/otc-intro.md)
- [/otc-markets](pages/otc-markets.md)
- [/otc-price](pages/otc-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# مارکت های فعال

Source: https://developers.wallex.ir/docs/otc-markets

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/otc/markets`

## JSON field names in documented examples

`USDTTMN`, `baseAsset`, `buyStatus`, `enName`, `exchangeStatus`, `faName`, `lastPrice`, `maxNotional`, `message`, `minNotional`, `minQty`, `quoteAsset`, `result`, `sellStatus`, `stats`, `success`, `symbol`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-otc-markets](pages/generated__get-otc-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-create-order](pages/otc-create-order.md)
- [/otc-intro](pages/otc-intro.md)
- [/otc-markets](pages/otc-markets.md)
- [/otc-price](pages/otc-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت قیمت ها در بازار آنی

Source: https://developers.wallex.ir/docs/otc-price

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/otc/price`

## JSON field names in documented examples

`current_time`, `message`, `price`, `price_expires_at`, `result`, `success`, `ttl`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-otc-markets](pages/generated__get-otc-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-create-order](pages/otc-create-order.md)
- [/otc-intro](pages/otc-intro.md)
- [/otc-markets](pages/otc-markets.md)
- [/otc-price](pages/otc-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت قیمت لحظه‌ای همه بازارها

Source: https://developers.wallex.ir/docs/socket-all-price

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`channel`, `data`, `id`, `price`, `pub`, `push`, `subscribe`, `symbol`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/connection/websocket`
- `wss://api.wallex.ir/ws`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت عمق بازار خرید (buyDepth)

Source: https://developers.wallex.ir/docs/socket-buy-depth

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`channel`, `data`, `id`, `price`, `pub`, `push`, `quantity`, `subscribe`, `sum`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/connection/websocket`
- `wss://api.wallex.ir/ws`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت به‌روزرسانی کندل‌های نمودار

Source: https://developers.wallex.ir/docs/socket-candle

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/udf/history`

## JSON field names in documented examples

`c`, `channel`, `data`, `h`, `l`, `o`, `offset`, `pub`, `push`, `s`, `t`, `v`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/connection/websocket`
- `wss://api.wallex.ir/ws`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# اتصال و عضویت

Source: https://developers.wallex.ir/docs/socket-connection

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Documented protocol addresses (not called)

- `https://api.wallex.ir/v3/auth/token/refresh`
- `wss://api.wallex.ir/connection/websocket`

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت قیمت منصفانه

Source: https://developers.wallex.ir/docs/socket-fair-price

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/all-fairPrice`

## JSON field names in documented examples

`BTCTMN`, `ETHTMN`, `USDTTMN`, `channel`, `data`, `id`, `prices`, `pub`, `push`, `subscribe`, `ts`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/connection/websocket`
- `wss://api.wallex.ir/ws`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# مقدمه

Source: https://developers.wallex.ir/docs/socket-intro

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`channel`, `error`, `id`, `maxPayload`, `pingInterval`, `pingTimeout`, `sid`, `subscribe`, `upgrades`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/connection/websocket`
- `wss://api.wallex.ir/ws`
- `wss://api.wallex.ir/ws،`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/place-easy-trade-order](pages/generated__place-easy-trade-order.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# راهنمای مهاجرت

Source: https://developers.wallex.ir/docs/socket-migration

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`channel`, `data`, `id`, `isBuyOrder`, `price`, `pub`, `push`, `quantity`, `subscribe`, `timestamp`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/wswss://api.wallex.ir/connection/websocket`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# رویدادهای خصوصی کاربران

Source: https://developers.wallex.ir/docs/socket-private-channel

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`TMN`, `active`, `asset`, `balanceUpdated`, `channel`, `client`, `clientOrderID`, `clientOrderId`, `connect`, `data`, `event`, `executedQty`, `expires`, `faName`, `feeAmount`, `feeCurrency`, `id`, `isMaker`, `locked`, `orderRemoved`, `orderSaved`, `origQty`, `price`, `pub`, `push`, `quantity`, `side`, `status`, `subs`, `sum`, `symbol`, `timestamp`, `token`, `tradeDetails`, `ttl`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `https://api.wallex.ir/v3/auth/token/refresh`
- `wss://api.wallex.ir/connection/websocket`
- `wss://api.wallex.ir/ws`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# اتصال بدون SDK

Source: https://developers.wallex.ir/docs/socket-raw-protocol

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`channel`, `client`, `code`, `connect`, `data`, `error`, `expires`, `id`, `isBuyOrder`, `message`, `ping`, `pong`, `price`, `pub`, `push`, `quantity`, `subs`, `subscribe`, `timestamp`, `token`, `ttl`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/connection/websocket`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت عمق بازار فروش (sellDepth)

Source: https://developers.wallex.ir/docs/socket-sell-depth

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`channel`, `data`, `id`, `price`, `pub`, `push`, `quantity`, `subscribe`, `sum`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/connection/websocket`
- `wss://api.wallex.ir/ws`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# توکن اتصال خصوصی

Source: https://developers.wallex.ir/docs/socket-token

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v3/auth/token/refresh`

## JSON field names in documented examples

`client`, `connect`, `expires`, `expires_in`, `id`, `message`, `ping`, `pong`, `result`, `subs`, `success`, `token`, `token_type`, `ttl`, `ws_access_token`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `https://api.wallex.ir/v3/auth/token/refresh`
- `wss://api.wallex.ir/connection/websocket`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت معاملات انجام‌شده

Source: https://developers.wallex.ir/docs/socket-trade

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`channel`, `data`, `id`, `isBuyOrder`, `price`, `pub`, `push`, `quantity`, `subscribe`, `timestamp`

Field presence in an example does not establish requiredness, type, or nesting.

## Documented protocol addresses (not called)

- `wss://api.wallex.ir/connection/websocket`
- `wss://api.wallex.ir/ws`

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-all-price](pages/socket-all-price.md)
- [/socket-buy-depth](pages/socket-buy-depth.md)
- [/socket-candle](pages/socket-candle.md)
- [/socket-connection](pages/socket-connection.md)
- [/socket-fair-price](pages/socket-fair-price.md)
- [/socket-intro](pages/socket-intro.md)
- [/socket-migration](pages/socket-migration.md)
- [/socket-private-channel](pages/socket-private-channel.md)
- [/socket-raw-protocol](pages/socket-raw-protocol.md)
- [/socket-sell-depth](pages/socket-sell-depth.md)
- [/socket-token](pages/socket-token.md)
- [/socket-trade](pages/socket-trade.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# مارکت های فعال

Source: https://developers.wallex.ir/docs/spot-active-markets

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /hector/web/v1/markets`

## JSON field names in documented examples

`amount_precision`, `base_asset`, `categories`, `change_24h`, `change_7D`, `created_at`, `en_base_asset`, `en_quote_asset`, `fa_base_asset`, `fa_quote_asset`, `flags`, `is_margin`, `is_new`, `is_otc`, `is_spot`, `is_tmn_based`, `is_usdt_based`, `is_zero_fee`, `leverage_step`, `markets`, `max_leverage`, `message`, `otc_is_new`, `price`, `price_precision`, `quote_asset`, `quote_volume_24h`, `result`, `spot_is_new`, `success`, `symbol`, `volume_24h`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# لیست سفارشات فعال

Source: https://developers.wallex.ir/docs/spot-active-orders

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/openOrders`

## JSON field names in documented examples

`active`, `additionalProp1`, `additionalProp2`, `additionalProp3`, `clientOrderId`, `created_at`, `executedPercent`, `executedPrice`, `executedQty`, `executedSum`, `fee`, `feeAsset`, `feeCoefficient`, `fills`, `isBuyer`, `makerFeeCoefficient`, `message`, `origQty`, `price`, `quantity`, `result`, `result_info`, `side`, `status`, `stopPrice`, `stopPriceCondition`, `success`, `sum`, `symbol`, `takerFeeCoefficient`, `timestamp`, `transactTime`, `type`, `updated_at`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# لغو سفارش

Source: https://developers.wallex.ir/docs/spot-cancel-order

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `DELETE /v1/account/orders/{client_id}`

## JSON field names in documented examples

`active`, `clientOrderId`, `created_at`, `executedPercent`, `executedPrice`, `executedQty`, `executedSum`, `fee`, `feeAsset`, `feeCoefficient`, `fills`, `isBuyer`, `makerFeeCoefficient`, `message`, `origQty`, `price`, `quantity`, `result`, `side`, `status`, `stopPrice`, `stopPriceCondition`, `success`, `sum`, `symbol`, `takerFeeCoefficient`, `timestamp`, `transactTime`, `type`, `updated_at`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# ثبت سفارش

Source: https://developers.wallex.ir/docs/spot-create-order

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/account/orders`

## JSON field names in documented examples

`active`, `clientOrderId`, `created_at`, `executedPercent`, `executedPrice`, `executedQty`, `executedSum`, `fee`, `feeAsset`, `feeCoefficient`, `fills`, `isBuyer`, `makerFeeCoefficient`, `message`, `origQty`, `price`, `quantity`, `result`, `side`, `status`, `stopPrice`, `stopPriceCondition`, `success`, `sum`, `symbol`, `takerFeeCoefficient`, `timestamp`, `transactTime`, `type`, `updated_at`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# معامله اسپات چیست؟

Source: https://developers.wallex.ir/docs/spot-intro

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Header names appearing in this page

`sub-account-client-id`

## JSON field names in documented examples

`sub-account-client-id`

Field presence in an example does not establish requiredness, type, or nesting.

## Official schema downloads

- https://developers.wallex.ir/assets/files/spot-b9d06896d1009adc9ebc69b9a5495e7e.json

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/candle-history](pages/generated__candle-history.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت لیست سفارش‌ها

Source: https://developers.wallex.ir/docs/spot-order-list

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/orders`

## JSON field names in documented examples

`active`, `additionalProp1`, `additionalProp2`, `additionalProp3`, `clientOrderId`, `created_at`, `executedPercent`, `executedPrice`, `executedQty`, `executedSum`, `fee`, `feeAsset`, `feeCoefficient`, `fills`, `isBuyer`, `makerFeeCoefficient`, `message`, `origQty`, `price`, `quantity`, `result`, `result_info`, `side`, `status`, `stopPrice`, `stopPriceCondition`, `success`, `sum`, `symbol`, `takerFeeCoefficient`, `timestamp`, `transactTime`, `type`, `updated_at`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# دریافت جزئیات سفارش

Source: https://developers.wallex.ir/docs/spot-single-order-detail

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/account/orders/{client_id}`

## JSON field names in documented examples

`active`, `clientOrderId`, `created_at`, `executedPercent`, `executedPrice`, `executedQty`, `executedSum`, `fee`, `feeAsset`, `feeCoefficient`, `fills`, `isBuyer`, `makerFeeCoefficient`, `message`, `origQty`, `price`, `quantity`, `result`, `side`, `stopPrice`, `stopPriceCondition`, `success`, `sum`, `symbol`, `takerFeeCoefficient`, `timestamp`, `transactTime`, `type`, `updated_at`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# انواع سفارش در معاملات اسپات

Source: https://developers.wallex.ir/docs/spot-types

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/get-markets](pages/generated__get-markets.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-active-markets](pages/spot-active-markets.md)
- [/spot-active-orders](pages/spot-active-orders.md)
- [/spot-cancel-order](pages/spot-cancel-order.md)
- [/spot-create-order](pages/spot-create-order.md)
- [/spot-intro](pages/spot-intro.md)
- [/spot-order-list](pages/spot-order-list.md)
- [/spot-single-order-detail](pages/spot-single-order-detail.md)
- [/spot-types](pages/spot-types.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)

---

# فعال کردن پکیج اعتبار معاملاتی

Source: https://developers.wallex.ir/docs/trade-credit-activate-sub-account

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/prop/user/packages`

## JSON field names in documented examples

`clientId`, `createdAt`, `darkAvatarUrl`, `isActive`, `isSuspend`, `lightAvatarUrl`, `message`, `result`, `success`, `title`, `type`, `userId`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# پکیج های فعال اعتبار معاملاتی والکس

Source: https://developers.wallex.ir/docs/trade-credit-active-packages

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/packages`

## JSON field names in documented examples

`assurance`, `currency`, `daily_fee`, `daily_fee_after_discount`, `daily_fee_discount`, `dark_image_url`, `destination_currency`, `expire_days`, `final_fee`, `final_fee_after_discount`, `final_fee_discount`, `id`, `light_image_url`, `liquidity_limit`, `loan`, `result`, `status`, `title`, `usage_count_step`, `warning_limit`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# لیست حساب های اعتبار معاملاتی

Source: https://developers.wallex.ir/docs/trade-credit-active-sub-account-list

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /sub-accounts`

## JSON field names in documented examples

`clientId`, `createdAt`, `darkAvatarUrl`, `isActive`, `isSuspend`, `lightAvatarUrl`, `result`, `title`, `type`, `userId`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# بستن اکانت اعتبار معاملاتی

Source: https://developers.wallex.ir/docs/trade-credit-close-sub-account

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `DELETE /v1/prop/user/packages`

## JSON field names in documented examples

`client_id`, `currency`, `final_balance`, `final_balance_without_transfers`, `prop_package_id`, `result`, `start_balance`, `user_id`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# بررسی شرایط کاربر برای دریافت اعتبار معاملاتی

Source: https://developers.wallex.ir/docs/trade-credit-condition-check

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/user/packages/{id}/check-availability`

## JSON field names in documented examples

`isValid`, `key`, `result`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# اتصال کیف پول اصلی به اکانت اعتبار معاملاتی

Source: https://developers.wallex.ir/docs/trade-credit-connect-wallet

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `POST /v1/prop/user/packages/connect-to-wallet`

## JSON field names in documented examples

`credit`, `currency`, `message`, `result`, `status`, `success`, `usageCount`, `usedCount`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# قطع اتصال کیف پول اصلی از اکانت اعتبار معاملاتی

Source: https://developers.wallex.ir/docs/trade-credit-disconnect-wallet

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `DELETE /v1/prop/user/packages/connect-to-wallet`

## JSON field names in documented examples

`message`, `result`, `success`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# اعتبار معاملاتی چیست؟

Source: https://developers.wallex.ir/docs/trade-credit-intro

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## Official schema downloads

- https://developers.wallex.ir/assets/files/trade-credit-ff5c60b5b97b77a5b2c2e4800f07729c.yaml

This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/generated/get-pnl](pages/generated__get-pnl.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# دریافت جزیيات پکیج و لیست بازارهای غیر فعال

Source: https://developers.wallex.ir/docs/trade-credit-package-details

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/packages/{id}`

## JSON field names in documented examples

`assurance`, `currency`, `daily_fee`, `daily_fee_after_discount`, `daily_fee_discount`, `dark_image_url`, `destination_currency`, `detail`, `expire_days`, `final_fee`, `final_fee_after_discount`, `final_fee_discount`, `id`, `light_image_url`, `liquidity_limit`, `loan`, `result`, `status`, `title`, `unavailableMarkets`, `usage_count_step`, `warning_limit`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# دریافت تاریخچه طرح های اعتبار معاملاتی

Source: https://developers.wallex.ir/docs/trade-credit-sub-account-history

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.

## Documented HTTP operations

- `GET /v1/prop/user/packages/history`

## JSON field names in documented examples

`applicable_daily_fee`, `applicable_daily_fee_after_discount`, `applicable_daily_fee_discount`, `assurance`, `client_id`, `close_reason`, `created_at`, `currency`, `daily_fee`, `daily_fee_after_discount`, `daily_fee_discount`, `dark_image_url`, `destination_currency`, `expire_at`, `expire_days`, `final_assurance`, `final_balance`, `final_balance_without_transfers`, `final_fee`, `final_fee_after_discount`, `final_fee_discount`, `final_payBack`, `finished_at`, `light_image_url`, `liquidity_limit`, `loan`, `open_days`, `package_title`, `profit`, `profit_percentage`, `result`, `start_balance`, `status`, `total_days`, `user_id`, `warning_limit`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# trade-credit-sub-account-transfer

Source: https://developers.wallex.ir/docs/trade-credit-sub-account-transfer

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/trade-credit-sub-account-transfer](pages/trade-credit-sub-account-transfer.md)

---

# اصطلاحات اعتبار معاملاتی

Source: https://developers.wallex.ir/docs/trade-credit-types

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


This conceptual page has no automatically extracted HTTP/JSON contract.
Consult the source for its narrative guidance; see key findings in the main reference.

## Internal documentation links

- [/](pages/index.md)
- [/basic-services](pages/basic-services.md)
- [/create-api-key](pages/create-api-key.md)
- [/generated/active-sub-accounts-list](pages/generated__active-sub-accounts-list.md)
- [/margin-intro](pages/margin-intro.md)
- [/otc-intro](pages/otc-intro.md)
- [/socket-intro](pages/socket-intro.md)
- [/spot-intro](pages/spot-intro.md)
- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-active-packages](pages/trade-credit-active-packages.md)
- [/trade-credit-active-sub-account-list](pages/trade-credit-active-sub-account-list.md)
- [/trade-credit-close-sub-account](pages/trade-credit-close-sub-account.md)
- [/trade-credit-condition-check](pages/trade-credit-condition-check.md)
- [/trade-credit-connect-wallet](pages/trade-credit-connect-wallet.md)
- [/trade-credit-disconnect-wallet](pages/trade-credit-disconnect-wallet.md)
- [/trade-credit-intro](pages/trade-credit-intro.md)
- [/trade-credit-package-details](pages/trade-credit-package-details.md)
- [/trade-credit-sub-account-history](pages/trade-credit-sub-account-history.md)
- [/trade-credit-types](pages/trade-credit-types.md)

---

# trade-credit-wallet

Source: https://developers.wallex.ir/docs/trade-credit-wallet

This is an extracted technical reference, not an executable API integration.
Descriptions and sample account values are not mirrored.


## JSON field names in documented examples

`TMN`, `USDT`, `aggregated`, `amount`, `assetWorth`, `assetWorthChangeAmount`, `assetWorthChangePercentage`, `assurance`, `available`, `balances`, `changeAmount`, `changePercentage`, `clientId`, `createdAt`, `currency`, `darkAvatarUrl`, `faName`, `lightAvatarUrl`, `loan`, `locked`, `overall`, `propDetail`, `result`, `subAccount`, `title`, `totalAssetWorth`, `value`

Field presence in an example does not establish requiredness, type, or nesting.

## Internal documentation links

- [/trade-credit-activate-sub-account](pages/trade-credit-activate-sub-account.md)
- [/trade-credit-wallet](pages/trade-credit-wallet.md)


---

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


---

# Official Swagger technical contracts

Source schemas were read in full. Narrative descriptions and sample payload values
are omitted; protocol fields, types, enums, required flags and references are retained.
These contracts are documentary evidence, not runtime verification or trading permission.

## basic-services-89626420b5f06e4d7a2dc9206cdeb192.json

Source: https://developers.wallex.ir/assets/files/basic-services-89626420b5f06e4d7a2dc9206cdeb192.json

[Technical schema](schemas/basic-services-89626420b5f06e4d7a2dc9206cdeb192.json)

### `GET /v1/account/wallets/{symbol}`

Operation ID: `getAccountWalletBySymbol`

- Parameter `symbol`; in=path; required=True; type=string
- Parameter `network`; in=query; required=False; type=string

Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/AccountWalletResponse`
- `result`: `$ref`; required=False
- `result` → `#/definitions/WalletResult`
- `result.coin_type`: `$ref`; required=False
- `result.coin_type` → `#/definitions/CoinType`
- `result.coin_type.key`: `string`; required=False
- `result.coin_type.name`: `string`; required=False
- `result.coin_type.name_en`: `string`; required=False
- `result.coin_type.type`: `string`; required=False
- `result.coin_type.deposit_availability`: `string`; required=False
- `result.coin_type.withdrawal_availability`: `string`; required=False
- `result.coin_type.deposit_unavailability_reason`: `['string', 'null']`; required=False
- `result.coin_type.withdrawal_unavailability_reason`: `['string', 'null']`; required=False
- `result.wallets`: `object`; required=False
- `message`: `string`; required=False
- `success`: `boolean`; required=False
- `provider`: `string`; required=False

### `POST /v1/account/ibans`

Operation ID: `addAccountIban`

- Parameter `body`; in=body; required=True; type=unspecified
- `$` → `#/definitions/AddIbanRequest`
- `iban`: `string`; required=True

Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/AddIbanResponse`
- `result`: `$ref`; required=False
- `result` → `#/definitions/IbanResponseItem`
- `result.id`: `integer`; required=False
- `result.withdraw_daily_amount`: `['number', 'null']`; required=False
- `result.withdraw_available_amount`: `['number', 'null']`; required=False
- `result.iban`: `string`; required=False
- `result.owners`: `array`; required=False
- `result.bank_name`: `string`; required=False
- `result.status`: `string`; required=False
- `result.is_default`: `integer`; required=False
- `result.bank_details`: `object`; required=False
- `result.bank_details.code`: `string`; required=False
- `result.bank_details.label`: `string`; required=False
- `result.bank_details.is_available`: `integer`; required=False
- `message`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/account/ibans`

Operation ID: `getAccountIbans`

- Parameter `per_page`; in=query; required=False; type=integer
- Parameter `page`; in=query; required=False; type=integer

Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/AccountIbansResponse`
- `result`: `array`; required=False
- `result[]` → `#/definitions/IbanItem`
- `result[].id`: `integer`; required=False
- `result[].withdraw_daily_amount`: `['number', 'null']`; required=False
- `result[].withdraw_available_amount`: `['number', 'null']`; required=False
- `result[].iban`: `string`; required=False
- `result[].owners`: `array`; required=False
- `result[].bank_name`: `string`; required=False
- `result[].status`: `string`; required=False
- `result[].is_default`: `integer`; required=False
- `result[].bank_details`: `object`; required=False
- `result[].bank_details.code`: `string`; required=False
- `result[].bank_details.label`: `string`; required=False
- `result[].bank_details.is_available`: `integer`; required=False
- `message`: `string`; required=False
- `success`: `boolean`; required=False
- `result_info`: `object`; required=False
- `result_info.page`: `integer`; required=False
- `result_info.per_page`: `integer`; required=False
- `result_info.count`: `integer`; required=False
- `result_info.total_count`: `integer`; required=False

### `POST /v1/account/money-withdrawal`

Operation ID: `createMoneyWithdrawal`

- Parameter `body`; in=body; required=True; type=unspecified
- `$` → `#/definitions/MoneyWithdrawalRequest`
- `iban`: `integer`; required=True
- `value`: `number`; required=True

Response status codes: `201`

Response `201` fields:

- `$` → `#/definitions/MoneyWithdrawalResponse`
- `result`: `$ref`; required=False
- `result` → `#/definitions/MoneyWithdrawalResult`
- `result.amount`: `number`; required=False
- `result.fee`: `number`; required=False
- `result.tracking_code`: `string`; required=False
- `result.created_at`: `string`; required=False
- `result.status`: `string`; required=False
- `result.iban`: `$ref`; required=False
- `result.iban` → `#/definitions/IbanInfo`
- `result.iban.id`: `integer`; required=False
- `result.iban.iban`: `string`; required=False
- `result.iban.owners`: `array`; required=False
- `result.iban.bank_name`: `string`; required=False
- `result.iban.status`: `string`; required=False
- `result.iban.is_default`: `integer`; required=False
- `result.iban.bank_details`: `object`; required=False
- `result.iban.bank_details.code`: `string`; required=False
- `result.iban.bank_details.label`: `string`; required=False
- `result.iban.bank_details.is_available`: `integer`; required=False
- `result.details`: `array`; required=False
- `result.details[]` → `#/definitions/WithdrawalDetail`
- `result.details[].value`: `number`; required=False
- `result.details[].status`: `string`; required=False
- `message`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/account/card-numbers`

Operation ID: `getAccountCardNumbers`


Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/AccountCardNumbersResponse`
- `result`: `array`; required=False
- `result[]` → `#/definitions/CardNumberItem`
- `result[].id`: `integer`; required=False
- `result[].card_number`: `string`; required=False
- `result[].owners`: `array`; required=False
- `result[].status`: `string`; required=False
- `result[].is_default`: `integer`; required=False
- `result[].bank_details`: `object`; required=False
- `result[].bank_details.code`: `string`; required=False
- `result[].bank_details.label`: `string`; required=False
- `message`: `string`; required=False
- `success`: `boolean`; required=False
- `result_info`: `object`; required=False
- `result_info.page`: `integer`; required=False
- `result_info.per_page`: `integer`; required=False
- `result_info.count`: `integer`; required=False
- `result_info.total_count`: `integer`; required=False

### `GET /v1/account/fee`

Operation ID: `getAccountFees`


Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/AccountFeeResponse`
- `success`: `boolean`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False

### `GET /v1/trades`

Operation ID: `getLatestTrades`

- Parameter `symbol`; in=query; required=True; type=string

Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/LatestTradesResponse`
- `result`: `object`; required=False
- `result.latestTrades`: `array`; required=False
- `result.latestTrades[]` → `#/definitions/TradeEntry`
- `result.latestTrades[].symbol`: `string`; required=False
- `result.latestTrades[].quantity`: `string`; required=False
- `result.latestTrades[].price`: `string`; required=False
- `result.latestTrades[].sum`: `string`; required=False
- `result.latestTrades[].isBuyOrder`: `boolean`; required=False
- `result.latestTrades[].timestamp`: `string`; required=False
- `message`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /hector/web/v1/markets`

Operation ID: `getMarkets`


Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/resources.allMarkets`
- `success`: `boolean`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.markets`: `array`; required=False
- `result.markets[].symbol`: `string`; required=False
- `result.markets[].base_asset`: `string`; required=False
- `result.markets[].quote_asset`: `string`; required=False
- `result.markets[].fa_base_asset`: `string`; required=False
- `result.markets[].fa_quote_asset`: `string`; required=False
- `result.markets[].en_base_asset`: `string`; required=False
- `result.markets[].en_quote_asset`: `string`; required=False
- `result.markets[].categories`: `array`; required=False
- `result.markets[].price`: `string`; required=False
- `result.markets[].change_24h`: `number`; required=False
- `result.markets[].volume_24h`: `number`; required=False
- `result.markets[].change_7D`: `number`; required=False
- `result.markets[].quote_volume_24h`: `number`; required=False
- `result.markets[].spot_is_new`: `boolean`; required=False
- `result.markets[].otc_is_new`: `boolean`; required=False
- `result.markets[].is_new`: `boolean`; required=False
- `result.markets[].is_spot`: `boolean`; required=False
- `result.markets[].is_otc`: `boolean`; required=False
- `result.markets[].is_margin`: `boolean`; required=False
- `result.markets[].is_tmn_based`: `boolean`; required=False
- `result.markets[].is_usdt_based`: `boolean`; required=False
- `result.markets[].is_zero_fee`: `boolean`; required=False
- `result.markets[].leverage_step`: `number`; required=False
- `result.markets[].max_leverage`: `number`; required=False
- `result.markets[].created_at`: `string`; required=False
- `result.markets[].amount_precision`: `integer`; required=False
- `result.markets[].price_precision`: `integer`; required=False
- `result.markets[].flags`: `array`; required=False

### `GET /v1/depth`

Operation ID: `getMarketDepth`

- Parameter `symbol`; in=query; required=True; type=string

Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/MarketDepthResponse`
- `result`: `object`; required=False
- `result.ask`: `array`; required=False
- `result.ask[]` → `#/definitions/OrderBookEntry`
- `result.ask[].price`: `number`; required=False
- `result.ask[].quantity`: `number`; required=False
- `result.ask[].sum`: `string`; required=False
- `result.bid`: `array`; required=False
- `result.bid[]` → `#/definitions/OrderBookEntry`
- `result.bid[].price`: `number`; required=False
- `result.bid[].quantity`: `number`; required=False
- `result.bid[].sum`: `string`; required=False
- `message`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/account/balances`

Operation ID: `getAccountBalances`


Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/AccountBalancesResponse`
- `result`: `object`; required=False
- `result.balances`: `object`; required=False
- `message`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/udf/history`

Operation ID: `candleHistory`

- Parameter `symbol`; in=query; required=True; type=string
- Parameter `resolution`; in=query; required=True; type=string
- Parameter `from`; in=query; required=True; type=integer
- Parameter `to`; in=query; required=True; type=integer

Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/MarketHistoryResponse`
- `s`: `string`; required=False
- `t`: `array`; required=False
- `c`: `array`; required=False
- `o`: `array`; required=False
- `h`: `array`; required=False
- `l`: `array`; required=False
- `v`: `array`; required=False

## margin-c709e1f52cb44387a2e35ffd678c6dfa.json

Source: https://developers.wallex.ir/assets/files/margin-c709e1f52cb44387a2e35ffd678c6dfa.json

[Technical schema](schemas/margin-c709e1f52cb44387a2e35ffd678c6dfa.json)

### `GET /margin-trade/v1/orders`

Operation ID: `getOrders`

- Parameter `active`; in=query; required=False; type=boolean
- Parameter `market`; in=query; required=False; type=string
- Parameter `position_side`; in=query; required=False; type=string
- Parameter `position_id`; in=query; required=False; type=string
- Parameter `position_type`; in=query; required=False; type=string
- Parameter `side`; in=query; required=False; type=string

Response status codes: `200`, `408`, `500`

Response `200` fields:

- `[]` → `#/definitions/dto.Order`
- `[].created_at`: `string`; required=False
- `[].fee`: `$ref`; required=False
- `[].fee` → `#/definitions/dto.Amount`
- `[].fee.currency`: `string`; required=False
- `[].fee.value`: `string`; required=False
- `[].filled`: `$ref`; required=False
- `[].filled` → `#/definitions/dto.Amount`
- `[].filled.currency`: `string`; required=False
- `[].filled.value`: `string`; required=False
- `[].filled_price`: `$ref`; required=False
- `[].filled_price` → `#/definitions/dto.Amount`
- `[].filled_price.currency`: `string`; required=False
- `[].filled_price.value`: `string`; required=False
- `[].id`: `string`; required=False
- `[].market`: `string`; required=False
- `[].price`: `$ref`; required=False
- `[].price` → `#/definitions/dto.Amount`
- `[].price.currency`: `string`; required=False
- `[].price.value`: `string`; required=False
- `[].side`: `string`; required=False
- `[].status`: `string`; required=False
- `[].trades`: `array`; required=False
- `[].trades[]` → `#/definitions/dto.Trade`
- `[].trades[].created_at`: `string`; required=False
- `[].trades[].fee`: `$ref`; required=False
- `[].trades[].fee` → `#/definitions/dto.Amount`
- `[].trades[].fee.currency`: `string`; required=False
- `[].trades[].fee.value`: `string`; required=False
- `[].trades[].price`: `$ref`; required=False
- `[].trades[].price` → `#/definitions/dto.Amount`
- `[].trades[].price.currency`: `string`; required=False
- `[].trades[].price.value`: `string`; required=False
- `[].trades[].volume`: `$ref`; required=False
- `[].trades[].volume` → `#/definitions/dto.Amount`
- `[].trades[].volume.currency`: `string`; required=False
- `[].trades[].volume.value`: `string`; required=False
- `[].volume`: `$ref`; required=False
- `[].volume` → `#/definitions/dto.Amount`
- `[].volume.currency`: `string`; required=False
- `[].volume.value`: `string`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /margin-trade/v1/positions`

Operation ID: `getPositions`

- Parameter `active`; in=query; required=False; type=boolean
- Parameter `position_side`; in=query; required=False; type=string
- Parameter `market`; in=query; required=False; type=string

Response status codes: `200`, `408`, `500`

Response `200` fields:

- `[]` → `#/definitions/dto.Position`
- `[].call_price`: `string`; required=False
- `[].close_filled_price`: `string`; required=False
- `[].close_price`: `string`; required=False
- `[].close_reason`: `string`; required=False
- `[].closed_at`: `string`; required=False
- `[].collateral`: `$ref`; required=False
- `[].collateral` → `#/definitions/dto.Amount`
- `[].collateral.currency`: `string`; required=False
- `[].collateral.value`: `string`; required=False
- `[].created_at`: `string`; required=False
- `[].expires_at`: `string`; required=False
- `[].extend_time`: `integer`; required=False
- `[].first_order_filled`: `boolean`; required=False
- `[].id`: `string`; required=False
- `[].interest`: `$ref`; required=False
- `[].interest` → `#/definitions/dto.Amount`
- `[].interest.currency`: `string`; required=False
- `[].interest.value`: `string`; required=False
- `[].is_called`: `boolean`; required=False
- `[].liquidity_price`: `string`; required=False
- `[].loan`: `$ref`; required=False
- `[].loan` → `#/definitions/dto.Amount`
- `[].loan.currency`: `string`; required=False
- `[].loan.value`: `string`; required=False
- `[].market`: `string`; required=False
- `[].max_age`: `integer`; required=False
- `[].open_filled_price`: `string`; required=False
- `[].open_price`: `string`; required=False
- `[].opened_at`: `string`; required=False
- `[].profit`: `$ref`; required=False
- `[].profit` → `#/definitions/dto.Amount`
- `[].profit.currency`: `string`; required=False
- `[].profit.value`: `string`; required=False
- `[].profit_percentage`: `string`; required=False
- `[].risk_coef`: `string`; required=False
- `[].side`: `string`; required=False
- `[].state`: `string`; required=False
- `[].stop_loss`: `string`; required=False
- `[].take_profit`: `string`; required=False
- `[].updated_at`: `string`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `POST /margin-trade/v1/positions`

Operation ID: `openPosition`

- Parameter `position`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.OpenRequest`
- `collateral`: `string`; required=False
- `market`: `string`; required=False
- `open_price`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False

Response status codes: `200`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.Position`
- `call_price`: `string`; required=False
- `close_filled_price`: `string`; required=False
- `close_price`: `string`; required=False
- `close_reason`: `string`; required=False
- `closed_at`: `string`; required=False
- `collateral`: `$ref`; required=False
- `collateral` → `#/definitions/dto.Amount`
- `collateral.currency`: `string`; required=False
- `collateral.value`: `string`; required=False
- `created_at`: `string`; required=False
- `expires_at`: `string`; required=False
- `extend_time`: `integer`; required=False
- `first_order_filled`: `boolean`; required=False
- `id`: `string`; required=False
- `interest`: `$ref`; required=False
- `interest` → `#/definitions/dto.Amount`
- `interest.currency`: `string`; required=False
- `interest.value`: `string`; required=False
- `is_called`: `boolean`; required=False
- `liquidity_price`: `string`; required=False
- `loan`: `$ref`; required=False
- `loan` → `#/definitions/dto.Amount`
- `loan.currency`: `string`; required=False
- `loan.value`: `string`; required=False
- `market`: `string`; required=False
- `max_age`: `integer`; required=False
- `open_filled_price`: `string`; required=False
- `open_price`: `string`; required=False
- `opened_at`: `string`; required=False
- `profit`: `$ref`; required=False
- `profit` → `#/definitions/dto.Amount`
- `profit.currency`: `string`; required=False
- `profit.value`: `string`; required=False
- `profit_percentage`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False
- `state`: `string`; required=False
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False
- `updated_at`: `string`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /margin-trade/v1/positions/{id}`

Operation ID: `getPositionId`

- Parameter `id`; in=path; required=True; type=string

Response status codes: `200`, `404`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.Position`
- `call_price`: `string`; required=False
- `close_filled_price`: `string`; required=False
- `close_price`: `string`; required=False
- `close_reason`: `string`; required=False
- `closed_at`: `string`; required=False
- `collateral`: `$ref`; required=False
- `collateral` → `#/definitions/dto.Amount`
- `collateral.currency`: `string`; required=False
- `collateral.value`: `string`; required=False
- `created_at`: `string`; required=False
- `expires_at`: `string`; required=False
- `extend_time`: `integer`; required=False
- `first_order_filled`: `boolean`; required=False
- `id`: `string`; required=False
- `interest`: `$ref`; required=False
- `interest` → `#/definitions/dto.Amount`
- `interest.currency`: `string`; required=False
- `interest.value`: `string`; required=False
- `is_called`: `boolean`; required=False
- `liquidity_price`: `string`; required=False
- `loan`: `$ref`; required=False
- `loan` → `#/definitions/dto.Amount`
- `loan.currency`: `string`; required=False
- `loan.value`: `string`; required=False
- `market`: `string`; required=False
- `max_age`: `integer`; required=False
- `open_filled_price`: `string`; required=False
- `open_price`: `string`; required=False
- `opened_at`: `string`; required=False
- `profit`: `$ref`; required=False
- `profit` → `#/definitions/dto.Amount`
- `profit.currency`: `string`; required=False
- `profit.value`: `string`; required=False
- `profit_percentage`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False
- `state`: `string`; required=False
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False
- `updated_at`: `string`; required=False

Response `404` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `PATCH /margin-trade/v1/positions/{id}/close`

Operation ID: `closePositionId`

- Parameter `id`; in=path; required=True; type=string
- Parameter `position`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.CloseRequest`
- `price`: `string`; required=False

Response status codes: `200`, `404`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.Position`
- `call_price`: `string`; required=False
- `close_filled_price`: `string`; required=False
- `close_price`: `string`; required=False
- `close_reason`: `string`; required=False
- `closed_at`: `string`; required=False
- `collateral`: `$ref`; required=False
- `collateral` → `#/definitions/dto.Amount`
- `collateral.currency`: `string`; required=False
- `collateral.value`: `string`; required=False
- `created_at`: `string`; required=False
- `expires_at`: `string`; required=False
- `extend_time`: `integer`; required=False
- `first_order_filled`: `boolean`; required=False
- `id`: `string`; required=False
- `interest`: `$ref`; required=False
- `interest` → `#/definitions/dto.Amount`
- `interest.currency`: `string`; required=False
- `interest.value`: `string`; required=False
- `is_called`: `boolean`; required=False
- `liquidity_price`: `string`; required=False
- `loan`: `$ref`; required=False
- `loan` → `#/definitions/dto.Amount`
- `loan.currency`: `string`; required=False
- `loan.value`: `string`; required=False
- `market`: `string`; required=False
- `max_age`: `integer`; required=False
- `open_filled_price`: `string`; required=False
- `open_price`: `string`; required=False
- `opened_at`: `string`; required=False
- `profit`: `$ref`; required=False
- `profit` → `#/definitions/dto.Amount`
- `profit.currency`: `string`; required=False
- `profit.value`: `string`; required=False
- `profit_percentage`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False
- `state`: `string`; required=False
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False
- `updated_at`: `string`; required=False

Response `404` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `PATCH /margin-trade/v1/positions/{id}/collateral`

Operation ID: `editColateral`

- Parameter `id`; in=path; required=True; type=string
- Parameter `update`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.AddCollateralRequest`
- `change`: `string`; required=False

Response status codes: `200`, `404`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.Position`
- `call_price`: `string`; required=False
- `close_filled_price`: `string`; required=False
- `close_price`: `string`; required=False
- `close_reason`: `string`; required=False
- `closed_at`: `string`; required=False
- `collateral`: `$ref`; required=False
- `collateral` → `#/definitions/dto.Amount`
- `collateral.currency`: `string`; required=False
- `collateral.value`: `string`; required=False
- `created_at`: `string`; required=False
- `expires_at`: `string`; required=False
- `extend_time`: `integer`; required=False
- `first_order_filled`: `boolean`; required=False
- `id`: `string`; required=False
- `interest`: `$ref`; required=False
- `interest` → `#/definitions/dto.Amount`
- `interest.currency`: `string`; required=False
- `interest.value`: `string`; required=False
- `is_called`: `boolean`; required=False
- `liquidity_price`: `string`; required=False
- `loan`: `$ref`; required=False
- `loan` → `#/definitions/dto.Amount`
- `loan.currency`: `string`; required=False
- `loan.value`: `string`; required=False
- `market`: `string`; required=False
- `max_age`: `integer`; required=False
- `open_filled_price`: `string`; required=False
- `open_price`: `string`; required=False
- `opened_at`: `string`; required=False
- `profit`: `$ref`; required=False
- `profit` → `#/definitions/dto.Amount`
- `profit.currency`: `string`; required=False
- `profit.value`: `string`; required=False
- `profit_percentage`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False
- `state`: `string`; required=False
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False
- `updated_at`: `string`; required=False

Response `404` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `POST /margin-trade/v1/positions/{id}/profit`

Operation ID: `profitPositionID`

- Parameter `id`; in=path; required=True; type=string
- Parameter `request`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.CalculateProfitRequest`
- `close_price`: `string`; required=False
- `strategy`: `string`; required=False

Response status codes: `200`, `404`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.CalculateProfitResponse`
- `fee`: `string`; required=False
- `filled_percentage`: `string`; required=False
- `interest`: `$ref`; required=False
- `interest` → `#/definitions/dto.Amount`
- `interest.currency`: `string`; required=False
- `interest.value`: `string`; required=False
- `price`: `string`; required=False
- `profit`: `$ref`; required=False
- `profit` → `#/definitions/dto.Amount`
- `profit.currency`: `string`; required=False
- `profit.value`: `string`; required=False
- `side`: `string`; required=False
- `volume`: `$ref`; required=False
- `volume` → `#/definitions/dto.Amount`
- `volume.currency`: `string`; required=False
- `volume.value`: `string`; required=False

Response `404` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `PATCH /margin-trade/v1/positions/{id}/sltp`

Operation ID: `editSltp`

- Parameter `id`; in=path; required=True; type=string
- Parameter `update`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.UpdateSLTPRequest`
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False

Response status codes: `200`, `404`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.Position`
- `call_price`: `string`; required=False
- `close_filled_price`: `string`; required=False
- `close_price`: `string`; required=False
- `close_reason`: `string`; required=False
- `closed_at`: `string`; required=False
- `collateral`: `$ref`; required=False
- `collateral` → `#/definitions/dto.Amount`
- `collateral.currency`: `string`; required=False
- `collateral.value`: `string`; required=False
- `created_at`: `string`; required=False
- `expires_at`: `string`; required=False
- `extend_time`: `integer`; required=False
- `first_order_filled`: `boolean`; required=False
- `id`: `string`; required=False
- `interest`: `$ref`; required=False
- `interest` → `#/definitions/dto.Amount`
- `interest.currency`: `string`; required=False
- `interest.value`: `string`; required=False
- `is_called`: `boolean`; required=False
- `liquidity_price`: `string`; required=False
- `loan`: `$ref`; required=False
- `loan` → `#/definitions/dto.Amount`
- `loan.currency`: `string`; required=False
- `loan.value`: `string`; required=False
- `market`: `string`; required=False
- `max_age`: `integer`; required=False
- `open_filled_price`: `string`; required=False
- `open_price`: `string`; required=False
- `opened_at`: `string`; required=False
- `profit`: `$ref`; required=False
- `profit` → `#/definitions/dto.Amount`
- `profit.currency`: `string`; required=False
- `profit.value`: `string`; required=False
- `profit_percentage`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False
- `state`: `string`; required=False
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False
- `updated_at`: `string`; required=False

Response `404` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `POST /margin-trade/v1/public/loan`

Operation ID: `calculateLoan`

- Parameter `request`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.CalculateLoanRequest`
- `collateral`: `string`; required=False
- `market`: `string`; required=False
- `open_price`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False

Response status codes: `200`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.CalculateLoanResponse`
- `collateral`: `$ref`; required=False
- `collateral` → `#/definitions/dto.CollateralRange`
- `collateral.max`: `string`; required=False
- `collateral.min`: `string`; required=False
- `loan`: `$ref`; required=False
- `loan` → `#/definitions/dto.Amount`
- `loan.currency`: `string`; required=False
- `loan.value`: `string`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `POST /margin-trade/v1/public/dry-run`

Operation ID: `detailedInformation`

- Parameter `position`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.OpenRequest`
- `collateral`: `string`; required=False
- `market`: `string`; required=False
- `open_price`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False

Response status codes: `200`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.DryRunResponse`
- `call_price`: `string`; required=False
- `collateral`: `$ref`; required=False
- `collateral` → `#/definitions/dto.Amount`
- `collateral.currency`: `string`; required=False
- `collateral.value`: `string`; required=False
- `extend_fee`: `$ref`; required=False
- `extend_fee` → `#/definitions/dto.Amount`
- `extend_fee.currency`: `string`; required=False
- `extend_fee.value`: `string`; required=False
- `extend_time`: `integer`; required=False
- `liquidity_price`: `string`; required=False
- `loan`: `$ref`; required=False
- `loan` → `#/definitions/dto.Amount`
- `loan.currency`: `string`; required=False
- `loan.value`: `string`; required=False
- `market`: `string`; required=False
- `max_age`: `integer`; required=False
- `open_fee`: `$ref`; required=False
- `open_fee` → `#/definitions/dto.Amount`
- `open_fee.currency`: `string`; required=False
- `open_fee.value`: `string`; required=False
- `open_price`: `string`; required=False
- `risk_coef`: `string`; required=False
- `side`: `string`; required=False
- `stop_loss`: `string`; required=False
- `take_profit`: `string`; required=False
- `trade_fee`: `$ref`; required=False
- `trade_fee` → `#/definitions/dto.Amount`
- `trade_fee.currency`: `string`; required=False
- `trade_fee.value`: `string`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /margin-trade/v1/public/markets`

Operation ID: `getMarkets`


Response status codes: `200`, `408`, `500`

Response `200` fields:

- `[]` → `#/definitions/dto.Market`
- `[].base`: `string`; required=False
- `[].liquidity_margin`: `string`; required=False
- `[].max_age`: `integer`; required=False
- `[].max_risk_coef`: `string`; required=False
- `[].min_risk_coef`: `string`; required=False
- `[].quote`: `string`; required=False
- `[].risk_coef_step`: `string`; required=False
- `[].symbol`: `string`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /margin-trade/v1/public/ratio/{market}`

Operation ID: `publicRatio`

- Parameter `market`; in=path; required=True; type=string

Response status codes: `200`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.PositionsRatioResponse`
- `long_percents`: `integer`; required=False
- `short_percents`: `integer`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /margin-trade/v1/user/levels`

Operation ID: `?getLevels`


Response status codes: `200`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.GetUserLevelResponse`
- `levels`: `$ref`; required=False
- `levels` → `#/definitions/settings.UserLevels`
- `user_level`: `integer`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /margin-trade/v1/user/levels/{market}`

Operation ID: `getLevelsMarket`

- Parameter `market`; in=path; required=True; type=string

Response status codes: `200`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.GetUserLevelResponse`
- `levels`: `$ref`; required=False
- `levels` → `#/definitions/settings.UserLevels`
- `user_level`: `integer`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /margin-trade/v1/user/pnl`

Operation ID: `getPnl`


Response status codes: `200`, `408`, `500`

Response `200` fields:

- `$` → `#/definitions/dto.CalculatePnlResponse`
- `collaterals`: `object`; required=False
- `loans`: `object`; required=False
- `profits`: `object`; required=False
- `total`: `object`; required=False

Response `408` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/dto.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

## otc-8e321a32f4509cbf103b3127bf7c9918.json

Source: https://developers.wallex.ir/assets/files/otc-8e321a32f4509cbf103b3127bf7c9918.json

[Technical schema](schemas/otc-8e321a32f4509cbf103b3127bf7c9918.json)

### `GET /v1/otc/markets`

Operation ID: `getOTCMarkets`


Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/OtcMarketsResponse`
- `success`: `boolean`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False

### `GET /v1/account/otc/price`

Operation ID: `getOtcPrice`

- Parameter `symbol`; in=query; required=True; type=string
- Parameter `side`; in=query; required=True; type=string

Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/OtcPriceResponse`
- `success`: `boolean`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.price`: `string`; required=False
- `result.price_expires_at`: `string`; required=False
- `result.ttl`: `integer`; required=False
- `result.current_time`: `string`; required=False

### `POST /v1/account/easy-trade/orders`

Operation ID: `placeEasyTradeOrder`

- Parameter `body`; in=body; required=True; type=unspecified
- `$` → `#/definitions/EasyTradeOrderRequest`
- `symbol`: `string`; required=True
- `side`: `string`; required=True; enum=["BUY", "SELL"]
- `quantity`: `number`; required=True
- `from`: `string`; required=True

Response status codes: `201`

Response `201` fields:

- `$` → `#/definitions/EasyTradeOrderResponse`
- `symbol`: `string`; required=False
- `sourceMarket`: `string`; required=False
- `destinationMarket`: `string`; required=False
- `type`: `string`; required=False
- `side`: `string`; required=False
- `clientOrderId`: `string`; required=False
- `transactTime`: `integer`; required=False
- `price`: `string`; required=False
- `origQty`: `string`; required=False
- `executedSum`: `string`; required=False
- `executedQty`: `string`; required=False
- `executedPrice`: `string`; required=False
- `sum`: `string`; required=False
- `executedPercent`: `number`; required=False
- `status`: `string`; required=False
- `active`: `boolean`; required=False
- `fills`: `array`; required=False
- `fills[]` → `#/definitions/EasyTradeFill`
- `fills[].price`: `string`; required=False
- `fills[].quantity`: `string`; required=False
- `fills[].fee`: `string`; required=False
- `fills[].feeCoefficient`: `string`; required=False
- `fills[].feeAsset`: `object`; required=False
- `fills[].timestamp`: `string`; required=False
- `fills[].symbol`: `string`; required=False
- `fills[].sum`: `string`; required=False
- `fills[].makerFeeCoefficient`: `string`; required=False
- `fills[].takerFeeCoefficient`: `string`; required=False
- `fills[].isBuyer`: `boolean`; required=False

## spot-b9d06896d1009adc9ebc69b9a5495e7e.json

Source: https://developers.wallex.ir/assets/files/spot-b9d06896d1009adc9ebc69b9a5495e7e.json

[Technical schema](schemas/spot-b9d06896d1009adc9ebc69b9a5495e7e.json)

### `GET /hector/web/v1/markets`

Operation ID: `getMarkets`


Response status codes: `200`

Response `200` fields:

- `$` → `#/definitions/resources.allMarkets`
- `success`: `boolean`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.markets`: `array`; required=False
- `result.markets[].symbol`: `string`; required=False
- `result.markets[].base_asset`: `string`; required=False
- `result.markets[].quote_asset`: `string`; required=False
- `result.markets[].fa_base_asset`: `string`; required=False
- `result.markets[].fa_quote_asset`: `string`; required=False
- `result.markets[].en_base_asset`: `string`; required=False
- `result.markets[].en_quote_asset`: `string`; required=False
- `result.markets[].categories`: `array`; required=False
- `result.markets[].price`: `string`; required=False
- `result.markets[].change_24h`: `number`; required=False
- `result.markets[].volume_24h`: `number`; required=False
- `result.markets[].change_7D`: `number`; required=False
- `result.markets[].quote_volume_24h`: `number`; required=False
- `result.markets[].spot_is_new`: `boolean`; required=False
- `result.markets[].otc_is_new`: `boolean`; required=False
- `result.markets[].is_new`: `boolean`; required=False
- `result.markets[].is_spot`: `boolean`; required=False
- `result.markets[].is_otc`: `boolean`; required=False
- `result.markets[].is_margin`: `boolean`; required=False
- `result.markets[].is_tmn_based`: `boolean`; required=False
- `result.markets[].is_usdt_based`: `boolean`; required=False
- `result.markets[].is_zero_fee`: `boolean`; required=False
- `result.markets[].leverage_step`: `number`; required=False
- `result.markets[].max_leverage`: `number`; required=False
- `result.markets[].created_at`: `string`; required=False
- `result.markets[].amount_precision`: `integer`; required=False
- `result.markets[].price_precision`: `integer`; required=False
- `result.markets[].flags`: `array`; required=False

### `GET /depth/all`

Operation ID: `getDepth`


Response status codes: `200`, `500`

Response `200` fields:

- `$` → `#/definitions/resources.AllMarketDepthResponse`
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `500` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /v1/account/openOrders`

Operation ID: `getOpenOrder`

- Parameter `symbol`; in=query; required=False; type=string
- Parameter `page`; in=query; required=False; type=integer
- Parameter `per_page`; in=query; required=False; type=integer

Response status codes: `200`, `400`, `401`, `422`

Response `200` fields:

- `$` → `#/definitions/resources.OrderListResponseV1`
- `message`: `string`; required=False
- `result`: `object`; required=False
- `result_info`: `unspecified`; required=False
- `success`: `boolean`; required=False

Response `400` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `401` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `422` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /v1/account/orders`

Operation ID: `getOrders`

- Parameter `market`; in=query; required=False; type=string
- Parameter `type`; in=query; required=False; type=string
- Parameter `side`; in=query; required=False; type=string
- Parameter `page`; in=query; required=False; type=integer
- Parameter `per_page`; in=query; required=False; type=integer
- Parameter `from`; in=query; required=False; type=string
- Parameter `to`; in=query; required=False; type=string

Response status codes: `200`, `400`, `401`, `422`

Response `200` fields:

- `$` → `#/definitions/resources.OrderPaginateResponseV1`
- `message`: `string`; required=False
- `result`: `object`; required=False
- `result_info`: `unspecified`; required=False
- `success`: `boolean`; required=False

Response `400` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `401` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `422` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `POST /v1/account/orders`

Operation ID: `postAccountOrders`

- Parameter `order`; in=body; required=True; type=unspecified
- `$` → `#/definitions/requests.CreateOrderRequest`
- `client_id`: `string`; required=False
- `price`: `string`; required=False
- `quantity`: `string`; required=False
- `side`: `string`; required=True
- `stop_Price`: `string`; required=False
- `symbol`: `string`; required=True
- `type`: `string`; required=True

Response status codes: `201`, `400`, `401`, `422`

Response `201` fields:

- `$` → `#/definitions/resources.OrderResponse`
- `message`: `string`; required=False
- `result`: `$ref`; required=False
- `result` → `#/definitions/resources.OrderResource`
- `result.active`: `boolean`; required=False
- `result.clientOrderId`: `string`; required=False
- `result.created_at`: `string`; required=False
- `result.executedPercent`: `integer`; required=False
- `result.executedPrice`: `string`; required=False
- `result.executedQty`: `string`; required=False
- `result.executedSum`: `string`; required=False
- `result.fee`: `string`; required=False
- `result.fills`: `array`; required=False
- `result.fills[]` → `#/definitions/resources.TradeResource`
- `result.fills[].fee`: `string`; required=False
- `result.fills[].feeAsset`: `string`; required=False
- `result.fills[].feeCoefficient`: `string`; required=False
- `result.fills[].isBuyer`: `boolean`; required=False
- `result.fills[].makerFeeCoefficient`: `string`; required=False
- `result.fills[].price`: `string`; required=False
- `result.fills[].quantity`: `string`; required=False
- `result.fills[].sum`: `string`; required=False
- `result.fills[].symbol`: `string`; required=False
- `result.fills[].takerFeeCoefficient`: `string`; required=False
- `result.fills[].timestamp`: `string`; required=False
- `result.origQty`: `string`; required=False
- `result.price`: `string`; required=False
- `result.side`: `string`; required=False
- `result.status`: `string`; required=False
- `result.stopPrice`: `string`; required=False
- `result.stopPriceCondition`: `string`; required=False
- `result.sum`: `string`; required=False
- `result.symbol`: `string`; required=False
- `result.transactTime`: `integer`; required=False
- `result.type`: `string`; required=False
- `result.updated_at`: `string`; required=False
- `success`: `boolean`; required=False

Response `400` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `401` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `422` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `DELETE /v1/account/orders`

Operation ID: `deleteAccountOrders`

- Parameter `order`; in=body; required=True; type=unspecified
- `$` → `#/definitions/requests.CancelOrderRequest`
- `clientOrderId`: `string`; required=True

Response status codes: `200`, `400`, `401`, `422`

Response `200` fields:

- `$` → `#/definitions/resources.OrderResponse`
- `message`: `string`; required=False
- `result`: `$ref`; required=False
- `result` → `#/definitions/resources.OrderResource`
- `result.active`: `boolean`; required=False
- `result.clientOrderId`: `string`; required=False
- `result.created_at`: `string`; required=False
- `result.executedPercent`: `integer`; required=False
- `result.executedPrice`: `string`; required=False
- `result.executedQty`: `string`; required=False
- `result.executedSum`: `string`; required=False
- `result.fee`: `string`; required=False
- `result.fills`: `array`; required=False
- `result.fills[]` → `#/definitions/resources.TradeResource`
- `result.fills[].fee`: `string`; required=False
- `result.fills[].feeAsset`: `string`; required=False
- `result.fills[].feeCoefficient`: `string`; required=False
- `result.fills[].isBuyer`: `boolean`; required=False
- `result.fills[].makerFeeCoefficient`: `string`; required=False
- `result.fills[].price`: `string`; required=False
- `result.fills[].quantity`: `string`; required=False
- `result.fills[].sum`: `string`; required=False
- `result.fills[].symbol`: `string`; required=False
- `result.fills[].takerFeeCoefficient`: `string`; required=False
- `result.fills[].timestamp`: `string`; required=False
- `result.origQty`: `string`; required=False
- `result.price`: `string`; required=False
- `result.side`: `string`; required=False
- `result.status`: `string`; required=False
- `result.stopPrice`: `string`; required=False
- `result.stopPriceCondition`: `string`; required=False
- `result.sum`: `string`; required=False
- `result.symbol`: `string`; required=False
- `result.transactTime`: `integer`; required=False
- `result.type`: `string`; required=False
- `result.updated_at`: `string`; required=False
- `success`: `boolean`; required=False

Response `400` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `401` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `422` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `GET /v1/account/orders/{client_id}`

Operation ID: `getOrdersClient`

- Parameter `client_id`; in=path; required=True; type=string

Response status codes: `200`, `400`, `401`, `404`

Response `200` fields:

- `$` → `#/definitions/resources.OrderResponse`
- `message`: `string`; required=False
- `result`: `$ref`; required=False
- `result` → `#/definitions/resources.OrderResource`
- `result.active`: `boolean`; required=False
- `result.clientOrderId`: `string`; required=False
- `result.created_at`: `string`; required=False
- `result.executedPercent`: `integer`; required=False
- `result.executedPrice`: `string`; required=False
- `result.executedQty`: `string`; required=False
- `result.executedSum`: `string`; required=False
- `result.fee`: `string`; required=False
- `result.fills`: `array`; required=False
- `result.fills[]` → `#/definitions/resources.TradeResource`
- `result.fills[].fee`: `string`; required=False
- `result.fills[].feeAsset`: `string`; required=False
- `result.fills[].feeCoefficient`: `string`; required=False
- `result.fills[].isBuyer`: `boolean`; required=False
- `result.fills[].makerFeeCoefficient`: `string`; required=False
- `result.fills[].price`: `string`; required=False
- `result.fills[].quantity`: `string`; required=False
- `result.fills[].sum`: `string`; required=False
- `result.fills[].symbol`: `string`; required=False
- `result.fills[].takerFeeCoefficient`: `string`; required=False
- `result.fills[].timestamp`: `string`; required=False
- `result.origQty`: `string`; required=False
- `result.price`: `string`; required=False
- `result.side`: `string`; required=False
- `result.status`: `string`; required=False
- `result.stopPrice`: `string`; required=False
- `result.stopPriceCondition`: `string`; required=False
- `result.sum`: `string`; required=False
- `result.symbol`: `string`; required=False
- `result.transactTime`: `integer`; required=False
- `result.type`: `string`; required=False
- `result.updated_at`: `string`; required=False
- `success`: `boolean`; required=False

Response `400` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `401` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `404` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

### `DELETE /v1/account/orders/{client_id}`

Operation ID: `deleteOrdersClient`

- Parameter `client_id`; in=path; required=True; type=string

Response status codes: `200`, `400`, `401`, `422`

Response `200` fields:

- `$` → `#/definitions/resources.OrderResponse`
- `message`: `string`; required=False
- `result`: `$ref`; required=False
- `result` → `#/definitions/resources.OrderResource`
- `result.active`: `boolean`; required=False
- `result.clientOrderId`: `string`; required=False
- `result.created_at`: `string`; required=False
- `result.executedPercent`: `integer`; required=False
- `result.executedPrice`: `string`; required=False
- `result.executedQty`: `string`; required=False
- `result.executedSum`: `string`; required=False
- `result.fee`: `string`; required=False
- `result.fills`: `array`; required=False
- `result.fills[]` → `#/definitions/resources.TradeResource`
- `result.fills[].fee`: `string`; required=False
- `result.fills[].feeAsset`: `string`; required=False
- `result.fills[].feeCoefficient`: `string`; required=False
- `result.fills[].isBuyer`: `boolean`; required=False
- `result.fills[].makerFeeCoefficient`: `string`; required=False
- `result.fills[].price`: `string`; required=False
- `result.fills[].quantity`: `string`; required=False
- `result.fills[].sum`: `string`; required=False
- `result.fills[].symbol`: `string`; required=False
- `result.fills[].takerFeeCoefficient`: `string`; required=False
- `result.fills[].timestamp`: `string`; required=False
- `result.origQty`: `string`; required=False
- `result.price`: `string`; required=False
- `result.side`: `string`; required=False
- `result.status`: `string`; required=False
- `result.stopPrice`: `string`; required=False
- `result.stopPriceCondition`: `string`; required=False
- `result.sum`: `string`; required=False
- `result.symbol`: `string`; required=False
- `result.transactTime`: `integer`; required=False
- `result.type`: `string`; required=False
- `result.updated_at`: `string`; required=False
- `success`: `boolean`; required=False

Response `400` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `401` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

Response `422` fields:

- `$` → `#/definitions/resources.ErrorResponse`
- `code`: `integer`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `success`: `boolean`; required=False

## trade-credit-ff5c60b5b97b77a5b2c2e4800f07729c.json

Source: https://developers.wallex.ir/assets/files/trade-credit-ff5c60b5b97b77a5b2c2e4800f07729c.yaml

[Technical schema](schemas/trade-credit-ff5c60b5b97b77a5b2c2e4800f07729c.json)

### `GET /sub-accounts`

Operation ID: `activeSubAccountsList`


Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `array`; required=False
- `result[].clientId`: `string`; required=False
- `result[].createdAt`: `string`; required=False
- `result[].darkAvatarUrl`: `string`; required=False
- `result[].isActive`: `boolean`; required=False
- `result[].isSuspend`: `boolean`; required=False
- `result[].lightAvatarUrl`: `string`; required=False
- `result[].title`: `string`; required=False
- `result[].type`: `string`; required=False
- `result[].userId`: `number`; required=False
- `result_info`: `object`; required=False
- `result_info.count`: `number`; required=False
- `result_info.page`: `number`; required=False
- `result_info.per_page`: `number`; required=False
- `result_info.total_count`: `number`; required=False
- `success`: `boolean`; required=False

### `GET /sub-accounts/transfers`

Operation ID: `subAccountTransfer`

- Parameter `sub-account-client-id`; in=header; required=False; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `array`; required=False
- `result[].createdAt`: `string`; required=False
- `result[].currency`: `string`; required=False
- `result[].destination_client_id`: `string`; required=False
- `result[].destination_client_title`: `string`; required=False
- `result[].destination_user_type`: `string`; required=False
- `result[].fa_destination_user_type`: `string`; required=False
- `result[].fa_source_user_type`: `string`; required=False
- `result[].reason`: `string`; required=False
- `result[].source_client_id`: `string`; required=False
- `result[].source_client_title`: `string`; required=False
- `result[].source_user_type`: `string`; required=False
- `result[].unique_id`: `number`; required=False
- `result[].value`: `string`; required=False
- `result_info`: `object`; required=False
- `result_info.count`: `number`; required=False
- `result_info.page`: `number`; required=False
- `result_info.per_page`: `number`; required=False
- `result_info.total_count`: `number`; required=False
- `success`: `boolean`; required=False

### `POST /sub-accounts/transfers`

Operation ID: `createTransferToSubAccount`

- Parameter `sub-account-client-id`; in=header; required=False; type=string

Request content: `application/json`
- `currency`: `string`; required=False
- `subAccount_client_id`: `string`; required=False
- `value`: `string`; required=False

Response status codes: `200`, `422`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.clientId`: `string`; required=False
- `result.createdAt`: `string`; required=False
- `result.darkAvatarUrl`: `string`; required=False
- `result.isActive`: `boolean`; required=False
- `result.isSuspend`: `boolean`; required=False
- `result.lightAvatarUrl`: `string`; required=False
- `result.title`: `string`; required=False
- `result.type`: `string`; required=False
- `result.userId`: `number`; required=False
- `success`: `boolean`; required=False

Response `422` / `application/json` fields:

- `code`: `number`; required=False
- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.currency`: `array`; required=False
- `success`: `boolean`; required=False

### `GET /v1/account/balances-detail`

Operation ID: `subAccountBalancesDetails`

- Parameter `sub-account-client-id`; in=header; required=False; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.BTC`: `object`; required=False
- `result.BTC.available`: `string`; required=False
- `result.BTC.freeze`: `string`; required=False
- `result.BTC.stats`: `object`; required=False
- `result.BTC.stats.BTC`: `object`; required=False
- `result.BTC.stats.BTC.changePercentage`: `string`; required=False
- `result.BTC.stats.BTC.estimatedValue`: `string`; required=False
- `result.BTC.stats.BTC.last24HoursEstimatedValueChange`: `string`; required=False
- `result.BTC.stats.TMN`: `object`; required=False
- `result.BTC.stats.TMN.baseMarketName`: `string`; required=False
- `result.BTC.stats.TMN.changePercentage`: `string`; required=False
- `result.BTC.stats.TMN.estimatedValue`: `string`; required=False
- `result.BTC.stats.TMN.last24HoursEstimatedValueChange`: `string`; required=False
- `result.BTC.stats.USDT`: `object`; required=False
- `result.BTC.stats.USDT.baseMarketName`: `string`; required=False
- `result.BTC.stats.USDT.changePercentage`: `string`; required=False
- `result.BTC.stats.USDT.estimatedValue`: `string`; required=False
- `result.BTC.stats.USDT.last24HoursEstimatedValueChange`: `string`; required=False
- `result.BTC.symbol`: `string`; required=False
- `result.BTC.total`: `string`; required=False
- `result.ETH`: `object`; required=False
- `result.ETH.available`: `string`; required=False
- `result.ETH.freeze`: `string`; required=False
- `result.ETH.stats`: `object`; required=False
- `result.ETH.stats.BTC`: `object`; required=False
- `result.ETH.stats.BTC.changePercentage`: `string`; required=False
- `result.ETH.stats.BTC.estimatedValue`: `string`; required=False
- `result.ETH.stats.BTC.last24HoursEstimatedValueChange`: `string`; required=False
- `result.ETH.stats.TMN`: `object`; required=False
- `result.ETH.stats.TMN.baseMarketName`: `string`; required=False
- `result.ETH.stats.TMN.changePercentage`: `string`; required=False
- `result.ETH.stats.TMN.estimatedValue`: `string`; required=False
- `result.ETH.stats.TMN.last24HoursEstimatedValueChange`: `string`; required=False
- `result.ETH.stats.USDT`: `object`; required=False
- `result.ETH.stats.USDT.baseMarketName`: `string`; required=False
- `result.ETH.stats.USDT.changePercentage`: `string`; required=False
- `result.ETH.stats.USDT.estimatedValue`: `string`; required=False
- `result.ETH.stats.USDT.last24HoursEstimatedValueChange`: `string`; required=False
- `result.ETH.symbol`: `string`; required=False
- `result.ETH.total`: `string`; required=False
- `result.TMN`: `object`; required=False
- `result.TMN.available`: `string`; required=False
- `result.TMN.freeze`: `string`; required=False
- `result.TMN.stats`: `object`; required=False
- `result.TMN.stats.BTC`: `object`; required=False
- `result.TMN.stats.BTC.baseMarketName`: `string`; required=False
- `result.TMN.stats.BTC.changePercentage`: `string`; required=False
- `result.TMN.stats.BTC.estimatedValue`: `string`; required=False
- `result.TMN.stats.BTC.last24HoursEstimatedValueChange`: `string`; required=False
- `result.TMN.stats.TMN`: `object`; required=False
- `result.TMN.stats.TMN.changePercentage`: `string`; required=False
- `result.TMN.stats.TMN.estimatedValue`: `string`; required=False
- `result.TMN.stats.TMN.last24HoursEstimatedValueChange`: `string`; required=False
- `result.TMN.stats.USDT`: `object`; required=False
- `result.TMN.stats.USDT.baseMarketName`: `string`; required=False
- `result.TMN.stats.USDT.changePercentage`: `string`; required=False
- `result.TMN.stats.USDT.estimatedValue`: `string`; required=False
- `result.TMN.stats.USDT.last24HoursEstimatedValueChange`: `string`; required=False
- `result.TMN.symbol`: `string`; required=False
- `result.TMN.total`: `string`; required=False
- `result.USDT`: `object`; required=False
- `result.USDT.available`: `string`; required=False
- `result.USDT.freeze`: `string`; required=False
- `result.USDT.stats`: `object`; required=False
- `result.USDT.stats.BTC`: `object`; required=False
- `result.USDT.stats.BTC.baseMarketName`: `string`; required=False
- `result.USDT.stats.BTC.changePercentage`: `string`; required=False
- `result.USDT.stats.BTC.estimatedValue`: `string`; required=False
- `result.USDT.stats.BTC.last24HoursEstimatedValueChange`: `string`; required=False
- `result.USDT.stats.TMN`: `object`; required=False
- `result.USDT.stats.TMN.baseMarketName`: `string`; required=False
- `result.USDT.stats.TMN.changePercentage`: `string`; required=False
- `result.USDT.stats.TMN.estimatedValue`: `string`; required=False
- `result.USDT.stats.TMN.last24HoursEstimatedValueChange`: `string`; required=False
- `result.USDT.stats.USDT`: `object`; required=False
- `result.USDT.stats.USDT.changePercentage`: `string`; required=False
- `result.USDT.stats.USDT.estimatedValue`: `string`; required=False
- `result.USDT.stats.USDT.last24HoursEstimatedValueChange`: `string`; required=False
- `result.USDT.symbol`: `string`; required=False
- `result.USDT.total`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/prop/packages`

Operation ID: `propPackagesList`

- Parameter ``; in=query; required=False; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `array`; required=False
- `result[].assurance`: `string`; required=False
- `result[].currency`: `string`; required=False
- `result[].daily_fee`: `string`; required=False
- `result[].daily_fee_after_discount`: `string`; required=False
- `result[].daily_fee_discount`: `string`; required=False
- `result[].dark_image_url`: `string`; required=False
- `result[].destination_currency`: `unspecified`; required=False
- `result[].expire_days`: `number`; required=False
- `result[].final_fee`: `string`; required=False
- `result[].final_fee_after_discount`: `string`; required=False
- `result[].final_fee_discount`: `string`; required=False
- `result[].id`: `number`; required=False
- `result[].light_image_url`: `string`; required=False
- `result[].liquidity_limit`: `string`; required=False
- `result[].loan`: `string`; required=False
- `result[].status`: `string`; required=False
- `result[].title`: `string`; required=False
- `result[].warning_limit`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/prop/packages/{id}`

Operation ID: `propPackageDetails`

- Parameter `id`; in=path; required=True; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.detail`: `object`; required=False
- `result.detail.assurance`: `string`; required=False
- `result.detail.currency`: `string`; required=False
- `result.detail.daily_fee`: `string`; required=False
- `result.detail.daily_fee_after_discount`: `string`; required=False
- `result.detail.daily_fee_discount`: `string`; required=False
- `result.detail.dark_image_url`: `string`; required=False
- `result.detail.destination_currency`: `unspecified`; required=False
- `result.detail.expire_days`: `number`; required=False
- `result.detail.final_fee`: `string`; required=False
- `result.detail.final_fee_after_discount`: `string`; required=False
- `result.detail.final_fee_discount`: `string`; required=False
- `result.detail.id`: `number`; required=False
- `result.detail.light_image_url`: `string`; required=False
- `result.detail.liquidity_limit`: `string`; required=False
- `result.detail.loan`: `string`; required=False
- `result.detail.status`: `string`; required=False
- `result.detail.title`: `string`; required=False
- `result.detail.warning_limit`: `string`; required=False
- `result.faq`: `array`; required=False
- `result.unavailableMarkets`: `array`; required=False
- `success`: `boolean`; required=False

### `GET /v1/prop/user/packages/history`

Operation ID: `userPackageHistoryList`


Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `array`; required=False
- `result[].applicable_daily_fee`: `string`; required=False
- `result[].applicable_daily_fee_after_discount`: `string`; required=False
- `result[].applicable_daily_fee_discount`: `string`; required=False
- `result[].assurance`: `string`; required=False
- `result[].client_id`: `string`; required=False
- `result[].close_reason`: `string`; required=False
- `result[].created_at`: `string`; required=False
- `result[].currency`: `string`; required=False
- `result[].daily_fee`: `string`; required=False
- `result[].daily_fee_after_discount`: `string`; required=False
- `result[].daily_fee_discount`: `string`; required=False
- `result[].dark_image_url`: `string`; required=False
- `result[].destination_currency`: `string`; required=False
- `result[].expire_at`: `string`; required=False
- `result[].expire_days`: `number`; required=False
- `result[].final_assurance`: `string`; required=False
- `result[].final_balance`: `string`; required=False
- `result[].final_balance_without_transfers`: `string`; required=False
- `result[].final_fee`: `string`; required=False
- `result[].final_fee_after_discount`: `string`; required=False
- `result[].final_fee_discount`: `string`; required=False
- `result[].final_payBack`: `string`; required=False
- `result[].finished_at`: `string`; required=False
- `result[].light_image_url`: `string`; required=False
- `result[].liquidity_limit`: `string`; required=False
- `result[].loan`: `string`; required=False
- `result[].open_days`: `number`; required=False
- `result[].package_title`: `string`; required=False
- `result[].profit`: `string`; required=False
- `result[].profit_percentage`: `string`; required=False
- `result[].start_balance`: `string`; required=False
- `result[].status`: `string`; required=False
- `result[].total_days`: `number`; required=False
- `result[].user_id`: `number`; required=False
- `result[].warning_limit`: `string`; required=False
- `result_info`: `object`; required=False
- `result_info.count`: `number`; required=False
- `result_info.page`: `number`; required=False
- `result_info.per_page`: `number`; required=False
- `result_info.total_count`: `number`; required=False
- `success`: `boolean`; required=False

### `GET /v1/prop/user/packages/history/{subAccountClientId}`

Operation ID: `userPackageHistoryDetails`

- Parameter `subAccountClientId`; in=path; required=True; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.applicable_daily_fee`: `string`; required=False
- `result.applicable_daily_fee_after_discount`: `string`; required=False
- `result.applicable_daily_fee_discount`: `string`; required=False
- `result.assurance`: `string`; required=False
- `result.client_id`: `string`; required=False
- `result.close_reason`: `string`; required=False
- `result.created_at`: `string`; required=False
- `result.currency`: `string`; required=False
- `result.daily_fee`: `string`; required=False
- `result.daily_fee_after_discount`: `string`; required=False
- `result.daily_fee_discount`: `string`; required=False
- `result.dark_image_url`: `string`; required=False
- `result.destination_currency`: `string`; required=False
- `result.expire_at`: `string`; required=False
- `result.expire_days`: `number`; required=False
- `result.final_assurance`: `string`; required=False
- `result.final_balance`: `string`; required=False
- `result.final_balance_without_transfers`: `string`; required=False
- `result.final_fee`: `string`; required=False
- `result.final_fee_after_discount`: `string`; required=False
- `result.final_fee_discount`: `string`; required=False
- `result.final_payBack`: `string`; required=False
- `result.finished_at`: `string`; required=False
- `result.light_image_url`: `string`; required=False
- `result.liquidity_limit`: `string`; required=False
- `result.loan`: `string`; required=False
- `result.open_days`: `number`; required=False
- `result.package_title`: `string`; required=False
- `result.profit`: `string`; required=False
- `result.profit_percentage`: `string`; required=False
- `result.start_balance`: `string`; required=False
- `result.status`: `string`; required=False
- `result.total_days`: `number`; required=False
- `result.user_id`: `number`; required=False
- `result.warning_limit`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/prop/user/packages/overview`

Operation ID: `activeUserPackagesOverview`


Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.aggregatedDetail`: `object`; required=False
- `result.aggregatedDetail.assurance`: `string`; required=False
- `result.aggregatedDetail.currency`: `string`; required=False
- `result.aggregatedDetail.loan`: `string`; required=False
- `result.aggregatedDetail.profit`: `string`; required=False
- `result.aggregatedDetail.profitPercentage`: `string`; required=False
- `result.userPackages`: `array`; required=False
- `result.userPackages[].balancesHistory`: `object`; required=False
- `result.userPackages[].balancesHistory.perDay`: `object`; required=False
- `result.userPackages[].balancesHistory.perDay.2025-04-06`: `object`; required=False
- `result.userPackages[].balancesHistory.perDay.2025-04-06.BTC`: `number`; required=False
- `result.userPackages[].balancesHistory.perDay.2025-04-06.TMN`: `number`; required=False
- `result.userPackages[].balancesHistory.perDay.2025-04-06.USDT`: `number`; required=False
- `result.userPackages[].balancesHistory.total`: `object`; required=False
- `result.userPackages[].balancesHistory.total.BTC`: `number`; required=False
- `result.userPackages[].balancesHistory.total.TMN`: `number`; required=False
- `result.userPackages[].balancesHistory.total.USDT`: `number`; required=False
- `result.userPackages[].packageDetail`: `object`; required=False
- `result.userPackages[].packageDetail.assurance`: `string`; required=False
- `result.userPackages[].packageDetail.currency`: `string`; required=False
- `result.userPackages[].packageDetail.darkImageUrl`: `string`; required=False
- `result.userPackages[].packageDetail.expireDays`: `number`; required=False
- `result.userPackages[].packageDetail.lightImageUrl`: `string`; required=False
- `result.userPackages[].packageDetail.loan`: `string`; required=False
- `result.userPackages[].packageDetail.title`: `string`; required=False
- `result.userPackages[].userPackageDetail`: `object`; required=False
- `result.userPackages[].userPackageDetail.createdAt`: `string`; required=False
- `result.userPackages[].userPackageDetail.expireAt`: `string`; required=False
- `result.userPackages[].userPackageDetail.id`: `number`; required=False
- `result.userPackages[].userPackageDetail.profit`: `string`; required=False
- `result.userPackages[].userPackageDetail.profitPercentage`: `string`; required=False
- `result.userPackages[].userPackageDetail.status`: `string`; required=False
- `result.userPackages[].userPackageDetail.subAccountClientId`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/prop/user/packages/active`

Operation ID: `activeUserPackageDetails`

- Parameter `sub-account-client-id`; in=header; required=False; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.alertsData`: `array`; required=False
- `result.alertsData[].type`: `string`; required=False
- `result.balancesHistory`: `object`; required=False
- `result.balancesHistory.perDay`: `object`; required=False
- `result.balancesHistory.perDay.2025-04-06`: `object`; required=False
- `result.balancesHistory.perDay.2025-04-06.BTC`: `number`; required=False
- `result.balancesHistory.perDay.2025-04-06.TMN`: `number`; required=False
- `result.balancesHistory.perDay.2025-04-06.USDT`: `number`; required=False
- `result.balancesHistory.total`: `object`; required=False
- `result.balancesHistory.total.BTC`: `number`; required=False
- `result.balancesHistory.total.TMN`: `number`; required=False
- `result.balancesHistory.total.USDT`: `number`; required=False
- `result.packageDetail`: `object`; required=False
- `result.packageDetail.assurance`: `string`; required=False
- `result.packageDetail.currency`: `string`; required=False
- `result.packageDetail.dailyFee`: `string`; required=False
- `result.packageDetail.dailyFeeAfterDiscount`: `string`; required=False
- `result.packageDetail.dailyFeeDiscount`: `string`; required=False
- `result.packageDetail.darkImageUrl`: `string`; required=False
- `result.packageDetail.destination_currency`: `unspecified`; required=False
- `result.packageDetail.expireDays`: `number`; required=False
- `result.packageDetail.id`: `number`; required=False
- `result.packageDetail.lightImageUrl`: `string`; required=False
- `result.packageDetail.loan`: `string`; required=False
- `result.packageDetail.startBalance`: `string`; required=False
- `result.packageDetail.title`: `string`; required=False
- `result.userPackageDetail`: `object`; required=False
- `result.userPackageDetail.connectToWallet`: `unspecified`; required=False
- `result.userPackageDetail.createdAt`: `string`; required=False
- `result.userPackageDetail.cyclesCount`: `number`; required=False
- `result.userPackageDetail.debtCyclesCount`: `number`; required=False
- `result.userPackageDetail.expireAt`: `string`; required=False
- `result.userPackageDetail.finalFee`: `string`; required=False
- `result.userPackageDetail.finalFeeAfterDiscount`: `string`; required=False
- `result.userPackageDetail.finalPayableFeeAmount`: `string`; required=False
- `result.userPackageDetail.finalPayback`: `string`; required=False
- `result.userPackageDetail.id`: `number`; required=False
- `result.userPackageDetail.liquidityLimit`: `string`; required=False
- `result.userPackageDetail.openDays`: `number`; required=False
- `result.userPackageDetail.paidCyclesCount`: `number`; required=False
- `result.userPackageDetail.profit`: `string`; required=False
- `result.userPackageDetail.profitPercentage`: `string`; required=False
- `result.userPackageDetail.status`: `string`; required=False
- `result.userPackageDetail.totalDays`: `number`; required=False
- `result.userPackageDetail.type`: `string`; required=False
- `result.userPackageDetail.warningLimit`: `string`; required=False
- `success`: `boolean`; required=False

### `GET /v1/prop/user/packages/{id}/check-availability`

Operation ID: `checkPropPackageAvailability`

- Parameter `id`; in=path; required=True; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `array`; required=False
- `result[].isValid`: `boolean`; required=False
- `result[].key`: `string`; required=False
- `success`: `boolean`; required=False

### `POST /v1/prop/user/packages`

Operation ID: `activateUserPackage`


Request content: `application/json`
- `prop_package_id`: `number`; required=False

Response status codes: `201`

Response `201` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.clientId`: `string`; required=False
- `result.createdAt`: `string`; required=False
- `result.darkAvatarUrl`: `string`; required=False
- `result.isActive`: `boolean`; required=False
- `result.isSuspend`: `boolean`; required=False
- `result.lightAvatarUrl`: `string`; required=False
- `result.title`: `string`; required=False
- `result.type`: `string`; required=False
- `result.userId`: `string`; required=False
- `success`: `boolean`; required=False

### `DELETE /v1/prop/user/packages`

Operation ID: `cancelUserPackage`

- Parameter `sub-account-client-id`; in=header; required=False; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.client_id`: `string`; required=False
- `result.currency`: `string`; required=False
- `result.final_balance`: `string`; required=False
- `result.final_balance_without_transfers`: `string`; required=False
- `result.prop_package_id`: `number`; required=False
- `result.start_balance`: `string`; required=False
- `result.user_id`: `string`; required=False
- `success`: `boolean`; required=False

### `POST /v1/prop/user/packages/connect-to-wallet`

Operation ID: `enableConnectToWallet`

- Parameter `sub-account-client-id`; in=header; required=False; type=string

Request content: `application/json`
- `credit`: `string`; required=False
- `currency`: `string`; required=False
- `usageCount`: `number`; required=False

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `object`; required=False
- `result.credit`: `string`; required=False
- `result.currency`: `string`; required=False
- `result.status`: `string`; required=False
- `result.usageCount`: `number`; required=False
- `result.usedCount`: `number`; required=False
- `success`: `boolean`; required=False

### `DELETE /v1/prop/user/packages/connect-to-wallet`

Operation ID: `disableConnectToWallet`

- Parameter `sub-account-client-id`; in=header; required=False; type=string

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `array`; required=False
- `success`: `boolean`; required=False

### `POST /v1/prop/user/packages/enable-renew`

Operation ID: `enableUserPackageRenew`

- Parameter `sub-account-client-id`; in=header; required=False; type=string

Request content: `application/json`

Response status codes: `200`

Response `200` / `application/json` fields:

- `message`: `string`; required=False
- `result`: `array`; required=False
- `success`: `boolean`; required=False
