"""数据库种子数据与初始化。"""

from sqlalchemy.orm import Session

from app.config import LEVELS, LEVEL_LABELS, SOFTWARE_INFO
from app.models import LevelStat, Scheme, SoftwareInfo

# 默认方案 Markdown 模板
DEFAULT_SCHEMES: dict[str, dict[str, str]] = {
    "L1": {
        "title": "萌新萝莉 · 轻度美颜",
        "markdown": """# L1 萌新萝莉 · 轻度美颜

> 今天的兄弟还会是兄弟吗？嘿嘿~ 最入门级变身，兄弟看了只会微微一笑。

## 效果描述
- 男生变可爱萝莉的轻度女性化，必须保留参考图人物完整面部特征（五官可辨认，禁止换脸）
- 萌新萝莉风：淡粉腮红、水润唇色、软萌眼神，皮肤细腻透亮
- 发型略变柔顺，可带小发卡或软萌刘海，整体气质偏天真可爱
- 粉色系柔和背景，真人可爱女生写真，kawaii 萝莉感但仍是真实人像

## 操作步骤
1. 上传兄弟高清正面照
2. 选择 **L1 萌新萝莉**
3. 点击「一键变身」
4. 笑到肚子疼再下载

## 扩图说明
画布轻微扩展 10%，添加粉色渐变背景。

## 注意事项
⚠️ 此等级适合初次整蛊，杀伤力最低，适合试探兄弟反应。
""",
        "prompt_template": "Male to female cute loli L1, kawaii soft pink, preserve face, light blush, adorable girl portrait",
    },
    "L2": {
        "title": "可爱加倍 · 双马尾觉醒",
        "markdown": """# L2 可爱加倍 · 双马尾觉醒

## 效果描述（必填项）
- 男生变可爱萝莉的中度女性化，面部必须与参考图完全一致，一眼可认出
- 经典萝莉元素：双马尾或公主切，蝴蝶结/发箍发饰，星星感眼妆与长睫毛
- 穿着粉色/白色可爱萝莉日常裙或卫衣，粉紫梦幻色调
- 表情软萌带笑，整体 kawaii 萝莉少女风，真人写真质感

## 操作步骤
1. 选一张兄弟最「男子气概」的照片（效果最佳）
2. 选择 L2 等级
3. 一键变身，截图发群

## 扩图说明
扩展 20% 画布，添加蝴蝶结装饰边框。

## 注意事项
⚠️ 兄弟可能会要求你请吃饭，请提前备好钱包。
""",
        "prompt_template": "Male to female cute loli L2, twin tails, bow hair accessories, kawaii pink dress, preserve face",
    },
    "L3": {
        "title": "萌系觉醒 · 洛丽塔初现",
        "markdown": """# L3 萌系觉醒 · 洛丽塔初现

## 效果描述
- 男生变萝莉的明显女性化，保留参考图面部身份（骨相眉眼鼻唇不改，禁止换脸）
- 日系萌系萝莉：洛丽塔短裙或 JK 制服，蕾丝花边、过膝袜、可爱包包
- 樱花/糖果色背景，卧蚕妆、玻璃唇，幼态可爱萝莉气质
- 8K 真人萝莉写真，软萌治愈系，等级 L3 萌系萝莉

## 适用场景
- 开黑前的「热身」整蛊
- 生日惊喜（惊吓）

## 扩图说明
扩展 30%，添加樱花飘落动效背景。
""",
        "prompt_template": "Male to female moe loli L3, lolita dress JK uniform, lace socks, cherry blossom, preserve face",
    },
    "L4": {
        "title": "魅力全开 · 萝莉公主",
        "markdown": """# L4 魅力全开 · 萝莉公主

## 效果描述（必填项）
- 男生变萝莉的深度女性化，面部100%继承参考图（禁止换脸）
- 精致萝莉公主风：层叠蕾丝洛丽塔洋装、大蝴蝶结、珍珠发饰、公主皇冠元素
- 粉金柔光、花瓣或星星点缀，眼神灵动可爱，整体华丽萌萝莉
- 超精美真人萝莉人像，可爱全开，既有萝莉感又保留本人五官

## 操作步骤
1. 选择兄弟最帅的照片（反差更大）
2. L4 一键变身
3. 设为他所有社交账号头像（不建议）

## 扩图说明
扩展 40%，添加光晕与粒子特效。
""",
        "prompt_template": "Male to female loli princess L4, frilly lolita dress, crown bow, pink gold light, preserve face",
    },
    "L5": {
        "title": "终极变身 · 萝莉女王降临",
        "markdown": """# L5 终极变身 · 萝莉女王降临

> 今天的兄弟还会是兄弟吗？嘿嘿~ **绝对不会了！**

## 效果描述
- 男生变萝莉的终极女性化，必须保留参考图面部身份（禁止换脸）
- 萝莉女王降临：华丽洛丽塔礼裙、皇冠、翅膀或魔法棒道具，全套萝莉女王造型
- 梦幻粉紫全屏场景，最大级别可爱萝莉特效，软萌又华丽
- 终极 photorealistic 萝莉女王全身大片，可爱萝莉风格拉满

## 操作步骤
1. 深吸一口气
2. 上传照片
3. 选择 L5
4. 点击变身
5. 做好被追杀的准备

## 扩图说明
扩展 50%，全屏梦幻场景，皇冠与翅膀装饰。

## 注意事项
⚠️⚠️⚠️ 此等级杀伤力极大，仅限铁哥们使用。友谊的小船说翻就翻。
""",
        "prompt_template": "Male to female ultimate loli queen L5, elaborate lolita gown, crown wings, fantasy pink, preserve face",
    },
}


def seedDatabase(db: Session) -> None:
    """初始化数据库种子数据。"""
    # 软件信息
    if not db.query(SoftwareInfo).first():
        db.add(
            SoftwareInfo(
                name=SOFTWARE_INFO["name"],
                slogan=SOFTWARE_INFO["slogan"],
                version=SOFTWARE_INFO["version"],
                description=SOFTWARE_INFO["description"],
            )
        )

    # 方案
    for level in LEVELS:
        existing = db.query(Scheme).filter(Scheme.level == level).first()
        if not existing:
            default = DEFAULT_SCHEMES[level]
            db.add(
                Scheme(
                    level=level,
                    title=default["title"],
                    markdown=default["markdown"],
                    prompt_template=default["prompt_template"],
                )
            )

    # 统计
    for level in LEVELS:
        if not db.query(LevelStat).filter(LevelStat.level == level).first():
            db.add(LevelStat(level=level, select_count=0, generate_count=0))

    db.commit()
