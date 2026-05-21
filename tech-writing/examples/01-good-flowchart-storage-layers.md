# 好范例：分层架构图（9 节点，subgraph + 标签边）

下图回答：「CC 一次请求经过哪几层？」

```mermaid
flowchart TD
    user["用户 prompt"]

    subgraph core["核心 (always-on)"]
        loop["Agent Loop"]
        model["Claude 模型"]
        tools["工具调度"]
    end

    subgraph storage["持久化"]
        session["session.jsonl"]
        memory["MEMORY.md"]
    end

    user -->|"输入"| loop
    loop -->|"推理请求"| model
    model -->|"tool_use"| tools
    tools -->|"tool_result"| loop
    loop -->|"append 事件"| session
    loop -->|"读 / 写"| memory
```

**为什么算好图**：

- 9 个节点，well below ≤12 上限
- `subgraph` 把"核心"和"持久化"分开，一眼看出层次
- 每条边都带动词（"输入" / "推理请求" / "tool_use" 等），不是裸箭头
- 方向 `TD` 自顶向下，符合数据流方向
- 节点标签用人话，ID 是 snake_case
- 没有混用 ASCII 或其他装饰
