from pathlib import Path

import pandas as pd
import streamlit as st

# 페이지를 넓게 사용하고 사이드바를 펼칩니다.
st.set_page_config(
    page_title="영업팀 매출 현황",
    layout="wide",
    initial_sidebar_state="expanded",
)


# 파일을 읽은 결과를 캐시하여 화면이 다시 실행될 때 재사용합니다.
@st.cache_data
def load_data():
    csv_path = Path(__file__).resolve().parent / "sales_sample.csv"
    data = pd.read_csv(csv_path, encoding="utf-8-sig")

    # 날짜 변환 전에 필수 열을 검사하여 누락된 열 이름을 안내합니다.
    required_columns = ["date", "region", "category", "sales", "quantity"]
    missing_columns = [column for column in required_columns if column not in data.columns]
    if missing_columns:
        raise ValueError(f"누락된 필수 열: {', '.join(missing_columns)}")

    data["date"] = pd.to_datetime(data["date"], errors="raise")
    return data


# 파일이나 열에 문제가 있으면 이후 화면을 그리기 전에 멈춥니다.
try:
    df = load_data()
except FileNotFoundError:
    st.error("CSV 파일을 찾을 수 없습니다. 파일 이름과 위치를 확인해 주세요. "
             "sales_sample.csv는 app.py와 같은 폴더에 있어야 합니다.")
    st.stop()
except ValueError as error:
    st.error(f"CSV 데이터를 확인해 주세요. {error}")
    st.stop()

st.title("영업팀 매출 현황")
st.caption("데이터 기준: 2026년 1~10월")

# 지역은 여러 개, 카테고리는 하나, 기간은 시작일과 종료일을 선택합니다.
st.sidebar.title("조건 선택")
regions = sorted(df["region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("지역", regions, default=regions)
categories = sorted(df["category"].dropna().unique().tolist())
selected_category = st.sidebar.selectbox("카테고리", ["전체"] + categories)
min_date = df["date"].min().date()
max_date = df["date"].max().date()
selected_period = st.sidebar.date_input(
    "기간",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# 기간 선택이 완료된 뒤 세 조건을 모두 적용합니다. 시작일과 종료일도 포함합니다.
if len(selected_period) != 2:
    st.info("기간의 시작일과 종료일을 모두 선택해 주세요.")
    st.stop()

start_date, end_date = selected_period
filtered_df = df[
    df["region"].isin(selected_regions)
    & df["date"].dt.date.between(start_date, end_date)
]
if selected_category != "전체":
    filtered_df = filtered_df[filtered_df["category"] == selected_category]

st.caption(f"선택 조건: {len(filtered_df):,}건 / 전체 {len(df):,}건")
if filtered_df.empty:
    st.info("조건을 넓혀 보세요")
    st.stop()

# CSV 한 행을 주문 한 건으로 보고 세 지표를 가로로 표시합니다.
total_sales = filtered_df["sales"].sum()
order_count = len(filtered_df)
average_order_value = total_sales / order_count if order_count else 0

sales_col, orders_col, average_col = st.columns(3)
sales_col.metric("총 매출", f"{total_sales:,.0f}원")
orders_col.metric("주문 건수", f"{order_count:,}건")
average_col.metric("평균 주문액", f"{average_order_value:,.0f}원")

# 지표 아래에 두 개의 탭을 배치합니다.
summary_tab, detail_tab = st.tabs(["요약", "상세 데이터"])

with summary_tab:
    # 연도와 월을 함께 묶고 시간순으로 정렬합니다.
    monthly_sales = (
        filtered_df.groupby(filtered_df["date"].dt.to_period("M"))["sales"]
        .sum()
        .sort_index()
        .rename("매출 (원)")
    )
    monthly_sales.index = monthly_sales.index.to_timestamp()
    monthly_sales.index.name = "월"

    st.subheader("월별 매출")
    st.line_chart(monthly_sales, x_label="월", y_label="매출 (원)")

    # 매출 내림차순을 유지하도록 막대 그래프의 자동 정렬을 끕니다.
    region_sales = (
        filtered_df.groupby("region")["sales"]
        .sum()
        .sort_values(ascending=False)
        .rename("매출 (원)")
    )
    region_sales.index.name = "지역"

    st.subheader("지역별 매출")
    st.bar_chart(region_sales, sort=False, x_label="지역", y_label="매출 (원)")

with detail_tab:
    # 필터 결과를 탭 너비에 맞춰 표시하고 행 번호는 숨깁니다.
    st.dataframe(filtered_df, width="stretch", hide_index=True)
