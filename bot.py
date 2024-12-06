import psutil
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue
import asyncio
import socket
import os
import subprocess
from datetime import datetime, timedelta

# Konfigurasi Threshold dan Chat ID
CHAT_ID = "6652516735"  # Ganti dengan chat_id Telegram Anda
CPU_THRESHOLD = 80       # Alert jika CPU di atas 80%
MEMORY_THRESHOLD = 90    # Alert jika RAM di atas 90%
STORAGE_THRESHOLD = 90   # Alert jika storage di atas 90%
TEMP_THRESHOLD = 70      # Alert jika suhu CPU di atas 70°C
CHECK_INTERVAL = 60      # Interval cek sistem dalam detik
SSH_LOG_FILE = "/var/log/auth.log"  # Log file untuk SSH login (ubah jika perlu)

prev_cpu_status = {"usage": 0, "alerted": False}
prev_ram_status = {"usage": 0, "alerted": False}
prev_storage_status = {"usage": 0, "alerted": False}
prev_temp_alerted = False  # Menyimpan status suhu CPU

# Fungsi untuk cek koneksi internet
def check_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Fungsi untuk kirim alert ke Telegram
async def send_alert(context, message):
    await context.bot.send_message(chat_id=CHAT_ID, text=f"⚠️ ALERT!\n{message}")

# Fungsi untuk konversi waktu UTC ke WIB
def convert_to_wib(utc_time_str, log_format="%b %d %H:%M:%S"):
    try:
        utc_time = datetime.strptime(utc_time_str, log_format)
        utc_time = utc_time.replace(year=datetime.now().year)  # Tambah tahun ke waktu log
        wib_time = utc_time + timedelta(hours=7)  # WIB = UTC + 7 jam
        return wib_time.strftime("%Y-%m-%d %H:%M:%S WIB")
    except ValueError:
        return "Invalid Time"

# Fungsi untuk monitoring login SSH
async def monitor_ssh_log(context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(SSH_LOG_FILE, "r") as log:
            log.seek(0, os.SEEK_END)  # Mulai dari akhir file
            while True:
                line = log.readline()
                if not line:
                    await asyncio.sleep(1)  # Tunggu jika tidak ada baris baru
                    continue
                if "Accepted password" in line or "Accepted publickey" in line:
                    parts = line.split()
                    timestamp = convert_to_wib(" ".join(parts[:3])) # Ambil tanggal dan waktu
                    user = parts[8]  # Nama user yang login
                    ip = parts[10]  # IP address
                    message = f"SSH Login detected!\nTime: {timestamp}\nUser: {user}\nIP: {ip}"
                    await send_alert(context, message)  # Kirim ke Telegram
                elif "session closed for user" in line:
                    parts = line.split()
                    timestamp = convert_to_wib(" ".join(parts[:3]))
                    user = parts[10]
                    message = f"SSH Logout detected!\nTime: {timestamp}\nUser: {user}"
                    await send_alert(context, message)

    except FileNotFoundError:
        print(f"Log file {SSH_LOG_FILE} tidak ditemukan.")
    except PermissionError:
        print(f"Tidak punya izin untuk membaca {SSH_LOG_FILE}. Jalankan dengan sudo.")

# Fungsi untuk monitoring sistem
async def monitor_system(context: ContextTypes.DEFAULT_TYPE):
    global prev_cpu_status, prev_ram_status, prev_storage_status, prev_temp_alerted
    while True:
        try:
            # Monitoring CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > CPU_THRESHOLD and not prev_cpu_status["alerted"]:
                await send_alert(context, f"⚠️ CPU usage tinggi: {cpu_percent}%")
                prev_cpu_status["alerted"] = True
            elif cpu_percent <= CPU_THRESHOLD and prev_cpu_status["alerted"]:
                prev_cpu_status["alerted"] = False  # Reset jika kembali normal

            # Monitoring RAM
            ram = psutil.virtual_memory()
            if ram.percent > MEMORY_THRESHOLD and not prev_ram_status["alerted"]:
                await send_alert(context, f"⚠️ RAM usage tinggi: {ram.percent}%")
                prev_ram_status["alerted"] = True
            elif ram.percent <= MEMORY_THRESHOLD and prev_ram_status["alerted"]:
                prev_ram_status["alerted"] = False

            # Monitoring Storage
            disk = psutil.disk_usage('/')
            if disk.percent > STORAGE_THRESHOLD and not prev_storage_status["alerted"]:
                await send_alert(context, f"⚠️ Storage hampir penuh: {disk.percent}%")
                prev_storage_status["alerted"] = True
            elif disk.percent <= STORAGE_THRESHOLD and prev_storage_status["alerted"]:
                prev_storage_status["alerted"] = False

            # Monitoring Suhu CPU
            try:
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read().strip()) / 1000
                if temp > TEMP_THRESHOLD and not prev_temp_alerted:
                    await send_alert(context, f"⚠️ Suhu CPU tinggi: {temp:.1f}°C")
                    prev_temp_alerted = True
                elif temp <= TEMP_THRESHOLD and prev_temp_alerted:
                    prev_temp_alerted = False  # Reset alert jika suhu kembali normal
            except FileNotFoundError:
                print("Sensor suhu CPU tidak tersedia.")

            # Cek per jam jika di bawah threshold
            if not prev_cpu_status["alerted"] and not prev_ram_status["alerted"] and not prev_storage_status["alerted"]:
                now = datetime.now()
                if now.minute == 0:  # Cek hanya di awal jam
                    await send_alert(context, "📊 Sistem normal:\n" +
                                     f"CPU: {cpu_percent}%\n" +
                                     f"RAM: {ram.percent}%\n" +
                                     f"Storage: {disk.percent}%")

        except Exception as e:
            print(f"Error in monitoring: {str(e)}")

        await asyncio.sleep(CHECK_INTERVAL)

# Function untuk command /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id 
    await update.message.reply_text("Bot monitoring sistem aktif! Anda akan menerima alert otomatis.")

# Function untuk command /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = f"""
CPU: {psutil.cpu_percent()}%
RAM: {psutil.virtual_memory().percent}% 
Storage: {psutil.disk_usage('/').percent}% 
Internet: {'Connected' if check_internet() else 'Disconnected'}
"""
    await update.message.reply_text(stats)

# Main function
def main():
    API_TOKEN = '7650472102:AAH1_aktpa3zrt8FLrYS_vRkmxKAh-daiAY'

    # Build aplikasi Telegram bot
    application = ApplicationBuilder().token(API_TOKEN).build()

    # Tambahin handler buat command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))

    # Tambahkan monitoring sistem sebagai job
    job_queue = application.job_queue
    job_queue.run_repeating(monitor_system, interval=CHECK_INTERVAL, first=0)

    # Jalankan monitoring login SSH sebagai task async
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_ssh_log(application))

    # Start bot
    application.run_polling()

if __name__ == '__main__':
    main()
