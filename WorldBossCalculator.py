import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib
import sys
import os

# 判断是否是打包后的环境
if getattr(sys, 'frozen', False):
    # 如果是打包后的exe，字体路径指向打包的字体
    base_path = sys._MEIPASS
else:
    # 如果是开发环境，使用当前目录
    base_path = os.path.dirname(__file__)

# 尝试加载字体文件
font_path = os.path.join(base_path, 'fonts', 'simhei.ttf')
if os.path.exists(font_path):
    matplotlib.font_manager.fontManager.addfont(font_path)
    font_name = matplotlib.font_manager.FontProperties(fname=font_path).get_name()
    matplotlib.rcParams['font.sans-serif'] = [font_name]
else:
    # 如果找不到字体文件，使用默认字体
    matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']

matplotlib.rcParams['axes.unicode_minus'] = False

# 设置中文字体，解决中文显示问题
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

# 普通模式数据
scores_normal_wan = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160,
                     170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310,
                     320, 330, 340, 350, 360, 370, 380, 390, 400]

damages_normal_yi = [0, 8.78, 19.32, 31.96, 47.13, 65.34, 87.18, 113.4, 144.86, 182.61, 227.92,
                    282.28, 347.52, 425.8, 519.74, 632.47, 767.74, 930.07, 1124.86, 1358.62,
                    1639.12, 1975.72, 2379.65, 2864.36, 3446.01, 4143.99, 4981.57, 5986.67,
                    7192.78, 8640.12, 10376.92, 12461.08, 14962.08, 17963.28, 21564.71, 25886.44,
                    31072.5, 37295.78, 44763.72, 53725.24, 64479.07]

# 挑战模式数据
scores_challenge_wan = [0, 400, 800, 1200, 1600, 2000, 2400, 2800, 3200, 3600, 4000, 4400, 4800,
                        5200, 5600, 6000, 6400, 6800, 7200, 7600, 8000, 8400, 8800, 9200, 9600,
                        10000, 10400, 10800, 11200, 11600, 12000, 12400, 12800, 13200, 13600,
                        14000, 14400, 14800, 15200, 15600, 16000]

damages_challenge_yi = [0, 1097.5, 2414.5, 3994.9, 5891.38, 8167.16, 10898.09, 14175.2, 18107.75,
                       22826.79, 28489.65, 35285.08, 43439.6, 53225.02, 64967.53, 79058.53,
                       95967.74, 116258.78, 140608.04, 169827.15, 204890.08, 246965.6, 297456.21,
                       358044.96, 430751.45, 517999.24, 622696.59, 748333.4, 899097.58, 1080014.6,
                       1297115.02, 1557635.53, 1870260.13, 2245409.66, 2695589.09, 3235804.41,
                       3884062.79, 4661972.85, 5595464.92, 6715655.4, 8059883.98]

# 转换为实际数值（单位：分和亿）
scores_normal = [score * 10000 for score in scores_normal_wan]  # 转换为分
damages_normal = damages_normal_yi  # 保持亿为单位

scores_challenge = [score * 10000 for score in scores_challenge_wan]  # 转换为分
damages_challenge = damages_challenge_yi  # 保持亿为单位


def get_damage_value(score, mode="普通模式"):
    if mode == "普通模式":
        scores = scores_normal
        damages = damages_normal
        max_score = 4000000
    else:  # 挑战模式
        scores = scores_challenge
        damages = damages_challenge
        max_score = 160000000

    # 边界检查
    if score < 0:
        return damages[0]
    if score >= scores[-1]:
        return damages[-1]

    # 查找score所在的区间
    for i in range(len(scores) - 1):
        if scores[i] <= score < scores[i + 1]:
            # 线性插值
            x1, x2 = scores[i], scores[i + 1]
            y1, y2 = damages[i], damages[i + 1]
            return y1 + (y2 - y1) * (score - x1) / (x2 - x1)

    return damages[-1]


def get_max_score(mode):
    if mode == "普通模式":
        return 4000000
    else:  # 挑战模式
        return 160000000


