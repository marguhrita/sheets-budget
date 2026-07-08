"""
Creates a new Google Sheet with the three core budgeting tabs (Budget
Planner, Smart Bill Calendar, Transactions Tracker) as defined in
docs/SPEC.md. Run once per new spreadsheet; re-run to create another one.

Usage:
    python scripts/build_budget.py ["Spreadsheet Title"]
"""

import sys

from dotenv import load_dotenv
from googleapiclient.discovery import build

from google_auth import get_credentials

MONTH_COLUMNS = ["E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

BUDGET_PLANNER_ENTRY_ROWS = (11, 110)   # 1-indexed, inclusive
BILL_CALENDAR_ENTRY_ROWS = (4, 53)
TRANSACTIONS_ENTRY_ROWS = (4, 203)


def bold_header_request(sheet_id: int, start_row: int, end_row: int, end_col: int, shaded: bool):
    cell_format = {"textFormat": {"bold": True}}
    if shaded:
        cell_format["backgroundColor"] = {"red": 0.92, "green": 0.93, "blue": 0.95}
    return {
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": start_row - 1,
                "endRowIndex": end_row,
                "startColumnIndex": 0,
                "endColumnIndex": end_col,
            },
            "cell": {"userEnteredFormat": cell_format},
            "fields": "userEnteredFormat(textFormat,backgroundColor)",
        }
    }


def freeze_rows_request(sheet_id: int, count: int):
    return {
        "updateSheetProperties": {
            "properties": {"sheetId": sheet_id, "gridProperties": {"frozenRowCount": count}},
            "fields": "gridProperties.frozenRowCount",
        }
    }


def list_validation_request(sheet_id: int, start_row: int, end_row: int, col_index: int, values: list[str]):
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": start_row - 1,
                "endRowIndex": end_row,
                "startColumnIndex": col_index,
                "endColumnIndex": col_index + 1,
            },
            "rule": {
                "condition": {
                    "type": "ONE_OF_LIST",
                    "values": [{"userEnteredValue": v} for v in values],
                },
                "showCustomUi": True,
                "strict": True,
            },
        }
    }


def checkbox_validation_request(sheet_id: int, start_row: int, end_row: int, start_col: int, end_col: int):
    return {
        "setDataValidation": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": start_row - 1,
                "endRowIndex": end_row,
                "startColumnIndex": start_col,
                "endColumnIndex": end_col,
            },
            "rule": {"condition": {"type": "BOOLEAN"}},
        }
    }


def budget_planner_values():
    start, end = BUDGET_PLANNER_ENTRY_ROWS
    return "Budget Planner!A1:F10", [
        ["Budget Planner", "", "", "", "", ""],
        ["", "", "", "", "", ""],
        ["Summary", "", "", "", "", ""],
        ["Total Income", f'=SUMIF(A{start}:A{end},"Income",D{start}:D{end})', "", "", "", ""],
        ["Total Bills", f'=SUMIF(A{start}:A{end},"Bill",D{start}:D{end})', "", "", "", ""],
        ["Total Savings", f'=SUMIF(A{start}:A{end},"Savings",D{start}:D{end})', "", "", "", ""],
        ["Total Debt Payments", f'=SUMIF(A{start}:A{end},"Debt",D{start}:D{end})', "", "", "", ""],
        ["Net (Income − Bills − Savings − Debt)", "=B4-B5-B6-B7", "", "", "", ""],
        ["", "", "", "", "", ""],
        ["Type", "Category", "Subcategory", "Amount", "Cadence", "Notes"],
    ]


def bill_calendar_values():
    start, end = BILL_CALENDAR_ENTRY_ROWS
    header = ["Name", "Type", "Amount", "Due Day"] + MONTH_NAMES
    totals_row = ["Monthly Net Total", "", "", ""] + [
        f"=SUMPRODUCT($C${start}:$C${end},{col}{start}:{col}{end})" for col in MONTH_COLUMNS
    ]
    return [
        ("Smart Bill Calendar!A1:P3", [
            ["Smart Bill Calendar"] + [""] * 15,
            [""] * 16,
            header,
        ]),
        (f"Smart Bill Calendar!A{end + 2}:P{end + 2}", [totals_row]),
    ]


def transactions_values():
    start, end = TRANSACTIONS_ENTRY_ROWS
    running_balance = (
        f'=ARRAYFORMULA(IF(F{start}:F{end}="","",'
        f'SUMIF(ROW(F{start}:F{end}),"<="&ROW(F{start}:F{end}),F{start}:F{end})))'
    )
    return "Transactions Tracker!A1:G4", [
        ["Transactions Tracker", "", "", "", "", "", ""],
        ["", "", "", "", "", "", ""],
        ["Date", "Description", "Category", "Subcategory", "Account", "Amount", "Running Balance"],
        ["", "", "", "", "", "", running_balance],
    ]


def build_format_requests(sheet_ids: dict[str, int]) -> list[dict]:
    bp_id = sheet_ids["Budget Planner"]
    bc_id = sheet_ids["Smart Bill Calendar"]
    tt_id = sheet_ids["Transactions Tracker"]
    bp_start, bp_end = BUDGET_PLANNER_ENTRY_ROWS
    bc_start, bc_end = BILL_CALENDAR_ENTRY_ROWS

    return [
        # Budget Planner
        freeze_rows_request(bp_id, 10),
        bold_header_request(bp_id, 1, 1, 6, shaded=False),
        bold_header_request(bp_id, 10, 10, 6, shaded=True),
        list_validation_request(bp_id, bp_start, bp_end, 0, ["Income", "Bill", "Savings", "Debt"]),
        list_validation_request(bp_id, bp_start, bp_end, 4, ["Weekly", "Biweekly", "Monthly", "One-time"]),
        # Smart Bill Calendar
        freeze_rows_request(bc_id, 3),
        bold_header_request(bc_id, 1, 1, 16, shaded=False),
        bold_header_request(bc_id, 3, 3, 16, shaded=True),
        list_validation_request(bc_id, bc_start, bc_end, 1, ["Income", "Bill", "Subscription", "Debt"]),
        checkbox_validation_request(bc_id, bc_start, bc_end, 4, 16),
        bold_header_request(bc_id, bc_end + 2, bc_end + 2, 16, shaded=True),
        # Transactions Tracker
        freeze_rows_request(tt_id, 3),
        bold_header_request(tt_id, 1, 1, 7, shaded=False),
        bold_header_request(tt_id, 3, 3, 7, shaded=True),
    ]


def main():
    title = sys.argv[1] if len(sys.argv) > 1 else "Annual Budget"

    load_dotenv()
    creds = get_credentials()
    sheets = build("sheets", "v4", credentials=creds)

    spreadsheet = sheets.spreadsheets().create(body={
        "properties": {"title": title},
        "sheets": [
            {"properties": {"title": "Budget Planner"}},
            {"properties": {"title": "Smart Bill Calendar"}},
            {"properties": {"title": "Transactions Tracker"}},
        ],
    }).execute()

    spreadsheet_id = spreadsheet["spreadsheetId"]
    sheet_ids = {s["properties"]["title"]: s["properties"]["sheetId"] for s in spreadsheet["sheets"]}

    value_data = [{"range": r, "values": v} for r, v in [
        budget_planner_values(),
        *bill_calendar_values(),
        transactions_values(),
    ]]
    sheets.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "valueInputOption": "USER_ENTERED",
        "data": value_data,
    }).execute()

    sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "requests": build_format_requests(sheet_ids),
    }).execute()

    print(f"Created: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")


if __name__ == "__main__":
    main()
