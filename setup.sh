#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════
#   FANTool Setup Script
#   Geliştirici: @FanteriBey
<<<<<<< HEAD
#   Tüm bağımlılıkları otomatik kurar
=======
>>>>>>> 6285dc30b74330a352fd4de0081b4f64fbd81ce9
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
<<<<<<< HEAD
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

=======
GITHUB_RAW="https://raw.githubusercontent.com/Fantool34/Fantool/main"
GITHUB_RELEASES="https://github.com/Fantool34/Fantool/releases/download"

# ── UPDATE MODE ───────────────────────────────────────────────────
if [ "$1" = "update" ]; then
    echo ""
    echo -e "${BOLD}${CYAN}  ⚡ FANTool Güncelleniyor...${NC}"
    echo ""

    LATEST=$(curl -s "$GITHUB_RAW/version.txt" 2>/dev/null | tr -d '[:space:]')
    if [ -z "$LATEST" ]; then
        echo -e "  ${RED}❌ Versiyon alınamadı — internet bağlantısını kontrol et${NC}"
        exit 1
    fi

    echo -e "  Yeni versiyon: ${BOLD}v$LATEST${NC}"
    echo ""

    # Binary indir
    echo -ne "  [1/3] Binary indiriliyor (25MB)..."
    curl -L --retry 3 -o $HOME/fanteri.tar.gz "$GITHUB_RELEASES/v$LATEST/fanteri.tar.gz"
    if [ $? -eq 0 ] && [ -s $HOME/fanteri.tar.gz ]; then
        tar -xzf $HOME/fanteri.tar.gz -C ~
        rm $HOME/fanteri.tar.gz
        chmod +x ~/fanteri.dist/fanteri.bin
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${RED}❌ İndirilemedi${NC}"
        exit 1
    fi

    # CSV güncelle
    echo -ne "  [2/3] CSV güncelleniyor..."
    wget -q "$GITHUB_RAW/CSV.zip" -O $HOME/fan_upd_csv.zip 2>/dev/null
    if [ $? -eq 0 ]; then
        unzip -o $HOME/fan_upd_csv.zip -d $HOME/fan_upd_csv/ > /dev/null 2>&1
        [ -f "$HOME/fan_upd_csv/CSV/BGMI.csv" ] && cp "$HOME/fan_upd_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        [ -f "$HOME/fan_upd_csv/CSV/PUBG.csv" ] && cp "$HOME/fan_upd_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        rm -rf $HOME/fan_upd_csv.zip $HOME/fan_upd_csv/
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${YELLOW}⚠ CSV güncellenemedi${NC}"
    fi

    # unluac güncelle
    echo -ne "  [3/3] unluac.jar güncelleniyor..."
    wget -q "$GITHUB_RAW/unluac_patched.jar" -O "$SOURCE_DIR/unluac_patched.jar" 2>/dev/null
    if [ $? -eq 0 ]; then
        cp "$SOURCE_DIR/unluac_patched.jar" "$FANTOOL_DIR/NEW_ENGINE/SOURCE/unluac_patched.jar" 2>/dev/null
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${YELLOW}⚠ Güncellenemedi${NC}"
    fi

    echo ""
    echo -e "${BOLD}${GREEN}  ✅ Güncelleme tamamlandı! v$LATEST${NC}"
    echo -e "  ${CYAN}~/fanteri.dist/fanteri.bin${NC}"
    echo ""
    exit 0
fi

# ── BANNER ────────────────────────────────────────────────────────
>>>>>>> 6285dc30b74330a352fd4de0081b4f64fbd81ce9
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

