#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════
#   FANTool Setup Script
#   Geliştirici: @FanteriBey
#   Tüm bağımlılıkları otomatik kurar
# ═══════════════════════════════════════════════════════════

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

FANTOOL_DIR="/sdcard/Download/FANTOOL"
INDEX_DIR="$FANTOOL_DIR/index"
SOURCE_DIR="$FANTOOL_DIR/SOURCE"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GITHUB_RAW="https://raw.githubusercontent.com/Fantool34/Fantool/main"

# ── UPDATE MODE ───────────────────────────────────────────────────
if [ "$1" = "update" ]; then
    echo ""
    echo -e "${BOLD}${CYAN}  ⚡ FANTool Güncelleniyor...${NC}"
    echo ""

    # fanteri.py güncelle
    echo -ne "  [1/3] fanteri.py indiriliyor..."
    wget -q "$GITHUB_RAW/fanteri.py" -O "$SCRIPT_DIR/fanteri.py" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${RED}❌ İndirilemedi — internet bağlantısını kontrol et${NC}"
        exit 1
    fi

    # CSV güncelle
    echo -ne "  [2/3] CSV güncelleniyor..."
    wget -q "$GITHUB_RAW/CSV.zip" -O "/tmp/fan_upd_csv.zip" 2>/dev/null
    if [ $? -eq 0 ]; then
        unzip -o /tmp/fan_upd_csv.zip -d /tmp/fan_upd_csv/ > /dev/null 2>&1
        [ -f "/tmp/fan_upd_csv/CSV/BGMI.csv" ] && cp "/tmp/fan_upd_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        [ -f "/tmp/fan_upd_csv/CSV/PUBG.csv" ] && cp "/tmp/fan_upd_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        rm -rf /tmp/fan_upd_csv.zip /tmp/fan_upd_csv/
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${YELLOW}⚠ CSV güncellenemedi (devam ediliyor)${NC}"
    fi

    # Şifrele
    echo -ne "  [3/3] Şifreleniyor..."
    FANTERI_SRC="$SCRIPT_DIR/fanteri.py"
    FIRST_LINE=$(head -2 "$FANTERI_SRC" 2>/dev/null | tail -1)
    if echo "$FIRST_LINE" | grep -q "import marshal"; then
        echo -e " ${GREEN}✅ (zaten şifreli)${NC}"
    else
        python3 << PYENC
import marshal, zlib, base64
src = open('$FANTERI_SRC', 'r', encoding='utf-8').read()
code = compile(src, 'fanteri.py', 'exec')
raw = marshal.dumps(code)
compressed = zlib.compress(raw, 9)
b64 = base64.b85encode(compressed).decode()
loader = '#!/data/data/com.termux/files/usr/bin/python3\nimport marshal,zlib,base64\nexec(marshal.loads(zlib.decompress(base64.b85decode(' + repr(b64) + '))))\n'
open('$FANTERI_SRC', 'w').write(loader)
PYENC
        echo -e " ${GREEN}✅${NC}"
    fi

    echo ""
    echo -e "${BOLD}${GREEN}  ✅ Güncelleme tamamlandı!${NC}"
    echo -e "  ${CYAN}python3 fanteri.py${NC}"
    echo ""
    exit 0
fi

echo ""
echo -e "${BOLD}${CYAN}  ███████╗ █████╗ ███╗  ██╗████████╗ ██████╗  ██████╗ ██╗${NC}"
echo -e "${BOLD}${CYAN}  ██╔════╝██╔══██╗████╗ ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║${NC}"
echo -e "${BOLD}${CYAN}  █████╗  ███████║██╔██╗██║   ██║   ██║   ██║██║   ██║██║${NC}"
echo -e "${BOLD}${CYAN}  ██╔══╝  ██╔══██║██║╚████║   ██║   ██║   ██║██║   ██║██║${NC}"
echo -e "${BOLD}${CYAN}  ██║     ██║  ██║██║ ╚███║   ██║   ╚██████╔╝╚██████╔╝███████╗${NC}"
echo -e "${BOLD}${CYAN}  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚══╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝${NC}"
echo ""
echo -e "${BOLD}            ⚡ KURULUM BAŞLIYOR — by @FanteriBey ⚡${NC}"
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── ADIM 1: Termux paketleri ──────────────────────────────────────
echo -e "${BOLD}${CYAN}[1/6] Termux paketleri kuruluyor...${NC}"
pkg update -y -q 2>/dev/null
pkg install -y python git openjdk-17 unzip wget 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✅ Termux paketleri hazır${NC}"
else
    echo -e "  ${YELLOW}⚠ Bazı paketler kurulamadı, devam ediliyor...${NC}"
