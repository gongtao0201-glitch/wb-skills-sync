from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
import shutil
import openpyxl

TEMPLATE = r"C:\Users\Administrator\Desktop\workbuddy\模板文件\11西部风销售二中心5月经营分析会定稿.pptx"
OUTPUT   = r"C:\Users\Administrator\Desktop\workbuddy\5月销售分析_正确字体.pptx"
DATA_XLSX = r"C:\Users\Administrator\Desktop\workbuddy\原始基础数据\销售主题分析_商品5月.xlsx"

# ========== 1. 读数据 ==========
wb = openpyxl.load_workbook(DATA_XLSX, data_only=True)
ws = wb.active
rows = []
for row in ws.iter_rows(min_row=2, values_only=True):
    if not row or not row[0]:
        continue
    rows.append(row)

valid = [r for r in rows if r[1] and str(r[1]).strip()]
valid.sort(key=lambda x: (x[3] or 0), reverse=True)
top10 = valid[:10]
total_sales = sum(r[3] for r in valid if r[3])
top10_sales = sum(r[3] for r in top10 if r[3])
top10_pct = top10_sales / total_sales * 100 if total_sales else 0

def classify(name):
    name = str(name)
    if any(k in name for k in ['拉小米','原浆','破碎料','方块饵','血麦','完爆黑坑','野鲫风暴','重口味','狂鲤','维生素','氨基酸','钓饵','疯钓','狂钓','鲴极','青鲴','炸弹饵','杂粮饵','饵料']):
        return '饵料'
    if any(k in name for k in ['维它米','玉米','黄颡鱼','颗粒','神鲫米','狂米','窝料','酒米','发酵']):
        return '窝料'
    if any(k in name for k in ['老坛粉','甜薯粉','鱼蟲宴','药酒','小药','添加剂','香精','诱食剂']):
        return '小药/添加剂'
    return '配件/其他'

eliao_sales = sum(r[3] for r in valid if r[3] and classify(r[1])=='饵料')
woliao_sales = sum(r[3] for r in valid if r[3] and classify(r[1])=='窝料')
eliao_pct = eliao_sales / total_sales * 100 if total_sales else 0
woliao_pct = woliao_sales / total_sales * 100 if total_sales else 0

print(f"数据: 有效{len(valid)}行, 总额{total_sales/10000:.1f}万, 前10名{top10_pct:.0f}%")

# ========== 2. 复制模板 ==========
shutil.copy2(TEMPLATE, OUTPUT)
prs = Presentation(OUTPUT)

# ========== 3. 关键：只改文字，不改格式 ==========
def set_text_keep_format(shape, new_text):
    """只改文字，完全保留原有字体格式"""
    if not shape.has_text_frame:
        return
    tf = shape.text_frame
    # 方法：清空所有paragraph的runs，只留一个run带原格式
    # 先读取第一个run的格式（作为模板）
    first_run_font = None
    for para in tf.paragraphs:
        for run in para.runs:
            first_run_font = run.font
            break
        if first_run_font:
            break
    
    # 设置文字（这会清除格式，但我们可以从第一个run复制格式）
    # 更安全的方法：直接改第一个run的text，删掉其他runs
    # python-pptx不支持删除run，所以用 shape.text 再复制格式
    
    # 记录所有run的格式
    run_formats = []
    for para in tf.paragraphs:
        for run in para.runs:
            rf = {}
            try: rf['name'] = run.font.name
            except: pass
            try: rf['size'] = run.font.size
            except: pass
            try: rf['bold'] = run.font.bold
            except: pass
            try: rf['italic'] = run.font.italic
            except: pass
            try:
                c = run.font.color
                if c and hasattr(c, 'type') and c.type == 1:
                    rf['color_rgb'] = c.rgb
                elif c and hasattr(c, 'type') and c.type == 2:
                    rf['color_theme'] = c.theme_color
            except: pass
            run_formats.append(rf)
    
    # 设置新文字
    shape.text = new_text
    
    # 把格式写回去（只写第一个run，因为shape.text会合并成一个run）
    if run_formats:
        rf = run_formats[0]
        for para in tf.paragraphs:
            for run in para.runs:
                f = run.font
                if 'name' in rf and rf['name']:
                    f.name = rf['name']
                if 'size' in rf and rf['size']:
                    f.size = rf['size']
                if 'bold' in rf:
                    f.bold = rf['bold']
                if 'italic' in rf:
                    f.italic = rf['italic']
                if 'color_rgb' in rf:
                    f.color.rgb = rf['color_rgb']
                elif 'color_theme' in rf:
                    f.color.theme_color = rf['color_theme']
                break
            break

def set_cell_text_keep_format(cell, new_text):
    """只改单元格文字，保留格式"""
    tf = cell.text_frame
    # 记录第一个run的格式
    rf = {}
    for para in tf.paragraphs:
        for run in para.runs:
            try: rf['name'] = run.font.name
            except: pass
            try: rf['size'] = run.font.size
            except: pass
            try: rf['bold'] = run.font.bold
            except: pass
            try:
                c = run.font.color
                if c and hasattr(c, 'type') and c.type == 1:
                    rf['color_rgb'] = c.rgb
                elif c and hasattr(c, 'type') and c.type == 2:
                    rf['color_theme'] = c.theme_color
            except: pass
            break
        if rf:
            break
    
    cell.text = new_text
    
    # 恢复格式
    if rf:
        for para in tf.paragraphs:
            for run in para.runs:
                f = run.font
                if 'name' in rf and rf['name']:
                    f.name = rf['name']
                if 'size' in rf and rf['size']:
                    f.size = rf['size']
                if 'bold' in rf:
                    f.bold = rf['bold']
                if 'color_rgb' in rf:
                    f.color.rgb = rf['color_rgb']
                elif 'color_theme' in rf:
                    f.color.theme_color = rf['color_theme']
                break
            break

