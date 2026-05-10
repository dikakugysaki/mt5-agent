# FULL CODE FINAL - AetherTrade AI - UPGRADE MTF + S/R
# Simpan sebagai bot.py
# Upgrade: 4 Strategi MTF, S/R ke AI, Semua fitur dipertahankan

import requests, json, logging, threading, time, asyncio, re, sqlite3, secrets
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ======================= KONFIGURASI =======================
TELEGRAM_TOKEN = "8537439287:AAFc2WPTG4I8X1gKPLNvn9jk8N2ub1zWK2w"
MAIA_API_KEY = "sk-n03H7ceb0UoUtx2qBmXs7Q"
MAIA_MODEL = "deepseek/deepseek-chat"
MAIA_ENDPOINT = "https://api.maiarouter.ai/v1/chat/completions"

ADMIN_IDS = [6000348929]
ADMIN_USERNAME = "@rimuru_genkai"  # Ganti dengan username Telegram admin (pakai @)
PAYMENT_METHODS = """
📱 *DANA*: 085930016248
📱 *GOPAY*: 085930016248
🏦 *SEABANK*: 901793777670
"""

TWELVE_DATA_KEYS = [
    "d918e5241a1d46e09417302d53ffa7b5", "94b6cbbd3d1f495faf7fe0e53eabd01d",
    "ffa0fec7bdd74ba0ac131658b7648c13", "ca29ef4e30a34ac0ab4cca2f4f4c8acf",
    "83601edd820b4afc8c64c22b083624c4", "1987fce846494cf4a9250167999bea63",
    "9d8eb5881b6a4e1497c089fa922f382b", "115533cc802a42d7b983f015765e790c",
    "e6835b83105042e8b9888c6941be5181", "49caac7014a240e9bed08b2baafd029b",
    "b68ca2f09e564b26ad4b1fdecd715877"
]
COINGECKO_KEYS = ["CG-U21PHksdWoL97k5pxvqR9Vr1", "CG-78kF31SVbnrERaMAt3HhEg2d"]
FCS_API_KEYS = ["98ux1Tr4upleYdqocItipjpIo", "pg0k56FwkIvLpf6hZM8cjwWw8kZix"]
FINNHUB_KEY = "d7s4s3hr01qm28g8b3ogd7s4s3hr01qm28g8b3p0"

CHECK_INTERVAL = 120
CACHE_TTL = 120
NEWS_CACHE_TTL = 600
MICIN_CACHE_TTL = 120
SAHAM_CACHE_TTL = 300

DB_FILE = "aethertrade.db"
TRIAL_MINUTES = 30

SUBSCRIPTION_PLANS = {
    "trial": {"name": "Trial", "duration_hours": 0.5, "price": 0, "emoji": "🆓"},
    "basic": {"name": "Basic", "duration_hours": 720, "price": 50000, "emoji": "🥈"},
    "pro": {"name": "Pro", "duration_hours": 2160, "price": 120000, "emoji": "🥇"},
    "vip": {"name": "VIP", "duration_hours": 4320, "price": 198000, "emoji": "💎"},
}

# ==================== BROKER TERPERCAYA ====================
BROKER_DATA = {
    "exness": {
        "name": "Exness",
        "logo": "🏦",
        "description": "Broker Multi-Aset Global — Didirikan 2008, 600.000+ trader aktif, volume trading $4 triliun/bulan",
        "link": "https://one.exnessonelink.com/a/tpdtmhxhoi",
        "features": [
            "✅ Spread Mulai 0.0 Pips — Biaya trading termurah di kelasnya",
            "✅ Leverage Hingga 1:2000 (Unlimited di MT4) — Maksimalkan modal kecil",
            "✅ Deposit Minimum $10 — Bisa mulai trading dengan modal minimal",
            "✅ Withdraw Instan 24/7 — 98% otomatis, dana sampai dalam hitungan detik",
            "✅ Bebas Biaya Deposit & Withdraw — Exness tanggung biaya pihak ketiga",
            "✅ Tersedia Bank Lokal Indonesia — BCA, BRI, Mandiri, dan lainnya",
            "✅ Platform MT4, MT5, WebTrader, Exness Terminal — Pilihan lengkap",
            "✅ Copy Trading — Ikuti strategi trader profesional",
            "✅ CS 24/7 Bahasa Indonesia — Dukungan penuh via live chat & telepon",
            "✅ Regulasi FCA (UK), CySEC, FSCA — Dana aman, rekening terpisah"
        ],
        "benefits": [
            "▸ *Kemitraan Resmi* — Anda terdaftar di bawah jaringan partner resmi Exness",
            "▸ *Rebate Spread* — Cashback otomatis dari setiap trading Anda",
            "▸ *Spread VIP* — Kondisi trading lebih rendah melalui link khusus",
            "▸ *Prioritas Withdraw* — Proses lebih cepat untuk pengguna link ini",
            "",
            "🛡 *Bantuan Jika Ada Kendala:*",
            "  • Withdraw tertunda — Saya bantu follow-up ke tim Exness",
            "  • Verifikasi akun gagal — Saya bantu cek dokumen & solusi",
            "  • Trading loss terus — Saya bantu evaluasi strategi & setting akun",
            "  • Bingung platform MT4/MT5 — Saya bantu setup & panduan lengkap",
            "  • Butuh edukasi tambahan — Saya sediakan materi belajar eksklusif",
            "",
            "▸ *Support Personal* — Konsultasi langsung dengan saya jika ada kendala"
        ],
        "pindah_kemitraan": """🔄 *CARA PINDAH KEMITRAAN KE SAYA*
━━━━━━━━━━━━━━━━━━━━━━

📌 *LANGKAH 1 — Cek Kemitraan Saat Ini:*
  • Login ke akun Exness Anda via website/app
  • Buka menu *Profil* atau *Pengaturan Akun*
  • Cari bagian *Partner* atau *Introducing Broker (IB)*
  • Lihat apakah ada kode partner/IB yang terdaftar
  • Jika *kosong*: langsung daftar pakai link saya
  • Jika *ada*: lanjut ke Langkah 2

📌 *LANGKAH 2 — Keluar dari Kemitraan Lama:*
  • Buka *Live Chat Support* Exness (24/7 Bahasa Indonesia)
  • Ketik pesan berikut ke CS:
    ```Halo, saya ingin melepaskan diri dari IB/partner saya saat ini. Mohon dibantu untuk dilepaskan.```
  • CS akan verifikasi identitas Anda (nama, email, nomor akun)
  • Setelah verifikasi, CS proses pelepasan dalam 1×24 jam
  • Anda akan dapat *email konfirmasi* bahwa IB sudah dilepas
  • *Alternatif* — Kirim email ke support@exness.com:
    Subjek: *Permohonan Pelepasan Introducing Broker*
    Isi: Nama lengkap, Nomor akun, Alasan pelepasan

📌 *LANGKAH 3 — Bergabung ke Kemitraan Saya:*
  • Setelah IB lama dilepas (tunggu email konfirmasi)
  • Klik tombol *🔗 Daftar Exness* di bawah
  • Buka link: [DAFTAR EXNESS PARTNER](https://one.exnessonelink.com/a/tpdtmhxhoi)
  • Daftar akun baru, atau login jika sudah punya akun
  • Sistem otomatis mendeteksi link partner saya
  • Cek ulang: Profil → Partner → muncul kode partner saya
  • ✅ *SELESAI!* Anda resmi di bawah kemitraan saya

━━━━━━━━━━━━━━━━━━━━━━

🎁 *KEUNTUNGAN SETELAH BERGABUNG:*
  ▸ Rebate spread otomatis ke akun trading Anda
  ▸ Spread lebih rendah (kondisi VIP)
  ▸ Prioritas bantuan withdraw & verifikasi
  ▸ Support personal 1-on-1 dengan saya
  ▸ Materi edukasi trading eksklusif
  ▸ Akses sinyal & analisa dari AetherTrade AI

━━━━━━━━━━━━━━━━━━━━━━

⚠️ *CATATAN PENTING:*
  • Proses pelepasan IB lama maksimal 1×24 jam (hari kerja)
  • Anda *TIDAK perlu* tutup akun lama, cukup lepas IB-nya
  • Jika CS mempersulit, minta eskalasi ke supervisor
  • Screenshot semua percakapan dengan CS sebagai bukti
  • Jika ada kendala, klik tombol *📩 Hubungi Admin*

━━━━━━━━━━━━━━━━━━━━━━

🤝 *Saya siap bantu Anda di setiap langkah!*
Jangan ragu untuk hubungi saya jika ada pertanyaan."""
    }
}

# ==================== TAMBAHKAN SETELAH BROKER_DATA ====================

# ==================== REAL TRADING SYSTEM ====================
import asyncio as ws_asyncio
import MetaTrader5 as mt5
try:
    import websockets
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    print("⚠️ websockets not installed. Run: pip install websockets")

