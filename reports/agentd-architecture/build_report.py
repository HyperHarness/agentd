"""Content and diagrams for the 36-slide Chinese project report.

Run: python3 reports/agentd-architecture/build_report.py
All claims refer to the workspace snapshot dated 2026-10-28.
"""
from render_engine import Slide, export_all, measure


BASE='docs/PRODUCT_REQUIREMENTS_BASELINE.md'
ARCH='docs/SOFTWARE_ARCHITECTURE_PROPOSAL.md'
TASK='docs/design/TASK_AND_REVIEW_PROTOCOL.md'
RUN='docs/design/RUNTIME_LIFECYCLE.md'
REL='docs/design/RELIABILITY_AND_STORAGE.md'
API='docs/design/INTERFACE_GUIDE.md'
VAL='docs/design/VALIDATION_PLAN.md'
DEC='docs/design/DECISIONS_AND_EVIDENCE.md'
SPEC='specs/agentd_v1/README.md'
MODELS='specs/agentd_v1/models.py'
OPS='specs/agentd_v1/operations.py'


def src(path,line,short):
    return dict(path=path,line=line,short=short)


slides=[]


def new(title,section,subtitle='',status='D · 候选设计',dark=False,sources=(),notes=''):
    s=Slide(title,section,subtitle,status,dark,sources,notes)
    slides.append(s)
    return s


def box(s,x,y,w,h,title,body='',accent='teal',fill=None,size=27):
    s.rect(x,y,w,h,fill or s.cardfill,radius=14)
    s.text(x+22,y+18,title,size,accent,True,width=w-44)
    if body:s.text(x+22,y+66,body,24,s.muted,width=w-44,line_height=1.4)


def number(s,x,y,n,label,body,w=430,h=225,accent='teal'):
    s.rect(x,y,w,h,s.cardfill,radius=18)
    s.text(x+24,y+15,n,65,accent,True)
    s.text(x+24,y+99,label,31,bold=True,width=w-48)
    s.text(x+24,y+153,body,25,s.muted,width=w-48,line_height=1.38)


def table(s,x,y,widths,headers,rows,heights=None,fs=24,header_fs=23):
    total=sum(widths);hh=53
    s.rect(x,y,total,hh,'darkcard' if s.dark else 'ink',radius=9)
    xx=x
    for w,h in zip(widths,headers):
        s.text(xx+16,y+10,h,header_fs,'white',True,width=w-30);xx+=w
    yy=y+hh
    for i,row in enumerate(rows):
        h=heights[i] if heights else 72
        s.rect(x,yy,total,h,('darkcard' if s.dark else ('white' if i%2==0 else '#EAEDE5')))
        xx=x
        for j,(w,cell) in enumerate(zip(widths,row)):
            s.text(xx+16,yy+13,cell,fs,'teal' if j==0 and not s.dark else s.ink,j==0,width=w-30,line_height=1.27)
            xx+=w
        yy+=h
    return yy


# 01 — Cover / summary entry
s=new('让模型并行，让结果可信','需求与架构报告',status='设计快照 · 2026-10-28',dark=True,
 sources=[src(BASE,19,'需求 §1–2'),src(ARCH,1,'架构总览'),src(SPEC,1,'契约状态')],
 notes='这份报告回答三个问题：agentd 要满足什么需求，系统如何组织，以及为什么选择这样的架构。当前项目是从零重写的需求与候选设计资料包，包含可执行接口契约，但没有新业务服务的实现。\n\n建议用法：时间有限时看第 1–6 页，约 3–5 分钟；需要评审时继续第 7–30 页；需求追踪、参数候选、历史教训和文件索引在第 31–36 页。PowerPoint 每页包含讲解备注，离线网页版按 N 可展开同一讲解。\n\n报告中的产品要求、待评审机制、待验证假设和待选择参数保持原文状态；界面图、任务故事和统计数据算例明确标为示意。')
s.chip(80,132,'可信用户 · 本机 · 多模型开发协作','darkcard','lightmuted',21)
s.text(80,231,'让模型并行，',78,'white',True)
s.text(80,336,'让结果可信。',78,'yellow',True)
s.text(84,470,'agentd 从零重写：需求、架构与设计取舍',31,'lightmuted')
s.text(84,540,'把任务交出去，把判决和进度留得住。',31,'white')
for x,y,label,sub in [(1050,224,'主线','定义目标'),(1265,364,'worker','并行执行'),(1050,504,'独审','判断成果')]:
    s.rect(x,y,220,115,'darkcard',radius=18)
    s.text(x+25,y+18,label,34,'white',True)
    s.text(x+25,y+68,sub,23,'lightmuted')
s.line(1160,340,1340,360,'yellow',3,arrow=True)
s.line(1340,480,1160,500,'yellow',3,arrow=True)
s.line(1030,558,980,558,'lightmuted',2)
s.line(980,558,980,280,'lightmuted',2)
s.line(980,280,1038,280,'lightmuted',2,arrow=True)
s.rect(80,683,1440,112,'darkcard',radius=16)
s.text(106,706,'01–06  快速概览',26,'yellow',True)
s.text(586,706,'07–30  需求与架构',26,'white',True)
s.text(1106,706,'31–36  证据附录',26,'white',True)
s.text(106,751,'先抓住结论，再按问题深入。当前：候选设计与契约；新服务尚未实施。',22,'lightmuted')

# 02 — Executive takeaway
s=new('60 秒：这个项目要交付什么','快速概览','一套可信本机上的任务协作系统，让模型团队持续交付可独审的成果。',status='R · 产品目标 / F · 当前状态',
 sources=[src(BASE,19,'需求 §1–2'),src(SPEC,57,'契约证明边界')],
 notes='目标有三个：提高并行吞吐，让合适的任务使用能力或成本较低的模型，并逐步积累按难度分配模型的依据。主线 Codex 负责拆任务、写验收、预先评难度；agentd 从用户配置的固定 worker 池选择执行者；Claude Code 保留原生工具循环；独立 Codex reviewer 给出有效判决。\n\n业务终点很明确：PASS 就成功，累计三个有效 REJECT 就审核失败。主线是否采用或合并成果在这一闭环之外。系统同时保存可恢复进度和不可变成果，避免把客户端关闭或进程中断当作成果消失。\n\n三个目标目前仍是目标。已有文档和契约检查可以证明设计资料具有可核对结构，不能证明实际提速、省钱或学习策略优于随机。')
number(s,80,245,'01','并行吞吐','让多个独立任务同时推进，减少串行等待。',w=464,accent='teal')
number(s,568,245,'02','合理用模','主线给难度，agentd 在固定池中选择执行模型。',w=464,accent='orange')
number(s,1056,245,'03','持续学习','按模型 × 难度积累结果，逐步形成分配偏好。',w=464,accent='blue')
s.rect(80,505,1440,184,'ink',radius=18)
s.text(112,529,'主线定义任务  →  原生 worker 执行  →  独立 reviewer 判决',35,'white',True)
s.text(112,600,'agentd 贯穿全程：保存、调度、监督、重试边界、通知、统计。',28,'lightmuted')
s.banner('当前可确认：需求与候选契约已整理；产品收益仍需真实任务实验。',y=730)

# 03 — Problem / stakes
s=new('并行开工容易，可靠交付需要规则','快速概览','情境示意：三个任务同时开始，主线一段时间后再回来查看。',status='R · 需求动机 / 情境示意',
 sources=[src(BASE,85,'需求 F01–F17'),src(DEC,22,'历史教训 §1.2')],
 notes='用一个忙碌开发者的视角理解需求：主线把几项工作交给模型后，会继续做别的事情。回来时，最需要的不是一屏输出，而是知道谁完成了、依据是什么、哪个任务需要介入，以及已有进度是否还能继续。此页三个任务只用于说明，未声称发生过对应实验。\n\n如果把执行退出、任务通过和通知到达混在一起，系统会出现三个误判：进程退出零被当作合格成果；内存不足消耗模型审核机会；审核客户端离线被算成失败。共享文件或端口还可能让本来独立的任务互相干扰。\n\nagentd 的价值是把这些事实分开记录，在确定的业务合同和运行边界内推进，给主线一个可追溯的结果和可行动的等待原因。')
table(s,80,238,[235,425,780],['并行任务','回来时看到的现象','系统需要给出的确定答案'],[
 ('任务 A','worker 已退出','候选是否完整？独立审核是否通过？'),
 ('任务 B','资源超限，运行中断','进度保存在哪里？旧进程停了吗？如何继续？'),
 ('任务 C','成果已交，reviewer 离线','原候选是否仍在队列？谁来领取？是否误计拒绝？'),
],heights=[102,102,102],fs=27)
s.card(80,625,700,161,'可见的价值','主线接回任务时，能直接作出下一步决定。',accent='teal',body_size=26)
s.card(804,625,716,161,'隐含的工程责任','每次重启、重发和清理，都保持同一份业务事实。',accent='orange',body_size=26)

# 04 — Invariants
s=new('六条规则，定义产品的性格','快速概览','后续架构都要服务于这些已确认边界。',status='R · 已确认要求',
 sources=[src(BASE,27,'需求 §2'),src(BASE,65,'任务终点 §4'),src(BASE,260,'不可降低的边界')],
 notes='第一，主线给任务和难度，模型由 agentd 自动选择。第二，独立评审 PASS 立即成功，主线之后不用成果也不改这个事实。第三，最多三个被独立评审拒绝的有效候选；第三次拒绝就结束，没有第四次自动尝试。\n\n第四，网络、工具、资源和审核环境故障都不是有效 REJECT；有限自动恢复耗尽后保留任务并等待显式处置。第五，worker 保留原生 Claude Code 的工具、MCP、subagent、网络和会话能力，前提是原模型、账号和主机本来支持。第六，任务终态不可覆写，后续改变目标或发现缺陷时建立关联新任务。\n\n任务合同两阶段冻结、五个状态名称和具体租约算法是为这些边界服务的候选设计，见后面的 D 页面。')
