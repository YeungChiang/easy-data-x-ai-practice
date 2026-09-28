import csv
import duckdb
from pathlib import Path

csv_path = Path("task05_orders.csv")

# 1. 用 Python 重新生成标准 UTF-8 CSV
rows = [
    ["order_id", "customer_id", "product", "amount"],
    [1001, "C001", "规划原理教材", 89],
    [1002, "C002", "相关知识教材", 96],
    [1003, "C001", "法规教材", 78],
    [1004, "C003", "实务教材", 108],
    [1005, "C002", "真题集", 66],
]

with csv_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

# 2. 先用 Python 验证 CSV 结构
with csv_path.open("r", encoding="utf-8", newline="") as f:
    parsed = list(csv.reader(f))

print("=== CSV 结构验证 ===")
print(parsed)
print("每行列数:", [len(row) for row in parsed])

# 3. DuckDB 直接查询 CSV
print("\n=== 1. SELECT FROM read_csv ===")
duckdb.sql("""
SELECT *
FROM read_csv('task05_orders.csv', header=true);
""").show()

print("\n=== 2. GROUP BY 聚合 ===")
duckdb.sql("""
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(amount) AS total_amount
FROM read_csv('task05_orders.csv', header=true)
GROUP BY customer_id
ORDER BY total_amount DESC;
""").show()
