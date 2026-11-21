// Settings for the private payout-details form (payout-form.html).
//
// The public repository ships placeholders only. Maintainers set real values in their
// PRIVATE deployment and never commit them here: this site is public, so anything in
// this file can be read by anyone. The invite code is validated by the form BACKEND,
// not by this file.
//
// 1. Create a form backend that notifies a maintainers-only mailbox/channel.
// 2. Set PAYOUT_FORM_ENDPOINT to its URL, e.g. "https://formspree.io/f/xxxxxxxx".
// 3. Set PAYOUT_FORM_ENABLED to true.
// See docs/payouts.md ("Setting up the private form") for the full checklist.

const PAYOUT_FORM_ENABLED = false;
const PAYOUT_FORM_ENDPOINT = "";
