# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。

import cv2
import numpy as np
import pyautogui
import pytesseract
import time
from typing import List, Tuple

# 设置 tesseract 路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class PokerBot:
    def __init__(self):
        # 游戏窗口区域
        self.game_region = None
        # 初始化 pyautogui 的安全设置
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 1.0
        # 设置图像匹配的置信度
        pyautogui.CONFIDENCE = 0.8
        # 定义卡牌区域（这些值需要根据实际游戏界面调整）
        self.hand_cards_region = None
        self.community_cards_region = None
        self.button_regions = {
            'fold': None,
            'call': None,
            'raise': None,
            'check': None
        }
        # 当前游戏状态
        self.current_state = {
            'hand_cards': [],
            'community_cards': [],
            'pot_size': 0,
            'my_chips': 0,
            'current_bet': 0
        }
        
    def locate_game_window(self):
        """定位游戏窗口"""
        try:
            # 等待用户将鼠标移动到游戏窗口左上角
            print("请在 3 秒内将鼠标移动到游戏窗口的左上角...")
            time.sleep(3)
            top_left = pyautogui.position()
            print(f"捕获到左上角坐标：{top_left}")
            
            print("请在 3 秒内将鼠标移动到游戏窗口的右下角...")
            time.sleep(3)
            bottom_right = pyautogui.position()
            print(f"捕获到右下角坐标：{bottom_right}")
            
            self.game_region = (
                top_left[0], top_left[1],
                bottom_right[0] - top_left[0],
                bottom_right[1] - top_left[1]
            )
            print(f"游戏窗口区域已设置为：{self.game_region}")
            
            # 设置关键区域
            self._setup_regions()
            
            # 验证窗口位置
            self._verify_window_position()
            return True
        except Exception as e:
            print(f"定位游戏窗口时出错：{e}")
            return False

    def _verify_window_position(self):
        """验证窗口位置是否正确"""
        print("\n验证窗口位置...")
        # 移动到窗口四个角落
        corners = [
            (self.game_region[0], self.game_region[1]),  # 左上
            (self.game_region[0] + self.game_region[2], self.game_region[1]),  # 右上
            (self.game_region[0], self.game_region[1] + self.game_region[3]),  # 左下
            (self.game_region[0] + self.game_region[2], self.game_region[1] + self.game_region[3])  # 右下
        ]
        
        for i, corner in enumerate(['左上', '右上', '左下', '右下']):
            print(f"移动到{corner}角: {corners[i]}")
            pyautogui.moveTo(corners[i][0], corners[i][1], duration=1)
            time.sleep(0.5)

    def _setup_regions(self):
        """设置游戏中各个关键区域的位置"""
        window_width = self.game_region[2]
        window_height = self.game_region[3]
        
        print(f"窗口大小：宽度={window_width}, 高度={window_height}")
        
        # 手牌区域 - 在底部中间
        self.hand_cards_region = (
            int(window_width * 0.45),  # x 起始位置
            int(window_height * 0.65),  # y 起始位置
            int(window_width * 0.15),   # 宽度
            int(window_height * 0.15)   # 高度
        )
        
        # 公共牌区域 - 在桌子中间
        self.community_cards_region = (
            int(window_width * 0.35),
            int(window_height * 0.35),
            int(window_width * 0.3),
            int(window_height * 0.15)
        )
        
        # 按钮区域 - 底部的操作按钮
        button_height = 35  # 调整按钮高度
        button_y = window_height - 60  # 距离底部距离
        
        # 定义按钮区域（根据实际游戏界面调整）
        self.button_regions = {
            'fold': (int(window_width * 0.85), button_y, 80, button_height),  # 弃牌在右下角
            'call': (int(window_width * 0.45), button_y, 80, button_height),  # 跟注
            'raise': (int(window_width * 0.75), button_y, 80, button_height), # 加注
            'check': (int(window_width * 0.45), button_y, 80, button_height)  # 过牌（与跟注位置相同）
        }
        
        print("\n按钮区域设置如下：")
        for button, region in self.button_regions.items():
            abs_x = self.game_region[0] + region[0] + region[2]//2
            abs_y = self.game_region[1] + region[1] + region[3]//2
            print(f"{button}: 相对区域={region}, 绝对点击位置=({abs_x}, {abs_y})")

    def capture_screen(self) -> np.ndarray:
        """捕获游戏窗口的截图"""
        if self.game_region is None:
            raise ValueError("游戏窗口区域未设置")
        screenshot = pyautogui.screenshot(region=self.game_region)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def recognize_cards(self, image: np.ndarray, region: Tuple[int, int, int, int]) -> List[str]:
        """识别图像中的扑克牌"""
        # 截取指定区域
        x, y, w, h = region
        card_area = image[y:y+h, x:x+w]
        
        # 转换为灰度图
        gray = cv2.cvtColor(card_area, cv2.COLOR_BGR2GRAY)
        
        # 二值化处理
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # 使用OCR识别文字
        text = pytesseract.image_to_string(binary, config='--psm 11')
        
        # 解析识别出的文字，转换为扑克牌格式
        # 这里需要根据实际识别效果调整解析逻辑
        cards = []
        # TODO: 解析逻辑
        return cards

    def get_game_state(self) -> dict:
        """获取当前游戏状态"""
        screen = self.capture_screen()
        
        # 识别手牌
        self.current_state['hand_cards'] = self.recognize_cards(
            screen, self.hand_cards_region
        )
        
        # 识别公共牌
        self.current_state['community_cards'] = self.recognize_cards(
            screen, self.community_cards_region
        )
        
        # TODO: 识别筹码和下注金额
        
        print(f"当前游戏状态：{self.current_state}")
        return self.current_state

    def make_decision(self) -> str:
        """基于当前游戏状态做出决策"""
        state = self.current_state
        
        # 测试阶段，我们先使用一个简单的决策逻辑
        actions = ['fold', 'call', 'raise']
        action = actions[0]  # 先总是选择 fold 用于测试
        
        print(f"做出决策：{action}")
        return action

    def perform_action(self, action: str):
        """执行决策动作"""
        try:
            print(f"\n执行{action}操作:")
            
            # 根据不同操作使用对应的按钮图片
            button_images = {
                'fold': ['fold_button.png'],
                'call': ['call_button.png'],
                'raise': ['raise_button.png'],
                'check': ['check_button.png', 'call_button.png']  # 过牌可能显示为check或call
            }
            
            # 获取当前操作可能的按钮图片
            possible_images = button_images.get(action, [f"{action}_button.png"])
            button_location = None
            matched_image = None
            
            # 计算按钮可能出现的区域
            window_width = self.game_region[2]
            window_height = self.game_region[3]
            
            # 根据不同按钮类型限定搜索区域
            if action == 'fold':
                # 弃牌按钮通常在右下
                search_region = (
                    self.game_region[0] + int(window_width * 0.7),  # x起点
                    self.game_region[1] + int(window_height * 0.8),  # y起点
                    int(window_width * 0.3),  # 宽度
                    int(window_height * 0.2)   # 高度
                )
            elif action == 'check':
                # 过牌按钮通常在中下
                search_region = (
                    self.game_region[0] + int(window_width * 0.3),  # x起点
                    self.game_region[1] + int(window_height * 0.8),  # y起点
                    int(window_width * 0.4),  # 宽度
                    int(window_height * 0.2)   # 高度
                )
            else:
                # 其他按钮搜索整个底部区域
                search_region = (
                    self.game_region[0],  # x起点
                    self.game_region[1] + int(window_height * 0.8),  # y起点
                    window_width,  # 宽度
                    int(window_height * 0.2)   # 高度
                )
            
            print(f"在区域 {search_region} 中搜索按钮")
            
            # 尝试所有可能的按钮图片
            for button_image in possible_images:
                print(f"尝试查找按钮图片: {button_image}")
                try:
                    # 提高置信度，使匹配更严格
                    confidence = 0.9 if action == 'check' else 0.8
                    
                    # 限制在特定区域内查找
                    button_location = pyautogui.locateCenterOnScreen(
                        button_image,
                        confidence=confidence,
                        region=search_region
                    )
                    
                    if button_location is not None:
                        print(f"找到按钮图片: {button_image}")
                        matched_image = button_image
                        break
                except Exception as e:
                    print(f"查找图片 {button_image} 时出错: {e}")
            
            if button_location is None:
                print(f"未找到{action}按钮")
                return
                
            print(f"找到按钮位置：{button_location}")
            print(f"使用的图片：{matched_image}")
            
            # 再次验证位置是否合理
            if action == 'check' and button_location.x > self.game_region[0] + window_width * 0.7:
                print("警告：检测到的过牌按钮位置不合理，可能是误判")
                return
            
            # 移动到按钮位置
            print("移动鼠标到按钮位置...")
            pyautogui.moveTo(button_location.x, button_location.y, duration=1)
            time.sleep(0.5)
            
            # 获取当前鼠标位置进行验证
            current_pos = pyautogui.position()
            print(f"当前鼠标位置：{current_pos}")
            
            # 再次验证当前位置的按钮（使用更大的验证区域）
            verify_region = (
                current_pos.x - 50,  # 扩大验证区域
                current_pos.y - 50,
                100,  # 验证区域大小为 100x100 像素
                100
            )
            
            try:
                verify_location = pyautogui.locateCenterOnScreen(
                    matched_image,
                    confidence=confidence,
                    region=verify_region
                )
                
                if verify_location is None:
                    print("警告：鼠标移动后未能再次确认按钮位置，操作取消")
                    return
                    
                # 执行点击
                print("准备点击...")
                pyautogui.click()
                print(f"点击完成：{action}")
                
            except Exception as e:
                print(f"验证按钮位置时出错：{e}")
                return
            
            # 移动鼠标到安全位置
            safe_x = self.game_region[0] + self.game_region[2] // 2
            safe_y = self.game_region[1] + self.game_region[3] // 2
            pyautogui.moveTo(safe_x, safe_y, duration=0.5)
            
        except Exception as e:
            print(f"执行点击操作时出错：{e}")
        
        time.sleep(1)  # 等待动作执行完成

    def run(self):
        """运行扑克机器人"""
        if not self.locate_game_window():
            print("无法定位游戏窗口，程序退出")
            return

        print("\n机器人开始运行...")
        try:
            while True:
                print("\n=== 新的回合开始 ===")
                print("按 'f' 键执行弃牌")
                print("按 'c' 键执行跟注")
                print("按 'r' 键执行加注")
                print("按 'k' 键执行过牌")
                print("按 'q' 键退出程序")
                
                # 等待用户按键
                key = input("请按键选择操作: ").lower()
                
                if key == 'q':
                    print("程序退出")
                    break
                    
                # 根据按键选择动作
                action_map = {
                    'f': 'fold',
                    'c': 'call',
                    'r': 'raise',
                    'k': 'check'
                }
                
                if key in action_map:
                    action = action_map[key]
                    print(f"执行操作：{action}")
                    self.perform_action(action)
                else:
                    print("无效的按键，请重试")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("程序已停止")

if __name__ == "__main__":
    bot = PokerBot()
    bot.run()

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
