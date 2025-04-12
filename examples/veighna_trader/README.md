# VeighNa Trader - 优化版量化交易平台

这是VeighNa量化交易平台的优化版本，专注于提供更现代化、美观的用户界面和更好的用户体验。

## 主要特点

- **现代化界面设计**：基于深色主题的精美界面，符合当代软件设计理念
- **优化的交互体验**：简化操作流程，提高使用效率
- **增强的视觉反馈**：通过颜色和动画提供更直观的信息展示
- **高DPI支持**：适配高分辨率显示器，保证界面元素清晰显示
- **多接口支持**：完美兼容富途证券等多种交易接口

## 界面优化

相比原版VeighNa平台，本版本进行了以下界面优化：

1. **整体风格**：采用现代化的深色主题，减少视觉疲劳
2. **控件美化**：重新设计了按钮、输入框、表格等控件，提升美观度
3. **交互优化**：改进了窗口布局和导航逻辑，使操作更加直观
4. **视觉反馈**：为关键数据和状态添加了颜色编码，使信息一目了然

## 功能改进

除了界面优化外，还增加了以下功能改进：

1. **订单管理**：增加订单筛选和搜索功能，方便管理大量订单
2. **状态监控**：改进了连接状态显示，提供更直观的服务器连接反馈
3. **图表展示**：优化了K线图表的显示效果，添加了更多技术分析工具
4. **快速启动**：添加了首页快速启动区，常用功能一键直达

## 快速开始

### 安装依赖

```bash
# 安装核心依赖
pip install -e .

# 安装富途接口
pip install -e ./vnpy_futu

# 安装其他应用模块
pip install -e ./vnpy_ctastrategy
pip install -e ./vnpy_ctabacktester
pip install -e ./vnpy_datamanager
```

### 启动平台

```bash
# 直接启动
python examples/veighna_trader/run.py

# 或使用脚本启动
cd examples/veighna_trader
./run.sh
```

## 自定义主题

平台支持定制界面主题，您可以：

1. 修改 `examples/veighna_trader/custom_style.qss` 文件来自定义界面样式
2. 在设置中选择深色或浅色主题
3. 调整字体大小和字体类型以适应个人偏好

## 贡献指南

欢迎贡献代码或提出改进建议：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 许可证

本项目遵循与原版VeighNa相同的许可证。

## 致谢

- 感谢VeighNa团队开发的优秀量化交易平台
- 感谢所有为本项目提供反馈和建议的用户