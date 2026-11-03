# 本地运行与复测（V1.3）

所有命令从仓库根目录运行。Python 3.10+；唯一第三方运行依赖为 requirements.txt 中的 Pillow，测试使用标准库 unittest。字体和真实图层是外部素材，不会由 pip 安装。

## 1. 环境

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$py = (Resolve-Path .\.venv\Scripts\python.exe).Path
$env:PYTHONUTF8 = '1'
& $py -m unittest discover -s tests -v
```

若桌面环境没有 PATH 中的 python，可使用客户端发现的 Python 运行时，将 `$py` 设置为其路径，并检查依赖：

```powershell
& $py -c "import sys,PIL; print(sys.version); print(PIL.__version__)"
```

不同客户端的路径可能不同，不应依赖固定用户目录。

## 2. 生成隔离测试包

```powershell
& $py tests/smoke_delivery.py outputs/engineering-test-new
```

必须指定尚不存在的目录。脚本分别调用 14 次 render_layout.py，生成5张1440×1920主图、1张1440×1440白底图、8张宽1440的详情屏，再调用拼接、预览、质检、打包脚本。几何图层是工程夹具，不代表商品，不包含性能参数。每个PNG独立生成，预览仅从单图缩小生成。

## 3. 真实商品运行

先按 SKILL.md 准备 product_facts.md、competitor_analysis.md、design_master.md，审核 main_01 方向后再制作全套。source/ 保留真实原图，working/ 存放可靠抠图及背景。将 examples/layout-example.json 复制到 working/，为每张画布单独配置图层。

示例配置的图片路径和字体路径都是占位符，必须替换。图层 path、font 的相对路径以**命令工作目录**为基准；跨 Agent 推荐绝对路径。Windows 中文可使用有授权的 `C:/Windows/Fonts/msyhbd.ttc`，其他系统提供可用 CJK 字体。字体存在不等于覆盖每一个字形，必须检查实际文字。

```powershell
& $py scripts/render_layout.py working/main_01.json outputs/demo/main_01.png
# 审核后，为 main_02...05、white_bg 和 detail_01...08 分别运行同一命令。
& $py scripts/compose_detail_long.py outputs/demo
& $py scripts/make_contact_sheet.py outputs/demo
& $py scripts/verify_and_package.py outputs/demo --product DEMO
```

`contain` 保持比例且保留完整主体；产品层使用此模式。`cover` 会裁边、`stretch` 会拉伸，它们仍保留供背景等非产品图层使用。脚本尚不识别图层的商品角色，不可把这两个选项用于真实产品主体。不要放大低清产品层冒充高清。

当前质检脚本以一个目录为单位：15个PNG、设计蓝图、事实表、竞品分析、QA报告应放在同一待交付目录。若采用 references 中的 final/ 子目录结构，请在 final/ 放入这4份文档的交付副本，再对 final/ 运行验证。脚本不会自动向父目录搜索，也不会要求这些文档必填；Agent 必须按交付契约检查。

可选预览参数：`--columns 3 --thumb-width 360`；预览允许只展示现有文件，不代表整套已完成。拼接仅接受8张宽1440的图片，使用 `--width` 可调整，但默认质检契约仍要求1440。长图保留透明通道；通常商品最终交付应为已合成的无透明成品。

## 4. 质检与ZIP

- exit 0：15张图片机器检查通过，ZIP已完成CRC、条目和图片SHA-256校验；不代表视觉或事实通过。
- exit 1：文件检查失败或ZIP校验失败；exit 2：参数/目录错误。其他I/O异常也会非零退出。
- manifest.json 记录尺寸、字节数、SHA-256和问题；脚本不会自动生成视觉审核结论。
- 已有同名ZIP会先保留为 `.zip.stale`（重名时追加编号）。失败重跑不会继续暴露旧的正式交付名。
- 新ZIP先写临时文件，校验通过才替换正式路径。旧备份不纳入新ZIP。
- qa_report.md 必须分别记录 MACHINE_QA、VISUAL_QA、FACT_QA；视觉/事实未审核只能写 PENDING。

手动复核压缩包：

```powershell
& $py -m zipfile -t outputs/demo/DEMO_taobao_listing_images.zip
```

Python脚本不包含模型API、自动抠图、Excel读取或千牛发布实现。背景生成和素材读取由调用 Agent 的工具完成；这些能力不是 requirements.txt 的隐含依赖。
