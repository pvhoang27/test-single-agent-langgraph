import sqlite3
from datetime import date
from pathlib import Path
from langchain_core.tools import tool

from app.config import settings


def _connect() -> sqlite3.Connection:
    database_path: Path = settings.database_path
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL CHECK (kind IN ('income', 'expense')),
                amount INTEGER NOT NULL CHECK (amount > 0),
                category TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                transaction_date TEXT NOT NULL
            )
            """
        )


def _add_transaction(
    database_kind: str,
    amount: int,
    category: str,
    note: str = "",
    transaction_date: str = "",
) -> str:
    if amount <= 0:
        return "Số tiền phải lớn hơn 0."
    transaction_date = transaction_date or date.today().isoformat()
    try:
        date.fromisoformat(transaction_date)
    except ValueError:
        return "Ngày không hợp lệ, cần dùng định dạng YYYY-MM-DD."

    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO transactions(kind, amount, category, note, transaction_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (database_kind, amount, category.strip(), note.strip(), transaction_date),
        )
        transaction_id = cursor.lastrowid
    return f"Đã thêm giao dịch ID {transaction_id}."


@tool
def them_khoan_chi(
    amount: int,
    category: str,
    note: str = "",
    transaction_date: str = "",
) -> str:
    """Thêm khoản CHI: tiền đã tiêu, mua hoặc thanh toán. amount là VND; ngày dạng YYYY-MM-DD."""
    return _add_transaction("expense", amount, category, note, transaction_date)


@tool
def them_khoan_thu(
    amount: int,
    category: str,
    note: str = "",
    transaction_date: str = "",
) -> str:
    """Thêm khoản THU: tiền lương, thưởng hoặc tiền đã nhận. amount là VND; ngày dạng YYYY-MM-DD."""
    return _add_transaction("income", amount, category, note, transaction_date)


@tool
def list_transactions(limit: int = 10) -> str:
    """Xem các giao dịch gần nhất. limit là số giao dịch cần hiển thị, từ 1 đến 50."""
    limit = max(1, min(limit, 50))
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, kind, amount, category, note, transaction_date
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    if not rows:
        return "Chưa có giao dịch nào."
    return "\n".join(
        f"ID {row['id']} | {row['transaction_date']} | "
        f"{'thu' if row['kind'] == 'income' else 'chi'} | "
        f"{row['amount']:,} VND | {row['category']} | {row['note']}"
        for row in rows
    )


@tool
def get_spending_summary(start_date: str, end_date: str) -> str:
    """Thống kê thu chi trong khoảng ngày bao gồm start_date và end_date, dạng YYYY-MM-DD."""
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError:
        return "Ngày không hợp lệ, cần dùng định dạng YYYY-MM-DD."
    if start > end:
        return "Ngày bắt đầu phải trước hoặc bằng ngày kết thúc."

    with _connect() as connection:
        totals = connection.execute(
            """
            SELECT kind, COALESCE(SUM(amount), 0) AS total
            FROM transactions
            WHERE transaction_date BETWEEN ? AND ?
            GROUP BY kind
            """,
            (start_date, end_date),
        ).fetchall()
        categories = connection.execute(
            """
            SELECT category, SUM(amount) AS total
            FROM transactions
            WHERE kind = 'expense' AND transaction_date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total DESC
            """,
            (start_date, end_date),
        ).fetchall()

    values = {row["kind"]: row["total"] for row in totals}
    income = values.get("income", 0)
    expense = values.get("expense", 0)
    category_text = ", ".join(
        f"{row['category']}: {row['total']:,} VND" for row in categories
    ) or "không có"
    return (
        f"Từ {start_date} đến {end_date}: thu {income:,} VND, "
        f"chi {expense:,} VND, số dư {income - expense:,} VND. "
        f"Chi theo danh mục: {category_text}."
    )


@tool
def delete_transaction(transaction_id: int) -> str:
    """Xóa một giao dịch theo đúng ID mà người dùng cung cấp."""
    with _connect() as connection:
        cursor = connection.execute(
            "DELETE FROM transactions WHERE id = ?", (transaction_id,)
        )
    if cursor.rowcount == 0:
        return f"Không tìm thấy giao dịch ID {transaction_id}."
    return f"Đã xóa giao dịch ID {transaction_id}."


TOOLS = [
    them_khoan_chi,
    them_khoan_thu,
    list_transactions,
    get_spending_summary,
    delete_transaction,
]