<<<<<<< HEAD
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
=======
# ── ADIM 1: Klasörler ─────────────────────────────────────────────
echo -e "${BOLD}${CYAN}[1/4] Klasörler oluşturuluyor...${NC}"
DIRS=(
    "$FANTOOL_DIR" "$INDEX_DIR" "$SOURCE_DIR"
    "$FANTOOL_DIR/LUA_ORIGINAL" "$FANTOOL_DIR/LUA_EDIT"
    "$FANTOOL_DIR/COMPILED" "$FANTOOL_DIR/PAK_UNPACK"
    "$FANTOOL_DIR/BACKUP" "$FANTOOL_DIR/DUMP"
>>>>>>> 6285dc30b74330a352fd4de0081b4f64fbd81ce9
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
<<<<<<< HEAD
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
    unzip -o "$REPO_CSV" -d $TMPDIR/fan_csv/ 2>/dev/null
    if [ -f "$TMPDIR/fan_csv/CSV/BGMI.csv" ]; then
        cp "$TMPDIR/fan_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        echo -e "  ${GREEN}✅ BGMI.csv → $INDEX_DIR/BGMI.csv${NC}"
    fi
    if [ -f "$TMPDIR/fan_csv/CSV/PUBG.csv" ]; then
        cp "$TMPDIR/fan_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        echo -e "  ${GREEN}✅ PUBG.csv → $INDEX_DIR/PUBG.csv${NC}"
    fi
    rm -rf $TMPDIR/fan_csv/
elif [ -f "$DOWNLOAD_CSV" ]; then
    echo -e "  ${CYAN}CSV.zip Download klasöründe bulundu, açılıyor...${NC}"
    unzip -o "$DOWNLOAD_CSV" -d $TMPDIR/fan_csv/ 2>/dev/null
    if [ -f "$TMPDIR/fan_csv/CSV/BGMI.csv" ]; then
        cp "$TMPDIR/fan_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        echo -e "  ${GREEN}✅ BGMI.csv kopyalandı${NC}"
    fi
    if [ -f "$TMPDIR/fan_csv/CSV/PUBG.csv" ]; then
        cp "$TMPDIR/fan_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        echo -e "  ${GREEN}✅ PUBG.csv kopyalandı${NC}"
    fi
    rm -rf $TMPDIR/fan_csv/
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
=======
for dir in "${DIRS[@]}"; do mkdir -p "$dir"; done
echo -e "  ${GREEN}✅ Tüm klasörler oluşturuldu${NC}"
echo ""

# ── ADIM 2: FANTool binary indir ──────────────────────────────────
echo -e "${BOLD}${CYAN}[2/4] FANTool indiriliyor...${NC}"
LATEST=$(curl -s "$GITHUB_RAW/version.txt" 2>/dev/null | tr -d '[:space:]')
[ -z "$LATEST" ] && LATEST="3.0.0"
echo -e "  Versiyon: ${BOLD}v$LATEST${NC}"
echo -ne "  İndiriliyor (~25MB)..."
curl -L --retry 3 -o $HOME/fanteri.tar.gz "$GITHUB_RELEASES/v$LATEST/fanteri.tar.gz"
if [ $? -eq 0 ] && [ -s $HOME/fanteri.tar.gz ]; then
    tar -xzf $HOME/fanteri.tar.gz -C ~
    rm $HOME/fanteri.tar.gz
    chmod +x ~/fanteri.dist/fanteri.bin
    echo -e " ${GREEN}✅${NC}"
else
    echo -e " ${RED}❌ İndirilemedi — internet bağlantısını kontrol et${NC}"
    exit 1
fi
echo ""

# ── ADIM 3: CSV ───────────────────────────────────────────────────
echo -e "${BOLD}${CYAN}[3/4] CSV index dosyaları kuruluyor...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_CSV="$SCRIPT_DIR/CSV.zip"
if [ -f "$REPO_CSV" ]; then
    unzip -o "$REPO_CSV" -d $HOME/fan_csv/ > /dev/null 2>&1
    if [ -f "$HOME/fan_csv/CSV/BGMI.csv" ]; then cp "$HOME/fan_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"; echo -e "  ${GREEN}BGMI.csv kuruldu${NC}"; fi
    if [ -f "$HOME/fan_csv/CSV/PUBG.csv" ]; then cp "$HOME/fan_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"; echo -e "  ${GREEN}PUBG.csv kuruldu${NC}"; fi
    rm -rf $HOME/fan_csv/
else
    echo -ne "  GitHub'dan indiriliyor..."
    wget -q "$GITHUB_RAW/CSV.zip" -O $HOME/fan_csv.zip 2>/dev/null
    if [ $? -eq 0 ]; then
        unzip -o $HOME/fan_csv.zip -d $HOME/fan_csv/ > /dev/null 2>&1
        [ -f "$HOME/fan_csv/CSV/BGMI.csv" ] && cp "$HOME/fan_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        [ -f "$HOME/fan_csv/CSV/PUBG.csv" ] && cp "$HOME/fan_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        rm -rf $HOME/fan_csv.zip $HOME/fan_csv/
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${YELLOW}⚠ CSV kurulamadı${NC}"
    fi
fi
echo ""

# ── ADIM 4: unluac.jar ────────────────────────────────────────────
echo -e "${BOLD}${CYAN}[4/4] unluac.jar kuruluyor...${NC}"
pkg install -y openjdk-17 > /dev/null 2>&1
REPO_JAR="$SCRIPT_DIR/unluac_patched.jar"
if [ -f "$REPO_JAR" ]; then
    cp "$REPO_JAR" "$SOURCE_DIR/unluac_patched.jar"
    cp "$REPO_JAR" "$FANTOOL_DIR/NEW_ENGINE/SOURCE/unluac_patched.jar"
    echo -e "  ${GREEN}✅ unluac_patched.jar hazır${NC}"
else
    echo -ne "  İndiriliyor..."
    wget -q "$GITHUB_RAW/unluac_patched.jar" -O "$SOURCE_DIR/unluac_patched.jar" 2>/dev/null
    if [ $? -eq 0 ]; then
        cp "$SOURCE_DIR/unluac_patched.jar" "$FANTOOL_DIR/NEW_ENGINE/SOURCE/unluac_patched.jar"
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${YELLOW}⚠ Manuel indir: sourceforge.net/projects/unluac${NC}"
    fi
fi
echo ""

# ── ÖZET ──────────────────────────────────────────────────────────
>>>>>>> 6285dc30b74330a352fd4de0081b4f64fbd81ce9
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BOLD}${GREEN}  ✅ KURULUM TAMAMLANDI!${NC}"
echo ""
<<<<<<< HEAD

