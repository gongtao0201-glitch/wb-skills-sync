import pandas as pd

# 读取5月数据
excel_path = 'C:/Users/Administrator/Desktop/workbuddy/原始基础数据/销售主题分析_商品5月.xlsx'
df = pd.read_excel(excel_path)
df = df.dropna(subset=['商品名称'])
df['毛利率数值'] = df['销售毛利率'].str.replace('%', '').astype(float)
df_clean = df[(df['成本价'] > 0) & (df['销售金额'] > 100) & (df['毛利率数值'] > -100) & (df['毛利率数值'] <= 100)].copy()

def classify(name):
    name = str(name)
    
    # === 饵料类 ===
    if '拉小米' in name:
        return '饵料'
    if '原浆' in name:
        return '饵料'
    if '破碎料' in name:
        return '饵料'
    if '方块饵' in name:
        return '饵料'
    if '血麦' in name:
        return '饵料'
    if '空钩饵' in name:
        return '饵料'
    if '空钩粘米' in name:
        return '饵料'
    if '空钩粘粉' in name:
        return '饵料'
    if '饵料' in name and '爆炸' not in name:
        return '饵料'
    if '鱼饵' in name:
        return '饵料'
    if '易杯饵' in name:
        return '饵料'
    if '雾化饵' in name:
        return '饵料'
    if '杯饵' in name:
        return '饵料'
    # 新增饵料
    if '完爆黑坑' in name:
        return '饵料'
    if '野鲫风暴' in name:
        return '饵料'
    if '狂野爆鲫' in name:
        return '饵料'
    if '野鲫' in name and '腥' in name:
        return '饵料'
    if '野鲫' in name and '香' in name:
        return '饵料'
    if '共同富鱼' in name:
        return '饵料'
    if '狂钓鲫' in name:
        return '饵料'
    if '罗非' in name:
        return '饵料'
    if '牛鲤三合一' in name:
        return '饵料'
    if '牛B千里鲫' in name:
        return '饵料'
    if '甜薯粒' in name:
        return '饵料'
    if '蛋黄' in name:
        return '饵料'
    if '重口味' in name:
        return '饵料'
    if '狂鲤' in name:
        return '饵料'
    
    # === 窝料类 ===
    if '维它米' in name:
        return '窝料'
    if '谷麦' in name:
        return '窝料'
    if '杂粮' in name and '握团' not in name:
        return '窝料'
    if '牛窝' in name:
        return '窝料'
    if '神窝' in name:
        return '窝料'
    if '酒米' in name:
        return '窝料'
    if '麝香米' in name:
        return '窝料'
    if '打窝' in name:
        return '窝料'
    if '玉米' in name:
        return '窝料'
    if '黄颡鱼' in name:
        return '窝料'
    if '颗粒' in name and '方块饵' not in name:
        return '窝料'
    if '爆炸饵' in name:
        return '窝料'
    if '窝' in name and '牛窝' not in name and '神窝' not in name:
        return '窝料'
    if '米团' in name:
        return '窝料'
    if '速散' in name:
        return '窝料'
    if '本草' in name and '本草纲目' not in name:
        return '窝料'
    if '果酸嫩玉米' in name or '蜂蜜嫩玉米' in name:
        return '窝料'
    # 新增窝料
    if '打浮' in name:
        return '窝料'
    if '草霸' in name:
        return '窝料'
    if '巨物' in name:
        return '窝料'
    if '狂米' in name:
        return '窝料'
    if '色诱米' in name:
        return '窝料'
    if '加强中草' in name and '米' in name:
        return '窝料'
    if '麝香麦粒' in name:
        return '窝料'
    if '升级版' in name and '米' in name:
        return '窝料'
    if '老坛甜薯 麦粒' in name:
        return '窝料'
    if '一桶天下' in name:
        return '窝料'
    if '西部风 握团杂粮' in name:
        return '窝料'
    if '五谷酿' in name:
        return '窝料'
    if '维它药米' in name:
        return '窝料'
    if '中草发酵米麦' in name:
        return '窝料'
    if '神鲫米' in name:
        return '窝料'
    
    # === 小药/添加剂类 ===
    if '拉丝粉' in name:
        return '小药/添加剂'
    if '粘粉' in name and '空钩粘粉' not in name:
        return '小药/添加剂'
    if '小药' in name:
        return '小药/添加剂'
    if '粉' in name and ('鲫粉' in name or '鲤粉' in name or '虾粉' in name or '蒜粉' in name):
        return '小药/添加剂'
    if '液' in name and ('红虫液' in name or '果酸' in name):
        return '小药/添加剂'
    if '诱' in name and ('狂诱' in name or '开口' in name):
        return '小药/添加剂'
    if '开口剂' in name:
        return '小药/添加剂'
    if '麝香王' in name or '麝香酒' in name:
        return '小药/添加剂'
    if '一滴' in name:
        return '小药/添加剂'
    if '全能辅助' in name:
        return '小药/添加剂'
    if '中药酒' in name or '药酒' in name:
        return '小药/添加剂'
    if '浓缩液' in name:
        return '小药/添加剂'
    if '喷剂' in name:
        return '小药/添加剂'
    if '中农味觉' in name:
        return '小药/添加剂'
    if '阿魏' in name:
        return '小药/添加剂'
    if '牛B' in name and ('粉' in name or '水' in name):
        return '小药/添加剂'
    if 'VB' in name:
        return '小药/添加剂'
    if '麝香味' in name or '红虫味' in name or '甜薯味' in name:
        return '小药/添加剂'
    if '果酸' in name and '嫩玉米' not in name and '杂粮' not in name and '维它米' not in name:
        return '小药/添加剂'
    if '千里香' in name:
        return '小药/添加剂'
    if '蛋奶' in name and '空钩' not in name:
        return '小药/添加剂'
    if '南极虾粉' in name:
        return '小药/添加剂'
    # 新增添加剂
    if '老坛粉' in name:
        return '小药/添加剂'
    if '甜薯粉' in name:
        return '小药/添加剂'
    if '肽甜香' in name:
        return '小药/添加剂'
    if '麝香麦粒红' in name and '100ml' in name:
        return '小药/添加剂'
    if '泡米曲酒' in name:
        return '小药/添加剂'
    if '鲫鱼老酒' in name or '鲤鱼老酒' in name:
        return '小药/添加剂'
    if '酒源' in name:
        return '小药/添加剂'
    if '红虫粉' in name:
        return '小药/添加剂'
    if '快拉' in name:
        return '小药/添加剂'
    if '鱼蟲宴' in name and '方块饵' not in name:
        return '小药/添加剂'
    if '牛B鲤' in name and ('粉' not in name and '水' not in name):
        if '350g' in name or '300g' in name:
            return '窝料'
        return '小药/添加剂'
    
    # === 配件/其他 ===
    if any(k in name for k in ['打窝杆', '毛巾', '水桶', '失手绳', '拉链袋', '袋装']):
        return '配件/其他'
    if '钓得多' in name:
        return '小药/添加剂'
    
    # === 配件/其他 ===
    if '通用拉链白袋' in name:
        return '配件/其他'
    
    return '未分类'

