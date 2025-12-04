import streamlit as st
import pandas as pd

st.set_page_config(page_title="LaTeX表作成ツール", layout="wide")

st.title("📊 LaTeX表作成ツール")

st.markdown("""
このツールで表を作成し、リアルタイムでLaTeX形式のコードを生成できます。
また、Notionなどのツールからコピーした表を貼り付けてLaTeX形式に変換することもできます。
""")

# タブ区切りのテキストをDataFrameに変換する関数
def parse_tab_separated_text(text, use_first_row_as_header=True, use_first_column_as_index=False):
    """タブ区切りのテキストをDataFrameに変換"""
    if not text.strip():
        return pd.DataFrame()

    lines = text.strip().split('\n')
    data = []

    for line in lines:
        # タブで分割（連続するタブも考慮）
        cells = line.split('\t')
        # 空のセルをNoneに変換（空文字列もNoneに）
        cells = [cell.strip() if cell.strip() else None for cell in cells]
        if cells:  # 空行でない場合のみ追加
            data.append(cells)

    if not data:
        return pd.DataFrame()

    # 最大列数に合わせてNoneで埋める
    max_cols = max(len(row) for row in data)
    for row in data:
        while len(row) < max_cols:
            row.append(None)

    # DataFrame作成
    df = pd.DataFrame(data)

    # ヘッダーの処理
    if use_first_row_as_header and len(df) > 0:
        # 最初の行をヘッダーとして使用
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)

    # インデックスの処理
    if use_first_column_as_index and len(df.columns) > 0:
        # 最初の列をインデックスとして使用
        df = df.set_index(df.columns[0])

    return df

# LaTeX形式に変換する関数
def dataframe_to_latex(df):
    """DataFrameをLaTeX表形式に変換"""
    if df.empty:
        return ""

    # 列数を取得
    num_cols = len(df.columns)

    # LaTeX表のヘッダー
    latex_code = "\\begin{tabular}{|" + "c|" * num_cols + "}\n\\hline\n"

    # ヘッダー行
    header_row = " & ".join(str(col) for col in df.columns)
    latex_code += header_row + " \\\\\n\\hline\n"

    # データ行
    for _, row in df.iterrows():
        row_data = []
        for cell in row:
            # 空のセルは空白として扱う
            cell_str = str(cell) if pd.notna(cell) and str(cell).strip() != "" else ""
            row_data.append(cell_str)
        latex_code += " & ".join(row_data) + " \\\\\n\\hline\n"

    # フッター
    latex_code += "\\end{tabular}"

    return latex_code

# タブで入力モード
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
    placeholder="課題2成功\t課題2失敗\t合計\t\n課題1成功\t7247\t177\t7424\t\n課題1失敗\t74\t4102\t4176\t\n合計\t7321\t4279\t\t",
    help="NotionやExcelから表をコピーして貼り付けてください。タブ区切りで自動認識します。"
)

if tab_input.strip():
    try:
        parsed_df = parse_tab_separated_text(tab_input, use_first_row_as_header=use_header, use_first_column_as_index=use_index)

        if not parsed_df.empty:
            st.success(f"✅ 表を解析しました: {len(parsed_df)}行 × {len(parsed_df.columns)}列")

            # 解析された表を表示
            st.subheader("📊 解析された表")
            st.dataframe(parsed_df, use_container_width=True)

            # LaTeXコード生成
            latex_code = dataframe_to_latex(parsed_df)
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
            st.warning("⚠️ 有効な表データを検出できませんでした。")

    except Exception as e:
        st.error(f"❌ 表の解析に失敗しました: {e}")

st.markdown("---")

# 既存のインタラクティブ表作成機能
st.subheader("🎨 インタラクティブ表作成")

# 表のサイズ設定
col1, col2 = st.columns(2)
with col1:
    rows = st.number_input("行数", min_value=1, max_value=20, value=3, step=1, key="interactive_rows")
with col2:
    cols = st.number_input("列数", min_value=1, max_value=10, value=3, step=1, key="interactive_cols")

# 初期データの作成
if 'table_data' not in st.session_state or st.button("🔄 新しい表を作成"):
    # 空のDataFrameを作成
    data = {}
    for i in range(cols):
        col_name = f"列{i+1}"
        data[col_name] = [""] * rows
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
st.session_state.table_data = edited_df

