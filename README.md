# **optimization_tutorial**
本仓库为零碳能源系统组24年寒假模型优化培训资料，需要同学们做：

1. 安装配置python和求解器环境，不限于gurobi
2. 阅读Baseline模型并补全`optimization_example.py`中的代码完成测算
3. 打包输出文件作为后续结果对比，并撰写分析报告，于收假前将代码+结果+报告打包发送至guoguoloveu@icloud.com

如果想更进一步，你可以：
1. 阅读gurobi求解器手册，理解gurobi日志，可以参考博客 [理解gurobi求解器日志｜果果的博客](https://gwyxjtu.github.io/2022/05/21/%E7%90%86%E8%A7%A3gurobi%E6%B1%82%E8%A7%A3%E5%99%A8%E6%97%A5%E5%BF%97/)
2. 尝试使用git进行代码合作，将你的代码和报告以pull request的方式请求合并到我的仓库中，前两名提交的同学我会帮你们 Code review


**请同学们在开发的时候注意自己的代码可读性和代码风格，祝同学们新年快乐**

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)


[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)

[![forthebadge](Img/powered-by-guo.svg)](https://github.com/gwyxjtu)



# **能源系统Baseline模型**
- 主要内容：一个简化的基础能源系统模型，包括设备约束与能量平衡约束等。

## **0. 约束方程和目标函数目录**

**1. 设备约束**
+ [光伏](#光伏)
+ [电解槽](#电解槽)
+ [燃料电池](#燃料电池)
+ [储氢罐](#储氢罐)
+ [储热罐](#储热罐)
+ [储冷罐](#储冷罐)
+ [热泵](#热泵)
+ [电锅炉](#电锅炉)

**2. 末端状态约束**
+ [储热罐末端状态](#储热罐末端状态)
+ [储冷罐末端状态](#储冷罐末端状态)
+ [储氢罐末端状态](#储氢罐末端状态)

**3. 能量平衡约束**
+ [电力供需平衡约束](#电力供需平衡约束)
+ [热供需平衡约束](#热供需平衡约束)
+ [冷供需平衡约束](#冷供需平衡约束)

**4. 目标函数**
+ [运行成本](#运行成本)
+ [投资成本](#投资成本)
+ [年化投资成本](#年化投资成本)
+ [年化总成本](#年化总成本)

**5. 经济性和碳排放分析**
+ [对比场景的运行成本](#对比场景的运行成本)
+ [年化收益](#年化收益)
+ [静态投资回收期](#静态投资回收期)
+ [相对投资回收期](#相对投资回收期)
+ [系统年碳排计算](#系统年碳排计算)
+ [对比场景年碳排计算](#对比场景年碳排计算)
+ [年碳减排计算](#年碳减排计算)

**6. 负荷分析**


### 1. 设备约束
#### 光伏

$$
p^{pv}_{t} = P^{pv}*p^{pv,fo}_{t},\forall t
$$

其中$p^{pv}_t，p^{pv,fo}_t$分别是光伏$t$时刻光伏发电量和单位光伏发电预测量，$P^{pv}$为光伏总量。

#### 电解槽
电解槽产生的氢气可以描述为：

$$
h^{el}_t=\beta^{el}*p^{el}_t,\forall t  \\
0\le p^{el}_t \le P^{el} ,\forall t
$$

其中$p^{el}_t，h^{el}_t$分别是电解槽$t$时刻用电量，产氢量，$\beta^{el}$为电解槽产氢效率系数，$P^{el}$为任一时刻最大用电量。

#### 燃料电池
在氢氧环境下，燃料电池可同时提供电力与热力需求，本模型下燃料电池运行约束包括产电、产热以及边界约束：

$$
p^{fc}_t={\eta}_p^{fc}*h^{fc}_t,\forall t  \\
g^{fc}_t=\theta^{fc}*{\eta}_g^{fc}*h^{fc}_t, \forall t  \\
0 \le p^{fc}_t \le P^{fc} ,\forall t
$$

其中$p^{fc}_t，g^{fc}_t，h^{fc}_t$分别是燃料电池$t$时刻发电量、产热量、耗氢量，$\eta_p^{fc}$为燃料电池产电效率系数，$\eta_g^{fc}$为燃料电池产热效率系数，$\theta^{fc}$为热回收系数,$P^{fc}$为设备任一时刻的最大发电量。

#### 储氢罐
相邻两时刻的储氢罐储氢量之差与用氢产氢应保持平衡关系。同时，储氢罐的储氢量应维持在最小最大储氢量之间；储氢罐的充放也应满足充放限制：

$$
h^{sto}_{t}-h^{sto}_{t-1}=h^{el}_t+h^{pur}_t-h^{fc}_t,\forall t  \\
h^{sto}_{min}\le h^{sto}_{t}\le h^{sto}_{max},\forall t \\
-H^{trans}_{max}\le h^{sto}_{t}-h^{sto}_{t-1}\le H^{trans}_{max}
$$

其中$h^{sto}_t，h^{pur}_t$分别是储氢罐$t$时刻用电量、购氢量。
$h^{sto}_{min},h^{sto}_{max}$分别为最小最大储氢量。
$H^{trans}_{max}$为最大充放氢限制。

#### 储热罐
储热罐的运行约束包括换热量温度转换关系、储热量限制、以及换热量限制：

$$
g^{hw}_t = c*m^{hw}*(t^{hw}_{t+1}-t^{hw}_{t}),\forall t  \\
t^{hw,min}  \leq t^{hw}_t \leq t^{hw,max} ,\forall t  \\
-G_{max}^{hw}\le g^{hw}_t\le G_{max}^{hw} ,\forall t
$$

其中$t^{hw}_t，g^{hw}_t$分别是储热罐$t$时刻水温，换热量。$c，m^{hw}$分别为热水的比热容与储热罐中换热水的质量。$t^{hw,min}，t^{hw,max}$分别为储热罐的最小最大水温。
$G_{max}^{hw}$为最大换热量。

#### 储冷罐
与储热罐类似，运行约束如下：

$$
q^{cw}_t = c*m^{cw}*(t^{cw}_{t+1}-t^{cw}_{t}),\forall t  \\
t^{cw,min}  \leq t^{cw}_t \leq t^{cw,max} ,\forall t  \\
-Q_{max}^{cw}\le q^{cw}_t\le Q_{max}^{cw} ,\forall t
$$

其中$t^{cw}_t，q^{cw}_t$分别是储冷罐$t$时刻水温，换冷量。$c，m^{cw}$分别为冷水的比热容与储冷罐中换冷水的质量。$t^{cw,min}，t^{cw,max}$分别为储冷罐的最小最大水温。
$Q_{max}^{cw}$为最大换冷量。

#### 热泵
热泵是一种将低品位热能转化为高品位热能的装置。能源转换效率高，功耗低，具有冬热、夏冷双重功能。从能量的角度来看，热泵的输出模型如下：

$$
g_t^{hp}=p_t^{hp}*COP_{hp\_g}*T_{hp},\forall t \\
q_t^{hp}=p_t^{hp}*COP_{hp\_q}*(1-T_{hp}),\forall t \\
0 \le p^{hp}_t \le P^{hp} ,\forall t
$$

其中$g^{hp}_{t}，q^{hp}_{t}，p^{hp}_{t}$分别是热泵$t$时刻产热量，制冷量，用电量。
$COP_{hp\_g}，COP_{hp\_q}$分别是热泵制热和制冷的能效系数，$T_{hp}$为热泵运行状态（0-1变量），$P^{hp}$为热泵最大运行功率。

#### 电锅炉
为了满足部分的热量需求，电锅炉可以通过用电来产生热量。EB产生的热功率与最大热功率限制可用下述等式来描述：

$$
g^{eb}_{t}=\beta^{eb}*p^{eb}_t,\forall t,  \\
0\le p^{eb}_t \le P^{eb} ,\forall t
$$

其中$p^{eb}_t，g^{el}_t$分别是电锅炉$t$时刻用电量、产热量，$\beta^{eb}$为电锅炉效率系数。

### 2. 末端状态约束
#### 储热罐末端状态：
本次考虑末端均为不松弛状态，即需要初末储能状态一致。

$$
t^{hw}_{start}*(1-sl_{hw})\le t^{hw}_{final}\le t^{hw}_{start}*(1+sl_{hw})
$$

其中， $t^{hw}_{start}，t^{hw}_{final}，sl_{hw}$ 分别为起始状态和末端状态储热罐温度，以及末端松弛尺度。

#### 储冷罐末端状态：

$$
t^{cw}_{start}*(1-sl_{cw})\le t^{cw}_{final}\le t^{cw}_{start}*(1+sl_{cw})
$$

其中， $t^{cw}_{start}，t^{cw}_{final}，sl_{cw}$ 分别为起始状态和末端状态储冷罐温度，以及末端松弛尺度。

#### 储氢罐末端状态：

$$
h^{sto}_{start}*(1-sl_{hsto})\le h^{sto}_{final}\le h^{sto}_{start}*(1+sl_{hsto})
$$

其中， $h^{sto}_{start}，h^{sto}_{final}，sl_{hsto}$ 分别为起始状态和末端状态储氢罐温度，以及末端松弛尺度。

### 3. 能量平衡约束
#### 电力供需平衡约束：

$$
p^{fc}_t + p^{pur}_t + p^{pv}_t = p^{el}_t + p^{eb}_t + p^{hp}_t + p^{load}_t,\forall t
$$

其中，$p^{load}_t$ 为 $t$ 时刻负载端用电需求。

#### 热供需平衡约束：

$$
g^{hw}_t + g^{load}_t = g^{fc}_t + g^{hp}_t + g^{eb}_t,\forall t
$$

其中，$g^{load}_t$ 为 $t$ 时刻负载端热需求。

#### 冷供需平衡约束：

$$
q^{cw}_t + q^{hp}_t = q^{load}_t,\forall t
$$

其中，$q^{load}_t$ 为$t$时刻负载端冷需求。

### 4. 目标函数
#### 运行成本
运行成本为运行期间所有时刻买电买氢的成本之和，即
$$
OPEX=\Sigma p^{pur}_t*\lambda^{p}_t+\Sigma h^{pur}_t*\lambda^{h}_t
$$
其中$\lambda^{p}_t$、$\lambda^{h}_t$分别为t时刻的电价和氢价

#### 投资成本
投资成本即为所有规划设备的购置成本之和，本文中设备有光伏、燃料电池、热泵、电锅炉、储热罐、储冷罐、储氢罐、电解槽。
$$
E_{cost}=c^{fc}*P^{fc}+c^{hp}*P^{hp}+c^{pv}*P^{pv}+c^{el}*P^{el}+c^{eb}*P^{eb}+c^{hw}*P^{hw}+c^{cw}*P^{cw}+c^{sto}*P^{sto}
$$
其中c为各设备的单位投资成本，P为规划容量
#### 年化投资成本
年化投资成本即为所有规划设备的年化投资成本之和
$$
CAPEX_{year}=c^{fc}*P^{fc}*CRF^{fc}+c^{hp}*P^{hp}*CRF^{hp}+c^{pv}*P^{pv}*CRF^{pv}+c^{el}*P^{el}*CRF^{el}+c^{eb}*P^{eb}*CRF^{eb}+c^{hw}*P^{hw}*CRF^{hw}+c^{cw}*P^{cw}*CRF^{cw}+c^{sto}*P^{sto}*CRF^{sto}
$$
其中c为各设备的单位投资成本，P为规划容量，CRF为设备年化收益率。各设备的年化收益率用下式计算
$$
CRF=((1+i)^{L}*i)/((1+i)^{L}-1)
$$
其中i为收益率，L为设备寿命
#### 年化总成本
年化总成本为年化投资成本+运行成本，本次作业按照年化总成本作为目标函数


$$
CAPEX_{sum}=CAPEX_{year}+OPEX\\
min\quad obj=CAPEX_{sum}
$$

### 5. 经济性和碳排放分析
#### 对比场景的运行成本
以电制冷、电制热、电网买电作为对比场景，则运行成本为
$$
OPEX^{contrast}=\Sigma p^{load}_t*\lambda^{p}_{t}+\Sigma g^{load}_t*\lambda^{p}_{t}/\eta^g+\Sigma q^{load}_t*\lambda^{p}_{t}/\eta^q
$$
其中$\eta^{g}$、$\eta^{q}$分别为电制热效率和电制冷效率

请思考：若对比场景采用集中供热，对比场景的运行成本应当如何计算

#### 年化收益

总收益，代表供冷、供热、供电和其他收益之和
$$
revenue=\Sigma p^{out}_t*\lambda^{p_{out}}_{t}+s^{g}*\lambda^{g}+s^{q}*\lambda^{q}
$$
其中$\lambda^{p_{out}}_t$、$\lambda^{g}$、$\lambda^{q}$分别为t时刻的卖电电价、单位面积供热价格、单位面积供冷价格

#### 静态投资回收期

投资回收期是指该规划结果下多少年可以回本，计算公式为投资成本除以净收益
$$
Y_{receive}=E_{cost}/(revenue-OPEX)
$$
请思考：什么情况下适合使用静态投资回收期

#### 相对投资回收期

相对投资回收期是指该规划结果中新增的投资多少年可以回本，计算公式为增加的投资成本除以减少的运行成本
$$
Y_{receive}=E_{cost}/(OPEX^{contrast}-OPEX)
$$
请思考：什么情况下适合使用相对投资回收期

#### 系统年碳排计算

碳排放为运行期间所有时刻买电的碳排之和，即
$$
c^{system}=\Sigma p^{pur}_t*c^{p}
$$
其中$c^{p}$为买电的碳排放因子

#### 对比场景年碳排计算

碳排放为运行期间所有时刻买电、买热、电制冷的碳排之和，即
$$
c^{contrast}=\Sigma p^{load}_t*c^{p}+\Sigma g^{load}_t*c^{g}+\Sigma q^{load}_t*c^{p}/\eta^q
$$
其中$c^{p}$、$c^{g}$分别为买电和买热的碳排放因子，$\eta^{q}$为电制冷系数

（请思考，若对比场景热为空调制热，碳排放应如何计算）

#### 年碳减排计算

碳排放为运行期间所有时刻买电的碳排之和，即
$$
c^{reduce}=c^{contrast}-c^{system}
$$

### 6. 负荷分析

请完成：在基础负荷上，叠加一个每日8：00-18:00的恒定电负荷（50kW）,并重新计算规划结果并进行指标计算，描述规划结果发生了哪些变化，为什么会发生这些变化

请完成：在基础负荷上，叠加一个每日8：00-18:00的恒定冷负荷（50kW）,并重新计算规划结果并进行指标计算，描述规划结果发生了哪些变化，为什么会发生这些变化
