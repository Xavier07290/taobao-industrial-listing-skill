# 安装与使用说明（V1.2）

本仓库是跨 Agent 的工业品图片与淘宝上品素材 Skill。主入口为 SKILL.md。Skill 提供工作流、规范和辅助脚本，不会自动获得图像生成、电脑控制或千牛发布权限。

## Codex

将仓库克隆或复制到项目的 .agents/skills/taobao-industrial-listing-skill/。在 Codex 中明确调用 taobao-industrial-listing-skill。项目内需要有可用的图像生成/编辑能力；运行图层合成和质检脚本需要 Python 3.10+ 与 Pillow。

## Claude Code

将仓库放到项目的 .claude/skills/taobao-industrial-listing-skill/，然后在 Claude Code 中调用。实际图像能力以当前客户端支持的工具为准。

## ChatGPT

自定义 Skill 的导入入口取决于当前账户、客户端和工作空间功能。将完整仓库作为 Skill 导入后才能按名称调用；仅在对话里提到 Skill 名称不代表它已安装。

## 安装图片脚本依赖

在仓库根目录运行：

    python -m pip install -r requirements.txt

脚本说明：
- scripts/render_layout.py：将背景、真实产品图层、图形和准确文字合成；
- scripts/compose_detail_long.py：把八屏详情图无损拼接成长图；
- scripts/make_contact_sheet.py：从最终独立图片生成可选总览；
- scripts/verify_and_package.py：检查15张PNG并打包ZIP。

## 调用示例

调用 taobao-industrial-listing-skill 的 IMAGE_PACK 模式。当前附件包括真实产品图、厂家参数、同类竞品图和风格参考。请高度参考竞品的通用版式、构图和信息层级，使用真实产品图层，参数和中文后期准确排版。质量优先，先做一张核心成交图供我审核，确认后再逐张制作五张主图、白底图、八屏详情页和长图。最后运行QA并提供每张独立图片和ZIP。

## 产品发布边界

本仓库不包含淘宝账号密码、Cookie或厂家机密资料。正式上架前必须由用户核实标题、价格、库存、运费、参数、售后、品牌授权和图片使用权。没有明确授权和浏览器操作工具时，不得声称已经发布商品。