# Durum kontrolü
echo -e "  ${BOLD}Durum:${NC}"
java -version &>/dev/null && echo -e "  ${GREEN}✅ Java: $(java -version 2>&1 | head -1)${NC}" || echo -e "  ${RED}❌ Java: kurulu değil${NC}"
python3 -c "import rich" &>/dev/null && echo -e "  ${GREEN}✅ Python paketleri: hazır${NC}" || echo -e "  ${RED}❌ Python paketleri: eksik${NC}"
=======
echo -e "  ${BOLD}Durum:${NC}"
[ -f ~/fanteri.dist/fanteri.bin ] && echo -e "  ${GREEN}✅ FANTool v$LATEST: hazır${NC}" || echo -e "  ${RED}❌ FANTool: kurulamadı${NC}"
>>>>>>> 6285dc30b74330a352fd4de0081b4f64fbd81ce9
[ -f "$INDEX_DIR/BGMI.csv" ] && echo -e "  ${GREEN}✅ BGMI.csv: hazır${NC}" || echo -e "  ${YELLOW}⚠ BGMI.csv: eksik${NC}"
[ -f "$SOURCE_DIR/unluac_patched.jar" ] && echo -e "  ${GREEN}✅ unluac.jar: hazır${NC}" || echo -e "  ${YELLOW}⚠ unluac.jar: eksik${NC}"
echo ""
echo -e "  ${BOLD}Başlatmak için:${NC}"
<<<<<<< HEAD
echo -e "  ${CYAN}./fanteri.bin${NC}"
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
# unluac repodan kopyala
SCRIPT_DIR2="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR2/unluac_patched.jar" ]; then
  cp "$SCRIPT_DIR2/unluac_patched.jar" /sdcard/Download/FANTOOL/SOURCE/unluac_patched.jar
  cp "$SCRIPT_DIR2/unluac_patched.jar" /sdcard/Download/FANTOOL/NEW_ENGINE/SOURCE/unluac_patched.jar
  echo "✅ unluac.jar kopyalandı"
fi
=======
echo -e "  ${CYAN}~/fanteri.dist/fanteri.bin${NC}"
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
>>>>>>> 6285dc30b74330a352fd4de0081b4f64fbd81ce9
