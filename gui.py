import tkinter as tk
from tkinter import ttk, messagebox
import threading
from threading import Event
from ai_browser import run_cmd, run_agent   # 你的核心逻辑

import sys

class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        if message.strip():
            self.text_widget.after(
                0,
                lambda: self._append(message)
            )

    def flush(self):
        pass

    def _append(self, message):
        self.text_widget.config(state="normal")
        self.text_widget.insert("end", message)
        self.text_widget.see("end")
        self.text_widget.config(state="disabled")


# ================= 状态 =================
browser_started = Event()

def start_browser():
    def worker():
        try:
            url = url_var.get().strip()

            if not url:
                root.after(0, lambda: messagebox.showwarning("提示", "请输入 URL"))
                return

            root.after(0, lambda: status_var.set(f"🚀 正在启动浏览器: {url}"))

            open_command = f'playwright-cli open {url} --headed'
            result = run_cmd(open_command)

            # ⭐ 判断是否启动成功
            if result and "opened with pid" in result.lower():
                browser_started.set()
                root.after(0, lambda: status_var.set("✅ 浏览器启动成功"))
            else:
                browser_started.clear()
                root.after(0, lambda: status_var.set("⚠️ 浏览器启动失败"))

                root.after(
                    0,
                    lambda: messagebox.showerror(
                        "启动失败",
                        result if result else "无返回内容"
                    )
                )

        except Exception as e:
            browser_started.clear()
            root.after(0, lambda: status_var.set("❌ 启动异常"))
            root.after(0, lambda: messagebox.showerror("错误", str(e)))

    threading.Thread(target=worker, daemon=True).start()

def start_task():
    global browser_started

    if not browser_started:
        messagebox.showwarning("提示", "请先启动浏览器")
        return

    goal = goal_var.get().strip()
    attention = attention_var.get().strip()

    if not goal:
        messagebox.showwarning("提示", "请输入执行目标")
        return

    def worker():
        try:
            status_var.set("🤖 Agent 执行中...")

            result = run_agent(goal, attention)

            status_var.set("✅ 执行完成")

            root.after(0, lambda: show_result(result))

        except Exception as e:
            status_var.set("❌ 执行失败")
            root.after(0, lambda: messagebox.showerror("错误", str(e)))

    threading.Thread(target=worker, daemon=True).start()


def show_result(result: str):
    result_text.config(state="normal")
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, result)
    result_text.config(state="disabled")


# ================= UI =================
root = tk.Tk()
root.title("Playwright Agent 控制台")
root.geometry("650x520")
root.configure(bg="#1e1e2f")

style = ttk.Style()
style.theme_use("clam")

style.configure("TLabel", background="#1e1e2f", foreground="white", font=("Microsoft YaHei", 10))
style.configure("TButton", font=("Microsoft YaHei", 10, "bold"))



# 标题
ttk.Label(root, text="Playwright Agent 控制台", font=("Microsoft YaHei", 14, "bold")).pack(pady=10)


# 输入
ttk.Label(root, text="🎯 总执行目标").pack(anchor="w", padx=20)
goal_var = tk.StringVar(value="今年五一假期怎么放？")
ttk.Entry(root, textvariable=goal_var, width=70).pack(padx=20, pady=5)

ttk.Label(root, text="⚠️ 提醒ai注意事项").pack(anchor="w", padx=20)
attention_var = tk.StringVar(value="注意时间")
ttk.Entry(root, textvariable=attention_var, width=70).pack(padx=20, pady=5)

ttk.Label(root, text="🌐 启动 URL").pack(anchor="w", padx=20)
url_var = tk.StringVar(value="https://demo.playwright.dev/todomvc/")
ttk.Entry(root, textvariable=url_var, width=70).pack(padx=20, pady=5)

# ================= 按钮区（关键改动） =================
btn_frame = tk.Frame(root, bg="#1e1e2f")
btn_frame.pack(pady=15)

ttk.Button(btn_frame, text="🚀 启动浏览器", command=start_browser).grid(row=0, column=0, padx=10)
ttk.Button(btn_frame, text="🤖 开始实现目标", command=start_task).grid(row=0, column=1, padx=10)


# 状态
status_var = tk.StringVar(value="等待操作...")
ttk.Label(root, textvariable=status_var, font=("Microsoft YaHei", 10, "bold")).pack()


# 结果
ttk.Label(root, text="📦 执行结果").pack(anchor="w", padx=20, pady=(15, 0))

result_text = tk.Text(root, height=12, bg="#111", fg="#00ff88", insertbackground="white")
result_text.pack(padx=20, pady=5, fill="both", expand=True)
result_text.config(state="disabled")

sys.stdout = TextRedirector(result_text)

root.mainloop()