fi
echo ""

# ── ADIM 2: Python paketleri ──────────────────────────────────────
echo -e "${BOLD}${CYAN}[2/6] Python paketleri kuruluyor...${NC}"
PYTHON_PKGS="rich pycryptodome zstandard gmalg requests colorama cffi six"
for pkg_name in $PYTHON_PKGS; do
    echo -ne "  Kuruluyor: $pkg_name..."
    pip install $pkg_name --break-system-packages -q 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${YELLOW}⚠${NC}"
    fi
done
echo ""

# ── ADIM 3: FANTOOL klasörleri oluştur ────────────────────────────
echo -e "${BOLD}${CYAN}[3/6] FANTOOL klasörleri oluşturuluyor...${NC}"
DIRS=(
    "$FANTOOL_DIR"
    "$FANTOOL_DIR/index"
    "$FANTOOL_DIR/SOURCE"
    "$FANTOOL_DIR/LUA_ORIGINAL"
    "$FANTOOL_DIR/LUA_EDIT"
    "$FANTOOL_DIR/COMPILED"
    "$FANTOOL_DIR/PAK_UNPACK"
    "$FANTOOL_DIR/BACKUP"
    "$FANTOOL_DIR/DUMP"
    "$FANTOOL_DIR/NEW_ENGINE/INPUT_PAK"
    "$FANTOOL_DIR/NEW_ENGINE/LUA_ORIGINAL"
    "$FANTOOL_DIR/NEW_ENGINE/LUA_EDIT"
    "$FANTOOL_DIR/NEW_ENGINE/LUA_COMPILED"
    "$FANTOOL_DIR/NEW_ENGINE/PAK_EDIT"
    "$FANTOOL_DIR/NEW_ENGINE/RESULT"
    "$FANTOOL_DIR/NEW_ENGINE/SOURCE"
    "$FANTOOL_DIR/NEW_ENGINE/DUMP_PAK/ORIGINAL_PAK"
    "$FANTOOL_DIR/NEW_ENGINE/DUMP_PAK/MOD_PAK"
    "$FANTOOL_DIR/NEW_ENGINE/DUMP_PAK/DUMP_RESULT"
)
for dir in "${DIRS[@]}"; do
    mkdir -p "$dir"
done
echo -e "  ${GREEN}✅ Tüm klasörler oluşturuldu${NC}"
echo ""

# ── ADIM 4: CSV dosyaları ──────────────────────────────────────────
echo -e "${BOLD}${CYAN}[4/6] CSV index dosyaları kuruluyor...${NC}"

# 1. Önce repodaki CSV.zip kontrol et
REPO_CSV="$SCRIPT_DIR/CSV.zip"
DOWNLOAD_CSV="/sdcard/Download/CSV.zip"

if [ -f "$REPO_CSV" ]; then
    echo -e "  ${CYAN}CSV.zip repo içinde bulundu, açılıyor...${NC}"
    unzip -o "$REPO_CSV" -d /tmp/fan_csv/ 2>/dev/null
    if [ -f "/tmp/fan_csv/CSV/BGMI.csv" ]; then
        cp "/tmp/fan_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        echo -e "  ${GREEN}✅ BGMI.csv → $INDEX_DIR/BGMI.csv${NC}"
    fi
    if [ -f "/tmp/fan_csv/CSV/PUBG.csv" ]; then
        cp "/tmp/fan_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        echo -e "  ${GREEN}✅ PUBG.csv → $INDEX_DIR/PUBG.csv${NC}"
    fi
    rm -rf /tmp/fan_csv/
elif [ -f "$DOWNLOAD_CSV" ]; then
    echo -e "  ${CYAN}CSV.zip Download klasöründe bulundu, açılıyor...${NC}"
    unzip -o "$DOWNLOAD_CSV" -d /tmp/fan_csv/ 2>/dev/null
    if [ -f "/tmp/fan_csv/CSV/BGMI.csv" ]; then
        cp "/tmp/fan_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        echo -e "  ${GREEN}✅ BGMI.csv kopyalandı${NC}"
    fi
    if [ -f "/tmp/fan_csv/CSV/PUBG.csv" ]; then
        cp "/tmp/fan_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        echo -e "  ${GREEN}✅ PUBG.csv kopyalandı${NC}"
    fi
    rm -rf /tmp/fan_csv/
else
    echo -e "  ${YELLOW}⚠ CSV.zip bulunamadı${NC}"
    echo -e "  ${YELLOW}  CSV.zip'i /sdcard/Download/ klasörüne koy ve tekrar çalıştır${NC}"
