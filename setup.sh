#!/data/data/com.termux/files/usr/bin/bash
echo "FANTool kuruluyor..."
pkg install python git unzip wget -y 2>/dev/null
pip install rich pycryptodome zstandard gmalg colorama cffi six requests --break-system-packages -q 2>/dev/null
mkdir -p /sdcard/Download/FANTOOL/index
mkdir -p /sdcard/Download/FANTOOL/SOURCE
mkdir -p /sdcard/Download/FANTOOL/NEW_ENGINE/SOURCE
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/CSV.zip" ]; then
  unzip -o "$SCRIPT_DIR/CSV.zip" -d $TMPDIR/fancsv/ 2>/dev/null
  cp $TMPDIR/fancsv/CSV/BGMI.csv /sdcard/Download/FANTOOL/index/ 2>/dev/null
  cp $TMPDIR/fancsv/CSV/PUBG.csv /sdcard/Download/FANTOOL/index/ 2>/dev/null
  echo "CSV dosyalari kopyalandi"
fi
if [ -f "$SCRIPT_DIR/unluac_patched.jar" ]; then
  cp "$SCRIPT_DIR/unluac_patched.jar" /sdcard/Download/FANTOOL/SOURCE/
  cp "$SCRIPT_DIR/unluac_patched.jar" /sdcard/Download/FANTOOL/NEW_ENGINE/SOURCE/
fi
chmod +x "$SCRIPT_DIR/fanteri.bin"
echo "KURULUM TAMAMLANDI!"
echo "Baslatmak icin: ./fanteri.bin"
