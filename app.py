import streamlit as st
import pandas as pd
from attendance_auto_input import AttendanceAutoInput
import io
import os

st.set_page_config(
    page_title="TimeFiller", 
    layout="centered",
    page_icon="📋"
)

# Header
st.title("📋 TimeFiller")
st.write("CSVファイルの勤務データをExcelの業務報告書に自動入力します。")

# Usage instructions at the top
with st.expander("📖 使い方", expanded=False):
    st.markdown("""
    1. **CSVファイル**（勤務データ）をアップロードします。
    2. **Excelファイル**（業務報告書のテンプレート）をアップロードします。
    3. **苗字と名前**を入力します。
    4. **「自動入力を実行」**ボタンを押します。
    5. 処理が完了すると、**ダウンロードボタン**が表示されます。
    """)

st.divider()

# Step 1: File Upload
st.header("📁 1. ファイルのアップロード")

# CSV Upload
uploaded_csv = st.file_uploader("【必須】CSVファイル (勤務データ)", type="csv", key="csv_uploader")

# Show CSV download instructions right below CSV uploader
if not uploaded_csv:
    with st.expander("💡 ジョブカンからのCSV取得方法"):
        st.markdown("""
        1. **ジョブカン勤怠管理**にログインします。
        2. 左側メニューの**「出勤簿」**をクリックします。
        3. **「指定月」**で取得したい月を選択します。
        4. ダウンロードボタン付近のラジオボタンで**「CSV」**を選択し、ダウンロードします。
        """)

# Display CSV file info and preview
if uploaded_csv:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.success(f"✅ {uploaded_csv.name}")
    with col2:
        file_size = uploaded_csv.size / 1024  # Convert to KB
        st.caption(f"サイズ: {file_size:.1f} KB")
    
    # CSV Preview
    with st.expander("👁️ CSVプレビュー（最初の5行）"):
        try:
            # Read CSV for preview
            csv_preview = pd.read_csv(uploaded_csv)
            st.dataframe(csv_preview.head(), use_container_width=True)
            # Reset file pointer for later use
            uploaded_csv.seek(0)
        except Exception as e:
            st.error(f"CSVの読み込みに失敗しました: {e}")

st.write("")  # Add spacing

# Excel Upload
uploaded_excel = st.file_uploader("【必須】Excelファイル (業務報告書)", type="xlsx", key="excel_uploader")

# Display Excel file info
if uploaded_excel:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.success(f"✅ {uploaded_excel.name}")
    with col2:
        file_size = uploaded_excel.size / 1024  # Convert to KB
        st.caption(f"サイズ: {file_size:.1f} KB")

st.divider()

# Step 2: Name Input
st.header("👤 2. 氏名の入力")
col1, col2 = st.columns(2)
with col1:
    surname = st.text_input("【必須】苗字", placeholder="例: 山田", key="surname_input")
with col2:
    given_name = st.text_input("【必須】名前", placeholder="例: 太郎", key="given_name_input")

# Combine for full name
full_name = f"{surname} {given_name}" if surname and given_name else ""

# Real-time validation feedback
if surname or given_name:
    if surname and given_name:
        st.success(f"✅ 氏名: {full_name}")
    else:
        if not surname:
            st.warning("⚠️ 苗字を入力してください")
        if not given_name:
            st.warning("⚠️ 名前を入力してください")

st.divider()

# Step 3: Execute
if uploaded_csv and uploaded_excel:
    st.header("⚙️ 3. 処理の実行")
    
    # Disable button if name is not complete
    button_disabled = not (surname and given_name)
    
    if button_disabled:
        st.info("💡 氏名を入力すると実行ボタンが有効になります")
    
    if st.button("🚀 自動入力を実行", type="primary", disabled=button_disabled):
        with st.spinner("⏳ 処理中..."):
            try:
                # Create tool instance with file objects
                tool = AttendanceAutoInput(uploaded_csv, uploaded_excel, surname, full_name)
                
                # Run process
                result_stream = tool.process()
                
                if result_stream:
                    st.divider()
                    st.header("💾 4. ダウンロード")
                    st.success("✨ 処理が完了しました！")
                    
                    # Generate filename for download
                    original_filename = uploaded_excel.name
                    if surname:
                        if '〇〇' in original_filename:
                            output_filename = original_filename.replace('〇〇', surname)
                        else:
                            output_filename = original_filename.replace('.xlsx', f'_{surname}.xlsx')
                    else:
                        filename_base = original_filename.rsplit('.', 1)[0]
                        output_filename = f"{filename_base}_processed.xlsx"
                    
                    st.download_button(
                        label="📥 作成されたExcelファイルをダウンロード",
                        data=result_stream,
                        file_name=output_filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary"
                    )
                    
                    st.balloons()
                else:
                    st.error("❌ 処理に失敗しました。ログを確認してください。")
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {e}")
                st.exception(e)

else:
    st.info("💡 CSVファイルとExcelファイルの両方をアップロードしてください。")
