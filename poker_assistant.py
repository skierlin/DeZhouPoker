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
        total_strength = (strength_score * 0.7 + position_strength * 0.3)
        bb_size = current_blind[1]
        stack_bb = stack / bb_size
        pot_bb = pot_size / bb_size

        if total_strength >= 8:  # 非常强的牌
            if stack_bb > 50:
                return "建议加注至底池的3倍"
            else:
                return "建议全压"
        elif total_strength >= 6:  # 强牌
            if pot_bb == 1:  # 没人加注
                return "建议加注至底池的2.5倍"
            elif pot_bb < 10:  # 有人小加注
                return "建议跟注或3bet至底池的3倍"
            else:  # 有人大加注
                return "建议弃牌，保留筹码等待更好机会"
        elif total_strength >= 4:  # 中等强度
            if position_strength >= 8 and pot_bb <= 2:  # 后位且没人大加注
                return "建议偷盲，加注至底池的2倍"
            else:
                return "建议弃牌"
        else:  # 弱牌
            if position == "大盲位(BB)" and pot_bb <= 2:
                return "可以考虑防守性跟注"
            else:
                return "建议弃牌"

    def calculate_odds(self):
        try:
            # 如果还没开始，直接返回
            if self.current_stage == '未开始':
                return

            # 获取当前底池
            try:
                self.pot_size = int(self.pot_entry.get())
            except:
                messagebox.showerror("错误", "请输入有效的底池大小！")
                return

            # 获取公共牌
            community_str = self.community_entry.get().strip()
            self.community_cards = self.parse_cards(community_str)

            # 根据当前阶段验证公共牌数量
            if self.current_stage != '底牌':  # 底牌阶段不需要公共牌
                if self.community_cards is None:
                    messagebox.showerror("错误", "公共牌格式错误！")
                    return

                community_cards_count = len(self.community_cards)
                expected_counts = {'底牌': 0, '翻牌': 3, '转牌': 4, '河牌': 5}
                expected_count = expected_counts.get(self.current_stage, 0)

                if community_cards_count > expected_count:
                    messagebox.showerror("错误", f"{self.current_stage}阶段最多只能有{expected_count}张公共牌！")
                    return
                elif community_cards_count < expected_count:
                    messagebox.showerror("错误", f"{self.current_stage}阶段需要{expected_count}张公共牌！")
                    return

            # 获取玩家手牌
            active_players = {}
            used_cards = set()
            player_stacks = {}

            # 验证公共牌
            for card in self.community_cards:
                card_str = Card.int_to_str(card)
                if card_str in used_cards:
                    messagebox.showerror("错误", f"发现重复的牌: {card_str}")
                    return
                used_cards.add(card_str)

            # 验证并收集玩家手牌和筹码
            for pos, entry in self.player_entries.items():
                cards_str = entry.get().strip()
                if not cards_str and pos == self.my_position:
                    messagebox.showerror("错误", "请输入您的手牌！")
                    return

                if cards_str:  # 只处理有输入手牌的位置
                    try:
                        chips = int(self.player_chips[pos].get())
                        if chips <= 0:  # 跳过出局玩家
                            continue
                    except:
                        messagebox.showerror("错误", f"{pos}的筹码输入无效！")
                        return

                    hole_cards = self.parse_cards(cards_str)
                    if hole_cards is None:
                        messagebox.showerror("错误", f"{pos}的手牌格式错误！")
                        return
                    if len(hole_cards) != 2:
                        messagebox.showerror("错误", f"{pos}必须输入两张手牌！")
                        return

                    # 检查重复牌
                    for card in hole_cards:
                        card_str = Card.int_to_str(card)
                        if card_str in used_cards:
                            messagebox.showerror("错误", f"发现重复的牌: {card_str}")
                            return
                        used_cards.add(card_str)

                    active_players[pos] = hole_cards
                    player_stacks[pos] = chips

            if not active_players:
                messagebox.showerror("错误", "请至少输入一位在场玩家的手牌！")
                return

            # 计算胜率和建议
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(tk.END, "分析结果：\n\n")

            # 获取当前盲注
            current_blind = self.tournament.blind_levels[self.current_level]

            # 计算每个玩家的当前牌力和建议
            for pos, hole_cards in active_players.items():
                hand_strength = self.get_hand_strength(hole_cards, self.community_cards)
                position_strength = self.get_position_strength(pos)

                # 获取建议
                recommendation = self.get_action_recommendation(
                    pos, hand_strength, position_strength,
                    player_stacks[pos], self.pot_size, current_blind
                )

                # 显示结果
                self.analysis_text.insert(tk.END, f"位置: {pos}\n")
                # 显示手牌
                hand_cards = ' '.join(Card.int_to_pretty_str(card) for card in hole_cards)
                self.analysis_text.insert(tk.END, f"手牌: {hand_cards}\n")
                action = self.player_actions[pos].get()
                action_text = action
                if action == "加注":
                    raise_amount = self.raise_entries[pos].get().strip()
                    if raise_amount:
                        action_text = f"加注 {raise_amount}"
                self.analysis_text.insert(tk.END, f"当前操作: {action_text}\n")
                score = max(0, min((7462 - hand_strength) / 7462 * 10, 10))
                self.analysis_text.insert(tk.END, f"手牌强度评分: {score:.1f}/10\n")
                self.analysis_text.insert(tk.END, f"位置优势: {position_strength}/10\n")
                self.analysis_text.insert(tk.END, f"建议: {recommendation}\n\n")

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def parse_cards(self, card_str):
        """解析卡牌字符串，返回treys的卡牌整数列表"""
        if not card_str:
            return []
        try:
            cards = []
            # 移除空格
            card_str = card_str.replace(" ", "")

            # 检查输入长度是否为偶数
            if len(card_str) % 2 != 0:
                print(f"输入不完整: {card_str}")
                return None

            # 将输入字符串按每两个字符分割为单个牌面
            card_list = [card_str[i:i+2] for i in range(0, len(card_str), 2)]

            for c_str in card_list:
                if len(c_str) != 2:
                    print(f"输入不完整: {c_str}")
                    return None

                rank = c_str[0].upper()  # 保持牌面值为大写字母
                suit = c_str[1].lower()  # 将花色转换为小写字母

                # 验证牌面值
                if rank not in 'AKQJT98765432':
                    print(f"无效的牌面值: {rank}")
                    return None

                # 验证花色
                if suit not in 'hdsc':
                    print(f"无效的花色: {suit}")
                    return None

                # 创建Card整数
                try:
                    card_str_formatted = rank + suit
                    card_int = Card.new(card_str_formatted)
                    cards.append(card_int)
                except Exception as e:
                    print(f"创建卡牌对象失败: {card_str_formatted}, 错误: {str(e)}")
                    return None

            return cards
        except Exception as e:
            print(f"解析错误: {str(e)}")
            return None

    def reset_game(self):
        # 清空所有输入
        for entry in self.player_entries.values():
            entry.delete(0, tk.END)
        self.community_entry.delete(0, tk.END)
        self.analysis_text.delete(1.0, tk.END)
        # 重置所有操作选择和加注金额
        for pos in self.player_positions:
            self.player_actions[pos].set("等待")
            self.raise_entries[pos].delete(0, tk.END)
            self.raise_entries[pos].pack_forget()
        # 重置筹码为起始值
        for chips_entry in self.player_chips.values():
            chips_entry.delete(0, tk.END)
            chips_entry.insert(0, str(self.tournament.starting_chips))
        # 重置底池
        self.pot_entry.delete(0, tk.END)
        self.pot_entry.insert(0, "0")

    def on_position_change(self, *args):
        """当选择新的位置时触发"""
        self.my_position = self.my_position_var.get()
        self.update_positions()

    def get_adjusted_positions(self):
        """根据当前位置获取调整后的位置列表"""
        # 获取当前位置的编号
        current_number = self.position_to_number[self.my_position]

        # 创建一个从当前位置开始的位置列表
        adjusted_positions = []
        for i in range(9):
            # 计算实际位置编号（1-9之间循环）
            position_number = ((current_number - 1 + i) % 9) + 1
            adjusted_positions.append(self.position_numbers[position_number])

        return adjusted_positions

    def update_positions(self):
        """更新所有位置的显示"""
        positions = self.get_adjusted_positions()

        # 计算9个位置的坐标
        center_x, center_y = 400, 300  # 调整中心点位置
        radius_x, radius_y = 350, 200  # 增加半径

        # 计算位置，底部中间为0度，顺时针排列
        angles = []
        for i in range(9):
            if i == 0:  # 底部中间（我的位置）
                angle = math.pi / 2
            elif i <= 4:  # 左半边（顺时针方向的后面位置）
                angle = math.pi / 2 + (i * math.pi / 5)
            else:  # 右半边（顺时针方向的前面位置）
                angle = math.pi / 2 - ((9 - i) * math.pi / 5)
            angles.append(angle)

        # 更新每个位置的框架
        for i, pos in enumerate(positions):
            frame = self.player_frames[pos]
            x = center_x + radius_x * math.cos(angles[i])
            y = center_y + radius_y * math.sin(angles[i])
            self.table_canvas.coords(self.frame_windows[pos], x, y)

            # 检查玩家是否出局（筹码为0）
            try:
                chips = int(self.player_chips[pos].get())
                is_active = chips > 0
            except:
                is_active = True  # 如果无法读取筹码，默认玩家在场

            # 更新位置标签，显示编号和位置名称，出局玩家显示灰色
            position_number = self.position_to_number[pos]
            for child in frame.winfo_children():
                if isinstance(child, ttk.Label) and child.cget("text").endswith(pos):
                    text = f"{position_number}号位: {pos}"
                    if not is_active:
                        text += " (出局)"
                    child.configure(text=text)
                    # 如果玩家出局，禁用所有输入
                    if not is_active:
                        for widget in frame.winfo_children():
                            if isinstance(widget, (ttk.Entry, ttk.OptionMenu)):
                                widget.configure(state='disabled')
                    else:
                        for widget in frame.winfo_children():
                            if isinstance(widget, (ttk.Entry, ttk.OptionMenu)):
                                widget.configure(state='normal')
                    break

    def start_new_round(self):
        """开始新的一轮"""
        self.current_stage = '底牌'
        self.stage_label.config(text=f"当前阶段: {self.current_stage}")

        # 清空公共牌
        self.community_entry.delete(0, tk.END)
        self.community_entry.config(state='disabled')

        # 启用翻牌按钮，禁用其他阶段按钮
        self.stage_buttons['翻牌']['state'] = 'normal'
        self.stage_buttons['转牌']['state'] = 'disabled'
        self.stage_buttons['河牌']['state'] = 'disabled'

        # 清空分析结果
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "新的一轮开始，请输入玩家手牌...\n")

        # 自动计算初始底池（大小盲注之和）
        current_blind = self.tournament.blind_levels[self.current_level]
        initial_pot = current_blind[0] + current_blind[1]  # 小盲 + 大盲
        self.pot_entry.delete(0, tk.END)
        self.pot_entry.insert(0, str(initial_pot))

    def proceed_to_stage(self, stage):
        """进入指定的比赛阶段"""
        self.current_stage = stage
        self.stage_label.config(text=f"当前阶段: {self.current_stage}")

        # 启用公共牌输入
        self.community_entry.config(state='normal')

        # 根据阶段设置按钮状态
        if stage == '翻牌':
            self.stage_buttons['翻牌']['state'] = 'disabled'
            self.stage_buttons['转牌']['state'] = 'normal'
            self.analysis_text.insert(tk.END, "\n进入翻牌圈，请输入三张公共牌...\n")
        elif stage == '转牌':
            self.stage_buttons['转牌']['state'] = 'disabled'
            self.stage_buttons['河牌']['state'] = 'normal'
            self.analysis_text.insert(tk.END, "\n进入转牌圈，请输入第四张公共牌...\n")
        elif stage == '河牌':
            self.stage_buttons['河牌']['state'] = 'disabled'
            self.analysis_text.insert(tk.END, "\n进入河牌圈，请输入第五张公共牌...\n")

        # 自动计算胜率
        self.calculate_odds()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = PokerAssistant()
    app.run()
