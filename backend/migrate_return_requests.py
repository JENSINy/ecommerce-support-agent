from sqlalchemy import text

from database import engine


def column_exists(column_name: str) -> bool:
    with engine.connect() as connection:
        result = connection.execute(text("PRAGMA table_info(return_requests)"))

        columns = result.fetchall()

    return any(column[1] == column_name for column in columns)


def add_column_if_not_exists(
    column_name: str,
    column_definition: str,
) -> None:
    if column_exists(column_name):
        print(f"字段已存在：{column_name}")
        return

    with engine.begin() as connection:
        connection.execute(
            text(
                "ALTER TABLE return_requests "
                f"ADD COLUMN {column_name} {column_definition}"
            )
        )

    print(f"字段已添加：{column_name}")


def migrate() -> None:
    add_column_if_not_exists(
        "reviewed_by",
        "VARCHAR(100)",
    )
    add_column_if_not_exists(
        "reviewed_at",
        "DATETIME",
    )
    add_column_if_not_exists(
        "review_note",
        "TEXT",
    )

    print("退货申请表升级完成")


if __name__ == "__main__":
    migrate()
