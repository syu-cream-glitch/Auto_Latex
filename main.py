import streamlit as st
from tool import tab1, tab2, tab3

st.set_page_config(page_title="LaTeX表作成ツール", layout="wide")

st.title("📊 LaTeX表作成ツール")

st.markdown("""
このツールで表を作成し，リアルタイムでLaTeX形式のコードを生成できます．
また，Notionなどのツールからコピーした表を貼り付けてLaTeX形式に変換することもできます．
""")

# 入力モードの選択
tab1_render, tab2_render, tab3_render = st.tabs(["📋 Notion貼り付け", "🎨 インタラクティブ表作成", "📉 高度表作成"])

with tab1_render:
    tab1.render_tab1()

with tab2_render:
    tab2.render_tab2()

with tab3_render:
    tab3.render_tab3()

# 使い方の説明
with st.expander("📚 使い方"):
    st.markdown("""
    ## 📋 Notion表の貼り付け
    1. NotionやExcelで表を選択してコピー（Ctrl+C）
    2. 上のテキストエリアに貼り付けてください．タブ区切りで自動認識します．
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
    [LaTeXコードをここに挿入]
    \\end{document}
    ```
    """)

st.markdown("---")
st.caption("💡 表の値を変更すると，LaTeXコードが自動的に更新されます．")
