# ⚖️ 婚姻家事AI法律助手

律师私有化部署 · MiniMax-2.7 加持 · 婚姻家事领域专用

## 功能

- 📝 **离婚协议智能生成器**：输入当事人信息，自动生成完整离婚协议草稿
- ⚖️ **婚姻纠纷法律咨询**：输入案件情况，获取AI法律分析和建议
- 🧮 **财产分割 & 抚养费计算器**：快速计算子女抚养费、财产分割方案

## 快速启动

### 1. 安装依赖

```bash
cd ~/law-assistant
python3.11 -m pip install streamlit openai python-dotenv
```

### 2. 配置API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 MiniMax API Key
```

### 3. 启动

```bash
cd ~/law-assistant
python3.11 -m streamlit run app.py
```

启动后访问 http://localhost:8501

## 系统要求

- macOS 12+
- Python 3.11+
- MiniMax API Key

## 免责声明

本工具仅供参考，不能替代律师的专业判断。具体案件请咨询持证律师。
