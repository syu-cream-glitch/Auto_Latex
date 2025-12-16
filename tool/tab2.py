import streamlit as st
import pandas as pd
from .utils import dataframe_to_latex

def render_tab2():
    st.subheader("🎨 インタラクティブ表作成")

    # 表のサイズ設定
    col1, col2 = st.columns(2)
    with col1:
        rows = st.number_input("行数", min_value=1, max_value=20, value=3, step=1, key="interactive_rows")
    with col2:
        cols = st.number_input("列数", min_value=1, max_value=10, value=3, step=1, key="interactive_cols")

    # 列名の設定
    st.subheader("📋 列名の設定")
    col_names = []
    
    # 列数に応じてレイアウトを決定
    if cols <= 3:
        cols_input = st.columns(cols)
    elif cols <= 6:
        cols_input = st.columns(3)
    else:
        cols_input = st.columns(4)
    
    for i in range(cols):
        col_idx = i % len(cols_input)
        with cols_input[col_idx]:
            default_name = f"列{i+1}"
            if f'col_name_{i}' in st.session_state:
                default_name = st.session_state[f'col_name_{i}']
            col_name = st.text_input(
                f"列{i+1}",
                value=default_name,
                key=f"col_name_input_{i}",
                label_visibility="collapsed"
            )
            col_names.append(col_name)
            st.session_state[f'col_name_{i}'] = col_name

    # 初期データの作成
    if 'table_data' not in st.session_state or st.button("🔄 新しい表を作成"):
        # 列名をリセット
        for i in range(10):  # 最大10列まで
            if f'col_name_{i}' in st.session_state:
                del st.session_state[f'col_name_{i}']
        
        # 空のDataFrameを作成
        data = {}
        for i in range(cols):
            col_name = col_names[i] if i < len(col_names) else f"列{i+1}"
            data[col_name] = [""] * (rows)
        st.session_state.table_data = pd.DataFrame(data)

    # 表の編集
    st.subheader("📝 表の編集")
    edited_df = st.data_editor(
        st.session_state.table_data,
        num_rows="dynamic",
        width="stretch",
        key="table_editor"
    )

    # 編集されたデータをセッションステートに保存
    #重複していたためコメントアウト
    #st.session_state.table_data = edited_df

    # LaTeXコードの生成と表示
    st.subheader("📄 LaTeXコード")

    # LaTeX設定
    col1, col2 = st.columns(2)
    with col1:
        caption = st.text_input("キャプション", placeholder="表のタイトルを入力", key="interactive_caption")
        label = st.text_input("ラベル", placeholder="tab:example", key="interactive_label")
    with col2:
        position_options = {"h": "ここ(here)", "t": "上(top)", "b": "下(bottom)", "p": "別ページ(page)"}
        position = st.selectbox("位置", options=list(position_options.keys()),
                              format_func=lambda x: position_options[x], key="interactive_position")
        caption_position = st.radio("キャプションの位置", options=["上", "下"], index=0, key="caption_position_interactive")
        left_centered = st.checkbox("左端も中央寄せにする", value=False, key="left_centered_interactive")

    # LaTeX用にダミー列を追加（関数を変えない場合の対応）
    df_for_latex = edited_df.copy()
    df_for_latex[""] = ""  # 右端に空列を追加
    
    latex_code = dataframe_to_latex(df_for_latex, caption=caption, label=label, position=position, caption_position=caption_position, left_centered=left_centered)


    # LaTeXコードを表示
    st.code(latex_code, language="latex")


    # エクスポート機能
    st.subheader("💾 エクスポート")
    col1, col2, col3 = st.columns(3)

    with col1:
        # CSVエクスポート
        csv_data = edited_df.to_csv(index=False)
        st.download_button(
            label="📊 CSVダウンロード",
            data=csv_data,
            file_name="table.csv",
            mime="text/csv",
            key="csv_download"
        )

    with col2:
        # HTMLエクスポート
        html_table = edited_df.to_html(index=False, border=1, justify='center')
        st.download_button(
            label="🌐 HTMLダウンロード",
            data=f"<html><body>{html_table}</body></html>",
            file_name="table.html",
            mime="text/html",
            key="html_download"
        )

    with col3:
        # LaTeXファイルダウンロード
        st.download_button(
            label="📄 LaTeXファイルダウンロード",
            data=latex_code,
            file_name="table.tex",
            mime="text/plain",
            key="latex_download"
        )