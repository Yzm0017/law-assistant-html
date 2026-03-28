"""
婚姻家事AI法律助手
律师私有化部署 · MiniMax-2.7 加持
"""

import streamlit as st
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env 配置
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# MiniMax API
from openai import OpenAI

# ==================== 配置 ====================
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"

# 页面配置
st.set_page_config(
    page_title="婚姻家事AI法律助手",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        padding: 1rem 0;
        border-bottom: 2px solid #e94560;
        margin-bottom: 2rem;
    }
    .function-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
    }
    .result-box {
        background: #f8f9fa;
        border-left: 4px solid #e94560;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .disclaimer {
        background: #fff3cd;
        border: 1px solid #ffc107;
        padding: 1rem;
        border-radius: 8px;
        font-size: 0.85rem;
        color: #856404;
    }
    .stButton > button {
        background: linear-gradient(135deg, #e94560 0%, #0f3460 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 访问密码 ====================
def check_password():
    """简单密码保护"""
    def password_entered():
        if st.session_state.get("password") == "law2026":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔑 请输入访问密码", type="password", on_change=password_entered, key="password")
        st.stop()
    elif not st.session_state["password_correct"]:
        st.text_input("🔑 密码错误，请重新输入", type="password", on_change=password_entered, key="password")
        st.stop()


# ==================== 初始化 ====================
@st.cache_resource
def init_client():
    if not MINIMAX_API_KEY:
        return None
    return OpenAI(api_key=MINIMAX_API_KEY, base_url=MINIMAX_BASE_URL)


def call_ai(client, prompt, system_prompt=None):
    """调用MiniMax-2.7"""
    if client is None:
        return "❌ API未配置，请设置 MINIMAX_API_KEY 环境变量"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="MiniMax-M2.7",
            messages=messages,
            temperature=0.3,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ 调用失败：{str(e)}"


# ==================== 系统提示词 ====================
SYSTEM_DIVORCE_AGREEMENT = """你是一位专业的婚姻家事律师，擅长起草离婚协议。请根据用户提供的真实信息，起草一份完整、合规的离婚协议。

要求：
1. 语言严谨、专业、条款清晰
2. 财产分割要公平合理，附法律依据
3. 子女抚养条款要写明抚养费、探望权等细节
4. 协议结构：前言 → 子女抚养 → 财产分割 → 债权债务 → 违约责任 → 签署页
5. 最后附"离婚协议使用说明"，提醒当事人注意的事项

输出格式：Markdown"""

SYSTEM_LAW_ADVICE = """你是一位专业的婚姻家事法律顾问。用户会描述一个婚姻纠纷的情况，你需要：

1. 分析案件类型（离婚纠纷/财产分割/抚养权/家暴等）
2. 分析法律关系和适用法条
3. 预测可能的结果
4. 建议需要收集的证据清单
5. 给出初步建议

回答要专业、严谨、有依据。涉及具体数字的要给出参考区间而非确定值。
输出格式：Markdown"""

SYSTEM_CALCULATOR = """你是一个婚姻家事法律计算器。根据用户输入的信息：

1. 计算子女抚养费（参照对方收入的20%-30%，有两个孩子可适当提高）
2. 计算财产分割方案（区分婚前财产和婚后共同财产）
3. 计算婚姻过错赔偿（如果有出轨、家暴等）
4. 给出法律依据

最后输出一个清晰的计算报告，Markdown格式。"""


# ==================== 页面 ====================
def main():
    # 密码验证
    check_password()

    # 标题
    st.markdown('<h1 class="main-header">⚖️ 婚姻家事AI法律助手</h1>', unsafe_allow_html=True)

    # 警告
    st.markdown("""
    <div class="disclaimer">
    ⚠️ <strong>免责声明</strong>：本工具仅供参考，不能替代律师的专业判断。
    具体案件请咨询持证律师，实际法律文件需经双方协商并由法院确认。
    </div>
    """, unsafe_allow_html=True)

    # 功能选择
    tabs = st.tabs([
        "📝 离婚协议生成器",
        "⚖️ 婚姻纠纷咨询",
        "🧮 财产&抚养费计算"
    ])

    client = init_client()

    # ------ Tab 1: 离婚协议 ------
    with tabs[0]:
        st.subheader("离婚协议智能生成器")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**👤 甲方（申请人）信息**")
            party_a_name = st.text_input("姓名", value="张某", key="a_name")
            party_a_id = st.text_input("身份证号", key="a_id")
            party_a_address = st.text_input("住所地", key="a_addr")

            st.markdown("**💰 财产概况**")
            property_info = st.text_area(
                "财产清单",
                value="婚后共同房产一套（位于北京，估值800万），婚后存款200万，婚后购买的汽车一辆（估值30万）",
                height=100,
                key="property"
            )

        with col2:
            st.markdown("**👤 乙方（被申请人）信息**")
            party_b_name = st.text_input("姓名", value="李某", key="b_name")
            party_b_id = st.text_input("身份证号", key="b_id")
            party_b_address = st.text_input("住所地", key="b_addr")

            st.markdown("**👶 子女情况**")
            children_info = st.text_area(
                "子女信息",
                value="婚生女张某某，10周岁，由甲方抚养，乙方每月支付抚养费5000元",
                height=100,
                key="children"
            )

        # 离婚原因
        divorce_reason = st.text_area(
            "💔 离婚原因（简述）",
            value="双方因性格不合导致夫妻感情破裂，已分居满两年",
            height=60,
            key="reason"
        )

        # 其他约定
        other_terms = st.text_area(
            "📋 其他约定事项（选填）",
            value="",
            placeholder="如有特殊约定，请在此说明",
            height=60,
            key="other"
        )

        if st.button("🚀 生成离婚协议", key="gen_divorce"):
            prompt = f"""请根据以下信息生成离婚协议：

【甲方】姓名：{party_a_name}，身份证：{party_a_id}，住所地：{party_a_address}
【乙方】姓名：{party_b_name}，身份证：{party_b_id}，住所地：{party_b_address}

【离婚原因】
{divorce_reason}

【财产状况】
{property_info}

【子女情况】
{children_info}

【其他约定】
{other_terms if other_terms else "无"}"""

            with st.spinner("🤖 AI正在生成协议，请稍候..."):
                result = call_ai(client, prompt, SYSTEM_DIVORCE_AGREEMENT)

            st.session_state['divorce_result'] = result

        if 'divorce_result' in st.session_state:
            st.markdown("---")
            st.markdown("### 📄 离婚协议（草稿）")
            st.markdown('<div class="result-box">' + st.session_state['divorce_result'].replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

            # 下载按钮
            st.download_button(
                "📥 下载协议文本",
                st.session_state['divorce_result'],
                file_name=f"离婚协议_{party_a_name}_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )

    # ------ Tab 2: 婚姻纠纷咨询 ------
    with tabs[1]:
        st.subheader("婚姻纠纷法律咨询")

        case_type = st.selectbox(
            "案件类型",
            ["离婚纠纷", "财产分割纠纷", "抚养权纠纷", "抚养费纠纷", "探望权纠纷", "婚内财产分割", "其他"]
        )

        case_description = st.text_area(
            "📋 请详细描述案件情况",
            value="",
            placeholder="例如：我和丈夫结婚8年，婚后育有一子5岁。丈夫出轨有外遇，我有录音和聊天记录作为证据。婚后共同购买了一套房产，价值600万，剩余房贷200万。请问离婚后财产如何分割？",
            height=150,
            key="case_desc"
        )

        evidence = st.text_area(
            "📎 已收集的证据（选填）",
            value="",
            placeholder="例如：微信聊天记录、录音、照片、转账记录等",
            height=80,
            key="evidence"
        )

        if st.button("🔍 获取法律分析", key="gen_advice"):
            if not case_description:
                st.warning("请输入案件情况")
            else:
                prompt = f"""【案件类型】{case_type}
【案件详情】
{case_description}
【已有证据】
{evidence if evidence else "暂无"}"""

                with st.spinner("🤖 AI正在分析，请稍候..."):
                    result = call_ai(client, prompt, SYSTEM_LAW_ADVICE)

                st.session_state['advice_result'] = result

        if 'advice_result' in st.session_state:
            st.markdown("---")
            st.markdown("### ⚖️ 法律分析报告")
            st.markdown('<div class="result-box">' + st.session_state['advice_result'].replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

    # ------ Tab 3: 计算器 ------
    with tabs[2]:
        st.subheader("财产分割 & 抚养费计算器")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**💼 收入情况**")
            income_a = st.number_input("甲方月收入（元）", value=30000, step=1000, key="inc_a")
            income_b = st.number_input("乙方月收入（元）", value=20000, step=1000, key="inc_b")

            st.markdown("**🏠 房产**")
            has_house = st.checkbox("有房产", value=True)
            if has_house:
                house_value = st.number_input("房产估值（万元）", value=800, step=10, key="house_val")
                house_loan = st.number_input("剩余房贷（万元）", value=200, step=10, key="house_loan")

        with col2:
            st.markdown("**👶 子女情况**")
            num_children = st.number_input("子女数量", value=1, min_value=0, step=1, key="num_child")
            children_ages = st.text_input("子女年龄（如：8岁、5岁）", value="10岁", key="child_ages")

            st.markdown("**⚠️ 过错情况（如有）**")
            has_fault = st.checkbox("存在过错（出轨/家暴/遗弃）")
            fault_type = st.selectbox(
                "过错类型",
                ["无", "重婚", "同居", "家暴", "虐待遗弃", "其他重大过错"],
                index=0,
                key="fault"
            ) if has_fault else "无"

        # 存款/股票等
        st.markdown("**💳 其他共同财产**")
        col_a, col_b = st.columns(2)
        with col_a:
            savings = st.number_input("银行存款（万元）", value=100, step=10, key="savings")
        with col_b:
            stocks = st.number_input("股票/基金（万元）", value=50, step=5, key="stocks")

        if st.button("🧮 计算分割方案", key="gen_calc"):
            prompt = f"""请计算以下婚姻财产分割和抚养费：

【甲方】月收入：{income_a}元
【乙方】月收入：{income_b}元

【房产】
估值：{house_value}万元（若有）
剩余房贷：{house_loan}万元（若有）

【子女】
数量：{num_children}人
年龄：{children_ages}

【过错情况】{fault_type if has_fault else "无"}

【其他财产】
存款：{savings}万元
股票基金：{stocks}万元

请给出：
1. 子女抚养费计算（按月支付）
2. 房产分割方案
3. 其他财产分割方案
4. 如有过错，赔偿金额参考
5. 法律依据"""

            with st.spinner("🤖 AI正在计算，请稍候..."):
                result = call_ai(client, prompt, SYSTEM_CALCULATOR)

            st.session_state['calc_result'] = result

        if 'calc_result' in st.session_state:
            st.markdown("---")
            st.markdown("### 📊 分割方案参考")
            st.markdown('<div class="result-box">' + st.session_state['calc_result'].replace('\n', '<br>') + '</div>', unsafe_allow_html=True)

            st.info("💡 以上为AI参考计算结果，实际分割方案需由法院根据具体情况判定。")


# ==================== 启动 ====================
if __name__ == "__main__":
    main()
