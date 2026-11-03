# 淘宝工业品主图与详情页生成 Skill

一套面向淘宝工业品与五金机电商家的可复用 Agent Skill，支持手拉葫芦、手扳葫芦、电动葫芦、搬运车、卷扬机、千斤顶、磁力吊、吊装索具等多种产品。

**核心输入：真实产品照片 + 厂家参数表 + 同类竞品主图/详情截图。**

**默认输出：**5张独立3:4商品主图（建议1440×1920）、1张白底图、8屏详情页及完整长图。可选生成标题、SKU建议、商家编码和上品前质检报告。

## 核心规则

- **产品真实外观锁定：**不重画、不增删吊钩/链条/零件、不改颜色/铭牌/Logo/比例；优先真实图片抠图与分层合成。
- **竞品参考只提炼营销逻辑：**可学习卖点方向、构图、信息层级，但不直接复制品牌、图像、完整文案。
- **参数必须可核验：**厂家资料或铭牌未确认的“双刹车”“G80链条”等不得擅自写入。
- **视觉统一：**黑红白工业电商风，真实产品主体、清晰细节与参数表。
- **先质检后上品：**图片、技术事实、中文字、尺寸与平台合规逐项检查。

## 快速调用

> 调用 `taobao-industrial-listing-skill` 的 IMAGE_PACK 模式。用我提供的真实产品图、厂家参数及同类竞品图，参考竞品卖点和版式，按黑红工业风生成5张独立3:4主图、白底图和8屏详情长图。产品外观与铭牌不允许改变，未知参数不要编造。

## 主要文件

- [SKILL.md](SKILL.md)：Agent Skills 主入口
- [references/production-workflow.md](references/production-workflow.md)：各类工业品制作步骤
- [references/prompt-templates.md](references/prompt-templates.md)：图片编辑与排版提示词
- [references/visual-system.md](references/visual-system.md)：视觉设计规范
- [examples/hst-golden-sample.md](examples/hst-golden-sample.md)：HS-T案例使用原则
- [安装说明](README-安装说明.md)：Codex、Claude Code、ChatGPT等使用方法

## 安装

下载或克隆本仓库，将文件夹放入支持 Agent Skills 的客户端技能目录。例如 Codex 项目的 `.agents/skills/taobao-industrial-listing-skill/`、Claude Code 项目的 `.claude/skills/taobao-industrial-listing-skill/`。

Skill 是流程与规则，不会自动附加图像生成、抠图或浏览器操作权限。要精确保留产品外观，须使用支持真实图层合成的工具。

## 免责声明

这是独立的通用电商图片工作流，不代表任何品牌官方或平台授权。示例产品和品牌信息仅用于描述制作方法。实际发布前应人工核对产品规格、技术参数、图片权利及宣传内容。
