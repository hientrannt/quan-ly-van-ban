import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import plotly.express as px
import plotly.graph_objects as go

# Cấu hình trang
st.set_page_config(
    page_title="Hệ Thống Quản Lý Văn Bản DHG",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {padding: 0rem 1rem;}
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    div[data-testid="metric-container"] {
        background: rgba(28, 131, 225, 0.1);
        border: 1px solid rgba(28, 131, 225, 0.2);
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }

    /* Calendar Styles - Full Container */
    .calendar-container {
        width: 100%;
        height: 85vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }

    .calendar-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        padding: 15px 20px;
        background: #f8f9fa;
        border-radius: 12px 12px 0 0;
        border-bottom: 2px solid #e0e0e0;
    }

    .calendar-title {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        flex: 1;
    }

    .calendar-stats {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
    }

    .stat-card {
        background: white;
        padding: 10px 16px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        text-align: center;
        min-width: 90px;
    }

    .stat-card:nth-child(1) {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    }

    .stat-card:nth-child(2) {
        background: linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%);
    }

    .stat-card:nth-child(3) {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
    }

    .stat-value {
        font-size: 22px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 4px;
    }

    .stat-label {
        font-size: 11px;
        color: #666;
        font-weight: 500;
    }

    .calendar-weekdays {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        background: #e0e0e0;
        gap: 7px;
        padding: 7px 7px 0 7px;
    }

    .calendar-weekday {
        background: #e0e0e0;
        text-align: center;
        padding: 10px 8px;
        font-weight: 600;
        font-size: 13px;
        color: #2c3e50;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .calendar-weekday.sunday {
        color: #e74c3c;
    }

    .calendar-weekday.saturday {
        color: #3498db;
    }

    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        background: #f8f9fa;
        gap: 7px;
        flex: 1;
        overflow-y: auto;
        padding: 7px;
    }

    .calendar-day {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        min-height: 120px;
        padding: 8px;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
        transition: all 0.3s;
    }

    .calendar-day:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .calendar-day.other-month {
        opacity: 0.4;
        background: #fafafa;
    }

    .calendar-day.today {
        border-color: #f99d07;
        background: #fff8f085;
    }

    .day-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        padding-bottom: 6px;
        border-bottom: 1px solid #e0e0e0;
    }

    .day-number {
        font-size: 13px;
        font-weight: 600;
        color: #2c3e50;
    }

    .day-number.sunday {
        color: #e74c3c;
    }

    .day-number.saturday {
        color: #3498db;
    }

    .event-count {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: #ffebeb;
        color: #f43737;
        font-weight: 700;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 10px;
        margin-left: 4px;
    }

    .lunar-date {
        font-size: 11px;
        color: #888;
        margin-bottom: 5px;
        font-style: italic;
    }

    .lunar-special {
        font-size: 11px;
        color: #d63031;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .events-list {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 5px;
    }

    .event-item {
        background: linear-gradient(135deg, #fff9e6 0%, #fffef9 100%);
        padding: 4px 6px;
        border-radius: 6px;
        border-left: 3px solid #3782f4;
        display: flex;
        flex-direction: column;
        gap: 2px;
        transition: all 0.3s;
        cursor: pointer;
        min-height: 28px;
    }

    .event-item:hover {
        background: linear-gradient(135deg, #fff3cc 0%, #fffcf0 100%);
        transform: translateX(3px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }

    .event-time {
        font-weight: bold;
        font-size: 11px;
        color: #666;
    }

    .event-content {
        font-size: 11px;
        color: #333;
        line-height: 1.3;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .event-location {
        font-size: 10px;
        color: #888;
        font-style: italic;
    }

    /* Responsive */
    @media (max-width: 1199px) {
        .calendar-grid {
            grid-template-columns: repeat(4, 1fr);
        }
        .calendar-weekday:nth-child(5),
        .calendar-weekday:nth-child(6),
        .calendar-weekday:nth-child(7) {
            display: none;
        }
    }

    @media (max-width: 768px) {
        .calendar-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .calendar-weekday:nth-child(3),
        .calendar-weekday:nth-child(4),
        .calendar-weekday:nth-child(5),
        .calendar-weekday:nth-child(6),
        .calendar-weekday:nth-child(7) {
            display: none;
        }
        .calendar-header {
            flex-direction: column;
        }
        .calendar-stats {
            order: -1;
        }
    }
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None

if 'calendar_month' not in st.session_state:
    st.session_state.calendar_month = datetime.now().month
if 'calendar_year' not in st.session_state:
    st.session_state.calendar_year = datetime.now().year

# ===== LUNAR CALENDAR FUNCTIONS =====
import math
import calendar

def jd_from_date(dd, mm, yy):
    """Tính Julian Day Number từ ngày dương lịch"""
    a = math.floor((14 - mm) / 12)
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + math.floor((153 * m + 2) / 5) + 365 * y + math.floor(y / 4) - math.floor(y / 100) + math.floor(y / 400) - 32045
    if jd < 2299161:
        jd = dd + math.floor((153 * m + 2) / 5) + 365 * y + math.floor(y / 4) - 32083
    return jd

def sun_longitude(jdn):
    """Tính góc mặt trời"""
    T = (jdn - 2451545.0) / 36525
    T2 = T * T
    dr = math.pi / 180
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    DL = DL + (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(dr * 3 * M)
    L = L0 + DL
    L = L - 360 * math.floor(L / 360)
    return L

def new_moon(k):
    """Tính thời điểm trăng non"""
    PI = math.pi
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = PI / 180
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 = Jd1 + 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
    C1 = C1 - 0.4068 * math.sin(Mpr * dr) + 0.0161 * math.sin(dr * 2 * Mpr)
    C1 = C1 - 0.0004 * math.sin(dr * 3 * Mpr)
    C1 = C1 + 0.0104 * math.sin(dr * 2 * F) - 0.0051 * math.sin(dr * (M + Mpr))
    C1 = C1 - 0.0074 * math.sin(dr * (M - Mpr)) + 0.0004 * math.sin(dr * (2 * F + M))
    C1 = C1 - 0.0004 * math.sin(dr * (2 * F - M)) - 0.0006 * math.sin(dr * (2 * F + Mpr))
    C1 = C1 + 0.001 * math.sin(dr * (2 * F - Mpr)) + 0.0005 * math.sin(dr * (2 * Mpr + M))
    if T < -11:
        deltat = 0.001 + 0.000839 * T + 0.0002261 * T2 - 0.00000845 * T3 - 0.000000081 * T * T3
    else:
        deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
    JdNew = Jd1 + C1 - deltat
    return JdNew

def get_new_moon_day(k, timeZone):
    """Tìm ngày bắt đầu tháng âm lịch"""
    jd = new_moon(k)
    return math.floor(jd + 0.5 + timeZone / 24)

def get_lunar_month_11(yy, timeZone):
    """Tìm tháng 11 âm lịch"""
    off = jd_from_date(31, 12, yy) - 2415021
    k = math.floor(off / 29.530588853)
    nm = get_new_moon_day(k, timeZone)
    sunLong = math.floor(sun_longitude(nm) / 30)
    if sunLong >= 9:
        nm = get_new_moon_day(k - 1, timeZone)
    return nm

def get_leap_month_offset(a11, timeZone):
    """Tìm năm nhuận"""
    k = math.floor((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    last = 0
    i = 1
    arc = math.floor(sun_longitude(get_new_moon_day(k + i, timeZone)) / 30)
    while arc != last and i < 14:
        last = arc
        i += 1
        arc = math.floor(sun_longitude(get_new_moon_day(k + i, timeZone)) / 30)
    return i - 1

def convert_solar_to_lunar(dd, mm, yy, timeZone=7):
    """Chuyển đổi dương lịch sang âm lịch"""
    dayNumber = jd_from_date(dd, mm, yy)
    k = math.floor((dayNumber - 2415021.076998695) / 29.530588853)
    monthStart = get_new_moon_day(k + 1, timeZone)
    if monthStart > dayNumber:
        monthStart = get_new_moon_day(k, timeZone)

    a11 = get_lunar_month_11(yy, timeZone)
    b11 = a11

    if a11 >= monthStart:
        lunarYear = yy
        a11 = get_lunar_month_11(yy - 1, timeZone)
    else:
        lunarYear = yy + 1
        b11 = get_lunar_month_11(yy + 1, timeZone)

    lunarDay = dayNumber - monthStart + 1
    diff = math.floor((monthStart - a11) / 29)
    lunarLeap = 0
    lunarMonth = diff + 11

    if b11 - a11 > 365:
        leapMonthDiff = get_leap_month_offset(a11, timeZone)
        if diff >= leapMonthDiff:
            lunarMonth = diff + 10
            if diff == leapMonthDiff:
                lunarLeap = 1

    if lunarMonth > 12:
        lunarMonth = lunarMonth - 12
    if lunarMonth >= 11 and diff < 4:
        lunarYear -= 1

    return {'day': lunarDay, 'month': lunarMonth, 'year': lunarYear, 'leap': lunarLeap}

def get_lunar_special_event(lunar_day, lunar_month):
    """Lấy sự kiện đặc biệt từ âm lịch"""
    month_names = ["Giêng", "Hai", "Ba", "Tư", "Năm", "Sáu", "Bảy", "Tám", "Chín", "Mười", "Mười Một", "Chạp"]
    month_name = month_names[lunar_month - 1]

    if lunar_day == 1 and lunar_month == 1:
        return 'Mùng 1 Tết'
    elif 2 <= lunar_day <= 4 and lunar_month == 1:
        return f'Tết (Mùng {lunar_day})'
    elif lunar_day == 30 and lunar_month == 12:
        return 'Giao Thừa'
    elif lunar_day == 15:
        return f'Rằm Tháng {month_name}'
    elif lunar_day == 5 and lunar_month == 5:
        return 'Tết Đoan Ngọ'
    elif 1 < lunar_day <= 10:
        return f'Mùng {lunar_day} Tháng {month_name}'
    else:
        return f'{lunar_day} Tháng {month_name}'

# Hàm tạo data demo
def create_demo_data():
    """Tạo data demo để test khi không có file Excel"""
    # Tạo dữ liệu calendar demo
    calendar_events = []
    today = datetime.now()

    # Tạo các sự kiện định kỳ
    for week in range(4):
        # Chủ nhật hàng tuần
        sunday = today.replace(day=1) + timedelta(days=week*7 + (6 - today.replace(day=1).weekday() + 7) % 7)
        if sunday.month == today.month:
            calendar_events.append({
                'Ngày dương': sunday,
                'Giờ': '07:30',
                'Nội dung': f'ĐỀ NGHỊ CẤP VỐN ngày {sunday.strftime("%d/%m/%Y")}',
                'Địa điểm': 'Phòng họp A'
            })

    # Thứ 5 và 6 hàng tuần
    for day in range(1, 32):
        try:
            date = today.replace(day=day)
            if date.month != today.month:
                continue
            weekday = date.weekday()
            if weekday in [3, 4]:  # Thứ 5 và Thứ 6
                calendar_events.append({
                    'Ngày dương': date,
                    'Giờ': '08:00',
                    'Nội dung': 'Đảm bảo số liệu đúng thời gian',
                    'Địa điểm': 'Văn phòng'
                })
        except:
            break

    # Thêm sự kiện đặc biệt
    calendar_events.append({
        'Ngày dương': today.replace(day=19) if today.month == 11 else today,
        'Giờ': '19:00',
        'Nội dung': 'Chụp đồng hồ nước',
        'Địa điểm': 'Nhà'
    })

    calendar_df = pd.DataFrame(calendar_events)

    return {
        'Users': pd.DataFrame({
            'ID': [1, 2],
            'Tên đăng nhập': ['admin', 'user'],
            'Mật khẩu': ['Hientran', '123456'],
            'Email': ['admin@test.com', 'user@test.com'],
            'Quyền': ['admin', 'user'],
            'Trạng thái': ['active', 'active'],
            'Đăng nhập cuối': [datetime.now(), datetime.now()]
        }),
        'Calendar': calendar_df,
        'Documents': pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Tên văn bản': ['VB001 - Thông báo nghỉ lễ', 'VB002 - Quy định làm việc', 
                           'VB003 - Hướng dẫn sử dụng', 'VB004 - Chính sách bán hàng',
                           'VB005 - Quy trình ISO'],
            'Danh mục': ['Thông báo', 'Quy định', 'Hướng dẫn', 'Chính sách', 'Quy trình'],
            'Phòng ban': ['Nhân sự', 'Nhân sự', 'IT', 'Kinh doanh', 'Chất lượng'],
            'Ngày ban hành': [datetime.now() - timedelta(days=i*5) for i in range(5)],
            'Trạng thái văn bản=': ['Còn hiệu lực', 'Còn hiệu lực', 'Hết hiệu lực', 
                                   'Còn hiệu lực', 'Còn hiệu lực']
        }),
        'Categories': pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Tên danh mục': ['Thông báo', 'Quy định', 'Hướng dẫn', 'Chính sách', 'Quy trình'],
            'Icon': ['📢', '📋', '📖', '📜', '⚙️'],
            'Màu sắc': ['#FF0000', '#00FF00', '#0000FF', '#FFA500', '#800080'],
            'Mô tả': ['Các thông báo', 'Các quy định', 'Tài liệu hướng dẫn', 
                     'Chính sách công ty', 'Quy trình làm việc']
        }),
        'Departments': pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Tên phòng ban': ['Nhân sự', 'IT', 'Kế toán', 'Kinh doanh', 'Chất lượng'],
            'Mô tả': ['Phòng nhân sự', 'Phòng IT', 'Phòng kế toán', 
                     'Phòng kinh doanh', 'Phòng chất lượng']
        }),
        'InvoiceDocuments': pd.DataFrame({
            'ID': [1, 2],
            'Số Chứng Từ': ['CT001', 'CT002'],
            'Tên Chứng Từ': ['Hóa đơn mua hàng', 'Phiếu chi'],
            'Danh mục': ['Chứng từ', 'Chứng từ'],
            'Phòng ban': ['Kế toán', 'Kế toán'],
            'Ngày Phát Hành': [datetime.now(), datetime.now() - timedelta(days=1)],
            'Trạng thái': ['Active', 'Active']
        })
    }