def calculate_improvement():
    global improvement_label

    try:
        # 获取当前模式
        mode = mode_var.get()
        max_score = get_max_score(mode)

        # 获取用户输入
        current_score = int(current_score_entry.get().strip())
        target_score = int(target_score_entry.get().strip())

        # 输入验证
        if current_score < 0 or current_score > max_score:
            messagebox.showerror("输入错误", f"当前分数必须在0-{max_score}之间！")
            return
        if target_score < 0 or target_score > max_score:
            messagebox.showerror("输入错误", f"目标分数必须在0-{max_score}之间！")
            return
        if target_score <= current_score:
            messagebox.showerror("输入错误", "目标分数必须大于当前分数！")
            return

        # 计算对应的血量值
        current_damage = get_damage_value(current_score, mode)
        target_damage = get_damage_value(target_score, mode)

        # 计算提升百分比
        if current_damage > 0:
            improvement = ((target_damage - current_damage) / current_damage * 100)
        else:
            improvement = 0

        # 显示结果
        result_text = f"模式: {mode}\n"
        result_text += f"当前分数: {current_score:,} 分\n"
        result_text += f"对应血量: {current_damage:,.2f} 亿\n"
        result_text += f"目标分数: {target_score:,} 分\n"
        result_text += f"对应血量: {target_damage:,.2f} 亿\n"

        # 使用标签直接显示所有结果，提升百分比使用加粗红色字体
        result_label.config(text=result_text, font=('Arial', 11), fg='black')

        # 创建提升百分比文本，使用HTML样式的标记
        improvement_text = f"血量提升: {improvement:.2f}%"

        # 清除之前的提升百分比标签（如果存在）
        if 'improvement_label' in globals():
            improvement_label.destroy()

        # 创建新的提升百分比标签，使用加粗红色字体
        improvement_label = tk.Label(result_frame,
                                     text=improvement_text,
                                     font=('Arial', 12, 'bold'),
                                     fg='red',
                                     bg='#F0F0F0')
        improvement_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        # 更新图表
        update_chart(current_score, target_score, current_damage, target_damage, mode)

    except ValueError:
        messagebox.showerror("输入错误", "请输入有效的整数！")
    except Exception as e:
        messagebox.showerror("计算错误", f"发生错误: {str(e)}")


