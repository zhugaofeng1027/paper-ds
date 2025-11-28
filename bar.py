import matplotlib.pyplot as plt


# # 设置数据
# ACL
# years = ["ACL2023", "ACL2024", "ACL2025"]
# values = [14, 79, 260]

# CVPR
# years = ["CVPR2023", "CVPR2024", "CVPR2025"]
# values = [10, 12, 31]

# ICCV
years = ["ICCV2023", "ECCV2024", "ICCV2025", ]
values = [6, 12, 23]


# Nips
# years = ["Nips2023", "Nips2024", "Nips2025"]
# values = [54, 106, 221]

# ICML
# years = ["icml2023", "icml2024", "icml2025"]
# values = [30, 59, 113]

# ICLR
# years = ["iclr2023", "iclr2024"]
# values = [24, 42]

# 创建柱状图
plt.figure(figsize=(6, 6))
# 调整柱子宽度使其更细且更紧凑
plt.bar(years, values, color=['#FFB6C1', '#98FB98', '#87CEFA'], width=0.3)
# plt.bar(years, values, color=['#FFB6C1', '#98FB98'], width=0.3)

# 添加标题和标签
plt.title('eccv and iccv example')
plt.xlabel('year')
plt.ylabel('count')

# 在柱状图上添加数值标签
# for i, value in enumerate(values):
#     plt.text(i, value + 5, str(value), ha='center')
for i, value in enumerate(values):
     plt.text(i, value + 0.5, str(value), ha='center')

# 保存图表（可选）
plt.savefig('iccv.png')

# 显示图表
plt.tight_layout()
plt.show()