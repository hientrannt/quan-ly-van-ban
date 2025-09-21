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
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None

# Hàm tạo data demo
def create_demo_data():
    """Tạo data demo để test khi không có file Excel"""
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
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            ["🏠 Tổng quan", "📄 Văn bản", "📑 Chứng từ", "👥 Người dùng", "📁 Danh mục"]
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