# ==================== LISENSI DATABASE ====================
def init_license_db():
    conn = sqlite3.connect("licenses.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses (
        key TEXT PRIMARY KEY,
        owner_name TEXT,
        package TEXT,
        created TEXT,
        expires TEXT,
        is_active INTEGER DEFAULT 1,
        max_pairs INTEGER DEFAULT 10
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS trade_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        license_key TEXT,
        pair TEXT,
        direction TEXT,
        entry REAL,
        sl REAL,
        tp REAL,
        strategy TEXT,
        lot REAL,
        status TEXT DEFAULT 'SENT',
        timestamp TEXT,
        result TEXT DEFAULT NULL
    )''')
    conn.commit()
    conn.close()

def generate_license(owner_name, package, duration_days):
    """Generate lisensi untuk pelanggan"""
    key = f"AT-{secrets.token_hex(8).upper()}"
    now = datetime.now()
    expires = now + timedelta(days=duration_days)
    
    max_pairs = {"basic": 5, "pro": 8, "vip": 10}.get(package, 10)
    
    conn = sqlite3.connect("licenses.db")
    c = conn.cursor()
    c.execute("INSERT INTO licenses (key, owner_name, package, created, expires, max_pairs) VALUES (?,?,?,?,?,?)",
              (key, owner_name, package, now.isoformat(), expires.isoformat(), max_pairs))
    conn.commit()
    conn.close()
    return key

def verify_license(key):
    """Verifikasi lisensi pelanggan"""
    conn = sqlite3.connect("licenses.db")
    c = conn.cursor()
    c.execute("SELECT owner_name, package, expires, is_active, max_pairs FROM licenses WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    if not row: return None
    owner_name, package, expires, active, max_pairs = row
    if not active: return None
    if datetime.fromisoformat(expires) < datetime.now(): return None
    return {"owner_name": owner_name, "package": package, "expires": expires, "max_pairs": max_pairs}

# ==================== WEBSOCKET SERVER ====================
connected_clients = {}  # {license_key: websocket}

async def ws_send_signal(license_key, signal_data):
    """Kirim sinyal trading ke MT5 Agent pelanggan"""
    if license_key in connected_clients:
        try:
            ws = connected_clients[license_key]
            await ws.send(json.dumps({
                "action": "trade_signal",
                "signal": signal_data,
                "timestamp": datetime.now().isoformat()
            }))
            return True
        except:
            del connected_clients[license_key]
    return False

async def ws_handle_client(websocket, path):
    """Handle koneksi dari MT5 Agent"""
    client_key = None
    
    try:
        async for message in websocket:
            data = json.loads(message)
            
            # Autentikasi lisensi
            if data.get("action") == "auth":
                key = data.get("key")
                license_info = verify_license(key)
                
                if license_info:
                    client_key = key
                    connected_clients[key] = websocket
                    await websocket.send(json.dumps({
                        "status": "OK",
                        "message": f"✅ Lisensi valid — {license_info['owner_name']} ({license_info['package'].upper()})",
                        "package": license_info["package"],
                        "expires": license_info["expires"],
                        "max_pairs": license_info["max_pairs"]
                    }))
                    logger.info(f"🔗 Client connected: {license_info['owner_name']} ({key[:12]}...)")
                else:
                    await websocket.send(json.dumps({
                        "status": "ERROR",
                        "message": "❌ Lisensi tidak valid atau expired. Hubungi admin."
                    }))
            
            # Status eksekusi dari MT5
            elif data.get("action") == "trade_result":
                trade_id = data.get("trade_id")
                result = data.get("result")
                logger.info(f"📊 Trade {trade_id}: {result}")
                
                conn = sqlite3.connect("licenses.db")
                c = conn.cursor()
                c.execute("UPDATE trade_log SET result=? WHERE id=?", (result, trade_id))
                conn.commit()
                conn.close()
            
            # Ping keep-alive
            elif data.get("action") == "ping":
                await websocket.send(json.dumps({"status": "PONG"}))
    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if client_key and client_key in connected_clients:
            del connected_clients[client_key]
            logger.info(f"🔌 Client disconnected: {client_key[:12]}...")

async def ws_start_server():
    """Start WebSocket server"""
    if not WEBSOCKET_AVAILABLE:
        logger.error("❌ WebSocket tidak tersedia. Install: pip install websockets")
        return
    
    init_license_db()
    print("🔌 WebSocket Server starting on ws://0.0.0.0:8765")
    
    # Notifikasi ke admin
    for admin_id in ADMIN_IDS:
        try:
            send_telegram_message(admin_id, "🔌 *WebSocket Server* siap di `ws://0.0.0.0:8765`\n\nMenunggu koneksi dari MT5 Agent pelanggan...")
        except:
            pass
    
    async with websockets.serve(ws_handle_client, "0.0.0.0", 8765):
        await ws_asyncio.Future()  # run forever

def ws_server_worker():
    """Wrapper untuk menjalankan WebSocket server di thread terpisah"""
    asyncio.run(ws_start_server())

# ==================== SEND SIGNAL TO ALL CLIENTS ====================
def broadcast_trade_signal(pair_symbol, signal_data):
    """Kirim sinyal ke semua client yang terkoneksi"""
    for license_key in list(connected_clients.keys()):
        try:
            # Simpan ke trade log
            conn = sqlite3.connect("licenses.db")
            c = conn.cursor()
            c.execute("INSERT INTO trade_log (license_key, pair, direction, entry, sl, tp, strategy, lot, timestamp, status) VALUES (?,?,?,?,?,?,?,?,?,?)",
                      (license_key, signal_data["pair"], signal_data["direction"], signal_data["entry"],
                       signal_data["sl"], signal_data["tp"], signal_data["strategy"], signal_data["lot"],
                       datetime.now().isoformat(), "SENT"))
            trade_id = c.lastrowid
            conn.commit()
            conn.close()
            
            signal_data["id"] = trade_id
            asyncio.run(ws_send_signal(license_key, signal_data))
            logger.info(f"📤 Signal sent to {license_key[:12]}...: {signal_data['pair']} {signal_data['direction']}")
        except Exception as e:
            logger.error(f"Error sending to {license_key}: {e}")


# ==================== ADMIN COMMANDS FOR LICENSE ====================
async def genlicense_command(update: Update, context):
    """Command /genlicense untuk admin generate lisensi"""
    if update.effective_chat.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Admin only.")
        return
    
    args = context.args
    if len(args) < 3:
        await update.message.reply_text(
            "🎟️ */genlicense [nama] [paket] [hari]*\n\n"
            "📦 Paket:\n"
            "  basic — 5 pair, Rp 200K/bulan\n"
            "  pro — 8 pair, Rp 500K/bulan\n"
            "  vip — 10 pair, Rp 1JT/bulan\n\n"
            "Contoh: /genlicense Alex pro 30",
            parse_mode='Markdown'
        )
        return
    
    name = args[0]
    package = args[1].lower()
    days = int(args[2])
    
    if package not in ["basic", "pro", "vip"]:
        await update.message.reply_text("❌ Paket tidak valid: basic, pro, vip"); return
    
    key = generate_license(name, package, days)
    info = verify_license(key)
    
    price_map = {"basic": "Rp 200K", "pro": "Rp 500K", "vip": "Rp 1JT"}
    
    await update.message.reply_text(
        f"🎟️ *LISENSI AUTO TRADING*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 Pemilik: {name}\n"
        f"📦 Paket: {package.upper()}\n"
        f"💰 Harga: {price_map.get(package, 'N/A')}/bulan\n"
        f"📊 Max Pair: {info['max_pairs']}\n"
        f"📅 Expired: {info['expires'][:10]}\n\n"
        f"🔑 *License Key:*\n`{key}`\n\n"
        f"📋 *Untuk Pelanggan:*\n"
        f"1. Download MT5 Agent dari link\n"
        f"2. Install & masukkan key di atas\n"
        f"3. Buka Telegram: /autotrade on\n\n"
        f"⚠️ Simpan key ini, tidak bisa di-recover!",
        parse_mode='Markdown'
    )

# ==================== TAMBAHKAN SETELAH KONFIGURASI BROKER_DATA ====================

# ==================== AUTO TRADING CONFIG ====================
LOT_CONFIG = {
    "mode": "FIXED",
    "fixed_lot": 0.01,
    "auto": {
        "balance": 1000,
        "risk_percent": 0.5,
        "min_lot": 0.01,
        "max_lot": 0.05,
        "lot_step": 0.01
    },
    "custom_lot": {
        "XAU/USD": {"mode": "FIXED", "fixed_lot": 0.01},
        "BTC/USD": {"mode": "FIXED", "fixed_lot": 0.01},
    }
}

AUTOTRADE_PAIR_CONFIG = {
    # 📌 S01_EMA_Tight: Mean Reversion EMA50
    "XAU/USD": {"strategies": ["S01_EMA_Tight"], "max_positions": 99, "note": "📌 Mean Reversion EMA50"},
    "BTC/USD": {"strategies": ["S01_EMA_Tight"], "max_positions": 99, "note": "📌 Mean Reversion EMA50"},
    "NZD/USD": {"strategies": ["S01_EMA_Tight"], "max_positions": 99, "note": "📌 Mean Reversion EMA50"},
    
    # 📌 S02_AllInOne_Agg: Multi-Indikator Agresif
    "EUR/USD": {"strategies": ["S02_AllInOne_Agg"], "max_positions": 99, "note": "📌 Multi-Indikator Agresif"},
    "USD/JPY": {"strategies": ["S02_AllInOne_Agg"], "max_positions": 99, "note": "📌 Multi-Indikator Agresif"},
    "AUD/USD": {"strategies": ["S02_AllInOne_Agg"], "max_positions": 99, "note": "📌 Multi-Indikator Agresif"},
    "USD/CAD": {"strategies": ["S02_AllInOne_Agg"], "max_positions": 99, "note": "📌 Multi-Indikator Agresif"},
    "EUR/JPY": {"strategies": ["S02_AllInOne_Agg"], "max_positions": 99, "note": "📌 Multi-Indikator Agresif"},
    "GBP/JPY": {"strategies": ["S02_AllInOne_Agg"], "max_positions": 99, "note": "📌 Multi-Indikator Agresif"},
    
    # 📌 S04_KC_Scalp: Keltner Channel Scalp
    "USD/CHF": {"strategies": ["S04_KC_Scalp"], "max_positions": 99, "note": "📌 Keltner Channel Scalp"},
    "GBP/USD": {"strategies": ["S04_KC_Scalp"], "max_positions": 99, "note": "📌 Keltner Channel Scalp"},
}

# ==================== AUTO TRADING STATE ====================
autotrade_state = {
    "active": False,
    "mode": "real",  # "paper" atau "real"
    "balance": 1000.0,
    "starting_balance": 1000.0,
    "total_trades": 0,
    "total_wins": 0,
    "total_losses": 0,
    "positions": {},
    "active_pairs": set(),  # 🆕 Pair yang dipilih user
}

# ==================== PAPER TRADING ENGINE ====================
class LotCalculator:
    def __init__(self):
        self.config = LOT_CONFIG
    
    def calculate(self, pair, entry_price, stop_loss_price):
        pair_config = self.config.get("custom_lot", {}).get(pair, {})
        mode = pair_config.get("mode", self.config["mode"])
        
        if mode == "FIXED":
            return pair_config.get("fixed_lot", self.config["fixed_lot"])
        
        auto = self.config["auto"]
        risk_percent = pair_config.get("risk_percent", auto["risk_percent"])
        risk_usd = autotrade_state["balance"] * (risk_percent / 100)
        sl_distance = abs(entry_price - stop_loss_price)
        
        if "XAU" in pair:
            lot = (risk_usd / sl_distance) * 0.01
        elif pair.endswith("JPY"):
            lot = risk_usd / (sl_distance * 100 * 9.0)
        else:
            lot = risk_usd / (sl_distance * 10000 * 10.0)
        
        lot = max(auto["min_lot"], min(auto["max_lot"], lot))
        return round(lot / auto["lot_step"]) * auto["lot_step"]

lot_calculator = LotCalculator()

def get_autotrade_price(pair_symbol):
    """Ambil harga real-time untuk paper trading"""
    try:
        resp = requests.get(f"https://api.twelvedata.com/quote?symbol={pair_symbol}&apikey={get_next_twelve_key()}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if 'close' in data:
                return float(data['close'])
    except: pass
    return None

def get_autotrade_candles(pair_symbol, interval="1h", outputsize=300):
    """Ambil data candle untuk strategi auto trading"""
    for attempt in range(2):
        try:
            resp = requests.get(f"https://api.twelvedata.com/time_series?symbol={pair_symbol}&interval={interval}&outputsize={outputsize}&apikey={get_next_twelve_key()}", timeout=15)
            if resp.status_code == 200 and 'values' in resp.json():
                candles = resp.json()['values']
                if len(candles) >= 100:
                    candles.reverse()
                    return candles
        except: pass
        time.sleep(2)
    return None

def run_autotrade_strategy_1h(symbol_key, pair_symbol):
    """Jalankan strategi 1H untuk auto trading"""
    candles = get_autotrade_candles(pair_symbol)
    if not candles: return []
    
    closes = [float(c['close']) for c in candles]
    highs = [float(c['high']) for c in candles]
    lows = [float(c['low']) for c in candles]
    opens = [float(c['open']) for c in candles]
    
    config = AUTOTRADE_PAIR_CONFIG.get(pair_symbol, {})
    strat_list = config.get("strategies", [])
    
    signals = []
    for sname in strat_list:
        if sname in ["S16_MTF_Breakout", "S08_MTF_BB_Walk"]:
            continue  # MTF di-handle terpisah
        
        func = STRATEGY_FUNCTIONS.get(sname)
        if not func: continue
        
        try:
            res = func(opens, highs, lows, closes)
            if res and res[0] in ['BUY', 'SELL']:
                signals.append({"strategy": sname, "direction": res[0], "entry": res[1], "sl": res[2], "tp": res[3], "adx": res[4]})
        except: pass
    
    return signals

def run_autotrade_strategy_mtf(symbol_key, pair_symbol):
    """Jalankan strategi MTF untuk auto trading"""
    candles = get_autotrade_candles(pair_symbol, "1h", 300)
    if not candles: return []
    
    closes = [float(c['close']) for c in candles]
    highs = [float(c['high']) for c in candles]
    lows = [float(c['low']) for c in candles]
    opens = [float(c['open']) for c in candles]
    
    o4, h4, l4, c4 = [], [], [], []
    for i in range(0, len(closes)-3, 4):
        o4.append(opens[i])
        h4.append(max(highs[i:i+4]))
        l4.append(min(lows[i:i+4]))
        c4.append(closes[i+3])
    
    config = AUTOTRADE_PAIR_CONFIG.get(pair_symbol, {})
    strat_list = config.get("strategies", [])
    
    signals = []
    for sname in strat_list:
        if sname not in ["S16_MTF_Breakout", "S08_MTF_BB_Walk"]:
            continue
        
        if sname == "S16_MTF_Breakout":
            func = STRATEGY_FUNCTIONS.get(sname)
        elif sname == "S08_MTF_BB_Walk":
            func = STRATEGY_FUNCTIONS.get(sname)
        else:
            continue
        
        if not func: continue
        
        try:
            res = func(opens, highs, lows, closes)
            if res and res[0] in ['BUY', 'SELL']:
                signals.append({"strategy": sname, "direction": res[0], "entry": res[1], "sl": res[2], "tp": res[3], "adx": res[4]})
        except: pass
    
    return signals

def check_sl_tp(price, positions):
    """Cek apakah ada posisi yang kena SL atau TP"""
    closed = []
    for i, pos in enumerate(positions):
        if pos["status"] != "OPEN": continue
        if pos["direction"] == "BUY":
            if price <= pos["sl"]:
                positions[i]["status"] = "CLOSED_SL"
                positions[i]["exit_price"] = pos["sl"]
                positions[i]["result"] = "LOSS"
                closed.append((i, "SL"))
            elif price >= pos["tp"]:
                positions[i]["status"] = "CLOSED_TP"
                positions[i]["exit_price"] = pos["tp"]
                positions[i]["result"] = "WIN"
                closed.append((i, "TP"))
        else:
            if price >= pos["sl"]:
                positions[i]["status"] = "CLOSED_SL"
                positions[i]["exit_price"] = pos["sl"]
                positions[i]["result"] = "LOSS"
                closed.append((i, "SL"))
            elif price <= pos["tp"]:
                positions[i]["status"] = "CLOSED_TP"
                positions[i]["exit_price"] = pos["tp"]
                positions[i]["result"] = "WIN"
                closed.append((i, "TP"))
    return closed

BOT_NAME = "AetherTrade AI"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FOREX_SYMBOLS = {
    "xauusd": "XAU/USD", "xagusd": "XAG/USD",
    "eurusd": "EUR/USD", "gbpusd": "GBP/USD", "usdjpy": "USD/JPY",
    "audusd": "AUD/USD", "usdcad": "USD/CAD", "nzdusd": "NZD/USD", "usdchf": "USD/CHF",
}
STOCK_SYMBOLS = {
    "aapl": "Apple Inc.", "msft": "Microsoft", "googl": "Alphabet",
    "tsla": "Tesla Inc.", "amzn": "Amazon", "nvda": "NVIDIA",
    "meta": "Meta", "nflx": "Netflix",
}
MEME_SYMBOLS = {
    "dogeusd": "Dogecoin", "shibusd": "Shiba Inu",
    "pepeusd": "Pepe", "wifusd": "Dogwifhat",
    "bonkusd": "Bonk", "flokiusd": "Floki Inu",
}
CRYPTO_SYMBOLS = {
    "btcusd": "Bitcoin", "ethusd": "Ethereum",
    "bnbusd": "BNB", "solusd": "Solana",
}

ALL_SYMBOLS = {**FOREX_SYMBOLS, **STOCK_SYMBOLS, **MEME_SYMBOLS, **CRYPTO_SYMBOLS}
CATEGORY_MAP = {}
for s in FOREX_SYMBOLS: CATEGORY_MAP[s] = "forex"
for s in STOCK_SYMBOLS: CATEGORY_MAP[s] = "stock"
for s in MEME_SYMBOLS: CATEGORY_MAP[s] = "meme"
for s in CRYPTO_SYMBOLS: CATEGORY_MAP[s] = "crypto"

TWELVEDATA_PAIR_MAP = {
    "xauusd": "XAU/USD", "xagusd": "XAG/USD",
    "eurusd": "EUR/USD", "gbpusd": "GBP/USD", "usdjpy": "USD/JPY",
    "audusd": "AUD/USD", "usdcad": "USD/CAD", "nzdusd": "NZD/USD", "usdchf": "USD/CHF",
}

MICIN_CHAINS = {
    "solana": {"name": "Solana", "emoji": "🟣"},
    "bsc": {"name": "BSC", "emoji": "🟡"},
    "base": {"name": "Base", "emoji": "🔷"},
    "ethereum": {"name": "Ethereum", "emoji": "🔵"},
    "arbitrum": {"name": "Arbitrum", "emoji": "🔘"},
    "polygon": {"name": "Polygon", "emoji": "🟪"},
}
NATIVE_NAMES = ['solana', 'ethereum', 'bsc', 'base', 'bnb', 'weth', 'wbnb',
                'usdc', 'usdt', 'dai', 'busd', 'wmatic', 'arb']

SAHAM_WATCHLIST = [
    "LCID", "NIO", "XPEV", "RIVN", "F", "SOFI", "HOOD", "SQ",
    "COIN", "MARA", "RIOT", "CLSK", "ACHR", "JOBY", "GME", "AMC",
    "SNAP", "PINS", "ASTS", "LUNR", "RKLB", "PLUG", "FCEL", "BE",
    "EOSE", "IONQ", "QS", "SPCE", "DNA", "CRSP", "SNDL", "TLRY",
    "CHWY", "PTON", "BYND", "BBAI", "SERV", "MVST", "UBER", "LYFT", "DKNG"
]

# Strategi existing PER PAIR (TIDAK DIHAPUS)
BEST_STRATEGIES_PER_PAIR = {
    "xauusd": ["S02_Keltner_ADX", "S01_EMA_ADX_Break", "S12_EMA20_50_Break"],
    "usdjpy": ["S04_Donchian_ADX_RSI", "S10_Stoch_ADX"],
    "audusd": ["S05_Engulf_RSI_ADX", "S06_Engulf_HA_ADX", "S04_Donchian_ADX_RSI"],
    "nzdusd": ["S05_Engulf_RSI_ADX", "S10_Stoch_ADX"],
    "usdcad": ["S02_Keltner_ADX", "S12_EMA20_50_Break", "S11_WPR_ADX"],
    "usdchf": ["S05_Engulf_RSI_ADX", "S15_HA_EMA200_ADX_RSI", "S06_Engulf_HA_ADX"],
    "eurusd": ["S08_BB_Walk_ADX", "S07_MACD_Cross_ADX", "S04_Donchian_ADX_RSI"],
    "gbpusd": ["S04_Donchian_ADX_RSI", "S08_BB_Walk_ADX"],
}

# 🆕 STRATEGI MTF TAMBAHAN per pair (tidak menghapus yg existing)
MTF_ADDITIONS = {
    "xauusd": ["S16_MTF_Breakout"],
    "usdchf": ["S16_MTF_Breakout"],
    "nzdusd": ["S16_MTF_Breakout"],
    "eurusd": ["S08_MTF_BB_Walk"],
}

UNIVERSAL_STRATEGIES = ["S02_Keltner_ADX", "S04_Donchian_ADX_RSI", "S05_Engulf_RSI_ADX", "S08_BB_Walk_ADX", "S16_Breakout_conf"]
STOCK_STRATEGIES = ["S04_Donchian_ADX_RSI", "S05_Engulf_RSI_ADX", "S07_MACD_Cross_ADX", "S08_BB_Walk_ADX", "S16_Breakout_conf",
                    "S04_MTF_Donchian", "S05_MTF_Engulf", "S08_MTF_BB_Walk", "S16_MTF_Breakout"]
CRYPTO_STRATEGIES = ["S04_Donchian_ADX_RSI", "S05_Engulf_RSI_ADX", "S16_Breakout_conf",
                     "S04_MTF_Donchian", "S05_MTF_Engulf", "S08_MTF_BB_Walk", "S16_MTF_Breakout"]

user_data = {}
user_alerts = {}
micin_cache = {}
saham_cache = {}
current_twelve_key_index = 0
current_cg_key_index = 0
current_fcs_key_index = 0

def get_next_twelve_key():
    global current_twelve_key_index
    key = TWELVE_DATA_KEYS[current_twelve_key_index]
    current_twelve_key_index = (current_twelve_key_index + 1) % len(TWELVE_DATA_KEYS)
    return key

def get_next_coingecko_key():
    global current_cg_key_index
    key = COINGECKO_KEYS[current_cg_key_index]
    current_cg_key_index = (current_cg_key_index + 1) % len(COINGECKO_KEYS)
    return key

def get_next_fcs_key():
    global current_fcs_key_index
    key = FCS_API_KEYS[current_fcs_key_index]
    current_fcs_key_index = (current_fcs_key_index + 1) % len(FCS_API_KEYS)
    return key

def get_decimals(symbol_key):
    if symbol_key in MEME_SYMBOLS: return 8
    elif symbol_key in STOCK_SYMBOLS or symbol_key in CRYPTO_SYMBOLS: return 2
    elif symbol_key in ["xauusd", "xagusd"]: return 2
    elif "jpy" in symbol_key: return 3
    return 5

def format_price(sym, price):
    if price is None: return "N/A"
    return f"${price:.{get_decimals(sym)}f}"

# ==================== INDIKATOR ATR WILDER ====================
def calc_atr_wilder(highs, lows, closes, period=14):
    if len(closes) <= period: return [0.0]*len(closes)
    atr = [0.0]*len(closes)
    tr_sum = sum(max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1])) for i in range(1, period+1))
    atr[period] = tr_sum / period
    for i in range(period+1, len(closes)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        atr[i] = (atr[i-1]*(period-1) + tr)/period
    return atr

def calc_ema(data, period):
    if len(data) < period: return 0.0
    mult = 2/(period+1)
    ema = sum(data[:period])/period
    for x in data[period:]:
        ema = (x - ema)*mult + ema
    return ema

def calc_adx(highs, lows, closes, period=14):
    if len(closes) < period*2: return 0.0
    tr = [0.0]*len(closes); dp = [0.0]*len(closes); dm = [0.0]*len(closes)
    for i in range(1, len(closes)):
        tr[i] = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        up = highs[i]-highs[i-1]; down = lows[i-1]-lows[i]
        dp[i] = up if up > down and up > 0 else 0
        dm[i] = down if down > up and down > 0 else 0
    ts = sum(tr[1:period+1]); ps = sum(dp[1:period+1]); ms = sum(dm[1:period+1])
    for i in range(period+1, len(closes)):
        ts = ts - ts/period + tr[i]; ps = ps - ps/period + dp[i]; ms = ms - ms/period + dm[i]
    atr_val = ts/period
    di_plus = (ps/atr_val*100) if atr_val else 0; di_minus = (ms/atr_val*100) if atr_val else 0
    dx = abs(di_plus - di_minus)/(di_plus + di_minus)*100 if (di_plus + di_minus) else 0
    return dx

def calc_rsi_hybrid(closes, period=14):
    if len(closes) < period+1: return 50.0
    gains = [max(closes[i]-closes[i-1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i-1]-closes[i], 0) for i in range(1, len(closes))]
    avg_gain = sum(gains[:period])/period; avg_loss = sum(losses[:period])/period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain*(period-1) + gains[i])/period
        avg_loss = (avg_loss*(period-1) + losses[i])/period
    if avg_loss == 0: return 100.0
    return 100 - (100/(1 + avg_gain/avg_loss))

def calc_donchian(highs, lows, period=20):
    if len(highs) < period: return 0.0, 0.0
    return max(highs[-period:]), min(lows[-period:])

def calc_bollinger(closes, period=20, std=2):
    if len(closes) < period: return 0.0, 0.0, 0.0
    window = closes[-period:]
    sma = sum(window)/period
    variance = sum((x-sma)**2 for x in window)/period
    std_val = variance**0.5
    return sma + std*std_val, sma, sma - std*std_val

def calc_macd(closes, fast=12, slow=26):
    ef = calc_ema(closes, fast); es = calc_ema(closes, slow)
    return ef - es if ef and es else 0.0

def calc_wpr(highs, lows, closes, period=14):
    idx = len(closes)-1
    if idx < period-1: return -50.0
    hh = max(highs[idx-period+1:idx+1]); ll = min(lows[idx-period+1:idx+1])
    if hh == ll: return 0.0
    return -100*(hh - closes[-1])/(hh-ll)

def calc_stoch(highs, lows, closes, period=14):
    idx = len(closes)-1
    if idx < period-1: return 50.0
    hh = max(highs[idx-period+1:idx+1]); ll = min(lows[idx-period+1:idx+1])
    if hh == ll: return 50.0
    return 100*(closes[-1]-ll)/(hh-ll)

def calc_heiken_ashi(opens, highs, lows, closes):
    if len(opens) < 3: return None, None
    ha_close = [(opens[i]+highs[i]+lows[i]+closes[i])/4 for i in range(len(closes))]
    ha_open = [0.0]*len(closes)
    ha_open[0] = opens[0]
    for i in range(1, len(closes)): ha_open[i] = (ha_open[i-1]+ha_close[i-1])/2
    return ha_open[-1], ha_close[-1]

# ==================== 12 STRATEGI EXISTING (TIDAK DIHAPUS) ====================
def signal_S01_EMA_ADX_Break(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); ema200 = calc_ema(closes, 200)
    if adx_val < 20 or not ema200: return None
    hn = max(highs[-61:-1]) if len(highs) >= 61 else max(highs[:-1])
    ln = min(lows[-61:-1]) if len(lows) >= 61 else min(lows[:-1])
    if closes[-2] > hn and closes[-1] > ema200:
        sl = closes[-1] - atr_val*1.2; tp = closes[-1] + atr_val*2.5
        if sl < closes[-1] and tp > closes[-1]: return ("BUY", closes[-1], sl, tp, adx_val)
    elif closes[-2] < ln and closes[-1] < ema200:
        sl = closes[-1] + atr_val*1.2; tp = closes[-1] - atr_val*2.5
        if sl > closes[-1] and tp < closes[-1]: return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S02_Keltner_ADX(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); ema20 = calc_ema(closes, 20)
    ku = ema20 + 1.5*atr_val if ema20 else 0; kl = ema20 - 1.5*atr_val if ema20 else 0
    if adx_val < 25 or not ema20: return None
    hn = max(highs[-51:-1]) if len(highs) >= 51 else max(highs[:-1])
    ln = min(lows[-51:-1]) if len(lows) >= 51 else min(lows[:-1])
    if closes[-1] > ku and closes[-2] > hn:
        sl = closes[-1] - atr_val*1.2; tp = closes[-1] + atr_val*3.0
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif closes[-1] < kl and closes[-2] < ln:
        sl = closes[-1] + atr_val*1.2; tp = closes[-1] - atr_val*3.0
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S04_Donchian_ADX_RSI(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); rsi_val = calc_rsi_hybrid(closes)
    du, dl = calc_donchian(highs, lows, 20)
    if adx_val < 25: return None
    if closes[-1] > du and rsi_val > 55:
        sl = closes[-1] - atr_val*1.5; tp = closes[-1] + atr_val*3.0
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif closes[-1] < dl and rsi_val < 45:
        sl = closes[-1] + atr_val*1.5; tp = closes[-1] - atr_val*3.0
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S05_Engulf_RSI_ADX(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); rsi_val = calc_rsi_hybrid(closes)
    if adx_val < 25: return None
    bull = closes[-1] > opens[-1] and closes[-2] < opens[-2] and opens[-1] <= closes[-2] and closes[-1] >= opens[-2]
    bear = closes[-1] < opens[-1] and closes[-2] > opens[-2] and opens[-1] >= closes[-2] and closes[-1] <= opens[-2]
    if bull and rsi_val > 60:
        sl = closes[-1] - atr_val*1.0; tp = closes[-1] + atr_val*3.0
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif bear and rsi_val < 40:
        sl = closes[-1] + atr_val*1.0; tp = closes[-1] - atr_val*3.0
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S06_Engulf_HA_ADX(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes)
    ha_open, ha_close = calc_heiken_ashi(opens, highs, lows, closes)
    if adx_val < 25 or ha_open is None: return None
    bull = closes[-1] > opens[-1] and closes[-2] < opens[-2] and opens[-1] <= closes[-2] and closes[-1] >= opens[-2]
    bear = closes[-1] < opens[-1] and closes[-2] > opens[-2] and opens[-1] >= closes[-2] and closes[-1] <= opens[-2]
    ha_bull = ha_close > ha_open; ha_bear = ha_close < ha_open
    if bull and ha_bull:
        sl = closes[-1] - atr_val*1.0; tp = closes[-1] + atr_val*3.0
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif bear and ha_bear:
        sl = closes[-1] + atr_val*1.0; tp = closes[-1] - atr_val*3.0
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S07_MACD_Cross_ADX(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); macd_val = calc_macd(closes)
    if adx_val < 25 or macd_val == 0: return None
    if macd_val > 0:
        sl = closes[-1] - atr_val*1.2; tp = closes[-1] + atr_val*2.5
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif macd_val < 0:
        sl = closes[-1] + atr_val*1.2; tp = closes[-1] - atr_val*2.5
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S08_BB_Walk_ADX(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes)
    bb_upper, _, bb_lower = calc_bollinger(closes)
    if adx_val < 25: return None
    if closes[-1] > bb_upper:
        sl = closes[-1] - atr_val*1.5; tp = closes[-1] + atr_val*3.0
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif closes[-1] < bb_lower:
        sl = closes[-1] + atr_val*1.5; tp = closes[-1] - atr_val*3.0
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S10_Stoch_ADX(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); stoch_val = calc_stoch(highs, lows, closes)
    if adx_val < 25: return None
    hn = max(highs[-51:-1]) if len(highs) >= 51 else max(highs[:-1])
    ln = min(lows[-51:-1]) if len(lows) >= 51 else min(lows[:-1])
    if stoch_val > 80 and closes[-2] > hn:
        sl = closes[-1] - atr_val*1.2; tp = closes[-1] + atr_val*2.5
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif stoch_val < 20 and closes[-2] < ln:
        sl = closes[-1] + atr_val*1.2; tp = closes[-1] - atr_val*2.5
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S11_WPR_ADX(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); wpr_val = calc_wpr(highs, lows, closes)
    if adx_val < 25: return None
    hn = max(highs[-51:-1]) if len(highs) >= 51 else max(highs[:-1])
    ln = min(lows[-51:-1]) if len(lows) >= 51 else min(lows[:-1])
    if wpr_val > -20 and closes[-2] > hn:
        sl = closes[-1] - atr_val*1.2; tp = closes[-1] + atr_val*2.5
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif wpr_val < -80 and closes[-2] < ln:
        sl = closes[-1] + atr_val*1.2; tp = closes[-1] - atr_val*2.5
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S12_EMA20_50_Break(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); ema20 = calc_ema(closes, 20); ema50 = calc_ema(closes, 50)
    if adx_val < 25 or not ema20 or not ema50: return None
    hn = max(highs[-51:-1]) if len(highs) >= 51 else max(highs[:-1])
    ln = min(lows[-51:-1]) if len(lows) >= 51 else min(lows[:-1])
    if ema20 > ema50 and closes[-2] > hn:
        sl = closes[-1] - atr_val*1.2; tp = closes[-1] + atr_val*2.5
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif ema20 < ema50 and closes[-2] < ln:
        sl = closes[-1] + atr_val*1.2; tp = closes[-1] - atr_val*2.5
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S15_HA_EMA200_ADX_RSI(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); rsi_val = calc_rsi_hybrid(closes); ema200 = calc_ema(closes, 200)
    ha_open, ha_close = calc_heiken_ashi(opens, highs, lows, closes)
    if adx_val < 20 or not ema200 or ha_open is None: return None
    hn = max(highs[-21:-1]) if len(highs) >= 21 else max(highs[:-1])
    ln = min(lows[-21:-1]) if len(lows) >= 21 else min(lows[:-1])
    ha_bull = ha_close > ha_open; ha_bear = ha_close < ha_open
    if ha_bull and closes[-2] > hn and closes[-1] > ema200 and rsi_val > 55:
        sl = closes[-1] - atr_val*1.0; tp = closes[-1] + atr_val*3.0
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif ha_bear and closes[-2] < ln and closes[-1] < ema200 and rsi_val < 45:
        sl = closes[-1] + atr_val*1.0; tp = closes[-1] - atr_val*3.0
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

def signal_S16_Breakout_conf(opens, highs, lows, closes):
    atr_arr = calc_atr_wilder(highs, lows, closes); atr_val = atr_arr[-1]
    adx_val = calc_adx(highs, lows, closes); ema200 = calc_ema(closes, 200)
    if adx_val < 25 or not ema200: return None
    hn = max(highs[-51:-1]) if len(highs) >= 51 else max(highs[:-1])
    ln = min(lows[-51:-1]) if len(lows) >= 51 else min(lows[:-1])
    if closes[-2] > hn and closes[-1] > ema200 and closes[-1] > opens[-1]:
        sl = closes[-1] - atr_val*1.5; tp = closes[-1] + atr_val*2.0
        return ("BUY", closes[-1], sl, tp, adx_val)
    elif closes[-2] < ln and closes[-1] < ema200 and closes[-1] < opens[-1]:
        sl = closes[-1] + atr_val*1.5; tp = closes[-1] - atr_val*2.0
        return ("SELL", closes[-1], sl, tp, adx_val)
    return None

# ==================== 🆕 4 STRATEGI MTF ====================
def signal_S16_MTF_Breakout(opens_1h, highs_1h, lows_1h, closes_1h):
    """S16_MTF_Breakout: Breakout 50 + EMA200 + ADX>25 + Filter 4H EMA50"""
    opens_4h, highs_4h, lows_4h, closes_4h = resample_4h(opens_1h, highs_1h, lows_1h, closes_1h)
    if len(closes_4h) < 60: return None
    
    atr_arr_1h = calc_atr_wilder(highs_1h, lows_1h, closes_1h); atr_val = atr_arr_1h[-1]
    adx_val = calc_adx(highs_1h, lows_1h, closes_1h)
    ema200_1h = calc_ema(closes_1h, 200)
    ema50_4h = calc_ema(closes_4h, 50)
    
    if adx_val < 25 or not ema200_1h or not ema50_4h: return None
    
    # Konversi index 1H ke 4H
    idx_4h = min(len(closes_4h)-2, (len(closes_1h)-1)//4)
    if idx_4h < 20: return None
    trend_4h = closes_4h[idx_4h] > ema50_4h
    
    hn = max(highs_1h[-51:-1]) if len(highs_1h) >= 51 else max(highs_1h[:-1])
    ln = min(lows_1h[-51:-1]) if len(lows_1h) >= 51 else min(lows_1h[:-1])
    
    if closes_1h[-2] > hn and closes_1h[-1] > ema200_1h and closes_1h[-1] > opens_1h[-1] and trend_4h:
        sl = closes_1h[-1] - atr_val*1.5; tp = closes_1h[-1] + atr_val*2.0
        return ("BUY", closes_1h[-1], sl, tp, adx_val)
    elif closes_1h[-2] < ln and closes_1h[-1] < ema200_1h and closes_1h[-1] < opens_1h[-1] and not trend_4h:
        sl = closes_1h[-1] + atr_val*1.5; tp = closes_1h[-1] - atr_val*2.0
        return ("SELL", closes_1h[-1], sl, tp, adx_val)
    return None

def signal_S08_MTF_BB_Walk(opens_1h, highs_1h, lows_1h, closes_1h):
    """S08_MTF_BB_Walk: BB Walk + ADX>25 + Filter 4H EMA50"""
    opens_4h, highs_4h, lows_4h, closes_4h = resample_4h(opens_1h, highs_1h, lows_1h, closes_1h)
    if len(closes_4h) < 60: return None
    
    atr_arr_1h = calc_atr_wilder(highs_1h, lows_1h, closes_1h); atr_val = atr_arr_1h[-1]
    adx_val = calc_adx(highs_1h, lows_1h, closes_1h)
    bb_upper, _, bb_lower = calc_bollinger(closes_1h)
    ema50_4h = calc_ema(closes_4h, 50)
    
    if adx_val < 25 or not ema50_4h: return None
    
    idx_4h = min(len(closes_4h)-2, (len(closes_1h)-1)//4)
    if idx_4h < 20: return None
    trend_4h = closes_4h[idx_4h] > ema50_4h
    
    if closes_1h[-1] > bb_upper and closes_1h[-2] > calc_bollinger(closes_1h[:-1])[0] and trend_4h:
        sl = closes_1h[-1] - atr_val*1.5; tp = closes_1h[-1] + atr_val*3.0
        return ("BUY", closes_1h[-1], sl, tp, adx_val)
    elif closes_1h[-1] < bb_lower and closes_1h[-2] < calc_bollinger(closes_1h[:-1])[2] and not trend_4h:
        sl = closes_1h[-1] + atr_val*1.5; tp = closes_1h[-1] - atr_val*3.0
        return ("SELL", closes_1h[-1], sl, tp, adx_val)
    return None

def signal_S04_MTF_Donchian(opens_1h, highs_1h, lows_1h, closes_1h):
    """S04_MTF_Donchian: Donchian + RSI + ADX>25 + Filter 4H EMA50"""
    opens_4h, highs_4h, lows_4h, closes_4h = resample_4h(opens_1h, highs_1h, lows_1h, closes_1h)
    if len(closes_4h) < 60: return None
    
    atr_arr_1h = calc_atr_wilder(highs_1h, lows_1h, closes_1h); atr_val = atr_arr_1h[-1]
    adx_val = calc_adx(highs_1h, lows_1h, closes_1h)
    rsi_val = calc_rsi_hybrid(closes_1h)
    du, dl = calc_donchian(highs_1h, lows_1h, 20)
    ema50_4h = calc_ema(closes_4h, 50)
    
    if adx_val < 25 or not ema50_4h: return None
    
    idx_4h = min(len(closes_4h)-2, (len(closes_1h)-1)//4)
    if idx_4h < 20: return None
    trend_4h = closes_4h[idx_4h] > ema50_4h
    
    if closes_1h[-1] > du and rsi_val > 55 and trend_4h:
        sl = closes_1h[-1] - atr_val*1.5; tp = closes_1h[-1] + atr_val*3.0
        return ("BUY", closes_1h[-1], sl, tp, adx_val)
    elif closes_1h[-1] < dl and rsi_val < 45 and not trend_4h:
        sl = closes_1h[-1] + atr_val*1.5; tp = closes_1h[-1] - atr_val*3.0
        return ("SELL", closes_1h[-1], sl, tp, adx_val)
    return None

def signal_S05_MTF_Engulf(opens_1h, highs_1h, lows_1h, closes_1h):
    """S05_MTF_Engulf: Engulfing + RSI + ADX>25 + Filter 4H EMA50"""
    opens_4h, highs_4h, lows_4h, closes_4h = resample_4h(opens_1h, highs_1h, lows_1h, closes_1h)
    if len(closes_4h) < 60: return None
    
    atr_arr_1h = calc_atr_wilder(highs_1h, lows_1h, closes_1h); atr_val = atr_arr_1h[-1]
    adx_val = calc_adx(highs_1h, lows_1h, closes_1h)
    rsi_val = calc_rsi_hybrid(closes_1h)
    ema50_4h = calc_ema(closes_4h, 50)
    
    if adx_val < 25 or not ema50_4h: return None
    
    idx_4h = min(len(closes_4h)-2, (len(closes_1h)-1)//4)
    if idx_4h < 20: return None
    trend_4h = closes_4h[idx_4h] > ema50_4h
    
    bull = closes_1h[-1] > opens_1h[-1] and closes_1h[-2] < opens_1h[-2] and opens_1h[-1] <= closes_1h[-2] and closes_1h[-1] >= opens_1h[-2]
    bear = closes_1h[-1] < opens_1h[-1] and closes_1h[-2] > opens_1h[-2] and opens_1h[-1] >= closes_1h[-2] and closes_1h[-1] <= opens_1h[-2]
    
    if bull and rsi_val > 60 and trend_4h:
        sl = closes_1h[-1] - atr_val*1.0; tp = closes_1h[-1] + atr_val*3.0
        return ("BUY", closes_1h[-1], sl, tp, adx_val)
    elif bear and rsi_val < 40 and not trend_4h:
        sl = closes_1h[-1] + atr_val*1.0; tp = closes_1h[-1] - atr_val*3.0
        return ("SELL", closes_1h[-1], sl, tp, adx_val)
    return None

def resample_4h(opens_1h, highs_1h, lows_1h, closes_1h):
    """Resample data 1H ke 4H"""
    o4, h4, l4, c4 = [], [], [], []
    for i in range(0, len(closes_1h)-3, 4):
        o4.append(opens_1h[i])
        h4.append(max(highs_1h[i:i+4]))
        l4.append(min(lows_1h[i:i+4]))
        c4.append(closes_1h[i+3])
    return o4, h4, l4, c4

# ==================== STRATEGI BARU (S17 & S20) ====================

def signal_S17_EMA_Dist(opens, highs, lows, closes):
    """
    Strategi khusus XAU/USD & BTC/USD
    Entry: Harga menjauh >1% dari EMA50 (mean reversion)
    BUY: Harga di bawah EMA50 → TP = EMA50, SL = 0.5 ATR
    SELL: Harga di atas EMA50 → TP = EMA50, SL = 0.5 ATR
    """
    atr_arr = calc_atr_wilder(highs, lows, closes)
    atr_val = atr_arr[-1] if atr_arr else 0
    ema50 = calc_ema(closes, 50)
    
    if not ema50 or atr_val == 0:
        return None
    
    price = closes[-1]
    dist = abs(price - ema50) / ema50 * 100
    
    if dist > 1.0:
        if price < ema50:
            sl = price - atr_val * 0.5
            tp = ema50
            if sl < price and tp > price:
                return ("BUY", price, sl, tp, 30.0)
        else:
            sl = price + atr_val * 0.5
            tp = ema50
            if sl > price and tp < price:
                return ("SELL", price, sl, tp, 30.0)
    
    return None


def signal_S20_AllInOne(opens, highs, lows, closes):
    """
    Strategi umum untuk 8 pair forex
    Entry: Minimal 2 dari 4 indikator setuju
    Indikator: RSI, Stochastic, MACD, ADX
    BUY: 2+ bullish → TP = 1.5 ATR, SL = 0.5 ATR
    SELL: 2+ bearish → TP = 1.5 ATR, SL = 0.5 ATR
    """
    atr_arr = calc_atr_wilder(highs, lows, closes)
    atr_val = atr_arr[-1] if atr_arr else 0
    
    if atr_val == 0:
        return None
    
    rsi_val = calc_rsi_hybrid(closes)
    stoch_val = calc_stoch(highs, lows, closes)
    macd_val = calc_macd(closes)
    adx_val = calc_adx(highs, lows, closes)
    
    price = closes[-1]
    
    buy_count = 0
    sell_count = 0
    
    # RSI
    if rsi_val < 40:
        buy_count += 1
    if rsi_val > 60:
        sell_count += 1
    
    # Stochastic
    if stoch_val < 20:
        buy_count += 1
    if stoch_val > 80:
        sell_count += 1
    
    # MACD
    if macd_val > 0:
        buy_count += 1
    if macd_val < 0:
        sell_count += 1
    
    # ADX + Price direction
    if adx_val > 20 and len(closes) >= 2:
        if closes[-1] > closes[-2]:
            buy_count += 1
        elif closes[-1] < closes[-2]:
            sell_count += 1
    
    if buy_count >= 2:
        sl = price - atr_val * 0.5
        tp = price + atr_val * 1.5
        if sl < price and tp > price:
            return ("BUY", price, sl, tp, adx_val)
    
    if sell_count >= 2:
        sl = price + atr_val * 0.5
        tp = price - atr_val * 1.5
        if sl > price and tp < price:
            return ("SELL", price, sl, tp, adx_val)
    
    return None

# ==================== 🆕 3 STRATEGI OVERPOWER ====================
# 🆕 Keltner Channel helper (digunakan oleh S04_KC_Scalp)
def calc_keltner_channel(highs, lows, closes, period=20, mult=1.5):
    """Hitung Keltner Channel: Upper dan Lower band"""
    atr_arr = calc_atr_wilder(highs, lows, closes)
    ema_arr = [0.0] * len(closes)
    # Hitung EMA
    ema_val = calc_ema(closes, period)
    # Hitung full array
    upper = [0.0] * len(closes)
    lower = [0.0] * len(closes)
    for i in range(period, len(closes)):
        e = calc_ema(closes[:i+1], period)
        if e and atr_arr[i]:
            upper[i] = e + mult * atr_arr[i]
            lower[i] = e - mult * atr_arr[i]
    return upper, lower


def signal_S01_EMA_Tight(opens, highs, lows, closes):
    """
    📌 STRATEGI S01: EMA TIGHT (Mean Reversion)
    DIGUNAKAN UNTUK: XAU/USD, BTC/USD, NZD/USD
    Entry saat harga menjauh >0.5% dari EMA50
    BUY: harga di bawah EMA50, TP = EMA50, SL = 0.3 ATR
    SELL: harga di atas EMA50, TP = EMA50, SL = 0.3 ATR
    """
    atr_arr = calc_atr_wilder(highs, lows, closes)
    atr_val = atr_arr[-1] if atr_arr else 0
    ema50 = calc_ema(closes, 50)
    
    if not ema50 or atr_val == 0:
        return None
    
    price = closes[-1]
    dist = abs(price - ema50) / ema50 * 100
    
    if dist > 0.5:
        if price < ema50:
            sl = price - atr_val * 0.3
            tp = ema50
            if sl < price and tp > price:
                return ("BUY", price, sl, tp, 25.0)
        else:
            sl = price + atr_val * 0.3
            tp = ema50
            if sl > price and tp < price:
                return ("SELL", price, sl, tp, 25.0)
    
    return None


def signal_S02_AllInOne_Agg(opens, highs, lows, closes):
    """
    📌 STRATEGI S02: ALL-IN-ONE AGRESIF (Multi-Indikator)
    DIGUNAKAN UNTUK: EUR/USD, USD/JPY, AUD/USD, USD/CAD, EUR/JPY, GBP/JPY
    Entry jika minimal 2 dari 4 indikator setuju
    Indikator: RSI(<45/>55), Stochastic(<30/>70), MACD, ADX(>15)
    BUY: 2+ bullish, TP = 1.0 ATR, SL = 0.3 ATR
    SELL: 2+ bearish, TP = 1.0 ATR, SL = 0.3 ATR
    """
    atr_arr = calc_atr_wilder(highs, lows, closes)
    atr_val = atr_arr[-1] if atr_arr else 0
    
    if atr_val == 0:
        return None
    
    rsi_val = calc_rsi_hybrid(closes)
    stoch_val = calc_stoch(highs, lows, closes)
    macd_val = calc_macd(closes)
    adx_val = calc_adx(highs, lows, closes)
    
    price = closes[-1]
    buy_count = 0
    sell_count = 0
    
    if rsi_val < 45: buy_count += 1
    if rsi_val > 55: sell_count += 1
    if stoch_val < 30: buy_count += 1
    if stoch_val > 70: sell_count += 1
    if macd_val > 0: buy_count += 1
    if macd_val < 0: sell_count += 1
    if adx_val > 15:
        if len(closes) >= 2 and closes[-1] > closes[-2]: buy_count += 1
        elif len(closes) >= 2 and closes[-1] < closes[-2]: sell_count += 1
    
    if buy_count >= 2:
        sl = price - atr_val * 0.3
        tp = price + atr_val * 1.0
        if sl < price and tp > price:
            return ("BUY", price, sl, tp, adx_val)
    
    if sell_count >= 2:
        sl = price + atr_val * 0.3
        tp = price - atr_val * 1.0
        if sl > price and tp < price:
            return ("SELL", price, sl, tp, adx_val)
    
    return None


def signal_S04_KC_Scalp(opens, highs, lows, closes):
    """
    📌 STRATEGI S04: KELTNER CHANNEL SCALP
    DIGUNAKAN UNTUK: USD/CHF, GBP/USD
    Entry saat harga menyentuh Keltner Channel
    BUY: harga di bawah lower band, TP = EMA20, SL = 0.3 ATR
    SELL: harga di atas upper band, TP = EMA20, SL = 0.3 ATR
    """
    atr_arr = calc_atr_wilder(highs, lows, closes)
    atr_val = atr_arr[-1] if atr_arr else 0
    ema20 = calc_ema(closes, 20)
    ku_arr, kl_arr = calc_keltner_channel(highs, lows, closes)
    
    if atr_val == 0 or not ema20 or len(ku_arr) < 30:
        return None
    
    price = closes[-1]
    ku = ku_arr[-1]
    kl = kl_arr[-1]
    
    if kl == 0 or ku == 0:
        return None
    
    if price < kl:
        sl = price - atr_val * 0.3
        tp = ema20
        if sl < price and tp > price:
            return ("BUY", price, sl, tp, 20.0)
    elif price > ku:
        sl = price + atr_val * 0.3
        tp = ema20
        if sl > price and tp < price:
            return ("SELL", price, sl, tp, 20.0)
    
    return None

# Registry strategi (existing + MTF)
STRATEGY_FUNCTIONS = {
    "S01_EMA_ADX_Break": signal_S01_EMA_ADX_Break,
    "S02_Keltner_ADX": signal_S02_Keltner_ADX,
    "S04_Donchian_ADX_RSI": signal_S04_Donchian_ADX_RSI,
    "S05_Engulf_RSI_ADX": signal_S05_Engulf_RSI_ADX,
    "S06_Engulf_HA_ADX": signal_S06_Engulf_HA_ADX,
    "S07_MACD_Cross_ADX": signal_S07_MACD_Cross_ADX,
    "S08_BB_Walk_ADX": signal_S08_BB_Walk_ADX,
    "S10_Stoch_ADX": signal_S10_Stoch_ADX,
    "S11_WPR_ADX": signal_S11_WPR_ADX,
    "S12_EMA20_50_Break": signal_S12_EMA20_50_Break,
    "S15_HA_EMA200_ADX_RSI": signal_S15_HA_EMA200_ADX_RSI,
    "S16_Breakout_conf": signal_S16_Breakout_conf,
    "S16_MTF_Breakout": signal_S16_MTF_Breakout,
    "S08_MTF_BB_Walk": signal_S08_MTF_BB_Walk,
    "S04_MTF_Donchian": signal_S04_MTF_Donchian,
    "S05_MTF_Engulf": signal_S05_MTF_Engulf,
    "S17_EMA_Dist": signal_S17_EMA_Dist,
    "S20_AllInOne": signal_S20_AllInOne,
    # 🆕 3 STRATEGI OVERPOWER
    "S01_EMA_Tight": signal_S01_EMA_Tight,
    "S02_AllInOne_Agg": signal_S02_AllInOne_Agg,
    "S04_KC_Scalp": signal_S04_KC_Scalp,
}

# ==================== FUNGSI UTAMA ANALISA ====================
def get_candles(symbol, interval="1h", outputsize=300):
    if symbol in FOREX_SYMBOLS:
        pair = TWELVEDATA_PAIR_MAP.get(symbol, symbol.upper())
    elif symbol in STOCK_SYMBOLS:
        pair = symbol.upper()
    elif symbol in CRYPTO_SYMBOLS:
        pair = symbol.upper().replace("USD", "/USD")
    else:
        pair = symbol.upper()
    for attempt in range(3):
        try:
            resp = requests.get(f"https://api.twelvedata.com/time_series?symbol={pair}&interval={interval}&outputsize={outputsize}&apikey={get_next_twelve_key()}", timeout=15)
            if resp.status_code == 200 and 'values' in resp.json():
                candles = resp.json()['values']
                if len(candles) >= 100:
                    candles.reverse()
                    return candles
        except Exception as e:
            logger.error(f"Error ambil candle {pair}: {e}")
        time.sleep(2)
    return None

def get_live_price(symbol):
    if symbol in FOREX_SYMBOLS:
        pair = TWELVEDATA_PAIR_MAP.get(symbol, symbol.upper())
    elif symbol in STOCK_SYMBOLS:
        pair = symbol.upper()
    elif symbol in CRYPTO_SYMBOLS:
        pair = symbol.upper().replace("USD", "/USD")
    else:
        pair = symbol.upper()
    try:
        resp = requests.get(f"https://api.twelvedata.com/quote?symbol={pair}&apikey={get_next_twelve_key()}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if 'close' in data:
                return float(data['close'])
    except Exception as e:
        logger.error(f"Error ambil harga live {pair}: {e}")
    return None

def detect_signals(symbol, candles, strategy_list):
    closes = [float(c['close']) for c in candles]
    highs = [float(c['high']) for c in candles]
    lows = [float(c['low']) for c in candles]
    opens = [float(c['open']) for c in candles]
    signals = {}
    
    # Tentukan apakah ini pair forex (SELL diizinkan)
    is_forex = symbol in FOREX_SYMBOLS
    
    for sname in strategy_list:
        func = STRATEGY_FUNCTIONS.get(sname)
        if not func: continue
        try:
            res = func(opens, highs, lows, closes)
            if res:
                direction, entry, sl, tp, adx = res
                
                # 🆕 Filter: hanya izinkan SELL untuk forex
                if direction == "SELL" and not is_forex:
                    continue
                
                signals[sname] = {"direction": direction, "entry": entry, "sl": sl, "tp": tp, "adx": adx}
        except Exception as e:
            logger.error(f"Error strategi {sname}: {e}")
    if not signals:
        return None, {}
    best_name = max(signals, key=lambda x: signals[x]['adx'])
    best = signals[best_name]
    best['strategy_name'] = best_name
    return best, signals

def format_signal_text(best_signal, symbol):
    if not best_signal: return "⏸️ *TIDAK ADA SINYAL*\nSemua strategi (existing + MTF) tidak memberikan sinyal entry.\nMenunggu setup berikutnya..."
    d = best_signal
    rr = abs(d['tp']-d['entry'])/abs(d['sl']-d['entry']) if d['sl'] != d['entry'] else 0
    return (f"{'🟢' if d['direction']=='BUY' else '🔴'} *{d['direction']} — {d['strategy_name']}*\n"
            f"💰 Entry: {format_price(symbol, d['entry'])}\n"
            f"🛑 SL: {format_price(symbol, d['sl'])} (ATR×faktor)\n"
            f"🎯 TP: {format_price(symbol, d['tp'])} (ATR×faktor)\n"
            f"📊 ADX: {d['adx']:.1f} | RR: 1:{rr:.2f}")

def calculate_sr_levels(symbol, price, candles=None):
    """
    Hitung S/R levels dari strategi yang tersedia (Keltner, Bollinger, Donchian, EMA, Pivot)
    + Swing High/Low. Semua level diambil dari perhitungan real, bukan perkiraan AI.
    """
    if candles is None or len(candles) < 50:
        candles = get_candles(symbol, "1h", 100)
    
    if not candles or len(candles) < 50:
        return "S/R tidak tersedia (data kurang)."
    
    closes = [float(c['close']) for c in candles]
    highs = [float(c['high']) for c in candles]
    lows = [float(c['low']) for c in candles]
    opens = [float(c['open']) for c in candles]
    
    atr_arr = calc_atr_wilder(highs, lows, closes)
    atr_val = atr_arr[-1] if atr_arr else 0
    
    lines = []
    lines.append("📊 *LEVEL TEKNIKAL DARI STRATEGI:*")
    lines.append("━━━━━━━━━━━━━━━━━━━━━━")
    
    # 1. Keltner Channel (S02)
    ema20 = calc_ema(closes, 20)
    if ema20 and atr_val:
        ku = ema20 + 1.5 * atr_val
        kl = ema20 - 1.5 * atr_val
        lines.append(f"🔸 *Keltner (S02):*")
        lines.append(f"  Upper: ${ku:.2f} | Lower: ${kl:.2f}")
        lines.append(f"  EMA20: ${ema20:.2f}")
    
    # 2. Bollinger Bands (S08)
    bb_upper, bb_mid, bb_lower = calc_bollinger(closes)
    if bb_upper and bb_lower:
        lines.append(f"🔸 *Bollinger (S08):*")
        lines.append(f"  Upper: ${bb_upper:.2f} | Mid: ${bb_mid:.2f} | Lower: ${bb_lower:.2f}")
    
    # 3. Donchian Channel (S04)
    du, dl = calc_donchian(highs, lows, 20)
    if du and dl:
        lines.append(f"🔸 *Donchian 20 (S04):*")
        lines.append(f"  Upper: ${du:.2f} | Lower: ${dl:.2f}")
    
    # 4. EMA Levels
    ema50 = calc_ema(closes, 50)
    ema200 = calc_ema(closes, 200)
    if ema50 or ema200:
        lines.append(f"🔸 *EMA Levels:*")
        if ema50: lines.append(f"  EMA50: ${ema50:.2f}")
        if ema200: lines.append(f"  EMA200: ${ema200:.2f}")
    
    # 5. Daily Pivot (dari candle kemarin)
    if len(highs) >= 3:
        prev_h = highs[-2]
        prev_l = lows[-2]
        prev_c = closes[-2]
        pp = (prev_h + prev_l + prev_c) / 3
        r1 = 2*pp - prev_l
        s1 = 2*pp - prev_h
        lines.append(f"🔸 *Daily Pivot:*")
        lines.append(f"  PP: ${pp:.2f} | R1: ${r1:.2f} | S1: ${s1:.2f}")
    
    # 6. Swing High/Low
    swing_highs = []
    swing_lows = []
    for i in range(2, min(len(highs)-2, 72)):
        if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
            if highs[i] > price:
                swing_highs.append(highs[i])
        if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
            if lows[i] < price:
                swing_lows.append(lows[i])
    
    swing_highs = sorted(set(round(h, 2) for h in swing_highs))[:3]
    swing_lows = sorted(set(round(l, 2) for l in swing_lows), reverse=True)[:3]
    
    if swing_highs or swing_lows:
        lines.append(f"🔸 *Swing Levels (1H):*")
        if swing_highs:
            lines.append(f"  Resistance: " + " | ".join([f"${h:.2f}" for h in swing_highs]))
        if swing_lows:
            lines.append(f"  Support: " + " | ".join([f"${l:.2f}" for l in swing_lows]))
    
    # 7. Psychological Levels
    if symbol in ["xauusd", "xagusd"]:
        tier = 50 if symbol == "xauusd" else 5
    elif "jpy" in symbol:
        tier = 1
    else:
        tier = 0.01
    
    below = (price // tier) * tier
    above = below + tier
    lines.append(f"🔸 *Psychological:*")
    lines.append(f"  Below: ${below:.2f} | Above: ${above:.2f}")
    
    return "\n".join(lines)

def ai_analyze(symbol, price, best_signal, signal_text, fundamental_text, category="forex"):
    price_str = format_price(symbol, price)
    cat_label = {"forex": "Forex", "stock": "Saham", "crypto": "Crypto"}.get(category, "Aset")
    has_signal = best_signal is not None and best_signal.get('direction') in ['BUY', 'SELL']
    
    # Dapatkan S/R levels dari strategi
    sr_text = calculate_sr_levels(symbol, price, candles=None)
    
    if has_signal:
        prompt = (
            f"Anda adalah analis {cat_label} profesional. Analisis {symbol.upper()}.\n\n"
            f"HARGA SAAT INI: {price_str}\n"
            f"WAJIB gunakan harga {price_str} sebagai acuan. JANGAN mengarang harga lain.\n\n"
            f"{signal_text}\n\n"
            f"{sr_text}\n\n"
            f"Fundamental:\n{fundamental_text}\n\n"
            f"Tugas Anda:\n"
            f"- Berikan analisa SINGKAT (maks 200 kata) dalam Bahasa Indonesia.\n"
            f"- Sertakan Rekomendasi, Entry, SL, TP MENGIKUTI sinyal di atas.\n"
            f"- Jelaskan alasan teknikal dan fundamental secara ringkas.\n"
            f"- Akhiri dengan kalimat motivasi trading yang bijak."
        )
    else:
        prompt = (
            f"Anda adalah analis {cat_label} profesional. Analisis {symbol.upper()}.\n\n"
            f"HARGA SAAT INI: {price_str}\n"
            f"WAJIB gunakan harga {price_str} sebagai acuan. JANGAN mengarang harga lain.\n\n"
            f"STATUS: TIDAK ADA SINYAL STRATEGI yang valid saat ini.\n"
            f"Semua strategi (existing + MTF) tidak memberikan sinyal entry.\n\n"
            f"{sr_text}\n\n"
            f"Fundamental:\n{fundamental_text}\n\n"
            f"Tugas Anda — berikan analisa yang MENARIK dan INFORMATIF (maks 200 kata) dalam Bahasa Indonesia:\n"
            f"1. Jelaskan KONDISI PASAR saat ini berdasarkan harga {price_str}.\n"
            f"2. Sebutkan 2-3 LEVEL RESISTANCE dan SUPPORT TERDEKAT dari data teknikal di atas (WAJIB spesifik nominalnya).\n"
            f"3. Jelaskan strategi mana yang PALING RELEVAN untuk situasi ini dan apa yang perlu terjadi agar sinyal muncul.\n"
            f"   Contoh: 'Jika harga breakout di atas Keltner Upper, S02 akan memberi sinyal BUY.'\n"
            f"   Atau: 'Jika engulfing bullish muncul di dekat Donchian Lower, S05 bisa memberi sinyal BUY.'\n"
            f"4. Rekomendasikan HOLD dengan alasan yang jelas.\n"
            f"5. JANGAN memberikan Entry, SL, atau TP spesifik.\n"
            f"6. Akhiri dengan kalimat motivasi trading yang bijak dan relevan."
        )
    
    try:
        resp = requests.post(MAIA_ENDPOINT,
                             headers={"Authorization": f"Bearer {MAIA_API_KEY}", "Content-Type": "application/json"},
                             json={"model": MAIA_MODEL, "messages": [{"role": "user", "content": prompt}],
                                   "temperature": 0.3 if has_signal else 0.6, "max_tokens": 450}, timeout=25)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error(f"AI error: {e}")
    return "⚠️ AI tidak tersedia, gunakan sinyal teknikal."

def get_news(symbol):
    try:
        r = requests.get(f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}", timeout=10)
        if r.status_code == 200:
            articles = r.json()
            return "\n".join([f"📰 {a['headline'][:80]}" for a in articles[:2]]) if articles else "Tidak ada berita"
    except: pass
    return "Tidak ada berita"

def get_economic_calendar():
    today = datetime.now(); items = []
    for i in range(7):
        day = today + timedelta(days=i)
        if day.weekday() == 4 and day.day <= 7: items.append(f"{day.strftime('%d %b')}: Non-Farm Payrolls (US)")
        if 10 <= day.day <= 14 and day.weekday() in [2,3,4]: items.append(f"{day.strftime('%d %b')}: CPI (US)")
    return "\n".join(items) if items else "Tidak ada data penting"

# FULL CODE FINAL - AetherTrade AI - PART 2/2
# Sambungan dari Part 1/2 - Simpan sebagai lanjutan bot.py
# Pastikan PART 1 sudah di-copy terlebih dahulu

# ==================== DATABASE ====================
def init_db():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscriptions (
        chat_id INTEGER PRIMARY KEY, username TEXT, plan TEXT,
        start_time TEXT, end_time TEXT, is_active INTEGER DEFAULT 1, source TEXT DEFAULT 'manual')''')
    c.execute('''CREATE TABLE IF NOT EXISTS vouchers (
        code TEXT PRIMARY KEY, plan TEXT, created_by INTEGER,
        used_by INTEGER, used_at TEXT, is_used INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alerts (
        chat_id INTEGER, symbol TEXT, PRIMARY KEY (chat_id, symbol))''')
    c.execute('''CREATE TABLE IF NOT EXISTS watchlists (
        chat_id INTEGER, symbol TEXT, PRIMARY KEY (chat_id, symbol))''')
    
    # 🆕 Tabel untuk menyimpan history analisa user (persistent)
    c.execute('''CREATE TABLE IF NOT EXISTS analysis_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        symbol TEXT,
        recommendation TEXT,
        entry REAL,
        sl REAL,
        tp REAL,
        timestamp TEXT
    )''')
    
    # 🆕 Tabel untuk menyimpan auto trade state (persistent)
    c.execute('''CREATE TABLE IF NOT EXISTS autotrade_save (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        active INTEGER DEFAULT 0,
        mode TEXT DEFAULT 'paper',
        balance REAL DEFAULT 1000.0,
        starting_balance REAL DEFAULT 1000.0,
        total_trades INTEGER DEFAULT 0,
        total_wins INTEGER DEFAULT 0,
        total_losses INTEGER DEFAULT 0,
        active_pairs TEXT DEFAULT '',
        lot_config TEXT DEFAULT '{}',
        updated_at TEXT
    )''')
    
    # Pastikan ada 1 baris untuk autotrade state
    c.execute("INSERT OR IGNORE INTO autotrade_save (id, updated_at) VALUES (1, ?)", (datetime.now().isoformat(),))
    
    conn.commit(); conn.close()
    load_alerts_from_db(); load_watchlists_from_db()
    load_analysis_history_from_db()  # 🆕 Load history analisa
    load_autotrade_state_from_db()   # 🆕 Load auto trade state

