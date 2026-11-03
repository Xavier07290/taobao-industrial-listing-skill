# 安装与使用说明

本仓库遵循常见 Agent Skills 文件夹布局，主入口为根目录的 `SKILL.md`。这份 Skill 用于批量制作工业品淘宝图片与上品资料，**不是已经连接千牛的自动上架机器人**。

## Codex

将仓库克隆或复制到项目的 `.agents/skills/taobao-industrial-listing-skill/`，然后在Codex中指名本Skill。若客户端没有图像生成、图层合成和导出工具，需要另配相应能力。

## Claude Code

将本文件夹放到项目 `.claude/skills/taobao-industrial-listing-skill/`，然后在Claude Code中调用。实际功能由运行环境支持的工具决定。

## ChatGPT

自定义Skill安装入口随账户与工作空间权限而异。若有自定义Skills导入能力，可导入完整文件夹或压缩包；否则在支持的工作空间用此说明作为参考，不能把普通对话中提及名称当作已安装。

## 调用示例

```text
调用 taobao-industrial-listing-skill 的 IMAGE_PACK 模式。
当前产品实拍、厂家参数表、同类竞品图已提供。
参考竞品营销卖点和版式，采用黑红白工业电商风。
严格锁定我自己的产品外观、铭牌与配件数量。
生成五张独立3:4主图、白底图及八屏详情长图。
技术参数必须可证实，并附带QA报告。
```

## 使用边界

本仓库不包含淘宝账号密码、Cookie、内部采购价、厂家全量报价表，也不包括品牌官方授权的声明。正式商品发布前，应检查图片、Logo、技术宣称和商品数据。