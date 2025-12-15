import streamlit as st
import pandas as pd
from .utils import parse_tab_separated_text, dataframe_to_latex

def render_tab1():
    st.subheader("📋 Notionなどから表を貼り付け")

    # ヘッダー設定オプション
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        use_header = st.checkbox("最初の行をヘッダーとして扱う", value=True, key="use_header_checkbox")
    with col_opt2:
        use_index = st.checkbox("最初の列を行名として扱う", value=True, key="use_index_checkbox")

    tab_input = st.text_area(
        "タブ区切りの表を貼り付けてください",
        height=150,
        placeholder="\t課題2成功\t課題2失敗\t合計\t\n課題1成功\t7247\t166\t7424\t\n課題1失敗\t74\t4102\t4176\t\n合計\t7321\t4279\t\t",
        help="NotionやExcelから表をコピーして貼り付けてください．タブ区切りで自動認識します．"
    )

    # デフォルト表示用のサンプルデータ
    sample_data = "\t課題2成功\t課題2失敗\t合計\t\n課題1成功\t7247\t166\t7424\t\n課題1失敗\t74\t4102\t4176\t\n合計\t7321\t4279\t\t"
    
    # 入力データまたはサンプルデータを使用
    input_data = tab_input.strip() if tab_input.strip() else sample_data
    
    try:
        parsed_df = parse_tab_separated_text(input_data, use_first_row_as_header=use_header)

        if not parsed_df.empty:
            if tab_input.strip():
                st.success(f"✅ 表を解析しました: {len(parsed_df)}行 × {len(parsed_df.columns)}列")
            else:
                st.info("💡 サンプル表を表示しています．実際の表を貼り付けてください．")

            # LaTeX設定
            st.subheader("⚙️ LaTeX設定")
            col1, col2 = st.columns(2)
            with col1:
                caption = st.text_input("キャプション", placeholder="表のタイトルを入力", key="pasted_caption")
                label = st.text_input("ラベル", placeholder="tab:example", key="pasted_label")
            with col2:
                position_options = {"h": "ここ(here)", "t": "上(top)", "b": "下(bottom)", "p": "別ページ(page)"}
                position = st.selectbox("位置", options=list(position_options.keys()),
                                      format_func=lambda x: position_options[x], key="pasted_position")
                caption_position = st.radio("キャプションの位置", options=["上", "下"], index=0, key="caption_position_pasted")
                left_centered = st.checkbox("左端も中央寄せにする", value=False, key="left_centered_pasted")

            # LaTeXコード生成
            latex_code = dataframe_to_latex(parsed_df, caption=caption, label=label, position=position, caption_position=caption_position, left_centered=left_centered)
            st.subheader("📄 LaTeXコード")
            st.code(latex_code, language="latex")

            # ダウンロードボタン
            col1, col2, col3 = st.columns(3)
            with col1:
                csv_data = parsed_df.to_csv(index=False)
                st.download_button(
                    label="📊 CSVダウンロード",
                    data=csv_data,
                    file_name="pasted_table.csv",
                    mime="text/csv",
                    key="pasted_csv_download"
                )
            with col2:
                st.download_button(
                    label="📄 LaTeXファイルダウンロード",
                    data=latex_code,
                    file_name="pasted_table.tex",
                    mime="text/plain",
                    key="pasted_latex_download"
                )
            with col3:
                html_table = parsed_df.to_html(index=False, border=1, justify='center')
                st.download_button(
                    label="🌐 HTMLダウンロード",
                    data=f"<html><body>{html_table}</body></html>",
                    file_name="pasted_table.html",
                    mime="text/html",
                    key="pasted_html_download"
                )
        else:
            if tab_input.strip():
                st.warning("⚠️ 有効な表データを検出できませんでした．")

    except Exception as e:
        if tab_input.strip():
            st.error(f"❌ 表の解析に失敗しました: {e}")
        else:
            st.error("❌ サンプルデータの解析に失敗しました．")