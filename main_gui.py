import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from strategy_optimizer import StrategyOptimizer

class PokerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Poker Strategy Optimizer")

        self.optimizer = StrategyOptimizer('Texas_Holdem/poker_games_detailed2.csv')
        self.optimizer.optimize_strategy()

        # 設置主框架
        main_frame = ttk.Frame(master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 標題標籤
        self.label = ttk.Label(main_frame, text="Enter Position, Hand, Community Cards, and Funds:", font=("Helvetica", 16))
        self.label.grid(row=0, column=0, columnspan=3, pady=10)

        # 添加小標題
        self.blind_label = ttk.Label(main_frame, text="Big Blind: $20  |  Small Blind: $10", font=("Helvetica", 12), anchor=tk.CENTER)
        self.blind_label.grid(row=1, column=0, columnspan=3, pady=5)

        # 添加資金輸入框
        self.initial_funds_label = ttk.Label(main_frame, text="Initial Funds:", font=("Helvetica", 12))
        self.initial_funds_label.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.initial_funds_var = tk.StringVar(master, value="1000")
        self.initial_funds_entry = ttk.Entry(main_frame, textvariable=self.initial_funds_var)
        self.initial_funds_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.remaining_funds_label = ttk.Label(main_frame, text="Remaining Funds:", font=("Helvetica", 12))
        self.remaining_funds_label.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.remaining_funds_var = tk.StringVar(master, value="1000")
        self.remaining_funds_entry = ttk.Entry(main_frame, textvariable=self.remaining_funds_var)
        self.remaining_funds_entry.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 添加底池大小輸入框
        self.pot_size_label = ttk.Label(main_frame, text="Pot Size:", font=("Helvetica", 12))
        self.pot_size_label.grid(row=5, column=0, sticky=tk.W, pady=5)
        self.pot_size_var = tk.StringVar(master, value="30")
        self.pot_size_entry = ttk.Entry(main_frame, textvariable=self.pot_size_var)
        self.pot_size_entry.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 添加位置選單
        self.position_label = ttk.Label(main_frame, text="Position:", font=("Helvetica", 12))
        self.position_label.grid(row=6, column=0, sticky=tk.W, pady=5)
        self.positions = ['Button', 'Small Blind', 'Big Blind', 'UTG', 'HighJack', 'CutOff']
        self.position_var = tk.StringVar(master)
        self.position_var.set("")  # 預設值
        self.position_menu = ttk.OptionMenu(main_frame, self.position_var, "", *self.positions)
        self.position_menu.grid(row=6, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 定義rank和suit
        self.ranks = ['','2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.suits = ['','Hearts', 'Diamonds', 'Clubs', 'Spades']

        self.hand_labels = []
        self.rank_vars = []
        self.suit_vars = []

        # 創建選單來選擇每張手牌
        for i in range(2):
            hand_label = ttk.Label(main_frame, text=f"Card {i + 1}:", font=("Helvetica", 12))
            hand_label.grid(row=i + 7, column=0, sticky=tk.W, pady=5)
            self.hand_labels.append(hand_label)

            rank_var = tk.StringVar(master)
            rank_var.set("")  # 預設值
            rank_menu = ttk.OptionMenu(main_frame, rank_var, "", *self.ranks)
            rank_menu.grid(row=i + 7, column=1, sticky=(tk.W, tk.E), pady=5)
            self.rank_vars.append(rank_var)

            suit_var = tk.StringVar(master)
            suit_var.set("")  # 預設值
            suit_menu = ttk.OptionMenu(main_frame, suit_var, "", *self.suits)
            suit_menu.grid(row=i + 7, column=2, sticky=(tk.W, tk.E), pady=5)
            self.suit_vars.append(suit_var)

        # 創建選單來選擇桌面的每張牌
        self.community_labels = []
        self.community_rank_vars = []
        self.community_suit_vars = []

        for i in range(5):
            community_label = ttk.Label(main_frame, text=f"Community Card {i + 1}:", font=("Helvetica", 12))
            community_label.grid(row=i + 9, column=0, sticky=tk.W, pady=5)
            self.community_labels.append(community_label)

            community_rank_var = tk.StringVar(master)
            community_rank_var.set("")  # 預設值
            community_rank_menu = ttk.OptionMenu(main_frame, community_rank_var, "", *self.ranks)
            community_rank_menu.grid(row=i + 9, column=1, sticky=(tk.W, tk.E), pady=5)
            self.community_rank_vars.append(community_rank_var)

            community_suit_var = tk.StringVar(master)
            community_suit_var.set("")  # 預設值
            community_suit_menu = ttk.OptionMenu(main_frame, community_suit_var, "", *self.suits)
            community_suit_menu.grid(row=i + 9, column=2, sticky=(tk.W, tk.E), pady=5)
            self.community_suit_vars.append(community_suit_var)

        # 添加推薦動作按鈕
        self.recommend_button = ttk.Button(main_frame, text="Recommend Action", command=self.recommend_action)
        self.recommend_button.grid(row=15, column=0, columnspan=3, pady=10)

    def recommend_action(self):
        position = self.position_var.get()
        hand = [f'{rank_var.get()} of {suit_var.get()}' for rank_var, suit_var in zip(self.rank_vars, self.suit_vars) if rank_var.get() and suit_var.get()]
        community_cards = [f'{rank_var.get()} of {suit_var.get()}' for rank_var, suit_var in zip(self.community_rank_vars, self.community_suit_vars) if rank_var.get() and suit_var.get()]
        initial_funds = self.initial_funds_var.get()
        remaining_funds = self.remaining_funds_var.get()
        pot_size = self.pot_size_var.get()

        if not position:
            messagebox.showerror("Error", "Please select a position.")
            return

        if len(hand) != 2:
            messagebox.showerror("Error", "Please select two unique cards for the hand.")
            return

        if not initial_funds or not remaining_funds or not pot_size:
            messagebox.showerror("Error", "Please enter initial funds, remaining funds, and pot size.")
            return

        # 檢查是否有重複的牌
        all_cards = hand + community_cards
        if len(all_cards) != len(set(all_cards)):
            messagebox.showerror("Error", "Duplicate cards selected. Please select unique cards.")
            return

        try:
            action = self.optimizer.recommend_action(position, hand, community_cards, initial_funds, remaining_funds, pot_size)
            if isinstance(action, tuple):
                action_text = f"Action: {action[0]}, Raise Size: {action[1]}"
            else:
                action_text = f"Action: {action}"

            messagebox.showinfo("Recommended Action", f"Recommended action for position {position} with hand {hand}, community cards {community_cards}, initial funds {initial_funds}, remaining funds {remaining_funds}, and pot size {pot_size}: {action_text}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    gui = PokerGUI(root)
    root.mainloop()
