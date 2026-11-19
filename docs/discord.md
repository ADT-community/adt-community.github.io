# ADT Community Discord Server

Welcome to the central coordination hub for the **Africa Deep Tech (ADT) Community**. The Discord server brings together developers, designers, researchers, writers, and maintainers from across Africa to build open source products that solve African problems—and get paid for their contributions.

- **Discord Server Invite:** [https://discord.gg/adt-community](https://discord.gg/adt-community)
- **ADT Community Website:** [https://adt-community.github.io](https://adt-community.github.io)
- **ADT Work (Task Board):** [https://adt-community.github.io/work.html](https://adt-community.github.io/work.html)
- **GitHub Organization:** [https://github.com/ADT-community](https://github.com/ADT-community)

---

## 1. Channel Structure and Layout

The server is organized into clear categories to ensure focused conversations, seamless onboarding, and high visibility for open tasks.

### 📢 Information & Onboarding

| Channel | Purpose | Permissions |
| :--- | :--- | :--- |
| `#welcome` | Welcome message for new members, server navigation, and quick-start links. | Read-only for members; Core team posts |
| `#announcements` | Major community news, release updates, and the **Weekly Update** every week. | Read-only for members; Maintainers post |
| `#how-we-pay` | Comprehensive instructions on bounty rewards, payout schedules, payment methods (mobile money / bank), and the strict privacy process. | Read-only for members; pinned guidance |
| `#rules` | Server rules and expectations imported directly from `CODE_OF_CONDUCT.md`. | Read-only for members; verification gate |

### 🎯 Bounty Feed

| Channel | Purpose | Permissions |
| :--- | :--- | :--- |
| `#bounties` | **Automated Bounty Feed**: The ADT Bounty Bot streams newly published tasks and bounties here directly from GitHub issues across all ADT repositories. | Automated bot postings; threaded discussions enabled |

### 🛠️ Flagship Projects (One per Project)

Each project repository has a dedicated channel where contributors, maintainers, and reviewers discuss implementations, architecture, bug reports, and pull requests.

| Channel | Project Repo | Description |
| :--- | :--- | :--- |
| `#trans_sport` | [ADT-community/trans_sport](https://github.com/ADT-community/trans_sport) | **Minibus app**: Uber-style convenience for African minibuses (route, fare, GPS, and arrival tracking). |
| `#locallity_ai` | [ADT-community/locallity_ai](https://github.com/ADT-community/locallity_ai) | **Local-language AI**: AI platform that speaks African languages via voice and text across apps and WhatsApp/SMS. |
| `#content_feed` | [ADT-community/content_feed](https://github.com/ADT-community/content_feed) | **Creator social app**: Short-form video and posts that pay African creators via mobile money. |
| `#adt_agent` | [ADT-community/ADT_agent](https://github.com/ADT-community/ADT_agent) | **ADT agent**: Autonomous AI agent coordinating repository tasks, tracking bounties, and monitoring progress. |
| `#trader` | [ADT-community/trader](https://github.com/ADT-community/trader) | **Quant trading lab**: Automated trading strategies and market analysis infrastructure. |
| `#community-site` | [ADT-community/adt-community.github.io](https://github.com/ADT-community/adt-community.github.io) | **ADT Community & Work Board**: The main website, task board, documentation, and proposal portal. |

### 💡 Community & Support

| Channel | Purpose | Permissions |
| :--- | :--- | :--- |
| `#ideas` | Brainstorming new product ideas, technical concepts, and feedback before submitting formal project proposals. | Open to all members |
| `#help` | Getting unstuck: GitHub and git support, pull request troubleshooting, development environment setup, and peer mentorship. | Open to all members |
| `#general` | General African tech discussions, introductions, wins, and community networking. | Open to all members |

---

## 2. Server Rules & Code of Conduct

All members must adhere to the community standards established in [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md).

### Expected Behaviour
- **Be respectful and patient**, especially with newcomers taking their first steps in open source.
- **Give constructive feedback on work, not on people.** Focus on code quality, design usability, and problem solving.
- **Credit others' contributions honestly.** Acknowledge co-authors and collaborators.
- **Keep discussions on topic** in the appropriate project and topic channels.

### Not Acceptable
- **Harassment, insults, or discrimination** of any kind, including based on nationality, ethnicity, tribe, religion, gender, or language.
- **Plagiarism or gaming**: Claiming someone else's work as your own or gaming the bounty / points system.
- **Sharing private information**: Never share personal phone numbers, bank accounts, or payment credentials in public channels.
- **Spam or unsolicited self-promotion**: Direct messaging members with spam or unrelated marketing is prohibited.

### Strict Payment Privacy Policy
- **Never share bank account numbers, mobile money numbers, or payment identifiers in public channels or issues.**
- After your first pull request is merged, a maintainer will contact you privately through secure off-channel communication to collect payout credentials once.

### Enforcement
- Violations can be reported to a maintainer or moderator privately by DM or by emailing community moderation.
- Penalties include formal warnings, removal of content, disqualification from bounties earned in bad faith, and permanent server/organization bans.

---

## 3. How We Pay: Channel Content (`#how-we-pay`)

The `#how-we-pay` channel is pinned with the following exact policy:

```markdown
# Getting Paid at ADT Community

We believe in open source that pays creators. Here is how earning works:

### 1. Two Ways to Earn
- **Bounties ($20 fixed in the current wave):** Fixed reward for scoped tasks (2–5 hours). The price is agreed before work starts and is paid upon pull request merge.
- **Goals:** Milestone rewards for larger achievements (e.g. MVP launch, first 1,000 users) divided among agreed team contributors.

### 2. How to Claim a Task
1. Browse open tasks on the website task board (https://adt-community.github.io/work.html) or the `#bounties` Discord feed.
2. Open the GitHub issue and comment: `"I'd like to take this"`.
3. Wait to be assigned by a maintainer before starting work.
4. Deliver your PR or draft within 5 days (maximum 14 days).

### 3. Weekly Payout Run
- Work merged **Monday through Sunday** is paid by the following **Wednesday**.
- Payouts start in **January 2027** (first run: **Wednesday, 6 January 2027**). Work merged before then is recorded and paid in that inaugural run, and weekly thereafter.
- Payout methods: **Mobile Money** (M-Pesa, MTN MoMo, Airtel Money, Orange Money) or direct **Bank Transfer**.

### 4. Privacy Rule
- NEVER post your phone number, mobile money details, or bank account in any public channel or GitHub issue.
- Maintainers collect payout details once privately after your first PR merge.
```

---

## 4. Roles and Permissions Hierarchy

| Role | Color | Responsibilities |
| :--- | :--- | :--- |
| **Maintainer / Core** | Gold (`#F1C40F`) | Repository owners, code reviews, PR merges, Discord moderation, and payout processing. |
| **Contributor** | Green (`#2ECC71`) | Active community members who have claimed or delivered bounties. |
| **Partner** | Blue (`#3498DB`) | Startups and teams posting paid tasks and funding bounties on ADT Work. |
| **Bot** | Purple (`#9B59B6`) | Automated integrations including the ADT Bounty Feed Bot. |
| **Community Member** | Light Gray (`#BDC3C7`) | General members, aspiring contributors, and learners. |

---

## 5. Automated Bounty Feed Bot

The `#bounties` channel is powered by the **ADT Bounty Feed Bot** (`bot/bounty_bot.py`), which bridges GitHub issues to Discord.

### How It Works
```
+---------------------------+        +--------------------------+        +-----------------------+
|  GitHub Repositories      |        |   ADT Bounty Feed Bot    |        |   Discord Channel     |
|  - Issue opened / labeled |  --->  |   - Parse deliverable    |  --->  |   #bounties           |
|    with `bounty`          |        |   - Format rich embed    |        |   (Rich Webhook Embed)|
+---------------------------+        +--------------------------+        +-----------------------+
```

### Discord Embed Appearance
Each new bounty post contains:
- **Title:** `🎯 New Task: <Title>` (linked directly to the GitHub issue)
- **Color:** Emerald Green for paid bounties; Royal Blue for next-wave tasks
- **Fields:**
  - 💰 **Reward:** `$20` (or labeled amount)
  - 📦 **Project:** Project title and repo name (e.g. `Minibus app (trans_sport)`)
  - 🏷️ **Type:** Code, Design, Research, or Operations
  - 🎯 **Level:** Beginner / Intermediate
  - ⏱️ **Time:** Estimated hours (e.g. `2–5 hours`)
  - 📌 **Status:** Open for claim
  - 🚀 **How to claim:** Instructions to comment on GitHub to be assigned
- **Footer:** `ADT Community • Build for Africa. Get paid.`

### Bot Setup Instructions
1. In Discord:
   - Go to `#bounties` channel settings -> **Integrations** -> **Webhooks**.
   - Click **Create Webhook**, name it `ADT Bounty Feed`, and copy the Webhook URL.
2. In GitHub:
   - Go to repository **Settings** -> **Secrets and variables** -> **Actions**.
   - Add a repository secret named `DISCORD_WEBHOOK_URL` with the webhook URL value.
3. Automated Action:
   - The bot workflow at `.github/workflows/bounty-feed.yml` runs automatically whenever a new issue is opened or labeled with `bounty`.
4. Manual or Scheduled Run:
   - Scan all ADT repositories locally or in cron:
     ```bash
     python3 -m bot.bounty_bot scan --webhook-url "$DISCORD_WEBHOOK_URL"
     ```
   - Dry-run mode (outputs to console without making network calls):
     ```bash
     python3 -m bot.bounty_bot scan --dry-run
     ```

---

## 6. Weekly Update Habit

Momentum is visible when a community ships every week. Every Wednesday alongside the payout run:
1. The maintainers publish the week's update in [`docs/updates/`](updates/).
2. A summary is posted to the `#announcements` channel on Discord and pinned for the week.
3. The update follows the standard template:
   - **Shipped:** What was merged and launched
   - **Paid:** Payouts processed and contributors rewarded
   - **New tasks:** Fresh bounties available to claim
   - **Next:** Priorities for the coming week