def update_chart(current_score, target_score, current_damage, target_damage, mode):
    # 清除之前的图表
    ax.clear()

    # 根据模式选择数据
    if mode == "普通模式":
        scores = scores_normal
        damages = damages_normal
        max_score = 4000000
        title = f'{mode} - [分数-血量]关系图'
    else:
        scores = scores_challenge
        damages = damages_challenge
        max_score = 160000000
        title = f'{mode} - [分数-血量]关系图'

    # 绘制分段线性函数
    x_vals = np.linspace(0, max_score, 1000)
    y_vals = [get_damage_value(x, mode) for x in x_vals]

    ax.plot(x_vals, y_vals, 'b-', linewidth=2, label='[分数-血量]函数')

    # 标记当前点和目标点
    ax.plot(current_score, current_damage, 'ro', markersize=8, label='当前点')
    ax.plot(target_score, target_damage, 'go', markersize=8, label='目标点')

    # 设置图表属性
    ax.set_xlabel('分数 (分)', fontsize=10)
    ax.set_ylabel('血量 (亿)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    # 调整布局
    ax.set_xlim(0, max_score)
    ax.set_ylim(0, max(damages) * 1.1)

    # 设置x轴格式（分数）
    ax.get_xaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    # 设置y轴格式（血量）
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    # 重新绘制
    canvas.draw()


def on_mode_change(*args):
    global improvement_label

    mode = mode_var.get()
    max_score = get_max_score(mode)

    # 更新输入框的提示文本
    current_score_label.config(text=f"当前分数 (0-{max_score}):")
    target_score_label.config(text=f"目标分数 (0-{max_score}):")

    # 清除结果
    result_label.config(text="请选择模式并输入分数进行计算", font=('Arial', 11), fg='black')

    # 清除提升百分比标签（如果存在）
    if 'improvement_label' in globals():
        improvement_label.destroy()


def create_gui():
    root = tk.Tk()
    root.title("世界领主[分数-血量]计算器")
    root.geometry("1000x750")

    # 窗口关闭事件处理
    def on_closing():
        try:
            # 停止matplotlib动画
            plt.close('all')
            # 如果存在canvas，断开连接
            if 'canvas' in globals():
                try:
                    canvas.stop_event_loop()
                except:
                    pass
            # 关闭所有matplotlib图形窗口
            import matplotlib.pyplot as plt
            plt.close('all')
        except Exception as e:
            print(f"清理资源时发生错误: {e}")
        finally:
            # 确保窗口被销毁
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 设置样式
    style = ttk.Style()
    style.configure('TLabel', font=('Arial', 10))
    style.configure('TButton', font=('Arial', 10))

    # 主框架
    main_frame = ttk.Frame(root, padding="20")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # 标题
    title_label = ttk.Label(main_frame, text="世界领主[分数-血量]计算器",
                            font=('Arial', 16, 'bold'))
    title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

    # 模式选择区域
    mode_frame = ttk.LabelFrame(main_frame, text="选择模式", padding="10")
    mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

    global mode_var
    mode_var = tk.StringVar(value="普通模式")
    mode_var.trace('w', on_mode_change)  # 绑定模式改变事件

    normal_radio = ttk.Radiobutton(mode_frame, text="普通模式",
                                   variable=mode_var, value="普通模式")
    normal_radio.grid(row=0, column=0, padx=10, pady=5)

    challenge_radio = ttk.Radiobutton(mode_frame, text="挑战模式",
                                      variable=mode_var, value="挑战模式")
    challenge_radio.grid(row=0, column=1, padx=10, pady=5)

    # 输入区域
    input_frame = ttk.LabelFrame(main_frame, text="输入参数", padding="10")
    input_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

    # 当前分数输入
    global current_score_label
    current_score_label = ttk.Label(input_frame, text="当前分数 (0-4000000):")
    current_score_label.grid(row=0, column=0, sticky=tk.W, pady=5)

    global current_score_entry
    current_score_entry = ttk.Entry(input_frame, width=20)
    current_score_entry.grid(row=0, column=1, padx=10, pady=5)
    ttk.Label(input_frame, text="分").grid(row=0, column=2, sticky=tk.W, pady=5)

    # 目标分数输入
    global target_score_label
    target_score_label = ttk.Label(input_frame, text="目标分数 (0-4000000):")
    target_score_label.grid(row=1, column=0, sticky=tk.W, pady=5)

    global target_score_entry
    target_score_entry = ttk.Entry(input_frame, width=20)
    target_score_entry.grid(row=1, column=1, padx=10, pady=5)
    ttk.Label(input_frame, text="分").grid(row=1, column=2, sticky=tk.W, pady=5)

    # 计算按钮
    calculate_button = ttk.Button(input_frame, text="计算提升百分比",
                                  command=calculate_improvement)
    calculate_button.grid(row=2, column=0, columnspan=3, pady=10)

    # 结果显示区域
    global result_frame
    result_frame = ttk.LabelFrame(main_frame, text="计算结果", padding="10")
    result_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))

    global result_label
    result_label = tk.Label(result_frame, text="请选择模式并输入分数进行计算",
                            font=('Arial', 11), justify=tk.LEFT, bg='#F0F0F0')
    result_label.grid(row=0, column=0, sticky=tk.W, pady=5)

    # 图表区域
    chart_frame = ttk.LabelFrame(main_frame, text="数据可视化", padding="10")
    chart_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

    # 创建图表
    global fig, ax, canvas
    fig, ax = plt.subplots(figsize=(10, 5))
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # 初始绘制函数曲线（普通模式）
    x_vals = np.linspace(0, 4000000, 1000)
    y_vals = [get_damage_value(x, "普通模式") for x in x_vals]
    ax.plot(x_vals, y_vals, 'b-', linewidth=2)
    ax.set_xlabel('分数 (分)', fontsize=10)
    ax.set_ylabel('血量 (亿)', fontsize=10)
    ax.set_title('普通模式 - [分数-血量]关系图', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    # 设置x轴格式（分数）
    ax.get_xaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    # 设置y轴格式（血量），强制显示为整数
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    # 使用说明
    info_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="10")
    info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

    info_text = """1. 选择游戏模式（普通模式或挑战模式）
2. 输入当前分数和目标分数（输入范围内的整数）
3. 点击"计算提升百分比"按钮
4. 查看计算结果和可视化图表
5. 红色点表示当前分数，绿色点表示目标分数"""

    ttk.Label(info_frame, text=info_text, justify=tk.LEFT).grid(row=0, column=0, sticky=tk.W)

    # 配置权重
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.columnconfigure(2, weight=1)
    main_frame.rowconfigure(4, weight=1)

    return root


def main():
    # 创建并运行GUI
    root = create_gui()
    root.mainloop()


if __name__ == "__main__":
    main()