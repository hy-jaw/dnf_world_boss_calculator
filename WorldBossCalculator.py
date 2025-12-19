import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import math

# 设置使用默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


def generate_function_nodes(mode="普通模式", target_score=None):
    if mode == "普通模式":
        if target_score is None:
            # 默认显示完整曲线：0到400万
            max_node_wan = 400
        else:
            # 计算最大节点（万）
            max_node_wan = math.floor(target_score / 100000 / 0.9) * 10
            # 如果计算出的最大节点为0，设为10（最小节点间隔）
            if max_node_wan == 0:
                max_node_wan = 10

        # 生成节点序列（以万为单位），从0到max_node_wan，间隔10
        scores_wan = list(range(0, int(max_node_wan) + 1, 10))

        # 生成对应的函数值
        damages = []
        for score_wan in scores_wan:
            n = score_wan / 10
            if n == 0:
                damage = 0
            else:
                damage = 43.9 * (1.2 ** n - 1)
            damages.append(damage)

        # 将节点转换为分
        scores = [score_wan * 10000 for score_wan in scores_wan]

    else:  # 挑战模式
        if target_score is None:
            # 默认显示完整曲线：0到16000万
            max_node_wan = 16000
        else:
            # 计算最大节点（万）
            max_node_wan = math.floor(target_score / 4000000 / 0.9) * 400
            # 如果计算出的最大节点为0，设为400（最小节点间隔）
            if max_node_wan == 0:
                max_node_wan = 400

        # 生成节点序列（以万为单位），从0到max_node_wan，间隔400
        scores_wan = list(range(0, int(max_node_wan) + 1, 400))

        # 生成对应的函数值
        damages = []
        for score_wan in scores_wan:
            n = score_wan / 400
            if n == 0:
                damage = 0
            else:
                damage = 5487.5 * (1.2 ** n - 1)
            damages.append(damage)

        # 将节点转换为分
        scores = [score_wan * 10000 for score_wan in scores_wan]

    return scores, damages


def get_damage_value(score, mode="普通模式", target_score=None):
    # 生成函数节点
    scores, damages = generate_function_nodes(mode, target_score)

    # 边界检查
    if score < 0:
        return damages[0]
    if score >= scores[-1]:
        # 如果超出当前节点范围，使用最后一个节点的值
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
    # 现在不设上限，返回一个足够大的值
    if mode == "普通模式":
        return 1000000000
    else:  # 挑战模式
        return 10000000000


def calculate_improvement():
    global improvement_label

    try:
        # 获取当前模式
        mode = mode_var.get()

        # 获取用户输入
        current_score = int(current_score_entry.get().strip())
        target_score = int(target_score_entry.get().strip())

        # 输入验证
        if current_score < 0:
            messagebox.showerror("输入错误", f"当前分数不能为负数！")
            return
        if target_score < 0:
            messagebox.showerror("输入错误", f"目标分数不能为负数！")
            return
        if target_score <= current_score:
            messagebox.showerror("输入错误", "目标分数必须大于当前分数！")
            return

        # 计算对应的血量值（传入target_score用于生成合适的节点）
        current_damage = get_damage_value(current_score, mode, target_score)
        target_damage = get_damage_value(target_score, mode, target_score)

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

        # 使用标签直接显示所有结果
        result_label.config(text=result_text, font=('Arial', 11), fg='black')

        # 创建提升百分比文本
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

    # 生成函数节点
    scores, damages = generate_function_nodes(mode, target_score)

    # 计算目标分数在x轴上的位置百分比
    max_score = scores[-1]
    target_position_percent = target_score / max_score * 100

    # 绘制分段线性函数
    ax.plot(scores, damages, 'b-', linewidth=2, label='[分数-血量]函数')

    # 标记当前点和目标点
    ax.plot(current_score, current_damage, 'ro', markersize=8, label='当前点')
    ax.plot(target_score, target_damage, 'go', markersize=8, label='目标点')

    # 设置图表属性
    ax.set_xlabel('分数 (分)', fontsize=10)
    ax.set_ylabel('血量 (亿)', fontsize=10)

    # 根据模式设置标题
    if mode == "普通模式":
        title = f'普通模式 - [分数-血量]关系图'
    else:
        title = f'挑战模式 - [分数-血量]关系图'

    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc='upper left')

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

    # 更新输入框的提示文本
    current_score_label.config(text=f"当前分数:")
    target_score_label.config(text=f"目标分数:")

    # 清除结果
    result_label.config(text="请选择模式并输入分数进行计算", font=('Arial', 11), fg='black')

    # 清除提升百分比标签（如果存在）并清除图表
    if 'improvement_label' in globals():
        improvement_label.destroy()

    # 清除图表，显示默认函数曲线
    ax.clear()

    # 生成并显示默认函数曲线（完整曲线）
    if mode == "普通模式":
        scores, damages = generate_function_nodes("普通模式")  # 显示完整0-400万曲线
        title = f'普通模式 - [分数-血量]关系图'
    else:
        scores, damages = generate_function_nodes("挑战模式")  # 显示完整0-16000万曲线
        title = f'挑战模式 - [分数-血量]关系图'

    ax.plot(scores, damages, 'b-', linewidth=2)
    ax.set_xlabel('分数 (分)', fontsize=10)
    ax.set_ylabel('血量 (亿)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # 设置x轴格式（分数）
    ax.get_xaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    # 设置y轴格式（血量）
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    canvas.draw()


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
    current_score_label = ttk.Label(input_frame, text="当前分数:")
    current_score_label.grid(row=0, column=0, sticky=tk.W, pady=5)

    global current_score_entry
    current_score_entry = ttk.Entry(input_frame, width=20)
    current_score_entry.grid(row=0, column=1, padx=10, pady=5)
    ttk.Label(input_frame, text="分").grid(row=0, column=2, sticky=tk.W, pady=5)

    # 目标分数输入
    global target_score_label
    target_score_label = ttk.Label(input_frame, text="目标分数:")
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

    # 初始绘制函数曲线（普通模式，完整0-400万曲线）
    scores, damages = generate_function_nodes("普通模式")  # 显示完整0-400万曲线
    ax.plot(scores, damages, 'b-', linewidth=2)
    ax.set_xlabel('分数 (分)', fontsize=10)
    ax.set_ylabel('血量 (亿)', fontsize=10)
    ax.set_title('普通模式 - [分数-血量]关系图', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    # 设置x轴格式（分数）
    ax.get_xaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    # 设置y轴格式（血量）
    ax.get_yaxis().set_major_formatter(
        plt.FuncFormatter(lambda x, p: format(int(x), ','))
    )

    # 使用说明
    info_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="10")
    info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

    info_text = """1. 选择游戏模式（普通模式或挑战模式）
2. 输入当前分数和目标分数（非负整数，且目标分数须大于当前分数）
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
    root = create_gui()
    root.mainloop()


if __name__ == "__main__":
    main()