# LaTeX形式に変換する関数
def dataframe_to_latex(df):
    """DataFrameをLaTeX表形式に変換"""
    if df.empty:
        return ""

    # 列数を取得
    num_cols = len(df.columns)

    # LaTeX表のヘッダー
    latex_code = "\\begin{tabular}{|" + "c|" * num_cols + "}\n\\hline\n"

    # ヘッダー行
    header_row = " & ".join(df.columns)
    latex_code += header_row + " \\\\\n\\hline\n"

    # データ行
    for _, row in df.iterrows():
        row_data = []
        for cell in row:
            # 空のセルは空白として扱う
            cell_str = str(cell) if pd.notna(cell) and str(cell).strip() != "" else ""
            row_data.append(cell_str)
        latex_code += " & ".join(row_data) + " \\\\\n\\hline\n"

    # フッター
    latex_code += "\\end{tabular}"

    return latex_code

# LaTeXコードの生成と表示
st.subheader("📄 LaTeXコード")
latex_code = dataframe_to_latex(edited_df)

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

# プレビュー表示（改善版）
st.subheader("👀 表のプレビュー")
st.markdown("**現在の表の見た目:**")

# HTMLテーブルとしてプレビュー表示
html_preview = f"""
<style>
.preview-table {{
    border-collapse: collapse;
    width: 100%;
    margin: 10px 0;
    font-family: Arial, sans-serif;
}}
.preview-table th, .preview-table td {{
    border: 1px solid #ddd;
    padding: 8px 12px;
    text-align: center;
}}
.preview-table th {{
    background-color: #f2f2f2;
    font-weight: bold;
}}
.preview-table tr:nth-child(even) {{
    background-color: #f9f9f9;
}}
.preview-table tr:hover {{
    background-color: #f5f5f5;
}}
</style>
"""

html_preview += edited_df.to_html(
    index=False,
    classes='preview-table',
    border=0,
    justify='center'
)

st.markdown(html_preview, unsafe_allow_html=True)

# 統計情報
st.subheader("📊 表の情報")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("行数", len(edited_df))
with col2:
    st.metric("列数", len(edited_df.columns))
with col3:
    total_cells = len(edited_df) * len(edited_df.columns)
    filled_cells = edited_df.notna().sum().sum()
    st.metric("入力済みセル", f"{filled_cells}/{total_cells}")

# 印刷用ビュー
if st.button("🖨️ 印刷用ビュー"):
    st.markdown("---")
    st.markdown("### 🖨️ 印刷用ビュー")
    st.markdown("このビューを印刷（Ctrl+P）して表のスクリーンショットとして使用できます。")

    # 印刷用スタイル
    print_html = f"""
    <style>
    @media print {{
        body {{ font-family: Arial, sans-serif; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
        th {{ background-color: #f0f0f0; font-weight: bold; }}
    }}
    </style>
    """

    print_html += edited_df.to_html(
        index=False,
        border=1,
        justify='center'
    )

    st.markdown(print_html, unsafe_allow_html=True)

    # LaTeXコードも印刷用に
    st.markdown("### LaTeXコード:")
    st.code(latex_code, language="latex")

# 使い方の説明
with st.expander("📚 使い方"):
    st.markdown("""
    ## 📋 Notion表の貼り付け
    1. NotionやExcelで表を選択してコピー（Ctrl+C）
    2. 上のテキストエリアに貼り付け（Ctrl+V）
    3. 自動的にLaTeX形式に変換されます

    ## 🎨 インタラクティブ作成
    1. **表のサイズを設定**: 行数と列数を指定して「新しい表を作成」をクリック
    2. **表を編集**: 各セルをクリックして値を入力
    3. **LaTeXコードを確認**: 表の下にリアルタイムでLaTeX形式のコードが生成されます
    4. **コードをコピー**: 下のテキストエリアからLaTeXコードをコピーして使用

    **LaTeXでの使用例:**
    ```latex
    \\documentclass{article}
    \\begin{document}
    """ + latex_code + """
    \\end{document}
    ```
    """)

st.markdown("---")
st.caption("💡 表の値を変更すると、LaTeXコードが自動的に更新されます。")
