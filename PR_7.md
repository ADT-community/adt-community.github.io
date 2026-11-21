## Summary

Implements the payout operations deliverable from issue #7: a platform recommendation, a private payout-details form, and a documented weekly process. No money is moved by this PR.

- `docs/payout-platforms.md` — comparison of payout options for **$20** transfers to mobile money and bank accounts in Nigeria, Ghana, Kenya and elsewhere, with 2026 fees, speed and country coverage. Recommendation: **Paystack** (NG/GH/KE, flat local fees) + **Flutterwave** (wider African coverage) for the weekly batch, funded through **Wise** at the mid-market rate; WorldRemit/Remitly/Africa-focused apps only as exceptions. Includes per-country fee tables and a "what to check before a run" list.
- `payout-form.html` — a ready-to-deploy payout-details form. Collects name, email, African phone (reusing `adt.js` validation), payout country, method (mobile money or bank, with conditional fields), a private invite code and consent. It contains **no endpoints or secrets** and is disabled by default.
- `payout-config.js` — placeholders for the private deployment (`PAYOUT_FORM_ENABLED`, `PAYOUT_FORM_ENDPOINT`). Real values are deliberately not committed: the site is public.
- `docs/payouts.md` — the runbook: roles/separation of duties, the private form and how it is shared, the Mon–Wed–Thu weekly cycle, approval rules, the payout register and retention, and a failure/escalation procedure with a quick-reference table. Includes a pre-launch checklist for the first run on 6 January 2027.
- `CONTRIBUTING.md` / `README.md` — links to the new docs and to the private form.

### Acceptance criteria

- [x] Platform recommendation with fees — `docs/payout-platforms.md`
- [x] Form ready (deployable template + private setup/shared-link procedure in `docs/payouts.md`) — `payout-form.html`, `payout-config.js`
- [x] Process documented — `docs/payouts.md`

**Operational note:** the last step of "Form ready" (hosting on a private URL and sharing the link/invite code with each contributor) can only be done by maintainers with their own form backend and accounts. This PR delivers the complete form and the exact setup checklist; it intentionally commits no credentials, endpoints or invite codes.

## Tests

No test framework or CI exists in this repository. Validation run locally:

- `node --check` on all `.js` files and on the inline scripts extracted from every `.html` page (including the new `payout-form.html`) — **all passed**.
- HTML structure check (balanced tags, all DOM ids referenced by JS exist) for all 8 pages — **passed**.
- Relative Markdown link check across all `.md` files — **all links resolve** (13 checked).

Closes #7
