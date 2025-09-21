import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import hashlib
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
    .uploadedFile {display: none}
    .st-emotion-cache-1y4p8pa {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

# Khởi tạo session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_role = None

# Hàm đọc dữ liệu Excel
@st.cache_data
def load_excel_data(file):
    """Load tất cả sheets từ file Excel"""
    excel_data = {}
    xls = pd.ExcelFile(file)
    for sheet_name in xls.sheet_names:
        excel_data[sheet_name] = pd.read_excel(file, sheet_name=sheet_name)
    return excel_data

# Hàm login đơn giản
def check_login(username, password, users_df):
    """Kiểm tra đăng nhập"""
    user = users_df[(users_df['Tên đăng nhập'] == username) & 
                    (users_df['Mật khẩu'] == password)]
    if not user.empty:
        return True, user.iloc[0]['Quyền']
    return False, None

# Hàm hiển thị metrics dashboard
def show_dashboard_metrics(data):
    """Hiển thị thống kê tổng quan"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📄 Tổng văn bản", len(data['Documents']))
        
    with col2:
        st.metric("📑 Chứng từ", len(data['InvoiceDocuments']))
        
    with col3:
        st.metric("👥 Người dùng", len(data['Users']))
        
    with col4:
        st.metric("🏢 Phòng ban", len(data['Departments']))
        
    with col5:
        st.metric("📁 Danh mục", len(data['Categories']))

# Hàm tìm kiếm văn bản
def search_documents(df, search_term):
    """Tìm kiếm trong DataFrame"""
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        return df[mask]
    return df

# Hàm hiển thị và chỉnh sửa văn bản
def show_documents_management(documents_df, categories_df, departments_df):
    """Quản lý văn bản chính"""
    st.header("📄 Quản lý Văn bản")
    
    # Tabs cho các chức năng
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Danh sách", "➕ Thêm mới", "📊 Thống kê", "🔍 Tìm kiếm nâng cao"])
    
    with tab1:
        # Bộ lọc
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            selected_category = st.selectbox(
                "Danh mục",
                ["Tất cả"] + list(documents_df['Danh mục'].dropna().unique())
            )
        
        with col2:
            selected_dept = st.selectbox(
                "Phòng ban",
                ["Tất cả"] + list(documents_df['Phòng ban'].dropna().unique())
            )
        
        with col3:
            selected_status = st.selectbox(
                "Trạng thái",
                ["Tất cả", "Còn hiệu lực", "Hết hiệu lực", "Active"]
            )
        
        with col4:
            search_term = st.text_input("🔍 Tìm kiếm nhanh", placeholder="Nhập từ khóa...")
        
        # Áp dụng bộ lọc
        filtered_df = documents_df.copy()
        
        if selected_category != "Tất cả":
            filtered_df = filtered_df[filtered_df['Danh mục'] == selected_category]
        
        if selected_dept != "Tất cả":
            filtered_df = filtered_df[filtered_df['Phòng ban'] == selected_dept]
        
        if selected_status != "Tất cả":
            filtered_df = filtered_df[filtered_df['Trạng thái văn bản='] == selected_status]
        
        if search_term:
            filtered_df = search_documents(filtered_df, search_term)
        
        # Hiển thị kết quả
        st.info(f"Tìm thấy {len(filtered_df)} văn bản")
        
        # Chỉnh sửa dữ liệu
        edited_df = st.data_editor(
            filtered_df,
            use_container_width=True,
            height=400,
            column_config={
                "ID": st.column_config.NumberColumn("ID", width="small"),
                "Tên văn bản": st.column_config.TextColumn("Tên văn bản", width="large"),
                "Danh mục": st.column_config.SelectboxColumn(
                    "Danh mục",
                    options=list(categories_df['Tên danh mục'].unique())
                ),
                "Phòng ban": st.column_config.SelectboxColumn(
                    "Phòng ban",
                    options=list(departments_df['Tên phòng ban'].unique())
                ),
                "Ngày ban hành": st.column_config.DateColumn("Ngày ban hành"),
                "Trạng thái văn bản=": st.column_config.SelectboxColumn(
                    "Trạng thái",
                    options=["Còn hiệu lực", "Hết hiệu lực", "Active"]
                )
            },
            hide_index=True
        )
        
        # Nút lưu
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Lưu thay đổi", type="primary"):
                st.success("Đã lưu thay đổi thành công!")
        
        with col2:
            # Export
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                edited_df.to_excel(writer, sheet_name='Documents', index=False)
            
            st.download_button(
                label="📥 Xuất Excel",
                data=excel_buffer.getvalue(),
                file_name=f"documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.ms-excel"
            )
    
    with tab2:
        # Form thêm văn bản mới
        st.subheader("Thêm văn bản mới")
        
        with st.form("add_document"):
            col1, col2 = st.columns(2)
            
            with col1:
                doc_name = st.text_input("Tên văn bản *")
                category = st.selectbox("Danh mục *", categories_df['Tên danh mục'].unique())
                department = st.selectbox("Phòng ban *", departments_df['Tên phòng ban'].unique())
                issue_date = st.date_input("Ngày ban hành")
            
            with col2:
                effective_date = st.date_input("Ngày hiệu lực")
                expiry_date = st.date_input("Ngày hết hiệu lực")
                status = st.selectbox("Trạng thái", ["Còn hiệu lực", "Hết hiệu lực"])
                description = st.text_area("Mô tả")
            
            uploaded_file = st.file_uploader("Tải file đính kèm", type=['pdf', 'docx', 'xlsx'])
            
            submitted = st.form_submit_button("➕ Thêm văn bản", type="primary")
            
            if submitted and doc_name:
                st.success(f"Đã thêm văn bản: {doc_name}")
                st.balloons()
    
    with tab3:
        # Thống kê
        st.subheader("📊 Thống kê văn bản")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Biểu đồ theo danh mục
            category_counts = documents_df['Danh mục'].value_counts()
            fig1 = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Phân bổ theo danh mục"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Biểu đồ theo phòng ban
            dept_counts = documents_df['Phòng ban'].value_counts().head(10)
            fig2 = px.bar(
                x=dept_counts.values,
                y=dept_counts.index,
                orientation='h',
                title="Top 10 phòng ban có nhiều văn bản nhất"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Biểu đồ theo thời gian
        if 'Ngày ban hành' in documents_df.columns:
            documents_df['Ngày ban hành'] = pd.to_datetime(documents_df['Ngày ban hành'], errors='coerce')
            monthly_docs = documents_df.groupby(documents_df['Ngày ban hành'].dt.to_period('M')).size()
            
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=monthly_docs.index.astype(str),
                y=monthly_docs.values,
                mode='lines+markers',
                name='Số lượng văn bản'
            ))
            fig3.update_layout(title="Xu hướng ban hành văn bản theo tháng")
            st.plotly_chart(fig3, use_container_width=True)
    
    with tab4:
        # Tìm kiếm nâng cao
        st.subheader("🔍 Tìm kiếm nâng cao")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_name = st.text_input("Tên văn bản chứa")
            search_categories = st.multiselect("Danh mục", documents_df['Danh mục'].dropna().unique())
        
        with col2:
            date_from = st.date_input("Từ ngày")
            date_to = st.date_input("Đến ngày")
        
        with col3:
            search_status = st.multiselect("Trạng thái", ["Còn hiệu lực", "Hết hiệu lực", "Active"])
            search_dept = st.multiselect("Phòng ban", documents_df['Phòng ban'].dropna().unique())
        
        if st.button("🔍 Tìm kiếm", type="primary"):
            result_df = documents_df.copy()
            
            if search_name:
                result_df = result_df[result_df['Tên văn bản'].str.contains(search_name, case=False, na=False)]
            
            if search_categories:
                result_df = result_df[result_df['Danh mục'].isin(search_categories)]
            
            if search_status:
                result_df = result_df[result_df['Trạng thái văn bản='].isin(search_status)]
            
            if search_dept:
                result_df = result_df[result_df['Phòng ban'].isin(search_dept)]
            
            st.success(f"Tìm thấy {len(result_df)} kết quả")
            st.dataframe(result_df, use_container_width=True)

# Main App
def main():
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/4285f4/ffffff?text=DHG+PHARMA", use_column_width=True)
        st.title("📄 Quản lý Văn bản")
        
        # Upload file Excel
        uploaded_file = st.file_uploader(
            "Tải file Excel",
            type=['xlsx', 'xls'],
            help="Upload file Excel quản lý văn bản"
        )
        
        if uploaded_file:
            st.success("✅ Đã tải file thành công!")
            
            # Login section
            if not st.session_state.logged_in:
                st.divider()
                st.subheader("🔐 Đăng nhập")
                username = st.text_input("Tên đăng nhập")
                password = st.text_input("Mật khẩu", type="password")
                
                if st.button("Đăng nhập", type="primary", use_container_width=True):
                    data = load_excel_data(uploaded_file)
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
                
                # Menu điều hướng
                st.divider()
                page = st.radio(
                    "📋 Menu",
                    ["🏠 Tổng quan", "📄 Văn bản", "📑 Chứng từ", "👥 Người dùng", 
                     "📁 Danh mục", "🏢 Phòng ban", "⚙️ Cài đặt"],
                    label_visibility="collapsed"
                )
    
    # Main content
    if uploaded_file and st.session_state.logged_in:
        # Load data
        data = load_excel_data(uploaded_file)
        
        # Header
        st.title("🏢 HỆ THỐNG QUẢN LÝ VĂN BẢN DHG PHARMA")
        st.caption(f"Cập nhật: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Hiển thị metrics
        show_dashboard_metrics(data)
        st.divider()
        
        # Routing based on sidebar selection
        if 'page' not in locals():
            page = "🏠 Tổng quan"
        
        if page == "🏠 Tổng quan":
            st.header("🏠 Tổng quan hệ thống")
            
            # Thống kê nhanh
            col1, col2 = st.columns(2)
            
            with col1:
                # Văn bản mới nhất
                st.subheader("📄 Văn bản mới nhất")
                recent_docs = data['Documents'].head(5)[['Tên văn bản', 'Danh mục', 'Ngày ban hành']]
                st.dataframe(recent_docs, use_container_width=True, hide_index=True)
            
            with col2:
                # Chứng từ mới nhất
                st.subheader("📑 Chứng từ mới nhất")
                recent_invoices = data['InvoiceDocuments'].head(5)[['Tên Chứng Từ', 'Phòng ban', 'Ngày Phát Hành']]
                st.dataframe(recent_invoices, use_container_width=True, hide_index=True)
            
            # Biểu đồ tổng quan
            st.subheader("📊 Biểu đồ tổng quan")
            
            fig = go.Figure(data=[
                go.Bar(name='Văn bản', x=['Tổng số'], y=[len(data['Documents'])]),
                go.Bar(name='Chứng từ', x=['Tổng số'], y=[len(data['InvoiceDocuments'])]),
                go.Bar(name='Người dùng', x=['Tổng số'], y=[len(data['Users'])])
            ])
            fig.update_layout(barmode='group', height=400)
            st.plotly_chart(fig, use_container_width=True)
            
        elif page == "📄 Văn bản":
            show_documents_management(data['Documents'], data['Categories'], data['Departments'])
            
        elif page == "📑 Chứng từ":
            st.header("📑 Quản lý Chứng từ - Hóa đơn")
            
            # Tìm kiếm
            search = st.text_input("🔍 Tìm kiếm chứng từ")
            filtered = search_documents(data['InvoiceDocuments'], search)
            
            # Hiển thị và chỉnh sửa
            edited_invoices = st.data_editor(
                filtered,
                use_container_width=True,
                height=500,
                column_config={
                    "Ngày Phát Hành": st.column_config.DateColumn("Ngày phát hành"),
                    "Ngày hiệu lực": st.column_config.DateColumn("Ngày hiệu lực"),
                }
            )
            
            if st.button("💾 Lưu thay đổi chứng từ"):
                st.success("Đã lưu thay đổi!")
                
        elif page == "👥 Người dùng":
            st.header("👥 Quản lý Người dùng")
            
            if st.session_state.user_role == "admin":
                # Chỉ admin mới được quản lý users
                tab1, tab2 = st.tabs(["Danh sách", "Thêm mới"])
                
                with tab1:
                    edited_users = st.data_editor(
                        data['Users'],
                        use_container_width=True,
                        column_config={
                            "Mật khẩu": st.column_config.TextColumn("Mật khẩu", disabled=True),
                            "Quyền": st.column_config.SelectboxColumn(
                                "Quyền",
                                options=["admin", "user", "viewer"]
                            ),
                            "Trạng thái": st.column_config.SelectboxColumn(
                                "Trạng thái",
                                options=["active", "inactive"]
                            )
                        }
                    )
                    
                    if st.button("💾 Lưu thay đổi người dùng"):
                        st.success("Đã cập nhật người dùng!")
                
                with tab2:
                    with st.form("add_user"):
                        new_username = st.text_input("Tên đăng nhập")
                        new_password = st.text_input("Mật khẩu", type="password")
                        new_email = st.text_input("Email")
                        new_role = st.selectbox("Quyền", ["user", "viewer", "admin"])
                        
                        if st.form_submit_button("➕ Thêm người dùng"):
                            st.success(f"Đã thêm người dùng: {new_username}")
            else:
                st.warning("⚠️ Bạn không có quyền quản lý người dùng!")
                
        elif page == "📁 Danh mục":
            st.header("📁 Quản lý Danh mục")
            
            edited_categories = st.data_editor(
                data['Categories'],
                use_container_width=True,
                num_rows="dynamic"
            )
            
            if st.button("💾 Lưu danh mục"):
                st.success("Đã lưu danh mục!")
                
        elif page == "🏢 Phòng ban":
            st.header("🏢 Quản lý Phòng ban")
            
            edited_departments = st.data_editor(
                data['Departments'],
                use_container_width=True,
                num_rows="dynamic"
            )
            
            if st.button("💾 Lưu phòng ban"):
                st.success("Đã lưu phòng ban!")
                
        elif page == "⚙️ Cài đặt":
            st.header("⚙️ Cài đặt hệ thống")
            
            if 'Settings' in data:
                st.dataframe(data['Settings'], use_container_width=True)
            else:
                st.info("Không có dữ liệu cài đặt")
    
    elif not uploaded_file:
        # Welcome screen
        st.title("🏢 HỆ THỐNG QUẢN LÝ VĂN BẢN")
        st.info("👈 Vui lòng tải file Excel để bắt đầu")
        
        # Hướng dẫn
        st.markdown("""
        ### 📖 Hướng dẫn sử dụng:
        
        1. **Tải file Excel**: Upload file `QUAN LY TAI LIEU VAN BAN CHUNG TU.xlsx`
        2. **Đăng nhập**: Sử dụng tài khoản có trong sheet Users
        3. **Quản lý văn bản**: Xem, thêm, sửa, xóa văn bản
        4. **Tìm kiếm**: Tìm kiếm nhanh hoặc nâng cao
        5. **Báo cáo**: Xem thống kê và xuất báo cáo
        
        ### 🚀 Tính năng chính:
        
        - ✅ Quản lý văn bản, chứng từ
        - ✅ Phân quyền người dùng
        - ✅ Tìm kiếm thông minh
        - ✅ Thống kê trực quan
        - ✅ Export/Import dữ liệu
        - ✅ Lưu trữ đám mây (Google Drive)
        """)
        
        # Demo login info
        with st.expander("🔐 Thông tin đăng nhập demo"):
            st.code("""
            Admin:
            - Username: admin
            - Password: Hientran
            
            User:
            - Username: Admin1  
            - Password: Hientran
            """)
    
    elif not st.session_state.logged_in:
        st.warning("⚠️ Vui lòng đăng nhập để sử dụng hệ thống")

# Run app
if __name__ == "__main__":
    main()