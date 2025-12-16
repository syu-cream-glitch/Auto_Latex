import streamlit as st
import pandas as pd
from .utils import generate_preview_html, generate_complex_latex

def render_tab3():
    st.subheader("🧩 リアルタイム・プレビュー付き表作成")
    st.markdown("""
    **使い方：** 隣り合ったセルに「同じ文字」を入力すると、下のプレビュー画面で自動的に結合されます。
    """)

    # テンプレートボタン
    if st.button("深海データセットの例をロード", key="load_template_btn"):
        st.session_state.header_data_tab3 = pd.DataFrame([
            ["観測コード", "水温 (C)", "水温 (C)", "塩分濃度", "塩分濃度", "深度"],
            ["観測コード", "エリアA", "エリアB", "ゾーンX", "ゾーンY", "トレンチZ"]
        ])
        st.session_state.body_data_tab3 = pd.DataFrame([
            ["データセット X01", "5.1", "1.3", "34.90", "35.15", "9870.5"],
            ["解析セット S02", "22.8", "7.7", "33.05", "36.88", "1234.9"]
        ])
        st.rerun()

    # サイズ設定
    with st.expander("📏 行数・列数の変更", expanded=False):
        c1, c2, c3 = st.columns(3)
        rows_t3 = c1.number_input("データ行数", 1, 20, 2, key="rows_t3")
        cols_t3 = c2.number_input("列数", 1, 10, 6, key="cols_t3")
        h_rows_t3 = c3.number_input("ヘッダー段数", 1, 3, 2, key="h_rows_t3")

    # データ初期化
    if 'header_data_tab3' not in st.session_state:
        st.session_state.header_data_tab3 = pd.DataFrame("", index=range(h_rows_t3), columns=range(cols_t3))
    if 'body_data_tab3' not in st.session_state:
        st.session_state.body_data_tab3 = pd.DataFrame("", index=range(rows_t3), columns=range(cols_t3))

    # リサイズ対応
    if st.session_state.header_data_tab3.shape != (h_rows_t3, cols_t3):
        st.session_state.header_data_tab3 = pd.DataFrame("", index=range(h_rows_t3), columns=range(cols_t3))
    if st.session_state.body_data_tab3.shape != (rows_t3, cols_t3):
        st.session_state.body_data_tab3 = pd.DataFrame("", index=range(rows_t3), columns=range(cols_t3))

    col_editor, col_preview = st.columns([1, 1])

    with col_editor:
        st.write("###### 1. ヘッダー編集 (同じ文字で結合)")
        edited_header = st.data_editor(
            st.session_state.header_data_tab3,
            key="header_editor_t3",
            width="stretch"  # リクエスト通り変更
        )
        #重複しているのでコメントアウト：連続の編集ができない
        #st.session_state.header_data_tab3 = edited_header

        st.write("###### 2. データ入力")
        edited_body = st.data_editor(
            st.session_state.body_data_tab3,
            key="body_editor_t3",
            width="stretch"  # リクエスト通り変更
        )
        #上記と同じ理由でコメントアウト
        #st.session_state.body_data_tab3 = edited_body

    with col_preview:
        st.write("###### 👀 仕上がりプレビュー")
        # ここでHTMLプレビューを表示
        preview_html = generate_preview_html(edited_header, edited_body)
        st.markdown(preview_html, unsafe_allow_html=True)
        st.info("👆 同じ文字が隣り合うと、このように結合されて表示されます。")

    st.markdown("---")
    
    # LaTeX出力
    c_out1, c_out2 = st.columns([3, 1])
    with c_out1:
        caption = st.text_input("キャプション", "深海探査データ", key="cap_t3")
        label = st.text_input("ラベル", "tab:deepsea", key="lbl_t3")
    with c_out2:
        pos = st.selectbox("位置", ["h", "t", "b"], key="pos_t3")

    if st.button("LaTeXコードを生成", type="primary", key="gen_btn_t3"):
        latex = generate_complex_latex(edited_header, edited_body, caption, label, pos)
        st.code(latex, language="latex")