# Hàm đọc dữ liệu Excel
@st.cache_data
def load_excel_data(file):
    """Load tất cả sheets từ file Excel"""
    try:
        excel_data = {}
        xls = pd.ExcelFile(file)
        for sheet_name in xls.sheet_names:
            excel_data[sheet_name] = pd.read_excel(file, sheet_name=sheet_name)
        return excel_data
    except Exception as e:
        st.error(f"Lỗi khi đọc file: {e}")
        return None

# Hàm login
def check_login(username, password, users_df):
    """Kiểm tra đăng nhập"""
    user = users_df[(users_df['Tên đăng nhập'] == username) & 
                    (users_df['Mật khẩu'] == password)]
    if not user.empty:
        return True, user.iloc[0]['Quyền']
    return False, None

# Hàm hiển thị metrics
def show_dashboard_metrics(data):
    """Hiển thị thống kê tổng quan"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📄 Tổng văn bản", len(data.get('Documents', [])))
    with col2:
        st.metric("📑 Chứng từ", len(data.get('InvoiceDocuments', [])))
    with col3:
        st.metric("👥 Người dùng", len(data.get('Users', [])))
    with col4:
        st.metric("🏢 Phòng ban", len(data.get('Departments', [])))
    with col5:
        st.metric("📁 Danh mục", len(data.get('Categories', [])))

# Hàm tìm kiếm
def search_documents(df, search_term):
    """Tìm kiếm trong DataFrame"""
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        return df[mask]
    return df

# Hàm render calendar
def render_calendar(year, month, events_df=None):
    """Render calendar với events - FULL CONTAINER với Stats"""
    import calendar as cal

    # Tạo calendar cho tháng
    cal_obj = cal.monthcalendar(year, month)

    # Tên tháng
    month_names = ["", "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
                   "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"]

    # Tên ngày trong tuần
    weekdays = ["TH 2", "TH 3", "TH 4", "TH 5", "TH 6", "TH 7", "CN"]

    # Chuẩn bị events dict và tính stats
    events_dict = {}
    total_events = 0
    if events_df is not None and len(events_df) > 0:
        for _, event in events_df.iterrows():
            event_date = event.get('Ngày dương')
            if isinstance(event_date, datetime):
                if event_date.year == year and event_date.month == month:
                    day = event_date.day
                    if day not in events_dict:
                        events_dict[day] = []
                    events_dict[day].append({
                        'time': event.get('Giờ', ''),
                        'content': event.get('Nội dung', ''),
                        'location': event.get('Địa điểm', '')
                    })
                    total_events += 1

    # Tính số ngày có công việc
    days_with_events = len(events_dict)

    # Tính upcoming events (7 ngày tới)
    today = datetime.now()
    upcoming_count = 0
    if events_df is not None and len(events_df) > 0:
        for _, event in events_df.iterrows():
            event_date = event.get('Ngày dương')
            if isinstance(event_date, datetime):
                if today <= event_date <= today + timedelta(days=7):
                    upcoming_count += 1

    # Tạo HTML với Stats
    html = f"""
    <div class="calendar-container">
        <div class="calendar-header">
            <div class="calendar-stats">
                <div class="stat-card">
                    <div class="stat-value">{total_events}</div>
                    <div class="stat-label">Tổng công việc</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{days_with_events}</div>
                    <div class="stat-label">Ngày có việc</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{upcoming_count}</div>
                    <div class="stat-label">7 ngày tới</div>
                </div>
            </div>

            <div class="calendar-title">
                {month_names[month]} năm {year}
            </div>
        </div>

        <div class="calendar-weekdays">
    """

    # Header ngày trong tuần
    for i, day in enumerate(weekdays):
        css_class = 'sunday' if i == 6 else ('saturday' if i == 5 else '')
        html += f'<div class="calendar-weekday {css_class}">{day}</div>'

    html += '</div><div class="calendar-grid">'

    # Render từng tuần
    for week in cal_obj:
        for day in week:
            if day == 0:
                # Ngày của tháng khác
                html += '<div class="calendar-day other-month"></div>'
            else:
                # Ngày của tháng hiện tại
                date_obj = datetime(year, month, day)
                weekday = date_obj.weekday()

                # Xác định CSS class
                css_classes = ['calendar-day']
                day_num_class = ''

                if date_obj.date() == today.date():
                    css_classes.append('today')

                if weekday == 6:  # Chủ nhật
                    day_num_class = 'sunday'
                elif weekday == 5:  # Thứ 7
                    day_num_class = 'saturday'

                # Tính âm lịch
                lunar = convert_solar_to_lunar(day, month, year)
                lunar_special = get_lunar_special_event(lunar['day'], lunar['month'])

                # Đếm số events trong ngày
                event_count = len(events_dict.get(day, []))

                # Bắt đầu render ngày với day-header
                html += f'<div class="{" ".join(css_classes)}">'
                html += '<div class="day-header">'
                html += f'<div class="day-number {day_num_class}">{day:02d}/{month:02d}'
                if event_count > 0:
                    html += f'<span class="event-count">{event_count}</span>'
                html += '</div></div>'

                html += f'<div class="lunar-date">{lunar["day"]:02d}/{lunar["month"]:02d} ÂL</div>'

                # Hiển thị ngày âm đặc biệt
                if lunar['day'] in [1, 15] or (lunar['day'] >= 2 and lunar['day'] <= 4 and lunar['month'] == 1):
                    html += f'<div class="lunar-special">{lunar_special}</div>'

                # Hiển thị events trong events-list
                if day in events_dict:
                    html += '<div class="events-list">'
                    for event in events_dict[day]:
                        time_str = event['time'] if event['time'] else ''
                        content = event['content']
                        location = event['location'] if event['location'] else ''

                        html += '<div class="event-item">'
                        if time_str:
                            html += f'<span class="event-time">{time_str}</span>'
                        html += f'<span class="event-content">{content}</span>'
                        if location:
                            html += f'<span class="event-location">📍 {location}</span>'
                        html += '</div>'
                    html += '</div>'

                html += '</div>'

    html += '</div></div>'

    return html

# Main App
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/4285f4/ffffff?text=DHG+PHARMA", use_column_width=True)
        st.title("📄 Quản lý Văn bản")
        
        # Tùy chọn nguồn dữ liệu
        use_demo = st.checkbox("🎯 Dùng data demo", value=True, 
                               help="Tick để dùng data demo, bỏ tick để upload file")
        
        data = None
        
        if not use_demo:
            # Upload file Excel
            uploaded_file = st.file_uploader(
                "Tải file Excel",
                type=['xlsx', 'xls'],
                help="Upload file Excel quản lý văn bản"
            )
            
            if uploaded_file:
                st.success("✅ Đã tải file thành công!")
                data = load_excel_data(uploaded_file)
        else:
            # Dùng data demo
            st.info("🎯 Đang dùng data demo")
            st.caption("Tài khoản: admin / Hientran")
            data = create_demo_data()
        
        # Login section nếu có data
        if data:
            if not st.session_state.logged_in:
                st.divider()
                st.subheader("🔐 Đăng nhập")
                
                username = st.text_input("Tên đăng nhập", value="admin" if use_demo else "")
                password = st.text_input("Mật khẩu", type="password", 
                                        value="Hientran" if use_demo else "")
                
                if st.button("Đăng nhập", type="primary", use_container_width=True):
                    is_valid, role = check_login(username, password, data['Users'])
                    
                    if is_valid:
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_role = role
                        st.rerun()
                    else:
                        st.error("Sai tên đăng nhập hoặc mật khẩu!")
            else:
                st.divider()
                st.info(f"👤 Xin chào: **{st.session_state.username}**")
                st.info(f"🎯 Quyền: **{st.session_state.user_role}**")
                
                if st.button("🚪 Đăng xuất", use_container_width=True):
                    st.session_state.logged_in = False
                    st.session_state.username = None
                    st.session_state.user_role = None
                    st.rerun()
    
    # Main content area
    if data and st.session_state.logged_in:
        # Header
        st.title("🏢 HỆ THỐNG QUẢN LÝ VĂN BẢN DHG PHARMA")
        st.caption(f"Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Metrics
        show_dashboard_metrics(data)
        st.divider()
        
        # Tabs cho các chức năng
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["🏠 Tổng quan", "📄 Văn bản", "📑 Chứng từ", "👥 Người dùng", "📁 Danh mục", "📅 Lịch"]
        )
        
        with tab1:
            st.header("🏠 Tổng quan hệ thống")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📄 Văn bản mới nhất")
                if 'Documents' in data and len(data['Documents']) > 0:
                    recent_docs = data['Documents'].head(5)
                    display_cols = ['Tên văn bản', 'Danh mục']
                    display_cols = [col for col in display_cols if col in recent_docs.columns]
                    if display_cols:
                        st.dataframe(recent_docs[display_cols], use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("📑 Chứng từ mới nhất")
                if 'InvoiceDocuments' in data and len(data['InvoiceDocuments']) > 0:
                    recent_inv = data['InvoiceDocuments'].head(5)
                    display_cols = ['Tên Chứng Từ', 'Phòng ban']
                    display_cols = [col for col in display_cols if col in recent_inv.columns]
                    if display_cols:
                        st.dataframe(recent_inv[display_cols], use_container_width=True, hide_index=True)
            
            # Biểu đồ
            if 'Documents' in data and 'Danh mục' in data['Documents'].columns:
                st.subheader("📊 Thống kê theo danh mục")
                category_counts = data['Documents']['Danh mục'].value_counts()
                fig = px.pie(values=category_counts.values, names=category_counts.index)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.header("📄 Quản lý Văn bản")
            
            # Tìm kiếm
            search = st.text_input("🔍 Tìm kiếm văn bản")
            
            if 'Documents' in data:
                filtered = search_documents(data['Documents'], search)
                
                # Editor
                edited_docs = st.data_editor(
                    filtered,
                    use_container_width=True,
                    height=400,
                    num_rows="dynamic"
                )
                
                if st.button("💾 Lưu thay đổi", type="primary"):
                    st.success("Đã lưu thay đổi!")
        
        with tab3:
            st.header("📑 Quản lý Chứng từ")
            
            if 'InvoiceDocuments' in data:
                st.data_editor(
                    data['InvoiceDocuments'],
                    use_container_width=True,
                    height=400,
                    num_rows="dynamic"
                )
        
        with tab4:
            st.header("👥 Quản lý Người dùng")
            
            if st.session_state.user_role == "admin":
                if 'Users' in data:
                    st.data_editor(
                        data['Users'],
                        use_container_width=True,
                        column_config={
                            "Mật khẩu": st.column_config.TextColumn("Mật khẩu", disabled=True)
                        }
                    )
            else:
                st.warning("⚠️ Bạn không có quyền xem trang này!")
        
        with tab5:
            st.header("📁 Quản lý Danh mục")

            if 'Categories' in data:
                st.data_editor(
                    data['Categories'],
                    use_container_width=True,
                    num_rows="dynamic"
                )

        with tab6:
            st.header("📅 Lịch Công Việc")

            # Controls
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

            with col1:
                selected_month = st.selectbox(
                    "Chọn tháng",
                    range(1, 13),
                    index=st.session_state.calendar_month - 1,
                    format_func=lambda x: f"Tháng {x}"
                )

            with col2:
                selected_year = st.selectbox(
                    "Chọn năm",
                    range(2020, 2031),
                    index=range(2020, 2031).index(st.session_state.calendar_year)
                )

            with col3:
                if st.button("◀ Tháng trước"):
                    if st.session_state.calendar_month == 1:
                        st.session_state.calendar_month = 12
                        st.session_state.calendar_year -= 1
                    else:
                        st.session_state.calendar_month -= 1
                    st.rerun()

            with col4:
                if st.button("Tháng sau ▶"):
                    if st.session_state.calendar_month == 12:
                        st.session_state.calendar_month = 1
                        st.session_state.calendar_year += 1
                    else:
                        st.session_state.calendar_month += 1
                    st.rerun()

            # Update session state nếu user chọn từ dropdown
            if selected_month != st.session_state.calendar_month:
                st.session_state.calendar_month = selected_month
                st.rerun()
            if selected_year != st.session_state.calendar_year:
                st.session_state.calendar_year = selected_year
                st.rerun()

            # Lọc events cho tháng hiện tại
            events_df = None
            if 'Calendar' in data and data['Calendar'] is not None and len(data['Calendar']) > 0:
                calendar_data = data['Calendar'].copy()

                # Lọc theo tháng và năm
                filtered_events = []
                for _, row in calendar_data.iterrows():
                    event_date = row.get('Ngày dương')
                    if isinstance(event_date, datetime):
                        if event_date.month == st.session_state.calendar_month and event_date.year == st.session_state.calendar_year:
                            filtered_events.append(row)

                if filtered_events:
                    events_df = pd.DataFrame(filtered_events)

            # Render calendar
            calendar_html = render_calendar(
                st.session_state.calendar_year,
                st.session_state.calendar_month,
                events_df
            )

            st.markdown(calendar_html, unsafe_allow_html=True)

            # Thêm form tạo event mới
            st.divider()
            st.subheader("➕ Thêm công việc mới")

            with st.form("add_event_form"):
                col1, col2 = st.columns(2)

                with col1:
                    new_event_date = st.date_input("Ngày", datetime.now())
                    new_event_time = st.time_input("Giờ", datetime.now().replace(hour=8, minute=0))

                with col2:
                    new_event_content = st.text_input("Nội dung công việc")
                    new_event_location = st.text_input("Địa điểm")

                submitted = st.form_submit_button("💾 Lưu công việc", type="primary")

                if submitted:
                    if new_event_content:
                        # Thêm event mới vào data
                        new_event = {
                            'Ngày dương': datetime.combine(new_event_date, new_event_time),
                            'Giờ': new_event_time.strftime('%H:%M'),
                            'Nội dung': new_event_content,
                            'Địa điểm': new_event_location
                        }

                        if 'Calendar' not in data or data['Calendar'] is None:
                            data['Calendar'] = pd.DataFrame([new_event])
                        else:
                            data['Calendar'] = pd.concat([data['Calendar'], pd.DataFrame([new_event])], ignore_index=True)

                        st.success("✅ Đã thêm công việc thành công!")
                        st.rerun()
                    else:
                        st.error("⚠️ Vui lòng nhập nội dung công việc!")

    elif not data:
        # Welcome screen
        st.title("🏢 HỆ THỐNG QUẢN LÝ VĂN BẢN DHG PHARMA")
        st.info("👈 Vui lòng chọn nguồn dữ liệu ở sidebar (Demo hoặc Upload file)")
        
        # Hướng dẫn
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🎯 Cách 1: Dùng Data Demo
            1. Tick ✅ "Dùng data demo" ở sidebar
            2. Đăng nhập: **admin / Hientran**
            3. Khám phá các tính năng
            """)
        
        with col2:
            st.markdown("""
            ### 📤 Cách 2: Upload File Excel
            1. Bỏ tick "Dùng data demo"
            2. Upload file Excel của bạn
            3. Đăng nhập với tài khoản trong file
            """)
        
        # Tạo file Excel mẫu
        if st.button("📥 Tải file Excel mẫu"):
            demo_data = create_demo_data()
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                for sheet_name, df in demo_data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            st.download_button(
                label="💾 Download Excel mẫu",
                data=buffer.getvalue(),
                file_name="demo_quan_ly_van_ban.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    elif not st.session_state.logged_in:
        st.warning("⚠️ Vui lòng đăng nhập để sử dụng hệ thống")

# Run app
if __name__ == "__main__":
    main()
