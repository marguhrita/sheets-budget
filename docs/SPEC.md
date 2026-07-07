# Target spreadsheet: Ultimate Annual Budget

Reference product: "Ultimate Annual Budget Spreadsheet" (Google Sheets, HayeCreativesCo, Etsy).
This is the spec to build against once we start generating the sheet through the MCP server —
not yet implemented, captured here for the next planning pass.

## Core behavior

- Google Sheets only (uses Sheets-native features, not portable to Excel/Numbers/Notion)
- Any currency, any start day/month/year
- Budgeting cadence is configurable: weekly, biweekly, per-paycheck, or monthly
- Recurring transactions are entered once and toggled on/off via checkbox per period
  rather than re-entered
- Up to 80 bank accounts, with balances that update automatically from transactions
- Future balance preview from planned/recurring transactions
- Reusable across years: start a new year without repurchasing/rebuilding
- Custom (sub)categories under top-level groups

## Tabs

1. **Budget Planner** — income, bills, expenses, savings, debt inputs that drive the rest
   of the workbook
2. **Smart Bill Calendar** — recurring transactions entered once, checkbox to include in
   period totals; covers income, savings, bills/subscriptions, debts
3. **Transactions Tracker** — freeform transaction log, auto-totaled, feeds budget/trackers
4. **Budget Template** — the actual weekly/biweekly/paycheck/monthly budget view
5. **Annual Dashboard** — full-year overview (charts/tables)
6. **Budget Dashboard** — income/expenses/balances/cash flow view
7. **Debt Payoff Tracker** — up to 40 debts; snowball, avalanche, or custom order
8. **Savings Tracker** — grouped savings goals and sinking funds, progress over time
9. **Net Worth Tracker** — assets vs. liabilities, computed net worth over time
10. **50/30/20 Tracker** (bonus) — needs / wants / future allocation view
11. **No Spend Tracker** (bonus) — calendar-style spend/no-spend day tracking

## Open questions for the build plan

- Generate as: a Sheets template built via Apps Script formulas/named ranges vs. plain
  values+formulas pushed through the Sheets API — affects how much of this the MCP
  `sheets` tools can do directly vs. needs a bootstrap script.
- Chart/dashboard elements (bar graphs, progress bars) may need the Sheets API's chart
  endpoints, which may exceed what `google_workspace_mcp`'s `sheets` tool tier exposes —
  check `core` vs `extended` vs `complete` tool tiers.
- Multi-account (80) and multi-debt (40) support implies templated row ranges — decide
  fixed max rows vs. dynamic sheet growth.
