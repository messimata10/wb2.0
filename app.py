import streamlit as st
import pandas as pd
import json
import random

def load_data_and_quotes():
    """加载数据和金句"""
    data = {}
    try:
        data['df'] = pd.read_csv('finance_with_predictions_day6.csv')
    except Exception as e:
        st.error(f"数据加载失败: {e}")
        return None, None
        
    quotes = {"buffett": [], "multi_disc": {}, "llm": {}}
    try:
        with open("buffett_quotes.txt", "r", encoding="utf-8") as f:
            quotes["buffett"] = [line.strip() for line in f if line.strip()]
        with open("multi_disc_quotes.json", "r", encoding="utf-8") as f:
            quotes["multi_disc"] = json.load(f)
        with open("llm_generated_quotes.json", "r", encoding="utf-8") as f:
            quotes["llm"] = json.load(f)
    except Exception as e:
        st.warning(f"部分金句加载失败: {e}")
    
    return data, quotes

def get_random_quote(quotes):
    """获取随机金句"""
    if random.random() < 0.5 and quotes["buffett"]:
        return "[巴菲特] " + random.choice(quotes["buffett"])
    elif quotes["multi_disc"]:
        field = random.choice(list(quotes["multi_disc"].keys()))
        return f"[{field}] " + random.choice(quotes["multi_disc"][field])
    return "金句加载失败"

def main():
    # 页面配置
    st.set_page_config(
        page_title="金融数据分析平台",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("金融数据分析平台 📈")
    
    # 加载数据和金句
    data, quotes = load_data_and_quotes()
    if data is None:
        st.error("数据加载失败，请检查数据文件。")
        return
        
    # 侧边栏 - 公司选择
    with st.sidebar:
        st.header("📊 数据筛选")
        companies = sorted(data['df']['company'].unique())
        selected_company = st.selectbox("选择公司", companies)
        
    # 获取选中公司数据
    company_data = data['df'][data['df']['company'] == selected_company].copy()
    
    # 三层分析的标签页
    tab1, tab2, tab3 = st.tabs(["Quick(3s)", "Intermediate(5min)", "Deep(30min)"])
    
    # Quick(3s) 分析
    with tab1:
        st.subheader("Quick(3s) - 快速诊断")
        if st.button("一键分析"):
            if not company_data.empty:
                latest = company_data.iloc[-1]
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("公司状态", latest.get('multi_state', 'N/A'))
                    st.metric("预测收入", f"¥{latest.get('revenue', 0):,.2f}")
                
                with col2:
                    st.info(get_random_quote(quotes))
                    
    # Intermediate(5min) 分析
    with tab2:
        st.subheader("Intermediate(5min) - 趋势分析")
        if not company_data.empty:
            # 财务趋势图
            metrics = ['revenue', 'n_income', 'net_operate_cash_flow']
            available_metrics = [m for m in metrics if m in company_data.columns]
            
            if available_metrics:
                st.line_chart(
                    company_data[['year'] + available_metrics].set_index('year')
                )
            
            # 增长模拟
            col1, col2 = st.columns(2)
            with col1:
                growth = st.slider("增长预期 (%)", -20, 20, 0)
                latest_revenue = company_data['revenue'].iloc[-1]
                projected = latest_revenue * (1 + growth/100)
                st.metric(
                    "预计收入",
                    f"¥{projected:,.2f}",
                    f"{growth:+.1f}%"
                )
            
            with col2:
                st.subheader("多维度点评")
                for _ in range(2):
                    st.info(get_random_quote(quotes))
    
    # Deep(30min) 分析
    with tab3:
        st.subheader("Deep(30min) - 深度分析")
        
        # 完整数据表格
        st.dataframe(company_data)
        
        # 关键指标分析
        st.subheader("核心指标分析")
        if not company_data.empty:
            latest = company_data.iloc[-1]
            cols = st.columns(3)
            
            with cols[0]:
                st.metric(
                    "资产负债率",
                    f"{(latest.get('total_liab', 0) / latest.get('total_assets', 1) * 100):.1f}%"
                )
            
            with cols[1]:
                st.metric(
                    "净利率",
                    f"{(latest.get('n_income', 0) / latest.get('revenue', 1) * 100):.1f}%"
                )
            
            with cols[2]:
                st.metric(
                    "现金流比率",
                    f"{(latest.get('net_operate_cash_flow', 0) / latest.get('revenue', 1) * 100):.1f}%"
                )
        
        # AI深度点评
        st.subheader("AI 深度观点")
        if selected_company in quotes["llm"]:
            st.success(quotes["llm"][selected_company])
        else:
            st.info(get_random_quote(quotes))

if __name__ == "__main__":
    main()
