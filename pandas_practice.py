from pathlib import Path

import pandas as pd


# 스크립트와 같은 폴더에 있는 CSV를 읽습니다.
csv_path = Path(__file__).resolve().parent / "sales_sample.csv"
df = pd.read_csv(csv_path, encoding="utf-8-sig")

# 공백만 있는 칸도 빈칸으로 처리합니다.
df = df.replace(r"^\s*$", pd.NA, regex=True)

print("[행·열 개수]")
print(f"행: {df.shape[0]}개, 열: {df.shape[1]}개")
print("\n[CSV를 처음 읽었을 때 열 이름과 자료형]")
print(df.dtypes.to_string())
print("\n[열별 빈칸 개수]")
print(df.isna().sum().to_string())

# 날짜는 날짜형으로, 매출과 수량은 숫자형으로 변환합니다.
# 잘못된 값이 있으면 오류를 표시하여 합계에서 조용히 빠지지 않도록 합니다.
df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d", errors="raise")
df["sales"] = pd.to_numeric(df["sales"], errors="raise")
df["quantity"] = pd.to_numeric(df["quantity"], errors="raise")

print("\n[변환 후 자료형 확인]")
print(df.dtypes.to_string())
print(f"date가 날짜형인가? {pd.api.types.is_datetime64_any_dtype(df['date'])}")
print(f"sales가 숫자형인가? {pd.api.types.is_numeric_dtype(df['sales'])}")
print(f"quantity가 숫자형인가? {pd.api.types.is_numeric_dtype(df['quantity'])}")

# 지역별 합계와 연도·월별 합계를 출력합니다. 전부 빈 매출은 0으로 바꾸지 않습니다.
region_sales = df.groupby("region", dropna=False)["sales"].sum(min_count=1)
monthly_sales = df.groupby(df["date"].dt.to_period("M"), dropna=False)["sales"].sum(min_count=1)

print("\n[지역별 매출 합계 (원)]")
print(region_sales.to_string())
print("\n[월별 매출 합계 (원)]")
print(monthly_sales.to_string())
