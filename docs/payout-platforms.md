# Payout platforms: comparison and recommendation

This note compares ways to pay a **$20 bounty** to an African mobile money wallet or
bank account, and recommends what ADT should use for the weekly payout run. It supports
[`payouts.md`](payouts.md), which describes the weekly process.

**Scope of this task:** research and a recommendation only. This PR does not move any
money and does not create accounts.

All fees below were checked against public provider/comparison pages in **November 2026**.
Fees, rates and country lists change often — always confirm the live quote for the exact
amount and corridor before a payout. Compare **what the recipient gets**, not the
headline fee: a "free" transfer can hide a worse exchange rate.

## TL;DR — recommendation

1. **Primary rails: Paystack + Flutterwave business accounts.** For a weekly batch of
   $20 payouts they are by far the cheapest: local-currency *flat* fees (often under
   $0.35 on $20), support for bulk transfers, recipient records and both bank accounts
   and mobile money. Use **Paystack** where it is available (Nigeria, Ghana, Kenya) and
   **Flutterwave** for the wider set of countries ("elsewhere").
2. **Funding/FX: Wise** to move USD into the local business balances at the mid-market
   rate with an upfront, transparent fee (~1.4%), keeping a small buffer for fees.
3. **Exceptions only:** WorldRemit / Remitly / Africa-focused apps (LemFi, Grey, Chipper,
   Afriex) or Wave for a contributor in a country the primary rails do not cover, or
   when cash pickup is genuinely needed. Avoid these for routine $20 payments — their
   flat fees are a large share of a small transfer.

**Why not a single remittance app?** A $20 transfer is small. Remitly's $2.99–$3.99 fee
is 15–20% of the amount before the exchange-rate margin; Wise/WorldRemit margins are
~1–2%. Paying from a local business balance with a flat local fee keeps almost all of
the $20 for the contributor.

## The two models

| Model | Examples | Best for | Cost on $20 |
| --- | --- | --- | --- |
| **Bulk payout API** (business balance → many recipients) | Paystack Transfers, Flutterwave Transfers | The weekly run: dozens of small payouts, bank + mobile money, bulk CSV/API, audit trail | ~$0.02–$0.85 flat per payout |
| **Remittance app** (USD/EUR from abroad → one recipient) | Wise, WorldRemit, Remitly, LemFi, Grey, Chipper, Afriex | Funding the balances, and one-off payouts to uncovered countries / cash pickup | ~$0.30–$4 per transfer + FX margin |

## $20 transfers: fees, speed and coverage

Approximate local values use ~₦1,390/$, ~GH₵11.7/$ and ~KES 129/$ (Nov 2026).
"Mobile money" means wallets such as MTN MoMo, Telecel Cash, M-Pesa, Orange Money,
Wave and Airtel Money.

### Nigeria

| Provider | Method | Fee on ~$20 (≈₦27,800) | Speed | Notes |
| --- | --- | --- | --- | --- |
| **Paystack** (recommended) | Bank (NUBAN) | ₦25 (≤₦50k band) ≈ $0.02 | Same day / next day | Bulk CSV/API; cheapest option here |
| **Flutterwave** | Bank | ₦25 (₦5,001–50,000 band) ≈ $0.02 | Next day | Bulk transfers; wide coverage |
| **Wise** | Bank deposit | ~1.4% ≈ $0.28, mid-market FX | Seconds–1 day | Transparent; no cash/mobile wallet in NG |
| **LemFi** | Bank / wallet | $0 flat, ~0.8% FX ≈ $0.16 | Minutes | Africa-focused, good for small transfers |
| **Grey** | Bank | ~$1.50 + ~0.6% FX | Minutes | Africa-focused |
| **WorldRemit** | Bank / cash | Often $0–$0.99 + FX margin | Bank up to 1 h; cash minutes | Wide payout options |
| **Remitly** | Bank / cash | $2.99–$3.99 + 1.5–2.5% FX | Minutes (Express) / days (Economy) | Fee is too high for routine $20 |
| Western Union / MoneyGram | Cash pickup | $4.99–$7.99 | Minutes–2 days | Last resort only |

### Ghana

| Provider | Method | Fee on ~$20 (≈GH₵234) | Speed | Notes |
| --- | --- | --- | --- | --- |
| **Paystack** (recommended) | Mobile money | GH₵1 ≈ $0.09 | Same/next day | Flat fee; MTN MoMo, Telecel Cash, AirtelTigo |
| **Paystack** | Bank | GH₵8 ≈ $0.68 | Same/next day | Ghipss |
| **Flutterwave** | Mobile money | 1.5% ≈ GH₵3.50 ≈ $0.30 | Next day | Wide network support |
| **Flutterwave** | Bank | GH₵10 ≈ $0.85 | Next day | — |
| **Wise** | Bank deposit | ~1.4% ≈ $0.28 | Seconds–1 day | Bank only, no MoMo in GH |
| **WorldRemit / Remitly** | MoMo / bank | $0–$3.99 + FX margin | Minutes–1 day | WorldRemit mobile money is instant |
| LemFi / Chipper | Bank / wallet | $0 flat + FX margin | Minutes | Check current GH availability |

