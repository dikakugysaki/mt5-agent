import asyncio
import websockets
import json
import MetaTrader5 as mt5
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime

VPS_URL = "ws://174.138.22.235:55999:8765"
LICENSE_KEY = ""

# ==================== KONEKSI MT5 ====================
def connect_mt5():
    if not mt5.initialize():
        return False
    account = mt5.account_info()
    if account:
        return True
    return False


# ==================== EKSEKUSI ORDER ====================
def execute_order(signal):
    pair = signal["pair"]
    direction = signal["direction"]
    lot = signal["lot"]
    sl = signal["sl"]
    tp = signal["tp"]
    symbol = pair.replace("/", "")
    
    # Cek symbol tersedia di MT5
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return False
    
    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)
    
    if direction == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    else:
        order_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid
    
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot),
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "AT_" + signal.get("strategy", "Auto"),
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request)
    
    if result.retcode == mt5.TRADE_RETCODE_DONE:
        return True
    else:
        # Log error detail
        print(f"MT5 Error: {result.comment} (code: {result.retcode})")
        return False


# ==================== GUI ====================
class AgentGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AetherTrade AI - MT5 Agent")
        self.root.geometry("500x450")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)
        
        # Header
        tk.Label(
            self.root, text="AETHER TRADE AI", 
            font=("Arial", 20, "bold"), bg="#1a1a2e", fg="#e2b04a"
        ).pack(pady=(15, 0))
        
        tk.Label(
            self.root, text="MT5 Agent - Auto Trading", 
            font=("Arial", 10), bg="#1a1a2e", fg="white"
        ).pack()
        
        # Separator
        tk.Frame(self.root, height=1, bg="#e2b04a").pack(fill="x", padx=30, pady=10)
        
        # License Key Input
        tk.Label(
            self.root, text="License Key:", 
            font=("Arial", 11, "bold"), bg="#1a1a2e", fg="white"
        ).pack(pady=(10, 0))
        
        self.key_entry = tk.Entry(
            self.root, font=("Arial", 11), width=45, justify="center",
            bg="#0f3460", fg="#00ff88", insertbackground="#00ff88"
        )
        self.key_entry.pack(pady=5, ipady=3)
        
        # Buttons
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        
        self.connect_btn = tk.Button(
            btn_frame, text="🔌 CONNECT", command=self.connect, 
            bg="#00ff88", fg="black", font=("Arial", 11, "bold"), width=14, cursor="hand2"
        )
        self.connect_btn.pack(side="left", padx=5)
        
        self.disconnect_btn = tk.Button(
            btn_frame, text="⏹️ DISCONNECT", command=self.disconnect, 
            bg="#ff4444", fg="white", font=("Arial", 11, "bold"), width=14, cursor="hand2",
            state="disabled"
        )
        self.disconnect_btn.pack(side="left", padx=5)
        
        # Status
        self.status_frame = tk.Frame(self.root, bg="#1a1a2e")
        self.status_frame.pack(pady=5)
        
        self.status_indicator = tk.Canvas(
            self.status_frame, width=12, height=12, bg="#1a1a2e", highlightthickness=0
        )
        self.status_indicator.pack(side="left", padx=(0, 8))
        self.status_dot = self.status_indicator.create_oval(1, 1, 11, 11, fill="#ff4444")
        
        self.status_label = tk.Label(
            self.status_frame, text="Disconnected", 
            font=("Arial", 10, "bold"), bg="#1a1a2e", fg="#ff4444"
        )
        self.status_label.pack(side="left")
        
        # Info License
        self.license_info = tk.Label(
            self.root, text="", font=("Arial", 9), bg="#1a1a2e", fg="#gray"
        )
        self.license_info.pack(pady=2)
        
        # Log Area
        log_frame = tk.Frame(self.root, bg="#0f3460")
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log = scrolledtext.ScrolledText(
            log_frame, height=10, bg="#0f3460", fg="#00ff88", 
            font=("Consolas", 9), wrap=tk.WORD
        )
        self.log.pack(fill="both", expand=True, padx=1, pady=1)
        self.log.insert("end", "Welcome to AetherTrade AI MT5 Agent\n")
        self.log.insert("end", "Please enter your License Key and click CONNECT\n")
        self.log.configure(state="disabled")
        
        # Footer
        tk.Label(
            self.root, text="Pastikan MetaTrader 5 terbuka & Agent tetap berjalan", 
            font=("Arial", 8), bg="#1a1a2e", fg="gray"
        ).pack(side="bottom", pady=8)
        
        self.running = False
        self.ws_connected = False
    
    def log_msg(self, msg, color=None):
        """Tambah log dengan timestamp"""
        self.log.configure(state="normal")
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log.insert("end", f"[{timestamp}] {msg}\n")
        self.log.see("end")
        self.log.configure(state="disabled")
    
    def set_status(self, text, color):
        """Update status indicator"""
        self.status_label.config(text=text, fg=color)
        self.status_indicator.itemconfig(self.status_dot, fill=color)
    
    def connect(self):
        """Tombol Connect ditekan"""
        key = self.key_entry.get().strip()
        
        if not key:
            messagebox.showerror("Error", "Masukkan License Key terlebih dahulu!")
            return
        
        if not key.startswith("AT-"):
            messagebox.showerror("Error", "Format License Key tidak valid!\nHarus diawali dengan 'AT-'")
            return
        
        # Cek MT5
        self.log_msg("🔄 Menghubungkan ke MetaTrader 5...")
        if not connect_mt5():
            self.set_status("MT5 Not Found!", "#ff4444")
            self.log_msg("❌ MetaTrader 5 tidak ditemukan!")
            self.log_msg("   Pastikan MT5 sedang berjalan di PC ini.")
            messagebox.showerror("Error", "MetaTrader 5 tidak ditemukan!\n\nPastikan MT5 sedang berjalan.")
            return
        
        account = mt5.account_info()
        self.set_status(f"MT5 OK - {account.login}", "#00ff88")
        self.log_msg(f"✅ MT5 Connected - Login: {account.login}")
        self.log_msg(f"   Balance: ${account.balance:,.2f} | Equity: ${account.equity:,.2f}")
        self.log_msg(f"   Server: {account.server}")
        
        # Disable input
        self.key_entry.config(state="disabled")
        self.connect_btn.config(state="disabled")
        self.disconnect_btn.config(state="normal")
        
        # Simpan license key
        global LICENSE_KEY
        LICENSE_KEY = key
        
        # Start WebSocket di thread terpisah
        self.running = True
        import threading
        threading.Thread(target=self._run_ws_thread, daemon=True).start()
    
    def disconnect(self):
        """Tombol Disconnect ditekan"""
        self.running = False
        self.set_status("Disconnecting...", "#ff4444")
        self.log_msg("⏹️ Disconnecting...")
        
        # Enable input
        self.key_entry.config(state="normal")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        
        # Shutdown MT5
        try:
            mt5.shutdown()
        except:
            pass
        
        self.set_status("Disconnected", "#ff4444")
        self.log_msg("🔌 Disconnected from MT5")
    
    def _run_ws_thread(self):
        """Wrapper untuk menjalankan asyncio di thread"""
        try:
            asyncio.run(self._websocket_loop())
        except Exception as e:
            self.log_msg(f"❌ Connection error: {e}")
            self.root.after(0, self.disconnect)
    
    async def _websocket_loop(self):
        """Main WebSocket loop"""
        try:
            self.root.after(0, lambda: self.log_msg(f"🔗 Connecting to AetherTrade AI Server..."))
            
            async with websockets.connect(VPS_URL, ping_interval=None) as ws:
                # Kirim autentikasi
                await ws.send(json.dumps({
                    "action": "auth",
                    "key": LICENSE_KEY
                }))
                
                # Tunggu response auth
                response = await asyncio.wait_for(ws.recv(), timeout=15)
                auth = json.loads(response)
                
                if auth.get("status") != "OK":
                    error_msg = auth.get("message", "License tidak valid!")
                    self.root.after(0, lambda: self.log_msg(f"❌ {error_msg}"))
                    self.root.after(0, lambda: self.set_status("License Invalid", "#ff4444"))
                    self.root.after(0, self.disconnect)
                    return
                
                # ✅ Lisensi valid
                package = auth.get("package", "Unknown").upper()
                expires_str = auth.get("expires", "Unknown")
                max_pairs = auth.get("max_pairs", "N/A")
                
                self.root.after(0, lambda: self.set_status(f"LICENSED - {package}", "#00ff88"))
                self.root.after(0, lambda: self.log_msg(f"✅ {auth.get('message', 'Connected')}"))
                
                # Tampilkan info lisensi
                if expires_str != "Unknown":
                    try:
                        expires_date = datetime.fromisoformat(expires_str)
                        days_left = (expires_date - datetime.now()).days
                        
                        info_text = f"📦 {package} | 📅 Expires: {expires_str[:10]} | ⏰ {days_left} days left"
                        self.root.after(0, lambda: self.license_info.config(text=info_text))
                        
                        self.root.after(0, lambda: self.log_msg(f"📅 License expires: {expires_str[:10]} ({days_left} days left)"))
                        self.root.after(0, lambda: self.log_msg(f"📊 Max Pairs: {max_pairs}"))
                        
                        # 🆕 Cek apakah sudah expired
                        if expires_date < datetime.now():
                            self.root.after(0, lambda: self.set_status("LICENSE EXPIRED", "#ff4444"))
                            self.root.after(0, lambda: self.log_msg("❌ LICENSE HAS EXPIRED!"))
                            self.root.after(0, lambda: self.log_msg("   Silakan hubungi admin untuk perpanjang."))
                            self.root.after(0, lambda: messagebox.showwarning(
                                "License Expired", 
                                "Lisensi Anda sudah expired!\n\nSilakan hubungi admin untuk perpanjang lisensi."
                            ))
                            self.root.after(0, self.disconnect)
                            return
                    except Exception as e:
                        self.root.after(0, lambda: self.log_msg(f"⚠️ Could not parse expiry: {e}"))
                
                # 🆕 Mulai trading
                self.root.after(0, lambda: self.log_msg("🟢 Auto Trading ACTIVE - Waiting for signals..."))
                self.root.after(0, lambda: self.log_msg("━" * 40))
                
                # Loop terima sinyal
                while self.running:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=30)
                        data = json.loads(msg)
                        
                        if data.get("action") == "trade_signal":
                            signal = data["signal"]
                            
                            # Eksekusi order
                            loop = asyncio.get_event_loop()
                            success = await loop.run_in_executor(None, execute_order, signal)
                            
                            emoji = "✅" if success else "❌"
                            pair = signal["pair"]
                            direction = signal["direction"]
                            entry = signal["entry"]
                            strategy = signal.get("strategy", "Unknown")
                            lot = signal.get("lot", "N/A")
                            
                            if success:
                                self.root.after(0, lambda: self.log_msg(
                                    f"{emoji} {pair} {direction} | Entry: ${entry:.2f} | Lot: {lot} | Strategy: {strategy}"
                                ))
                            else:
                                self.root.after(0, lambda: self.log_msg(
                                    f"{emoji} FAILED: {pair} {direction} | Check MT5 for details"
                                ))
                        
                        elif data.get("status") == "PONG":
                            pass  # Keep-alive response
                        
                    except asyncio.TimeoutError:
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        self.root.after(0, lambda: self.log_msg("⚠️ Connection closed by server"))
                        break
                    except Exception as e:
                        self.root.after(0, lambda: self.log_msg(f"⚠️ Error: {e}"))
                        continue
        
        except websockets.exceptions.InvalidURI:
            self.root.after(0, lambda: self.log_msg("❌ Invalid VPS URL. Check VPS_URL setting."))
        except websockets.exceptions.ConnectionClosed:
            self.root.after(0, lambda: self.log_msg("❌ Connection failed. Server may be offline."))
        except asyncio.TimeoutError:
            self.root.after(0, lambda: self.log_msg("❌ Connection timeout. Server not responding."))
        except Exception as e:
            self.root.after(0, lambda: self.log_msg(f"❌ Connection error: {e}"))
        finally:
            if self.running:
                self.root.after(0, self.disconnect)
    
    def run(self):
        """Start GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
    
    def _on_closing(self):
        """Handle close window"""
        self.running = False
        try:
            mt5.shutdown()
        except:
            pass
        self.root.destroy()


# ==================== MAIN ====================
if __name__ == "__main__":
    app = AgentGUI()
    app.run()