fi
echo ""

# ── ADIM 5: unluac.jar indir ──────────────────────────────────────
echo -e "${BOLD}${CYAN}[5/6] unluac.jar indiriliyor...${NC}"
UNLUAC_PATHS=(
    "$SOURCE_DIR/unluac_patched.jar"
    "$FANTOOL_DIR/NEW_ENGINE/SOURCE/unluac_patched.jar"
)

# Check if Java is available
if command -v java &>/dev/null; then
    UNLUAC_URL="https://downloads.sourceforge.net/project/unluac/Unstable/unluac_2025_12_23.jar"
    UNLUAC_TMP="/tmp/unluac_patched.jar"
    
    echo -ne "  İndiriliyor..."
    wget -q "$UNLUAC_URL" -O "$UNLUAC_TMP" 2>/dev/null
    
    if [ -f "$UNLUAC_TMP" ] && [ -s "$UNLUAC_TMP" ]; then
        for path in "${UNLUAC_PATHS[@]}"; do
            cp "$UNLUAC_TMP" "$path"
        done
        rm -f "$UNLUAC_TMP"
        echo -e " ${GREEN}✅ unluac_patched.jar hazır${NC}"
    else
        echo -e " ${YELLOW}⚠ İndirilemedi (internet kontrolü yap)${NC}"
        echo -e "  ${YELLOW}  Manuel indir: sourceforge.net/projects/unluac${NC}"
        echo -e "  ${YELLOW}  Kaydet: $SOURCE_DIR/unluac_patched.jar${NC}"
    fi
else
    echo -e "  ${YELLOW}⚠ Java bulunamadı — 'pkg install openjdk-17' çalıştır${NC}"
fi
echo ""

# ── ADIM 6: fanteri.py'yi şifrele ve hazırla ──────────────────────
echo -e "${BOLD}${CYAN}[6/6] FANTool hazırlanıyor...${NC}"
FANTERI_SRC="$SCRIPT_DIR/fanteri.py"

if [ -f "$FANTERI_SRC" ]; then
    # Check if already encrypted
    FIRST_LINE=$(head -2 "$FANTERI_SRC" | tail -1)
    if echo "$FIRST_LINE" | grep -q "import marshal"; then
        echo -e "  ${GREEN}✅ fanteri.py zaten şifreli${NC}"
    else
        echo -ne "  Şifreleniyor..."
        python3 << PYENC
import marshal, zlib, base64
src = open('$FANTERI_SRC', 'r', encoding='utf-8').read()
code = compile(src, 'fanteri.py', 'exec')
raw = marshal.dumps(code)
compressed = zlib.compress(raw, 9)
b64 = base64.b85encode(compressed).decode()
loader = '#!/data/data/com.termux/files/usr/bin/python3\nimport marshal,zlib,base64\nexec(marshal.loads(zlib.decompress(base64.b85decode(' + repr(b64) + '))))\n'
open('$FANTERI_SRC', 'w').write(loader)
print(" done")
PYENC
        echo -e "  ${GREEN}✅ Şifrelendi${NC}"
    fi
else
    echo -e "  ${RED}❌ fanteri.py bulunamadı${NC}"
fi
echo ""

# ── Özet ──────────────────────────────────────────────────────────
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BOLD}${GREEN}  ✅ KURULUM TAMAMLANDI!${NC}"
echo ""

# Durum kontrolü
echo -e "  ${BOLD}Durum:${NC}"
java -version &>/dev/null && echo -e "  ${GREEN}✅ Java: $(java -version 2>&1 | head -1)${NC}" || echo -e "  ${RED}❌ Java: kurulu değil${NC}"
python3 -c "import rich" &>/dev/null && echo -e "  ${GREEN}✅ Python paketleri: hazır${NC}" || echo -e "  ${RED}❌ Python paketleri: eksik${NC}"
[ -f "$INDEX_DIR/BGMI.csv" ] && echo -e "  ${GREEN}✅ BGMI.csv: hazır${NC}" || echo -e "  ${YELLOW}⚠ BGMI.csv: eksik${NC}"
[ -f "$SOURCE_DIR/unluac_patched.jar" ] && echo -e "  ${GREEN}✅ unluac.jar: hazır${NC}" || echo -e "  ${YELLOW}⚠ unluac.jar: eksik${NC}"
echo ""
echo -e "  ${BOLD}Başlatmak için:${NC}"
echo -e "  ${CYAN}python3 fanteri.py${NC}"
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