def load_alerts_from_db():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT chat_id, symbol FROM alerts")
    for chat_id, symbol in c.fetchall():
        if chat_id not in user_alerts: user_alerts[chat_id] = {'symbols': set(), 'sent': {}}
        user_alerts[chat_id]['symbols'].add(symbol)
    conn.close()

def save_alert_to_db(chat_id, symbol):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO alerts (chat_id, symbol) VALUES (?, ?)", (chat_id, symbol))
    conn.commit(); conn.close()

def remove_alert_from_db(chat_id, symbol):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("DELETE FROM alerts WHERE chat_id=? AND symbol=?", (chat_id, symbol))
    conn.commit(); conn.close()

def load_watchlists_from_db():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT chat_id, symbol FROM watchlists")
    for chat_id, symbol in c.fetchall():
        if chat_id not in user_data: user_data[chat_id] = {'history': [], 'watchlist': set(), 'last_analysis': None}
        user_data[chat_id]['watchlist'].add(symbol)
    conn.close()
    
# ==================== 🆕 PERSISTENT STORAGE ====================

def save_analysis_to_db(chat_id, symbol, recommendation, entry=None, sl=None, tp=None):
    """Simpan history analisa ke database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO analysis_history (chat_id, symbol, recommendation, entry, sl, tp, timestamp) VALUES (?,?,?,?,?,?,?)",
              (chat_id, symbol, recommendation, entry, sl, tp, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def load_analysis_history_from_db():
    """Load history analisa dari database ke memory"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT chat_id, symbol, recommendation, entry, sl, tp, timestamp FROM analysis_history ORDER BY id DESC LIMIT 500")
    rows = c.fetchall()
    conn.close()
    
    for chat_id, symbol, rec, entry, sl, tp, ts in rows:
        if chat_id not in user_data:
            user_data[chat_id] = {'history': [], 'watchlist': set(), 'last_analysis': None}
        user_data[chat_id]['history'].append({
            'symbol': symbol,
            'recommendation': rec,
            'timestamp': datetime.fromisoformat(ts),
            'entry': entry,
            'sl': sl,
            'tp': tp
        })
    
    # Limit history per user (20 terbaru) & set last_analysis
    for chat_id in user_data:
        user_data[chat_id]['history'] = user_data[chat_id]['history'][:20]
        if user_data[chat_id]['history']:
            user_data[chat_id]['last_analysis'] = user_data[chat_id]['history'][0]


