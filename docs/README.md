# Block 框架概览
## 框架定位
Block 是一个面向分布式节点网络的集成框架，目标是让其他业务项目可以快速接入 Block 协议栈，实现节点之间的安全注册、指令传输与转发。框架提供了一套统一的指令模型、节点管理、路由分发、消息转发、桥接 API 等能力，适合构建需要跨节点通信的上层业务。
## 核心能力一览
- **指令模型 (`models/ins`)**：定义 `open` 与 `cert` 两类协议的指令结构、序列化/反序列化逻辑，以及工厂类 `InsOpenFactory`、`INS_CERT_FACTORY`。
- **节点管理 (`models/node`)**：`NodeModel` 表示一个节点的连接上下文，`NODE_MANAGER` 负责节点注册、激活、断连及本机节点的单例缓存。
- **连接信息 (`models/connect`)**：`ConnectModel` 描述与远端节点的连接方式，`CONNECT_MANAGER` 负责加载 `data/connect/*.yml` 中的记录并维护主动连接协程。
- **路由体系 (`models/routers`)**：`RouteBlock`、`ROUTE_BLOCK_MANAGE` 负责将指令路由到具体业务处理函数，并统一包装响应指令。
- **发送管道 (`utils/send.py`)**：`execute_send_ins` 根据目标节点选择本地调用或网络发送，支持等待响应、超时控制与转发逻辑。
- **桥接 API (`routers/bridge.py`)**：提供 HTTP/JSON → Block 指令的入口，适合第三方系统通过 HTTP 接入。
- **策略系统 (`strategy/`)**：`ConnectStrategy` 负责启动与已知节点的持续连接；`DiscoverStrategy` 在局域网扫描并自动发现新节点。
## 全局结构
- `adapters/`：封装对外适配器逻辑，例如向节点发送本机信息等。
- `models/`：领域模型与工厂模式实现，涵盖节点、连接、指令、路由、签名等核心对象。
- `routers/`：FastAPI/WS 路由。`bridge.py` 提供 HTTP 指令桥接；`node.py`、`res.py`、`ws.py` 则处理节点注册、响应下发与 websocket 服务。
- `strategy/`：框架启动时的后台策略任务，结合 FastAPI lifespan 持续运行。
- `utils/`：通用工具（密码学、序列化、网络发现、消息派发、Future 管理等）。
- `gui/`：界面相关组件（目前较少使用）。
## 指令协议速览
### Open 协议
- 明文传输路由与数据，使用 Base64 编码 JSON 负载。
- 典型字段：`bid`、`sender`、`receiver`、`routing`、`data`、`status_code`、`res`。
- 工厂：`InsOpenFactory` 负责生成与解析。

### Cert 协议
- 用于携带敏感数据，负载会按目标节点的对称密钥加密。
- 创建时会自动使用 `node_encryption_base64` 以接收者密钥加密路由、数据、状态码等字段。
- 工厂：`INS_CERT_FACTORY`。

### 响应约定
- 返回 `/res/data`（或 `/res/file`）路由的指令作为响应，通过 `RES_FUTURES` 将结果回传给等待方。
- 状态码定义见 `文档.md` 中的“状态码”章节。
## 节点注册与通信流程
1. **握手开始**：客户端节点发送 `open` 指令到 `/node/register/start`，附带随机挑战与签名。
2. **验证签名**：服务端节点通过 `SignatureModel` 校验身份，生成对称密钥并回传挑战。
3. **挑战确认**：客户端解密密文并回送 `ok`，服务端调用 `NODE_MANAGER.active` 激活节点。
4. **持久化信息**：成功后保存证书与连接信息到 `data/signature/`、`data/connect/`。
5. **持续通信**：双方 websocket 连接建立，指令通过 `node_message` 解析后进入 `ROUTE_BLOCK_MANAGE`。
6. **转发策略**：若目标节点未直接连接，`node_send` 会选择具备桥接能力的节点中继发送。
## HTTP 桥接入口
`/bridge/ins` 允许第三方系统通过 HTTP POST 推送加密后的指令：
1. `text` 字段需使用环境变量 `IDENTITY`（Base64 编码的对称密钥）进行 AES-CBC 加密。
2. 桥接服务解密后构造 `InsOpen` 或 `InsCert` 指令并交由 `execute_send_ins` 执行。
3. 可选 `wait`、`timeout` 控制是否同步等待响应。

示例结构：
```json
{
  "protocol": "open",
  "routing": "/node/signature",
  "data": {"foo": "bar"},
  "receiver": "*",
  "wait": true,
  "timeout": 60
}
```
## 策略任务
- **ConnectStrategy**：循环调用 `CONNECT_MANAGER.connect()`，尝试与记录在案的节点建立/恢复连接。
- **DiscoverStrategy**：扫描 `192.168.*.*` 网段，探测存在 Block 节点的主机，自动保存连接信息并触发注册。
- **StrategyManager**：在 FastAPI lifespan 中以后台任务启动多条策略协程，应用关闭时统一取消。
## 配置与依赖
- Python 版本要求在 `setup.py` 中写为 `>=3.13`，实际运行建议锁定到当前兼容版本（如 3.10/3.11）；根据部署环境自行调整。
- 关键依赖：`fastapi`、`starlette`、`websockets`、`cryptography`、`pyyaml`、`requests`、`netifaces` 等。
- 配置文件与环境变量：
  - `config/node.yml`：本节点基础信息（BID、角色、桥接标记等）。
  - `TOP_VERIFY_PUBLIC_PEY_PATH`：顶级验证公钥路径。
  - `NODE_PRIVATE_PEY_PATH`：节点私钥路径。
  - `SIGNATURE_PATH`：本节点签名文件。
  - `IDENTITY`：HTTP 桥接使用的对称密钥（Base64）。
- 数据目录：
  - `data/signature/`：已保存的远端节点证书。
  - `data/connect/`：与远端节点的连接信息（含对称密钥 hex）。
## 集成指引
1. **准备环境**：安装依赖、配置密钥文件与 `config/node.yml`。
2. **导入框架**：在业务服务中 `import Block`，按需挂载 `routers` 中的 FastAPI 路由或启动 websocket 服务。
3. **注册路由**：新业务可以使用 `RouteBlock` 装饰器注册自定义路由函数，并通过 `ROUTE_BLOCK_MANAGE.add()` 纳入调度。
4. **启动策略**：将 `StrategyManager.lifespan(app)` 交给 FastAPI 应用，确保发现/连接任务常驻。
5. **测试通信**：利用 `/bridge/ins` 或现有节点发起 `open/cert` 指令，确认响应流程是否正常。
## 后续文档
- `文档.md`：概念说明、状态码、指令安全规范。
- `运维.md`：容器化部署示例（IPFS、Block 镜像）。

随着项目演进，可以继续在 README 中补充配置范例、部署脚本、常见问题等内容，以方便其他项目快速集成 Block 框架。
