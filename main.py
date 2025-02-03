import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

st.title("米国株価可視化アプリ")

st.sidebar.write("""
                 # GAFA株価
                 こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
                 """)

st.sidebar.write(f"""
                 ## 表示日数選択
                 """)

days = st.sidebar.slider("日数", 1, 50, 20)

st.markdown(f"""
         ### 過去 **{days}日間** のGAFAの株価
         """)

@st.cache_data
def get_data(days, tickers):
    # 空のデータフレーム（データを格納する場所）を作成
    df = pd.DataFrame()

    # tickersの辞書をfor文で回して各企業のデータを処理
    for company in tickers.keys():  # 各企業名 ("apple", "facebook") を繰り返し取得
        # ティッカーオブジェクトを作成
        tkr = yf.Ticker(tickers[company])  
        
        # 指定期間（ここでは過去20日間）の株価データを取得
        hist = tkr.history(period=f"{days}d")
        
        # インデックスを DatetimeIndex に変換
        hist.index = pd.to_datetime(hist.index)

        # 日付インデックスをフォーマット変更（例: "2025-01-01" → "01 January 2025"）
        hist.index = hist.index.strftime("%d %B %Y")
        
        # 終値（Close列）のみを抽出
        hist = hist[["Close"]]
        
        # 列名を企業名に変更
        hist.columns = [company]
        
        # データフレームを転置（行と列を入れ替え）
        hist = hist.T
        
        # インデックス名を "Name" に変更（行名に企業名が入る）
        hist.index.name = "Name"
        
        # 既存のデータフレーム（df）と現在のデータ（hist）を結合
        # ※ pd.concat() は結果を返すだけで df そのものには反映されないので注意
        df = pd.concat([df, hist])
    return df
try:
    st.sidebar.write("""
                    ## 株価の範囲指定
                    """)

    ymin, ymax = st.sidebar.slider(
        "範囲を指定してください。",
        0.0, 3500.0, (0.0, 3500.0)
    )

    # 株式ティッカーの辞書（企業名とティッカーシンボルを対応付ける）
    tickers = {
        "apple": "AAPL",
        "facebook": "META",
        "google" : "GOOGL",
        "microsoft" : "MSFT",
        "netflix" : "NFLX",
        "amazon" : "AMZN"
    }

    df = get_data(days, tickers)

    companies = st.multiselect(
        "会社名を選択してください。",
        df.index.tolist(),
        ["google", "amazon", "facebook", "apple"]
    )

    if not companies:
        st.error("少なくとも1社は選んでください")
    else:
        data = df.loc[companies]
        st.write("### 株価 (USD)", data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=["Date"]).rename(
            columns={"value": "Stock Prices(USD)"}
        )
        
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color="Name:N"
            )
        )

        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
    "何かエラーが起きているようです。"
    )