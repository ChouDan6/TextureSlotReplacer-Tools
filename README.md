# TextureSlotReplacer-Tools
TSR作者: 
https://gamebanana.com/members/2987570  
https://gamebanana.com/blogs/21076  
TSR-ORFix-converter.pyw作者: me & Gemini 3 pro  

Resource\TSR\Diffuse = ref ResourceDiffuse  
Resource\TSR\Lightmap = ref ResourceLightmap  
Resource\TSR\Normalmap = ref ResourceNormalmap  
Resource\TSR\NataFXMap = ref ResourceNataFXMap  
Resource\TSR\NataFXOutline = ref ResourceNataFXOutline  
Run = CommandList\TSR\SetTextures  

`TextureSlotReplacer.ini` (TSR) 和 `ORFix.ini` 的目标完全一致（解决轮廓、倒影、透明度等贴图错乱问题），但它们的**实现逻辑有着根本性的区别**。

打个比方：

  * **ORFix** 像是\*\*“交通警察”\*\*。它拿着一张写满车牌号（Shader Hash）的清单，看到特定的车牌（着色器），就指挥它：“你去停在 1 号位，你去停在 2 号位”。如果游戏更新，车牌号变了，警察就瞎了。
  * **TSR** 像是\*\*“基因改造医生”\*\*。它不看车牌号，而是直接把司机的大脑（Shader 代码）切开做手术，植入一段新逻辑：“如果你口袋里有我给你的特殊钥匙（Mod 贴图），你就开新车；如果没有，你就开旧车。”

下面是 TSR 具体的工作原理详细解析：

### 1\. 核心机制：代码注入 (Shader Code Injection)

与 ORFix 依赖 `[ShaderOverride]` 匹配哈希值不同，TSR 使用了 3dmigoto 的高级功能 **`[ShaderRegex]`**。

它利用正则表达式（Regex）扫描当前正在运行的着色器（Shader）代码，找到读取贴图的那一行指令，然后**当场重写这行代码**。

### 2\. 具体步骤解析

#### 第一步：建立“安全区” (Staging)

在文件的开头，你可以看到：

```ini
[CommandListSetTextures]
ps-t100 = ref ResourceDiffuse
ps-t101 = ref ResourceLightmap
ps-t102 = ref ResourceNormalmap
...
```

TSR 不去动游戏原本的 `t0`, `t1` 等低号槽位（这些槽位经常变来变去）。相反，它把 Mod 的贴图强行塞到了**非常靠后的槽位**（`t100` 到 `t104`）。这些是游戏平时不用的“安全区”。

#### 第二步：扫描代码 (Pattern Matching)

以 `[ShaderRegexMain]` 为例，它定义了一段复杂的正则表达式：

```ini
[ShaderRegexMain.Pattern]
(?<texture1>sample\w+\(\w+\)... t\d ...)
```

这段正则的意思是：**“寻找当前 Shader 代码中，所有‘读取纹理 (sample texture)’并且指向 `t0`, `t1` 等原始槽位的指令。”**

#### 第三步：逻辑手术 (Dynamic Replacement)

一旦找到这行代码，TSR 就会用 `Pattern.Replace` 里的内容替换它。它插入了一段 `if/else` 的逻辑。

**原始 Shader 代码可能是这样的：**

```hlsl
// 这里的 t0 是游戏原本想读的槽位
颜色 = 读取纹理(t0);
```

**被 TSR 修改后的 Shader 代码变成了这样：**

```hlsl
// TSR 插入的检查逻辑
检查 t100 (Mod的漫反射贴图) 是否存在且有效;
if (t100 有效) {
    颜色 = 读取纹理(t100); // 强行读取 Mod 的贴图
} else {
    颜色 = 读取纹理(t0);   // 如果没有 Mod，保持原样
}
```

请看配置文件中的这一段替换逻辑：

```ini
if_nz ${useTex}.x\n             ; 如果 t100 (useTex.x) 不为空
    ${texture1head}t100${texture1tail} ; 使用 t100 替换原来的 tX
else\n
    ${texture1}                 ; 否则使用原来的代码
endif\n
```

### 3\. 各个模块的作用

TSR 针对不同的渲染场景写了不同的正则替换逻辑：

  * **`[ShaderRegexMain]`**：

      * 处理最基础的角色渲染。它会尝试把游戏的贴图读取指令替换为读取 `t100` (漫反射) 或 `t101` (光影)。
      * 这就解决了**倒影问题**：即使倒影 Shader 原本想从 `t0` 读颜色，TSR 也会强行让它去检查 `t100`，从而读到正确的 Mod 贴图。

  * **`[ShaderRegexOutline]`**：

      * 处理轮廓线。轮廓线 Shader 通常结构比较特殊，它专门匹配轮廓线的代码模式，把读取颜色的指令指向 `t100` 或 `t101`。这解决了**轮廓断裂/变色**问题。

  * **`[ShaderRegexNormal]`**：

      * 专门处理法线贴图。如果检测到 Mod 提供了法线（存放在 `t102`），它就强行让 Shader 读取 `t102`。

  * **`[ShaderRegexNataFX]`**：

      * **纳塔版本特供**。纳塔角色的“夜魂”特效和纹身使用了非常特殊的渲染逻辑。TSR 在这里不仅替换基础贴图，还增加了 `t103` (轮廓光) 和 `t104` (纹身) 的注入逻辑，防止纳塔角色的特效在打 Mod 后消失。

### 4\. 相比 ORFix 的优缺点

**TSR 的优点（更先进）：**

  * **抗更新能力强**：游戏更新通常会改变 Shader 的哈希值（Hash），导致 ORFix 失效需要重新抓取。但 Shader 的**代码写法**通常不会大变。只要代码结构相似，TSR 的正则就能匹配上，不用频繁更新。
  * **通用性强**：它不需要为每个角色的每个特殊 Shader（如雷电将军的刀、公子的水刀）单独记录哈希，只要符合“读取纹理”的代码结构，统统能修。

**TSR 的缺点：**

  * **性能开销稍大**：它在 GPU 层面增加了很多 `if/else` 判断（尽管开销极小，但在极端低配机上理论上比 ORFix 重一点点）。
  * **更难调试**：如果正则写错了，或者米哈游突然彻底重写了 Shader 的代码结构，整个修复就会瞬间全部失效，而且很难定位是哪里匹配失败了。

### 总结

**ORFix** 是\*\*“手动档”**，靠的是庞大的数据库（Hash 表）来一一对应修复。
TextureSlotReplacer 是**“自动档”\*\*，它通过实时修改游戏渲染代码，让 Shader 自动优先读取 Mod 放在“安全区（t100+）”里的贴图。

这就解释了为什么你在用 TSR 时，不需要像 ORFix 那样担心“这个角色的 Hash 有没有被收录”，通常装上就能用。



