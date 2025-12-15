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
def dataframe_to_latex(df, caption="", label="", position="h", caption_position="上", left_centered=False):
    if df.empty:
        return ""

    # 列数はヘッダーの列数
    num_cols = len(df.columns)
    col_format = "c" + "c" * (num_cols - 1) if left_centered else "l" + "c" * (num_cols - 1)

    latex_code = f"\\begin{{table}}[{position}]\n"
    latex_code += "    \\centering\n"

    if caption and caption_position == "上":
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

    # 下キャプションの場合
    if caption and caption_position == "下":
        latex_code += f"    \\caption{{{caption}}}\n"

    if label:
        latex_code += f"    \\label{{{label}}}\n"

    latex_code += "\\end{table}"

    return latex_code

# --- ヘッダー処理・HTMLプレビュー用関数 ---
def generate_preview_html(header_df, body_df):
    """
    現在のDataFrameの状態から、結合状態を可視化したHTMLを作成する関数
    """
    html = ['<table style="border-collapse: collapse; width: 100%; text-align: center; font-family: sans-serif;">']
    
    # --- ヘッダー部分の生成 ---
    header_rows = header_df.values.tolist()
    n_cols = len(header_df.columns)
    
    for r_idx, row in enumerate(header_rows):
        html.append("<tr>")
        c_idx = 0
        while c_idx < n_cols:
            current_val = str(row[c_idx])
            colspan = 1
            rowspan = 1
            
            # 横結合チェック
            while (c_idx + colspan < n_cols) and (str(row[c_idx + colspan]) == current_val):
                colspan += 1
            
            # 縦結合チェック（簡易版：下の行と同じならrowspan=2、上の行と同じならスキップ）
            is_vertical_merge_start = False
            skip_cell = False
            
            if r_idx + 1 < len(header_rows):
                if str(header_rows[r_idx+1][c_idx]) == current_val:
                    rowspan = 2
                    is_vertical_merge_start = True
            
            if r_idx > 0:
                if str(header_rows[r_idx-1][c_idx]) == current_val:
                    skip_cell = True
            
            # HTML生成
            if not skip_cell:
                # スタイル調整
                bg_color = "#f0f2f6"
                border = "1px solid #ddd"
                cell_style = f"background-color: {bg_color}; border: {border}; padding: 8px; font-weight: bold;"
                
                # 属性作成
                attrs = f'style="{cell_style}"'
                if colspan > 1: attrs += f' colspan="{colspan}"'
                if rowspan > 1: attrs += f' rowspan="{rowspan}"'
                
                html.append(f'<th {attrs}>{current_val}</th>')
            
            c_idx += colspan
        html.append("</tr>")
    
    # --- ボディ部分の生成 ---
    for _, row in body_df.iterrows():
        html.append("<tr>")
        for val in row:
            val_str = str(val) if val is not None else ""
            html.append(f'<td style="border: 1px solid #ddd; padding: 6px;">{val_str}</td>')
        html.append("</tr>")
        
    html.append("</table>")
    return "\n".join(html)

def generate_complex_latex(header_df, body_df, caption, label, position):
    """ LaTeXコード生成ロジック（前回のものと同じロジック） """
    latex = []
    pos_str = f"[{position}]" if position else ""
    latex.append(f"\\begin{{table}}{pos_str}")
    latex.append(f"\\centering")
    if caption: latex.append(f"\\caption{{{caption}}}")
    if label: latex.append(f"\\label{{{label}}}")
    
    n_cols = len(body_df.columns)
    latex.append(f"\\begin{{tabular}}{{{'c' * n_cols}}}")
    latex.append(f"\\toprule")

    header_rows = header_df.values.tolist()
    for r_idx, row in enumerate(header_rows):
        row_latex = []
        cmidrules = []
        c_idx = 0
        while c_idx < n_cols:
            current_val = str(row[c_idx])
            colspan = 1
            while (c_idx + colspan < n_cols) and (str(row[c_idx + colspan]) == current_val):
                colspan += 1
            
            cell_text = current_val
            if r_idx + 1 < len(header_rows) and str(header_rows[r_idx+1][c_idx]) == current_val:
                 if r_idx > 0 and str(header_rows[r_idx-1][c_idx]) == current_val: cell_text = ""
                 else: cell_text = f"\\multirow{{2}}{{*}}{{{current_val}}}"
            elif r_idx > 0 and str(header_rows[r_idx-1][c_idx]) == current_val: cell_text = ""
            
            if colspan > 1:
                row_latex.append(f"\\multicolumn{{{colspan}}}{{c}}{{{cell_text}}}")
                if current_val.strip() != "" and (r_idx + 1 < len(header_rows)):
                     # 下の行のセル構成を見て線を引くか判断（簡易的に全部引く）
                     cmidrules.append(f"\\cmidrule(lr){{{c_idx+1}-{c_idx+colspan}}}")
            else:
                row_latex.append(cell_text)
            c_idx += colspan
        
        latex.append(" & ".join(row_latex) + " \\\\")
        if cmidrules: latex.append(" ".join(cmidrules))

    latex.append(f"\\midrule")
    for _, row in body_df.iterrows():
        row_str = " & ".join([str(x) if x is not None else "" for x in row])
        latex.append(f"{row_str} \\\\")
    latex.append(f"\\bottomrule")
    latex.append(f"\\end{{tabular}}")
    latex.append(f"\\end{{table}}")
    return "\n".join(latex)

# 入力モードの選択
tab1, tab2, tab3 = st.tabs(["📋 Notion貼り付け", "🎨 インタラクティブ表作成", "📉 高度表作成"])

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

with tab3:
    st.subheader("🧩 リアルタイム・プレビュー付き表作成")
    st.markdown("""
    **使い方：** 隣り合ったセルに**「同じ文字」**を入力すると、下のプレビュー画面で自動的に結合されます。
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
        st.session_state.header_data_tab3 = edited_header

        st.write("###### 2. データ入力")
        edited_body = st.data_editor(
            st.session_state.body_data_tab3,
            key="body_editor_t3",
            width="stretch"  # リクエスト通り変更
        )
        st.session_state.body_data_tab3 = edited_body

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
