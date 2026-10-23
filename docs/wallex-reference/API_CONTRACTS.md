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

### `POST /v1/account/ibans`

Operation ID: `addAccountIban`

- Parameter `body`; in=body; required=True; type=unspecified
- `$` → `#/definitions/AddIbanRequest`

Response status codes: `200`

### `GET /v1/account/ibans`

Operation ID: `getAccountIbans`

- Parameter `per_page`; in=query; required=False; type=integer
- Parameter `page`; in=query; required=False; type=integer

Response status codes: `200`

### `POST /v1/account/money-withdrawal`

Operation ID: `createMoneyWithdrawal`

- Parameter `body`; in=body; required=True; type=unspecified
- `$` → `#/definitions/MoneyWithdrawalRequest`

Response status codes: `201`

### `GET /v1/account/card-numbers`

Operation ID: `getAccountCardNumbers`


Response status codes: `200`

### `GET /v1/account/fee`

Operation ID: `getAccountFees`


Response status codes: `200`

### `GET /v1/trades`

Operation ID: `getLatestTrades`

- Parameter `symbol`; in=query; required=True; type=string

Response status codes: `200`

### `GET /hector/web/v1/markets`

Operation ID: `getMarkets`


Response status codes: `200`

### `GET /v1/depth`

Operation ID: `getMarketDepth`

- Parameter `symbol`; in=query; required=True; type=string

Response status codes: `200`

### `GET /v1/account/balances`

Operation ID: `getAccountBalances`


Response status codes: `200`

### `GET /v1/udf/history`

Operation ID: `candleHistory`

- Parameter `symbol`; in=query; required=True; type=string
- Parameter `resolution`; in=query; required=True; type=string
- Parameter `from`; in=query; required=True; type=integer
- Parameter `to`; in=query; required=True; type=integer

Response status codes: `200`

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

### `GET /margin-trade/v1/positions`

Operation ID: `getPositions`

- Parameter `active`; in=query; required=False; type=boolean
- Parameter `position_side`; in=query; required=False; type=string
- Parameter `market`; in=query; required=False; type=string

Response status codes: `200`, `408`, `500`

### `POST /margin-trade/v1/positions`

Operation ID: `openPosition`

- Parameter `position`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.OpenRequest`

Response status codes: `200`, `408`, `500`

### `GET /margin-trade/v1/positions/{id}`

Operation ID: `getPositionId`

- Parameter `id`; in=path; required=True; type=string

Response status codes: `200`, `404`, `408`, `500`

### `PATCH /margin-trade/v1/positions/{id}/close`

Operation ID: `closePositionId`

- Parameter `id`; in=path; required=True; type=string
- Parameter `position`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.CloseRequest`

Response status codes: `200`, `404`, `408`, `500`

### `PATCH /margin-trade/v1/positions/{id}/collateral`

Operation ID: `editColateral`

- Parameter `id`; in=path; required=True; type=string
- Parameter `update`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.AddCollateralRequest`

Response status codes: `200`, `404`, `408`, `500`

### `POST /margin-trade/v1/positions/{id}/profit`

Operation ID: `profitPositionID`

- Parameter `id`; in=path; required=True; type=string
- Parameter `request`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.CalculateProfitRequest`

Response status codes: `200`, `404`, `408`, `500`

### `PATCH /margin-trade/v1/positions/{id}/sltp`

Operation ID: `editSltp`

- Parameter `id`; in=path; required=True; type=string
- Parameter `update`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.UpdateSLTPRequest`

Response status codes: `200`, `404`, `408`, `500`

### `POST /margin-trade/v1/public/loan`

Operation ID: `calculateLoan`

- Parameter `request`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.CalculateLoanRequest`

Response status codes: `200`, `408`, `500`

### `POST /margin-trade/v1/public/dry-run`

Operation ID: `detailedInformation`

- Parameter `position`; in=body; required=True; type=unspecified
- `$` → `#/definitions/dto.OpenRequest`

Response status codes: `200`, `408`, `500`

### `GET /margin-trade/v1/public/markets`

Operation ID: `getMarkets`


Response status codes: `200`, `408`, `500`

### `GET /margin-trade/v1/public/ratio/{market}`

Operation ID: `publicRatio`

- Parameter `market`; in=path; required=True; type=string

Response status codes: `200`, `408`, `500`

### `GET /margin-trade/v1/user/levels`

Operation ID: `?getLevels`


Response status codes: `200`, `408`, `500`

### `GET /margin-trade/v1/user/levels/{market}`

Operation ID: `getLevelsMarket`

- Parameter `market`; in=path; required=True; type=string

Response status codes: `200`, `408`, `500`

### `GET /margin-trade/v1/user/pnl`

Operation ID: `getPnl`


Response status codes: `200`, `408`, `500`

## otc-8e321a32f4509cbf103b3127bf7c9918.json

Source: https://developers.wallex.ir/assets/files/otc-8e321a32f4509cbf103b3127bf7c9918.json

[Technical schema](schemas/otc-8e321a32f4509cbf103b3127bf7c9918.json)

### `GET /v1/otc/markets`

Operation ID: `getOTCMarkets`


Response status codes: `200`

### `GET /v1/account/otc/price`

Operation ID: `getOtcPrice`

- Parameter `symbol`; in=query; required=True; type=string
- Parameter `side`; in=query; required=True; type=string

Response status codes: `200`

### `POST /v1/account/easy-trade/orders`

Operation ID: `placeEasyTradeOrder`

- Parameter `body`; in=body; required=True; type=unspecified
- `$` → `#/definitions/EasyTradeOrderRequest`

Response status codes: `201`

## spot-b9d06896d1009adc9ebc69b9a5495e7e.json

Source: https://developers.wallex.ir/assets/files/spot-b9d06896d1009adc9ebc69b9a5495e7e.json

[Technical schema](schemas/spot-b9d06896d1009adc9ebc69b9a5495e7e.json)

### `GET /hector/web/v1/markets`

Operation ID: `getMarkets`


Response status codes: `200`

### `GET /depth/all`

Operation ID: `getDepth`


Response status codes: `200`, `500`

### `GET /v1/account/openOrders`

Operation ID: `getOpenOrder`

- Parameter `symbol`; in=query; required=False; type=string
- Parameter `page`; in=query; required=False; type=integer
- Parameter `per_page`; in=query; required=False; type=integer

Response status codes: `200`, `400`, `401`, `422`

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

### `POST /v1/account/orders`

Operation ID: `postAccountOrders`

- Parameter `order`; in=body; required=True; type=unspecified
- `$` → `#/definitions/requests.CreateOrderRequest`

Response status codes: `201`, `400`, `401`, `422`

### `DELETE /v1/account/orders`

Operation ID: `deleteAccountOrders`

- Parameter `order`; in=body; required=True; type=unspecified
- `$` → `#/definitions/requests.CancelOrderRequest`

Response status codes: `200`, `400`, `401`, `422`

### `GET /v1/account/orders/{client_id}`

Operation ID: `getOrdersClient`

- Parameter `client_id`; in=path; required=True; type=string

Response status codes: `200`, `400`, `401`, `404`

### `DELETE /v1/account/orders/{client_id}`

Operation ID: `deleteOrdersClient`

- Parameter `client_id`; in=path; required=True; type=string

Response status codes: `200`, `400`, `401`, `422`
