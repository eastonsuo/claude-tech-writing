# claude-tech-writing

> 一个 [Claude Code](https://code.claude.com) skill：写技术文章时把 mermaid 图当一等公民对待，再用一个 lint 把每张图按死规则审一遍。

**中文** | [English](README.en.md)

---

## 背景：为什么要做这个

写技术文章 / design doc / 复盘的时候，我长期被两件事卡住：

### 1. 图被严重低估

很多本该是图的关系、流程、时序，因为画图有摩擦——选图类型、调布局、写语法——就退化成了几段密集文字。读者读这种文字时要在脑子里把它再"渲染"成图，慢、累、易偏差。

让 Claude Code 帮忙写技术文档时，这毛病一样有。CC 默认行为更接近"模仿样本"——你没立规矩，它就照默认套路出，倾向用文字而不是图。

### 2. 画了图也不一定好

经常踩的坑：

- 一张图塞 30+ 节点的"系统全景"，最后谁也看不懂
- 节点叫 `A` / `B` / `S1`，读者不知道每个圆圈代表什么
- 边全是裸箭头，看不出每条边的语义（同步？异步？读？写？）
- 图前没有"这张图想让你看到什么"的钩子，图后没有任何解读
- 颜色乱用，dark mode 或灰度打印下完全失明
- 5+ 字段对照硬画成 `classDiagram`，节点撑爆

两个问题加起来：要么没图，要么图也救不了。

## 这个 skill 要解决什么

目标是把"用图把事情讲清楚"做成 CC 写技术内容时的**默认动作**，而不是事后才想到补：

- **触发时机**是"写文章"，不是"画图"——你说「写一篇关于 X 的文章 / 解释 X 怎么工作」它就介入，不需要主动喊"画个图"
- **每张图按硬指标审**：复杂度上限按图类型分级、节点标签必须人话化、边必须带标签、subgraph 必须有名字、5+ 字段对照一律改用表格、颜色不能是唯一区分维度……
- **lint 跑得起来**：写完一稿 `python3 lint_article.py article.md` 看到一串 ❌ 就改，不靠主观判断

观点是有立场的，默认数值是我个人取舍。**Fork 改阈值随便。**

## 它能做的

接到"写技术文章 / 解释 X 的设计 / 写个 design doc / 复盘"这类请求时，这个 skill 会让 Claude Code：

1. **在每一个非平凡的关系 / 流程 / 时序点**先问"这里能不能补一张图"，而不是默认用文字
2. **守住每种图类型的复杂度上限**：
   - `flowchart` / `classDiagram` 节点 ≤ 12
   - `sequenceDiagram` participants ≤ 8、messages ≤ 15
   - `stateDiagram-v2` states ≤ 10、transitions ≤ 15
   - `erDiagram` entities ≤ 8
   - `mindmap` 二级节点 ≤ 6、每个二级下的叶子 ≤ 6
3. **节点标签必须人话化**（不允许 `A` `B` `S1` 这种裸 ID）
4. **每张图配两段散文**：前面 1-2 句钩子说"想让你看到什么"、后面 3-5 句"读图要点"
5. **写完跑 lint** 把上面所有规则机器化查一遍

## 它不做的

- 不替你想清楚"要写什么"——它只在你已经决定写时介入
- 不渲染 mermaid 验语法合法性——lint 只做静态规则匹配；要真渲染请自己装 `mermaid-cli` 跑 `mmdc`
- 不支持 mermaid 以外的图（PlantUML / D2 / Graphviz 暂不在范围，PR 欢迎）
- 不是行业标准——是一个人的写作品味写成的规则

## 安装

skill 在 **Claude Code** 和 **Claude.ai 聊天 / Claude Desktop**（Pro / Max / Team / Enterprise）上都能装，格式完全一样（都是 [Agent Skills 开放标准](https://support.claude.com/en/articles/12512180-use-skills-in-claude)）。

### Claude Code（CLI / IDE 插件 / claude.ai/code）

```bash
git clone https://github.com/eastonsuo/claude-tech-writing
cd claude-tech-writing
./install.sh
```

`install.sh` 把 `tech-writing/` 软链到 `~/.claude/skills/tech-writing/`。重启 Claude Code 即可。

卸载：`rm ~/.claude/skills/tech-writing`。

### Claude.ai 聊天 / Claude Desktop（需 Pro 及以上、开启 Code Execution）

两种方式选一：

**方式 A：下载预打好的 ZIP** → [Releases](https://github.com/eastonsuo/claude-tech-writing/releases/latest) 下载 `tech-writing.zip`

**方式 B：本地构建**
```bash
git clone https://github.com/eastonsuo/claude-tech-writing
cd claude-tech-writing
./build-zip.sh   # 生成 tech-writing.zip
```

然后在 Claude.ai 网页（或 Claude Desktop 聊天 app）：

1. 对话输入框旁的 **+** 按钮 → **Skills** → **Add skill**
2. 选 `tech-writing.zip` 上传
3. 上传成功后所有新对话自动触发，trigger 词同 CC

卸载：+ 按钮 → Skills → Manage skills → 删除。

## 使用

skill 在你给 Claude Code 发这类 prompt 时自动触发：

- 「写一篇关于 X 的文章」
- 「解释一下 X 的原理 / 设计」
- 「帮我写个 design doc / 调研报告 / 复盘」
- 英文同样支持："write an article about…", "explain how … works", "document the design of …"

也可以显式调用：`/tech-writing` + 你的请求。

写完后 Claude 会自动跑 lint，输出类似这样：

```
图 1 (行 5-26, 类型: flowchart, nodes: 9)
  ✅ 通过所有检查

图 2 (行 30-50, 类型: sequenceDiagram, participants: 12, messages: 18)
  ❌ participants 12 > 8（考虑拆图）
  ❌ messages 18 > 15（考虑拆图）

=== 共 2 张图，2 个问题 ===
```

## 检查的规则

完整规则见 [`tech-writing/SKILL.md`](tech-writing/SKILL.md)（[英文版](tech-writing/SKILL.en.md)）。核心检查项：

| 规则 | 为什么 |
|---|---|
| 各图类型分级复杂度上限 | 30 节点的 flowchart 是把两件事塞进一个壳子里 |
| 节点标签人话化（不允许 `A` / `B`） | "IM 截图测试"——把图截屏给没读过文章的人看，能不能猜出 ≥ 70% 语义 |
| 边必须带动词 / 条件标签 | 裸箭头几乎传递不了信息 |
| subgraph 必须有显示名字 | `subgraph storage["持久化层"]`，而不是 `s1` |
| 代码定位写在散文里，不嵌节点标签 | 行号会随代码漂移；节点应该稳定 |
| 颜色按固定语义集复用 | 否则读者每张图都要重新学色彩含义 |
| 颜色不能是唯一区分维度 | dark mode + 灰度打印 + 色觉障碍三场景都要扛过 |
| 每张图前后都要有散文 | "如图所示"然后断片 = 这张图等于没看 |
| 5+ 字段对照一律用表格 | 表格才是这类信息的天然载体 |

## 范例

`tech-writing/examples/` 下有 5 个对照范例，写之前 Claude 会先翻一两个最相关的：

- `01-good-flowchart-storage-layers.md` — 分层架构图（subgraph + 标签边 + 人话节点）
- `02-bad-flowchart-too-many-nodes.md` — 节点过多 + 裸 ID 反例 + 拆图建议
- `03-good-sequence-api-call.md` — 干净的请求-响应时序图
- `04-bad-no-prose-around.md` — 图前后没散文的典型反例
- `05-good-state-machine.md` — 订单状态机

## 独立跑 lint

不开 Claude Code 也能用——直接对任何 markdown 文件跑：

```bash
python3 tech-writing/scripts/lint_article.py path/to/article.md
```

退出码 0 = 干净，1 = 至少有一个 ❌。可以挂到 pre-commit hook 或 CI 上。

零依赖，stdlib only。

## FAQ

**为什么是这些具体数字？** 是我个人写作 / 阅读品味的取舍。觉得不合理就 fork 改 [`tech-writing/scripts/lint_article.py`](tech-writing/scripts/lint_article.py) 里的 `LIMITS` dict。

**为什么只支持 mermaid？** 因为 mermaid 在 GitHub / GitLab / 大部分 IDE 和静态站点生成器里都能直接渲染，零额外依赖。加 PlantUML / D2 / Graphviz 意味着用户要额外装东西、lint 要加更多图类型检测、examples 要再做一套。PR 欢迎。

**lint 会真的渲染图来验语法吗？** 不会——它用正则解析 mermaid，能抓结构性问题（节点超、缺标签、裸 ID、嵌行号），但不保证语法 100% 合法。要全套验证请装 [`mermaid-cli`](https://github.com/mermaid-js/mermaid-cli) 手动跑 `mmdc`。

**能配置关掉某条规则吗？** 暂时没做配置层。要关请 fork 改脚本。`.tech-writing.toml` 这类配置欢迎 PR。

**每次 CC 会话都加载吗？** 不——CC 只在你 prompt 匹配 skill 的 `description` 时才召唤它。不写技术文章的对话不受影响。

**需要哪个 CC 版本？** 带 bundled scripts 的 skill 在 CC v2.1.x 及以后稳定可用，实测 v2.1.145。

## License

MIT。见 [LICENSE](LICENSE)。

## Author

[@eastonsuo](https://github.com/eastonsuo) · 反馈 / issue / PR 都欢迎。