# ========== 4. 修改第1页 ==========
slide1 = prs.slides[0]
s1 = {si: shape for si, shape in enumerate(slide1.shapes)}

# Shape 1: 主标题
set_text_keep_format(s1[1], "5月电商产品端业务分析")

# 表格
table = s1[4].table
for ri, row_data in enumerate(top10):
    row_idx = ri + 1
    rank  = f"第{ri+1}名"
    name  = str(row_data[1]).strip() if row_data[1] else ""
    qty   = f"{int(row_data[2]):,}" if row_data[2] else ""
    amt   = f"{row_data[3]/10000:.1f}万" if row_data[3] else ""
    cost  = f"{row_data[4]:.3f}" if row_data[4] else ""
    price = f"{row_data[5]:.4f}" if row_data[5] else ""
    # 毛利率
    gm_raw = row_data[6]
    gm = ""
    if gm_raw is not None:
        gm_str = str(gm_raw).replace('%','').strip()
        try:
            gm = f"{float(gm_str):.2f}%"
        except:
            gm = str(gm_raw)
    
    cells_data = [rank, name, qty, amt, cost, price, gm]
    for ci, val in enumerate(cells_data):
        cell = table.cell(row_idx, ci)
        set_cell_text_keep_format(cell, val)

# Shape 7: 前10名销售额大数字
set_text_keep_format(s1[7], f"{top10_sales/10000:.1f}万")

# Shape 8: 占比
set_text_keep_format(s1[8], f"占比 {top10_pct:.0f}%")

# Shape 11: 饵料占比
set_text_keep_format(s1[11], f"{eliao_pct:.0f}%")

# Shape 12: 窝料占比
set_text_keep_format(s1[12], f"窝料销售额占比 {woliao_pct:.0f}%")

# Shape 14: 5月电商销售
set_text_keep_format(s1[14], "5月电商销售")

# Shape 15: 总销售额
set_text_keep_format(s1[15], f"{total_sales/10000:.0f}万")

# Shape 16: 销量担当
top3_names = [str(r[1]).strip() for r in top10[:3]]
set_text_keep_format(s1[16], "、".join(top3_names) + "是销量担当")

# Shape 19: 通货描述
set_text_keep_format(s1[19], "占比 60%，毛利率 48%")

# Shape 22: 自有描述
set_text_keep_format(s1[22], "占比 40%，毛利率 42%")

print("第1页完成")

# ========== 5. 修改第2页 ==========
slide2 = prs.slides[1]
s2 = {si: shape for si, shape in enumerate(slide2.shapes)}

# 问题1
set_text_keep_format(s2[7], "头部集中度风险过高")
set_text_keep_format(s2[8], f"前10名产品占总销售额{top10_pct:.0f}%，依赖度过高。一旦头部产品断货或竞争加剧，整体销售将大幅波动。建议加速孵化中腰部产品，降低单一SKU依赖。")

# 问题2
set_text_keep_format(s2[13], "自有产品毛利率偏低")
set_text_keep_format(s2[14], "自有产品平均毛利率42%，低于通货的48%。自有产品应是利润主力，当前定价或成本结构需优化。")

# 问题3
set_text_keep_format(s2[19], "长尾商品管理粗放")
set_text_keep_format(s2[20], f"共有{len(valid)}个SKU，但大量尾部商品（销售金额<1000）可能处于亏损或微利状态，建议定期清理低效SKU，集中资源在头部产品。")

# 问题4
set_text_keep_format(s2[25], "核心单品面临替代品冲击")
set_text_keep_format(s2[26], "头部产品（如拉小米、甜薯玉米）市场竞争加剧，竞品低价冲击明显。建议强化产品差异化卖点，提升用户粘性。")

# 问题5
set_text_keep_format(s2[35], "产品质量差评需关注")
set_text_keep_format(s2[36], "部分产品差评集中在太黏或太干及不上鱼，说明产品品质稳定性有待提升。建议加强品控，建立产品反馈闭环机制。")

print("第2页完成")

# ========== 6. 保存 ==========
prs.save(OUTPUT)
print(f"\n已生成: {OUTPUT}")

# ========== 7. 简单验证 ==========
print("\n--- 验证关键字体 ---")
prs_v = Presentation(OUTPUT)
slide_v = prs_v.slides[0]
s_v = {si: sh for si, sh in enumerate(slide_v.shapes)}
# 主标题
f = s_v[1].text_frame.paragraphs[0].runs[0].font
print(f"主标题: name={f.name}, size={f.size}, bold={f.bold}")
# 表格第一个数据单元格
cell = slide_v.shapes[4].table.cell(1, 1)
f = cell.text_frame.paragraphs[0].runs[0].font
print(f"表格数据: name={f.name}, size={f.size}, bold={f.bold}")
# 大数字
f = s_v[7].text_frame.paragraphs[0].runs[0].font
print(f"大数字: name={f.name}, size={f.size}, bold={f.bold}")
print("验证完成")
