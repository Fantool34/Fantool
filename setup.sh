#!/data/data/com.termux/files/usr/bin/bash
# ═══════════════════════════════════════════════════════════
#   FANTool Setup Script
#   Geliştirici: @FanteriBey
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
    curl -L --retry 3 -o /tmp/fanteri.tar.gz "$GITHUB_RELEASES/v$LATEST/fanteri.tar.gz"
    if [ $? -eq 0 ] && [ -s /tmp/fanteri.tar.gz ]; then
        tar -xzf /tmp/fanteri.tar.gz -C ~
        rm /tmp/fanteri.tar.gz
        chmod +x ~/fanteri.dist/fanteri.bin
        echo -e " ${GREEN}✅${NC}"
    else
        echo -e " ${RED}❌ İndirilemedi${NC}"
        exit 1
    fi

    # CSV güncelle
    echo -ne "  [2/3] CSV güncelleniyor..."
    wget -q "$GITHUB_RAW/CSV.zip" -O /tmp/fan_upd_csv.zip 2>/dev/null
    if [ $? -eq 0 ]; then
        unzip -o /tmp/fan_upd_csv.zip -d /tmp/fan_upd_csv/ > /dev/null 2>&1
        [ -f "/tmp/fan_upd_csv/CSV/BGMI.csv" ] && cp "/tmp/fan_upd_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        [ -f "/tmp/fan_upd_csv/CSV/PUBG.csv" ] && cp "/tmp/fan_upd_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        rm -rf /tmp/fan_upd_csv.zip /tmp/fan_upd_csv/
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

# ── ADIM 1: Klasörler ─────────────────────────────────────────────
echo -e "${BOLD}${CYAN}[1/4] Klasörler oluşturuluyor...${NC}"
DIRS=(
    "$FANTOOL_DIR" "$INDEX_DIR" "$SOURCE_DIR"
    "$FANTOOL_DIR/LUA_ORIGINAL" "$FANTOOL_DIR/LUA_EDIT"
    "$FANTOOL_DIR/COMPILED" "$FANTOOL_DIR/PAK_UNPACK"
    "$FANTOOL_DIR/BACKUP" "$FANTOOL_DIR/DUMP"
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
for dir in "${DIRS[@]}"; do mkdir -p "$dir"; done
echo -e "  ${GREEN}✅ Tüm klasörler oluşturuldu${NC}"
echo ""

# ── ADIM 2: FANTool binary indir ──────────────────────────────────
echo -e "${BOLD}${CYAN}[2/4] FANTool indiriliyor...${NC}"
LATEST=$(curl -s "$GITHUB_RAW/version.txt" 2>/dev/null | tr -d '[:space:]')
[ -z "$LATEST" ] && LATEST="3.0.0"
echo -e "  Versiyon: ${BOLD}v$LATEST${NC}"
echo -ne "  İndiriliyor (~25MB)..."
curl -L --retry 3 -o /tmp/fanteri.tar.gz "$GITHUB_RELEASES/v$LATEST/fanteri.tar.gz"
if [ $? -eq 0 ] && [ -s /tmp/fanteri.tar.gz ]; then
    tar -xzf /tmp/fanteri.tar.gz -C ~
    rm /tmp/fanteri.tar.gz
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
    unzip -o "$REPO_CSV" -d /tmp/fan_csv/ > /dev/null 2>&1
    [ -f "/tmp/fan_csv/CSV/BGMI.csv" ] && cp "/tmp/fan_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv" && echo -e "  ${GREEN}✅ BGMI.csv${NC}"
    [ -f "/tmp/fan_csv/CSV/PUBG.csv" ] && cp "/tmp/fan_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv" && echo -e "  ${GREEN}✅ PUBG.csv${NC}"
    rm -rf /tmp/fan_csv/
else
    echo -ne "  GitHub'dan indiriliyor..."
    wget -q "$GITHUB_RAW/CSV.zip" -O /tmp/fan_csv.zip 2>/dev/null
    if [ $? -eq 0 ]; then
        unzip -o /tmp/fan_csv.zip -d /tmp/fan_csv/ > /dev/null 2>&1
        [ -f "/tmp/fan_csv/CSV/BGMI.csv" ] && cp "/tmp/fan_csv/CSV/BGMI.csv" "$INDEX_DIR/BGMI.csv"
        [ -f "/tmp/fan_csv/CSV/PUBG.csv" ] && cp "/tmp/fan_csv/CSV/PUBG.csv" "$INDEX_DIR/PUBG.csv"
        rm -rf /tmp/fan_csv.zip /tmp/fan_csv/
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
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BOLD}${GREEN}  ✅ KURULUM TAMAMLANDI!${NC}"
echo ""
echo -e "  ${BOLD}Durum:${NC}"
[ -f ~/fanteri.dist/fanteri.bin ] && echo -e "  ${GREEN}✅ FANTool v$LATEST: hazır${NC}" || echo -e "  ${RED}❌ FANTool: kurulamadı${NC}"
[ -f "$INDEX_DIR/BGMI.csv" ] && echo -e "  ${GREEN}✅ BGMI.csv: hazır${NC}" || echo -e "  ${YELLOW}⚠ BGMI.csv: eksik${NC}"
[ -f "$SOURCE_DIR/unluac_patched.jar" ] && echo -e "  ${GREEN}✅ unluac.jar: hazır${NC}" || echo -e "  ${YELLOW}⚠ unluac.jar: eksik${NC}"
echo ""
echo -e "  ${BOLD}Başlatmak için:${NC}"
echo -e "  ${CYAN}~/fanteri.dist/fanteri.bin${NC}"
echo ""
echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
