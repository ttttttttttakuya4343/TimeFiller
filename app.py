import streamlit as st
import pandas as pd
from attendance_auto_input import AttendanceAutoInput
import io
import os

def check_password():
    """Returns `True` if the user had the correct password."""

    password = os.environ.get("APP_PASSWORD")
    if not password:
        # No password set, allow access
        return True

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input
        st.text_input(
            "パスワードを入力してください", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "パスワードを入力してください", type="password", on_change=password_entered, key="password"
        )
        st.error("パスワードが違います")
        return False
    else:
        # Password correct
        return True

st.set_page_config(page_title="TimeFiller", layout="centered")

if not check_password():
    st.stop()

st.title("TimeFiller")
st.write("CSVファイルの勤務データをExcelの業務報告書に自動入力します。")

# File Uploaders
st.header("1. ファイルのアップロード")

uploaded_csv = st.file_uploader("CSVファイル (勤務データ)", type="csv")
uploaded_excel = st.file_uploader("Excelファイル (業務報告書)", type="xlsx")

st.header("2. 氏名の入力")
col1, col2 = st.columns(2)
with col1:
    surname = st.text_input("苗字", placeholder="例: 山田")
with col2:
    given_name = st.text_input("名前", placeholder="例: 太郎")

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
