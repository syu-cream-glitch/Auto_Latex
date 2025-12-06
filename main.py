import streamlit as st
import pandas as pd

st.set_page_config(page_title="LaTeX表作成ツール", layout="wide")

st.title("📊 LaTeX表作成ツール")

st.markdown("""
このツールで表を作成し，リアルタイムでLaTeX形式のコードを生成できます．
また，Notionなどのツールからコピーした表を貼り付けてLaTeX形式に変換することもできます．
""")

# タブ区切りのテキストをDataFrameに変換する関数
import pandas as pd

def parse_tab_separated_text(text, use_first_row_as_header=True, use_first_column_as_index=False):
    """
    タブ区切りのテキストをDataFrameに変換．
    - 列数は行ごとの最大列数で揃える
    - 左上セルは空白化せず，必要に応じてインデックスに設定
    """
    if not text.strip():
        return pd.DataFrame()

    lines = text.strip().split('\n')
    data = []

    # 各行をタブで分割
    for line in lines:
        cells = line.split('\t')
        cells = [c.strip() for c in cells]
        data.append(cells)

    # データ全体の最大列数で揃える
    max_cols = max(len(row) for row in data)
    for i in range(len(data)):
        row = data[i]
        while len(row) < max_cols:
            row.append("")
        data[i] = row

    df = pd.DataFrame(data)

    # ヘッダー処理
    if use_first_row_as_header:
        header = list(df.iloc[0])
        df = df.iloc[1:].reset_index(drop=True)
        df.columns = header

    # インデックス処理
    if use_first_column_as_index:
        df = df.set_index(df.columns[0])

    return df

# LaTeX形式に変換する関数
def dataframe_to_latex(df, caption="", label="", position="h"):
    if df.empty:
        return ""

    # 列数はヘッダーの列数
    num_cols = len(df.columns)
    col_format = "l" + "c" * (num_cols - 1)

    latex_code = f"\\begin{{table}}[{position}]\n"
    latex_code += "    \\centering\n"

    if caption:
        latex_code += f"    \\caption{{{caption}}}\n"

    latex_code += f"    \\begin{{tabular}}{{{col_format}}}\n"
    latex_code += "        \\hline\n"

    # ヘッダー行：左上セルだけ空白
    header_cells = [""] + [f"\\text{{{str(col)}}}" for col in df.columns[0:(len(df.columns) - 1)]]
    latex_code += "        " + " & ".join(header_cells) + " \\\\\n"
    latex_code += "        \\hline\n"

    # データ行
    for _, row in df.iterrows():
        row_data = [str(c) for c in row]
        latex_code += "        " + " & ".join(row_data) + " \\\\\n"

    latex_code += "        \\hline\n"
    latex_code += "    \\end{tabular}\n"

    if label:
        latex_code += f"    \\label{{{label}}}\n"

    latex_code += "\\end{table}"

    return latex_code


# 入力モードの選択
tab1, tab2 = st.tabs(["📋 Notion貼り付け", "🎨 インタラクティブ表作成"])

with tab1:
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

            # LaTeXコード生成
            latex_code = dataframe_to_latex(parsed_df, caption=caption, label=label, position=position)
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

with tab2:
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
    st.session_state.table_data = edited_df

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

    # LaTeX用にダミー列を追加（関数を変えない場合の対応）
    df_for_latex = edited_df.copy()
    df_for_latex[""] = ""  # 右端に空列を追加
    
    latex_code = dataframe_to_latex(df_for_latex, caption=caption, label=label, position=position)


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


# 使い方の説明
with st.expander("📚 使い方"):
    st.markdown("""
    ## 📋 Notion表の貼り付け
    1. NotionやExcelで表を選択してコピー（Ctrl+C）
    2. 上のテキストエリアに貼り付け（Ctrl+V）
    3. 自動的にLaTeX形式に変換されます

    ## 🎨 インタラクティブ作成
    1. **表のサイズを設定**: 行数と列数を指定
    2. **列名を設定**: 各列に名前を付ける
    3. **新しい表を作成**: 「新しい表を作成」ボタンをクリック
    4. **表を編集**: 各セルをクリックして値を入力
    5. **LaTeXコードを確認**: 表の下にリアルタイムでLaTeX形式のコードが生成されます
    6. **コードをコピー**: 下のテキストエリアからLaTeXコードをコピーして使用

    **LaTeXでの使用例:**
    ```latex
    \\documentclass{article}
    \\begin{document}
    """ + latex_code + """
    \\end{document}
    ```
    """)

st.markdown("---")
st.caption("💡 表の値を変更すると，LaTeXコードが自動的に更新されます．")
