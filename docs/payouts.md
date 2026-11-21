# Payouts: process and records

This is the operations runbook for paying ADT contributors. It covers the weekly
cycle, who approves what, what we record, and what to do when a payment fails. Platform
choice and current fees are in [`payout-platforms.md`](payout-platforms.md).

**Policy (see [CONTRIBUTING.md](../CONTRIBUTING.md)):**
- **$20** per approved paid task.
- Work approved **Monday–Sunday** is paid **by the following Wednesday**.
- First payout run: **Wednesday 6 January 2027**, covering everything approved before then.
- Contributors share payout details **once, privately**, after their first approved task.
  Payout details must **never** be posted in a public issue, PR, discussion or chat.

This document describes a process; it does **not** authorise or make any payment. Only
maintainers with access to the payout accounts execute transfers.

## Roles and separation of duties

| Role | Responsibility |
| --- | --- |
| Reviewer | Checks a delivery against the task's "Done when" list and marks it **approved**. A reviewer does not enter or edit payout details. |
| Payout operator | Collects the approved list, prepares and executes transfers in the payout platform. |
| Second maintainer (approver) | Independently checks the batch (recipient, amount, total) and approves it before transfers are sent. For small batches the same person may not both prepare and approve — a second set of eyes is required. |
| Record keeper | Maintains the payout register and attaches proof. Usually the payout operator, checked by the approver. |

One person must never be the only one who can both **change payout details** and
**release money**. Maintainers rotate the operator role so no single person holds it
forever.

## The private payout-details form

- Form file: [`payout-form.html`](../payout-form.html). It reuses `adt.js` for the African
  phone-country picker and validation.
- Configuration: [`payout-config.js`](../payout-config.js). The public repo contains
  **placeholders only**. Maintainers set the real endpoint and enable the form in their
  **private deployment**; real endpoints/codes are never committed.