df_clean['产品分类'] = df_clean['商品名称'].apply(classify)
df_clean['产品属性'] = df_clean['商品名称'].apply(lambda x: '自有' if '自有' in str(x) else '通货')

# 总览
total_sales = df_clean['销售金额'].sum()
print('=== 5月销售总览（最终分类）===')
print(f'总销售额: ¥{total_sales:,.2f} ({total_sales/10000:.1f}万)')
print(f'商品种类数: {len(df_clean)}')
print()

# 分类占比
cat_sales = df_clean.groupby('产品分类')['销售金额'].sum().sort_values(ascending=False)
print('=== 产品分类占比 ===')
for cat, sales in cat_sales.items():
    print(f'{cat}: ¥{sales:,.2f} ({sales/total_sales*100:.1f}%)')
print()

# 前10名
top10 = df_clean.nlargest(10, '销售金额')[['商品名称', '销售金额', '毛利率数值', '产品分类', '产品属性']]
print('=== 5月前10名（最终分类）===')
for idx, row in top10.iterrows():
    name = str(row['商品名称'])[:30]
    print(f"{name:<33} | ¥{row['销售金额']:>10,.0f} | 毛利{row['毛利率数值']:>5.1f}% | {row['产品分类']} | {row['产品属性']}")
print()

# 未分类的
unclassified = df_clean[df_clean['产品分类'] == '未分类']
print(f'=== 未分类商品（{len(unclassified)}个）===')
for idx, row in unclassified.iterrows():
    print(f"{str(row['商品名称'])[:40]:<45} | ¥{row['销售金额']:>10,.0f}")