def save_autotrade_state_to_db():
    """Simpan auto trade state ke database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""UPDATE autotrade_save SET 
        active=?, mode=?, balance=?, starting_balance=?,
        total_trades=?, total_wins=?, total_losses=?,
        active_pairs=?, lot_config=?, updated_at=?
        WHERE id=1""", (
        1 if autotrade_state["active"] else 0,
        autotrade_state.get("mode", "paper"),
        autotrade_state["balance"],
        autotrade_state["starting_balance"],
        autotrade_state["total_trades"],
        autotrade_state["total_wins"],
        autotrade_state["total_losses"],
        json.dumps(list(autotrade_state.get("active_pairs", set()))),
        json.dumps(LOT_CONFIG),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def load_autotrade_state_from_db():
    """Load auto trade state dari database"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT active, mode, balance, starting_balance, total_trades, total_wins, total_losses, active_pairs, lot_config FROM autotrade_save WHERE id=1")
    row = c.fetchone()
    conn.close()
    
    if row:
        active, mode, balance, start_bal, total_t, total_w, total_l, pairs_json, lot_json = row
        autotrade_state["active"] = bool(active)
        autotrade_state["mode"] = mode or "paper"
        autotrade_state["balance"] = balance or 1000.0
        autotrade_state["starting_balance"] = start_bal or 1000.0
        autotrade_state["total_trades"] = total_t or 0
        autotrade_state["total_wins"] = total_w or 0
        autotrade_state["total_losses"] = total_l or 0
        
        if pairs_json:
            autotrade_state["active_pairs"] = set(json.loads(pairs_json))
        else:
            autotrade_state["active_pairs"] = set(AUTOTRADE_PAIR_CONFIG.keys())
        
        if lot_json:
            saved_lot = json.loads(lot_json)
            LOT_CONFIG["mode"] = saved_lot.get("mode", LOT_CONFIG["mode"])
            LOT_CONFIG["fixed_lot"] = saved_lot.get("fixed_lot", LOT_CONFIG["fixed_lot"])
            if "auto" in saved_lot:
                LOT_CONFIG["auto"] = saved_lot["auto"]
            if "custom_lot" in saved_lot:
                LOT_CONFIG["custom_lot"] = saved_lot["custom_lot"]
        
        logger.info("✅ Auto trade state loaded from database")    

def save_watchlist_to_db(chat_id, symbol):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO watchlists (chat_id, symbol) VALUES (?, ?)", (chat_id, symbol))
    conn.commit(); conn.close()

def remove_watchlist_from_db(chat_id, symbol):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("DELETE FROM watchlists WHERE chat_id=? AND symbol=?", (chat_id, symbol))
    conn.commit(); conn.close()

def add_subscription(chat_id, username, plan, source="manual"):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    pinfo = SUBSCRIPTION_PLANS.get(plan)
    if not pinfo: conn.close(); return False
    now = datetime.now(); end_time = now + timedelta(hours=pinfo['duration_hours'])
    c.execute("SELECT chat_id FROM subscriptions WHERE chat_id=?", (chat_id,))
    if c.fetchone():
        c.execute("UPDATE subscriptions SET plan=?,start_time=?,end_time=?,is_active=1 WHERE chat_id=?",
                  (plan, now.isoformat(), end_time.isoformat(), chat_id))
    else:
        c.execute("INSERT INTO subscriptions (chat_id,username,plan,start_time,end_time,is_active) VALUES (?,?,?,?,?,1)",
                  (chat_id, username, plan, now.isoformat(), end_time.isoformat()))
    conn.commit(); conn.close(); return True

def check_subscription(chat_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT plan, end_time, is_active FROM subscriptions WHERE chat_id=?", (chat_id,))
    row = c.fetchone(); conn.close()
    if row:
        plan, end_str, active = row; end_time = datetime.fromisoformat(end_str)
        if datetime.now() > end_time: return False, plan, end_time
        if active: return True, plan, end_time
    return False, None, None

def get_all_subscribers():
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT chat_id, username, plan, end_time, source FROM subscriptions WHERE is_active=1")
    rows = c.fetchall(); conn.close(); return rows

def remove_subscription(chat_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("UPDATE subscriptions SET is_active=0 WHERE chat_id=?", (chat_id,))
    conn.commit(); conn.close()

def generate_voucher(plan, created_by):
    code = f"AT-{secrets.token_hex(4).upper()}"
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("INSERT INTO vouchers (code, plan, created_by) VALUES (?,?,?)", (code, plan, created_by))
    conn.commit(); conn.close(); return code

def redeem_voucher(code, chat_id):
    conn = sqlite3.connect(DB_FILE); c = conn.cursor()
    c.execute("SELECT plan, is_used FROM vouchers WHERE code=?", (code.upper(),))
    row = c.fetchone()
    if not row: conn.close(); return None, "Kode tidak ditemukan."
    plan, used = row
    if used: conn.close(); return None, "Kode sudah digunakan."
    c.execute("UPDATE vouchers SET is_used=1, used_by=?, used_at=? WHERE code=?",
              (chat_id, datetime.now().isoformat(), code.upper()))
    conn.commit(); conn.close()
    return plan, f"Berhasil! Paket: {SUBSCRIPTION_PLANS[plan]['name']}"

def require_subscription(func):
    async def wrapper(update: Update, context, *args, **kwargs):
        chat_id = update.effective_chat.id
        if chat_id in ADMIN_IDS: return await func(update, context, *args, **kwargs)
        active, _, _ = check_subscription(chat_id)
        if active: return await func(update, context, *args, **kwargs)
        kb = [[InlineKeyboardButton("💳 Berlangganan", callback_data="subscribe_menu")],
              [InlineKeyboardButton("🆓 Trial 30 menit", callback_data="trial_start")]]
        await update.message.reply_text("🔒 *AKSES TERBATAS*\n\nFitur premium. Trial 30 menit gratis atau /subscribe",
                                        parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    return wrapper

def send_telegram_message(chat_id, message):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e: logger.error(f"Send error: {e}")

# ==================== MICIN & SAHAM US ====================
def is_native_token(name, symbol):
    name_lower = name.lower(); symbol_lower = symbol.lower()
    for native in NATIVE_NAMES:
        if native in name_lower or native == symbol_lower: return True
    return name_lower in ['base', 'solana', 'ethereum', 'bsc', 'bnb', 'polygon']

def check_honeypot(token_address, chain):
    chain_map = {"solana": "solana", "bsc": "bsc", "base": "base", "ethereum": "ethereum", "arbitrum": "arbitrum", "polygon": "polygon"}
    try:
        resp = requests.get(f"https://api.honeypot.is/v1/check?address={token_address}&chain={chain_map.get(chain, chain)}", timeout=15)
        if resp.status_code == 200:
            d = resp.json()
            return {'is_honeypot': d.get('honeypot', True), 'buy_tax': d.get('buyTax', 100), 'sell_tax': d.get('sellTax', 100), 'checked': True}
    except: pass
    return {'is_honeypot': None, 'buy_tax': None, 'sell_tax': None, 'checked': False}

def get_micin_coins(chain_name):
    now = time.time(); ck = f"micin_{chain_name}"
    if ck in micin_cache and (now - micin_cache[ck][1]) < MICIN_CACHE_TTL: return micin_cache[ck][0]
    all_pools = []
    for term in [chain_name[:3], chain_name[:4]]:
        try:
            resp = requests.get(f"https://api.dexscreener.com/latest/dex/search?q={term}", timeout=15)
            if resp.status_code == 200:
                for pair in resp.json().get('pairs', [])[:30]:
                    try:
                        base = pair.get('baseToken', {})
                        pair_age = pair.get('pairCreatedAt', 0)
                        if pair_age:
                            age = (datetime.now() - datetime.fromtimestamp(pair_age/1000)).total_seconds() / 3600
                            if age <= 168:
                                symbol = base.get('symbol', '?')[:12]; name = base.get('name', '?')
                                if not is_native_token(name, symbol):
                                    all_pools.append({'symbol': symbol, 'address': base.get('address', ''), 'age_hours': age, 'name': name, 'chain': pair.get('chainId', chain_name)})
                    except: pass
        except: pass
        time.sleep(0.3)
    seen = set(); unique_pools = []
    for p in all_pools:
        if p['address'] and p['address'] not in seen: seen.add(p['address']); unique_pools.append(p)
    verified = []
    for pool in unique_pools[:15]:
        if not pool['address']: continue
        try:
            resp = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{pool['address']}", timeout=10)
            if resp.status_code == 200 and resp.json().get('pairs'):
                p = resp.json()['pairs'][0]
                liq = float(p.get('liquidity', {}).get('usd', 0) or 0)
                vol_1h = float(p.get('volume', {}).get('h1', 0) or 0)
                if liq < 5000 or vol_1h < 5000: continue
                hp = check_honeypot(pool['address'], chain_name)
                if hp.get('checked') and (hp.get('is_honeypot') or hp.get('buy_tax', 0) > 10 or hp.get('sell_tax', 0) > 10): continue
                verified.append({**pool, 'price': float(p.get('priceUsd',0) or 0), 'liquidity': liq, 'volume_1h': vol_1h})
            time.sleep(0.25)
        except: continue
    verified.sort(key=lambda x: (x['liquidity'], x['volume_1h']), reverse=True)
    micin_cache[ck] = (verified, now); return verified

def get_saham_potensial():
    """
    📌 SAHAM US POTENSIAL V2 — Filter Kualitas + Momentum
    Mencari saham oversold yang mulai reversal, bukan falling knife.
    
    Filter:
    1. RSI < 45 (oversold / mulai jenuh jual)
    2. Harga > EMA50 (trend belum rusak total)
    3. Volume > 500K (likuid)
    4. % Change hari ini > -1% (tidak sedang anjlok)
    5. Harga di 5-40% dari 52-week low (dekat bottom, bukan puncak)
    """
    now = time.time()
    if 'saham' in saham_cache and (now - saham_cache['saham'][1]) < SAHAM_CACHE_TTL:
        return saham_cache['saham'][0]
    
    found = []
    
    for i, sym in enumerate(SAHAM_WATCHLIST):
        try:
            # Rate limiting setiap 8 saham
            if i > 0 and i % 8 == 0:
                time.sleep(0.5)
            
            # 1. Ambil data quote (harga, volume, 52-week)
            resp = requests.get(
                f"https://api.twelvedata.com/quote?symbol={sym}&apikey={get_next_twelve_key()}",
                timeout=8
            )
            if resp.status_code != 200:
                continue
            
            d = resp.json()
            if 'code' in d and d['code'] != 200:
                continue
            
            price = float(d.get('close', 0) or 0)
            vol = int(d.get('volume', 0) or 0)
            
            # Filter dasar
            if price <= 0 or vol < 500000:
                continue
            
            # 2. Filter 52-week position (5-40% dari low)
            h52 = float(d.get('fifty_two_week', {}).get('high', 0) or 0)
            l52 = float(d.get('fifty_two_week', {}).get('low', 0) or 0)
            if h52 == 0 or l52 == 0:
                continue
            
            # Harga minimal 5% di atas 52w low (bukan saham mati)
            if price < l52 * 1.05:
                continue
            
            pos = ((price - l52) / (h52 - l52)) * 100
            
            # Posisi 5-40% dari range (dekat bottom, bukan puncak)
            if pos < 5 or pos > 40:
                continue
            
            # 3. Filter % change hari ini (tidak sedang anjlok >1%)
            pct_change = float(d.get('percent_change', 0) or 0)
            if pct_change < -1:
                continue
            
            # 4. Ambil candle 1H untuk hitung RSI & EMA50
            try:
                candle_resp = requests.get(
                    f"https://api.twelvedata.com/time_series?symbol={sym}&interval=1h&outputsize=100&apikey={get_next_twelve_key()}",
                    timeout=10
                )
                if candle_resp.status_code != 200:
                    continue
                
                candle_data = candle_resp.json()
                if 'values' not in candle_data:
                    continue
                
                candles = candle_data['values']
                if len(candles) < 60:
                    continue
                
                candles.reverse()
                closes = [float(c['close']) for c in candles]
                
                # Hitung RSI 14
                rsi_val = calc_rsi_hybrid(closes)
                
                # Hitung EMA50
                ema50 = calc_ema(closes, 50)
                
                # Filter: RSI < 45 (oversold / mulai reversal)
                if rsi_val >= 45:
                    continue
                
                # Filter: Harga > EMA50 (trend jangka menengah masih ok)
                if ema50 and price < ema50:
                    continue
                
                # 5. Skor kualitas (semakin kecil RSI + semakin rendah posisi = semakin baik)
                quality_score = (45 - rsi_val) + (40 - pos)  # RSI rendah + posisi rendah = skor tinggi
                
                found.append({
                    'symbol': sym,
                    'name': d.get('name', sym),
                    'price': price,
                    'price_position': round(pos, 1),
                    'low_52w': l52,
                    'rsi': round(rsi_val, 1),
                    'volume': vol,
                    'change_pct': round(pct_change, 2),
                    'quality_score': round(quality_score, 1)
                })
                
            except Exception as e:
                logger.debug(f"Saham {sym}: gagal ambil candle - {e}")
                continue
                
        except Exception as e:
            logger.debug(f"Saham {sym}: error - {e}")
            continue
    
    # Sort: RSI terendah + posisi terendah = paling potensial
    found.sort(key=lambda x: x['quality_score'], reverse=True)
    
    result = found[:8]
    saham_cache['saham'] = (result, now)
    return result

# ==================== USER FUNCTIONS ====================
def init_user(chat_id):
    if chat_id not in user_data: user_data[chat_id] = {'history': [], 'watchlist': set(), 'last_analysis': None}

def update_analysis_history(chat_id, symbol, recommendation, entry=None, sl=None, tp=None):
    init_user(chat_id)
    user_data[chat_id]['history'].insert(0, {'symbol': symbol, 'recommendation': recommendation, 'timestamp': datetime.now(), 'entry': entry, 'sl': sl, 'tp': tp})
    user_data[chat_id]['history'] = user_data[chat_id]['history'][:20]
    user_data[chat_id]['last_analysis'] = user_data[chat_id]['history'][0]
    # 🆕 Simpan ke database persistent
    save_analysis_to_db(chat_id, symbol, recommendation, entry, sl, tp)

def get_dashboard_text(chat_id):
    init_user(chat_id)
    d = user_data[chat_id]
    fav = Counter([h['symbol'] for h in d['history']]).most_common(1)[0][0].upper() if d['history'] else "N/A"
    wl = ", ".join([s.upper() for s in d['watchlist']]) if d['watchlist'] else "Kosong"
    last = d['last_analysis']
    last_str = f"{last['symbol'].upper()} {last['recommendation']}" if last else "Belum ada"
    return f"📈 *DASHBOARD {BOT_NAME}*\n⭐ Pair: {fav}\n📊 Analisis: {len(d['history'])}\n📋 Watchlist: {wl}\n🕐 Terakhir: {last_str}"

# ==================== ALERT WORKER ====================
def alert_worker():
    print("🔔 Alert Worker dimulai...")
    while True:
        try:
            now = datetime.now()
            all_alerted = set()
            for cid, ad in user_alerts.items():
                all_alerted.update(ad.get('symbols', set()))
            if not all_alerted:
                time.sleep(CHECK_INTERVAL)
                continue
            for sym in all_alerted:
                try:
                    if sym in FOREX_SYMBOLS:
                        strat_list = UNIVERSAL_STRATEGIES + BEST_STRATEGIES_PER_PAIR.get(sym, []) + MTF_ADDITIONS.get(sym, [])
                    elif sym in STOCK_SYMBOLS:
                        strat_list = STOCK_STRATEGIES
                    elif sym in CRYPTO_SYMBOLS:
                        strat_list = CRYPTO_STRATEGIES
                    else:
                        continue
                    candles = get_candles(sym)
                    if not candles: continue
                    best, _ = detect_signals(sym, candles, strat_list)
                    if not best or best['direction'] not in ['BUY', 'SELL']: continue
                    for cid, ad in user_alerts.items():
                        if sym not in ad.get('symbols', set()): continue
                        sent_dict = ad.get('sent', {})
                        last_sent = sent_dict.get(sym)
                        if last_sent and (now - last_sent) < timedelta(hours=4): continue
                        emoji = "🟢" if best['direction'] == "BUY" else "🔴"
                        msg = (
                            f"🔔 *ALERT SINYAL {sym.upper()}*\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"{emoji} *{best['direction']}* — {best.get('strategy_name', 'Unknown')}\n"
                            f"💰 Entry: {format_price(sym, best['entry'])}\n"
                            f"🛑 SL: {format_price(sym, best['sl'])}\n"
                            f"🎯 TP: {format_price(sym, best['tp'])}\n"
                            f"📊 ADX: {best['adx']:.1f}\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"⏰ {now.strftime('%H:%M WIB, %d %b')}"
                        )
                        send_telegram_message(cid, msg)
                        ad.setdefault('sent', {})[sym] = now
                        logger.info(f"Alert sent to {cid} for {sym}: {best['direction']}")
                except Exception as e:
                    logger.error(f"Alert error for {sym}: {e}")
                    continue
                time.sleep(2)
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            logger.error(f"Alert worker error: {e}")
            time.sleep(60)

# ==================== COMMANDS & CALLBACKS ====================
async def start(update: Update, context):
    cid = update.effective_chat.id
    active, plan, end = check_subscription(cid)
    status_text = ""
    if active:
        h = max(0, (end - datetime.now()).total_seconds()/3600)
        status_text = f"\n🟢 *{plan}* - Sisa {h:.0f} jam"
    kb = [
        [InlineKeyboardButton("💱 Analisa Forex", callback_data="menu_forex")],
        [InlineKeyboardButton("🏢 Analisa Saham", callback_data="menu_stock")],
        [InlineKeyboardButton("₿ Analisa Crypto", callback_data="menu_crypto")],
        [InlineKeyboardButton("🐸 Koin Meme", callback_data="menu_meme")],
        [InlineKeyboardButton("🧂 Koin Micin", callback_data="micin_menu")],
        [InlineKeyboardButton("🏢 Saham US Potensial", callback_data="saham_menu")],
        [InlineKeyboardButton("🤖 Auto Trading Forex", callback_data="menu_autotrade")],
        [InlineKeyboardButton("📈 Dashboard", callback_data="dashboard"), InlineKeyboardButton("🔔 Alert", callback_data="alert_menu")],
        [InlineKeyboardButton("🏦 Broker Terpercaya", callback_data="broker_menu")],
    ]
    kb.append([InlineKeyboardButton("💳 Berlangganan", callback_data="subscribe_menu")])
    await update.message.reply_text(
        f"✨ *{BOT_NAME}*\nAI Trading Analysis & Scalping{status_text}\n\n"
        f"💱 *Forex* Multi-Strategi (12 existing + 4 MTF)\n"
        f"🏢 *Saham* 9 Strategi | ₿ *Crypto* 7 Strategi\n\n"
        f"🔔 *Alert Sinyal* — Notifikasi otomatis saat strategi mendeteksi sinyal\n\n"
        f"Command: /forex /saham /crypto /subscribe",
        parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def subscribe_command(update: Update, context):
    cid = update.effective_chat.id
    active, plan, end = check_subscription(cid)
    if active:
        h = max(0, (end - datetime.now()).total_seconds()/3600)
        await update.message.reply_text(f"👑 *AKTIF*\n{SUBSCRIPTION_PLANS[plan]['emoji']} {plan}\nSisa: {h:.0f} jam", parse_mode='Markdown'); return
    msg = f"💳 *PAKET*\n\n"; kb = []
    for pid, pinfo in SUBSCRIPTION_PLANS.items():
        if pid == "trial": msg += f"{pinfo['emoji']} *TRIAL* - {pinfo['duration_hours']} Jam GRATIS\n\n"
        else:
            days = pinfo['duration_hours']/24; price = f"Rp {pinfo['price']:,}"
            msg += f"{pinfo['emoji']} *{pinfo['name']}* - {days:.0f} Hari\n   💰 {price}\n\n"
            kb.append([InlineKeyboardButton(f"{pinfo['emoji']} Beli {pinfo['name']} - {price}", callback_data=f"buy_{pid}")])
    kb.append([InlineKeyboardButton("🆓 COBA TRIAL 30 menit", callback_data="trial_start")])
    kb.append([InlineKeyboardButton("🎟️ Reedem Voucher", callback_data="redeem_info")])
    await update.message.reply_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def redeem_command(update: Update, context):
    args = context.args
    if not args:
        await update.message.reply_text("🎟️ */redeem [kode]*\nContoh: /redeem AT-ABCD1234", parse_mode='Markdown')
        return
    plan, msg = redeem_voucher(args[0].upper(), update.effective_chat.id)
    if plan:
        add_subscription(update.effective_chat.id, update.effective_user.username or update.effective_user.first_name, plan, "voucher")
        pinfo = SUBSCRIPTION_PLANS[plan]
        end = datetime.now() + timedelta(hours=pinfo['duration_hours'])
        await update.message.reply_text(
            f"🎉 *BERHASIL!*\n{pinfo['emoji']} *{pinfo['name']}*\nBerakhir: {end.strftime('%d %b %H:%M')}",
            parse_mode='Markdown')
    else:
        await update.message.reply_text(f"❌ {msg}", parse_mode='Markdown')

async def genvoucher_command(update: Update, context):
    if update.effective_chat.id not in ADMIN_IDS:
        return
    args = context.args
    if len(args) < 1:
        await update.message.reply_text("🎟️ */genvoucher [plan] [jumlah]*\nContoh: /genvoucher basic 3\n\nPlan: basic, pro, vip", parse_mode='Markdown')
        return
    plan = args[0].lower()
    amount = int(args[1]) if len(args) > 1 else 1
    if plan not in SUBSCRIPTION_PLANS or plan == "trial":
        await update.message.reply_text("❌ Plan tidak valid. Gunakan: basic, pro, vip", parse_mode='Markdown')
        return
    codes = [generate_voucher(plan, update.effective_chat.id) for _ in range(amount)]
    await update.message.reply_text(
        f"🎟️ *VOUCHER ({plan.upper()})*\n" + "\n".join([f"`{c}`" for c in codes]),
        parse_mode='Markdown')

@require_subscription
async def forex_command(update: Update, context):
    args = context.args
    if not args: await update.message.reply_text("💱 */forex [simbol]*\nContoh: /forex xauusd"); return
    sym = args[0].lower()
    if sym not in FOREX_SYMBOLS: await update.message.reply_text("❌ Simbol tidak dikenal."); return
    await perform_standard_analysis(update, context, sym, "forex")

@require_subscription
async def saham_command(update: Update, context):
    args = context.args
    if not args: await update.message.reply_text("🏢 */saham [simbol]*\nContoh: /saham aapl"); return
    sym = args[0].lower()
    if sym not in STOCK_SYMBOLS: await update.message.reply_text("❌ Simbol tidak dikenal."); return
    await perform_standard_analysis(update, context, sym, "stock")

@require_subscription
async def crypto_command(update: Update, context):
    args = context.args
    if not args: await update.message.reply_text("₿ */crypto [simbol]*\nContoh: /crypto btcusd"); return
    sym = args[0].lower()
    if sym not in CRYPTO_SYMBOLS: await update.message.reply_text("❌ Simbol tidak dikenal."); return
    await perform_standard_analysis(update, context, sym, "crypto")

@require_subscription
async def broker_command(update: Update, context):
    """Command /broker - tampilkan daftar broker terpercaya"""
    msg = "🏦 *BROKER TERPERCAYA*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for key, data in BROKER_DATA.items():
        msg += f"{data['logo']} *{data['name']}*\n"
        msg += f"📌 {data['description']}\n\n"
        msg += "*Fitur Unggulan:*\n"
        for f in data['features']:
            msg += f"  {f}\n"
        msg += "\n*Keuntungan Khusus:*\n"
        for b in data['benefits']:
            msg += f"  {b}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += "⚠️ *Disclaimer:* Trading forex/CFD memiliki risiko tinggi. 81.4% akun retail mengalami kerugian. Edukasi diri sebelum trading."
    
    # Tombol di bawah
    kb = [
        [InlineKeyboardButton("🔗 Daftar Exness", url="https://one.exnessonelink.com/a/tpdtmhxhoi")],
        [InlineKeyboardButton("🔄 Cara Pindah Kemitraan", callback_data="broker_pindah")],
        [InlineKeyboardButton("📩 Hubungi Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
    ]
    
    await update.message.reply_text(
        msg,
        parse_mode='Markdown',
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(kb)
    )

def get_strategy_list(symbol, category):
    """Dapatkan list strategi lengkap berdasarkan kategori dan pair"""
    if category == "forex":
        base = UNIVERSAL_STRATEGIES + BEST_STRATEGIES_PER_PAIR.get(symbol, [])
        additions = MTF_ADDITIONS.get(symbol, [])
        return base + additions
    elif category == "stock":
        return STOCK_STRATEGIES
    elif category == "crypto":
        return CRYPTO_STRATEGIES
    return UNIVERSAL_STRATEGIES

async def perform_standard_analysis(update, context, symbol, category):
    cat_names = {"forex": "💱 Analisa Forex", "stock": "🏢 Analisa Saham", "crypto": "₿ Analisa Crypto"}
    msg = update.message
    status = await msg.reply_text(f"⏳ Melakukan {cat_names[category]} untuk {symbol.upper()}...")
    await update.effective_chat.send_chat_action(action="typing")
    loop = asyncio.get_event_loop()
    live_price = await loop.run_in_executor(None, get_live_price, symbol)
    candles = await loop.run_in_executor(None, get_candles, symbol)
    if not candles:
        await status.edit_text(f"❌ Gagal mengambil data untuk {symbol.upper()}."); return
    price = live_price if live_price else float(candles[-1]['close'])
    strat_list = get_strategy_list(symbol, category)
    best, _ = await loop.run_in_executor(None, detect_signals, symbol, candles, strat_list)
    signal_text = format_signal_text(best, symbol)
    news = await loop.run_in_executor(None, get_news, symbol)
    calendar = get_economic_calendar()
    fundamental = f"📰 Berita: {news}"
    if calendar and calendar != "Tidak ada data penting": fundamental += f"\n📅 High-Impact: {calendar}"
    ai_res = await loop.run_in_executor(None, ai_analyze, symbol, price, best, signal_text, fundamental, category)
    final_text = (f"{cat_names[category].upper()}\n\n"
                  f"💵 Harga: {format_price(symbol, price)}\n\n"
                  f"{signal_text}\n\n"
                  f"🧠 *AI Analysis:*\n{ai_res}\n\n"
                  f"📋 *Fundamental:*\n{fundamental}\n\n"
                  f"⚠️ Disclaimer: Edukasi, bukan saran keuangan.")
    if best and best.get('entry'): update_analysis_history(update.effective_chat.id, symbol, best['direction'], best['entry'], best['sl'], best['tp'])
    await status.delete()
    try: await msg.reply_text(final_text, parse_mode='Markdown')
    except: await msg.reply_text(final_text.replace('*', ''))

# ==================== CALLBACKS UNTUK MENU ====================
async def menu_forex_callback(update: Update, context):
    query = update.callback_query; await query.answer()
    cid = update.effective_chat.id
    if not check_subscription(cid)[0] and cid not in ADMIN_IDS: await query.edit_message_text("🔒 Akses terbatas."); return
    kb = [[InlineKeyboardButton(f"{sym.upper()} - {FOREX_SYMBOLS[sym]}", callback_data=f"ana_forex_{sym}")] for sym in FOREX_SYMBOLS]
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text("💱 *ANALISA FOREX*\n\nPilih pair:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def menu_stock_callback(update: Update, context):
    query = update.callback_query; await query.answer()
    cid = update.effective_chat.id
    if not check_subscription(cid)[0] and cid not in ADMIN_IDS: await query.edit_message_text("🔒 Akses terbatas."); return
    kb = [[InlineKeyboardButton(f"{sym.upper()} - {STOCK_SYMBOLS[sym]}", callback_data=f"ana_stock_{sym}")] for sym in STOCK_SYMBOLS]
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text("🏢 *ANALISA SAHAM*\n\nPilih saham:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def menu_crypto_callback(update: Update, context):
    query = update.callback_query; await query.answer()
    cid = update.effective_chat.id
    if not check_subscription(cid)[0] and cid not in ADMIN_IDS: await query.edit_message_text("🔒 Akses terbatas."); return
    kb = [[InlineKeyboardButton(f"{sym.upper()} - {CRYPTO_SYMBOLS[sym]}", callback_data=f"ana_crypto_{sym}")] for sym in CRYPTO_SYMBOLS]
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text("₿ *ANALISA CRYPTO*\n\nPilih crypto:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def menu_meme_callback(update: Update, context):
    query = update.callback_query; await query.answer()
    kb = [[InlineKeyboardButton(f"{sym.upper()} - {MEME_SYMBOLS[sym]}", callback_data=f"ana_meme_{sym}")] for sym in MEME_SYMBOLS]
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text("🐸 *KOIN MEME*\n\nPilih:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def analyze_callback(update: Update, context):
    query = update.callback_query; await query.answer()
    cid = update.effective_chat.id
    if not check_subscription(cid)[0] and cid not in ADMIN_IDS: await query.edit_message_text("🔒 Akses terbatas."); return
    data = query.data
    if data.startswith("ana_forex_"): sym = data.replace("ana_forex_", ""); category = "forex"
    elif data.startswith("ana_stock_"): sym = data.replace("ana_stock_", ""); category = "stock"
    elif data.startswith("ana_crypto_"): sym = data.replace("ana_crypto_", ""); category = "crypto"
    elif data.startswith("ana_meme_"): sym = data.replace("ana_meme_", ""); category = "meme"
    else: await query.edit_message_text("❌ Tidak dikenal."); return
    if category == "meme": await query.edit_message_text(f"🐸 {sym.upper()} — analisa lanjutan tidak tersedia."); return
    await query.edit_message_text(f"⏳ Menganalisa {sym.upper()}...")
    await context.bot.send_chat_action(chat_id=cid, action="typing")
    live_price = await asyncio.get_event_loop().run_in_executor(None, get_live_price, sym)
    candles = await asyncio.get_event_loop().run_in_executor(None, get_candles, sym)
    if not candles: await query.edit_message_text(f"❌ Gagal mengambil data untuk {sym.upper()}."); return
    price = live_price if live_price else float(candles[-1]['close'])
    strat_list = get_strategy_list(sym, category)
    best, _ = await asyncio.get_event_loop().run_in_executor(None, detect_signals, sym, candles, strat_list)
    signal_text = format_signal_text(best, sym)
    news = await asyncio.get_event_loop().run_in_executor(None, get_news, sym)
    calendar = get_economic_calendar()
    fundamental = f"📰 Berita: {news}"
    if calendar and calendar != "Tidak ada data penting": fundamental += f"\n📅 High-Impact: {calendar}"
    ai_res = await asyncio.get_event_loop().run_in_executor(None, ai_analyze, sym, price, best, signal_text, fundamental, category)
    cat_names = {"forex": "💱 Analisa Forex", "stock": "🏢 Analisa Saham", "crypto": "₿ Analisa Crypto"}
    final_text = (f"{cat_names[category].upper()}\n\n"
                  f"💵 Harga: {format_price(sym, price)}\n\n"
                  f"{signal_text}\n\n"
                  f"🧠 *AI Analysis:*\n{ai_res}\n\n"
                  f"📋 *Fundamental:*\n{fundamental}\n\n"
                  f"⚠️ Disclaimer: Edukasi, bukan saran keuangan.")
    if best and best.get('entry'): update_analysis_history(cid, sym, best['direction'], best['entry'], best['sl'], best['tp'])
    try: await query.edit_message_text(final_text, parse_mode='Markdown')
    except: await query.edit_message_text(final_text.replace('*', ''))

# ==================== CALLBACKS LAINNYA ====================
async def subscribe_menu_callback(update: Update, context):
    query = update.callback_query; await query.answer()
    await subscribe_command(update, context)

async def broker_menu_callback(update: Update, context):
    """Callback untuk tombol Broker Terpercaya"""
    query = update.callback_query
    await query.answer()
    
    # Bangun pesan broker
    msg = "🏦 *BROKER TERPERCAYA*\n━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for key, data in BROKER_DATA.items():
        msg += f"{data['logo']} *{data['name']}*\n"
        msg += f"📌 {data['description']}\n\n"
        msg += "*Fitur Unggulan:*\n"
        for f in data['features']:
            msg += f"  {f}\n"
        msg += "\n*Keuntungan Khusus:*\n"
        for b in data['benefits']:
            msg += f"  {b}\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    msg += "⚠️ *Disclaimer:* Trading forex/CFD memiliki risiko tinggi. 81.4% akun retail mengalami kerugian. Edukasi diri sebelum trading."
    
    # Tombol di bawah
    kb = [
        [InlineKeyboardButton("🔗 Daftar Exness", url="https://one.exnessonelink.com/a/tpdtmhxhoi")],
        [InlineKeyboardButton("🔄 Cara Pindah Kemitraan", callback_data="broker_pindah")],
        [InlineKeyboardButton("📩 Hubungi Admin", url=f"https://t.me/{ADMIN_USERNAME.replace('@', '')}")],
    ]
    
    await query.edit_message_text(
        msg,
        parse_mode='Markdown',
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def broker_pindah_callback(update: Update, context):
    """Callback untuk tombol Cara Pindah Kemitraan"""
    query = update.callback_query
    await query.answer()
    
    # Ambil panduan dari BROKER_DATA
    panduan = BROKER_DATA.get("exness", {}).get("pindah_kemitraan", "Panduan tidak tersedia.")
    
    kb = [[InlineKeyboardButton("🔙 Kembali ke Broker", callback_data="broker_menu")]]
    
    await query.edit_message_text(
        panduan,
        parse_mode='Markdown',
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def trial_start_callback(update: Update, context):
    query = update.callback_query
    try:
        await query.answer(); cid = update.effective_chat.id
        if check_subscription(cid)[0]: await query.edit_message_text("✅ Anda sudah aktif."); return
        conn = sqlite3.connect(DB_FILE); c = conn.cursor()
        c.execute("SELECT chat_id FROM subscriptions WHERE chat_id=? AND plan='trial'", (cid,))
        if c.fetchone(): conn.close(); await query.edit_message_text("⚠️ Anda sudah pernah trial."); return
        conn.close()
        add_subscription(cid, update.effective_user.username or update.effective_user.first_name, "trial", "trial")
        end = datetime.now() + timedelta(minutes=TRIAL_MINUTES)
        await query.edit_message_text(f"🎉 *TRIAL DIAKTIFKAN!*\n⏰ Berakhir: {end.strftime('%H:%M, %d %b')}", parse_mode='Markdown')
    except Exception as e: logger.error(f"Trial error: {e}")

async def buy_callback(update: Update, context):
    query = update.callback_query
    try:
        await query.answer(); plan_id = query.data.replace("buy_", ""); pinfo = SUBSCRIPTION_PLANS.get(plan_id)
        if not pinfo: return
        await query.edit_message_text(f"💳 *PEMBELIAN*\n{pinfo['name']} - Rp {pinfo['price']:,}\n\nTransfer ke:\n{PAYMENT_METHODS}\n\nKirim bukti ke Admin.", parse_mode='Markdown')
    except: pass

async def redeem_info_callback(update: Update, context):
    query = update.callback_query
    try: await query.answer(); await query.edit_message_text("🎟️ `/redeem [kode]`\nContoh: `/redeem AT-ABCD1234`", parse_mode='Markdown')
    except: pass

async def micin_menu_callback(update: Update, context):
    query = update.callback_query
    try:
        await query.answer(); cid = update.effective_chat.id
        if not check_subscription(cid)[0] and cid not in ADMIN_IDS: await query.edit_message_text("🔒 Akses terbatas."); return
        kb = [[InlineKeyboardButton(f"{v['emoji']} {v['name']}", callback_data=f"micin_{k}")] for k, v in MICIN_CHAINS.items()]
        kb.append([InlineKeyboardButton("🌐 Semua Chain", callback_data="micin_all")])
        kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
        await query.edit_message_text("🧂 *KOIN MICIN HUNTER*\nFilter: Liq > $5K | Vol 1h > $5K\nPilih chain:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    except: pass

async def micin_analyze_callback(update: Update, context):
    query = update.callback_query
    try:
        await query.answer(); cid = update.effective_chat.id
        if not check_subscription(cid)[0] and cid not in ADMIN_IDS: return
        target = query.data.replace("micin_", "")
        if target == "all":
            all_coins = []
            for chain in MICIN_CHAINS:
                coins = await asyncio.get_event_loop().run_in_executor(None, get_micin_coins, chain)
                all_coins.extend(coins)
            all_coins.sort(key=lambda x: (x['liquidity'], x['volume_1h']), reverse=True)
            coins = all_coins[:10]; chain_label = "🌐 Semua Chain"
        else:
            coins = await asyncio.get_event_loop().run_in_executor(None, get_micin_coins, target)
            chain_label = MICIN_CHAINS.get(target, {"name": target, "emoji": ""}).get('emoji', '') + " " + target
        await query.edit_message_text(f"🧂 Mencari koin di {chain_label}...")
        await context.bot.send_chat_action(chat_id=cid, action="typing")
        if not coins: await query.edit_message_text(f"❌ Tidak ada koin aman."); return
        txt = f"🧂 *{chain_label}*\n📊 {len(coins)} koin aman\n\n"
        for c in coins[:5]:
            age_str = f"{c['age_hours']:.1f}h" if c['age_hours'] < 24 else f"{c['age_hours']/24:.1f}d"
            txt += f"🟢 *{c['symbol']}* | Age: {age_str}\n  Liq: ${c['liquidity']:,.0f} | Vol 1h: ${c['volume_1h']:,.0f}\n\n"
        txt += "⚠️ Risiko tinggi! Data: DEXScreener + Honeypot.is"
        await query.edit_message_text(txt, parse_mode='Markdown')
    except: pass

async def saham_menu_callback(update: Update, context):
    query = update.callback_query
    try:
        await query.answer(); cid = update.effective_chat.id
        if not check_subscription(cid)[0] and cid not in ADMIN_IDS: return
        await query.edit_message_text("🏢 Mencari saham US oversold berkualitas...")
        await context.bot.send_chat_action(chat_id=cid, action="typing")
        stocks = await asyncio.get_event_loop().run_in_executor(None, get_saham_potensial)
        if not stocks:
            await query.edit_message_text("❌ Tidak ada saham yang memenuhi kriteria.\n\nFilter: RSI<45 | Harga>EMA50 | Vol>500K | Dekat 52w low")
            return
        
        txt = (
            f"🏢 *SAHAM US POTENSIAL — OVERSOLD QUALITY*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 {len(stocks)} saham memenuhi kriteria\n"
            f"Filter: RSI<45 | Harga>EMA50 | Vol>500K\n\n"
        )
        
        for s in stocks[:8]:
            # RSI indicator
            rsi_emoji = "🔥" if s['rsi'] < 30 else "🟠" if s['rsi'] < 40 else "🟡"
            
            # Entry, SL, TP
            entry = s['price']
            sl_val = round(s['low_52w'] * 0.95, 2)
            tp_val = round(entry * 1.15, 2)  # 15% take profit
            
            txt += (
                f"*{s['symbol']}* — ${s['price']:.2f}\n"
                f"  {rsi_emoji} RSI: {s['rsi']} | 📉 Pos: {s['price_position']}% dari 52w low\n"
                f"  📊 Vol: {s['volume']:,} | Δ: {s['change_pct']:+.1f}%\n"
                f"  🎯 Entry: ${entry:.2f} | SL: ${sl_val:.2f} | TP: ${tp_val:.2f}\n"
                f"  ⭐ Skor: {s['quality_score']}\n\n"
            )
        
        txt += (
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 RSI < 30 (jenuh jual) | 🟠 RSI 30-40 (oversold)\n"
            f"🟡 RSI 40-45 (mulai reversal)\n\n"
            f"⚠️ Bukan saran keuangan. Selalu DYOR!"
        )
        
        await query.edit_message_text(txt, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Saham menu error: {e}")
        await query.edit_message_text("❌ Gagal memuat data saham.")

async def dashboard_callback(update: Update, context):
    query = update.callback_query; await query.answer()
    await query.edit_message_text(get_dashboard_text(update.effective_chat.id), parse_mode='Markdown')

async def alert_menu(update: Update, context):
    query = update.callback_query; await query.answer()
    cid = update.effective_chat.id
    active = user_alerts.get(cid, {}).get('symbols', set())
    status = f"Aktif: {', '.join([s.upper() for s in active])}" if active else "Belum ada"
    kb, row = [], []
    for sym in ALL_SYMBOLS:
        mark = "✅" if sym in active else "⬜"
        row.append(InlineKeyboardButton(f"{mark} {sym.upper()}", callback_data=f"alt_{sym}"))
        if len(row) == 2: kb.append(row); row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text(
        f"🔔 *ALERT SINYAL*\n\nStatus: {status}\n\n"
        f"Notifikasi otomatis saat strategi mendeteksi sinyal BUY/SELL.\n"
        f"Minimal interval: 4 jam antar notifikasi.\n\nToggle symbol:",
        parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def alert_toggle(update: Update, context):
    query = update.callback_query; await query.answer()
    sym = query.data.replace("alt_", ""); cid = update.effective_chat.id
    if cid not in user_alerts: user_alerts[cid] = {'symbols': set(), 'sent': {}}
    if sym in user_alerts[cid]['symbols']:
        user_alerts[cid]['symbols'].discard(sym); remove_alert_from_db(cid, sym)
    else:
        user_alerts[cid]['symbols'].add(sym); save_alert_to_db(cid, sym)
    active = user_alerts[cid]['symbols']
    status = f"Aktif: {', '.join([s.upper() for s in active])}" if active else "Belum ada"
    kb, row = [], []
    for s in ALL_SYMBOLS:
        mark = "✅" if s in active else "⬜"
        row.append(InlineKeyboardButton(f"{mark} {s.upper()}", callback_data=f"alt_{s}"))
        if len(row) == 2: kb.append(row); row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton("🔙 Menu", callback_data="menu")])
    await query.edit_message_text(f"🔔 *ALERT SINYAL*\n{status}\nToggle:", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def menu(update: Update, context):
    query = update.callback_query; await query.answer()
    kb = [
        [InlineKeyboardButton("💱 Analisa Forex", callback_data="menu_forex")],
        [InlineKeyboardButton("🏢 Analisa Saham", callback_data="menu_stock")],
        [InlineKeyboardButton("₿ Analisa Crypto", callback_data="menu_crypto")],
        [InlineKeyboardButton("🐸 Koin Meme", callback_data="menu_meme")],
        [InlineKeyboardButton("🧂 Koin Micin", callback_data="micin_menu")],
        [InlineKeyboardButton("🏢 Saham US", callback_data="saham_menu")],
        [InlineKeyboardButton("🤖 Auto Trading Forex", callback_data="menu_autotrade")],
        [InlineKeyboardButton("📈 Dashboard", callback_data="dashboard"), InlineKeyboardButton("🔔 Alert", callback_data="alert_menu")],
        [InlineKeyboardButton("💳 Subscribe", callback_data="subscribe_menu")],
    ]
    await query.edit_message_text(f"✨ *{BOT_NAME}* - Menu\n\n🆕 MTF Strategies Active", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def fallback(update: Update, context):
    cid = update.effective_chat.id
    if check_subscription(cid)[0]:
        await update.message.reply_text(f"✨ *{BOT_NAME}*\n\nCommand:\n/forex /saham /crypto /subscribe\n/start untuk menu.", parse_mode='Markdown')
    else: await update.message.reply_text(f"✨ *{BOT_NAME}*\n\n🔒 Trial 30 menit GRATIS\n/start", parse_mode='Markdown')
    
# ==================== GANTI MULAI DARI SINI SAMPAI AKHIR FILE ====================

# ==================== AUTO TRADE WORKER ====================
def autotrade_worker():
    """Background worker untuk auto trading"""
    print("🤖 Auto Trade Worker dimulai...")
    
    # Notifikasi ke admin bahwa Auto Trade Worker siap
    for admin_id in ADMIN_IDS:
        try:
            send_telegram_message(admin_id, "🤖 *Auto Trade Worker* siap!\n\n📌 S01_EMA_Tight: XAU, BTC, NZD\n📌 S02_AllInOne_Agg: EUR, JPY, AUD, CAD\n📌 S04_KC_Scalp: CHF, GBP\n\n⏰ Memindai setiap 120 detik.\nGunakan /autotrade on untuk memulai.")
        except:
            pass
    
    while True:
        try:
            if not autotrade_state["active"]:
                time.sleep(60)
                continue
            
            now = datetime.now()
            logger.info(f"Auto Trade cycle: {now.strftime('%H:%M:%S')}")
            
            if "positions" not in autotrade_state:
                autotrade_state["positions"] = {}
            
            # Inisialisasi active_pairs jika belum ada (default: semua pair)
            if not autotrade_state.get("active_pairs"):
                autotrade_state["active_pairs"] = set(AUTOTRADE_PAIR_CONFIG.keys())
            
            active_pairs = autotrade_state["active_pairs"]
            
            notifications = []
            
            # 🔧 PERBAIKAN: Loop semua pair dari AUTOTRADE_PAIR_CONFIG (termasuk BTC, XAU, dll)
            all_autotrade_pairs = list(AUTOTRADE_PAIR_CONFIG.keys())
            
            for pair_symbol in all_autotrade_pairs:
                try:
                    # SKIP jika pair TIDAK dipilih oleh user
                    if pair_symbol not in active_pairs:
                        continue
                    
                    # Skip pair saat weekend (Sabtu-Minggu), kecuali crypto & XAU
                    is_weekend = now.weekday() >= 5
                    is_crypto_or_gold = "BTC" in pair_symbol.upper() or "XAU" in pair_symbol.upper()
                    if is_weekend and not is_crypto_or_gold:
                        continue
                    
                    # 🔧 PERBAIKAN: Ambil harga langsung pakai pair_symbol
                    price = get_autotrade_price(pair_symbol)
                    if not price:
                        continue
                    
                    if pair_symbol not in autotrade_state["positions"]:
                        autotrade_state["positions"][pair_symbol] = []
                    
                    positions = autotrade_state["positions"][pair_symbol]
                    closed = check_sl_tp(price, positions)
                    
                    for idx, reason in closed:
                        pos = positions[idx]
                        if reason == "TP":
                            profit = abs(pos["entry"] - pos["tp"]) * pos["lot"] * (100 if "XAU" in pair_symbol else 10000)
                            autotrade_state["balance"] += profit
                            autotrade_state["total_wins"] += 1
                            notifications.append(f"✅ *{pair_symbol} WIN* — {pos['strategy']}\nEntry: ${pos['entry']:.2f} → TP: ${pos['tp']:.2f}\nProfit: +${profit:.2f} | Lot: {pos['lot']}")
                        else:
                            loss = abs(pos["entry"] - pos["sl"]) * pos["lot"] * (100 if "XAU" in pair_symbol else 10000)
                            autotrade_state["balance"] -= loss
                            autotrade_state["total_losses"] += 1
                            notifications.append(f"❌ *{pair_symbol} LOSS* — {pos['strategy']}\nEntry: ${pos['entry']:.2f} → SL: ${pos['sl']:.2f}\nLoss: -${loss:.2f} | Lot: {pos['lot']}")
                        autotrade_state["total_trades"] += 1
                    
                    config = AUTOTRADE_PAIR_CONFIG.get(pair_symbol, {})
                    max_pos = config.get("max_positions", 3)
                    open_count = sum(1 for p in positions if p["status"] == "OPEN")
                    
                    if open_count >= max_pos:
                        continue
                    
                    # 🔧 PERBAIKAN: Kirim pair_symbol langsung
                    signals_1h = run_autotrade_strategy_1h(pair_symbol, pair_symbol)
                    signals_mtf = run_autotrade_strategy_mtf(pair_symbol, pair_symbol)
                    all_signals = signals_1h + signals_mtf
                    
                    for sig in all_signals:
                        if open_count >= max_pos:
                            break
                        
                        lot = lot_calculator.calculate(pair_symbol, sig["entry"], sig["sl"])
                        
                        if autotrade_state.get("mode") == "real":
                            symbol = pair_symbol.replace("/", "")
                            if sig["direction"] == "BUY":
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
                                "sl": sig["sl"],
                                "tp": sig["tp"],
                                "deviation": 20,
                                "magic": 123456,
                                "comment": "AT_" + sig["strategy"],
                                "type_time": mt5.ORDER_TIME_GTC,
                                "type_filling": mt5.ORDER_FILLING_IOC,
                            }
                            result = mt5.order_send(request)
                            if result.retcode == mt5.TRADE_RETCODE_DONE:
                                logger.info("MT5 Order OK: " + sig["direction"] + " " + pair_symbol)
                            else:
                                logger.error("MT5 Error: " + str(result.comment))
                        
                        new_pos = {
                            "pair": pair_symbol,
                            "direction": sig["direction"],
                            "entry": sig["entry"],
                            "sl": sig["sl"],
                            "tp": sig["tp"],
                            "strategy": sig["strategy"],
                            "lot": lot,
                            "status": "OPEN",
                            "time": now.isoformat(),
                            "exit_price": None,
                            "result": None
                        }
                        positions.append(new_pos)
                        open_count += 1
                        
                        notifications.append(f"{'🟢' if sig['direction']=='BUY' else '🔴'} *{pair_symbol} {sig['direction']}* — {sig['strategy']}\nEntry: ${sig['entry']:.2f} | SL: ${sig['sl']:.2f} | TP: ${sig['tp']:.2f}\nLot: {lot} | ADX: {sig['adx']:.1f}")
                        
                except Exception as e:
                    logger.error(f"Auto trade error for {pair_symbol}: {e}")
                    continue
                
                time.sleep(1)
            
            # Kirim notifikasi ke admin
            if notifications:
                for admin_id in ADMIN_IDS:
                    msg = "🤖 *AUTO TRADING REPORT*\n" + f"⏰ {now.strftime('%H:%M WIB, %d %b')}\n" + "━"*30 + "\n"
                    for notif in notifications[:10]:
                        msg += f"\n{notif}\n"
                    if len(notifications) > 10:
                        msg += f"\n... dan {len(notifications)-10} notifikasi lainnya."
                    msg += f"\n━"*30 + f"\n💰 Balance: ${autotrade_state['balance']:,.2f}"
                    send_telegram_message(admin_id, msg)
            
            # 🆕 AUTO-SAVE: Simpan state SETIAP SIKLUS agar tidak kehilangan data jika bot restart
            save_autotrade_state_to_db()
            logger.info("💾 Auto trade state saved to database")
            
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Auto trade worker error: {e}")
            # 🆕 Tetap simpan state meskipun error
            try:
                save_autotrade_state_to_db()
            except:
                pass
            time.sleep(60)


# ==================== AUTO TRADE COMMANDS ====================
@require_subscription
async def autotrade_command(update: Update, context):
    """Command /autotrade untuk kontrol auto trading"""
    args = context.args
    
    if not args:
        status = "🟢 AKTIF" if autotrade_state["active"] else "🔴 NON-AKTIF"
        mode = autotrade_state.get("mode", "paper")
        balance = autotrade_state["balance"]
        start_balance = autotrade_state["starting_balance"]
        profit = balance - start_balance
        profit_pct = (profit / start_balance * 100) if start_balance > 0 else 0
        total_trades = autotrade_state["total_trades"]
        wins = autotrade_state["total_wins"]
        losses = autotrade_state["total_losses"]
        wr = (wins / total_trades * 100) if total_trades > 0 else 0
        
        msg = (
            f"🤖 *AUTO TRADING STATUS*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Status: {status}\n"
            f"Mode: {mode.upper()}\n"
            f"💰 Balance: ${balance:,.2f}\n"
            f"📈 P/L: {profit:+,.2f} ({profit_pct:+.1f}%)\n"
            f"📊 Total Trades: {total_trades}\n"
            f"✅ Win: {wins} | ❌ Loss: {losses}\n"
            f"📊 Win Rate: {wr:.1f}%\n\n"
        )
        
        open_positions = []
        if "positions" in autotrade_state:
            for pair_symbol, positions in autotrade_state["positions"].items():
                for pos in positions:
                    if pos["status"] == "OPEN":
                        open_positions.append(f"  {'🟢' if pos['direction']=='BUY' else '🔴'} {pair_symbol} {pos['direction']} @ ${pos['entry']:.2f} ({pos['strategy']})")
        
        if open_positions:
            msg += "*POSISI TERBUKA:*\n" + "\n".join(open_positions[:10])
            if len(open_positions) > 10:
                msg += f"\n... dan {len(open_positions)-10} lainnya."
        else:
            msg += "*POSISI TERBUKA:* Tidak ada."
        
        msg += f"\n\nCommand:\n/autotrade on — Aktifkan\n/autotrade off — Matikan\n/autotrade mode paper/real — Mode\n/autotrade report — Laporan\n/autotrade balance [jumlah] — Set Balance"
        
        await update.message.reply_text(msg, parse_mode='Markdown')
        return
    
    subcommand = args[0].lower()
    
    if subcommand == "on":
        if autotrade_state["active"]:
            await update.message.reply_text("🤖 Auto Trading sudah *AKTIF*.", parse_mode='Markdown')
        else:
            autotrade_state["active"] = True
            save_autotrade_state_to_db()
            mode = autotrade_state.get("mode", "paper")
            await update.message.reply_text(
                f"🤖 *AUTO TRADING DIAKTIFKAN*\n\n"
                f"Mode: {mode.upper()}\n"
                f"💰 Balance: ${autotrade_state['balance']:,.2f}\n"
                f"📊 Pair: {len(AUTOTRADE_PAIR_CONFIG)} pasang\n"
                f"⏰ Siklus: Setiap {CHECK_INTERVAL} menit\n\n"
                f"⚠️ *{'REAL TRADING' if mode == 'real' else 'Paper Trading'}*",
                parse_mode='Markdown'
            )
    
    elif subcommand == "off":
        if not autotrade_state["active"]:
            await update.message.reply_text("🤖 Auto Trading sudah *NON-AKTIF*.", parse_mode='Markdown')
        else:
            autotrade_state["active"] = False
            save_autotrade_state_to_db()
            await update.message.reply_text(
                f"🤖 *AUTO TRADING DIMATIKAN*\n\n"
                f"💰 Balance Akhir: ${autotrade_state['balance']:,.2f}\n"
                f"📊 Total Trades: {autotrade_state['total_trades']}",
                parse_mode='Markdown'
            )
    
    elif subcommand == "balance":
        if len(args) < 2:
            await update.message.reply_text("💰 */autotrade balance [jumlah]*\nContoh: /autotrade balance 5000")
            return
        try:
            new_balance = float(args[1])
            autotrade_state["balance"] = new_balance
            autotrade_state["starting_balance"] = new_balance
            autotrade_state["total_trades"] = 0
            autotrade_state["total_wins"] = 0
            autotrade_state["total_losses"] = 0
            save_autotrade_state_to_db()
            await update.message.reply_text(f"💰 *BALANCE DIUPDATE*\n\nBalance Baru: ${new_balance:,.2f}\nStatistik trading di-reset.", parse_mode='Markdown')
        except:
            await update.message.reply_text("❌ Format tidak valid. Contoh: /autotrade balance 5000")
    
    elif subcommand == "report":
        await generate_autotrade_report(update)

    elif subcommand == "mode":
        if len(args) < 2:
            await update.message.reply_text("⚙️ */autotrade mode [paper/real]*\n\nPaper = Simulasi\nReal = Trading di MT5", parse_mode='Markdown')
            return
        mode = args[1].lower()
        if mode in ["paper", "real"]:
            autotrade_state["mode"] = mode
            save_autotrade_state_to_db()
            await update.message.reply_text(f"✅ Mode diubah ke: *{mode.upper()}*", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Mode tidak valid. Gunakan: paper atau real", parse_mode='Markdown')

    else:
        await update.message.reply_text("❌ Subcommand tidak dikenal. Gunakan: on, off, status, balance, report, mode")


async def generate_autotrade_report(update):
    """Generate laporan performa auto trading"""
    balance = autotrade_state["balance"]
    start_balance = autotrade_state["starting_balance"]
    profit = balance - start_balance
    profit_pct = (profit / start_balance * 100) if start_balance > 0 else 0
    total_trades = autotrade_state["total_trades"]
    wins = autotrade_state["total_wins"]
    losses = autotrade_state["total_losses"]
    wr = (wins / total_trades * 100) if total_trades > 0 else 0
    
    msg = (
        f"🤖 *AETHER TRADE AI — AUTO TRADING REPORT*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 {datetime.now().strftime('%d %B %Y %H:%M WIB')}\n\n"
        f"💰 *BALANCE*\n"
        f"  Starting: ${start_balance:,.2f}\n"
        f"  Current: ${balance:,.2f}\n"
        f"  P/L: {profit:+,.2f} ({profit_pct:+.1f}%)\n\n"
        f"📊 *PERFORMANCE*\n"
        f"  Total Trades: {total_trades}\n"
        f"  ✅ Win: {wins} | ❌ Loss: {losses}\n"
        f"  Win Rate: {wr:.1f}%\n\n"
    )
    
    strategy_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "profit": 0.0})
    pair_stats = defaultdict(lambda: {"wins": 0, "losses": 0, "profit": 0.0})
    
    if "positions" in autotrade_state:
        for pair_symbol, positions in autotrade_state["positions"].items():
            for pos in positions:
                if pos["status"] in ["CLOSED_TP", "CLOSED_SL"]:
                    strat = pos.get("strategy", "Unknown")
                    pnl = abs(pos["entry"] - pos.get("exit_price", pos["entry"])) * pos["lot"] * (100 if "XAU" in pair_symbol else 10000)
                    if pos["result"] == "WIN":
                        strategy_stats[strat]["wins"] += 1
                        strategy_stats[strat]["profit"] += pnl
                        pair_stats[pair_symbol]["wins"] += 1
                        pair_stats[pair_symbol]["profit"] += pnl
                    else:
                        strategy_stats[strat]["losses"] += 1
                        strategy_stats[strat]["profit"] -= pnl
                        pair_stats[pair_symbol]["losses"] += 1
                        pair_stats[pair_symbol]["profit"] -= pnl
    
    if pair_stats:
        sorted_pairs = sorted(pair_stats.items(), key=lambda x: x[1]["profit"], reverse=True)
        msg += "🏆 *TOP PAIR:*\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (pair, stats) in enumerate(sorted_pairs[:3]):
            total = stats["wins"] + stats["losses"]
            wr_pair = (stats["wins"] / total * 100) if total > 0 else 0
            msg += f"  {medals[i]} {pair}: {stats['profit']:+,.0f} (WR {wr_pair:.0f}%)\n"
    
    if strategy_stats:
        sorted_strats = sorted(strategy_stats.items(), key=lambda x: x[1]["profit"], reverse=True)
        msg += "\n🏆 *TOP STRATEGI:*\n"
        for i, (strat, stats) in enumerate(sorted_strats[:3]):
            total = stats["wins"] + stats["losses"]
            wr_strat = (stats["wins"] / total * 100) if total > 0 else 0
            msg += f"  {medals[i]} {strat}: {stats['profit']:+,.0f} (WR {wr_strat:.0f}%)\n"
    
    msg += (
        f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ *Disclaimer:* Hasil simulasi Paper Trading.\n"
        f"Bukan jaminan profit untuk trading real.\n"
        f"Gunakan link broker terpercaya: /broker"
    )
    
    await update.message.reply_text(msg, parse_mode='Markdown')


# ==================== 🆕 PAIR SELECTOR CALLBACKS ====================
async def autotrade_pair_selector(update: Update, context):
    """Tampilkan halaman pemilihan pair"""
    query = update.callback_query
    await query.answer()
    
    # Inisialisasi active_pairs jika kosong (default: semua pair)
    if not autotrade_state["active_pairs"]:
        autotrade_state["active_pairs"] = set(AUTOTRADE_PAIR_CONFIG.keys())
    
    active_pairs = autotrade_state["active_pairs"]
    total_pairs = len(AUTOTRADE_PAIR_CONFIG)
    selected_count = len(active_pairs)
    all_selected = selected_count == total_pairs
    
    msg = (
        f"⚙️ *PILIH PAIR AUTO TRADING*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 Terpilih: {selected_count}/{total_pairs} pair\n\n"
        f"*Toggle pair di bawah:*\n"
        f"✅ = Aktif | ❌ = Non-Aktif\n"
    )
    
    # Buat tombol per pair (2 kolom)
    kb = []
    row = []
    for pair_symbol, config in AUTOTRADE_PAIR_CONFIG.items():
        name = pair_symbol.split("/")[0]
        is_active = pair_symbol in active_pairs
        emoji = "✅" if is_active else "❌"
        strategies = ", ".join(config.get("strategies", [])[:2])
        row.append(InlineKeyboardButton(
            f"{emoji} {name}", 
            callback_data=f"at_pair_toggle_{pair_symbol}"
        ))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    
    # 🆕 Toggle "Aktifkan Semua" / "Nonaktifkan Semua"
    if all_selected:
        kb.append([InlineKeyboardButton("❌ NONAKTIFKAN SEMUA", callback_data="at_pair_all_off")])
    else:
        kb.append([InlineKeyboardButton("✅ AKTIFKAN SEMUA", callback_data="at_pair_all_on")])
    
    kb.append([
        InlineKeyboardButton("💾 Simpan & Kembali", callback_data="at_pair_save"),
        InlineKeyboardButton("🔙 Batal", callback_data="at_back")
    ])
    
    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))


async def autotrade_pair_toggle(update: Update, context):
    """Toggle satu pair on/off"""
    query = update.callback_query
    await query.answer()
    
    pair_symbol = query.data.replace("at_pair_toggle_", "")
    
    if pair_symbol in autotrade_state["active_pairs"]:
        autotrade_state["active_pairs"].discard(pair_symbol)
    else:
        autotrade_state["active_pairs"].add(pair_symbol)
    
    # Refresh halaman
    update.callback_query.data = "at_pair_selector"
    await autotrade_pair_selector(update, context)


async def autotrade_pair_all_on(update: Update, context):
    """Aktifkan semua pair"""
    query = update.callback_query
    await query.answer("✅ Semua pair diaktifkan!")
    autotrade_state["active_pairs"] = set(AUTOTRADE_PAIR_CONFIG.keys())
    
    update.callback_query.data = "at_pair_selector"
    await autotrade_pair_selector(update, context)


async def autotrade_pair_all_off(update: Update, context):
    """Nonaktifkan semua pair"""
    query = update.callback_query
    await query.answer("❌ Semua pair dinonaktifkan!")
    autotrade_state["active_pairs"] = set()
    
    update.callback_query.data = "at_pair_selector"
    await autotrade_pair_selector(update, context)


async def autotrade_pair_save(update: Update, context):
    """Simpan pemilihan pair dan kembali ke menu auto trade"""
    query = update.callback_query
    
    count = len(autotrade_state["active_pairs"])
    
    if count == 0:
        await query.answer("⚠️ Pilih minimal 1 pair!", show_alert=True)
        return
    
    await query.answer(f"✅ {count} pair disimpan!")
    
    # 🆕 Simpan ke database
    save_autotrade_state_to_db()
    
    # Kembali ke menu auto trade
    update.callback_query.data = "at_back"
    await autotrade_menu_callback(update, context)


async def autotrade_menu_callback(update: Update, context):
    """Callback untuk tombol Auto Trading Forex di menu"""
    query = update.callback_query
    await query.answer()
    
    status = "🟢 AKTIF" if autotrade_state["active"] else "🔴 NON-AKTIF"
    mode = autotrade_state.get("mode", "paper")
    balance = autotrade_state["balance"]
    start_balance = autotrade_state["starting_balance"]
    profit = balance - start_balance
    profit_pct = (profit / start_balance * 100) if start_balance > 0 else 0
    
    # 🆕 Info pair yang dipilih
    active_pairs = autotrade_state.get("active_pairs", set())
    if not active_pairs:
        active_pairs = set(AUTOTRADE_PAIR_CONFIG.keys())
        autotrade_state["active_pairs"] = active_pairs
    pair_count = len(active_pairs)
    total_pairs = len(AUTOTRADE_PAIR_CONFIG)
    
    msg = (
        f"🤖 *AUTO TRADING FOREX*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Status: {status} | Mode: {mode.upper()}\n"
        f"💰 Balance: ${balance:,.2f}\n"
        f"📈 P/L: {profit:+,.2f} ({profit_pct:+.1f}%)\n"
        f"📊 Pair: {pair_count}/{total_pairs} dipilih\n\n"
        f"⚙️ *Kontrol Cepat:*"
    )
    
    if autotrade_state["active"]:
        kb = [
            [InlineKeyboardButton("📊 Status", callback_data="at_status"),
             InlineKeyboardButton("📋 Report", callback_data="at_report")],
            [InlineKeyboardButton("⏹️ Matikan", callback_data="at_off"),
             InlineKeyboardButton("🔄 Ganti Mode", callback_data="at_mode")],
            [InlineKeyboardButton("⚙️ Pilih Pair", callback_data="at_pair_selector"),
             InlineKeyboardButton("📐 Lot", callback_data="lot_menu")],
            [InlineKeyboardButton("🔙 Menu", callback_data="menu")],
        ]
    else:
        kb = [
            [InlineKeyboardButton("▶️ Aktifkan", callback_data="at_on"),
             InlineKeyboardButton("⚙️ Pilih Pair", callback_data="at_pair_selector")],
            [InlineKeyboardButton("🔄 Ganti Mode", callback_data="at_mode"),
             InlineKeyboardButton("📐 Lot", callback_data="lot_menu")],
            [InlineKeyboardButton("💰 Set Balance", callback_data="at_back")],
            [InlineKeyboardButton("🔙 Menu", callback_data="menu")],
        ]
    
    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))

async def autotrade_control_callback(update: Update, context):
    """Callback untuk tombol kontrol Auto Trading"""
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == "at_on":
        # 🆕 Cek apakah user sudah memilih pair
        if not autotrade_state["active_pairs"]:
            autotrade_state["active_pairs"] = set(AUTOTRADE_PAIR_CONFIG.keys())
        
        pair_count = len(autotrade_state["active_pairs"])
        pair_list = "\n".join([f"  • {p}" for p in sorted(autotrade_state["active_pairs"])])
        
        autotrade_state["active"] = True
        save_autotrade_state_to_db()
        mode = autotrade_state.get("mode", "paper")
        await query.edit_message_text(
            f"✅ *Auto Trading DIAKTIFKAN*\n\n"
            f"Mode: {mode.upper()}\n"
            f"💰 Balance: ${autotrade_state['balance']:,.2f}\n"
            f"📊 Pair Aktif: {pair_count}\n\n"
            f"*Pair:*\n{pair_list}\n\n"
            f"Gunakan tombol di bawah untuk kontrol:",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 Status", callback_data="at_status"),
                 InlineKeyboardButton("📋 Report", callback_data="at_report")],
                [InlineKeyboardButton("⏹️ Matikan", callback_data="at_off"),
                 InlineKeyboardButton("🔄 Mode", callback_data="at_mode")],
                [InlineKeyboardButton("⚙️ Pilih Pair", callback_data="at_pair_selector")],
                [InlineKeyboardButton("🔙 Menu", callback_data="menu")],
            ])
        )
    
    elif action == "at_off":
        autotrade_state["active"] = False
        save_autotrade_state_to_db()
        await query.edit_message_text(
            "⏹️ *Auto Trading DIMATIKAN*\n\n"
            "Semua posisi yang sudah terbuka tetap berjalan di MT5.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Aktifkan", callback_data="at_on")],
                [InlineKeyboardButton("🔙 Menu", callback_data="menu")],
            ])
        )
    
    elif action == "at_status":
        status = "🟢 AKTIF" if autotrade_state["active"] else "🔴 NON-AKTIF"
        mode = autotrade_state.get("mode", "paper")
        balance = autotrade_state["balance"]
        start_balance = autotrade_state["starting_balance"]
        profit = balance - start_balance
        profit_pct = (profit / start_balance * 100) if start_balance > 0 else 0
        total_trades = autotrade_state["total_trades"]
        wins = autotrade_state["total_wins"]
        losses = autotrade_state["total_losses"]
        wr = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # 🆕 Info pair aktif
        pair_count = len(autotrade_state.get("active_pairs", set()))
        if pair_count == 0:
            pair_info = f"{len(AUTOTRADE_PAIR_CONFIG)} (default)"
        else:
            pair_info = str(pair_count)
        
        msg = (
            f"🤖 *AUTO TRADING STATUS*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Status: {status} | Mode: {mode.upper()}\n"
            f"📊 Pair: {pair_info}\n"
            f"💰 Balance: ${balance:,.2f}\n"
            f"📈 P/L: {profit:+,.2f} ({profit_pct:+.1f}%)\n"
            f"📊 Trades: {total_trades} | WR: {wr:.1f}%\n"
            f"✅ Win: {wins} | ❌ Loss: {losses}\n\n"
        )
        
        open_positions = []
        if "positions" in autotrade_state:
            for pair_symbol, positions in autotrade_state["positions"].items():
                for pos in positions:
                    if pos["status"] == "OPEN":
                        open_positions.append(f"  {'🟢' if pos['direction']=='BUY' else '🔴'} {pair_symbol} {pos['direction']} @ ${pos['entry']:.2f}")
        
        if open_positions:
            msg += "*POSISI TERBUKA:*\n" + "\n".join(open_positions[:5])
        else:
            msg += "*POSISI TERBUKA:* Tidak ada"
        
        await query.edit_message_text(
            msg,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Refresh", callback_data="at_status"),
                 InlineKeyboardButton("📋 Report", callback_data="at_report")],
                [InlineKeyboardButton("⚙️ Pilih Pair", callback_data="at_pair_selector")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="at_back")],
            ])
        )
    
    elif action == "at_mode":
        current_mode = autotrade_state.get("mode", "paper")
        await query.edit_message_text(
            f"⚙️ *PILIH MODE TRADING*\n\n"
            f"Mode saat ini: *{current_mode.upper()}*\n\n"
            f"📄 Paper = Simulasi (tidak kirim ke MT5)\n"
            f"💰 Real = Trading di akun MT5",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(f"{'✅ ' if current_mode == 'paper' else ''}📄 Paper", callback_data="at_mode_paper"),
                 InlineKeyboardButton(f"{'✅ ' if current_mode == 'real' else ''}💰 Real", callback_data="at_mode_real")],
                [InlineKeyboardButton("🔙 Kembali", callback_data="at_back")],
            ])
        )
    
    elif action == "at_mode_paper":
        autotrade_state["mode"] = "paper"
        save_autotrade_state_to_db()
        await query.edit_message_text("✅ Mode diubah ke *PAPER* (Simulasi)\n\nTrading tidak akan dikirim ke MT5.", parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="at_back")]]))
    
    elif action == "at_mode_real":
        autotrade_state["mode"] = "real"
        save_autotrade_state_to_db()
        await query.edit_message_text("✅ Mode diubah ke *REAL*\n\nOrder akan dikirim ke MT5!", parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Kembali", callback_data="at_back")]]))
    
    elif action == "at_report":
        await generate_autotrade_report_from_callback(update)
    
    elif action == "at_back":
        await autotrade_menu_callback(update, context)
        
async def lot_menu_callback(update: Update, context):
    """Callback untuk menu pengaturan lot"""
    query = update.callback_query
    await query.answer()
    action = query.data
    
    if action == "lot_menu":
        # Tampilkan daftar pair dengan lot saat ini
        msg = "📐 *PENGATURAN LOT*\n\n"
        msg += "Pilih pair untuk diatur:\n"
        
        kb = []
        row = []
        for pair_symbol in AUTOTRADE_PAIR_CONFIG:
            custom = LOT_CONFIG.get("custom_lot", {}).get(pair_symbol, {})
            mode = custom.get("mode", LOT_CONFIG["mode"])
            if mode == "FIXED":
                lot_info = f"FIX {custom.get('fixed_lot', LOT_CONFIG['fixed_lot'])}"
            else:
                lot_info = f"AUTO {custom.get('risk_percent', LOT_CONFIG['auto']['risk_percent'])}%"
            
            short = pair_symbol.split("/")[0]
            row.append(InlineKeyboardButton(f"{short}", callback_data=f"lot_pair_{pair_symbol}"))
            if len(row) == 3:
                kb.append(row)
                row = []
        if row:
            kb.append(row)
        
        # Default lot info
        default_mode = LOT_CONFIG["mode"]
        if default_mode == "FIXED":
            default_info = f"Default: FIXED {LOT_CONFIG['fixed_lot']}"
        else:
            default_info = f"Default: AUTO {LOT_CONFIG['auto']['risk_percent']}%"
        
        msg += f"\n{default_info}"
        kb.append([InlineKeyboardButton("🔄 Set Default", callback_data="lot_default")])
        kb.append([InlineKeyboardButton("🔙 Kembali", callback_data="at_back")])
        
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    elif action.startswith("lot_pair_"):
        pair_symbol = action.replace("lot_pair_", "")
        custom = LOT_CONFIG.get("custom_lot", {}).get(pair_symbol, {})
        current_mode = custom.get("mode", LOT_CONFIG["mode"])
        current_value = custom.get("fixed_lot", custom.get("risk_percent", 0.01))
        
        msg = (
            f"📐 *LOT UNTUK {pair_symbol}*\n\n"
            f"Saat ini: {current_mode.upper()} {current_value}\n\n"
            f"Pilih mode:"
        )
        
        kb = [
            [InlineKeyboardButton(f"{'✅' if current_mode=='FIXED' else ''} FIXED", callback_data=f"lot_set_{pair_symbol}_fixed"),
             InlineKeyboardButton(f"{'✅' if current_mode=='AUTO' else ''} AUTO", callback_data=f"lot_set_{pair_symbol}_auto")],
        ]
        
        # Pilihan nilai
        if current_mode == "FIXED":
            values = [0.01, 0.02, 0.03, 0.05, 0.10]
            label = "Lot"
        else:
            values = [0.5, 1.0, 1.5, 2.0, 3.0]
            label = "Risk %"
        
        row = []
        for v in values:
            mark = "✅" if current_value == v else ""
            row.append(InlineKeyboardButton(f"{mark}{v}", callback_data=f"lot_val_{pair_symbol}_{v}"))
            if len(row) == 3:
                kb.append(row)
                row = []
        if row:
            kb.append(row)
        
        kb.append([InlineKeyboardButton("🔙 Kembali", callback_data="lot_menu")])
        
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    elif action.startswith("lot_set_"):
        parts = action.replace("lot_set_", "").split("_")
        pair_symbol = "_".join(parts[:-1])
        mode = parts[-1]
        
        if "custom_lot" not in LOT_CONFIG:
            LOT_CONFIG["custom_lot"] = {}
        
        if mode == "fixed":
            LOT_CONFIG["custom_lot"][pair_symbol] = {"mode": "FIXED", "fixed_lot": 0.01}
        else:
            LOT_CONFIG["custom_lot"][pair_symbol] = {"mode": "AUTO", "risk_percent": 1.0}
        
        # Redirect ke halaman pair
        update.callback_query.data = f"lot_pair_{pair_symbol}"
        await lot_menu_callback(update, context)
    
    elif action.startswith("lot_val_"):
        parts = action.replace("lot_val_", "").split("_")
        value = float(parts[-1])
        pair_symbol = "_".join(parts[:-1])
        
        if "custom_lot" not in LOT_CONFIG:
            LOT_CONFIG["custom_lot"] = {}
        
        custom = LOT_CONFIG.get("custom_lot", {}).get(pair_symbol, {})
        current_mode = custom.get("mode", LOT_CONFIG["mode"])
        
        if current_mode == "FIXED":
            LOT_CONFIG["custom_lot"][pair_symbol] = {"mode": "FIXED", "fixed_lot": value}
        else:
            LOT_CONFIG["custom_lot"][pair_symbol] = {"mode": "AUTO", "risk_percent": value}
        
        # Redirect ke halaman pair
        update.callback_query.data = f"lot_pair_{pair_symbol}"
        await lot_menu_callback(update, context)
    
    elif action == "lot_default":
        default_mode = LOT_CONFIG["mode"]
        default_value = LOT_CONFIG["fixed_lot"] if default_mode == "FIXED" else LOT_CONFIG["auto"]["risk_percent"]
        
        msg = (
            f"📐 *SET DEFAULT LOT*\n\n"
            f"Saat ini: {default_mode} {default_value}\n\n"
            f"Pilih mode default:"
        )
        
        kb = [
            [InlineKeyboardButton(f"{'✅' if default_mode=='FIXED' else ''} FIXED", callback_data="lot_def_set_fixed"),
             InlineKeyboardButton(f"{'✅' if default_mode=='AUTO' else ''} AUTO", callback_data="lot_def_set_auto")],
        ]
        
        if default_mode == "FIXED":
            values = [0.01, 0.02, 0.03, 0.05, 0.10]
        else:
            values = [0.5, 1.0, 1.5, 2.0, 3.0]
        
        row = []
        for v in values:
            row.append(InlineKeyboardButton(str(v), callback_data=f"lot_def_val_{v}"))
            if len(row) == 3:
                kb.append(row)
                row = []
        if row:
            kb.append(row)
        
        kb.append([InlineKeyboardButton("🔙 Kembali", callback_data="lot_menu")])
        
        await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))
    
    elif action.startswith("lot_def_set_"):
        mode = action.replace("lot_def_set_", "")
        LOT_CONFIG["mode"] = mode.upper()
        LOT_CONFIG["custom_lot"] = {}
        update.callback_query.data = "lot_default"
        await lot_menu_callback(update, context)
    
    elif action.startswith("lot_def_val_"):
        value = float(action.replace("lot_def_val_", ""))
        mode = LOT_CONFIG["mode"]
        if mode == "FIXED":
            LOT_CONFIG["fixed_lot"] = value
        else:
            LOT_CONFIG["auto"]["risk_percent"] = value
        LOT_CONFIG["custom_lot"] = {}
        update.callback_query.data = "lot_default"
        await lot_menu_callback(update, context)        


async def generate_autotrade_report_from_callback(update):
    query = update.callback_query
    balance = autotrade_state["balance"]
    start_balance = autotrade_state["starting_balance"]
    profit = balance - start_balance
    profit_pct = (profit / start_balance * 100) if start_balance > 0 else 0
    total_trades = autotrade_state["total_trades"]
    wins = autotrade_state["total_wins"]
    losses = autotrade_state["total_losses"]
    wr = (wins / total_trades * 100) if total_trades > 0 else 0
    
    msg = (
        f"🤖 *AUTO TRADING REPORT*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📅 {datetime.now().strftime('%d %B %Y %H:%M WIB')}\n\n"
        f"💰 Balance: ${balance:,.2f} (P/L: {profit:+,.2f})\n"
        f"📊 Trades: {total_trades} | WR: {wr:.1f}%\n"
        f"✅ Win: {wins} | ❌ Loss: {losses}\n\n"
        f"Mode: {autotrade_state.get('mode', 'paper').upper()}\n"
        f"⚠️ Gunakan broker terpercaya: /broker"
    )
    
    kb = [[InlineKeyboardButton("🔙 Kembali", callback_data="at_back")]]
    await query.edit_message_text(msg, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(kb))


# ==================== MAIN ====================
def main():
    print(f"✨ {BOT_NAME} STARTED")
    print("💱 Forex | 🏢 Saham | ₿ Crypto | 🧂 Micin | 🔔 Alert | 🤖 Auto Trade")
    print("🆕 S01_EMA_Tight | S02_AllInOne_Agg | S04_KC_Scalp | Real MT5 Trading")
    init_db()
    
    # Koneksi ke MT5
    mt5_status_msg = ""
    if not mt5.initialize():
        mt5_status_msg = "❌ *MT5 GAGAL TERHUBUNG*\nPastikan MetaTrader 5 sedang berjalan di VPS."
        print("❌ Gagal koneksi ke MT5. Pastikan MetaTrader 5 sedang berjalan.")
    else:
        account = mt5.account_info()
        if account:
            mt5_status_msg = (
                f"✅ *MT5 TERHUBUNG — VPS*\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 Login: `{account.login}`\n"
                f"🏢 Server: `{account.server}`\n"
                f"💰 Balance: `${account.balance:,.2f}`\n"
                f"💵 Equity: `${account.equity:,.2f}`\n"
                f"📊 Leverage: `1:{account.leverage}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🟢 Auto Trading siap digunakan!"
            )
            print(f"✅ MT5 Connected — Login: {account.login} | Balance: ${account.balance:,.2f}")
        else:
            mt5_status_msg = "⚠️ *MT5 TERHUBUNG*\nTapi tidak bisa membaca info akun.\nCek ulang login di terminal MT5."
            print("⚠️ MT5 terhubung tapi tidak bisa baca info akun.")
    
    # Kirim notifikasi ke semua admin
    for admin_id in ADMIN_IDS:
        try:
            send_telegram_message(admin_id, f"🚀 *{BOT_NAME} BOT STARTED*\n\n{mt5_status_msg}")
        except Exception as e:
            logger.error(f"Gagal kirim notifikasi ke admin {admin_id}: {e}")
    
    # Start workers
    threading.Thread(target=alert_worker, daemon=True).start()
    threading.Thread(target=autotrade_worker, daemon=True).start()
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("redeem", redeem_command))
    app.add_handler(CommandHandler("genvoucher", genvoucher_command))
    app.add_handler(CommandHandler("genlicense", genlicense_command))
    app.add_handler(CommandHandler("forex", forex_command))
    app.add_handler(CommandHandler("saham", saham_command))
    app.add_handler(CommandHandler("crypto", crypto_command))
    app.add_handler(CommandHandler("broker", broker_command))
    app.add_handler(CommandHandler("autotrade", autotrade_command))
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(subscribe_menu_callback, pattern="^subscribe_menu$"))
    app.add_handler(CallbackQueryHandler(trial_start_callback, pattern="^trial_start$"))
    app.add_handler(CallbackQueryHandler(buy_callback, pattern="^buy_"))
    app.add_handler(CallbackQueryHandler(redeem_info_callback, pattern="^redeem_info$"))
    app.add_handler(CallbackQueryHandler(menu_forex_callback, pattern="^menu_forex$"))
    app.add_handler(CallbackQueryHandler(menu_stock_callback, pattern="^menu_stock$"))
    app.add_handler(CallbackQueryHandler(menu_crypto_callback, pattern="^menu_crypto$"))
    app.add_handler(CallbackQueryHandler(menu_meme_callback, pattern="^menu_meme$"))
    app.add_handler(CallbackQueryHandler(autotrade_menu_callback, pattern="^menu_autotrade$"))
    app.add_handler(CallbackQueryHandler(broker_menu_callback, pattern="^broker_menu$"))
    app.add_handler(CallbackQueryHandler(broker_pindah_callback, pattern="^broker_pindah$"))
    app.add_handler(CallbackQueryHandler(menu, pattern="^menu$"))
    app.add_handler(CallbackQueryHandler(analyze_callback, pattern="^ana_"))
    app.add_handler(CallbackQueryHandler(autotrade_pair_selector, pattern="^at_pair_selector$"))
    app.add_handler(CallbackQueryHandler(autotrade_pair_toggle, pattern="^at_pair_toggle_"))
    app.add_handler(CallbackQueryHandler(autotrade_pair_all_on, pattern="^at_pair_all_on$"))
    app.add_handler(CallbackQueryHandler(autotrade_pair_all_off, pattern="^at_pair_all_off$"))
    app.add_handler(CallbackQueryHandler(autotrade_pair_save, pattern="^at_pair_save$"))
    app.add_handler(CallbackQueryHandler(autotrade_control_callback, pattern="^at_(?!pair_)"))
    app.add_handler(CallbackQueryHandler(lot_menu_callback, pattern="^lot_"))
    app.add_handler(CallbackQueryHandler(micin_menu_callback, pattern="^micin_menu$"))
    app.add_handler(CallbackQueryHandler(micin_analyze_callback, pattern="^micin_"))
    app.add_handler(CallbackQueryHandler(saham_menu_callback, pattern="^saham_menu$"))
    app.add_handler(CallbackQueryHandler(dashboard_callback, pattern="^dashboard$"))
    app.add_handler(CallbackQueryHandler(alert_menu, pattern="^alert_menu$"))
    app.add_handler(CallbackQueryHandler(alert_toggle, pattern="^alt_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback))
    
    print("✅ Bot siap!")
    app.run_polling()

if __name__ == "__main__":
    main()