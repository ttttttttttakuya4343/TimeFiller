# -*- coding: utf-8 -*-
"""
勤務データ自動入力ツール設定ファイル
"""

# Excelファイルの設定
EXCEL_CONFIG = {
    # データ開始行（1から始まる行番号）
    'data_start_row': 13,
    
    # 列の設定（1から始まる列番号）
    'columns': {
        'date': 2,          # B列: 日付
        'weekday': 3,       # C列: 曜日
        'start_time': 4,    # D列: 出勤時刻
        'end_time': 5,      # E列: 退勤時刻
        'break_time': 6,    # F列: 休憩時間
        'work_hours': 7,    # G列: 稼働時間
        'work_content': 8,  # H列: 作業内容
    },
    
    # サマリー行の設定
    'summary': {
        'work_days_row': 9,     # 出勤日数の行
        'work_days_col': 3,     # 出勤日数の列
        'total_hours_row': 10,  # 総稼働時間の行
        'total_hours_col': 3,   # 総稼働時間の列
        'name_cell_row': 7,     # 氏名の行 (C7)
        'name_cell_col': 3,     # 氏名の列 (C7)
    }
}

# CSVファイルの設定
CSV_CONFIG = {
    'encoding': 'utf-8-sig',  # UTF-8 BOM対応
    'date_format': '%Y/%m/%d',
    'time_format': '%H:%M'
}

# 作業内容のデフォルト設定
WORK_CONTENT = {
    'default': '開発業務',
    'vacation': '有休',
    'holiday': ''
}

# 休日区分の設定
HOLIDAY_TYPES = ['公休', '法休', '祝日']

# 勤怠状況の設定
ATTENDANCE_STATUS = {
    'vacation': '有休'
}
