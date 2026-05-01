# MultiAgent-CodeForge

<p align="center">
  <strong>多Agent协作的代码智能分析与优化系统</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/version-1.0.0-orange.svg" alt="Version">
</p>

---

## 项目简介

MultiAgent-CodeForge 是一个基于多Agent协作的代码智能分析与优化系统。通过多个专业化的AI Agent协同工作，实现对代码的全面分析、架构评估、优化建议和自动化测试生成。

### 核心特性

- **多Agent协作**: 5个专业Agent各司其职，通过消息传递协同工作
- **长链推理**: 基于Chain-of-Thought的深度分析能力
- **异步处理**: 全异步架构，支持高并发任务处理
- **结构化输出**: 基于Pydantic的数据验证和结构化输出
- **错误恢复**: 完善的错误处理和重试机制
- **可扩展性**: 模块化设计，易于扩展新的Agent和功能

---

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      OrchestratorAgent                       │
│                    (编排Agent - 协调中心)                      │
└─────────────┬─────────────┬─────────────┬─────────────┬─────┘
              │             │             │             │
              ▼             ▼             ▼             ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Code      │ │Architecture│ │Optimization │ │    Test     │
    │  Analyzer   │ │   Agent    │ │   Agent     │ │  Generator  │
    │    Agent    │ │            │ │             │ │    Agent    │
    └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
         │               │               │               │
         ▼               ▼               ▼               ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    MessageBus (消息总线)                   │
    │              发布-订阅模式 / 点对点通信                      │
    └─────────────────────────────────────────────────────────┘
```

### Agent协作流程

```
┌──────────────────────────────────────────────────────────────┐
│                    工作流执行流程                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 用户提交代码 ──► OrchestratorAgent                        │
│                          │                                   │
│  2. 任务分解           ▼                                     │
│     ┌─────────────────────────────────────┐                  │
│     │  CodeAnalyzerAgent (代码分析)        │                  │
│     │  - 解析代码结构                       │                  │
│     │  - 计算复杂度                         │                  │
│     │  - 识别技术债                         │                  │
│     └─────────────────────────────────────┘                  │
│                          │                                   │
│  3. 并行分析           ▼                                     │
│     ┌─────────────────────────────────────┐                  │
│     │  ArchitectureAgent (架构评估)        │                  │
│     │  - 识别架构模式                       │                  │
│     │  - 检查设计原则                       │                  │
│     │  - 评估依赖关系                       │                  │
│     └─────────────────────────────────────┘                  │
│                          │                                   │
│  4. 生成建议           ▼                                     │
│     ┌─────────────────────────────────────┐                  │
│     │  OptimizationAgent (优化建议)        │                  │
│     │  - 性能优化                           │                  │
│     │  - 代码质量优化                       │                  │
│     │  - 架构优化                           │                  │
│     └─────────────────────────────────────┘                  │
│                          │                                   │
│  5. 生成测试           ▼                                     │
│     ┌─────────────────────────────────────┐                  │
│     │  TestGeneratorAgent (测试生成)       │                  │
│     │  - 单元测试                           │                  │
│     │  - 边界测试                           │                  │
│     │  - 错误处理测试                       │                  │
│     └─────────────────────────────────────┘                  │
│                          │                                   │
│  6. 结果聚合           ▼                                     │
│     ┌─────────────────────────────────────┐                  │
│     │  聚合所有分析结果                     │                  │
│     │  生成综合报告                         │                  │
│     └─────────────────────────────────────┘                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 核心功能

### 1. CodeAnalyzerAgent - 代码分析Agent

负责解析代码结构、识别技术债务：

- **代码结构解析**: 函数、类、导入等结构提取
- **复杂度分析**: 圈复杂度、认知复杂度计算
- **技术债识别**: 长方法、大类、死代码等检测
- **代码度量**: 可维护性指数、代码密度等指标

### 2. ArchitectureAgent - 架构评估Agent

评估代码架构的合理性：

- **架构模式识别**: MVC、整洁架构、六边形架构等
- **依赖关系分析**: 模块间依赖、耦合度分析
- **设计原则检查**: SOLID原则、DRY原则等
- **架构健康度评估**: 综合评估架构质量