cards=[('主线给难度','模型选择由 agentd 完成。','teal'),('PASS 即成功','无需追加采纳或合并关卡。','teal'),('三次有效拒绝结束','三拒绝后由主线重新规划。','orange'),('故障保留接续能力','故障次数与审核拒绝分开记录。','blue'),('保留原生能力','MCP、subagent、shell 与会话继续可用。','teal'),('终态留作历史事实','修改目标或发现缺陷，建立关联新任务。','orange')]
for i,(title,body,accent) in enumerate(cards):
    s.card(80+(i%3)*488,238+(i//3)*281,464,253,title,body,accent=accent,body_size=28,title_size=30)

# 05 — Architecture overview
s=new('一张图：谁思考，谁执行，谁保证过程','快速概览','所有入口共享同一业务 daemon、同一权威状态；U 独立承担生命周期操作。',status='R · 角色边界 / D · 结构方案',dark=True,
 sources=[src(ARCH,37,'系统组成与模块'),src(RUN,5,'统一运行拓扑')],
 notes='从上到下读：Dashboard 给用户配置和管理；主线和独立 reviewer 使用同一 bridge 的两个固定角色连接，经 HTTP 访问同一个后端。后端认证身份并执行业务用例，任务、调度、审核、通知和统计都在一个 daemon 中。\n\ndaemon 与宿主监督器协作派发受控 worker。每次执行有独立工作区、会话和本地后代资源组。SQLite 保存合同、状态、判决和索引；Git 与文件保存代码、报告和证据正文。\n\nU 是按需运行的生命周期执行器，位于服务 S 的停止边界之外，负责安装、升级和卸载；日常启停由服务管理器处理。主线和 reviewer 是外部客户端，不由 agentd 托管其账号或推理循环，也不在 worker 的资源预算内。图是职责视图，连线不代表一律是父子进程关系。')
for x,title,body in [(80,'Dashboard','用户配置与管理'),(565,'主线 Codex','任务 / 验收 / 难度'),(1050,'独立 reviewer','领取 / 验证 / 判决')]:
    box(s,x,237,470,100,title,accent='yellow',size=28)
    s.text(x+22,290,body,23,'lightmuted')
    s.line(x+235,339,x+235,382,'lightmuted',2,arrow=True)
s.rect(80,385,1440,116,'darkcard',stroke='#4C7D71',radius=16)
s.text(110,405,'统一 HTTP 接入 · 内部认证与授权',28,'white',True)
s.text(110,453,'业务 daemon：任务  /  调度与执行  /  候选与审核  /  通知与查询  /  配置',26,'lightmuted')
for x,w in [(315,470),(800,470)]:s.line(x,503,x,550,'lightmuted',2,arrow=True)
box(s,80,553,470,138,'原生 Claude Code workers','宿主监督器 + 私有工作区\n本地后代共享该次执行预算',accent='yellow',size=27)
box(s,575,553,470,138,'SQLite + Git / 文件','事务事实与成果正文分开保存\n共同组成可恢复的数据资产',accent='yellow',size=27)
box(s,1070,553,450,138,'生命周期执行器 U','S 停止后继续安装 / 升级 / 卸载\n独立操作记录与资源预算',accent='yellow',size=27)
s.line(1295,503,1295,550,'yellow',2,dash=True,arrow=True)
s.text(82,744,'主线负责业务选择   ·   worker 负责产出   ·   reviewer 负责判决   ·   agentd 负责可靠推进',27,'white',True,width=1440)

# 06 — current and delivery scope
s=new('交付路线：先跑通真实闭环，再补齐正式能力','快速概览','V0 / V1 是候选交付范围；阶段限制须接受后定案，没有工期承诺。',status='F · 资料事实 / D · 分期',
 sources=[src(BASE,243,'V0 / V1 范围'),src(VAL,25,'工作包 A–E'),src(SPEC,22,'离线契约检查')],
 notes='当前仓库已有产品基线、架构总览、六个专题和契约源码。本次复核：29 个操作、153 个注册模型、8 个正例、19 个反例及 3 组拆分回归通过，生成物一致；新服务、模型和主机验收未运行。\n\nV0 建议限制为单用户、单主机、单项目和独立任务。要求三个真实 worker 重叠执行、至少两种模型、完整独审终态、保留进度与显式继续。模型仅随机分配，reviewer 主动领取，自动恢复可以为 0；安装由最小 U 完成，升级和卸载尚未交付。\n\nV1 再加入固定依赖 DAG、已验证的客户端提示、有限自动恢复、成熟样本下的能力偏好，以及受支持升级和保留数据卸载。不能把这些候选限制当作已经获得批准，也不能因有契约源码就认定 V0 合同已冻结。推进顺序是探针、合同、真实任务、故障与并行，再到 V1。')
s.card(80,238,440,400,'现在：可审阅的设计','需求与专题协议\n29 个操作的候选契约\n153 个注册模型\n离线检查通过',tag='真实运行验收：NOT RUN',accent='blue',body_size=28)
s.card(555,238,465,400,'V0：内部可用闭环','单项目、独立任务\n3 worker / 至少 2 模型\n随机择模、主动领取\n显式恢复、最小 U 安装',tag='分期限制待接受',accent='teal',body_size=28)
s.card(1055,238,465,400,'V1：正式支持能力','固定依赖 DAG\n通知与有限自动恢复\n有证据的能力偏好\nU 升级与保留数据卸载',tag='支持环境逐项验收',accent='orange',body_size=28)
s.text(80,677,'探针',29,'teal',True)
s.line(172,699,256,699,'teal',2,arrow=True)
s.text(280,677,'合同冻结',29,'teal',True)
s.line(422,699,516,699,'teal',2,arrow=True)
s.text(540,677,'真实任务',29,'teal',True)
s.line(685,699,779,699,'teal',2,arrow=True)
s.text(803,677,'故障与并行',29,'teal',True)
s.line(977,699,1071,699,'teal',2,arrow=True)
s.text(1095,677,'V1 扩展',29,'teal',True)
s.banner('首个交付里程碑：在实际安装产物中，跑通一条可取回成果的真实任务。',y=746)

# 07 — Narrative path
s=new('跟随一条任务：从“请修复”到可读取成果','业务闭环','示例任务：为导出接口补充参数校验与测试；难度由主线事先给定。',status='R · 角色 / D · 流程 / 示例',
 sources=[src(BASE,49,'角色责任'),src(TASK,21,'角色泳道'),src(API,57,'典型调用')],
 notes='这是一个贯穿报告的虚构任务，用于理解流程，没有假设当前系统已经执行。用户提出导出接口需要更稳健，主线把目标、范围、验收和难度写成任务，通过 submit_task 交给 agentd。\n\nagentd 排队并在首次派发时固定输入、模型和配置。worker 在原生 Claude Code 中修改、自检，再通过约定交付通道提交候选；服务核验执行闭合和材料完整后开放审核。外部 reviewer 领取精确候选，在自己的副本中检查，提交绑定该候选的证据与判决。\n\nPASS 立即结束并通知主线读取成果。如果第一或第二次拒绝，worker 沿用原合同、模型和已有成果返修；第三次拒绝结束，主线重新拆包或调整难度后创建关联新任务。实际采用、合并或发布由主线另行完成。')
lanes=[('主线',80,260,'teal'),('agentd',440,260,'blue'),('worker',800,260,'orange'),('独立 reviewer',1160,260,'teal')]
for label,x,y,c in lanes:
    s.chip(x,y,label,'mint' if c=='teal' else ('ice' if c=='blue' else 'sand'),c,23)
    s.line(x+160,y+59,x+160,713,'line',2,dash=True)
for x,y,w,h,title,body,c in [
 (80,343,320,140,'① 定义任务','目标、验收、难度\nsubmit_task','teal'),
 (440,343,320,140,'② 分配与冻结','输入、模型、固定配置\n保存执行意图','blue'),
 (800,454,320,140,'③ 执行与交付','开发、自检、候选\ndelivery.json','orange'),
 (1160,565,360,140,'④ 独立判决','精确候选与自有证据\nPASS / REJECT','teal')]:
    box(s,x,y,w,h,title,body,c,size=29)
s.line(402,412,431,412,'teal',3,arrow=True)
s.line(762,412,786,412,'blue',3)
s.line(786,412,786,520,'blue',3)
s.line(786,520,798,520,'blue',3,arrow=True)
s.line(1122,520,1144,520,'orange',3)
s.line(1144,520,1144,632,'orange',3)
s.line(1144,632,1158,632,'orange',3,arrow=True)
s.rect(80,566,660,139,'ink',radius=16)
s.text(106,586,'⑤ 主线接回结果',30,'white',True)
s.text(106,637,'成功就取用；三次拒绝则调整并新建关联任务。',24,'lightmuted',width=610)
s.line(1158,734,410,734,'teal',2,arrow=True)
s.line(1340,707,1340,734,'teal',2)
s.line(1340,734,1158,734,'teal',2)
s.text(755,757,'反馈与终态由 agentd 持久记录',23,'muted')

# 08 — Requirements map
s=new('17 项核心需求，组成六块交付责任','需求地图','每一块都要给用户一个可观察的结果，而不是只完成内部组件。',status='需求归纳 · 对应 F01–F17',
 sources=[src(BASE,85,'核心需求 F01–F17'),src(BASE,113,'交付链补充验收')],
 notes='此页把需求表压缩为六个便于评审的工作域，编号完整覆盖 F01–F17。任务域负责持久创建、调度与依赖；原生工作域确保实际工具可用、工作区独立并可复用明确版本的工具；运行保护域确保本地后代受预算约束，控制面和 U 的资源归属清楚。\n\n交付与独审域让代码或报告可取得、证据完整、三个有效拒绝闭环正确；故障与通知域让任务在客户端退出、执行中断和发送不确定时仍能被找到和接续；配置与运维域提供三个主要页面、固定 worker 池和有限生命周期保障。\n\n需求范围贯穿完整产品；V0/V1 的候选分期在第 6 页说明。附录第 32–33 页把每个编号进一步对应到机制和验收。')
items=[('任务与调度','F01 · F02 · F14','创建可重发；输入明确；容量不足排队。','teal'),
 ('原生开发能力','F03 · F04 · F13','保留工具循环；独立状态；显式版本复用。','orange'),
 ('运行保护','F05 · F15','约束本地后代；保护控制面；明确所有者。','blue'),
 ('成果与独审','F06 · F07 · F08','候选可取；独审绑定精确内容；三轮有终点。','teal'),
 ('故障与通知','F09 · F11','通知有记录；中断能继续；恢复有边界。','blue'),
 ('配置与生命周期','F10 · F12 · F16 · F17','固定池、三个页面、安装升级卸载和失败保全。','orange')]
for i,(title,tag,body,c) in enumerate(items):
    s.card(80+(i%3)*488,236+(i//3)*286,464,260,title,body,tag=tag,accent=c,body_size=26,title_size=29)

# 09 — State machine
s=new('五个业务阶段，配合真实执行观察','业务闭环','业务阶段告诉你走到哪里；执行观察告诉你此刻发生了什么。',status='D · 状态表示 / R · 结束语义',
 sources=[src(TASK,5,'五阶段'),src(REL,5,'状态组合与不变量')],
 notes='候选状态表示只有 queued、running、reviewing、finished、canceled。queued 等输入和容量；派发预留后进入 running；执行闭合且候选发布通过校验后进入 reviewing；PASS 或第三次有效 REJECT 进入 finished，分别记录 passed 或 review_failed。第一、第二次拒绝回到 queued。\n\n运行中断保留 running，并用观察字段显示 interrupted、等待原因和可用动作，所以 running 并不等于还有活动 PID。审核离线或无法进行保留 reviewing，不增加 REJECT。取消先保存意图、撤销审核权限并阻止新执行，所有所属执行闭合后才进入 canceled。\n\n取消与判决在同一事务顺序中裁决：终态先提交则保留终态；取消意图先提交则拒绝迟到判决。finished 和 canceled 均不可重开。')
for x,title,body,c in [(80,'queued','等待输入 / 容量','teal'),(470,'running','执行阶段','blue'),(860,'reviewing','冻结候选待独审','orange')]:
    box(s,x,257,320,143,title,body,c,size=34)
s.line(405,327,460,327,'teal',3,arrow=True)
s.line(795,327,850,327,'blue',3,arrow=True)
box(s,1230,257,290,143,'finished','passed / review_failed','teal',size=32)
s.line(1185,327,1220,327,'teal',3,arrow=True)
s.text(1190,215,'PASS / 第 3 次拒绝',20,'teal',True,align='center')
s.line(1020,403,1020,452,'orange',2)
s.line(1020,452,240,452,'orange',2)
s.line(240,452,240,405,'orange',2,arrow=True)
s.text(630,462,'第 1 / 2 次有效 REJECT：沿用合同、输入与模型返修',24,'orange',True,align='center')
box(s,80,551,690,169,'running / interrupted','示例：内存超限；进度已保存；等待资源调整与继续。','blue',size=31)
box(s,800,551,720,169,'canceled','取消意图生效 → 停止与租约核对 → 取消完成。','red',size=31)
s.banner('界面同时呈现：业务阶段 + 执行观察 + 等待原因 + 当前可用动作。',y=746)

# 10 — Data semantics
s=new('四种记录，避免把“重跑”误当成“又失败一次”','业务闭环','一个 Task 可以有多次 Execution；只有有效审核判决才消耗审核机会。',status='D · 对象与关系',
 sources=[src(TASK,147,'核心对象'),src(REL,39,'事务与唯一性约束')],
 notes='Task 是一份不可变业务合同与最终结果。Execution 是一次可追踪的运行，有 launch_id、执行代次、进程身份、资源和闭合证据。Candidate 是一次不可变交付，包含代码 commit 或报告，以及完整证据和摘要。Review 是独立 reviewer 对精确候选作出的有效判决。\n\n示例：E1 因资源问题中断，没有候选；确认停止后 E2 接续，交付 C1，被有效拒绝；E3 返修交付 C2，审核通过。这里有 3 次执行、2 个候选、1 次有效拒绝、1 个最终成功任务。它只贡献一个 benchmark 任务样本。\n\n数据库约束保护每个 Task 和 worker 槽最多一个未闭合 Execution、每个 Candidate 最多一个生效 Review。执行身份未知时也算占位，不能仅因为看不到 PID 就启动第二份。')
for i,(title,body,c) in enumerate([('Task','约定要做什么\n保存目标、验收与终态','teal'),('Execution','记录一次怎样运行\n保存进程、资源与闭合证据','blue'),('Candidate','冻结一次交付内容\ncommit / 报告 / 证据','orange'),('Review','绑定一次独立判决\n候选、身份、租约与依据','teal')]):
    s.card(80+i*364,237,340,246,title,body,accent=c,body_size=26,title_size=32)
s.text(80,524,'同一任务的示例时间线',28,'muted',True)
for x,label,desc,c in [(80,'E1 中断','0 个候选','blue'),(450,'E2 → C1','REJECT × 1','orange'),(820,'E3 → C2','PASS','teal')]:
    box(s,x,578,300,121,label,desc,c,size=29)
for x in [386,756]:s.line(x,635,x+54,635,'muted',2,arrow=True)
s.rect(1195,565,325,160,'ink',radius=18)
s.text(1222,587,'统计只记 1 个任务',27,'white',True)
s.text(1222,638,'3 次执行 ≠ 3 个样本',23,'lightmuted')
s.banner('拆开运行与判决，才能让可恢复故障保持原有审核次数。',y=746)

# 11 — Freeze
s=new('两次冻结：先锁定题目，再锁定具体材料','业务闭环','允许等待依赖，同时保证同一任务的返修始终回答同一个问题。',status='D · 双阶段冻结 / V1 依赖',
 sources=[src(TASK,167,'输入冻结与依赖'),src(BASE,65,'任务合同')],
 notes='提交成功时固定 TaskSpec：项目、目标、范围、成果、验收、难度、明确输入引用和依赖选择规则。主线不选模型；服务展开当时的项目默认值并固定版本。即使任务仍在 queued，也不能改合同。\n\n首次派发前再固定 ResolvedInputs：实际 base commit、上游最终通过 candidate_id、artifact 内容摘要、路径映射和保留引用；同时固定 Assignment 的模型与配置。输入准备可能较慢，完成后仍要重核暂停、取消、授权和资源容量。\n\n返修和恢复沿用这些精确输入，不重新解析 latest。上游失败使下游等待并说明原因，不能计作下游模型失败。上游 PASS 只说明候选通过审核，主线若要合并多个候选，应在流程外准备确定的 base 或另建整合任务。V0 仅独立任务且输入在提交时可取得，依赖 DAG 属 V1。')
s.card(80,245,650,336,'冻结 ①  提交时','TaskSpec\n目标 / 范围 / 成果 / 验收 / 难度\n明确输入与依赖选择规则\n项目默认值和规则版本',tag='题目不再改变',accent='teal',body_size=28)
s.card(870,245,650,336,'冻结 ②  首次派发前','ResolvedInputs + Assignment\n实际 base commit / 上游候选\n内容摘要与保留引用\n绑定模型、worker 与固定配置',tag='材料与执行配置固定',accent='orange',body_size=28)
s.line(744,402,855,402,'teal',3,arrow=True)
s.text(800,433,'等待依赖',24,'muted',align='center')
s.rect(80,614,1440,102,'white',radius=14)
s.text(106,634,'上游 PASS',28,'teal',True)
s.text(340,635,'→ 下游读取精确候选；需要整合时，由主线显式准备新的确定 base。',27,width=1150)
s.banner('调整目标、难度、验收或模型：建立关联新任务，保留原合同与结果。',y=746)

# 12 — Scheduler
s=new('模型分配从公平探索开始，再用足够证据形成偏好','调度与学习','用户配置固定 worker 池；主线只给难度；已绑定任务保持原模型。',status='R · 自动择模 / D·P · 策略',
 sources=[src(BASE,173,'随机到能力偏好'),src(BASE,198,'成熟队列门槛'),src(TASK,190,'固定 worker 选择')],
 notes='调度先过滤不可用、忙碌、禁用或不满足任务条件的槽位。冷启动不预设模型品牌强弱，建议先在拥有合格空闲 worker 的不同模型间等概率选择，再在该模型的合格 worker 内随机选槽，避免把槽位多误解为能力强。\n\n模型与难度组具有足够成熟、可比样本且差异达到预定门槛后，才启用能力偏好；样本不足继续随机，并保留随机探索与对照。难度量表、样本量、观察窗口、差异阈值、探索比例以及强模型忙时如何处理都仍待选择。\n\n首次绑定后，返修和恢复使用同一 worker_id、模型和固定配置。新统计影响后续未绑定的新任务。准入同时取得 worker 槽、预算和声明共享资源；没有合格容量就排队，每个 worker 同时最多一个未闭合执行。')
stages=[('1 过滤','可用性、原生能力\n空闲槽、资源条件','blue'),('2 选择','冷启动：随机\n成熟组：能力偏好','teal'),('3 准入','槽位 + 总预算\n完整共享资源集合','orange'),('4 绑定','模型 + 固定配置\n策略版本 + 分配理由','teal')]
for i,(title,body,c) in enumerate(stages):
    box(s,80+i*365,245,340,170,title,body,c,size=31)
    if i<3:s.line(426+i*365,329,440+i*365,329,c,2,arrow=True)
s.rect(80,459,700,247,'white',radius=18)
s.text(106,481,'为什么先选模型，再选槽位？',30,bold=True)
s.chip(107,543,'模型 A：2 个空闲槽','mint','teal',22)
s.chip(107,597,'模型 B：1 个空闲槽','ice','blue',22)
s.text(437,548,'建议冷启动\nA / B 等概率',28,'teal',True,width=310)
s.card(804,459,716,247,'何时允许学习路由？','同难度、同窗口、成熟样本足够；差异与可比性达到预设门槛，保留随机探索。',accent='orange',body_size=28)
s.banner('槽位数量表达容量；模型偏好必须来自可比较的任务结果。',y=746)

# 13 — Metric counterexample
s=new('完成率可能好看，等待中的任务必须留在视野里','调度与学习','示例数据用于解释统计口径，不是本项目测量结果。',status='D · 统计口径 / 演示算例',
 sources=[src(BASE,160,'审核结果完成率'),src(BASE,198,'固定窗口队列')],
 notes='审核结果完成率定义为 S/(S+R)，S 是最终通过的任务数，R 是三个有效拒绝后的失败任务数。取消和未结束单列；一个任务的三轮候选不能算三个样本。这个公式回答已经得到最终审核结果的任务表现如何。\n\n算例假设两个模型同难度、同观察窗口 H，且各有 10 个已走满窗口的首次分配任务。A 有 2 个在 H 内通过、0 个三轮失败、8 个在 H 时仍未结束；B 有 7 个在 H 内通过、3 个三轮失败。A 的结果完成率为 100%，但按期通过率只有 20%；B 两个值都是 70%。这说明仅按已结束比例排名可能奖励长期积压。\n\n成熟队列的按期通过率是 S_H/N，取消和未完成仍在分母，H 后通过不改写按期历史。产品层还要从提交时点建立队列纳入排队。算例不能证明 B 必然更强，真实启用偏好仍需样本、差异、故障比例和随机对照等门槛。')
table(s,80,240,[230,242,242,242,242,242],['同难度 / 同 H','H 内 PASS','三轮失败','H 时未结束','结果完成率','按期通过率'],[
 ('模型 A','2','0','8','100%','20%'),('模型 B','7','3','0','70%','70%')],heights=[101,101],fs=31,header_fs=23)
for y,label,pct,c in [(523,'A 按期通过',.2,'orange'),(596,'B 按期通过',.7,'teal')]:
    s.text(80,y,label,28,c,True)
    s.rect(310,y+5,1000,34,'line',radius=8)
    s.rect(310,y+5,1000*pct,34,c,radius=8)
    s.text(1352,y,f'{round(pct*100)}%',31,c,True)
s.text(80,684,'结果完成率 = S / (S + R)                 成熟队列按期通过率 = S_H / N',27,'muted')
s.banner('路由启用条件：成熟 + 可比 + 足够样本 + 差异门槛；未满足时继续随机。',y=746)

# 14 — modules
s=new('一个 daemon，按“谁拥有事实”拆成深模块','逻辑架构','外部接口保持简单；跨模块不变量由应用用例的一次短事务完成。',status='D · 模块与事务',
 sources=[src(ARCH,54,'模块所有权'),src(REL,39,'跨模块事务所有者')],
 notes='单 daemon 是本机部署与事务一致性的候选选择，不等于把所有代码塞进一个类。任务服务拥有 TaskSpec、阶段、首次分配、拒绝计数和终态；调度执行拥有选择、预留和运行观察；候选审核拥有冻结候选、租约与判决绑定；成果存储拥有摘要、引用、保留和回收；接入配置拥有项目、固定配置与身份；通知查询拥有队列、投影和可重建统计；平台适配拥有资源组、worktree 与服务接口。\n\n应用用例持有 UnitOfWork，各模块通过受限接口参与同一事务，不各自 commit，也不经 HTTP 调另一个本机模块完成原子动作。审核判决必须连同拒绝计数、任务阶段、成果引用、事件和 outbox 一起提交。\n\nGit、文件复制、hash 和进程调用属于慢外部操作，在写事务外做有界准备，提交前重新核验相关状态；因此单服务仍然需要明确的恢复与对账协议。')
modules=[('任务服务','合同 / 阶段 / 终态','teal'),('调度与执行','选择 / 槽位 / Execution','blue'),('候选与审核','候选 / 租约 / 判决','orange'),('成果存储','摘要 / pins / 回收','teal'),('接入与配置','项目 / 身份 / 固定配置','blue'),('通知与查询','队列 / 投影 / 统计','orange')]
for i,(title,body,c) in enumerate(modules):
    box(s,80+(i%3)*488,238+(i//3)*168,464,145,title,body,c,size=30)
s.rect(80,596,1440,76,'ink',radius=14)
s.text(107,615,'平台适配：监督器 / 资源组 / 工作区 / 服务管理器 / U 接口',29,'white',True)
s.rect(80,701,1440,106,'mint',radius=14)
s.text(106,717,'审核提交 = 判决 + 次数 + 终态 + 成果引用 + 事件 / outbox',30,'teal',True)
s.text(106,763,'由同一应用用例原子提交；统计从已提交事实重建。',24,'teal')

# 15 — Contracts
s=new('契约先行：三个入口使用同一种业务语言','逻辑架构','字段与路由各有唯一来源，页面、CLI、MCP 按同一行为合同接入。',status='R · 接口先行 / F · 候选契约',
 sources=[src(SPEC,7,'契约文件分工'),src(API,177,'API 合同规则'),src(OPS,93,'操作注册表')],
 notes='现有可执行设计契约分工清晰：models.py 定义严格请求响应类型、跨字段约束和候选参数；operations.py 定义方法路径、角色、错误、幂等与 CLI/MCP 映射；generate.py 导出 OpenAPI、JSON Schema 和 API_REFERENCE；check.py 检查生成物、引用、样例和反例。生成文件不手工改。\n\n本次复核 29 个操作，其中 B01–B16 为业务及适配操作，M01–M13 为管理、会话和健康操作；B16 续租只供适配器，不是模型工具。153 个注册模型不等于 153 个 API。协议 /v1 表示拟定 HTTP 主版本，目前具体化的是产品 V0。\n\n写操作使用 request_key 幂等，配置使用 expected_version 检测竞争；202 表示意图被持久接受，任务结果另查。角色、权限、进程和事务仍必须由真实后端验证。合同代码没有生成服务 handler、数据库模型或前端业务实现。')
box(s,80,246,540,175,'models.py + operations.py','严格字段 / 传输映射 / 角色 / 错误\n幂等 / 前置条件 / 客户端映射','teal',size=31)
s.line(632,332,706,332,'teal',3,arrow=True)
box(s,720,246,800,175,'确定性生成','OpenAPI 3.1  +  JSON Schema  +  API_REFERENCE\ncheck.py 校验生成物、样例与规则','blue',size=31)
for i,(title,body) in enumerate([('Dashboard','配置、观察和允许动作'),('主线 CLI / MCP','submit / get / resume / cancel'),('reviewer CLI / MCP','next / evidence / submit / defer')]):
    box(s,80+i*488,470,464,157,title,body,'teal',size=28)
s.rect(80,669,1440,138,'ink',radius=16)
s.text(107,689,'29 个操作',36,'yellow',True)
s.text(480,689,'153 个注册模型',36,'white',True)
s.text(1040,689,'离线检查 PASS',36,'white',True)
s.text(108,755,'覆盖候选结构与一致性；真实鉴权、事务、主机隔离与模型表现仍待验收。',25,'lightmuted')

# 16 — UI conceptual
s=new('三个主页面，让忙碌用户先看到“下一步”','使用体验','概念示意，非已实现页面；权威状态与允许动作均由后端提供。',status='R · 页面范围 / D · 交互示意',
 sources=[src(API,137,'三个主页面'),src(API,154,'交互合同'),src(RUN,172,'配置生效范围')],
 notes='用户主要需要三个视角。总览与任务展示阶段、实际执行、审核轮次、等待原因和下一动作，详情及简单统计作为面板。Worker 配置管理数量、relay、模型参数、凭据来源、资源和固定配置版本，并明确配置变化影响新任务还是后续执行。服务管理展示版本、维护状态和本地操作记录。\n\nV0 服务管理仅提供状态和本地维护说明，升级和保留数据卸载按钮属于 V1。本页 UI 只是一种说明布局，未代表前端已开发或固定视觉要求。\n\n前端不自行推断任务结果或权限。后端返回动作和禁止原因，点击时再次检查。断线、无权、过期快照和空结果必须区别；保存后丢响应使用原 request_key 查回，不能盲重放。暂停新增派发不会停止活动 worker，取消也不是暂停。')
for i,label in enumerate(['总览与任务','Worker 配置','服务管理']):
    x=80+i*488;s.rect(x,236,464,485,'white',stroke='line',radius=18)
    s.rect(x,236,464,66,'ink',radius=18);s.rect(x,278,464,24,'ink')
    s.text(x+23,251,label,29,'white',True)
s.chip(103,325,'执行中断 · 内存超限','sand','orange',20)
s.text(103,389,'导出接口参数校验',28,bold=True,width=410)
s.text(103,444,'审核拒绝：1 / 3\n工作区已保留\n执行已停止并核对',26,'muted',width=410)
s.rect(103,608,188,53,'teal',radius=9);s.text(126,620,'查看继续动作',22,'white',True)
s.text(591,325,'worker-02  /  模型 B',27,bold=True)
s.text(591,382,'模型与参数：固定版本\n资源预算：明确数值\n当前准入：draining',26,'muted',width=412)
s.rect(591,525,416,151,'mint',radius=12)
s.text(611,546,'生效范围可见',26,'teal',True)
s.text(611,590,'新配置用于新任务；\n旧任务保留原配置接续。',24,'teal')
s.text(1079,325,'版本与维护状态',28,bold=True)
s.text(1079,382,'V0：状态与本地说明\nV1：升级 / 保留数据卸载\n异步操作按 ID 查询',26,'muted',width=416)
s.rect(1079,525,416,151,'ice',radius=12)
s.text(1099,546,'停机期间仍可查询',26,'blue',True)
s.text(1099,590,'本地 CLI 读取 U 的\n同一份操作记录。',24,'blue')
s.banner('界面必须解释：发生了什么、证据有多新、为什么等待、当前允许做什么。',y=746)

# 17 — auth
s=new('同一个用户，也需要清楚的角色边界','接入与权限','固定角色连接自动加载凭据；每个后端用例继续核验权限和前置条件。',status='R · 固定角色 / D · 授权合同',
 sources=[src(API,17,'两个固定 MCP 连接'),src(API,77,'权限矩阵'),src(API,110,'凭据生命周期')],
 notes='同一个人既是业务负责人，也可能是平台管理员，但主线任务权限不自动等于管理权限。Dashboard 管理身份配置 worker 和角色；主线提交、查询、继续和取消项目任务；reviewer 领取候选、保存自己的证据和提交独立判决；worker 通过专属交付通道产出候选。管理员也不能用 admin 凭据提交独审判决。\n\n同一 MCP bridge 实现提供 agentd_lead 和 agentd_reviewer 两个固定连接，连接层从私有来源自动附带凭据，模型不需要填写 token，也没有业务工具切换角色。服务端根据凭据得到受信身份，拒绝请求自报 role。\n\n权限和租约在关键提交时重核，撤销或根重绑使旧代次失效。可信本机定位优先防误操作与身份混用，不承诺抵御恶意同 UID 管理员；线程和凭据分离也不能证明模型推理语义绝对独立。')
table(s,80,238,[300,285,285,285,285],['操作','Dashboard 管理','主线','reviewer','worker'],[
 ('配置池 / 管理接入','允许','—','—','—'),
 ('提交 / 继续 / 取消','授权项目内','允许','—','—'),
 ('独立审核判决','—','—','有效领取内','—'),
 ('交付候选','—','—','—','专属结果通道'),
],heights=[82,82,82,82],fs=26)
s.rect(80,623,1440,184,'ink',radius=18)
s.text(110,644,'业务参数 → bridge 自动附凭据 → 后端认证 → 用例授权 → 状态检查',29,'white',True)
s.text(110,704,'凭据轮换 / 撤销 / 根重绑都留痕；历史回执不能绕过当前权限。',26,'lightmuted')
s.text(110,751,'定位：可信本机的职责隔离；恶意同 UID 强隔离不在本轮承诺内。',23,'lightmuted')

# 18 — delivery
s=new('原生工具循环保留，交付出口必须明确','执行与交付','服务用可核对的材料形成候选；开发工具仍由原生 Claude Code 提供。',status='R · 原生能力 / D · 交付协议',
 sources=[src(TASK,204,'Worker 输入与交付'),src(RUN,146,'原生能力'),src(MODELS,1002,'WorkerDelivery 类型')],
 notes='适配器只负责准备环境、启动原生 Claude Code、传递输入、观察运行、停止和收集交付。MCP、subagent、shell、网络与会话仍由原生 harness 负责，具体版本、relay 与私有配置能否兼容属于目标环境验证。\n\n每次执行得到 ExecutionInput/1，绑定精确任务、输入和配置。V0 建议唯一权威出口为执行专属 delivery.json，worker 先写临时文件再原子改名。执行闭合后，适配器核验 schema、路径、成员、大小、hash 和代码对象，再形成受信封装。退出 0、日志里的 success 或 worker 自报 hash 都不能替代这些检查。\n\n代码交付需要合法 commit 与固定 base 的关系；报告交付无需 commit，但必需报告和证据必须齐全。无效交付保存原件与进度，补交属于同任务的有界运行恢复，不消耗 REJECT。worker 自检与 reviewer 的独立验证分别记录。')
steps=[('ExecutionInput/1','任务、固定输入\n配置与运行边界','blue'),('原生 Claude Code','read / edit / shell\nMCP / subagent / session','teal'),('delivery.json','代码或报告\n自检记录与成员清单','orange'),('受信交接与候选','停止证明、实际摘要\n完整性与归属核验','teal')]
for i,(title,body,c) in enumerate(steps):
    box(s,80+i*365,250,340,189,title,body,c,size=28)
    if i<3:s.line(425+i*365,342,440+i*365,342,c,2,arrow=True)
s.card(80,493,700,227,'代码成果','固定 base → 可获取的 candidate commit；未提交修改留在恢复工作区，不隐式混入候选。',accent='teal',body_size=27)
s.card(804,493,716,227,'报告成果','主报告 + 不可变文件与证据；无需制造 commit，也要满足全部必需交付键。',accent='orange',body_size=27)
s.banner('交付格式错误、文件缺失或读取失败：保存进度并诊断，审核次数保持不变。',y=746)

# 19 — Independent review
s=new('独审的关键：材料独立、候选精确、判决有效','执行与交付','reviewer 验证自己的副本，保存自己的证据，并对当前有效领取提交判决。',status='R · 独审 / D·H · 材料与租约',
 sources=[src(TASK,240,'独立材料与租约'),src(API,39,'reviewer 行为'),src(API,217,'判决覆盖与绑定')],
 notes='服务向 reviewer 提供冻结任务合同、候选和完整证据索引。代码材料使用限定授权范围、可核验自足性的 Git bundle；报告使用不可变成员清单。reviewer 在自己的 checkout 或文件副本运行检查，避免测试修改候选原件或 worker 接续目录。必需的 LFS、submodule 或外部材料也必须明确可取。\n\n判决须覆盖冻结验收项，并区分 worker 自检记录与 reviewer 自己产生的证据。PASS 不能包含未满足或无法验证项；REJECT 至少有真实不满足项；环境条件不足使用 defer。服务保证候选绑定与材料检查，外部测试过程仍是 reviewer 声明，不冒充 daemon 监督执行。\n\n领取有 TTL 和绝对总期。自然材料读取或证据上传可让连接层另发 POST renew，普通 GET、ping 或 bridge 存活本身不续租。过期后用新领取重领同候选、重新核验摘要与权限，再复用仍然适用的证据；不能把旧报告直接换 handle 提交。')
for i,(title,body,c) in enumerate([('1 领精确候选','candidate_id + 内容摘要\n固定验收 + 有效 review_handle','blue'),('2 建独立副本','自足 bundle / 成员清单\n自有 checkout，不改候选原件','teal'),('3 存独立证据','命令、实际 HEAD、时间\n退出观察、环境与日志引用','orange')]):
    s.card(80+i*488,239,464,252,title,body,accent=c,body_size=25,title_size=29)
s.rect(80,527,1440,178,'ink',radius=18)
for x,title,body,c in [(110,'PASS','验收满足，任务成功。','lightmuted'),(590,'REJECT','确有不满足项，计一次拒绝。','yellow'),(1085,'defer','无法判断，保留原候选。','lightmuted')]:
    s.text(x,548,title,34,c,True)
    s.text(x,607,body,25,'white',width=398)
s.banner('租约过期：重领同候选并复核；网络存活和模型仍在审核是两回事。',y=746)

# 20 — Recovery story
s=new('发生 OOM 后，系统应保住这一任务','故障与恢复','情境示意：第一次有效拒绝后，返修执行因内存不足而中断。',status='R · 可继续 / D · 恢复机制',
 sources=[src(REL,156,'恢复故障窗口'),src(REL,171,'恢复动作'),src(RUN,172,'任务资源覆盖')],
 notes='设想任务已经被有效拒绝一次，返修时内存超限。先用真实资源观察确认故障，不仅凭 SIGKILL 推断 OOM。系统保存工作区、未提交修改、原生会话引用、日志和已用审核次数。运行故障不增加 REJECT，自动额度耗尽也不自动判定任务失败。\n\n恢复前核对旧执行与本地后代已闭合，并处理不明外部副作用。管理员可以为该任务建立完整资源覆盖，例如把后续 Execution 的预算从 4 GiB 提升至 8 GiB；这是文档中的示例，不是默认配置。旧模型和执行配置保持绑定。当前运行的资源组不会被热改。\n\n主线读取后端当前 action_ref，再显式请求继续。原会话可用就接续，否则新会话接手已有进度；如果输入和工作区无法恢复，可以明确选择同合同重做或取消。副作用不明时仅点击继续不能越过核对，不提供 force 或 reset_rejections。取消是终态，不能作为调资源后恢复的手段。')
steps=[('① 保存进度','代码、会话、日志\n已用拒绝次数 = 1','blue'),('② 核对停止','旧执行与所有后代\n外部副作用是否明确','orange'),('③ 修复条件','例：任务资源覆盖\n4 GiB → 8 GiB','teal'),('④ 显式继续','原会话 / 新会话接手\n原合同、模型、次数','teal')]
for i,(title,body,c) in enumerate(steps):
    box(s,80+i*365,259,340,203,title,body,c,size=30)
    if i<3:s.line(426+i*365,359,440+i*365,359,c,2,arrow=True)
s.card(80,512,700,211,'可以确认停止，且副作用明确','通过准入后建立唯一新执行，接续已保存成果。',accent='teal',body_size=28)
s.card(804,512,716,211,'仍有未知执行或不明副作用','保留占位、显示原因，先核对或明确处置，再决定是否恢复。',accent='orange',body_size=28)
s.banner('恢复额度、审核恢复额度、有效 REJECT 次数，分别记账并保留历史。',y=746)

# 21 — consistency
s=new('可靠性集中在五个“刚好出故障”的窗口','故障与恢复','先保存意图，再做外部动作；响应丢失时，按原操作核对事实。',status='D · 一致性协议 / H · 故障注入',
 sources=[src(REL,100,'五条关键路径'),src(REL,77,'幂等与操作结果')],
 notes='SQLite 的事务不包含文件系统、进程或远端副作用，所以关键不是写一个万能 success，而是保存操作意图、精确身份和已确认步骤，并在重启后对账。\n\n启动窗口使用 launch_id、generation、门控监督器和运行许可，在绑定可核验身份前不让子进程执行业务。候选发布先完成不可变内容与摘要，再提交 DB 引用；文件已发布但事务失败时按原 publish operation 对账。判决、计数、任务结果和 outbox 在一笔事务内提交；响应丢失用原 key 读取结果。\n\n取消只有在所属执行闭合后才释放容量；恢复也只有在旧执行和副作用核清后才能建新执行。同 key 同内容返回原结果，不同内容冲突；当前授权检查优先于历史回执。五类路径是固定业务协议，不引入可编程通用工作流引擎。各机制仍要通过实际主机故障注入。')
table(s,80,232,[190,500,750],['路径','最危险的时刻','候选设计怎样收住结果'],[
 ('启动','进程已创建，DB 尚未记清身份','门控 + launch 身份；未知时保留占位，核对原执行。'),
 ('发布','文件已写好，Candidate 事务失败','先发布内容，后提交引用；按原 publish 操作对账。'),
 ('判决','判决已提交，但响应丢失','判决 / 计数 / 终态 / outbox 原子提交；原 key 查回。'),
 ('取消','父 PID 消失，后代仍在运行','核对整个执行边界闭合后，才 canceled 并释放槽。'),
 ('恢复','远端动作可能已发生，本地无回执','先查副作用；只对已证明安全的同一操作接续。'),
],heights=[91,91,91,91,91],fs=25)
s.banner('“未知”是需要保留的事实；把超时当作未执行，会制造重复副作用。',y=764,size=26)

# 22 — resources / physical
s=new('运行拓扑：把控制余量与执行预算分开','运行架构','S 是常驻服务边界；C 放控制进程；每次 worker 执行拥有独立资源组。',status='D · 拓扑 / H · 主机验证',dark=True,
 sources=[src(RUN,83,'P / S / C 的关系'),src(RUN,91,'进程资源所有权'),src(VAL,41,'目标主机探针')],
 notes='候选拓扑是一个 S 服务，内部有 C 控制组和逐执行 worker 资源组，服务外有按需 U。C 中放监督器和业务 daemon；worker 的 shell、本地 MCP 和 subagent 后代共享该次执行的 CPU、内存和 pids 总预算。一个 worker 的普通故障应被遏制在该执行边界。\n\nS 的准入总账必须为 C 和辅助开销保留余量，只给 C 一个最大值并不能证明有保底资源。U 也有自己的资源预算，S 和 U 同时运行时仍需要主机余量。外部主线、reviewer、已存在的共享服务和远端 MCP 不纳入 worker 预算。\n\n新方案默认不新增旧设计中的专用父池 P，因此没有等同于 P 的跨服务原子总预算保证；如确有需求应重新评审。Linux/WSL2 只是候选平台，必须实测委派、后代归属、worker 超限而控制面可用、杀 daemon 与停 S 的差别，以及 U 在 S 停止后继续。')
s.rect(80,240,1040,485,'darkcard',stroke='#629988',radius=20)
s.text(108,261,'S · agentd 常驻服务 / 总预算与停止边界',31,'white',True)
s.rect(109,326,981,105,'navy',radius=14)
s.text(134,345,'C · 控制资源组',29,'yellow',True)
s.text(134,390,'业务 daemon + 固定宿主监督器 + 控制余量',25,'lightmuted')
for i in range(3):
    x=109+i*334
    s.rect(x,470,313,215,'navy',radius=14)
    s.text(x+22,489,f'Worker {i+1}',29,'white',True)
    s.text(x+22,543,'CPU / memory / pids\n私有工作区与会话\n本地 MCP / 子进程',23,'lightmuted',width=275)
s.rect(1160,240,360,229,'darkcard',radius=18)
s.text(1185,262,'U · 生命周期执行器',27,'yellow',True,width=315)
s.text(1185,318,'独立于 S\n固定运行环境\n安装 / 升级 / 卸载',26,'lightmuted',width=315)
s.rect(1160,496,360,229,'darkcard',radius=18)
s.text(1185,518,'外部进程与服务',28,'white',True)
s.text(1185,574,'主线 / reviewer\n共享 MCP / 远端服务\n由原所有者管理',25,'lightmuted',width=315)
s.text(80,761,'关键实测：一个 worker 超限时，其他任务继续；控制面仍能查询和受理取消。',28,'yellow',True,width=1440)

# 23 — configuration and shared writes
s=new('并行安全还取决于共享写入与配置生效范围','运行架构','worktree 解决源码目录分离；端口、数据库、缓存仍需要明确约定。',status='D · 共享资源与配置生命周期',
 sources=[src(RUN,172,'固定配置 / 槽位 / 覆盖'),src(RUN,200,'共享资源准入')],
 notes='共享资源优先使用任务独立命名空间或专用实例，必须共享写入时才采用明确协调。项目登记规范 resource_id 以及读写需求，调度在一笔事务中取得完整资源集合、worker 槽与总预算；任一项不足就全不取得，避免部分占有后互等。共享副作用只能在取得 claim 后开始。\n\n进程闭合且远端副作用核清后才能释放 claim；超时、缺心跳或重启不会自动释放未知持有。内部协调只覆盖遵守同一声明的参与者，不自动发现任意原生 shell 的未声明写入，外部 reviewer 必须使用独立资源或遵守同一外部协调合同。\n\nWorkerSlot 管理可变准入状态，ExecutionConfig 是不可变执行内容，TaskResourceOverride 只影响下次执行。enabled 接新任务；draining 拒绝新绑定但保留旧任务返修接续；disabled 让旧任务明确等待，不隐式取消。减少槽位不强杀，也不静默换模型。')
s.card(80,240,700,263,'共享资源：先声明，再取得全部占用','优先使用任务独立命名空间。\n共享写入使用明确独占声明。\n槽位、预算与资源一次取得；\n未知持有继续核对。',accent='teal',body_size=28)
s.card(804,240,716,263,'配置：区分三个生效范围','WorkerSlot 管准入；\nExecutionConfig 固定执行内容；\n任务资源覆盖只作用下一次执行。',accent='blue',body_size=28)
table(s,80,541,[300,380,760],['槽位状态','新任务','旧任务返修 / 恢复'],[
 ('enabled','可首次绑定','按原配置取得原槽'),('draining','停止新绑定','允许旧任务接续，完成后再退役'),('disabled','不可首次绑定','明确等待，管理员恢复准入后再继续')
],heights=[63,63,63],fs=25)
s.text(80,799,'内部声明协调只保证约定范围；共享外部服务和任意未声明写入仍需项目约束。',22,'muted')

# 24 — notification
s=new('通知是提醒，持久队列才是工作来源','协作与通知','通知失败仍能主动查询；发送、收件、领取和判决分别记录。',status='R · 通知目标 / D·H · 客户端路径',
 sources=[src(TASK,293,'两条通知链路'),src(BASE,243,'V0 / V1 通知范围')],
 notes='业务链路在候选发布、终态或重要中断时保存事实及必要 outbox，主线和 reviewer 随时可经 CLI/MCP 查队列。唤醒链路只向已登记的既有根发送短提示，引导读取当前 inbox 和领取；提示不携带完整证据，也不授权任务结果。\n\n旧实现已有 codex queue 适配源码路径，但它只证明旧版本存在此方式，不能证明目标客户端能收到、唤醒空闲根并实际领取。V0 可由用户打开客户端主动查队列；V1 至少验证一种真实消息传输。客户端关闭时不承诺自动启动，根忙碌时依客户端支持方式排队。\n\n发送回执丢失意味着消息可能已经入队，必须保存 uncertain 并核对，不能不断启动新的发送。领取和最终判决使用自己的幂等与租约规则，重复提示不产生重复计分。合并提示减少打扰，但不能抹掉未解决事项或压制新工作。')
s.rect(80,247,1440,193,'ink',radius=18)
s.text(109,268,'持久业务链',30,'yellow',True)
s.text(109,323,'候选 / 终态 / 中断事项  →  outbox + inbox  →  主动查询  →  领取与处理',31,'white',True,width=1380)
s.text(109,382,'队列来自已提交业务事实；任务不因提示发送失败而丢失。',25,'lightmuted')
s.rect(80,477,1440,166,'white',radius=18)
s.text(108,496,'客户端提醒链',30,'blue',True)
s.text(108,552,'发送提示  →  传输回执  →  根线程实际收件  →  调用 next_review',29,'ink',True)
s.text(108,600,'每一跳都要单独观察，真实支持能力需在目标客户端验证。',23,'muted')
for x,title,body,c in [(80,'在线且支持','提示后读取实时队列','teal'),(570,'离线 / 已关闭','保留事项，恢复后主动查询','blue'),(1060,'发送结果未知','保留 uncertain，先核对','orange')]:
    box(s,x,683,460,122,title,body,c,size=27)

# 25 — storage lifecycle
s=new('成果能交付，依靠“内容 + 引用 + 保留义务”','数据架构','SQLite 管事实，Git 与文件管正文；工作区、成果和历史索引各有生命周期。',status='D · 存储 / P · 保留期限',
 sources=[src(RUN,5,'存储分工'),src(REL,121,'候选发布'),src(REL,196,'保留与备份')],
 notes='SQLite 保存任务、分配、执行、判决、通知以及成果归属和引用；Git 与文件保存代码、报告、证据、日志和可恢复工作区。先在私有暂存核验内容并持久发布，再以短事务登记 Candidate、Artifact、阶段和 outbox；目录存在本身不表示候选已经生效。\n\n历史索引长期保留不等于正文永久保留。active_task、dependent_task、delivery、explicit_keep 和未完成发布/备份的 pin 保护需要保留的内容，ReadGuard 保护一次实际读取不被并发删除。回收必须与新引用申请互斥；到期回收留下 expired 元数据，损坏或丢失是另外的完整性事件。未选择期限时默认 retain，不自动到期。\n\n备份需要同时包含一致 DB 快照、承诺保留的 Git/文件和清单；必须在新目录恢复并实际取出成果。恢复旧快照创建新的 store_epoch 与授权代次，使旧游标、凭据、handle、动作和未确认客户端写入失效，避免把旧请求自动重放到更早的历史。恢复备份不能被当作随意覆盖新成果的回退按钮。')
s.card(80,239,700,239,'SQLite：可事务提交的事实','Task / Assignment / Execution / Review\n幂等回执、通知、配置、成果索引\n统计由这些事实重新计算',accent='teal',body_size=27)
s.card(804,239,716,239,'Git + 文件：可验证的成果正文','commit 与受保护引用\n报告、证据、日志、会话、工作区\n内容摘要、成员清单与大小',accent='orange',body_size=27)
for i,(title,body,c) in enumerate([('发布','暂存核验 → 持久内容\n→ DB 引用与候选生效','teal'),('保留','活动 / 依赖 / 交付 pins\n+ 传输 ReadGuard','blue'),('回收','到期且义务闭合\n保留摘要与过期事实','orange'),('恢复','DB + Git + 文件清单\n新 epoch 阻止旧写重放','teal')]):
    box(s,80+i*365,525,340,180,title,body,c,size=30)
s.banner('只有索引没有原件，无法完成交付；只有文件没有事务引用，也不等于发布成功。',y=746,size=26)

# 26 — lifecycle
s=new('升级时，负责升级的人必须留在服务之外','运行架构','U 管安装、升级、卸载；服务管理器管 S 的日常启动、停止与重启。',status='R · U 独立 / D·H · 切换方案',dark=True,
 sources=[src(BASE,221,'生命周期要求'),src(RUN,229,'升级与锁交接'),src(RUN,247,'故障与回退边界')],
 notes='已确认责任是 U 在 S 的停止边界外，按需执行安装、升级和卸载；U 自身程序与 journal 位于不会被此次切换删除的固定环境。首次安装不依赖 daemon，关闭发起终端或停止 S 后仍能按原 operation_id 查询与接续。\n\n候选升级方案在独立最终目录准备新版本，旧服务继续运行；然后建立维护 hold、停止新增工作并排空在途执行和写入。确认整个 S 及后代闭合后，U 取得离线 state lock，一致备份、检查兼容并切换。新版先维护态启动、核任务与引用，通过后只释放此次 hold，保留用户原暂停。lifecycle lock 串行主机变更，state lock 保证业务单写；持久 fence 保护锁交接间隙。\n\n该方案有 API 停机窗口，不承诺 worker 不停的热升级。新版失败时先保全当前数据，只有旧程序兼容当前数据库才可回退代码，不能自动恢复旧备份覆盖切换后写入。V0 只实现最小 U 安装；完整升级与保留数据卸载在 V1。')
s.rect(80,235,1440,91,'darkcard',radius=16)
s.text(110,256,'U 始终持有同一 operation_id；操作 journal 在 S 停止时仍可查询和接续。',29,'yellow',True,width=1378)
steps=[('1 准备','独立版本目录\n旧 S 继续运行'),('2 排空','维护 hold\n核对在途执行'),('3 停机','写入屏障\n证明 S 闭合'),('4 切换','离线锁 + 备份\n受支持的迁移'),('5 验证','新版维护态\n核对事实与引用')]
for i,(title,body) in enumerate(steps):
    x=80+i*292
    s.rect(x,379,272,194,'darkcard',radius=16)
    s.text(x+20,399,title,31,'white',True)
    s.text(x+20,456,body,25,'lightmuted',width=232)
    if i<4:s.line(x+276,475,x+287,475,'yellow',2,arrow=True)
s.line(80,624,664,624,'lightmuted',4)
s.line(664,624,1220,624,'yellow',4)
s.line(1220,624,1520,624,'lightmuted',4)
s.text(80,646,'旧服务可继续使用',24,'lightmuted')
s.text(943,646,'受控停机窗口',24,'yellow',True,align='center')
s.text(1520,646,'验证后恢复',24,'lightmuted',align='right')
s.rect(80,723,1440,84,'darkcard',radius=14)
s.text(108,742,'失败保全：保留原版、当前数据、备份与操作记录；回退取决于数据兼容和新增写入。',27,'white',True,width=1385)

# 27 — tradeoffs
s=new('为什么这样做：每个选择都有明确收益与代价','设计取舍','用足够的机制兑现边界，避免让主线承担运行系统的内部步骤。',status='D · 方案论证',
 sources=[src(DEC,7,'设计选择独立论证'),src(ARCH,54,'模块与事务')],
 notes='这些选择是当前候选设计，不是宣称某种技术普遍最好。单 daemon 加 SQLite 简化本机部署并支持必要原子事务，代价是单机容量与控制面瓶颈需要量化；原生 harness 薄适配保留成熟工具能力，代价是配置、版本和资源归属需要支持矩阵。\n\n外部 reviewer 避免再托管一套账号和推理生命周期，代价是客户端离线时等待，唤醒能力要实测；不可变任务和候选带来明确评审与统计口径，代价是需求变化时要建立关联新任务。阶段与运行观察分层避免故障误计分，但组合约束仍然复杂，需要系统验收。\n\n独立 U 让 daemon 停止后还有明确的执行与恢复责任，代价是锁交接、资源余量和停机窗口。固定窗口统计减少未完成样本被丢弃造成的偏差，但要等待样本成熟，仍无法完全消除同难度任务差异。选择是否合适，要靠针对这些代价的实验与验收判断。')
table(s,80,233,[290,540,610],['选择','得到的收益','接受的代价 / 必须验证'],[
 ('单 daemon + SQLite','统一事实；本机部署简单；关键变化可原子提交','单机容量有限；慢工作必须有界，保护控制响应'),
 ('原生 harness 薄适配','保留 MCP / subagent / shell 与原生迭代','版本、配置、relay 与子进程归属需要实测'),
 ('外部独立 reviewer','职责清楚；复用已有客户端与独立根','客户端离线会等待；提示到实际领取需验收'),
 ('冻结合同与候选','返修问题不漂移；证据、判决和统计可追溯','需求变化需新任务；引用与保留管理更严格'),
 ('独立 U + 停机切换','S 停止后仍有执行者；操作可接续','需要锁与 fence；有停机窗口；回退受数据约束'),
 ('成熟窗口 + 随机探索','未完成任务不从分母消失；新模型有取样机会','等待样本成熟；相关表现仍非纯因果能力'),
],heights=[86,86,86,86,86,86],fs=24)

# 28 — validation journey
s=new('验收的单位：同一条真实用户旅程','验证与交付','从安装产物到最终成果，逐层记录 PASS / FAIL / NOT RUN。',status='D · 验收计划 / H · 真实验证',
 sources=[src(VAL,5,'验收顺序'),src(VAL,25,'工作包'),src(VAL,79,'C01–C16 补充验收')],
 notes='首要旅程是使用真实发布目录和最小 U 完成安装，经 Dashboard 配置，主线提交真实任务，worker 交付代码或报告，外部 reviewer 独立审核，主线实际读出成果。服务健康、页面展示或 CLI 可启动都只是局部证据。\n\n进一步必须验证第一轮和第三轮 PASS、第三次 REJECT、重复请求和迟到判决，证明唯一终态和计数；三个真实 worker 至少两种模型重叠工作，其中一个超限时另两个仍可交付；保留进度并在 daemon 重启后显式接续；独立副本与自有审核证据；原始字节和长中文目标不截断；完整备份在新目录实际恢复。\n\n每条结果标记源码版本、实际程序路径、主机、客户端、模型配置和证据。目标故障必须先被证明成功注入，才能声称隔离通过。离线合同、真实模型、真实客户端和目标主机分开记录；缺一层就保留 NOT RUN。V1 的通知、学习和升级按其阶段验收。')
s.rect(80,235,1440,103,'ink',radius=16)
s.text(108,259,'U 安装 → 页面配置 → 主线提交 → 真实 worker → 外部独审 → 实际取回成果',31,'white',True,width=1380)
checks=[('终态唯一','首轮 / 第三轮 PASS；三拒绝停止；重复请求不重计。','teal'),
 ('真实并行','3 worker、至少 2 模型；一个超限，其他任务继续。','orange'),
 ('中断可继续','工作区保留；旧执行核清；原会话或新会话接手。','blue'),
 ('材料完整','长中文验收、原始字节、独立副本、分段证据齐全。','teal'),
 ('生命周期明确','关终端 / 停 S / U 崩溃后按原操作核对接续。','orange'),
 ('备份真能恢复','新目录启动，实际读出 commit、报告和审核证据。','blue')]
for i,(title,body,c) in enumerate(checks):
    s.card(80+(i%3)*488,370+(i//3)*214,464,191,title,body,accent=c,body_size=25,title_size=28)
s.text(80,810,'结果必须绑定同一候选版本与真实入口；mock、历史通过记录和近似环境单列。',20,'muted')

# 29 — measuring value
s=new('证明收益，需要同时看速度、等待、用量和对照','验证与交付','机制可运行与产品有效果分别报告；缺失数据明确标为未知。',status='D · 指标口径 / 无实测收益',
 sources=[src(BASE,184,'最小效果指标'),src(BASE,198,'队列与对照')],
 notes='吞吐比较同一预定任务集的串行与并行墙钟时间，以及固定观察时段内 PASS 数；如果并行增加资源要注明，任务集未全部结束不能宣称整体加速。交付时延从提交到最终审核，包含排队、审核和中断等待，成功和三轮失败分列，未结束展示年龄，取消单列。\n\nusage 记录原生可得的 input、output、cache、reasoning 字段及来源，避免累计值、增量或 subagent 汇总重复计算；缺失为 null 并给覆盖率。只掌握 worker 数据时只能叫 worker tokens。每个 PASS 的已知 token 消耗需包含该批失败、取消和中断任务的消耗；没有可靠价格和完整用量时不能称省钱。\n\n学习策略与随机基线比较同难度、同观察窗口的按期 PASS、时延和用量覆盖率，记录初始策略分组，保留未完成和取消。共享池会互相影响，无有效对照只能说分配改变，不能说优于随机。此页没有项目测量值。')
metrics=[('吞吐','相同任务集的总墙钟时间\n固定时间内 PASS 数','输入、验收、资源预算一致；串行基线可比较。','teal'),
 ('交付时延','提交 → 审核终态\n含排队、审核、中断等待','成功 / 三轮失败分列；未结束年龄和取消单列。','blue'),
 ('已知用量','整批尝试与返修的 tokens\n同时报告角色范围与覆盖率','缺失为未知；失败消耗保留；token 不等于账单。','orange'),
 ('学习增益','能力策略 vs 随机对照\n同难度、同成熟窗口','记录初始策略组；样本不足时保留随机。','teal')]
for i,(title,metric,why,c) in enumerate(metrics):
    x=80+(i%2)*732;y=239+(i//2)*279
    s.rect(x,y,708,255,'white',radius=18)
    s.text(x+25,y+20,title,32,c,True)
    s.text(x+25,y+78,metric,29,bold=True,width=658)
    s.text(x+25,y+174,why,25,'muted',width=658,line_height=1.35)

# 30 — decision / action
s=new('下一步：把关键未知逐个变成可验收的承诺','决策与行动','以下是推进顺序建议；没有替项目擅自批准分期、平台或参数。',status='D · 推进建议 / P·H · 待闭合',
 sources=[src(DEC,71,'待定决策'),src(VAL,25,'A–E 工作包'),src(BASE,308,'决定清单')],
 notes='首先由产品负责人选择首发环境和是否接受 V0 的明确限制：单项目独立任务、随机择模、主动领取、自动恢复可以为零、最小 U 安装。然后用准确 OS、内核、资源委派、原生 CLI、模型 relay 和客户端版本做关键探针。主机假设失败时重审方案，而不是继续把未经验证能力扩成更多平台。\n\n接着评审并冻结 V0 精确合同与限额，前后端可分别开发但尽早接通同一真实任务链。随后完成三轮、取消竞争、幂等、故障窗口、资源隔离和实际成果读取。V1 的通知、依赖、自动恢复、学习与生命周期按范围补齐。\n\n需要选择的参数包括难度量表、观察窗口、最小样本、差异/探索比例、租约与恢复预算、资源/磁盘限额、保留期限及升级支持窗口。候选初值不能在实现中被悄悄当作批准值。当前最值得投入的下一产物，是关键探针证据与一条真实闭环，而不是更多并列架构。')
table(s,80,236,[250,720,470],['决策包','需要明确什么','形成的可评审结果'],[
 ('先定范围','首发主机组合；V0 阶段限制；原生工具与客户端矩阵','产品范围决定 + SupportProfile'),
 ('再证假设','资源委派、后代归属、U 独立、通知与长审核路径','版本准确的探针证据'),
 ('冻结合同','API、权限、幂等、资源、大小、租期、恢复与保留参数','唯一契约与可运行正反例'),
 ('交付闭环','配置 → 提交 → 执行 → 独审 → 成果；再验证并行故障','真实端到端验收记录'),
],heights=[92,92,92,92],fs=26)
s.rect(80,659,1440,147,'ink',radius=18)
s.text(112,678,'值得兑现的结果',25,'yellow',True)
s.text(112,727,'主线只管提出任务与使用成果，系统把过程推进到一个可信的结论。',35,'white',True,width=1370)

# 31 — evidence states
s=new('附录：当前到底有什么，哪些仍然未知','证据与追踪','报告制作时重新运行了现有离线检查，未运行真实服务、模型或主机验收。',status='F · 本次复核 / R·D·H·P · 状态',
 sources=[src(BASE,5,'决定状态'),src(SPEC,22,'校验方法与边界'),src('audit/VALIDATION.md',1,'快照审计')],
 notes='本次在 /home/cying/agentd-new 使用文档指定的已有解释器运行 python -m specs.agentd_v1.check，结果 PASS。报告值为 29 operations/routes、153 registered_models、154 schema_definitions、8 valid_examples、7 structural_rejections、7 semantic_rejections、5 json_policy_rejections、3 split_contract_regression_checks，三份生成物一致。runtime_model_host_validation 明确为 NOT_RUN。\n\n同时执行 sha256sum -c audit/SHA256SUMS，原始快照清单的 32 个受覆盖文件均 OK。本次只新增 reports/agentd-architecture 下的报告与生成源码，原审计描述的是既有快照，不把新增报告伪称为原来已审计内容。运行 Python 检查可能生成可删除的 __pycache__，不属于设计变更。\n\nR 是用户已确认要求；D 是候选设计；H 是需要实际主机、模型或客户端验证的假设；P 是尚未选定参数；F 是有版本和范围的事实。离线 PASS 不能将 D/H/P 升级为已支持能力。报告内标为示例的任务、界面与统计数字不属于项目实测。')
for i,(label,title,c) in enumerate([('R','已确认要求','teal'),('D','待评审设计','blue'),('H','待验证假设','orange'),('P','待选择参数','orange'),('F','有范围的事实','teal')]):
    x=80+i*292
    s.rect(x,237,272,131,'white',radius=16)
    s.text(x+20,249,label,53,c,True)
    s.text(x+88,271,title,24,bold=True,width=165)
table(s,80,409,[430,355,655],['检查范围','本次结果','结论边界'],[
 ('契约结构与一致性','PASS','29 操作；153 注册模型；3 份生成物一致'),
 ('样例与反例','PASS','8 正例；19 反例；3 组拆分回归'),
 ('原始快照文件摘要','32 / 32 OK','核对既有 SHA256SUMS 覆盖文件'),
 ('真实服务 / 模型 / 主机','NOT RUN','没有新服务实现与真实效果验收证据'),
],heights=[77,77,77,77],fs=25)
s.text(80,783,'离线可执行设计契约 ≠ 已运行的新产品。每页保留文件依据，详细行号见讲解备注。',24,'muted')

# 32 — requirements trace 1
s=new('附录：需求追踪 F01–F09','证据与追踪','编号沿用需求基线；机制是候选实现路径，验收要落到真实行为。',status='需求 → 设计 → 可观察验收',
 sources=[src(BASE,85,'核心需求'),src(TASK,147,'对象与交付'),src(VAL,79,'补充验收')],
 notes='F01 验证主线退出后任务仍存在，以及创建丢响应后原 key 返回同一任务。F02 验证固定池自动择模、容量排队、同任务和同槽唯一未闭合执行。F03 在真实执行环境验证 read/edit/shell/MCP/subagent，而不只是单独 CLI 探针。\n\nF04 验证任务写入不改变模板和其他 worker 状态；F05 真正注入资源故障，核后代归属与其他任务继续；F06 工作区回收后仍能取得保留候选和报告；F07 reviewer 独立副本、自有证据与租约绑定；F08 三个有效拒绝原子结束，重启和重发不重计；F09 持久事项和通知传输分离。\n\n这些是完整需求的追踪，交付按已接受的版本范围进行。V0 主动领取，V1 才承诺经验证的客户端提示路径；V0 独立任务，依赖 DAG 在 V1。')
table(s,80,237,[100,340,580,420],['编号','需求','设计机制','关键验收'],[
 ('F01','创建与查询','TaskSpec + 持久回执 + request_key','退出与重发均不丢、不重复'),
 ('F02','自动分配与并行','固定池；随机 / 能力偏好；原子准入','无模型指定；唯一活动执行'),
 ('F03','原生 worker','原生 CLI + 薄适配 + 支持矩阵','真实 MCP / subagent 可用'),
 ('F04','独立执行环境','私有 worktree / 配置 / 会话 / 临时状态','写入不串到模板或其他任务'),
 ('F05','资源保护','逐执行 CPU / memory / pids 总预算','一个超限，其他任务仍可完成'),
 ('F06','成果保存','不可变候选、保留引用与完整清单','工作区清理后成果仍可读取'),
 ('F07','独立审核','独立副本、有效租约、候选证据绑定','自审、过期与错候选均拒绝'),
 ('F08','三轮闭环','判决 / 次数 / 终态 / outbox 同事务','三拒绝结束，不开始第四轮'),
 ('F09','通知与唤醒','持久业务队列 + 适配器提示','失败可查询；重发不重计分'),
],heights=[57]*9,fs=23,header_fs=23)

# 33 — requirements trace 2
s=new('附录：需求追踪 F10–F17','证据与追踪','运行责任、配置版本与升级恢复，都是交付范围的一部分。',status='需求 → 设计 → 可观察验收',
 sources=[src(BASE,85,'核心需求'),src(RUN,172,'配置与运行机制'),src(VAL,25,'交付与验收')],
 notes='F10 固定 worker 池要把配置请求值、生效观察和未知分开，更新产生新版本而不热改绑定任务；F11 明确故障类别、自动预算、停止核对、副作用处置和显式继续；F12 三个页面和薄客户端使用同一后台事实。\n\nF13 让原生工具可用，工具代码作为普通成果审阅后由主线选择共享版本，基础阶段无需自动推广平台。F14 固定上游 Task ID 和精确产物，失败使下游等待，PASS 不代表已合并。F15 同时说明控制面、worker 后代、外部 Codex 和 U 的资源所有权。\n\nF16 安装、升级和卸载统一交 U，记录原 operation_id，在停 daemon 或终端后仍可接续；F17 支持窗口先明确，失败保全当前数据，回退要看实际数据兼容和切换后写入。V0 最小 U 安装和本地备份恢复，V1 完整生命周期流程。')
table(s,80,237,[100,340,580,420],['编号','需求','设计机制','关键验收'],[
 ('F10','固定 worker 池','可变槽位 + 不可变配置 + 任务资源覆盖','更新不热换旧任务模型'),
 ('F11','有界故障恢复','固定恢复策略；action_ref；原操作对账','耗尽后保留进度，可显式继续'),
 ('F12','Dashboard Web UI','三个主页面；后台动作与一致快照','断线 / 无权 / 空结果分开'),
 ('F13','基本工具复用','普通工具成果；主线选共享版本','工具可用，版本不串用'),
 ('F14','任务依赖','固定 ID 的 DAG；两阶段输入冻结','上游失败仅使下游等待'),
 ('F15','运行与资源归属','S / C / 逐执行资源组；独立 U','超限不拖垮控制与升级者'),
 ('F16','生命周期接续','U + journal + lock / fence','停 S 后按原操作继续'),
 ('F17','升级兼容与保全','支持窗口；一致备份；维护态验证','不兼容拒绝，不覆盖新成果'),
],heights=[64]*8,fs=23,header_fs=23)

# 34 — proposed parameters
s=new('附录：这些数值仍是候选，不能静默变成承诺','参数与支持范围','首发 Linux / WSL2 组合待选择；每个主机组合单独验证。',status='P · 建议初值 / H · 目标环境',
 sources=[src(MODELS,44,'DRAFT_PARAMETERS'),src(REL,196,'保留策略候选'),src(VAL,41,'参考 profile 与负载')],
 notes='此页选取会影响实现与运营的候选值，便于评审，不表示推荐值已经获准或真实测量通过。契约给出的审核 TTL 为 1800 秒、单次持有绝对上限 28800 秒；候选成果成员总量 1 GiB、bundle 2 GiB；审核证据段 256 KiB、总量 16 MiB；执行自动恢复候选为 V0 零次、V1 两次，仍受整体时间与副作用核验约束。\n\n存储候选最终成果和必要独审证据保留 90 天，但未选择策略时使用 retain，不得隐式按 90 天删除。参考主机是 8 逻辑 CPU、32 GiB 内存，仅用于校准而非最低配置。\n\n控制面查询 p95 ≤ 1 秒、p99 ≤ 3 秒的候选测量条件是：已认证 loopback、标准 50 条摘要页、10,000 终态与 100 未结束任务、5 并发只读客户端、3 worker 施压并有候选复制，持续 10 分钟且至少 1,000 请求，错误和超时不能排除。成熟窗口 H、样本门槛、差异及探索比例尚无定值，未定时保持随机。')
table(s,80,235,[370,380,690],['参数','P 建议初值','选择与使用边界'],[
 ('审核领取租期','30 分钟；绝对上限 8 小时','自然活动后显式续租；过期不能复活旧 handle'),
 ('自动执行恢复','V0：0 次；V1：2 次','与有效 REJECT 分开；恢复前仍核停止与副作用'),
 ('候选内容上限','成员总量 1 GiB；bundle 2 GiB','超限明确处理，不静默截断必要材料'),
 ('审核证据大小','每段 256 KiB；总量 16 MiB','分段清单验证顺序、总长度与总摘要'),
 ('最终成果保留','90 天','未定策略时 retain；有效 pin 保护义务优先'),
 ('参考主机','8 逻辑 CPU / 32 GiB 内存','校准 profile，不能写成已批准最低配置'),
 ('查询响应指标','p95 ≤ 1 秒；p99 ≤ 3 秒','明确负载与错误率条件；当前没有实测结果'),
],heights=[66]*7,fs=24,header_fs=23)
s.text(80,777,'另须选择：难度量表、观察窗口 H、最小样本、差异门槛、探索比例与升级支持窗口。',23,'muted')

# 35 — history lessons
s=new('附录：历史问题给出风险线索，验证仍要重新做','历史证据','以下为项目专题对旧版本记录的归纳；本报告没有重跑历史实验。',status='F · 旧范围事实 / D · 新门槛',
 sources=[src(DEC,22,'旧问题与版本范围'),src(DEC,39,'P0 / P1 复查教训')],
 notes='历史资料的价值是解释为什么这些边界值得投入，不能拿旧修复或旧测试结果充当新方案验收。旧 reviewer 视图曾把目标裁至 4096 字节，启示是完整性包含验收目标，不只是附件。候选准备期间出现过 task/list 30 秒超时和静态页超过 3 秒无响应；缺现场栈，不能把某一函数认定为全部根因，但必须验控制面在重负载下可用。\n\nClaude Code 2.1.289 的合成探针显示部分原生工具能运行，不代表项目 skills、hooks、agents、MCP 与授权链齐全。另有实际安装入口和生成配置失败，说明必须从独立发布目录跑同一真实任务，避免开发路径掩盖缺依赖。\n\n旧文档与程序对数据库迁移能力的描述不一致，说明需要唯一权威来源和支持窗口。历史机械 Git 操作、证据字节、配置生效、磁盘容量等更多教训在来源专题中；本报告用第 21、23、25、28 页的机制与验收承接。')
table(s,80,235,[430,500,510],['旧记录说明的风险','对新设计的启示','对应验收'],[
 ('审核目标曾被裁至\n4096 字节','目标、验收、候选、证据\n都需要完整可读','长中文目标的最后一句\n仍决定实际验收'),
 ('候选准备时查询超时\n控制进程仍然存活','复制、hash、Git、解析\n有界并避开 HTTP 阻塞','放慢候选准备，仍可\n查询与受理取消'),
 ('合成原生探针可运行\n项目配置却有缺项','工具可见、配置加载、\n授权可用与产物取得分开核','在实际 worker 环境\n使用所需 MCP / subagent'),
 ('真实入口 / 生成配置失败\n组件检查曾绕过该路径','独立发布目录、生成配置\n和真实 CLI 组成同一链','让原开发路径不可访问\n仍能跑通任务'),
 ('指南与程序对旧库转换\n给出了不同承诺','唯一权威来源；明确\n支持版本与拒绝行为','不支持版本在写库前\n拒绝并保留数据'),
],heights=[100]*5,fs=25,header_fs=23)

# 36 — sources
s=new('按问题返回文件，继续评审与实施','来源导航','每页的备注和离线讲解稿都保留具体来源；字段和路由以契约源码为准。',status='报告依据 · 项目快照 2026-10-28',
 sources=[src(BASE,1,'需求基线'),src(ARCH,1,'架构总览'),src(TASK,1,'任务与独审'),src(RUN,1,'运行与生命周期'),src(REL,1,'事务与存储'),src(API,1,'接入与接口'),src(VAL,1,'验收计划'),src(DEC,1,'决策与证据'),src(SPEC,1,'可执行契约')],
 notes='本报告根据当前工作区现有资料形成，没有修改产品基线、行为专题或契约源码。阅读路径可以按问题跳转：先产品基线，再架构总览，再相关专题；字段、错误、权限映射和示例查可执行契约及生成 API 参考。\n\n资料权威分工：需求基线拥有目标、角色、终点和范围；架构总览拥有系统边界和模块职责；六个专题拥有行为与恢复约束；models.py / operations.py 拥有结构与传输映射，生成物不手工修改。\n\n报告交付包含可编辑 PPTX、嵌入字体的矢量 PDF、带目录和讲解备注的离线 HTML、逐页讲解与依据 HTML，以及可复现的生成源码。浏览器方向键翻页，N 展开备注，G 打开目录，F 全屏。需要转发时优先 PDF；需要修改内容使用 PPTX 或生成源码；离线 HTML 自身可放映，来源链接则需要保留与项目 docs/specs 的相对目录。')
table(s,80,234,[380,630,430],['阅读入口','回答的问题','本报告对应页'],[
 ('产品需求基线','目标、角色、成功标准、版本范围、统计口径','02–04 / 06 / 08 / 12–13 / 29'),
 ('软件架构总览','系统组成、模块职责、文档权威','05 / 14–15'),
 ('任务与独立审核协议','状态、输入、交付、独审、通知','07 / 09–12 / 18–19 / 24'),
 ('运行边界与生命周期','资源归属、固定配置、共享资源、U','20 / 22–23 / 26'),
 ('事务恢复与成果存储','并发不变量、故障窗口、保留、备份','10 / 20–21 / 25'),
 ('接入与接口行为','权限、凭据、HTTP、页面与管理动作','15–17'),
 ('验收计划 + 决策与证据','如何分批交付、历史依据、待闭合事项','27–30 / 34–35'),
 ('specs/agentd_v1 + audit','字段、路由、生成物、样例、离线证据','15 / 31–34'),
],heights=[62]*8,fs=23,header_fs=23)
s.text(80,796,'报告示意不替代协议；实现变化应同步需求影响、所属专题、契约生成物与验收证据。',23,'muted')


if __name__=='__main__':
    assert len(slides)==36
    export_all(slides)

