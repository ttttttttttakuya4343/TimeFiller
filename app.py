import streamlit as st
import pandas as pd
from attendance_auto_input import AttendanceAutoInput
import io
import os

st.set_page_config(page_title="TimeFiller", layout="centered")

st.title("TimeFiller")
st.write("CSVファイルの勤務データをExcelの業務報告書に自動入力します。")

# File Uploaders
st.header("1. ファイルのアップロード")

uploaded_csv = st.file_uploader("【必須】CSVファイル (勤務データ)", type="csv")
uploaded_excel = st.file_uploader("【必須】Excelファイル (業務報告書)", type="xlsx")

st.header("2. 氏名の入力")
col1, col2 = st.columns(2)
with col1:
    surname = st.text_input("【必須】苗字", placeholder="例: 山田")
with col2:
    given_name = st.text_input("【必須】名前", placeholder="例: 太郎")

# Combine for full name
full_name = f"{surname} {given_name}" if surname and given_name else ""

if uploaded_csv and uploaded_excel:
    st.success("ファイルがアップロードされました！")
    
    st.header("3. 処理の実行")
    if st.button("自動入力を実行", type="primary"):
        if not surname or not given_name:
            st.error("苗字と名前を入力してください。")
        else:
            with st.spinner("処理中..."):
                try:
                    # Create tool instance with file objects
                    # Note: Streamlit file objects work directly with pandas and openpyxl
                    tool = AttendanceAutoInput(uploaded_csv, uploaded_excel, surname, full_name)
                    
                    # Run process
                    # Since we didn't provide an output path, it returns a BytesIO stream
                    result_stream = tool.process()
                    
                    if result_stream:
                        st.success("処理が完了しました！")
                        
                        # Generate filename for download
                        original_filename = uploaded_excel.name
                        if surname:
                            # Replace '〇〇' with surname if present, otherwise just prepend/append?
                            # User request: "〇〇の部分には、勤務表作成者の苗字が入ります"
                            if '〇〇' in original_filename:
                                output_filename = original_filename.replace('〇〇', surname)
                            else:
                                # If 〇〇 is not found, maybe just insert it or keep original?
                                # Let's try to be smart but safe.
                                output_filename = original_filename.replace('.xlsx', f'_{surname}.xlsx')
                        else:
                            filename_base = original_filename.rsplit('.', 1)[0]
                            output_filename = f"{filename_base}_processed.xlsx"
                        
                        st.header("4. ダウンロード")
                        st.download_button(
                            label="作成されたExcelファイルをダウンロード",
                            data=result_stream,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        st.error("処理に失敗しました。ログを確認してください。")
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
                    st.exception(e)

else:
    st.info("CSVファイルとExcelファイルの両方をアップロードしてください。")

# Instructions
with st.expander("使い方"):
    st.markdown("""
    1. **CSVファイル**（勤務データ）をアップロードします。
    2. **Excelファイル**（業務報告書のテンプレート）をアップロードします。
    3. **「自動入力を実行」**ボタンを押します。
    4. 処理が完了すると、**ダウンロードボタン**が表示されます。
    """)

with st.expander("ジョブカンからのCSV取得方法"):
    st.markdown("""
    1. **ジョブカン勤怠管理**にログインします。
    2. 左側メニューの**「出勤簿」**をクリックします。
    3. **「指定月」**で取得したい月を選択します。
    4. ダウンロードボタン付近のラジオボタンで**「CSV」**を選択し、ダウンロードします。
    """)
