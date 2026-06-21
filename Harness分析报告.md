# hello-agents 工程结构分析报告

## 一、项目结构

hello-agents 是 Datawhale 开源的 Agent 入门教程，按模块化组织：

1.docs 16章教程，按 chapter1–16 编号，从 Agent 基础到毕业项目 
2.code目录 每章配套的代码
3.Extra-Chapter 社区贡献的补充内容：面试题、Dify 教程、GUI Agent 等 
4.Co-creation-projects 学员提交的完整毕业项目，供参考学习 

## 二、设计优点

1. 节奏清晰。每章理论和代码一一对应，初学者不会出现看完不知道怎么动手的情况。

2. 节奏递进合理。从 LLM 基础 → 工具调用 → RAG → Agent 架构 → 多 Agent → 项目实战，逐步铺垫，

3. 为社区贡献提供平台。Extra-Chapter 和 Co-creation-projects 让学过的人有地方贡献内容，降低了教程维护压力。

4. 提供代码答案。hello-agents 的 code目录提供代码，遇到问题可以对比自己的实现和标准答案。

## 三、可以改进的地方

1. 缺少统一测试。code目录下各章代码独立，没有跨章测试或集成测试。

2. 缺少难度标注。 16 章内容难度不一，如果每章标上难度标签，读者可以按自己的节奏选择性学习。



