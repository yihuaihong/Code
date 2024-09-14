import matplotlib.pyplot as plt
import numpy as np

# 假设数据
edits = np.arange(1, 11)  # 编辑次数从1到10

scores_pmet = np.random.rand(10) * 100  # PMET分数
scores_mend = np.random.rand(10) * 100  # MEND分数
scores_rome = np.random.rand(10) * 100  # ROME分数

efficacy_pmet = [97.2, 97.35, 96.3, 95.71, 95.08]
efficacy_MEMIT = [96.9, 96.91, 96.5, 95.72, 95.1]
efficacy_TKE = [99.79, 98.58610341, 97.7040017, 96.18849641, 95.90198893]
efficacy_TKE_rephrase = [99.84, 99.68610341, 97.79740017, 96.2749641, 95.93198893]
efficacy_TKE_target = [97.0, 96.92, 96.31, 95.81, 95.22]

###########################################
Generalization_pmet = [88.7, 88.39, 88.24, 87.23, 85.30, ]

Generalization_MEMIT = [88.1, 88.13, 87.64, 85.64, 84.33, ]

Generalization_TKE = [90.31, 89.26, 88.31, 87.79, 87.3]

Generalization_TKE_rephrase = [90.47, 90.31, 89.87, 87.99, 87.5]

Generalization_TKE_target = [88.0, 88.22, 87.27, 86.17, 85.01]

###########################################
Specificity_pmet = [26.44, 26.31, 26.33, 26.33, 25.89]

Specificity_MEMIT = [26.47, 26.34, 26.25, 26.35, 25.84]

Specificity_TKE = [27.3, 27.17, 27.12, 26.55, 26.1]

Specificity_TKE_rephrase = [26.2, 26.21, 25.97, 25.84, 25.83]

Specificity_TKE_target = [27.43, 27.3, 27.17, 26.87, 26.32]

print('scores_pmet: ', scores_pmet)
print('scores_mend: ', scores_mend)
print('scores_rome: ', scores_rome)

# 创建3个子图
fig, axs = plt.subplots(3, 1, figsize=(6, 15))

# 设置标题
titles = ['Efficacy', 'Generalization', 'Specificity']

# 设置 x 轴刻度和标签
xticks = np.arange(1, 6)
xticklabels = ['10^0', '10^1', '10^2', '10^3', '10^4']

for i, ax in enumerate(axs):

    if i == 0:
        ax.plot(xticks, efficacy_pmet, 'o-', color='pink', label='PMET')
        ax.plot(xticks, efficacy_MEMIT, 's-', color='green', label='MEMIT')
        ax.plot(xticks, efficacy_TKE, '*-', color='purple', label='TailoredKE')
        ax.plot(xticks, efficacy_TKE_rephrase, '--', color='red', label='TailoredKE$_{Rephrase}$')
        ax.plot(xticks, efficacy_TKE_target, '^-', color='blue', label='TailoredKE$_{Targeted}$')

        ax.set_title(titles[i])
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        ax.set_xlabel('Number of Edits')

    elif i == 1:
        ax.plot(xticks, Generalization_pmet, 'o-', color='pink', label='PMET')
        ax.plot(xticks, Generalization_MEMIT, 's-', color='green', label='MEMIT')
        ax.plot(xticks, Generalization_TKE, '*-', color='purple', label='TailoredKE')
        ax.plot(xticks, Generalization_TKE_rephrase, '--', color='red', label='TailoredKE$_{Rephrase}$')
        ax.plot(xticks, Generalization_TKE_target, '^-', color='blue', label='TailoredKE$_{Targeted}$')

        ax.set_title(titles[i])
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        ax.set_xlabel('Number of Edits')

    elif i == 2:
        ax.plot(xticks, Specificity_pmet, 'o-', color='pink', label='PMET')
        ax.plot(xticks, Specificity_MEMIT, 's-', color='green', label='MEMIT')
        ax.plot(xticks, Specificity_TKE, '*-', color='purple', label='TailoredKE')
        ax.plot(xticks, Specificity_TKE_rephrase, '--', color='red', label='TailoredKE$_{Rephrase}$')
        ax.plot(xticks, Specificity_TKE_target, '^-', color='blue', label='TailoredKE$_{Targeted}$')

        ax.set_title(titles[i])
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        ax.set_xlabel('Number of Edits')

# 创建一个图例，并将其放置在图像的正下方，稍微提高位置
handles, labels = axs[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=5, frameon=False)

# 调整子图间距和图例位置
plt.subplots_adjust(bottom=0.2, hspace=0.2)

# 显示图表
plt.show()

plt.savefig('your_figure_filename.png', bbox_inches='tight')