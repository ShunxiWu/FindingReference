# FindingReference
# 文献引用索引工具 (Literature Citation Indexing Tool)

这是一个基于 Streamlit 和 OpenAI API 的文献引用分析工具，用于自动识别文本中的引用并评估其与研究主题的相关性。

## 功能特点

- 自动识别文本中的引用
- 匹配引用与参考文献
- 评估引用与研究主题的相关性（1-10分）
- 提供引用分析和解释
- 支持结果导出为 CSV 格式
- 实时进度显示
- 分段展示分析结果

## 安装要求

```bash
pip install -r requirements.txt
```

## 环境配置

1. 创建 `.env` 文件并配置以下变量：

```env
OPENAI_API_KEY=你的OpenAI API密钥
SYSTEM_PROMPT=系统提示词
USER_PROMPT=用户提示词
EVALUATION_PROMPT=评估提示词
```

## 使用方法

1. 运行应用：
```bash
streamlit run app.py
```

2. 在网页界面中：
   - 输入研究主题和目标
   - 粘贴参考文献列表
   - 粘贴需要分析的文本
   - 点击"Analyze Citations"开始分析

3. 查看结果：
   - 每个段落的分析结果会分开显示
   - 左侧显示引用分析
   - 右侧显示原文
   - 可导出完整分析结果为CSV文件

## 文件结构
├── app.py # 主应用程序
├── .env # 环境变量配置
├── requirements.txt # 依赖包列表
└── README.md # 说明文档
## 依赖包

- streamlit
- openai
- python-dotenv
- pandas

## 注意事项

1. 请确保 `.env` 文件中包含有效的 OpenAI API 密钥
2. 文本分析可能需要一定时间，请耐心等待
3. 建议将较长文本分批次处理
4. API 调用可能产生费用，请注意使用频率

## 常见问题

1. 如果没有显示结果：
   - 检查 API 密钥是否正确
   - 确认提示词格式正确
   - 查看是否有错误信息显示

2. 如果分析结果不准确：
   - 检查参考文献格式是否规范
   - 调整系统提示词以提高准确度
   - 确保文本段落之间有适当的分隔

## 更新日志

- v1.0.0: 初始版本发布
  - 基本引用分析功能
  - CSV导出支持
  - 实时进度显示

## 贡献指南

欢迎提交 Issues 和 Pull Requests 来改进这个工具。

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过 Issues 提交。
