# Telegram Monitoring Bot

Telegram Monitoring Bot adalah bot berbasis Python untuk memonitoring sistem server seperti CPU, RAM, Storage, suhu CPU, dan aktivitas login SSH. Bot akan mengirimkan notifikasi melalui Telegram jika kondisi tertentu terpenuhi.

## Fitur
- Monitoring penggunaan CPU, RAM, dan Storage.
- Monitoring suhu CPU.
- Monitoring login dan logout SSH (dengan informasi waktu, username, dan IP).
- Mendukung multiple chat.
- Verifikasi password untuk keamanan.

## Prasyarat
- Python 3.10 atau versi terbaru.
- Library Python yang diperlukan:
  - `python-telegram-bot`
  - `psutil`
  - `asyncio`
  - `httpx`
- Token bot dari Telegram ([BotFather](https://core.telegram.org/bots#botfather)).

## Instalasi
1. Clone repository:
git clone https://github.com/username/telegram-monitoring-bot.git cd telegram-monitoring-bot

2. Install dependencies:
pip install -r requirements.txt

markdown
Copy code

3. Konfigurasi bot:
- Edit file `bot.py` dan ubah:
  ```
  API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
  CHAT_ID = 'YOUR_CHAT_ID(Optional)' 
  ```

4. Jalankan bot:
sudo python3 bot.py

## Cara Penggunaan
- **Command**:
- `/start`: Untuk mengaktifkan bot.
- `/stats`: Menampilkan status sistem (CPU, RAM, Storage, koneksi internet).
- **Notifikasi**:
- CPU, RAM, atau Storage melebihi threshold.
- Suhu CPU di atas batas.
- Login atau logout SSH terdeteksi.

## Konfigurasi Threshold
Edit threshold di file `bot.py`:
CPU_THRESHOLD = 80 # Default: 80% MEMORY_THRESHOLD = 90 # Default: 90% STORAGE_THRESHOLD = 90 # Default: 90% TEMP_THRESHOLD = 70 # Default: 70°C


## Troubleshooting
- Jika bot timeout, pastikan server memiliki koneksi internet.
- Jika terjadi error pada akses log SSH, jalankan bot dengan `sudo`.

## Lisensi
Proyek ini dilisensikan di bawah MIT License.
