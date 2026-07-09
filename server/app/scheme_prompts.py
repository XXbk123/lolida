"""各等级可爱萝莉风格「效果描述」模板。"""

import re

# 男生变萝莉：保留原脸 + 可爱萝莉风 + 真人质感
LOLI_EFFECT_SECTIONS: dict[str, str] = {
    "L1": """## 效果描述
- 男生变可爱萝莉的轻度女性化，必须保留参考图人物完整面部特征（五官可辨认，禁止换脸）
- 萌新萝莉风：淡粉腮红、水润唇色、软萌眼神，皮肤细腻透亮
- 发型略变柔顺，可带小发卡或软萌刘海，整体气质偏天真可爱
- 粉色系柔和背景，真人可爱女生写真，kawaii 萝莉感但仍是真实人像""",
    "L2": """## 效果描述（必填项）
- 男生变可爱萝莉的中度女性化，面部必须与参考图完全一致，一眼可认出
- 经典萝莉元素：双马尾或公主切，蝴蝶结/发箍发饰，星星感眼妆与长睫毛
- 穿着粉色/白色可爱萝莉日常裙或卫衣，粉紫梦幻色调
- 表情软萌带笑，整体 kawaii 萝莉少女风，真人写真质感""",
    "L3": """## 效果描述
- 男生变萝莉的明显女性化，保留参考图面部身份（骨相眉眼鼻唇不改，禁止换脸）
- 日系萌系萝莉：洛丽塔短裙或 JK 制服，蕾丝花边、过膝袜、可爱包包
- 樱花/糖果色背景，卧蚕妆、玻璃唇，幼态可爱萝莉气质
- 8K 真人萝莉写真，软萌治愈系，等级 L3 萌系萝莉""",
    "L4": """## 效果描述（必填项）
- 男生变萝莉的深度女性化，面部100%继承参考图（禁止换脸）
- 精致萝莉公主风：层叠蕾丝洛丽塔洋装、大蝴蝶结、珍珠发饰、公主皇冠元素
- 粉金柔光、花瓣或星星点缀，眼神灵动可爱，整体华丽萌萝莉
- 超精美真人萝莉人像，可爱全开，既有萝莉感又保留本人五官""",
    "L5": """## 效果描述
- 男生变萝莉的终极女性化，必须保留参考图面部身份（禁止换脸）
- 萝莉女王降临：华丽洛丽塔礼裙、皇冠、翅膀或魔法棒道具，全套萝莉女王造型
- 梦幻粉紫全屏场景，最大级别可爱萝莉特效，软萌又华丽
- 终极 photorealistic 萝莉女王全身大片，可爱萝莉风格拉满""",
}

# 兼容旧引用
REALISTIC_EFFECT_SECTIONS = LOLI_EFFECT_SECTIONS


def replaceEffectSection(markdown: str, level: str) -> str:
    """替换方案 Markdown 中的「效果描述」段落，保留其余章节不变。"""
    newSection = LOLI_EFFECT_SECTIONS.get(level)
    if not newSection:
        return markdown

    markdown = re.sub(
        r"\n## 效果描述（列表项）\s*\n.*?(?=\n## |\Z)",
        "\n",
        markdown,
        count=1,
        flags=re.DOTALL,
    )

    pattern = re.compile(
        r"## 效果描述(?:（必填项）)?\s*\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    if pattern.search(markdown):
        return pattern.sub(newSection + "\n", markdown, count=1)

    return newSection + "\n\n" + markdown.lstrip()


def upgradeSchemePrompts(db) -> None:
    """将数据库中 L1-L5 方案的效果描述升级为可爱萝莉风格。"""
    from app.models import Scheme

    for level, _section in LOLI_EFFECT_SECTIONS.items():
        scheme = db.query(Scheme).filter(Scheme.level == level).first()
        if not scheme:
            continue
        scheme.markdown = replaceEffectSection(scheme.markdown, level)
    db.commit()
