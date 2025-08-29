#!/usr/bin/env python3
"""
GUI Popup Blocker - ระบบป้องกัน Popup พร้อม GUI
สำหรับ Windows เท่านั้น
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import sys
import os
from datetime import datetime

# Import our existing modules
from config import Config
from logger import Logger

# Only import Windows-specific modules when on Windows
try:
    import ctypes
    from popup_blocker import PopupBlocker
    WINDOWS_AVAILABLE = True
except (ImportError, AttributeError):
    WINDOWS_AVAILABLE = False

class MouseMover:
    """คลาสสำหรับเลื่อนเมาส์เพื่อป้องกันการล็อคหน้าจอ"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        
    def start(self):
        """เริ่มการเลื่อนเมาส์"""
        if not WINDOWS_AVAILABLE:
            return False
            
        self.running = True
        self.thread = threading.Thread(target=self._move_mouse_loop, daemon=True)
        self.thread.start()
        return True
        
    def stop(self):
        """หยุดการเลื่อนเมาส์"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
            
    def _move_mouse_loop(self):
        """วนรอบการเลื่อนเมาส์ทุก 1 นาที"""
        try:
            while self.running:
                # รอ 1 นาที (60 วินาที)
                for i in range(60):
                    if not self.running:
                        return
                    time.sleep(1)
                
                # เลื่อนเมาส์เล็กน้อย
                self._nudge_mouse()
                
        except Exception as e:
            print(f"Error in mouse mover: {e}")
    
    def _nudge_mouse(self):
        """เลื่อนเมาส์เล็กน้อยเพื่อป้องกันการล็อคหน้าจอ"""
        try:
            if WINDOWS_AVAILABLE:
                # ได้ตำแหน่งเมาส์ปัจจุบัน
                point = ctypes.wintypes.POINT()
                ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
                
                # เลื่อนเมาส์ 1 พิกเซล แล้วเลื่อนกลับ
                ctypes.windll.user32.SetCursorPos(point.x + 1, point.y)
                time.sleep(0.1)
                ctypes.windll.user32.SetCursorPos(point.x, point.y)
                
        except Exception as e:
            print(f"Error nudging mouse: {e}")

class PopupBlockerGUI:
    """GUI สำหรับ Popup Blocker"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Popup Blocker - ป้องกัน Popup อัตโนมัติ")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # สถานะการทำงาน
        self.is_running = False
        self.blocker = None
        self.blocker_thread = None
        self.mouse_mover = MouseMover()
        
        # สร้าง GUI
        self.setup_gui()
        
        # ตั้งค่าปิดโปรแกรม
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_gui(self):
        """สร้าง GUI components"""
        
        # หัวเรื่อง
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(title_frame, text="🚫 Popup Blocker", font=("Arial", 16, "bold"))
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame, text="กดปุ่ม 'ไม่' อัตโนมัติ + ป้องกันล็อคหน้าจอ")
        subtitle_label.pack()
        
        # กรอบปุ่มควบคุม
        control_frame = ttk.LabelFrame(self.root, text="ควบคุมโปรแกรม", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # ปุ่มเริ่ม/หยุด
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(button_frame, text="▶️ เริ่มโปรแกรม", 
                                      command=self.start_blocker, style="Green.TButton")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ หยุดโปรแกรม", 
                                     command=self.stop_blocker, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # สถานะ
        self.status_var = tk.StringVar(value="พร้อมใช้งาน")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, 
                                font=("Arial", 10, "bold"))
        status_label.pack(pady=5)
        
        # กรอบตั้งค่า
        settings_frame = ttk.LabelFrame(self.root, text="ตั้งค่า", padding="10")
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # เช็คบ็อกซ์ป้องกันล็อคหน้าจอ
        self.prevent_lock_var = tk.BooleanVar(value=True)
        prevent_lock_cb = ttk.Checkbutton(settings_frame, 
                                         text="ป้องกันการล็อคหน้าจอ (เลื่อนเมาส์ทุก 1 นาที)",
                                         variable=self.prevent_lock_var)
        prevent_lock_cb.pack(anchor=tk.W)
        
        # กรอบสถิติ
        stats_frame = ttk.LabelFrame(self.root, text="สถิติการทำงาน", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_text = ttk.Label(stats_frame, text="ยังไม่เริ่มทำงาน")
        self.stats_text.pack()
        
        # กรอบ Log
        log_frame = ttk.LabelFrame(self.root, text="Log การทำงาน", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=60)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # ปุ่มล้าง Log
        clear_button = ttk.Button(log_frame, text="ล้าง Log", command=self.clear_log)
        clear_button.pack(pady=2)
        
        # เพิ่มข้อความเริ่มต้น
        self.add_log("โปรแกรม Popup Blocker พร้อมใช้งาน")
        self.add_log("✨ รุ่นปรับปรุง: คลิกซ้ำจนกว่าปุ่ม 'ไม่' จะหายไป")
        if not WINDOWS_AVAILABLE:
            self.add_log("⚠️ ตรวจพบว่าไม่ได้อยู่บน Windows - โปรแกรมจะไม่ทำงานได้")
            self.start_button.config(state=tk.DISABLED)
        else:
            self.add_log("🎯 ปรับปรุงแล้ว: การคลิกมีประสิทธิภาพมากขึ้น")
        
    def add_log(self, message):
        """เพิ่มข้อความใน log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # เลื่อนไปข้อความล่าสุด
        
    def clear_log(self):
        """ล้าง log"""
        self.log_text.delete(1.0, tk.END)
        self.add_log("ล้าง log แล้ว")
        
    def start_blocker(self):
        """เริ่มโปรแกรม Popup Blocker"""
        if not WINDOWS_AVAILABLE:
            messagebox.showerror("ข้อผิดพลาด", "โปรแกรมนี้ทำงานได้เฉพาะบน Windows เท่านั้น")
            return
            
        if self.is_running:
            return
            
        try:
            # เริ่ม Popup Blocker
            self.blocker = PopupBlocker()
            self.blocker_thread = threading.Thread(target=self._run_blocker, daemon=True)
            self.blocker_thread.start()
            
            # เริ่มป้องกันการล็อคหน้าจอ (ถ้าเลือก)
            if self.prevent_lock_var.get():
                if self.mouse_mover.start():
                    self.add_log("✅ เริ่มป้องกันการล็อคหน้าจอแล้ว")
                else:
                    self.add_log("⚠️ ไม่สามารถเริ่มป้องกันการล็อคหน้าจอได้")
            
            # อัพเดตสถานะ
            self.is_running = True
            self.status_var.set("🟢 กำลังทำงาน...")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.add_log("🚀 เริ่มโปรแกรม Popup Blocker แล้ว (รุ่นปรับปรุง)")
            self.add_log("🔄 จะคลิกซ้ำจนกว่าปุ่ม 'ไม่' จะหายไป")
            
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเริ่มโปรแกรมได้: {e}")
            self.add_log(f"❌ ข้อผิดพลาด: {e}")
    
    def stop_blocker(self):
        """หยุดโปรแกรม Popup Blocker"""
        if not self.is_running:
            return
            
        try:
            # หยุด Popup Blocker
            self.is_running = False
            if self.blocker:
                self.blocker.stop()
                
            # หยุดป้องกันการล็อคหน้าจอ
            self.mouse_mover.stop()
            
            # อัพเดตสถานะ
            self.status_var.set("🔴 หยุดทำงานแล้ว")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            
            self.add_log("⏹️ หยุดโปรแกรมแล้ว")
            
            # แสดงสถิติสุดท้าย
            if self.blocker:
                stats = self.blocker.stats
                self.update_stats_display(stats)
                
        except Exception as e:
            self.add_log(f"❌ ข้อผิดพลาดในการหยุดโปรแกรม: {e}")
    
    def _run_blocker(self):
        """รัน Popup Blocker ในเธรดแยก"""
        try:
            while self.is_running and self.blocker:
                # ตรวจสอบ popup
                self.blocker._check_for_popups()
                
                # อัพเดตสถิติ
                self.root.after(0, self.update_stats_display, self.blocker.stats.copy())
                
                # รอตามการตั้งค่า
                time.sleep(self.blocker.config.check_interval)
                
        except Exception as e:
            self.root.after(0, self.add_log, f"❌ ข้อผิดพลาดในการทำงาน: {e}")
    
    def update_stats_display(self, stats):
        """อัพเดตการแสดงสถิติ"""
        stats_text = f"Popup ที่พบ: {stats['popups_detected']} | กดปุ่มแล้ว: {stats['buttons_clicked']} | ข้อผิดพลาด: {stats['errors']}"
        self.stats_text.config(text=stats_text)
    
    def on_closing(self):
        """เมื่อปิดโปรแกรม"""
        if self.is_running:
            self.stop_blocker()
        
        # รอให้เธรดจบ
        if self.blocker_thread and self.blocker_thread.is_alive():
            self.blocker_thread.join(timeout=2)
            
        self.root.destroy()
    
    def run(self):
        """เริ่มรัน GUI"""
        self.root.mainloop()

def main():
    """ฟังก์ชันหลัก"""
    try:
        # สร้าง GUI และรัน
        app = PopupBlockerGUI()
        app.run()
        
    except Exception as e:
        print(f"ข้อผิดพลาดใน GUI: {e}")
        
        # ถ้า GUI ไม่ทำงาน ให้ใช้แบบ console
        if WINDOWS_AVAILABLE:
            from popup_blocker import main as console_main
            print("เปลี่ยนไปใช้ console mode...")
            console_main()
        else:
            print("ไม่สามารถรันโปรแกรมได้ - ต้องการ Windows")

if __name__ == "__main__":
    main()
