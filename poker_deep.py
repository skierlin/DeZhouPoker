import tkinter as tk
from tkinter import ttk, messagebox
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
        self.root.geometry("1200x900")  # 增加窗口大小

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

        self.setup_gui()

    def setup_gui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 创建左右分栏
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # 创建比赛信息框架 (放在左边)
        info_frame = ttk.LabelFrame(left_frame, text="比赛信息")
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        # 添加位置选择
        position_frame = ttk.Frame(info_frame)
        position_frame.pack(fill=tk.X, pady=2)
        ttk.Label(position_frame, text="我的位置:").pack(side=tk.LEFT)
        self.my_position_var = tk.StringVar(value=self.my_position)
        position_menu = ttk.OptionMenu(position_frame, self.my_position_var,
                                     self.my_position, *self.player_positions,
                                     command=self.on_position_change)
        position_menu.pack(side=tk.LEFT, padx=5)

        # 添加比赛信息（使用变量以便更新）
        self.blind_info_var = tk.StringVar()
        self.update_blind_info()
        self.blind_label = ttk.Label(info_frame, textvariable=self.blind_info_var)
        self.blind_label.pack(pady=2)

        # 添加当前级别显示
        self.level_var = tk.StringVar()
        self.update_level_info()
        self.level_label = ttk.Label(info_frame, textvariable=self.level_var)
        self.level_label.pack(pady=2)

        # 添加底池输入
        pot_frame = ttk.Frame(info_frame)
        pot_frame.pack(fill=tk.X, pady=2)
        ttk.Label(pot_frame, text="当前底池:").pack(side=tk.LEFT)
        self.pot_entry = ttk.Entry(pot_frame, width=10)
        self.pot_entry.pack(side=tk.LEFT, padx=5)
        self.pot_entry.insert(0, "0")

        # 创建牌桌框架 (放在左边)
        table_frame = ttk.Frame(left_frame)
        table_frame.pack(expand=True, fill=tk.BOTH)

        # 创建Canvas
        self.table_canvas = tk.Canvas(table_frame, width=800, height=600, bg='#1a472a')  # 增加画布高度
        self.table_canvas.pack(expand=True)

        # 画椭圆形牌桌
        self.table_canvas.create_oval(50, 50, 750, 550, fill='#2d5a3f', outline='#1e5631', width=3)  # 调整椭圆大小

        # 在中间显示公共牌区域
        community_frame = ttk.Frame(self.table_canvas)
        self.table_canvas.create_window(400, 300, window=community_frame)
        ttk.Label(community_frame, text="公共牌").pack()
        self.community_entry = ttk.Entry(community_frame, width=20)
        self.community_entry.pack()

        # 创建玩家位置框架
        self.frame_windows = {}  # 存储canvas window的ID
        for pos in self.player_positions:
            player_frame = ttk.Frame(self.table_canvas)
            self.player_frames[pos] = player_frame

            # 添加位置标签
            ttk.Label(player_frame, text=pos).pack()

            # 添加手牌输入框
            entry = ttk.Entry(player_frame, width=8)
            entry.pack()
            self.player_entries[pos] = entry

            # 添加筹码输入框
            chips_frame = ttk.Frame(player_frame)
            chips_frame.pack()
            ttk.Label(chips_frame, text="筹码:").pack(side=tk.LEFT)
            chips_entry = ttk.Entry(chips_frame, width=8)
            chips_entry.pack(side=tk.LEFT)
            chips_entry.insert(0, str(self.tournament.starting_chips))
            self.player_chips[pos] = chips_entry

            # 添加操作选择和加注金额输入框
            action_frame = ttk.Frame(player_frame)
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

            action_menu = ttk.OptionMenu(action_frame, action_var, "等待",
                                       "弃牌", "跟注", "加注", "allin",
                                       command=lambda *args, p=pos: on_action_change(p, *args))
            action_menu.pack(side=tk.LEFT)

            # 创建加注金额输入框（初始隐藏）
            raise_entry = ttk.Entry(action_frame, width=8)
            self.raise_entries[pos] = raise_entry

            # 创建window，但先不指定位置
            window_id = self.table_canvas.create_window(0, 0, window=player_frame)
            self.frame_windows[pos] = window_id

        # 初始化位置
        self.update_positions()

        # 创建控制面板和分析结果区域 (放在右边)
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # 添加比赛阶段控制
        stage_frame = ttk.LabelFrame(right_frame, text="比赛阶段")
        stage_frame.pack(fill=tk.X, pady=5)

        # 添加阶段控制按钮
        self.stage_buttons = {}
        self.stage_buttons['开始新一轮'] = ttk.Button(stage_frame, text="开始新一轮",
                                                command=self.start_new_round)
        self.stage_buttons['开始新一轮'].pack(side=tk.LEFT, padx=5, pady=5)

        self.stage_buttons['翻牌'] = ttk.Button(stage_frame, text="发翻牌",
                                             command=lambda: self.proceed_to_stage('翻牌'))
        self.stage_buttons['翻牌'].pack(side=tk.LEFT, padx=5, pady=5)
        self.stage_buttons['翻牌']['state'] = 'disabled'

        self.stage_buttons['转牌'] = ttk.Button(stage_frame, text="发转牌",
                                             command=lambda: self.proceed_to_stage('转牌'))
        self.stage_buttons['转牌'].pack(side=tk.LEFT, padx=5, pady=5)
        self.stage_buttons['转牌']['state'] = 'disabled'

        self.stage_buttons['河牌'] = ttk.Button(stage_frame, text="发河牌",
                                             command=lambda: self.proceed_to_stage('河牌'))
        self.stage_buttons['河牌'].pack(side=tk.LEFT, padx=5, pady=5)
        self.stage_buttons['河牌']['state'] = 'disabled'

        # 添加当前阶段显示
        self.stage_label = ttk.Label(stage_frame, text="当前阶段: 未开始")
        self.stage_label.pack(side=tk.LEFT, padx=20, pady=5)

        # 添加说明标签
        ttk.Label(control_frame,
                 text="输入格式说明：手牌和公共牌都使用两个字符表示一张牌\n"
                      "第一个字符是牌面值：A（A），K（K），Q（Q），J（J），T（10），9-2，使用大写字母\n"
                      "第二个字符是花色：h（红桃），d（方块），s（黑桃），c（梅花），使用小写字母\n"
                      "例如：AhKs 表示红桃A和黑桃K").pack(pady=5)

        # 添加按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="计算胜率",
                  command=self.calculate_odds).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空",
                  command=self.reset_game).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="下一级盲注",
                  command=self.increase_blind_level).pack(side=tk.LEFT, padx=5)

        # 添加分析结果显示区域
        result_frame = ttk.LabelFrame(right_frame, text="分析结果")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.analysis_text = tk.Text(result_frame, height=30, width=50)  # 增加文本框大小
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
        """获取位置强度评分（1-10）"""
        position_scores = {
            '大盲位(BB)': 3,
            '枪口位(UTG)': 5,
            '枪口+1(UTG+1)': 5,
            '枪口+2(UTG+2)': 6,
            '中间位(MP)': 7,
            '中间位+1(MP+1)': 8,
            '切位(CO)': 10,
            '庄家位(BTN)': 9,
            '小盲位(SB)': 4
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
        self.my_position = new_position
        self.update_positions()

    def update_positions(self):
        """更新玩家位置在牌桌上的布局（圆形布局）"""
        positions = list(self.position_numbers.keys())
        center_x, center_y = 400, 300  # 牌桌中心坐标
        radius = 250  # 布局半径
        angle_step = 360 / len(positions)

        # 根据当前用户位置调整起始角度（让用户位置在底部）
        my_pos_number = self.position_to_number[self.my_position]
        start_angle = 270 - (my_pos_number-1)*angle_step

        for pos_name in self.player_positions:
            pos_number = self.position_to_number[pos_name]
            # 计算角度（逆时针布局）
            angle = math.radians(start_angle + (pos_number-1)*angle_step)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            # 调整位置框的锚点方向
            if 135 < angle < 225:
                anchor = tk.S
            elif 225 <= angle < 315:
                anchor = tk.W
            else:
                anchor = tk.N

            # 更新Canvas窗口位置
            self.table_canvas.coords(self.frame_windows[pos_name], x, y)
            self.table_canvas.itemconfigure(self.frame_windows[pos_name], anchor=anchor)

    def start_new_round(self):
        """开始新一轮游戏"""
        self.current_stage = '底牌'
        self.community_cards = []
        self.community_entry.delete(0, tk.END)
        
        # 重置玩家输入（保留筹码量）
        for pos in self.player_positions:
            self.player_entries[pos].delete(0, tk.END)
            self.player_actions[pos].set("等待")
            self.raise_entries[pos].delete(0, tk.END)
            self.raise_entries[pos].pack_forget()
        
        # 修复点：正确设置阶段按钮状态
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
            "2. 在您的位置框中输入手牌(例如：AhKs)\n"
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
            # 解析用户手牌
            my_pos = self.my_position
            my_cards_str = self.player_entries[my_pos].get().strip()
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

        for pos in self.player_positions:
            self.player_entries[pos].delete(0, tk.END)
            self.player_actions[pos].set("等待")
            self.raise_entries[pos].delete(0, tk.END)
            self.player_chips[pos].delete(0, tk.END)
            self.player_chips[pos].insert(0, str(self.tournament.starting_chips))

        self.community_entry.delete(0, tk.END)
        self.pot_entry.delete(0, tk.END)
        self.pot_entry.insert(0, "0")
        self.analysis_text.delete(1.0, tk.END)
        self.stage_label.config(text="当前阶段: 未开始")
        
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

if __name__ == "__main__":
    app = PokerAssistant()
    app.root.mainloop()