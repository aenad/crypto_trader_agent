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