### 3. OptimizationAgent - 优化建议Agent

生成针对性的优化方案：

- **性能优化**: 算法优化、数据结构选择
- **代码质量优化**: 重构建议、代码异味修复
- **架构优化**: 解耦建议、模块化改进
- **安全优化**: 安全漏洞检测和修复建议

### 4. TestGeneratorAgent - 测试生成Agent

自动生成高质量的测试代码：

- **单元测试生成**: 基本功能测试
- **边界测试生成**: 边界条件测试
- **错误处理测试**: 异常情况测试
- **测试代码生成**: 可直接运行的测试代码

### 5. OrchestratorAgent - 编排Agent

协调其他Agent的工作：

- **任务分解**: 将复杂任务分解为子任务
- **工作流管理**: 定义和执行分析工作流
- **结果聚合**: 汇总各Agent的分析结果
- **错误处理**: 处理任务失败和重试

---

## 安装指南

### 环境要求

- Python 3.8+
- pip 或 poetry

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/cnqcyrj/MultiAgent.git
cd MultiAgent-CodeForge
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，根据需要修改配置
```

### 开发环境安装

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

---

## 使用指南

### 基本使用

```python
import asyncio
from src.agents.orchestrator import OrchestratorAgent

async def analyze_code():
    # 创建编排Agent
    orchestrator = OrchestratorAgent()
    
    # 启动Agent
    await orchestrator.on_start()
    
    try:
        # 执行分析
        workflow = await orchestrator.execute_workflow(
            source_code="your_python_code_here",
            file_path="your_file.py",
            workflow_type="full_analysis",
        )
        
        # 获取结果
        results = workflow.results
        print(results)
        
    finally:
        # 停止Agent
        await orchestrator.on_stop()

# 运行
asyncio.run(analyze_code())
```

### 工作流类型

系统支持以下工作流类型：

1. **full_analysis** - 完整分析
   - 代码分析 → 架构评估 → 优化建议 → 测试生成

2. **quick_analysis** - 快速分析
   - 代码分析 → 优化建议

3. **architecture_review** - 架构评审
   - 代码分析 → 架构评估

4. **test_generation** - 测试生成
   - 代码分析 → 测试生成

### 配置选项

```python
from src.core.agent import AgentConfig

config = AgentConfig(
    max_concurrent_tasks=10,  # 最大并发任务数
    timeout=300,              # 任务超时时间（秒）
    retry_attempts=3,         # 重试次数
    retry_delay=1.0,          # 重试延迟（秒）
    enable_logging=True,      # 是否启用日志
    log_level="INFO",         # 日志级别
)

orchestrator = OrchestratorAgent(config=config)
```

---

## 使用示例

### 示例1: 分析单个文件

```python
import asyncio
from src.agents.orchestrator import OrchestratorAgent

CODE = '''
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib
'''

async def main():
    orchestrator = OrchestratorAgent()
    await orchestrator.on_start()
    
    try:
        workflow = await orchestrator.execute_workflow(
            source_code=CODE,
            file_path="fibonacci.py",
            workflow_type="full_analysis",
        )
        
        # 输出结果
        summary = workflow.results.get("result_aggregation", {}).get("summary", {})
        print("分析结果:")
        print(f"  代码行数: {summary.get('metrics', {}).get('lines_of_code', 0)}")
        print(f"  函数数量: {summary.get('metrics', {}).get('function_count', 0)}")
        print(f"  关键发现: {summary.get('key_findings', [])}")
        
    finally:
        await orchestrator.on_stop()

asyncio.run(main())
```

### 示例2: 只生成测试

```python
import asyncio
from src.agents.orchestrator import OrchestratorAgent

CODE = '''
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
'''

async def main():
    orchestrator = OrchestratorAgent()
    await orchestrator.on_start()
    
    try:
        workflow = await orchestrator.execute_workflow(
            source_code=CODE,
            file_path="calculator.py",
            workflow_type="test_generation",
            options={
                "test_types": ["unit", "edge_case"],
                "test_framework": "pytest",
            },
        )
        
        # 获取生成的测试代码
        test_gen = workflow.results.get("test_generation", {})
        test_code = test_gen.get("generated_code", "")
        print("生成的测试代码:")
        print(test_code)
        
    finally:
        await orchestrator.on_stop()

