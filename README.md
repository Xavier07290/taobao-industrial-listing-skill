# 淘宝工业品主图与详情页生成 Skill

当前版本 **V1.3.0**：在下述 V1.2 工作流上加入已测试的工程修复，范围见 [docs/V1.3_RELEASE.md](docs/V1.3_RELEASE.md)。

一套跨 Agent 可复用的淘宝工业品视觉生产与上品资料工作流，适用于手拉葫芦、手扳葫芦、电动葫芦、搬运车、卷扬机、千斤顶、磁力吊、钢丝绳、吊装索具及五金机电产品。

**输入：**真实产品照片 + 厂家参数/Excel + 同类竞品图片 + 用户认可的风格参考。

**V1.2 默认输出：**5张独立3:4主图、1张白底图、8张独立详情屏、1张详情长图、设计蓝图、事实表和QA报告。完整ZIP只有在真实文件全部通过检查后才生成。

## V1.2 的核心变化

- **质量优先、先审核再批量：**先完成一张核心成交图，用户确认设计方向后再继续整套图片。
- **高度参考竞品版式：**分析构图、版面分区、产品占比、标题位置、信息层级、卖点卡片和阅读路径；保留通用版式逻辑，替换本商品的产品、品牌、文字和素材。
- **真实产品锁定：**产品主体使用用户实拍原图抠图和图层合成，不让生成模型重新绘制机械产品。
- **确定性排版：**中文、型号、铭牌、数字、单位和参数表使用准确文本后期排版。
- **真正可复用的工具：**增加 Pillow 图层合成、详情长图拼接、总览生成和严格文件验证脚本。
- **机器检查与视觉检查分离：**尺寸检查通过不代表产品外观、参数或视觉质量已经通过。

## 核心规则

1. 产品真实外观以用户上传的真实产品图为唯一依据。
2. 技术参数只使用厂家资料、铭牌或用户明确确认的信息。
3. 竞品图用于高参考度学习版式和营销逻辑，不复制品牌、完整文案或专有图稿。
4. 五张主图必须分别制作和导出，不能从总拼版裁切。
5. 详情页先制作八张独立屏，再无损拼接成长图。
6. 任何未完成或未通过检查的文件都必须如实标记。

## 快速调用

调用 taobao-industrial-listing-skill 的 IMAGE_PACK 模式。使用我提供的真实产品图、厂家参数、同类竞品图片和风格参考。高度参考竞品的版式、信息层级和构图，采用黑红工业风，质量优先。先完成一张核心成交图供我审核；确认后再逐张生成五张独立主图、白底图、八屏详情页和完整长图。产品必须使用真实图层合成，参数和中文必须准确排版，最后提供单张图片与通过检查的ZIP。

## 文件结构

- SKILL.md：跨 Agent 主入口
- references/delivery-contract.md：交付条件与禁止事项
- references/production-workflow.md：V1.2生产流程
- references/visual-system.md：竞品版式映射和视觉系统
- references/prompt-templates.md：背景、产品合成和排版提示
- references/competitor-layout-analysis-template.md：竞品拆解模板
- references/design-master-template.md：设计蓝图模板
- examples/layout-example.json：图层合成示例
- scripts/render_layout.py：确定性图层合成
- scripts/compose_detail_long.py：详情页拼接
- scripts/make_contact_sheet.py：总览预览
- scripts/verify_and_package.py：图片检查与ZIP打包

## 安装

将仓库克隆或复制到支持 Agent Skills 的客户端技能目录。Codex、Claude Code 等客户端的具体目录和调用方式见 README-安装说明.md。普通对话中提及 Skill 名称并不代表客户端已经安装它。

图层合成和质检脚本需要 Python 3.10+ 与 Pillow：

    python -m pip install -r requirements.txt

本地脚本命令与隔离测试见 [docs/LOCAL_RUN.md](docs/LOCAL_RUN.md)，V1.2 工程审计、测试结果及修复记录见 [docs/V1.2_AUDIT.md](docs/V1.2_AUDIT.md)。

## 能力边界

Skill 是生产规范和辅助脚本，不是图像模型或自动上架权限。背景生成、产品抠图和视觉审核仍依赖当前 Agent 可用的图像工具。严格保真时，产品图必须作为独立真实图层合成；单纯文字提示不能保证模型不改变机械结构。

淘宝正式发布、价格、库存、物流和售后承诺必须由用户核实并授权。
