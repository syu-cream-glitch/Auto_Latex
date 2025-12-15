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