asyncio.run(main())
```

### 示例3: 自定义Agent使用

```python
import asyncio
from src.agents.code_analyzer import CodeAnalyzerAgent
from src.core.task import Task

async def main():
    # 直接使用代码分析Agent
    agent = CodeAnalyzerAgent()
    await agent.start()
    
    try:
        # 创建任务
        task = Task(
            name="分析代码",
            input_data={
                "source_code": "def hello(): print('Hello, World!')",
                "file_path": "hello.py",
                "language": "python",
            },
        )
        
        # 执行任务
        result = await agent.execute_task(task)
        
        if result.success:
            print("分析成功!")
            print(f"函数数量: {len(result.data.get('functions', []))}")
        else:
            print(f"分析失败: {result.error}")
            
    finally:
        await agent.stop()

asyncio.run(main())
```

---

## 项目结构

```
MultiAgent-CodeForge/
├── src/                          # 源代码目录
│   ├── __init__.py              # 包初始化
│   ├── core/                    # 核心模块
│   │   ├── __init__.py
│   │   ├── agent.py            # Agent基类
│   │   ├── message.py          # 消息系统
│   │   ├── task.py             # 任务管理
│   │   └── exceptions.py       # 自定义异常
│   ├── agents/                  # Agent实现
│   │   ├── __init__.py
│   │   ├── code_analyzer.py    # 代码分析Agent
│   │   ├── architecture.py     # 架构评估Agent
│   │   ├── optimization.py     # 优化建议Agent
│   │   ├── test_generator.py   # 测试生成Agent
│   │   └── orchestrator.py     # 编排Agent
│   ├── utils/                   # 工具模块
│   │   ├── __init__.py
│   │   ├── logger.py           # 日志工具
│   │   ├── file_utils.py       # 文件工具
│   │   └── validators.py       # 验证器
│   └── models/                  # 数据模型
│       └── __init__.py
├── config/                      # 配置目录
│   ├── __init__.py
│   └── settings.py             # 配置管理
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── test_core.py            # 核心模块测试
│   ├── test_agents.py          # Agent测试
│   └── test_config.py          # 配置测试
├── examples/                    # 示例目录
│   └── basic_usage.py          # 基本使用示例
├── requirements.txt             # 依赖列表
├── setup.py                    # 安装配置
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略文件
└── README.md                   # 项目说明
```

---

## 技术栈

- **Python 3.8+**: 主要编程语言
- **Pydantic**: 数据验证和设置管理
- **asyncio**: 异步编程支持
- **python-dotenv**: 环境变量管理
- **pytest**: 测试框架
- **logging**: 日志系统

---

## 设计模式

项目应用了以下设计模式：

1. **Agent模式**: 每个Agent封装特定的专业能力
2. **发布-订阅模式**: 消息总线实现松耦合通信
3. **编排模式**: OrchestratorAgent协调多个Agent
4. **策略模式**: 不同的工作流类型对应不同的执行策略
5. **模板方法模式**: BaseAgent定义Agent的基本行为框架
6. **工厂模式**: 任务和消息的创建
7. **观察者模式**: 任务状态变更通知

---

## 性能指标

| 指标 | 说明 |
|------|------|
| 并发任务数 | 支持10+并发任务 |
| 分析速度 | 千行代码 < 5秒 |
| 内存占用 | < 100MB |
| 测试覆盖率 | 目标 > 80% |

---

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 代码规范

- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 使用 MyPy 进行类型检查
- 编写清晰的文档字符串
- 保持测试覆盖率

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 联系方式

- 项目主页: https://github.com/cnqcyrj/MultiAgent.git
- 问题反馈: https://github.com/cnqcyrj/MultiAgent.git/issues
- 邮箱: cn.qcyrj@gmail.com

---

## 致谢

感谢所有为这个项目做出贡献的开发者！

---

<p align="center">
  <strong>MultiAgent-CodeForge</strong> - 让代码分析更智能、更高效
</p>
