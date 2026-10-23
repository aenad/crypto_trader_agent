# Wallex spot order reference

Official Swagger: https://developers.wallex.ir/assets/files/spot-b9d06896d1009adc9ebc69b9a5495e7e.json

The previously captured normalized contract is in
[spot schema](wallex-reference/schemas/spot-b9d06896d1009adc9ebc69b9a5495e7e.json).
The web reader could not reopen the remote download during this update. The
following references the captured contract; no new remote revision is claimed.

`POST /v1/account/orders` accepts JSON `requests.CreateOrderRequest` and API-key
authentication. String fields: `symbol`, `side`, `type`, `quantity`, `price`,
optional `client_id`, and applicable `stop_Price`. Only symbol/side/type are
schema-required; LIMIT operation also needs price and quantity. Quantity is BTC
units, not a Toman budget. Creation response is documented as HTTP 201.
Inspect `success`, actual order status and fills; acceptance is not execution.

The official spot introduction requires a credit-specific key and the
`sub-account-client-id` header for credit spot context. Successful balance reads
do not certify order routing. No order was submitted to verify this example.

## PowerShell: real LIMIT BUY template

Running this with valid numeric values submits a real order. PowerShell does not
load `.env` automatically: set the two environment variables privately first.
Replace the placeholders with an intentional Toman limit price and BTC quantity.
Check approved market status, precision, minimum size, funds and fees first.
Notional plus fees must remain within the authorized 500,000 TMN order cap;
total allocated capital must stay within 5,000,000 TMN. This manual example
bypasses application risk gates; the automated LIVE adapter remains disabled.

```powershell
if (-not $env:WALLEX_API_KEY -or -not $env:WALLEX_SUB_ACCOUNT_CLIENT_ID) {
    throw 'Set both Wallex environment variables privately first.'
}
$orderBody = @{
    symbol = 'BTCTMN'
    side = 'BUY'
    type = 'LIMIT'
    price = '<LIMIT_PRICE_TMN>'
    quantity = '<BTC_QUANTITY>'
    client_id = ('qp-' + [guid]::NewGuid().ToString('N'))
} | ConvertTo-Json -Compress
$orderFile = Join-Path $env:TEMP 'quantpilot-manual-order.json'
[System.IO.File]::WriteAllText($orderFile, $orderBody, [System.Text.UTF8Encoding]::new($false))
curl.exe --request POST 'https://api.wallex.ir/v1/account/orders' `
  --header "x-api-key: $env:WALLEX_API_KEY" `
  --header "sub-account-client-id: $env:WALLEX_SUB_ACCOUNT_CLIENT_ID" `
  --header 'Content-Type: application/json' `
  --header 'Accept: application/json' `
  --data-binary "@$orderFile"
```

The file avoids native JSON argument quoting issues in Windows PowerShell.
No automatic retry is configured. If a timeout occurs, preserve the original
client ID and query `GET /v1/account/orders/{client_id}` before resubmitting.
The client ID field alone does not prove exchange idempotency. LIMIT orders may
remain open or fill partially. Do not share credentials or full account responses.

Documentation only: no production adapter or LIVE authorization was changed.
