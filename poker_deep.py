import tkinter as tk
from tkinter import ttk, messagebox, font
from treys import Card, Evaluator
import random
import itertools
import math

class TournamentInfo:


    def __init__(self):
        self.name = "挖矿赛"
        self.game_type = "无限注德州扑克"
        self.buy_in = 0.99
        self.starting_chips = 20000
        self.blind_levels = [
            (100, 200, 0),      # Level 1
            (200, 400, 0),      # Level 2
            (400, 800, 80),     # Level 3
            (800, 1600, 160),   # Level 4
            (1200, 2400, 240),  # Level 5
            (2000, 4000, 400),  # Level 6
            (4000, 8000, 800),  # Level 7
            (8000, 16000, 1600),# Level 8
            (12000, 24000, 2400), # Level 9
            (20000, 40000, 4000), # Level 10
            (30000, 60000, 6000), # Level 11
            (40000, 80000, 8000), # Level 12
            (50000, 100000, 10000), # Level 13
            (60000, 120000, 12000), # Level 14
            (80000, 160000, 16000), # Level 15
            (100000, 200000, 20000), # Level 16
            (200000, 400000, 40000), # Level 17
            (300000, 600000, 60000), # Level 18
            (400000, 800000, 80000), # Level 19
            (500000, 1000000, 100000), # Level 20
            (600000, 1200000, 120000), # Level 21
            (800000, 1600000, 160000), # Level 22
            (1000000, 2000000, 200000) # Level 23
        ]
        self.blind_time = 180  # 3分钟
        self.time_bank = 15
        self.max_players = 20000
        self.players_per_table = 9
        self.ante = 0  # 前注

class PokerAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("德州扑克助手")
        self.root.geometry("1200x900")

        # 创建字体对象 - 使用系统字体
        self.default_font = ('Liberation Sans', 10)
        self.title_font = ('Liberation Sans', 11)
        
        # 配置全局默认字体
        self.root.option_add('*Font', self.default_font)
        self.root.option_add('*Label.Font', self.default_font)
        self.root.option_add('*Button.Font', self.default_font)
        self.root.option_add('*Entry.Font', self.default_font)
        self.root.option_add('*Text.Font', self.default_font)
        self.root.option_add('*Menu.Font', self.default_font)
        self.root.option_add('*Listbox.Font', self.default_font)
        
        # 移除ttk样式配置
        # self.style = ttk.Style()
        # self.style.configure...

        self.tournament = TournamentInfo()
        self.current_level = 0  # 当前盲注等级

        # 添加比赛阶段控制
        self.game_stages = ['未开始', '底牌', '翻牌', '转牌', '河牌']
        self.current_stage = '未开始'

        # 位置编号和名称的映射（按照顺时针顺序，从BB开始）
        self.position_numbers = {
            1: '大盲位(BB)',
            2: '枪口位(UTG)',
            3: '枪口+1(UTG+1)',
            4: '枪口+2(UTG+2)',
            5: '中间位(MP)',
            6: '中间位+1(MP+1)',
            7: '切位(CO)',
            8: '庄家位(BTN)',
            9: '小盲位(SB)'
        }

        # 位置名称到编号的反向映射
        self.position_to_number = {v: k for k, v in self.position_numbers.items()}

        # 位置名称到英文缩写的映射
        self.position_map = {
            '大盲位(BB)': 'BB',
            '枪口位(UTG)': 'UTG',
            '枪口+1(UTG+1)': 'UTG+1',
            '枪口+2(UTG+2)': 'UTG+2',
            '中间位(MP)': 'MP',
            '中间位+1(MP+1)': 'MP+1',
            '切位(CO)': 'CO',
            '庄家位(BTN)': 'BTN',
            '小盲位(SB)': 'SB'
        }

        self.my_position = '大盲位(BB)'  # 默认我的位置
        self.player_positions = list(self.position_map.keys())  # 所有位置名称列表

        self.player_cards = {pos: None for pos in self.player_positions}
        self.community_cards = []
        self.player_entries = {}  # 存储玩家手牌输入框
        self.player_actions = {}  # 存储玩家操作选择
        self.raise_entries = {}   # 存储加注金额输入框
        self.player_chips = {}    # 存储玩家筹码量
        self.player_frames = {}   # 存储玩家位置框架
        self.pot_size = 0         # 底池大小

        self.evaluator = Evaluator()  # 创建评估器

        # 添加决策相关的属性
        self.active_players = set()  # 当前还在参与的玩家
        self.current_bet = 0  # 当前最大下注额
        self.total_pot = 0  # 总底池
        self.last_action = {}  # 记录每个位置的最后一个动作
        self.position_bets = {}  # 记录每个位置的下注额

        self.setup_gui()

    def setup_gui(self):
        # 使用tk原生widgets替代ttk
        main_frame = tk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # 使用tk.LabelFrame替代ttk.LabelFrame
        info_frame = tk.LabelFrame(left_frame, text="比赛信息", font=self.title_font)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        # 使用tk.Label替代ttk.Label
        position_frame = tk.Frame(info_frame)
        position_frame.pack(fill=tk.X, pady=2)
        tk.Label(position_frame, text="我的位置:", font=self.default_font).pack(side=tk.LEFT)
        self.my_position_var = tk.StringVar(value=self.my_position)
        position_menu = tk.OptionMenu(position_frame, self.my_position_var,
                                     self.my_position, *self.player_positions,
                                     command=self.on_position_change)
        position_menu.configure(font=self.default_font)  # 使用自定义字体
        position_menu.pack(side=tk.LEFT, padx=5)

        # 添加比赛信息（使用变量以便更新）
        self.blind_info_var = tk.StringVar()
        self.update_blind_info()
        self.blind_label = tk.Label(info_frame, textvariable=self.blind_info_var, font=self.default_font)
        self.blind_label.pack(pady=2)

        # 添加当前级别显示
        self.level_var = tk.StringVar()
        self.update_level_info()
        self.level_label = tk.Label(info_frame, textvariable=self.level_var, font=self.default_font)
        self.level_label.pack(pady=2)

        # 添加底池输入
        pot_frame = tk.Frame(info_frame)
        pot_frame.pack(fill=tk.X, pady=2)
        tk.Label(pot_frame, text="当前底池:", font=self.default_font).pack(side=tk.LEFT)
        self.pot_entry = tk.Entry(pot_frame, width=10, font=self.default_font)
        self.pot_entry.pack(side=tk.LEFT, padx=5)
        self.pot_entry.insert(0, "0")

        # 在中间显示公共牌区域之前，添加当前玩家手牌输入区域
        my_cards_frame = tk.LabelFrame(info_frame, text="我的手牌", font=self.title_font)
        my_cards_frame.pack(fill=tk.X, pady=2)
        
        # 添加当前玩家手牌输入框
        self.my_cards_entry = tk.Entry(my_cards_frame, width=10, font=self.default_font)
        self.my_cards_entry.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 添加提示标签
        tk.Label(my_cards_frame, text="(例如: AhKs)", font=self.default_font).pack(side=tk.LEFT, padx=5)

        # 创建牌桌框架 (放在左边)
        table_frame = tk.Frame(left_frame)
        table_frame.pack(expand=True, fill=tk.BOTH)

        # 创建Canvas - 增加高度，给底部留出更多空间
        self.table_canvas = tk.Canvas(table_frame, width=800, height=700, bg='#1a472a')  # 增加画布高度到700
        self.table_canvas.pack(expand=True)

        # 画椭圆形牌桌 - 向上移动一些，给底部留出更多空间
        self.table_canvas.create_oval(50, 50, 750, 600, fill='#2d5a3f', outline='#1e5631', width=3)  # 调整椭圆底部位置到600

        # 在中间显示公共牌区域 - 相应调整垂直位置
        community_frame = tk.LabelFrame(self.table_canvas, text="公共牌", font=self.title_font)
        self.table_canvas.create_window(400, 325, window=community_frame)  # 调整垂直位置到325
        
        # 添加公共牌输入框
        self.community_entry = tk.Entry(community_frame, width=20, font=self.default_font)
        self.community_entry.pack(padx=5, pady=5)
        
        # 添加提示标签
        tk.Label(community_frame, 
                 text="(例如: AhKsQd)", 
                 font=self.default_font).pack(padx=5, pady=2)

        # 创建玩家位置框架
        self.frame_windows = {}  # 存储canvas window的ID
        total_positions = len(self.player_positions)
        angle_step = 360 / total_positions  # 动态计算角度间隔

        for pos in self.player_positions:
            player_frame = tk.Frame(self.table_canvas)
            self.player_frames[pos] = player_frame

            # 添加位置标签
            tk.Label(player_frame, text=pos, font=self.default_font).pack()

            # 只为其他玩家添加手牌输入框
            if pos != self.my_position:
                entry = tk.Entry(player_frame, width=8, font=self.default_font)
                entry.pack()
                self.player_entries[pos] = entry
            else:
                # 为当前玩家位置添加手牌显示标签
                self.my_cards_label = tk.Label(player_frame, text="", font=self.default_font)
                self.my_cards_label.pack()

            # 添加筹码输入框
            chips_frame = tk.Frame(player_frame)
            chips_frame.pack()
            tk.Label(chips_frame, text="筹码:", font=self.default_font).pack(side=tk.LEFT)
            chips_entry = tk.Entry(chips_frame, width=8, font=self.default_font)
            chips_entry.pack(side=tk.LEFT)
            chips_entry.insert(0, str(self.tournament.starting_chips))
            self.player_chips[pos] = chips_entry

            # 添加操作选择和加注金额输入框
            action_frame = tk.Frame(player_frame)
            action_frame.pack()

            action_var = tk.StringVar(value="等待")
            self.player_actions[pos] = action_var

            def on_action_change(position, *args):
                action = self.player_actions[position].get()
                raise_entry = self.raise_entries[position]
                if action == "加注":
                    raise_entry.pack(side=tk.LEFT, padx=2)
                else:
                    raise_entry.pack_forget()
                # 如果选择allin，自动填入当前筹码量
                if action == "allin":
                    try:
                        current_chips = self.player_chips[position].get()
                        raise_entry.delete(0, tk.END)
                        raise_entry.insert(0, current_chips)
                        raise_entry.pack(side=tk.LEFT, padx=2)
                    except:
                        pass

            action_menu = tk.OptionMenu(action_frame, action_var, "等待",
                                       "弃牌", "跟注", "加注", "allin",
                                       command=lambda *args, p=pos: on_action_change(p, *args))
            action_menu.configure(font=self.default_font)  # 使用自定义字体
            action_menu.pack(side=tk.LEFT)

            # 修改Entry的样式
            raise_entry = tk.Entry(action_frame, width=8, font=self.default_font)
            self.raise_entries[pos] = raise_entry

            # 创建window，设置初始位置
            pos_number = self.position_to_number[pos]
            # 计算角度，确保均匀分布
            angle = math.radians(270 - (pos_number-1)*angle_step)
            
            # 基础半径和偏移量
            base_radius = 250
            x_offset = 0
            y_offset = 0
            
            # 根据位置调整半径和偏移
            angle_deg = math.degrees(angle) % 360
            if 0 <= angle_deg < 45 or 315 <= angle_deg < 360:  # 下方
                anchor = tk.N
                y_offset = 50
                adjusted_radius = base_radius
            elif 45 <= angle_deg < 135:  # 右侧
                anchor = tk.W
                x_offset = 60
                adjusted_radius = base_radius * 1.1
            elif 135 <= angle_deg < 225:  # 上方
                anchor = tk.S
                y_offset = -50
                adjusted_radius = base_radius * 1.2
            elif 225 <= angle_deg < 315:  # 左侧
                anchor = tk.E
                x_offset = -60
                adjusted_radius = base_radius * 1.1

            # 计算最终位置
            x = 400 + adjusted_radius * math.cos(angle) + x_offset
            y = 325 + adjusted_radius * math.sin(angle) + y_offset

            # 创建window
            window_id = self.table_canvas.create_window(x, y, window=player_frame, anchor=anchor)
            self.frame_windows[pos] = window_id

        # 初始化位置
        self.update_positions()

        # 创建控制面板和分析结果区域 (放在右边)
        control_frame = tk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # 添加比赛阶段控制
        stage_frame = tk.LabelFrame(right_frame, text="比赛阶段", font=self.title_font)
        stage_frame.pack(fill=tk.X, pady=5)

        # 添加阶段控制按钮
        self.stage_buttons = {}
        self.stage_buttons['开始新一轮'] = tk.Button(stage_frame, text="开始新一轮",
                                                command=self.start_new_round, font=self.default_font)
        self.stage_buttons['开始新一轮'].pack(side=tk.LEFT, padx=5, pady=5)

        self.stage_buttons['翻牌'] = tk.Button(stage_frame, text="发翻牌",
                                             command=lambda: self.proceed_to_stage('翻牌'), font=self.default_font)
        self.stage_buttons['翻牌'].pack(side=tk.LEFT, padx=5, pady=5)
        self.stage_buttons['翻牌']['state'] = 'disabled'

        self.stage_buttons['转牌'] = tk.Button(stage_frame, text="发转牌",
                                             command=lambda: self.proceed_to_stage('转牌'), font=self.default_font)
        self.stage_buttons['转牌'].pack(side=tk.LEFT, padx=5, pady=5)
        self.stage_buttons['转牌']['state'] = 'disabled'

        self.stage_buttons['河牌'] = tk.Button(stage_frame, text="发河牌",
                                             command=lambda: self.proceed_to_stage('河牌'), font=self.default_font)
        self.stage_buttons['河牌'].pack(side=tk.LEFT, padx=5, pady=5)
        self.stage_buttons['河牌']['state'] = 'disabled'

        # 添加当前阶段显示
        self.stage_label = tk.Label(stage_frame, text="当前阶段: 未开始", font=self.default_font)
        self.stage_label.pack(side=tk.LEFT, padx=20, pady=5)

        # 添加说明标签
        tk.Label(control_frame,
                 text="输入格式说明：手牌和公共牌都使用两个字符表示一张牌\n"
                      "第一个字符是牌面值：A（A），K（K），Q（Q），J（J），T（10），9-2，使用大写字母\n"
                      "第二个字符是花色：h（红桃），d（方块），s（黑桃），c（梅花），使用小写字母\n"
                      "例如：AhKs 表示红桃A和黑桃K", font=self.default_font).pack(pady=5)

        # 添加按钮
        button_frame = tk.Frame(control_frame)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="计算胜率",
                  command=self.calculate_odds, font=self.default_font).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="清空",
                  command=self.reset_game, font=self.default_font).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="下一级盲注",
                  command=self.increase_blind_level, font=self.default_font).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="决策分析",
                 command=self.analyze_decision, font=self.default_font).pack(side=tk.LEFT, padx=5)

        # 添加分析结果显示区域
        result_frame = tk.LabelFrame(right_frame, text="分析结果", font=self.title_font)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 添加滚动条
        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.analysis_text = tk.Text(result_frame, height=30, width=50, font=self.default_font)  # 增加文本框大小
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 配置滚动条
        scrollbar.config(command=self.analysis_text.yview)
        self.analysis_text.config(yscrollcommand=scrollbar.set)

    def update_blind_info(self):
        """更新盲注信息显示"""
        current_blind = self.tournament.blind_levels[self.current_level]
        ante = current_blind[2] if len(current_blind) > 2 else 0
        self.blind_info_var.set(
            f"比赛名称: {self.tournament.name} | "
            f"当前盲注: {current_blind[0]:,}/{current_blind[1]:,} | "
            f"前注: {ante:,}"
        )

    def update_level_info(self):
        """更新级别信息显示"""
        self.level_var.set(f"当前级别: {self.current_level + 1}")

    def increase_blind_level(self):
        """增加盲注等级"""
        if self.current_level < len(self.tournament.blind_levels) - 1:
            self.current_level += 1
            self.update_blind_info()
            self.update_level_info()
            current_blind = self.tournament.blind_levels[self.current_level]
            messagebox.showinfo("盲注更新",
                              f"盲注已更新为: {current_blind[0]:,}/{current_blind[1]:,}\n"
                              f"前注: {current_blind[2]:,}")

    def get_position_strength(self, position):
        """评估位置优势"""
        # 位置优势评分（0-10）
        position_scores = {
            '庄家位(BTN)': 10,    # 最强位置
            '切位(CO)': 9,        # 次强位置
            '中间位+1(MP+1)': 7,
            '中间位(MP)': 6,
            '枪口+2(UTG+2)': 5,
            '枪口+1(UTG+1)': 4,
            '枪口位(UTG)': 3,
            '小盲位(SB)': 2,      # 位置差
            '大盲位(BB)': 1       # 最差位置
        }
        return position_scores.get(position, 5)

    def get_hand_strength(self, hole_cards, community_cards):
        """使用Treys评估手牌强度（数值越小，牌力越强）"""
        rank = self.evaluator.evaluate(community_cards, hole_cards)
        return rank

    def get_action_recommendation(self, position, hand_strength, position_strength,
                                stack, pot_size, current_blind):
        """获取行动建议"""
        # 将手牌强度转换为0-10分，数值越高越好
        strength_score = max(0, min((7462 - hand_strength) / 7462 * 10, 10))
        total_strength = (strength_score * 0.7 + position_strength *     0.3) * (stack / self.tournament.starting_chips)  # 考虑筹码深度

        # 行动建议逻辑
        if total_strength > 8:
            return "加注/All-in"
        elif total_strength > 6:
            return "加注"
        elif total_strength > 4:
            return "跟注"
        else:
            return "弃牌"

    def on_position_change(self, new_position):
        """处理位置变更事件"""
        old_position = self.my_position
        self.my_position = new_position
        
        # 更新手牌显示
        if self.my_cards_entry.get():
            self.my_cards_label.config(text=self.my_cards_entry.get())
        
        self.update_positions()

    def update_positions(self):
        """更新玩家位置在牌桌上的布局（圆形布局）"""
        positions = list(self.position_numbers.keys())
        center_x, center_y = 400, 325  # 中心点位置
        base_radius = 250  # 增加基础半径
        angle_step = 360 / len(positions)

        # 根据当前用户位置调整起始角度
        my_pos_number = self.position_to_number[self.my_position]
        start_angle = 270 - (my_pos_number-1)*angle_step

        # 计算每个位置的实际大小
        frame_sizes = {}
        for pos in self.player_positions:
            frame = self.player_frames[pos]
            frame.update()  # 确保尺寸更新
            frame_sizes[pos] = (frame.winfo_width(), frame.winfo_height())

        for pos_name in self.player_positions:
            pos_number = self.position_to_number[pos_name]
            # 计算角度（逆时针布局）
            angle = math.radians(start_angle + (pos_number-1)*angle_step)
            angle_deg = math.degrees(angle) % 360

            # 获取当前框架的大小
            width, height = frame_sizes[pos_name]
            
            # 根据框架大小调整半径和偏移量
            adjusted_radius = base_radius
            x_offset = 0
            y_offset = 0

            # 根据位置调整
            if 0 <= angle_deg < 45 or 315 <= angle_deg < 360:  # 下方
                anchor = tk.N
                y_offset = height/2 + 50
                adjusted_radius *= 1.0
            elif 45 <= angle_deg < 135:  # 右侧
                anchor = tk.W
                x_offset = width/2 + 60
                adjusted_radius *= 1.1
            elif 135 <= angle_deg < 225:  # 上方
                anchor = tk.S
                y_offset = -height/2 - 50
                adjusted_radius *= 1.2
            elif 225 <= angle_deg < 315:  # 左侧
                anchor = tk.E
                x_offset = -width/2 - 60
                adjusted_radius *= 1.1

            # 计算最终位置，考虑框架大小
            x = center_x + adjusted_radius * math.cos(angle) + x_offset
            y = center_y + adjusted_radius * math.sin(angle) + y_offset

            # 更新Canvas窗口位置
            self.table_canvas.coords(self.frame_windows[pos_name], x, y)
            self.table_canvas.itemconfigure(self.frame_windows[pos_name], anchor=anchor)

            # 确保框架在最上层显示
            self.table_canvas.tag_raise(self.frame_windows[pos_name])

    def start_new_round(self):
        """开始新一轮游戏"""
        self.current_stage = '底牌'
        self.community_cards = []
        self.community_entry.delete(0, tk.END)
        
        # 清空当前玩家的手牌输入框
        self.my_cards_entry.delete(0, tk.END)
        if hasattr(self, 'my_cards_label'):
            self.my_cards_label.config(text="")
        
        # 重置玩家输入（保留筹码量）
        for pos in self.player_positions:
            if pos != self.my_position and pos in self.player_entries:
                self.player_entries[pos].delete(0, tk.END)
            if pos in self.player_actions:
                self.player_actions[pos].set("等待")
            if pos in self.raise_entries:
                self.raise_entries[pos].delete(0, tk.END)
                self.raise_entries[pos].pack_forget()
        
        # 设置阶段按钮状态
        self.stage_buttons['翻牌']['state'] = 'normal'
        self.stage_buttons['转牌']['state'] = 'disabled'
        self.stage_buttons['河牌']['state'] = 'disabled'
        self.stage_label.config(text="当前阶段: 底牌")
        self.update_positions()

        # 添加操作提示
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END,
            "=== 新一轮开始 ===\n"
            "1. 请先确认您的位置是否正确\n"
            "2. 在我的手牌输入框中输入手牌(例如：AhKs)\n"  # 更新提示文本
            "3. 输入完手牌后可以计算初始胜率\n"
            "4. 准备好后点击'发翻牌'进入下一阶段\n"
            f"{'-'*30}\n")
        self.analysis_text.see(tk.END)

    def proceed_to_stage(self, stage):
        """推进到指定阶段"""
        self.current_stage = stage
        self.stage_label.config(text=f"当前阶段: {stage}")

        # 根据阶段激活后续按钮
        if stage == '翻牌':
            self.stage_buttons['转牌']['state'] = 'normal'
            # 添加翻牌阶段提示
            self.analysis_text.insert(tk.END,
                "\n=== 翻牌阶段 ===\n"
                "1. 在公共牌区域输入3张翻牌\n"
                "2. 输入格式：例如 AhKsQd\n"
                "3. 输入后点击'计算胜率'查看概率\n"
                "4. 准备好后点击'发转牌'进入下一阶段\n"
                f"{'-'*30}\n")
        elif stage == '转牌':
            self.stage_buttons['河牌']['state'] = 'normal'
            # 添加转牌阶段提示
            self.analysis_text.insert(tk.END,
                "\n=== 转牌阶段 ===\n"
                "1. 在原公共牌后添加1张转牌\n"
                "2. 现在应该有4张公共牌\n"
                "3. 输入后点击'计算胜率'查看概率\n"
                "4. 准备好后点击'发河牌'进入最后阶段\n"
                f"{'-'*30}\n")
        elif stage == '河牌':
            # 添加河牌阶段提示
            self.analysis_text.insert(tk.END,
                "\n=== 河牌阶段 ===\n"
                "1. 在原公共牌后添加最后1张河牌\n"
                "2. 现在应该有5张公共牌\n"
                "3. 输入后点击'计算胜率'查看最终概率\n"
                f"{'-'*30}\n")
        self.analysis_text.see(tk.END)

    def calculate_odds(self):
        """计算胜率"""
        try:
            # 使用当前玩家手牌输入框的值
            my_cards_str = self.my_cards_entry.get().strip()
            if len(my_cards_str) != 4:
                raise ValueError("请输入2张手牌，格式如：AhKs")
                
            # 解析公共牌
            community_str = self.community_entry.get().strip()
            
            # 根据当前阶段验证公共牌数量
            expected_cards = {
                '底牌': 0,
                '翻牌': 6,  # 3张牌 * 2字符
                '转牌': 8,  # 4张牌 * 2字符
                '河牌': 10  # 5张牌 * 2字符
            }
            
            if self.current_stage in expected_cards:
                expected_length = expected_cards[self.current_stage]
                if community_str and len(community_str) != expected_length:
                    raise ValueError(f"{self.current_stage}阶段应该输入{expected_length//2}张公共牌")
            
            community_cards = []
            if community_str:
                community_cards = [Card.new(community_str[i:i+2]) for i in range(0, len(community_str), 2)]

            # 验证手牌格式
            try:
                my_cards = [Card.new(my_cards_str[i:i+2]) for i in range(0, 4, 2)]
            except:
                raise ValueError("手牌格式错误，请使用正确的格式（如：AhKs）\n"
                               "第一个字符是牌面值：A、K、Q、J、T(10)、9-2\n"
                               "第二个字符是花色：h(红桃)、d(方块)、s(黑桃)、c(梅花)")

            # 验证是否有重复的牌
            all_cards = my_cards + community_cards
            if len(set(all_cards)) != len(all_cards):
                raise ValueError("存在重复的牌，请检查输入")

            # 剩余牌堆
            deck = self._generate_deck(all_cards)

            # 蒙特卡洛模拟
            iterations = 1000
            win_count = 0
            for _ in range(iterations):
                random.shuffle(deck)

                # 根据阶段处理未发牌
                if self.current_stage == '底牌':
                    opp_cards = deck[:2]
                    remaining_comm = deck[2:7]
                elif self.current_stage == '翻牌':
                    opp_cards = deck[:2]
                    remaining_comm = community_cards + deck[2:4]
                elif self.current_stage == '转牌':
                    opp_cards = deck[:2]
                    remaining_comm = community_cards + [deck[2]]
                else:  # 河牌
                    opp_cards = deck[:2]
                    remaining_comm = community_cards

                # 确保我们有完整的5张公共牌
                if len(community_cards) > 0:
                    full_comm = community_cards + remaining_comm[len(community_cards):]
                else:
                    full_comm = remaining_comm

                # 评估双方手牌
                my_rank = self.evaluator.evaluate(full_comm, my_cards)
                opp_rank = self.evaluator.evaluate(full_comm, opp_cards)

                if my_rank < opp_rank:
                    win_count += 1
                elif my_rank == opp_rank:
                    win_count += 0.5

            win_rate = win_count / iterations * 100
            self.analysis_text.insert(tk.END,
                f"\n=== 胜率计算结果 ===\n"
                f"当前阶段: {self.current_stage}\n"
                f"我的手牌: {my_cards_str}\n"
                f"公共牌: {community_str}\n"
                f"胜率: {win_rate:.1f}%\n"
                f"提示: 您可以继续进入下一阶段，或重新计算当前胜率\n"
                f"{'-'*30}\n")
            self.analysis_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("输入错误", str(e))

    def reset_game(self):
        """重置游戏状态"""
        self.current_level = 0
        self.current_stage = '未开始'
        self.update_blind_info()
        self.update_level_info()

        # 清空当前玩家的手牌输入框
        self.my_cards_entry.delete(0, tk.END)
        if hasattr(self, 'my_cards_label'):
            self.my_cards_label.config(text="")

        # 清空其他玩家的输入框
        for pos in self.player_positions:
            if pos != self.my_position and pos in self.player_entries:
                self.player_entries[pos].delete(0, tk.END)
            if pos in self.player_actions:
                self.player_actions[pos].set("等待")
            if pos in self.raise_entries:
                self.raise_entries[pos].delete(0, tk.END)
            if pos in self.player_chips:
                self.player_chips[pos].delete(0, tk.END)
                self.player_chips[pos].insert(0, str(self.tournament.starting_chips))

        self.community_entry.delete(0, tk.END)
        self.pot_entry.delete(0, tk.END)
        self.pot_entry.insert(0, "0")
        self.analysis_text.delete(1.0, tk.END)
        self.stage_label.config(text="当前阶段: 未开始")
        
        # 重置所有按钮状态
        for btn in self.stage_buttons.values():
            btn['state'] = 'normal'
        self.stage_buttons['翻牌']['state'] = 'disabled'
        self.stage_buttons['转牌']['state'] = 'disabled'
        self.stage_buttons['河牌']['state'] = 'disabled'
        
        # 添加重置提示
        self.analysis_text.insert(tk.END,
            "=== 游戏已重置 ===\n"
            "1. 所有数据已清空\n"
            "2. 盲注等级已重置为初始级别\n"
            "3. 点击'开始新一轮'开始新的一手牌\n"
            f"{'-'*30}\n")
        self.analysis_text.see(tk.END)

    def _generate_deck(self, exclude=[]):
        """生成排除已使用牌后的牌堆"""
        deck = []
        for rank in '23456789TJQKA':
            for suit in 'shdc':
                card = Card.new(rank + suit)
                if card not in exclude:
                    deck.append(card)
        return deck

    def analyze_decision(self):
        """分析当前局势并给出决策建议"""
        try:
            # 获取当前玩家手牌
            my_cards_str = self.my_cards_entry.get().strip()
            if not my_cards_str or len(my_cards_str) != 4:
                raise ValueError("请先输入您的手牌")

            # 获取公共牌
            community_str = self.community_entry.get().strip()
            
            # 解析手牌和公共牌
            my_cards = [Card.new(my_cards_str[i:i+2]) for i in range(0, 4, 2)]
            community_cards = [Card.new(community_str[i:i+2]) for i in range(0, len(community_str), 2)] if community_str else []

            # 收集对手行动信息
            active_opponents = []
            aggressive_actions = 0  # 记录加注次数
            for pos in self.player_positions:
                if pos != self.my_position:
                    action = self.player_actions[pos].get()
                    if action != "弃牌":
                        active_opponents.append(pos)
                        if action in ["加注", "allin"]:
                            aggressive_actions += 1

            # 计算当前胜率
            win_rate = self.calculate_win_rate(my_cards, community_cards, len(active_opponents))

            # 获取位置强度
            position_strength = self.get_position_strength(self.my_position)

            # 计算底池赔率
            pot_size = float(self.pot_entry.get() or 0)
            current_bet = max(float(entry.get() or 0) for entry in self.raise_entries.values() if entry.get())
            pot_odds = current_bet / (pot_size + current_bet) if current_bet > 0 else 0

            # 生成决策建议
            self.analysis_text.insert(tk.END, "\n=== 决策分析 ===\n")
            self.analysis_text.insert(tk.END, f"当前阶段: {self.current_stage}\n")
            self.analysis_text.insert(tk.END, f"手牌: {my_cards_str}\n")
            self.analysis_text.insert(tk.END, f"位置: {self.my_position}\n")
            self.analysis_text.insert(tk.END, f"胜率: {win_rate:.1f}%\n")
            self.analysis_text.insert(tk.END, f"还在参与的玩家数: {len(active_opponents)}\n")
            self.analysis_text.insert(tk.END, f"底池赔率: {pot_odds:.2f}\n")

            # 根据不同情况给出建议
            recommendation = self.get_decision_recommendation(
                win_rate, position_strength, pot_odds, 
                len(active_opponents), aggressive_actions, 
                self.current_stage
            )

            self.analysis_text.insert(tk.END, f"\n决策建议: {recommendation}\n")
            self.analysis_text.insert(tk.END, f"{'-'*30}\n")
            self.analysis_text.see(tk.END)

        except Exception as e:
            messagebox.showerror("分析错误", str(e))

    def calculate_win_rate(self, my_cards, community_cards, active_opponents):
        """计算当前胜率"""
        # 使用现有的calculate_odds逻辑，但返回胜率值
        deck = self._generate_deck(my_cards + community_cards)
        iterations = 1000
        win_count = 0

        for _ in range(iterations):
            random.shuffle(deck)
            remaining_comm = []
            
            # 根据当前阶段补齐公共牌
            if self.current_stage == '底牌':
                remaining_comm = deck[:5]
            elif self.current_stage == '翻牌':
                remaining_comm = community_cards + deck[:2]
            elif self.current_stage == '转牌':
                remaining_comm = community_cards + [deck[0]]
            else:  # 河牌
                remaining_comm = community_cards

            # 模拟对手手牌
            opponent_wins = 0
            for _ in range(active_opponents):
                opp_cards = deck[5:7]  # 使用剩余牌堆中的牌
                opp_rank = self.evaluator.evaluate(remaining_comm, opp_cards)
                my_rank = self.evaluator.evaluate(remaining_comm, my_cards)
                if my_rank < opp_rank:
                    opponent_wins += 1

            if opponent_wins == 0:
                win_count += 1
            elif opponent_wins == active_opponents:
                continue
            else:
                win_count += 0.5  # 平分底池情况

        return win_count / iterations * 100

    def get_preflop_hand_strength(self, cards_str):
        """评估翻牌前手牌强度"""
        # 解析手牌
        card1, card2 = cards_str[:2], cards_str[2:]
        rank1, suit1 = card1[0], card1[1]
        rank2, suit2 = card2[0], card2[1]
        suited = suit1 == suit2
        
        # 牌值映射
        rank_map = {'2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':11, 'Q':12, 'K':13, 'A':14}
        r1, r2 = rank_map[rank1], rank_map[rank2]
        high_rank, low_rank = max(r1, r2), min(r1, r2)
        
        # 基础分值（0-10）
        if r1 == r2:  # 对子
            return min(10, 5 + high_rank/2)  # AA=12, 22=6
        elif suited:  # 同花
            gap = high_rank - low_rank - 1
            return min(8, max(0, 4 + (high_rank/3) - gap/2))
        else:  # 杂色
            gap = high_rank - low_rank - 1
            return min(7, max(0, 3 + (high_rank/3) - gap/2))

    def get_decision_recommendation(self, win_rate, position_strength, pot_odds, 
                                  active_opponents, aggressive_actions, stage):
        """根据各种因素给出决策建议"""
        try:
            # 获取手牌
            my_cards_str = self.my_cards_entry.get().strip()
            
            # 计算筹码深度
            my_chips = float(self.player_chips[self.my_position].get())
            big_blind = self.tournament.blind_levels[self.current_level][1]
            stack_depth = my_chips / big_blind
            
            # 计算底池优势
            pot_size = float(self.pot_entry.get() or 0)
            current_bet = max(float(entry.get() or 0) for entry in self.raise_entries.values() if entry.get())
            
            if stage == '底牌':
                # 获取翻牌前手牌强度（0-10分）
                hand_strength = self.get_preflop_hand_strength(my_cards_str)
                
                # 基础评分（考虑更多因素）
                base_score = (
                    hand_strength * 0.4 +      # 手牌强度权重
                    position_strength * 0.3 +   # 位置权重
                    (10 - active_opponents) * 0.2 +  # 参与人数权重
                    (10 - aggressive_actions) * 0.1   # 激进行动权重
                )
                
                # 翻牌前策略
                if stack_depth < 15:  # 短筹码策略
                    if hand_strength > 8:  # 强牌（AA, KK, QQ, AK等）
                        return "All-in"
                    elif hand_strength > 6 and position_strength > 7:  # 中强牌在好位置
                        return "小注加注（2-3BB），有人加注则All-in"
                    else:
                        return "弃牌"
                else:  # 深筹码策略
                    if hand_strength > 8:  # 超强牌
                        return f"加注 3BB，有人3bet可以4bet"
                    elif hand_strength > 6:  # 强牌
                        return "加注 2.5BB，有人3bet则弃牌"
                    elif hand_strength > 4 and position_strength > 8:  # 中等牌在好位置
                        return "偷盲加注 2BB，有人3bet则弃牌"
                    elif self.my_position == '大盲位(BB)' and current_bet <= big_blind:
                        return "免费看翻牌"
                    else:
                        return "弃牌"
            else:
                # 翻牌后策略
                if win_rate > 80:  # 超强牌力
                    if aggressive_actions > 0:
                        return "加注底池1-1.5倍或All-in"
                    else:
                        return "价值加注底池2/3"
                elif win_rate > 60:  # 强牌
                    if pot_odds < win_rate/100:
                        if aggressive_actions > 1:
                            return "谨慎跟注，考虑弃牌"
                        else:
                            return "加注底池1/2到2/3"
                    else:
                        return "跟注"
                elif win_rate > 40:  # 中等牌力
                    if pot_odds < win_rate/150:  # 更严格的底池赔率要求
                        if position_strength > 7:
                            return "尝试偷池，加注底池1/3"
                        else:
                            return "跟注一轮，后续行动需谨慎"
                    else:
                        return "弃牌"
                else:  # 弱牌
                    if position_strength > 8 and aggressive_actions == 0:
                        return "可以尝试诈唬，加注底池1/2"
                    else:
                        return "弃牌"

            # 特殊情况建议
            recommendation = []
            if aggressive_actions > 1:
                recommendation.append("警告：多人加注，建议保守行动")
            if active_opponents > 3:
                recommendation.append("警告：多人底池，胜率显著降低")
            if stack_depth < 15:
                recommendation.append("警告：筹码较短，需要寻找All-in机会")
            if stage != '底牌' and win_rate > 70 and pot_size > my_chips * 0.3:
                recommendation.append("提示：考虑全押以最大化价值")
            
            return "\n".join(recommendation) if recommendation else "弃牌"

        except Exception as e:
            return "分析错误，请检查输入"

if __name__ == "__main__":
    app = PokerAssistant()
    app.root.mainloop()