### Kenya

| Provider | Method | Fee on ~$20 (≈KES 2,580) | Speed | Notes |
| --- | --- | --- | --- | --- |
| **Paystack** (recommended) | M-Pesa B2C | KES 40 ≈ $0.31 | Same/next day | KES 1,501–20,000 band; bank KES 80 |
| **Flutterwave** | M-Pesa / bank | KES 100 ≈ $0.78 | Next day | Flat fee |
| **Wise** | Bank / M-Pesa | ~1.4% ≈ $0.28 | Seconds–1 day | One of few apps that pays M-Pesa wallet |
| **WorldRemit** | M-Pesa / bank | Often $0 + FX margin | Minutes | Strong mobile-money reach |
| **Remitly** | M-Pesa / bank | $2.99–$3.99 + FX margin | Minutes | Fee too high for $20 |

### Elsewhere (coverage to plan for)

| Provider | Countries / wallets | Indicative fee on $20 | Notes |
| --- | --- | --- | --- |
| **Flutterwave** (recommended) | 30+ African countries: Cameroon, Côte d'Ivoire, Senegal, Rwanda, Uganda, Tanzania, Sierra Leone, Zambia, Egypt, South Africa, … | Flat local fee; e.g. XAF 1,500 / RWF 500 / KES 100 / UGX 1,000 | Best single "elsewhere" rail; bank + mobile money |
| **Wave** | Senegal, Côte d'Ivoire, Mali, Burkina Faso, Ghana (verify current list) | Very low wallet-to-wallet fees | Good for Wave markets, separate onboarding |
| **WorldRemit** | 20+ countries, mobile money / cash / bank | $0–$0.99 + FX margin | Useful fallback per corridor |
| **Remitly** | 170+ countries incl. cash pickup | $2.99–$3.99 + FX margin | Use only when nothing else works |
| **Western Union / MoneyGram** | Very wide cash network | $4.99–$7.99 | Emergency cash pickup only |

## Recipient-side mobile money and bank references

- **Nigeria:** NUBAN bank account (10 digits); bank transfer and USSD are dominant.
- **Ghana:** MTN MoMo, Telecel Cash, AirtelTigo Money, or a Ghipss bank account.
  Wallets are KYC-tier capped (Bank of Ghana rules); confirm the recipient can receive
  the amount.
- **Kenya:** M-Pesa (Safaricom) or KEPS bank account. B2C M-Pesa fees are tiered by
  amount.
- **Francophone West/Central Africa:** Orange Money, Wave, MTN MoMo; often paid via
  Flutterwave or Wave rather than Paystack.

## Decision rules for the weekly run

1. Recipient in **Nigeria, Ghana or Kenya** → Paystack (cheapest, bulk, local currency).
2. Recipient in **another supported African country** → Flutterwave.
3. Need to top up balances / FX from USD → Wise (transparent mid-market rate).
4. Unsupported corridor or genuine cash-pickup need → WorldRemit, then Remitly, then
   a cash network. Get maintainer approval before using this exception.
5. Never ask a contributor for passwords, PINs, seed phrases or private keys. Payout
   details are only the details needed to receive money (see the private form).

## Rechecking these numbers

Before the first run (and whenever a corridor is added), open the provider's live quote
page for **$20** and record: fee, exchange rate, recipient amount, speed, payout methods.
Save the result as a dated row in the payout register (see `payouts.md`). The tables
above are a starting point, not a price guarantee.

## Sources (checked November 2026)

- [Flutterwave transfer pricing](https://www.flutterwave.com/tz/support/pricing/pricing-for-transfers-and-payouts) and [payout docs](https://developer.flutterwave.com/docs/payout-outflow/introduction)
- [Paystack transfer pricing](https://support.paystack.com/en/articles/2132866) and [bulk transfers](https://paystack.com/docs/transfers/bulk-transfers)
- [Wise vs Remitly 2026 cost comparison](https://transferfees.io/guides/wise-vs-remitly/)
- [Africa payment gateways 2026 (Paystack/Flutterwave/M-Pesa)](https://deepcodeinnovations.com/blog/africa-payment-gateways-2026-flutterwave-paystack-m-pesa-more/)
- [Ghana MoMo payout fees: Paystack vs Flutterwave](https://utopiagroup.io/resources/online-payments-ghana/)
- [Nigeria app fee comparison](https://lagos.cool/remittance/remitly) and [USD→NGN rates](https://www.remitbeat.com/send-money/nigeria)
- [Ghana remittance rate check, 16 Nov 2026](https://3news.com/news/diaspora/remittance-rate-check-sending-money-to-ghana-16-november-2026)