- Access: the form is shared **privately** (unlisted link + invite code) with a
  contributor only after their first approved task. It is not linked from the public
  site navigation. See [Setting up the private form](#setting-up-the-private-form).

The form collects only what is needed to pay someone:

- full name, email and African phone number;
- payout country;
- payout method — **mobile money** (network + wallet number) or **bank** (bank name +
  account number);
- the private **invite code**;
- a confirmation that the details belong to the contributor.

**Never** ask for, store or send: passwords, PINs, OTPs, card numbers, seed phrases,
private keys, or exchange/wallet logins. If someone sends one by mistake, delete it,
tell them not to reuse it, and note the incident in the register.

Contributors may update their details by submitting the form again with their existing
invite code; the newest submission wins. When in doubt, confirm a change out-of-band
(SMS/WhatsApp to the known number) before paying a changed destination.

## Weekly cycle

### Monday — collect and verify approvals

1. Pull the list of tasks approved in the previous Mon–Sun window from ADT Work/review
   records. For each: task id, contributor name, GitHub/ADT Work handle, approval date,
   amount ($20).
2. Check each contributor has submitted payout details via the private form. Chase those
   who have not; do not put them in this week's batch until details are complete.
3. Check for duplicate approvals (the same task paid twice) and for contributors whose
   details changed recently — flag them for out-of-band confirmation.

### Tuesday — prepare the batch

1. Open the **payout register** (a maintainers-only spreadsheet or the private repo,
   never a public file). Create a row per payment with:
   `payment_id`, `task_id`, `contributor`, `amount_usd`, `country`, `payout_method`,
   `destination_masked`, `platform`, `fx_rate`, `fee`, `status`, `operator`,
   `prepared_at`, `approved_by`, `sent_at`, `provider_reference`, `proof_link`, `notes`.
2. Choose the platform per [`payout-platforms.md`](payout-platforms.md) — normally
   Paystack (NG/GH/KE), Flutterwave (elsewhere). Confirm the live fee and rate for $20
   and record them.
3. Fund the local balance through Wise with a small buffer for fees. Record the funding
   transfer's provider reference.
4. Build the batch file (Paystack/Flutterwave support bulk CSV/API). **Mask** account
   numbers in the register (last 4 digits only); full details stay in the platform.
5. The operator sends the batch to the second maintainer for approval. **No transfers
   are executed before approval.**

### Wednesday — approve and pay

1. The approver checks, independently of the prepared file:
   - every payment maps to one approved task (no duplicates, no unapproved work);
   - amount is $20 per task;
   - total = number of payments × $20 + expected fees;
   - destinations match the newest form submission (masked comparison is enough);
   - the batch contains no cash-pickup or unusual-corridor exceptions unless approved.
2. Approver records `approved_by` and a timestamp in the register.
3. Operator executes the batch in the platform. Attach the batch/provider references and
   a screenshot or exported receipt to `proof_link`.
4. Operator marks each row `sent` with `sent_at` and `provider_reference`.

### Thursday — reconcile and notify

1. Confirm in each platform that transfers are `successful`, not merely `pending`.
2. Reconcile: funding amount = paid amounts + fees + remaining balance. Investigate any
   difference before closing the week.
3. Mark the week's register tab **closed** and keep the proof files.
4. Post a short, **public** note that the weekly run is complete (never include names,
   amounts, destinations or references). Tell contributors individually that their payout
   was sent, using their known contact channel.

## Approvals

- A task is payable only after a reviewer marks it **approved** against its "Done when"
  checklist. Self-approval of your own delivery is not allowed.
- A payout batch needs a second maintainer's approval before execution. Record who
  approved and when.
- Any exception — different amount, uncovered country, cash pickup, stale/changed payout
  details — needs an explicit maintainer decision recorded in `notes` before sending.
- Never bypass approvals for urgency. A late payment is recoverable; a wrong-destination
  payment usually is not.

## Records and retention

- The **payout register** is the single source of truth. Keep it in a maintainers-only
  location with access limited to the operator/approver group; do not commit it to this
  public repo.
- Store per payment: task id, contributor, masked destination, amount, currency, FX rate,
  fee, platform, provider reference, status, timestamps, operator, approver, proof.
- Keep platform receipts/batch exports and the register for **at least 7 years** (a
  conservative default; local rules may require longer).
- Keep a dated note of the fee/rate check for each corridor used (from the live quote),
  so fee changes are traceable.
- Do not store full bank/wallet numbers, passwords, PINs, seed phrases or private keys in
  the register, in issues, in chat or in git.
- Revoke an operator's access to the payout platforms and the register within a day of
  them leaving the maintainer team.

## When a payment fails

Treat a failure as **unresolved money**, not as "try again until it works". Repeated blind
retries can double-pay.

1. **Stop and mark the row `failed`** with the provider's error code/message. Do not
   immediately resend.
2. **Identify the cause** in the platform: wrong or masked-destination mismatch,
   invalid account/wallet number, unsupported corridor, insufficient balance, KYC/wallet
   limit, expired invite code, or a temporary provider/network error.
3. **Check the money's state** in the platform (pending / reversed / returned). Do not
   resend while a transfer is still pending — it may still land.
4. **Fix the data, not the symptom.** If the destination was wrong, ask the contributor
   to resubmit the private form and confirm the new details out-of-band. If it was a
   wallet limit, split or use a bank route. If funds were reversed, confirm the reversal
   in the balance before retrying.
5. **Get approval** for the retry/correction and record it in `notes`. Reference the
   original `provider_reference` so the two rows are linked.
6. **Retry once**, with a unique reference. If it fails again, escalate to a second
   platform or a maintainer decision — do not loop.
7. **If money is stuck or lost**, open a support ticket with the provider, keep the
   ticket id in the register, and tell the contributor honestly that the payment is
   delayed and being traced. Pay the contributor from the next run if ADT decides the
   loss is ours, and record that as a separate adjustment (never hide it).
8. **After resolution**, set the row to `paid`, `failed-then-paid` or `cancelled`, attach
   the evidence, and add a one-line "what we learned" so the runbook can be improved.

Common failure quick-reference:

| Symptom | Likely cause | First action |
| --- | --- | --- |
| `invalid account / recipient` | Typo or stale details | Resubmit form + out-of-band confirm |
| `insufficient balance` | Funding/FX shortfall | Top up via Wise; record funding reference |
| `pending` for days | Provider or partner delay | Check status, do not resend; open ticket if >3 business days |
| `reversed / returned` | Rejected by receiving bank/wallet | Confirm the credit to the balance, then correct and retry |
| `wallet limit exceeded` | KYC tier cap (common in GH) | Use bank route or smaller split with approval |
| `duplicate reference` | Retry with same id | Use a new unique reference; check if the first landed |

## Setting up the private form

This is a one-time maintainer task. The goal is that **only maintainers can read
submissions** and that the form is not discoverable from the public site.

1. Create a form backend that notifies a maintainers-only destination — e.g. a Formspree
   form with email notifications to a private mailbox, a Fillout/Tally form restricted
   to specific people, or a small server/worker you control. Enable server-side
   validation of the **invite code** so random submissions are ignored.
2. In your **private deployment** of the site (not the public repo), edit
   `payout-config.js`: set `PAYOUT_FORM_ENDPOINT` to the backend URL and
   `PAYOUT_FORM_ENABLED` to `true`. Keep real values out of git.
3. Host `payout-form.html` at an unlisted path, or behind HTTP basic auth / a Cloudflare
   Pages access rule. Do not add it to the site navigation or link it publicly.
4. Generate a random invite code (e.g. 16+ characters). Store it with the maintainers.
   Rotate it if it leaks. The code is *not* a substitute for server-side access control.
5. Share the unlisted link **and** the invite code privately with a contributor only
   after their first approved task — via their confirmed phone number or email, never in
   a public issue/PR/discussion.
6. Test with a dummy submission: confirm the maintainer destination receives it, that a
   wrong invite code is rejected, and that the browser shows the success message.
7. Review access monthly: who can read submissions, who can read the register, who can
   execute transfers. Revoke access for departed maintainers.

> Note: a static site cannot keep a secret in its source. The privacy of the form comes
> from the private backend, the unlisted/access-controlled page, and private sharing of
> the link and invite code — not from anything embedded in `payout-form.html`.

## Before the first run (6 January 2027)

- [ ] Payout accounts (Paystack, Flutterwave) verified with business/KYC documents.
- [ ] Wise funding route tested with a small transfer; fees recorded.
- [ ] Live $20 fees/rates confirmed per corridor and saved in the register.
- [ ] Private form deployed, invite code generated, dummy submission tested.
- [ ] Payout register created with restricted access; approver named.
- [ ] Failure/escalation contacts for each platform saved.
- [ ] Dry run of the full cycle reviewed by the maintainers.
