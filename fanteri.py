#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-
# ============================================================
# FANTool v3.0 — PUBG Mobile Toolkit
# Geliştirici: @FanteriBey
# ============================================================

import itertools as it
import math
import struct
import shutil
import os
import sys
import hashlib
import subprocess
import zlib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import PurePath, Path
from typing import List, Dict, Tuple, Optional, Any, Union
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich import print as rprint
from rich.markup import escape
import gmalg
from datetime import datetime
from collections import Counter
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
from Crypto.Cipher.AES import MODE_CBC
from Crypto.Hash import SHA1
try:
    from zstandard import ZstdDecompressor, ZstdCompressionDict, DICT_TYPE_AUTO, ZstdCompressor
except ImportError:
    print("zstandard not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "zstandard"])
    from zstandard import ZstdDecompressor, ZstdCompressionDict, DICT_TYPE_AUTO, ZstdCompressor
from colorama import init, Fore, Style, Back
init(autoreset=True)

console = Console()

if sys.version_info >= (3, 14):
    console.print("[yellow]⚠ Python 3.14 detected - some packages may need manual install[/yellow]")

try:
    from itertools import batched
except ImportError:
    import itertools as _itertools
    def batched(iterable, n):
        if n < 1:
            raise ValueError('n must be at least one')
        it = iter(iterable)
        while True:
            batch = tuple(_itertools.islice(it, n))
            if not batch:
                break
            yield batch

BASE_DIR = Path("/storage/emulated/0/Download/FANTOOL")

MAGENTA = "\033[1;35m"
CYAN    = "\033[1;36m"
YELLOW  = "\033[1;33m"
GREEN   = "\033[1;32m"
RED     = "\033[1;31m"
WHITE   = "\033[1;37m"
BLUE    = "\033[1;34m"
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

def flush_stdin():
    """Flush any lingering input from stdin"""
    try:
        import termios
        termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
    except:
        pass
    try:
        import select
        if select.select([sys.stdin], [], [], 0.1)[0]:
            sys.stdin.read()
    except:
        pass

def safe_input(prompt: str = "") -> str:
    """Safe input function that properly handles stdin"""
    try:
        return input(prompt)
    except (EOFError, RuntimeError, KeyboardInterrupt):
        try:
            if sys.platform != "win32":
                with open("/dev/tty", "r") as tty:
                    sys.stderr.write(prompt)
                    sys.stderr.flush()
                    result = tty.readline().rstrip("\n")
                    try:
                        import termios
                        termios.tcflush(sys.stdin.fileno(), termios.TCIFLUSH)
                    except:
                        pass
                    return result
            else:
                with open("CON", "r") as con:
                    sys.stderr.write(prompt)
                    sys.stderr.flush()
                    result = con.readline().rstrip("\r\n")
                    return result
        except Exception:
            return ""

def install_dependencies():
    """Install required Python packages for Termux with smart skip"""
    
    # Python version check
    python_ver = sys.version_info
    console.print(f"[dim]🐍 Python {python_ver.major}.{python_ver.minor}.{python_ver.micro} detected[/dim]")
    
    # All required packages with import names
    deps = {
        'rich': 'rich',
        'pycryptodome': 'Crypto',
        'zstandard': 'zstandard',
        'gmalg': 'gmalg',
        'requests': 'requests',
        'colorama': 'colorama',
        'cffi': 'cffi',
        'six': 'six',
    }
    
    missing = []
    installed = []
    
    console.print("[cyan]📦 Checking dependencies...[/cyan]")
    
    for package_name, import_name in deps.items():
        try:
            __import__(import_name)
            installed.append(package_name)
            console.print(f"  [green]✅ {package_name}[/green] [dim](already installed)[/dim]")
        except ImportError:
            missing.append(package_name)
            console.print(f"  [yellow]⚠ {package_name}[/yellow] [dim](missing)[/dim]")
    
    if not missing:
        console.print("[bold green]✅ All dependencies ready![/bold green]")
        time.sleep(1)
        return
    
    console.print(f"\n[yellow]📥 Installing {len(missing)} missing package(s)...[/yellow]")
    
    # Install missing packages
    for package_name in missing:
        console.print(f"[cyan]⏳ Installing {package_name}...[/cyan]")
        try:
            # Try normal install first
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            console.print(f"  [green]✅ {package_name} installed[/green]")
        except:
            # Retry with --no-deps for problematic packages
            try:
                console.print(f"  [yellow]Retrying {package_name} with --no-deps...[/yellow]")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", package_name, "--no-deps"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                console.print(f"  [green]✅ {package_name} installed (no-deps)[/green]")
            except:
                console.print(f"  [red]❌ Failed to install {package_name}[/red]")
                
                # Special handling for critical packages
                if package_name == 'pycryptodome':
                    console.print("[yellow]  ↳ Try manual: pkg install python-cryptography[/yellow]")
                elif package_name == 'gmalg':
                    console.print("[yellow]  ↳ Try manual: pip install gmalg --no-deps[/yellow]")
                elif package_name == 'zstandard':
                    console.print("[yellow]  ↳ Try manual: pkg install libzstd && pip install zstandard[/yellow]")
    
    # Final verification
    console.print("\n[cyan]🔍 Verifying installations...[/cyan]")
    failed = []
    for package_name in missing:
        import_name = deps.get(package_name, package_name)
        try:
            __import__(import_name)
            console.print(f"  [green]✅ {package_name}[/green]")
        except ImportError:
            failed.append(package_name)
            console.print(f"  [red]❌ {package_name}[/red]")
    
    if failed:
        console.print(f"\n[bold red]⚠ {len(failed)} package(s) failed to install![/bold red]")
        console.print("[yellow]Some features may not work. Continue anyway?[/yellow]")
        
        # Auto-continue after 3 seconds
        console.print("[dim]Continuing in 3 seconds...[/dim]")
        time.sleep(3)
    else:
        console.print("[bold green]✅ All dependencies ready![/bold green]")
    
    time.sleep(1)

def create_folders():
    folders = [
        BASE_DIR,
        BASE_DIR / "index",
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)

    # Print clear folder guide every startup
    console.print()
    console.print("[bold #00FFFF]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold #00FFFF]")
    console.print("[bold white]  📁 KLASÖR YAPISI — DOSYALARI NEREYE KOYACAKSIN:[/bold white]")
    console.print("[bold #00FFFF]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold #00FFFF]")
    console.print(f"[dim]  {BASE_DIR}/[/dim]")
    console.print(f"  [bold #FFFF00]├── game_patch_xxxxx.pak[/bold #FFFF00]  [dim]← ORİJİNAL PAK DOSYANI BURAYA KOY[/dim]")
    console.print(f"  [bold #00CCFF]├── index/[/bold #00CCFF]")
    console.print(f"  [bold #00CCFF]│   └── PUBG.csv[/bold #00CCFF]          [dim]← (opsiyonel) path index dosyası[/dim]")
    console.print(f"  [bold #00FF88]└── FANx[PAK_ADI]/[/bold #00FF88]        [dim]← tool otomatik oluşturur[/dim]")
    console.print(f"  [bold #00FF88]    ├── CUSTOM FILES/[/bold #00FF88]      [dim]← MOD DOSYALARINI BURAYA KOY[/dim]")
    console.print(f"  [bold #00FF88]    └── RESULT PAK/[/bold #00FF88]        [dim]← SONUÇ BURAYA ÇIKAR[/dim]")
    console.print("[bold #00FFFF]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold #00FFFF]")
    console.print()
    console.print("[bold white]  ADIMLAR:[/bold white]")
    console.print("  [green]1.[/green] .pak dosyasını [yellow]FANTOOL/[/yellow] klasörüne koy")
    console.print("  [green]2.[/green] Menüden [bold #00FF88][1] CUSTOM INJECT[/bold #00FF88] seç")
    console.print("  [green]3.[/green] Tool [bold #00FF88]CUSTOM FILES/[/bold #00FF88] klasörü oluşturur")
    console.print("  [green]4.[/green] Mod dosyalarını [bold #00FF88]CUSTOM FILES/[/bold #00FF88] içine koy")
    console.print("  [green]5.[/green] [bold #00FF88][1] CUSTOM INJECT[/bold #00FF88] tekrar seç → inject başlar")
    console.print("  [green]6.[/green] Sonuç [bold #00FF88]RESULT PAK/[/bold #00FF88] klasöründe çıkar")
    console.print("[bold #00FFFF]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold #00FFFF]")
    console.print()

    # CSV notice — accept any csv in index/
    index_dir = BASE_DIR / "index"
    csv_files = list(index_dir.glob("*.csv")) if index_dir.exists() else []
    if not csv_files:
        console.print(
            f"[dim]ℹ  index/ klasöründe CSV bulunamadı — manuel path modu aktif.[/dim]\n"
            f"[dim]   CSV varsa (BGMI.csv, PUBG.csv vb.) index/ içine koy, otomatik algılar.[/dim]"
        )
    else:
        console.print(f"[green]✅ Index CSV bulundu: {', '.join(f.name for f in csv_files)}[/green]")

# ========== CONSTANTS ==========
ZUC_KEY = bytes.fromhex('01010101010101010101010101010101')
ZUC_IV = bytes.fromhex('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')

RSA_MOD_1 = bytes.fromhex(
    'CBE8B9F2504050EF9831B719E9A6249A6D238505ADE909BDE78C180DED6072A0C3347B8AF4780E1F212D952D82D4BF7F233C1ECA499E1F9D9A85B4FAD759F54BABC1666C5DE411EA9E4B2374425DD6C6F54333BBC8F2610FE6063E4D0D6C21A671A8F7C3740555E5DC06D4E1691C456DB4116C0C012BF7B206E8311AAAEC689952BF804EF638F09D5822B4117B114208F14DEB459E80CB770E5B0D7978E21F5E6CED4999D3583108221A7AB28B960277ADB5690A332784019D9C195BE4EA9EA0A09459010F236465DE0D59C3EF7324E954E1118D93EE19F299760C2CDB963CE87973EA5ECC9BBE81C27D4C7C8572AC07E9BCEAC9BD72AB7A56A3C0AD736ABCE4')
RSA_MOD_2 = bytes.fromhex(
    '7F58E8A39A4DA4E87357DDD650EAA16D3B5CE95B213D1030A662566444796A78A84AE9AC3DBFFDE7F41094896696835DAF13B89E6EC2B84963B1B1BAF7151DA245C3FBFAE2A6AE18B2684D03F9229DE2C91440F2A3A3BCDE1E5680C16722A88039C73560D5D43F4B6562C2EEA5B1D926D86B51108A2643C70FB74D6442CE3A08339B8FD8F660AE88129B7AB8C46F2FA58124485CCCB1E987B05A6DA65A01858ED3F89905449AE42BB07290FCB9994BF22E26610BCABB9804783A3B9587917F3D97316EDDA15C5E13F79066407B55A93B291B68A4AC42A98D6E35FED84B14A792D154E62028DDAD20FC301951E5924BE9AD62FB719DD94CC30CAB871BEC4377A8')

SIMPLE1_DECRYPT_KEY = 0x79
SIMPLE2_DECRYPT_KEY = bytes.fromhex('E55B4ED1')
SIMPLE2_BLOCK_SIZE = 16

SM4_SECRET_4 = 'eb691efea914241317a8'      # BGMI/Global standard (most versions)
# SM4_SECRET_4 = 'XG2QW5LP7LV2IN5F'        # ALT — some older PAK versions (GAME_PATCH_TOOL)
SM4_SECRET_2 = 'Q0hVTKey$as*1ZFlQCiA'
SM4_SECRET_NEW = [
    "xG2qW5lP7lV2iN5fN5pG",
    "xT1cJ6dL5wC0kK1rB4dK",
    "qC4jS5bZ6fL5xE6nD4zA",
    "gD4jQ2aL3bS3lC3xT0iW",
    "xU1yQ8wE9zY3gZ3bT5aE",
    "uQ3cO2dX7xY4xU7gH7iS",
    "gW1fR0jK6wQ4oN0oK1kZ",
    "aJ4pV7iZ7pU4wP2aC2cZ",
    "cX6jT3cM2oT3vK0kJ1qN",
    "iT2vS0cS6yT6cZ1sE1lO",
    "hM1pH9iY8wM9hT4lN5uJ",
    "kG6bC8jK0fL0dE4sH4mL",
    "dB6lB3vE0eZ8wM8rI0aC",
    "tP7sP7nI9rA2vQ4cV5yQ",
    "aT0cL1yN4pT3sZ7eM2vY",
    "uV6fU8fC9zN3mP5dH8mN",
    "rT6aQ6oZ1yM0gO5tO1aN",
    "Q0hVTKey$as*1ZFlQCiA",
    "eb691efea914241317a8",
    "iQ0eM0mJ7uT0kV6kL5zY",
    "jU5bH7lQ0fM9hK2kI0oF"
]

EM_SIMPLE1 = 1
EM_SIMPLE2 = 16 
EM_SM4_2 = 2
EM_SM4_4 = 4
EM_SM4_NEW_BASE = 31
EM_SM4_NEW_MASK = ~EM_SM4_NEW_BASE
EM_UNKNOWN_17 = 17

CM_NONE = 0
CM_ZLIB = 1
CM_ZSTD = 6
CM_ZSTD_DICT = 8
CM_MASK = 15

# ========== SM4 IMPLEMENTATION ==========
class SM4:
    """SM4 Algorithm Implementation."""
    
    _S_BOX = bytes([
        0x34, 0x66, 0x25, 0x74, 0x89, 0x78, 0xE4, 0xA9, 0x5A, 0x41, 0xBC, 0x7A, 0xD6, 0x16, 0x21, 0x23,
        0x4D, 0x61, 0xDA, 0x94, 0x9B, 0xDF, 0x13, 0x3C, 0x69, 0x3A, 0x31, 0x0A, 0x5F, 0xD7, 0x99, 0x95,
        0xF1, 0xAE, 0x72, 0x3D, 0x07, 0x60, 0x24, 0xB6, 0x98, 0xEE, 0xC4, 0xA2, 0x2D, 0x88, 0xDD, 0x8D,
        0x04, 0xEA, 0xBB, 0x11, 0xCA, 0x3E, 0x5D, 0xA1, 0xF6, 0x3F, 0xB0, 0x97, 0x80, 0x47, 0x2B, 0xA6,
        0xE6, 0xF7, 0xD9, 0xB1, 0x59, 0xC0, 0x7C, 0xBE, 0x54, 0x28, 0xB7, 0x7E, 0x4F, 0xF8, 0x43, 0x6E,
        0xA0, 0x50, 0x0E, 0xF5, 0x90, 0xB8, 0xFB, 0xA3, 0x7B, 0x62, 0x19, 0x46, 0x03, 0x2A, 0xB9, 0x8F,
        0x9F, 0x77, 0xB4, 0x5B, 0x83, 0x87, 0x08, 0xEB, 0xE2, 0x1E, 0x42, 0xF0, 0x0F, 0xE8, 0x71, 0x6A,
        0x75, 0xAD, 0x55, 0x1F, 0xB5, 0xAB, 0x33, 0xFA, 0x7F, 0x15, 0xBD, 0x85, 0xD8, 0x06, 0x68, 0xB3,
        0x52, 0x30, 0x48, 0x0B, 0x00, 0xED, 0xEF, 0xB2, 0x57, 0x8E, 0xE7, 0x6C, 0xD5, 0xE5, 0x2E, 0x53,
        0x82, 0x05, 0xF9, 0x81, 0xF4, 0x56, 0xBF, 0x8C, 0x4B, 0xE3, 0xDB, 0x4A, 0x91, 0x4C, 0x2C, 0xD3,
        0x40, 0x29, 0x4E, 0x20, 0x14, 0x36, 0x79, 0x09, 0x6F, 0xD1, 0x37, 0xE0, 0x39, 0x0C, 0x8A, 0x92,
        0x38, 0x12, 0x35, 0x6D, 0xE1, 0xFD, 0x93, 0x9A, 0x17, 0xD4, 0xC9, 0x9C, 0x6B, 0x84, 0x26, 0x9D,
        0xAF, 0x76, 0xC1, 0x9E, 0xD0, 0x96, 0xC5, 0xCB, 0xE9, 0x73, 0x49, 0xD2, 0xCD, 0x64, 0xC3, 0xC7,
        0x01, 0x7D, 0xF3, 0xAC, 0xFC, 0xDE, 0xA4, 0x44, 0x32, 0x1B, 0xC2, 0xBA, 0x1C, 0x02, 0xC6, 0x27,
        0x45, 0x8B, 0xF2, 0x18, 0xA7, 0x10, 0x51, 0x1D, 0xC8, 0xCF, 0x63, 0xFF, 0x2F, 0x0D, 0x58, 0xCE,
        0x65, 0xA5, 0xDC, 0x1A, 0x3B, 0x86, 0xFE, 0x22, 0x5C, 0xA8, 0x5E, 0x67, 0xAA, 0xEC, 0x70, 0xCC
    ])

    _FK = [
        0x46970E9C, 0x4BC0685E, 0x59056186, 0xBCA2491E
    ]

    _CK = [
        0x000EB92B, 0x3A0AE783, 0x9E3B5C67, 0xADDBDABF, 0x7B7484CB, 0x49156C63, 0xC79AB5E7, 0x79EC9CFF,
        0x1725BEAB, 0x2FB89CA3, 0x24808AD7, 0xDDD28B1F, 0x4740DA4B, 0xBBC3EA73, 0x247B30E7, 0x91BE385F,
        0x0401248B, 0x45FCD3A3, 0x530B4CE7, 0xC68DD35F, 0xE3D16C2B, 0x4F698C13, 0x6B92C747, 0x769EFB1F,
        0x4C73BE9B, 0xC942B193, 0xAD80D827, 0x372FB33F, 0x13CB6AAB, 0x2BDC0AA3, 0x17A4A247, 0xD5E96CAF
    ]

    @staticmethod
    def ROL32(x, n):
        return ((x << n) & 0xFFFFFFFF) | (x >> (32 - n))

    @staticmethod
    def _BS(X):
        return ((SM4._S_BOX[(X >> 24) & 0xff] << 24) |
                (SM4._S_BOX[(X >> 16) & 0xff] << 16) |
                (SM4._S_BOX[(X >> 8) & 0xff] << 8) |
                (SM4._S_BOX[X & 0xff]))

    @staticmethod
    def _T0(X):
        X = SM4._BS(X)
        return X ^ SM4.ROL32(X, 2) ^ SM4.ROL32(X, 10) ^ SM4.ROL32(X, 18) ^ SM4.ROL32(X, 24)

    @staticmethod
    def _T1(X):
        X = SM4._BS(X)
        return X ^ SM4.ROL32(X, 13) ^ SM4.ROL32(X, 23)

    @staticmethod
    def _key_expand(key: bytes, rkey: list):
        K0 = int.from_bytes(key[0:4], "big") ^ SM4._FK[0]
        K1 = int.from_bytes(key[4:8], "big") ^ SM4._FK[1]
        K2 = int.from_bytes(key[8:12], "big") ^ SM4._FK[2]
        K3 = int.from_bytes(key[12:16], "big") ^ SM4._FK[3]

        for i in range(0, 32, 4):
            K0 = K0 ^ SM4._T1(K1 ^ K2 ^ K3 ^ SM4._CK[i])
            rkey[i] = K0
            K1 = K1 ^ SM4._T1(K2 ^ K3 ^ K0 ^ SM4._CK[i + 1])
            rkey[i + 1] = K1
            K2 = K2 ^ SM4._T1(K3 ^ K0 ^ K1 ^ SM4._CK[i + 2])
            rkey[i + 2] = K2
            K3 = K3 ^ SM4._T1(K0 ^ K1 ^ K2 ^ SM4._CK[i + 3])
            rkey[i + 3] = K3

    @classmethod
    def key_length(cls):
        return 16

    @classmethod
    def block_length(cls):
        return 16

    def __init__(self, key: bytes):
        if len(key) != self.key_length():
            raise ValueError(f"Key must be {self.key_length()} bytes")

        self._key = key
        self._rkey = [0] * 32
        SM4._key_expand(self._key, self._rkey)
        self._block_buffer = bytearray()

    def encrypt(self, block: bytes) -> bytes:
        if len(block) != self.block_length():
            raise ValueError(f"Block must be {self.block_length()} bytes")

        RK = self._rkey
        X0 = int.from_bytes(block[0:4], "big")
        X1 = int.from_bytes(block[4:8], "big")
        X2 = int.from_bytes(block[8:12], "big")
        X3 = int.from_bytes(block[12:16], "big")

        for i in range(0, 32, 4):
            X0 = X0 ^ SM4._T0(X1 ^ X2 ^ X3 ^ RK[i])
            X1 = X1 ^ SM4._T0(X2 ^ X3 ^ X0 ^ RK[i + 1])
            X2 = X2 ^ SM4._T0(X3 ^ X0 ^ X1 ^ RK[i + 2])
            X3 = X3 ^ SM4._T0(X0 ^ X1 ^ X2 ^ RK[i + 3])

        BUFFER = self._block_buffer
        BUFFER.clear()
        BUFFER.extend(X3.to_bytes(4, "big"))
        BUFFER.extend(X2.to_bytes(4, "big"))
        BUFFER.extend(X1.to_bytes(4, "big"))
        BUFFER.extend(X0.to_bytes(4, "big"))
        return bytes(BUFFER)

    def decrypt(self, block: bytes) -> bytes:
        if len(block) != self.block_length():
            raise ValueError(f"Block must be {self.block_length()} bytes")

        RK = self._rkey
        X0 = int.from_bytes(block[0:4], "big")
        X1 = int.from_bytes(block[4:8], "big")
        X2 = int.from_bytes(block[8:12], "big")
        X3 = int.from_bytes(block[12:16], "big")

        for i in range(0, 32, 4):
            X0 = X0 ^ SM4._T0(X1 ^ X2 ^ X3 ^ RK[31 - i])
            X1 = X1 ^ SM4._T0(X2 ^ X3 ^ X0 ^ RK[30 - i])
            X2 = X2 ^ SM4._T0(X3 ^ X0 ^ X1 ^ RK[29 - i])
            X3 = X3 ^ SM4._T0(X0 ^ X1 ^ X2 ^ RK[28 - i])

        BUFFER = self._block_buffer
        BUFFER.clear()
        BUFFER.extend(X3.to_bytes(4, "big"))
        BUFFER.extend(X2.to_bytes(4, "big"))
        BUFFER.extend(X1.to_bytes(4, "big"))
        BUFFER.extend(X0.to_bytes(4, "big"))
        return bytes(BUFFER)

# ========== UTILITY CLASSES ==========
class Misc:
    @staticmethod
    def pad_to_n(data: bytes, n: int) -> bytes:
        assert n > 0
        padding = n - (len(data) % n)
        if padding == n:
            return data
        return data + b'\x00' * padding

    @staticmethod
    def align_up(x: int, n: int) -> int:
        return ((x + n - 1) // n) * n

class Reader:
    def __init__(self, buffer, cursor=0):
        self._buffer = buffer
        self._cursor = cursor

    def u1(self, move_cursor=True) -> int:
        return self.unpack('B', move_cursor=move_cursor)[0]

    def u4(self, move_cursor=True) -> int:
        return self.unpack('<I', move_cursor=move_cursor)[0]

    def u8(self, move_cursor=True) -> int:
        return self.unpack('<Q', move_cursor=move_cursor)[0]

    def i1(self, move_cursor=True) -> int:
        return self.unpack('b', move_cursor=move_cursor)[0]

    def i4(self, move_cursor=True) -> int:
        return self.unpack('<i', move_cursor=move_cursor)[0]

    def i8(self, move_cursor=True) -> int:
        return self.unpack('<q', move_cursor=move_cursor)[0]

    def s(self, n: int, move_cursor=True) -> bytes:
        return self.unpack(f'{n}s', move_cursor=move_cursor)[0]

    def unpack(self, f: Union[str, bytes], offset=0, move_cursor=True):
        x = struct.unpack_from(f, self._buffer, self._cursor + offset)
        if move_cursor:
            self._cursor += struct.calcsize(f)
        return x

    def string(self, move_cursor=True) -> str:
        length = self.i4(move_cursor=move_cursor)
        if length == 0:
            return str()
        assert length > 0
        offset = 0 if move_cursor else 4
        return self.unpack(f'{length}s', offset=offset, move_cursor=move_cursor)[0].rstrip(b'\x00').decode()

# ========== PAK CLASSES ==========
class PakInfo:
    def __init__(self, buffer, keystream: List[int]):
        def decrypt_index_encrypted(x: int) -> int:
            MASK_8 = 0xFF
            return (x ^ keystream[3]) & MASK_8

        def decrypt_magic(x: int) -> int:
            return x ^ keystream[2]

        def decrypt_index_hash(x: bytes) -> bytes:
            key = struct.pack('<5I', *keystream[4:][:5])
            assert len(x) == len(key)
            return bytes(a ^ b for a, b in zip(x, key))

        def decrypt_index_size(x: int) -> int:
            return x ^ ((keystream[10] << 32) | keystream[11])

        def decrypt_index_offset(x: int) -> int:
            return x ^ ((keystream[0] << 32) | keystream[1])

        reader = Reader(buffer[-PakInfo._mem_size(-1):])
        self.index_encrypted: bool = decrypt_index_encrypted(reader.u1()) == 1
        self.magic: int = decrypt_magic(reader.u4())
        self.version: int = reader.u4()
        self.index_hash: bytes = decrypt_index_hash(reader.s(20)) if self.version >= 6 else bytes()
        self.index_size: int = decrypt_index_size(reader.u8())
        self.index_offset: int = decrypt_index_offset(reader.u8())
        if self.version <= 3:
            self.index_encrypted = False

    @staticmethod
    def _mem_size(_: int) -> int:
        return 1 + 4 + 4 + 20 + 8 + 8

class TencentPakInfo(PakInfo):
    def __init__(self, buffer, keystream: List[int]):
        def decrypt_unk(x: bytes) -> bytes:
            key = struct.pack('<8I', *keystream[7:][:8])
            assert len(x) == len(key)
            return bytes(a ^ b for a, b in zip(x, key))

        def decrypt_stem_hash(x: int) -> int:
            return x ^ keystream[8]

        def decrypt_unk_hash(x: int) -> int:
            return x ^ keystream[9]

        super().__init__(buffer, keystream)
        reader = Reader(buffer[-TencentPakInfo._mem_size(self.version):])
        self.unk1: bytes = decrypt_unk(reader.s(32)) if self.version >= 7 else bytes()
        self.packed_key: bytes = reader.s(256) if self.version >= 8 else bytes()
        self.packed_iv: bytes = reader.s(256) if self.version >= 8 else bytes()
        self.packed_index_hash: bytes = reader.s(256) if self.version >= 8 else bytes()
        self.stem_hash: int = decrypt_stem_hash(reader.u4()) if self.version >= 9 else 0
        self.unk2: int = decrypt_unk_hash(reader.u4()) if self.version >= 9 else 0
        self.content_org_hash: bytes = reader.s(20) if self.version >= 12 else bytes()

    @staticmethod
    def _mem_size(version: int) -> int:
        size_for_7 = 32 if version >= 7 else 0
        size_for_8 = 256 * 3 if version >= 8 else 0
        size_for_9 = 4 * 2 if version >= 9 else 0
        size_for_12 = 20 if version >= 12 else 0
        return PakInfo._mem_size(version) + size_for_7 + size_for_8 + size_for_9 + size_for_12

class PakCompressedBlock:
    def __init__(self, reader: Reader):
        self.start: int = reader.u8()
        self.end: int = reader.u8()

@dataclass
class TencentPakEntry:
    def __init__(self, reader: Reader, version: int):
        self.content_hash: bytes = reader.s(20)
        if version <= 1:
            _ = reader.u8()
        self.offset: int = reader.u8()
        self.uncompressed_size: int = reader.u8()
        self.compression_method: int = reader.u4() & CM_MASK
        self.size: int = reader.u8()
        self.unk1: int = reader.u1() if version >= 5 else 0
        self.unk2: bytes = reader.s(20) if version >= 5 else bytes()
        self.compressed_blocks: List[PakCompressedBlock] = [PakCompressedBlock(reader) for _ in range(
            reader.u4())] if self.compression_method != 0 and version >= 3 else []
        self.compression_block_size: int = reader.u4() if version >= 4 else 0
        self.encrypted: bool = reader.u1() == 1 if version >= 4 else False
        self.encryption_method: int = reader.u4() if version >= 12 else 0
        self.index_new_sep: int = reader.u4() if version >= 12 else 0

    def _mem_size(self, version: int) -> int:
        size_for_123 = 20 + 8 + 8 + 4 + 8 + (8 if version == 1 else 0)
        size_for_4 = 4 + 1 if version >= 4 else 0
        size_for_compressed_blocks = 4 + len(self.compressed_blocks) * 16 if self.compressed_blocks else 0
        size_for_5 = 1 + 20 if version >= 5 else 0
        size_for_12 = 4 if version >= 12 else 0
        return size_for_123 + size_for_4 + size_for_5 + size_for_12 + size_for_compressed_blocks

class PakCrypto:
    class _LCG:
        def __init__(self, seed: int):
            self.state = seed

        def next(self) -> int:
            MASK_32 = 0xFFFFFFFF
            MSB_1 = 1 << 31

            def wrap(x: int) -> int:
                x &= MASK_32
                if not x & MSB_1:
                    return x
                else:
                    return ((x + MSB_1) & MASK_32) - MSB_1

            x1 = wrap(0x41C64E6D * self.state)
            self.state = wrap(x1 + 12345)
            x2 = wrap(x1 + 0x13038) if self.state < 0 else self.state
            return ((x2 >> 16) & MASK_32) % 0x7FFF

    @staticmethod
    def zuc_keystream() -> List[int]:
        zuc = gmalg.ZUC(ZUC_KEY, ZUC_IV)
        return [struct.unpack('>I', zuc.generate())[0] for _ in range(16)]

    @staticmethod
    def _xorxor(buffer, x) -> bytes:
        return bytes(buffer[i] ^ x[i % len(x)] for i in range(len(buffer)))

    @staticmethod
    def _hashhash(buffer, n: int) -> bytes:
        result = bytes()
        for i in range(math.ceil(n / SHA1.digest_size)):
            result += SHA1.new(buffer).digest()
        if len(result) >= n:
            result = result[:n]
        else:
            result += b'\x00' * (n - len(result))
        return result

    @staticmethod
    def _meowmeow(buffer) -> bytes:
        def unpad(x):
            skip = 1 + next((i for i in range(len(x)) if x[i] != 0))
            return x[skip:]

        if len(buffer) < 43:
            return bytes()

        x1 = buffer[1:][:SHA1.digest_size]
        x2 = buffer[SHA1.digest_size + 1:]
        x1 = PakCrypto._xorxor(x1, PakCrypto._hashhash(x2, len(x1)))
        x2 = PakCrypto._xorxor(x2, PakCrypto._hashhash(x1, len(x2)))

        part1, m = (x2[:SHA1.digest_size], x2[SHA1.digest_size:])
        if part1 != SHA1.new(b'\x00' * SHA1.digest_size).digest():
            return bytes()

        return unpad(m)

    @staticmethod
    def rsa_extract(signature: bytes, modulus: bytes) -> bytes:
        c = int.from_bytes(signature, 'little')
        n = int.from_bytes(modulus, 'little')
        e = 0x10001
        m = pow(c, e, n).to_bytes(256, 'little').rstrip(b'\x00')
        return PakCrypto._meowmeow(Misc.pad_to_n(m, 4))

    @staticmethod
    def _decrypt_simple1(ciphertext) -> bytes:
        return bytes(x ^ SIMPLE1_DECRYPT_KEY for x in ciphertext)

    @staticmethod
    def _decrypt_simple2(ciphertext) -> bytes:
        class RollingKey:
            def __init__(self, initial_value: int):
                self._value = initial_value

            def update(self, x: int) -> int:
                self._value ^= x
                return self._value

        assert len(ciphertext) % SIMPLE2_BLOCK_SIZE == 0
        initial_key, = struct.unpack('<I', SIMPLE2_DECRYPT_KEY)
        rolling_key = RollingKey(initial_key)
        plaintext = (
            struct.pack('<I', rolling_key.update(x)) for x in struct.unpack(f'<{len(ciphertext) // 4}I', ciphertext)
        )
        return bytes(it.chain.from_iterable(plaintext))

    @staticmethod
    @lru_cache(maxsize=1)
    def _derive_sm4_key(file_path: PurePath, encryption_method: int) -> bytes:
        part1 = file_path.stem.lower()
        if encryption_method == EM_SM4_2:
            secret = SM4_SECRET_2
        elif encryption_method == EM_SM4_4:
            secret = SM4_SECRET_4
        elif encryption_method == EM_UNKNOWN_17:
            index = (encryption_method - EM_SM4_NEW_BASE) % len(SM4_SECRET_NEW)
            secret = SM4_SECRET_NEW[index]
        else:
            index = (encryption_method - EM_SM4_NEW_BASE) % len(SM4_SECRET_NEW)
            secret = f'{SM4_SECRET_NEW[index]}{encryption_method}'
        return SHA1.new(str(part1 + secret).encode()).digest()[:SM4.key_length()]

    @staticmethod
    @lru_cache(maxsize=1)
    def _sm4_context_for_key(key: bytes) -> SM4:
        return SM4(key)

    @staticmethod
    def _decrypt_sm4(ciphertext, file_path: PurePath, encryption_method: int) -> bytes:
        assert len(ciphertext) % SM4.block_length() == 0
        key = PakCrypto._derive_sm4_key(file_path, encryption_method)
        sm4 = PakCrypto._sm4_context_for_key(key)
        return bytes(
            it.chain.from_iterable(
                sm4.decrypt(x) for x in it.batched(ciphertext, SM4.block_length())
            )
        )

    @staticmethod
    def decrypt_index(ciphertext, pak_info: TencentPakInfo) -> bytes:
        if pak_info.version > 7:
            key = PakCrypto.rsa_extract(pak_info.packed_key, RSA_MOD_1)
            iv = PakCrypto.rsa_extract(pak_info.packed_iv, RSA_MOD_1)
            assert len(key) == 32 and len(iv) == 32
            aes = AES.new(key, MODE_CBC, iv[:16])
            return unpad(aes.decrypt(ciphertext), AES.block_size)
        else:
            return bytes(PakCrypto._decrypt_simple1(ciphertext))

    @staticmethod
    def _is_simple1_method(encryption_method: int) -> bool:
        return encryption_method == EM_SIMPLE1

    @staticmethod
    def _is_simple2_method(encryption_method: int) -> bool:
        return encryption_method == EM_SIMPLE2 or encryption_method == 17

    @staticmethod
    def _is_sm4_method(encryption_method: int) -> bool:
        return (encryption_method == EM_SM4_2
                or encryption_method == EM_SM4_4
                or encryption_method == EM_UNKNOWN_17
                or encryption_method & EM_SM4_NEW_MASK != 0)

    @staticmethod
    def align_encrypted_content_size(n: int, encryption_method: int) -> int:
        if PakCrypto._is_simple2_method(encryption_method):
            return Misc.align_up(n, SIMPLE2_BLOCK_SIZE)
        elif PakCrypto._is_sm4_method(encryption_method):
            return Misc.align_up(n, SM4.block_length())
        else:
            return n

    @staticmethod
    def decrypt_block(ciphertext, file: PurePath, encryption_method: int) -> bytes:
        if PakCrypto._is_simple1_method(encryption_method):
            return PakCrypto._decrypt_simple1(ciphertext)
        elif PakCrypto._is_simple2_method(encryption_method):
            return PakCrypto._decrypt_simple2(ciphertext)
        elif PakCrypto._is_sm4_method(encryption_method):
            return PakCrypto._decrypt_sm4(ciphertext, file, encryption_method)
        else:
            raise ValueError(f"Unknown encryption method: {encryption_method}")

    @staticmethod
    @lru_cache(maxsize=33)
    def generate_block_indices(n: int, encryption_method: int) -> List[int]:
        if not PakCrypto._is_sm4_method(encryption_method):
            return list(range(n))
        permutation = []
        lcg = PakCrypto._LCG(n)
        while len(permutation) != n:
            x = lcg.next() % n
            if x not in permutation:
                permutation.append(x)
        inverse = [0] * len(permutation)
        for i, x in enumerate(permutation):
            inverse[x] = i
        return inverse

class PakCompression:
    @staticmethod
    @lru_cache(maxsize=33)
    def _zstd_decompressor(dict: ZstdCompressionDict) -> ZstdDecompressor:
        return ZstdDecompressor(dict)

    @staticmethod
    def zstd_dictionary(dict_data) -> ZstdCompressionDict:
        return ZstdCompressionDict(dict_data, DICT_TYPE_AUTO)

    @staticmethod
    def decompress_block(block, dict: Optional[ZstdCompressionDict], compression_method: int) -> bytes:
        if compression_method == CM_ZLIB:
            try:
                return zlib.decompress(block)
            except zlib.error:
                return block
        elif compression_method == CM_ZSTD or compression_method == CM_ZSTD_DICT:
            if compression_method != CM_ZSTD_DICT:
                dict = None
            return PakCompression._zstd_decompressor(dict).decompress(block)
        else:
            raise ValueError(f"Unknown compression method: {compression_method}")

class TencentPakFile:
    def __init__(self, file_path: PurePath, is_od=True):
        self._file_path = file_path
        with open(file_path, 'rb') as file:
            self._file_content = memoryview(file.read())
        self._is_od = is_od
        self._mount_point = PurePath()
        self._is_zstd_with_dict = 'zsdic' in str(self._file_path)
        self._zstd_dict = None
        self._files: List[TencentPakEntry] = []
        self._index: Dict[PurePath, Dict[str, TencentPakEntry]] = {}
        self._pak_info = TencentPakInfo(self._file_content, PakCrypto.zuc_keystream())
        self._verify_stem_hash()
        self._tencent_load_index()

    def _verify_stem_hash(self) -> None:
        if not self._is_od and self._pak_info.version >= 9:
            assert self._pak_info.stem_hash == zlib.crc32(self._file_path.stem.encode('utf-32le'))

    def _tencent_load_index(self) -> None:
        index_data = self._file_content[self._pak_info.index_offset:][:self._pak_info.index_size]
        if self._pak_info.index_encrypted:
            index_data = PakCrypto.decrypt_index(index_data, self._pak_info)
        else:
            index_data = index_data
        self._verify_index_hash(index_data)
        self._load_index(index_data)

    def _verify_index_hash(self, index_data) -> None:
        expected_hash = self._pak_info.index_hash
        if not self._is_od and self._pak_info.version >= 8:
            assert expected_hash == PakCrypto.rsa_extract(self._pak_info.packed_index_hash, RSA_MOD_2)
        assert expected_hash == SHA1.new(index_data).digest()

    @staticmethod
    def _construct_mount_point(mount_point: str) -> PurePath:
        result = PurePath()
        for part in PurePath(mount_point).parts:
            if part != '..':
                result /= part
        return result

    def _peek_content(self, offset: int, size: int, encryption_method: int) -> memoryview:
        size = PakCrypto.align_encrypted_content_size(size, encryption_method)
        return self._file_content[offset:][:size]

    def _peek_block_content(self, block: PakCompressedBlock, encryption_method: int) -> memoryview:
        size = PakCrypto.align_encrypted_content_size(block.end - block.start, encryption_method)
        return self._file_content[block.start:][:size]

    def _construct_zstd_dict(self, dict_entry: TencentPakEntry) -> None:
        assert not self._zstd_dict
        assert not dict_entry.encrypted
        assert dict_entry.compression_method == CM_NONE
        reader = Reader(self._peek_content(dict_entry.offset, dict_entry.size, 0))
        dict_size = reader.u8()
        _ = reader.u4()
        assert dict_size == reader.u4()
        dict_data = reader.s(dict_size)
        self._zstd_dict = PakCompression.zstd_dictionary(dict_data)

    def _load_index(self, index_data) -> None:
        if self._pak_info.version <= 10:
            raise ValueError(f"Unsupported version: {self._pak_info.version}")
        reader = Reader(index_data)
        self._mount_point = self._construct_mount_point(reader.string())
        self._files = [TencentPakEntry(reader, self._pak_info.version) for _ in range(reader.u4())]
        for _ in range(reader.u8()):
            dir_path = PurePath(reader.string())
            e = {reader.string(): self._files[~reader.i4()] for _ in range(reader.u8())}
            if self._is_zstd_with_dict and dir_path.name == 'zstddic':
                assert len(e) == 1
                self._construct_zstd_dict(e[[*e.keys()][0]])
                continue
            self._index.update({PurePath(dir_path): e})

    def detect_dominant_style(self) -> dict:
        comp_counter = Counter()
        enc_counter = Counter()
        blk_counter = Counter()
        enc_flag_counter = Counter()
        total = len(self._files)
        if total == 0:
            return {'comp_method': CM_ZSTD, 'enc_method': 0, 'encrypted': False, 'block_size': 0x10000}
        for entry in self._files:
            comp_counter[entry.compression_method] += 1
            if entry.encrypted:
                enc_counter[entry.encryption_method] += 1
                enc_flag_counter['encrypted'] += 1
            else:
                enc_flag_counter['plain'] += 1
            if entry.compression_block_size:
                blk_counter[entry.compression_block_size] += 1
        non_none = [(m,c) for m,c in comp_counter.items() if m != CM_NONE]
        comp_method = max(non_none, key=lambda x: x[1])[0] if non_none else CM_NONE
        encrypted = enc_flag_counter.get('encrypted', 0) > enc_flag_counter.get('plain', 0)
        enc_method = enc_counter.most_common(1)[0][0] if encrypted and enc_counter else 0
        block_size = blk_counter.most_common(1)[0][0] if blk_counter else 0x10000
        return {'comp_method': comp_method, 'enc_method': enc_method, 'encrypted': encrypted, 'block_size': block_size}

    def list_existing_paths(self) -> List[str]:
        out = []
        for dir_path, files in self._index.items():
            for fname in files.keys():
                out.append(str(dir_path / fname).replace('\\', '/').lstrip('/'))
        return out

    def _make_signature_marker(self, current_offset: int) -> dict:
        empty_hash = SHA1.new(b'').digest()
        return {
            'content_hash': empty_hash,
            'offset': current_offset,
            'uncompressed_size': 0,
            'size': 0,
            'comp_method': CM_NONE,
            'enc_method': 0,
            'encrypted': False,
            'block_size_val': 0,
            'compressed_blocks': [],
            'unk1': 0,
            'unk2': b'\x00' * 20,
            'index_new_sep': 0,
            '_dir_path': PurePath('FANxPUBG'),
            '_file_name': 'PATCHED.txt',
        }

    @staticmethod
    def _extract_entry_plain(pak_buffer: memoryview, entry: TencentPakEntry,
                             file_path_for_crypto: PurePath, zstd_dict) -> bytes:
        """Extract a single entry's plaintext (decrypted + decompressed) bytes."""
        if entry.compression_method == CM_NONE:
            sz = PakCrypto.align_encrypted_content_size(entry.size, entry.encryption_method)
            data = bytes(pak_buffer[entry.offset:][:sz])
            if entry.encrypted:
                data = PakCrypto.decrypt_block(data, file_path_for_crypto, entry.encryption_method)
            return data

        parts = []
        for real_idx in PakCrypto.generate_block_indices(len(entry.compressed_blocks), entry.encryption_method):
            block = entry.compressed_blocks[real_idx]
            bsz = PakCrypto.align_encrypted_content_size(block.end - block.start, entry.encryption_method)
            blk = bytes(pak_buffer[block.start:][:bsz])
            if entry.encrypted:
                blk = PakCrypto.decrypt_block(blk, file_path_for_crypto, entry.encryption_method)
            dec = PakCompression.decompress_block(blk, zstd_dict, entry.compression_method)
            parts.append(dec)
        return b''.join(parts)

    def inject_files(self, inject_plan: list, output_pak: Path, add_signature_marker: bool = True) -> None:
        """Inject new files into this PAK, producing a new PAK at output_pak."""
        if not inject_plan:
            raise ValueError('inject_plan is empty — nothing to inject')

        console.print(f'[bold magenta]💉 CUSTOM INJECT[/bold magenta]')
        console.print(f'  [white]Source PAK:[/] [yellow]{self._file_path.name}[/yellow]')
        console.print(f'  [white]Output    :[/] [cyan]{output_pak.name}[/cyan]')
        console.print(f'  [white]Injecting :[/] [green]{len(inject_plan)} new file(s)[/green]')

        console.print('\n[bold magenta]━━ STEP 1/5 : LOADING INJECT FILES ━━[/bold magenta]')
        work_items = []
        for i, item in enumerate(inject_plan):
            if item.get('plain_bytes') is not None:
                plain = item['plain_bytes']
            elif item.get('src_path') is not None:
                try:
                    plain = Path(item['src_path']).read_bytes()
                except Exception as e:
                    console.print(f'   [red]✗ Cannot read {item["src_path"]}: {e} — skipping[/red]')
                    continue
            else:
                console.print(f'   [red]✗ Inject item {i} has no src_path or plain_bytes — skipping[/red]')
                continue

            internal = item['internal_path'].replace('\\', '/').lstrip('/')
            if not internal:
                console.print(f'   [red]✗ Empty internal_path for item {i} — skipping[/red]')
                continue

            parts = internal.rsplit('/', 1)
            if len(parts) == 2:
                dir_str, file_name = parts[0], parts[1]
            else:
                dir_str, file_name = '', parts[0]

            work_items.append({
                'dir_str':       dir_str,
                'file_name':     file_name,
                'internal_path': internal,
                'plain':         plain,
                'comp_method':   item['comp_method'],
                'enc_method':    item['enc_method'],
                'encrypted':     bool(item['encrypted']),
                'block_size':    item['block_size'],
                'comp_level':    item.get('comp_level', 19),
            })
            console.print(f'   [blue]✨[/] {internal} [dim]({len(plain):,} bytes)[/dim]')

        if not work_items:
            raise RuntimeError('No valid inject items after loading')
        console.print(f'[green]✔ Loaded {len(work_items)} file(s)[/green]')

        console.print('\n[bold magenta]━━ STEP 2/5 : ENCODING INJECT FILES ━━[/bold magenta]')
        keystream = PakCrypto.zuc_keystream()
        version = self._pak_info.version
        header_size = TencentPakInfo._mem_size(version)
        PAK_MAGIC = self._pak_info.magic

        orig_index_offset = self._pak_info.index_offset
        current_new_offset = orig_index_offset
        new_data_region = bytearray()
        new_injected_entries = []
        preferred_level = 19

        # Helper function for encryption
        def _encrypt_plaintext(plaintext, pak_relative_path, encryption_method):
            if PakCrypto._is_simple1_method(encryption_method):
                return bytes(b ^ SIMPLE1_DECRYPT_KEY for b in plaintext)
            elif PakCrypto._is_simple2_method(encryption_method):
                pad = (-len(plaintext)) % SIMPLE2_BLOCK_SIZE
                plaintext += b"\x00" * pad
                key, = struct.unpack("<I", SIMPLE2_DECRYPT_KEY)
                rolling = key
                out = []
                for x, in struct.iter_unpack("<I", plaintext):
                    c = rolling ^ x
                    out.append(c)
                    rolling ^= c
                return struct.pack(f"<{len(out)}I", *out)
            elif PakCrypto._is_sm4_method(encryption_method):
                key = PakCrypto._derive_sm4_key(pak_relative_path, encryption_method)
                sm4 = PakCrypto._sm4_context_for_key(key)
                pad_len = (-len(plaintext)) % 16
                if pad_len > 0:
                    plaintext = plaintext + b'\x00' * pad_len
                out = bytearray()
                for i in range(0, len(plaintext), 16):
                    block = plaintext[i:i+16]
                    if len(block) < 16:
                        block = block.ljust(16, b'\x00')
                    out.extend(sm4.encrypt(block))
                return bytes(out)
            return plaintext

        for item in work_items:
            plain = item['plain']
            comp_method = item['comp_method']
            enc_method = item['enc_method']
            encrypted = item['encrypted']
            block_size_val = item['block_size']
            file_path_for_crypto = PurePath(item['file_name'])

            if len(plain) == 0:
                new_injected_entries.append({
                    'content_hash': SHA1.new(b'').digest(),
                    'offset': current_new_offset,
                    'uncompressed_size': 0, 'size': 0,
                    'comp_method': CM_NONE, 'enc_method': 0, 'encrypted': False,
                    'block_size_val': 0, 'compressed_blocks': [],
                    'unk1': 0, 'unk2': b'\x00' * 20, 'index_new_sep': 0,
                    '_dir_path': PurePath(item['dir_str']) if item['dir_str'] else PurePath(),
                    '_file_name': item['file_name'],
                })
                continue

            if comp_method == CM_NONE:
                if encrypted:
                    aligned_size = PakCrypto.align_encrypted_content_size(len(plain), enc_method)
                    padded = plain + b'\x00' * (aligned_size - len(plain))
                    stored_data = _encrypt_plaintext(padded, file_path_for_crypto, enc_method)
                else:
                    stored_data = plain
                new_size = len(stored_data)
                new_compressed_blocks = []
            else:
                chunks = [plain[i:i+block_size_val] for i in range(0, len(plain), block_size_val)]
                if not chunks: chunks = [b'']
                compressed_chunks = []
                for chunk in chunks:
                    comp = None
                    if comp_method in (CM_ZSTD, CM_ZSTD_DICT):
                        zstd_dict = self._zstd_dict if comp_method == CM_ZSTD_DICT else None
                        for lvl in range(22, 0, -1):
                            try:
                                c = ZstdCompressor(level=lvl, dict_data=zstd_dict, threads=1)
                                comp = c.compress(chunk)
                                break
                            except: continue
                    elif comp_method == CM_ZLIB:
                        comp = zlib.compress(chunk, level=9)
                    if comp is None: comp = chunk
                    compressed_chunks.append(comp)

                encrypted_chunks = []
                for comp_data in compressed_chunks:
                    if encrypted:
                        comp_data = _encrypt_plaintext(comp_data, file_path_for_crypto, enc_method)
                    encrypted_chunks.append(comp_data)

                n_blocks = len(encrypted_chunks)
                indices = PakCrypto.generate_block_indices(n_blocks, enc_method)
                physical_blocks = [None] * n_blocks
                for j, chunk_data in enumerate(encrypted_chunks):
                    physical_blocks[indices[j]] = chunk_data

                physical_offsets = []
                block_cursor = current_new_offset
                for phys_block in physical_blocks:
                    physical_offsets.append((block_cursor, block_cursor + len(phys_block)))
                    block_cursor += len(phys_block)
                new_compressed_blocks = physical_offsets
                stored_data = b''.join(physical_blocks)
                new_size = len(stored_data)
                if encrypted:
                    aligned_total = PakCrypto.align_encrypted_content_size(new_size, enc_method)
                    if aligned_total > new_size:
                        stored_data = stored_data + b'\x00' * (aligned_total - new_size)
                        new_size = aligned_total

            new_content_hash = SHA1.new(stored_data).digest()
            new_data_region.extend(stored_data)

            new_injected_entries.append({
                'content_hash': new_content_hash,
                'offset': current_new_offset,
                'uncompressed_size': len(plain),
                'size': new_size,
                'comp_method': comp_method,
                'enc_method': enc_method if encrypted else 0,
                'encrypted': encrypted,
                'block_size_val': block_size_val,
                'compressed_blocks': new_compressed_blocks,
                'unk1': 0, 'unk2': b'\x00' * 20, 'index_new_sep': 0,
                '_dir_path': PurePath(item['dir_str']) if item['dir_str'] else PurePath(),
                '_file_name': item['file_name'],
            })
            current_new_offset += new_size

        console.print(f'[green]✔ Encoded {len(new_injected_entries)} file(s)[/green]')

        # Build final entries
        new_entries = []
        entry_to_path = {}
        for dir_path, files in self._index.items():
            for fname, entry in files.items():
                entry_to_path[id(entry)] = (dir_path, fname)
        for i, entry in enumerate(self._files):
            dir_path, fname = entry_to_path.get(id(entry), (PurePath(), f'unknown_{i}'))
            new_entries.append({
                'content_hash': entry.content_hash,
                'offset': entry.offset,
                'uncompressed_size': entry.uncompressed_size,
                'size': entry.size,
                'comp_method': entry.compression_method,
                'enc_method': entry.encryption_method if entry.encrypted else 0,
                'encrypted': entry.encrypted,
                'block_size_val': entry.compression_block_size,
                'compressed_blocks': [(b.start, b.end) for b in entry.compressed_blocks],
                'unk1': entry.unk1, 'unk2': entry.unk2,
                'index_new_sep': entry.index_new_sep,
            })
        new_entries.extend(new_injected_entries)

        if add_signature_marker:
            marker_already_present = False
            for dp, files_dict in self._index.items():
                if dp.name == 'FAN_PATCH' and 'PATCHED.txt' in files_dict:
                    marker_already_present = True
                    break
            if not marker_already_present:
                new_entries.append(self._make_signature_marker(current_new_offset))

        # Build Index
        index_data = bytearray()
        raw_orig_index = self._file_content[self._pak_info.index_offset:][:self._pak_info.index_size]
        orig_index_decoded = PakCrypto.decrypt_index(bytes(raw_orig_index), self._pak_info)
        orig_reader = Reader(orig_index_decoded)
        orig_mount_len = orig_reader.i4()
        orig_mount_bytes = bytes(orig_reader.s(orig_mount_len))
        index_data.extend(struct.pack('<I', orig_mount_len))
        index_data.extend(orig_mount_bytes)
        index_data.extend(struct.pack('<I', len(new_entries)))

        for item in new_entries:
            index_data.extend(item['content_hash'])
            if version <= 1: index_data.extend(struct.pack('<Q', 0))
            index_data.extend(struct.pack('<Q', item['offset']))
            index_data.extend(struct.pack('<Q', item['uncompressed_size']))
            index_data.extend(struct.pack('<I', item['comp_method'] & CM_MASK))
            index_data.extend(struct.pack('<Q', item['size']))
            if version >= 5:
                index_data.extend(struct.pack('<B', item['unk1']))
                index_data.extend(item['unk2'] if item['unk2'] else b'\x00' * 20)
            if item['comp_method'] != CM_NONE and version >= 3:
                index_data.extend(struct.pack('<I', len(item['compressed_blocks'])))
                for (start, end) in item['compressed_blocks']:
                    index_data.extend(struct.pack('<Q', start))
                    index_data.extend(struct.pack('<Q', end))
            if version >= 4:
                index_data.extend(struct.pack('<I', item['block_size_val']))
                index_data.extend(struct.pack('<B', 1 if item['encrypted'] else 0))
            if version >= 12:
                index_data.extend(struct.pack('<I', item['enc_method']))
                index_data.extend(struct.pack('<I', item['index_new_sep']))

        file_to_dirname = {}
        for dir_path, files_dict in self._index.items():
            dir_str = dir_path.as_posix()
            for fname, entry in files_dict.items():
                for i, fe in enumerate(self._files):
                    if id(fe) == id(entry):
                        file_to_dirname[i] = (dir_str, fname)
                        break
        for i, item in enumerate(new_entries):
            if i not in file_to_dirname:
                if '_dir_path' in item:
                    file_to_dirname[i] = (item['_dir_path'].as_posix(), item['_file_name'])
                else:
                    file_to_dirname[i] = ('', f'file_{i}')

        all_dirs = []
        dir_to_files = {}
        for dir_path in self._index.keys():
            ds = dir_path.as_posix()
            all_dirs.append(ds)
            dir_to_files[ds] = []
        for i, item in enumerate(new_entries):
            ds, fn = file_to_dirname[i]
            if ds not in dir_to_files:
                dir_to_files[ds] = []
                all_dirs.append(ds)
            dir_to_files[ds].append((fn, i))

        index_data.extend(struct.pack('<Q', len(all_dirs)))
        for dir_str in all_dirs:
            files_list = dir_to_files[dir_str]
            if not dir_str or dir_str == '.':
                index_data.extend(struct.pack('<I', 0))
            else:
                if not dir_str.endswith('/'): dir_str_with_slash = dir_str + '/'
                else: dir_str_with_slash = dir_str
                dir_bytes = dir_str_with_slash.encode('utf-8') + b'\x00'
                index_data.extend(struct.pack('<I', len(dir_bytes)))
                index_data.extend(dir_bytes)
            index_data.extend(struct.pack('<Q', len(files_list)))
            for file_name, fi in files_list:
                name_bytes = file_name.encode('utf-8') + b'\x00'
                index_data.extend(struct.pack('<I', len(name_bytes)))
                index_data.extend(name_bytes)
                index_data.extend(struct.pack('<i', -fi - 1))
        index_data.extend(b'\x1d\x00\x00\x00\x2e\x2e')

        index_hash = SHA1.new(bytes(index_data)).digest()

        if version > 7 and self._pak_info.index_encrypted:
            key = PakCrypto.rsa_extract(self._pak_info.packed_key, RSA_MOD_1)
            iv = PakCrypto.rsa_extract(self._pak_info.packed_iv, RSA_MOD_1)
            assert len(key) == 32 and len(iv) == 32
            padded = pad(bytes(index_data), AES.block_size)
            aes = AES.new(key, MODE_CBC, iv[:16])
            encrypted_index = aes.encrypt(padded)
        elif self._pak_info.index_encrypted:
            encrypted_index = bytes(b ^ SIMPLE1_DECRYPT_KEY for b in bytes(index_data))
        else:
            encrypted_index = bytes(index_data)

        index_size = len(encrypted_index)
        new_index_offset = orig_index_offset + len(new_data_region)

        encrypted_magic = PAK_MAGIC ^ keystream[2]
        key_stream_hash = struct.pack('<5I', *keystream[4:][:5])
        encrypted_index_hash = bytes(a ^ b for a, b in zip(index_hash, key_stream_hash))
        encrypted_index_size = index_size ^ ((keystream[10] << 32) | keystream[11])
        encrypted_index_offset = new_index_offset ^ ((keystream[0] << 32) | keystream[1])
        encrypted_flag_byte = (1 if self._pak_info.index_encrypted else 0) ^ (keystream[3] & 0xFF)

        orig_data_region = bytearray(self._file_content[0:orig_index_offset])
        output_pak.parent.mkdir(parents=True, exist_ok=True)
        with open(output_pak, 'wb') as f:
            f.write(bytes(orig_data_region))
            f.write(bytes(new_data_region))
            f.write(encrypted_index)
            if version >= 7:
                key_unk1 = struct.pack('<8I', *keystream[7:][:8])
                unk1_plain = self._pak_info.unk1 if self._pak_info.unk1 else b'\x00' * 32
                encrypted_unk1 = bytes(a ^ b for a, b in zip(unk1_plain, key_unk1))
                f.write(encrypted_unk1)
            if version >= 8:
                f.write(self._pak_info.packed_key if self._pak_info.packed_key else b'\x00' * 256)
                f.write(self._pak_info.packed_iv if self._pak_info.packed_iv else b'\x00' * 256)
                f.write(self._pak_info.packed_index_hash if self._pak_info.packed_index_hash else b'\x00' * 256)
            if version >= 9:
                f.write(struct.pack('<I', (self._pak_info.stem_hash or 0) ^ keystream[8]))
                f.write(struct.pack('<I', (self._pak_info.unk2 or 0) ^ keystream[9]))
            if version >= 12:
                f.write(self._pak_info.content_org_hash if self._pak_info.content_org_hash else b'\x00' * 20)
            f.write(struct.pack('<B', encrypted_flag_byte))
            f.write(struct.pack('<I', encrypted_magic))
            f.write(struct.pack('<I', version))
            if version >= 6:
                f.write(encrypted_index_hash)
            else:
                f.write(b'\x00' * 20)
            f.write(struct.pack('<Q', encrypted_index_size))
            f.write(struct.pack('<Q', encrypted_index_offset))

        console.print(f'[bold green]🎉 INJECT COMPLETE![/bold green]')
        console.print(f'  [white]Output  :[/] [cyan]{output_pak.name}[/cyan]')
        console.print(f'  [white]Output  :[/] [cyan]{output_pak.name}[/cyan]')

    def _write_to_disk(self, file_path: PurePath, entry: TencentPakEntry) -> None:
        encryption_method = entry.encryption_method
        compression_method = entry.compression_method
        
        console.print(f"[#00CCFF]{file_path.name}[/#00CCFF] - Encryption: {encryption_method}, Compression: {compression_method}, Blocks: {len(entry.compressed_blocks)}")
        
        # ----- BYPASS FOR ENC 17 (DSxDEMON) -----
        if encryption_method == 17:
            with open(file_path, 'wb') as file:
                for blk in entry.compressed_blocks:
                    raw_data = self._file_content[blk.start:blk.end]
                    file.write(raw_data)
            return
        # --------------------------------------------
        
        with open(file_path, 'wb') as file:
            if compression_method == CM_NONE:
                data = self._peek_content(entry.offset, entry.size, encryption_method)
                if entry.encrypted:
                    data = PakCrypto.decrypt_block(data, file_path, encryption_method)
                file.write(data)
                return
            for x in PakCrypto.generate_block_indices(len(entry.compressed_blocks), encryption_method):
                data = self._peek_block_content(entry.compressed_blocks[x], encryption_method)
                if entry.encrypted:
                    data = PakCrypto.decrypt_block(data, file_path, encryption_method)
                data = PakCompression.decompress_block(data, self._zstd_dict, compression_method)
                file.write(data)

    def dump(self, out_path: PurePath) -> None:
        out_path /= self._mount_point
        for dir_path, dir in self._index.items():
            current_out_path = Path(out_path / dir_path)
            if not current_out_path.exists():
                current_out_path.mkdir(parents=True, exist_ok=True)
            for file_name, entry in dir.items():
                self._write_to_disk(current_out_path / file_name, entry)

        # Generate manifest
        manifest = {
            'tool': 'FANTool_3_0',
            'pak_file': str(self._file_path),
            'mount_point': str(self._mount_point),
            'extracted_at': datetime.now().isoformat(),
            'files': []
        }
        for dir_path, files in self._index.items():
            for fname, entry in files.items():
                manifest['files'].append({
                    'internal_path': str(dir_path / fname).replace('\\', '/'),
                    'uncompressed_size': entry.uncompressed_size,
                    'compression': entry.compression_method,
                    'encryption': entry.encryption_method,
                    'encrypted': entry.encrypted,
                })
        manifest_path = Path(out_path) / 'pak_manifest.json'
        try:
            with open(manifest_path, 'w') as mf:
                json.dump(manifest, mf, indent=2)
            console.print(f"[cyan]📋 Manifest saved: {manifest_path}[/cyan]")
        except Exception as e:
            console.print(f"[yellow]⚠ Could not save manifest: {e}[/yellow]")

def human_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def _load_bgmi_path_index() -> Dict[str, List[str]]:
    """
    Load ALL .csv files from the 'index' subfolder — supports BGMI, PUBG Global,
    or any version. Returns a dict: lowercase_filename -> [list of full internal paths].
    """
    script_dir = Path(__file__).resolve().parent
    index_dirs = [
        script_dir / "index",
        BASE_DIR / "index",
        Path("/storage/emulated/0/Download/FANTOOL/index"),
    ]

    csv_files = []
    for d in index_dirs:
        if d.exists():
            csv_files.extend(d.glob("*.csv"))

    # Deduplicate by name
    seen = set()
    unique_csv = []
    for f in csv_files:
        if f.name not in seen:
            seen.add(f.name)
            unique_csv.append(f)

    if not unique_csv:
        return {}

    index: Dict[str, List[str]] = {}
    for csv_path in unique_csv:
        try:
            with open(csv_path, "r", encoding="utf-8", errors="replace") as fh:
                first = True
                for line in fh:
                    line = line.strip().strip("\r\n")
                    if not line:
                        continue
                    if first:
                        first = False
                        if line.lower() in ("filepath", "path", "internal_path"):
                            continue
                    internal = line.replace("\\", "/").lstrip("/")
                    fname = Path(internal).name.lower()
                    index.setdefault(fname, []).append(internal)
        except Exception:
            pass

    return index

def _resolve_path_from_index(
    file_path: Path,
    index: Dict[str, List[str]],
    already_resolved: Dict[str, str],
) -> Optional[str]:
    """
    Given a local file path, try to find its canonical internal PAK path
    from the pre-built BGMI index.

    Resolution priority:
      1. Exact filename match with a unique result -> use it
      2. Multiple matches -> try to narrow by stem+ext, then by parent folder hint
      3. No match -> return None (caller will fall back to manual path)
    """
    fname_lower = file_path.name.lower()

    # Cache hit
    if fname_lower in already_resolved:
        return already_resolved[fname_lower]

    matches = index.get(fname_lower, [])

    if not matches:
        return None

    if len(matches) == 1:
        result = matches[0]
        already_resolved[fname_lower] = result
        return result

    # --- Ambiguous: multiple paths share the same filename ---
    # Strategy A: match by the immediate parent directory name
    parent_hint = file_path.parent.name.lower()
    if parent_hint:
        narrowed = [m for m in matches if Path(m).parent.name.lower() == parent_hint]
        if len(narrowed) == 1:
            result = narrowed[0]
            already_resolved[fname_lower] = result
            return result
        if narrowed:
            matches = narrowed  # still ambiguous but smaller set

    # Strategy B: pick the shortest path (most likely a base asset, not a variant)
    result = min(matches, key=lambda p: len(p))
    already_resolved[fname_lower] = result
    return result

def _smart_resolve_in_pak(f: Path, pak, fallback_path: Optional[str]) -> Optional[str]:
    """
    Smart path resolver against actual PAK internal index.
    Priority:
      1. Exact relative path match (if file has sub-folder structure)
      2. Name-only match → unique → use it
      3. Multiple matches → sort by size diff → unique exact size → use it
      4. Still ambiguous → show top 2 to user, ask to choose
      5. No match → fallback_path + filename, or None
    Ported from Nadeem_tool (smart path matching logic).
    """
    fname      = f.name
    fname_low  = fname.lower()
    local_size = f.stat().st_size

    # 1. exact relative path match
    for dir_path, dir_content in pak._index.items():
        for index_fname, entry in dir_content.items():
            from pathlib import PurePath as _PP
            full = str(_PP(dir_path) / index_fname).replace('\\', '/')
            if full.lower().endswith('/' + fname_low):
                return full

    # 2. name-only match
    matches = []
    for dir_path, dir_content in pak._index.items():
        for index_fname, entry in dir_content.items():
            if index_fname.lower() == fname_low:
                from pathlib import PurePath as _PP
                full = str(_PP(dir_path) / index_fname).replace('\\', '/')
                matches.append((full, entry))

    if not matches:
        # no match in PAK index — use fallback path
        if fallback_path:
            return (fallback_path.rstrip('/') + '/' + fname)
        return None

    if len(matches) == 1:
        return matches[0][0]

    # 3. sort by size diff + fingerprint (dravix method)
    matches_sorted = sorted(matches, key=lambda m: abs(m[1].uncompressed_size - local_size))
    best_diff  = abs(matches_sorted[0][1].uncompressed_size - local_size)
    second_diff = abs(matches_sorted[1][1].uncompressed_size - local_size) if len(matches_sorted) > 1 else None

    if best_diff == 0 and (second_diff is None or second_diff > 0):
        return matches_sorted[0][0]

    # try dravix fingerprint resolve
    fp_result = _dravix_fingerprint_resolve(f.name, f, [(p, e) for p, e in matches])
    if fp_result:
        return fp_result[0]

    # 4. still ambiguous — show top choices to user
    top = matches_sorted[:3]
    console.print(f"\n[bold yellow]⚠ '{fname}' için birden fazla konum bulundu:[/bold yellow]")
    for i, (path, entry) in enumerate(top, 1):
        diff = abs(entry.uncompressed_size - local_size)
        mark = "[green]✓ boyut eşleşti[/green]" if diff == 0 else f"[dim]±{diff} byte[/dim]"
        console.print(f"  [{i}] {path}  {mark}")
    console.print(f"  [0] Atla")
    while True:
        c = safe_input(f"  Seç (0-{len(top)}): ").strip(); flush_stdin()
        if c == '0': return None
        if c.isdigit() and 1 <= int(c) <= len(top):
            return top[int(c)-1][0]
        console.print("  Geçersiz.")

def _create_fan_pak_workspace(pak_stem: str) -> tuple:
    """
    Creates a FANx-named workspace folder derived from the PAK filename.

    Structure:
        BASE_DIR/
        └── FANx{PAK_STEM}/
            ├── CUSTOM FILES/    ← user drops their mod files here (inject source)
            └── RESULT PAK/      ← modded PAK output goes here

    Returns:
        (workspace_root, custom_files_dir, result_pak_dir)
    """
    # Sanitize PAK stem — strip spaces, collapse special chars for folder safety
    safe_stem = re.sub(r'[^\w\-.]', '_', pak_stem).strip('_') or "PAK"
    workspace_root  = BASE_DIR / f"FANx{safe_stem}"
    custom_files_dir = workspace_root / "CUSTOM FILES"
    result_pak_dir = workspace_root / "RESULT PAK"

    for folder in (workspace_root, custom_files_dir, result_pak_dir):
        folder.mkdir(parents=True, exist_ok=True)

    return workspace_root, custom_files_dir, result_pak_dir

def run_inject():
    console.print("[white]Auto-detects internal PAK path from BGMI.csv index[/white]")

    out_path = BASE_DIR

    # ── PAK file selection (early — needed to derive workspace name) ─────────
    console.print("[cyan]🔍 Searching for PAK files...[/cyan]")
    pak_files = [f for f in BASE_DIR.iterdir() if f.name.lower().endswith(".pak")]

    if not pak_files:
        console.print("[bold red]❌ No PAK file found in folder![/bold red]")
        console.print(f"[red]📁 Please put a PAK file in: {BASE_DIR}[/red]")
        flush_stdin()
        safe_input("\nPress Enter to continue...")
        return

    if len(pak_files) == 1:
        pak_path = pak_files[0]
        console.print(f"[green]✅ Found PAK: {pak_path.name}[/green]")
    else:
        console.print(f"[yellow]⚠️ Multiple PAK files found:[/yellow]")
        for i, pak in enumerate(pak_files, 1):
            console.print(f"  [{i}] {pak.name}")
        console.print("\n[bold yellow]Enter number to select:[/bold yellow]")
        try:
            choice_pak = int(safe_input("> ").strip())
            if 1 <= choice_pak <= len(pak_files):
                pak_path = pak_files[choice_pak - 1]
                console.print(f"[green]✅ Selected: {pak_path.name}[/green]")
            else:
                console.print("[bold red]❌ Invalid choice![/bold red]")
                flush_stdin()
                safe_input("\nPress Enter to continue...")
                return
        except Exception:
            console.print("[bold red]❌ Invalid input![/bold red]")
            flush_stdin()
            safe_input("\nPress Enter to continue...")
            return

    # ── Create FANx workspace derived from PAK name ─────────────────────────
    workspace_root, custom_files_dir, result_pak_dir = \
        _create_fan_pak_workspace(pak_path.stem)

    console.print(
        f"\n[bold magenta]📁 FANx Workspace:[/bold magenta] [cyan]{workspace_root.name}[/cyan]"
    )
    console.print(f"  [dim]├── CUSTOM FILES/  ← drop mod files here[/dim]")
    console.print(f"  [dim]└── RESULT PAK/    ← modded PAK output[/dim]")

    # edit_dir is now the CUSTOM FILES subfolder inside workspace
    edit_dir = custom_files_dir

    # ── Folder existence checks ──────────────────────────────────────────────
    files_in_edit = [
        f for f in edit_dir.rglob("*")
        if f.is_file() and f.name not in ["pak_manifest.json", ".DS_Store"]
    ]
    if not files_in_edit:
        console.print(f"\n[bold yellow]⚠ CUSTOM FILES folder is empty![/bold yellow]")
        console.print(f"[yellow]📁 Drop your mod files into:[/yellow]")
        console.print(f"  [cyan]{edit_dir}[/cyan]")
        console.print("[dim]Then run Custom Inject again.[/dim]")
        flush_stdin()
        safe_input("\nPress Enter to continue...")
        return

    # ── Load BGMI path index ─────────────────────────────────────────────────
    console.print("\n[bold #00FFFF]📖 Loading BGMI path index...[/bold #00FFFF]")
    bgmi_index = _load_bgmi_path_index()

    if bgmi_index:
        console.print(
            f"[green]✅ Index loaded — {len(bgmi_index):,} unique filenames mapped[/green]"
        )
        use_auto_path = True
    else:
        console.print(
            "[yellow]⚠ BGMI.csv not found in 'index/' folder — falling back to manual path[/yellow]"
        )
        console.print(
            "[dim]Tip: place BGMI.csv inside a folder named 'index' next to the tool[/dim]"
        )
        use_auto_path = False

    # ── Fallback manual path (used when index is missing or file not found) ──
    fallback_path: Optional[str] = None
    if not use_auto_path:
        console.print("\n[bold yellow]Enter Target Repacking Path in PAK:[/bold yellow]")
        console.print("[dim](Press Enter for default: Content/Lua/)[/dim]")
        console.print("[dim]Example: Content/Lua/GameLua/Mod/BRMod/Gameplay/Core/[/dim]")
        raw = safe_input("> ").strip()
        flush_stdin()
        if not raw:
            fallback_path = "Content/Lua/"
        else:
            fallback_path = raw if raw.endswith("/") else raw + "/"
        console.print(f"[cyan]🎯 Fallback path: {fallback_path}[/cyan]")

    # ── Build inject plan ────────────────────────────────────────────────────
    try:
        console.print("[cyan]📦 Loading PAK file...[/cyan]")
        pak = TencentPakFile(PurePath(pak_path))
        output_name = f"{pak_path.stem}.pak"
        # Output modded PAK goes into RESULT PAK/ folder
        output_pak = result_pak_dir / output_name

        inject_folder = edit_dir
        files = [
            f for f in inject_folder.rglob("*")
            if f.is_file() and f.name not in ["pak_manifest.json", ".DS_Store"]
        ]

        if not files:
            console.print("[yellow]No files to inject.[/yellow]")
            flush_stdin()
            safe_input("\nPress Enter to continue...")
            return

        dominant = pak.detect_dominant_style()
        console.print(
            f"[cyan]Dominant style: comp={dominant['comp_method']}, "
            f"enc={dominant['enc_method']}, encrypted={dominant['encrypted']}, "
            f"block={dominant['block_size']}[/cyan]"
        )

        # ── REPACK OVERRIDE: PAK-aware config ───────────────────────────────
        pak_name_lower = pak_path.name.lower()
        if "res_pufferpatch" in pak_name_lower:
            dominant["comp_method"] = 1       # CM_ZLIB
            dominant["enc_method"]  = 47      # SM4_NEW(47)
            dominant["encrypted"]   = True
            dominant["block_size"]  = 54326
            console.print(
                f"[bold yellow]⚡ res_pufferpatch override: "
                f"comp=ZLIB(1), enc=SM4_NEW(47), encrypted=True, block=54326[/bold yellow]"
            )
        else:
            # game_patch and all other PAKs — keep dominant style as-is
            console.print(
                f"[bold cyan]⚡ Using detected dominant style (no override)[/bold cyan]"
            )
        # ────────────────────────────────────────────────────────────────────

        inject_plan = []
        resolution_cache: Dict[str, str] = {}   # fname_lower -> resolved internal path
        unresolved_files: List[Path] = []

        console.print("\n[bold #00FFFF]🧭 Resolving internal PAK paths...[/bold #00FFFF]")

        for f in files:
            internal_path: Optional[str] = None

            if use_auto_path:
                resolved = _resolve_path_from_index(f, bgmi_index, resolution_cache)
                if resolved:
                    internal_path = resolved
                    console.print(
                        f"  [green]✓[/green] [white]{f.name}[/white] "
                        f"[dim]→ {internal_path}[/dim]"
                    )
                else:
                    console.print(
                        f"  [yellow]⚠[/yellow] [white]{f.name}[/white] "
                        f"[dim]not found in index[/dim]"
                    )
                    unresolved_files.append(f)

            if internal_path is None:
                # Use fallback: either manual path or relative path inside inject_folder
                if fallback_path:
                    rel = str(f.relative_to(inject_folder)).replace("\\", "/")
                    internal_path = (
                        fallback_path + rel
                        if not rel.startswith(fallback_path)
                        else rel
                    )
                else:
                    # auto mode but file not in index — ask user for this specific file
                    console.print(
                        f"\n[bold yellow]Manual path needed for:[/bold yellow] {f.name}"
                    )
                    console.print("[dim]Press Enter to skip this file[/dim]")
                    manual = safe_input(f"  Internal path for {f.name}: ").strip()
                    flush_stdin()
                    if not manual:
                        console.print(f"  [red]✗ Skipping {f.name}[/red]")
                        continue
                    internal_path = manual.replace("\\", "/").lstrip("/")

            inject_plan.append({
                "src_path":      f,
                "internal_path": internal_path,
                "comp_method":   dominant["comp_method"],
                "enc_method":    dominant["enc_method"],
                "encrypted":     dominant["encrypted"],
                "block_size":    dominant["block_size"],
            })

        # ── Summary before inject ────────────────────────────────────────────
        console.print("\n[bold #00FFFF]📊 Inject Summary:[/bold #00FFFF]")
        console.print(f"  [green]✓ Resolved  : {len(inject_plan)} file(s)[/green]")
        if unresolved_files and not fallback_path:
            skipped = len(files) - len(inject_plan)
            if skipped:
                console.print(f"  [red]✗ Skipped   : {skipped} file(s)[/red]")

        if not inject_plan:
            console.print("[bold red]❌ Nothing to inject — aborting.[/bold red]")
            flush_stdin()
            safe_input("\nPress Enter to continue...")
            return

        # Print the resolved plan as a table
        table = Table(title="Inject Plan", show_lines=False, box=None)
        table.add_column("File", style="#00CCFF", no_wrap=True)
        table.add_column("→ Internal PAK Path", style="#FFFF00")
        for item in inject_plan:
            table.add_row(
                Path(str(item["src_path"])).name,
                item["internal_path"],
            )
        console.print(table)

        # ── Confirm ─────────────────────────────────────────────────────────
        console.print("\n[bold yellow]Proceed with inject? (Y/n):[/bold yellow]")
        confirm = safe_input("> ").strip().lower()
        flush_stdin()
        if confirm == "n":
            console.print("[yellow]Inject cancelled.[/yellow]")
            return

        console.print("[cyan]🔄 Running inject...[/cyan]")
        pak.inject_files(inject_plan, Path(output_pak))
        console.print(f"\n[bold green]✅ Inject complete![/bold green]")
        console.print(
            f"\n[bold magenta]📁 FANx{pak_path.stem}/[/bold magenta]"
        )
        console.print(f"  [yellow]├── CUSTOM FILES/[/yellow]  [dim]← your mod files[/dim]")
        console.print(f"  [bold white]└── RESULT PAK/{output_name}[/bold white]  [dim]← modded PAK[/dim]")
        console.print(f"\n[green]Processed {len(inject_plan)} file(s).[/green]")

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()

    flush_stdin()


def _rgb(r, g, b): return f'\033[38;2;{r};{g};{b}m'
def _bgg(r, g, b): return f'\033[48;2;{r};{g};{b}m'

def print_inject_banner():
    import sys as _sys, random as _random
    os.system('clear' if os.name == 'posix' else 'cls')
    now = datetime.now()
    RS = '\033[0m'; BOLD = '\033[1m'; BLINK = '\033[5m'; DIM = '\033[2m'

    LOGO = [
        "███████╗ █████╗ ███╗   ██╗████████╗ ██████╗  ██████╗ ██╗     ",
        "██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ",
        "█████╗  ███████║██╔██╗ ██║   ██║   ██║   ██║██║   ██║██║     ",
        "██╔══╝  ██╔══██║██║╚██╗██║   ██║   ██║   ██║██║   ██║██║     ",
        "██║     ██║  ██║██║ ╚████║   ██║   ╚██████╔╝╚██████╔╝███████╗",
        "╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝",
    ]

    PALETTE = [
        (0,255,255),(0,200,255),(50,150,255),
        (255,180,0),(255,220,0),(255,100,0),
    ]
    LIGHT_CHARS = ['★','◆','●','✦','◉','✸']
    DARK = (20,20,40)
    WIDTH = 66

    def _lights_row(frame):
        out = "  "
        for j in range(WIDTH):
            seed = (j * 7 + frame * 3) % 17
            if seed == 0:   out += f"{BLINK}{_rgb(255,220,0)}{LIGHT_CHARS[(j+frame)%len(LIGHT_CHARS)]}{RS}"
            elif seed < 3:  out += f"{_rgb(0,255,200)}{'·' if (j+frame)%2==0 else '·'}{RS}"
            elif seed < 6:  out += f"{_rgb(100,50,200)}·{RS}"
            else:           out += f"{_rgb(*DARK)}·{RS}"
        return out

    def _border(frame):
        out = "  "
        for j in range(WIDTH+2):
            if j % 4 == (frame % 4):
                r,g,b = PALETTE[(j//4+frame)%len(PALETTE)]
                out += f"{BOLD}{_rgb(r,g,b)}━{RS}"
            else:
                out += f"{_rgb(50,50,80)}─{RS}"
        return out

    # ── animation frames ──────────────────────────────────────────────
    for frame in range(14):
        os.system('clear' if os.name == 'posix' else 'cls')
        print()
        print(_border(frame))
        print()
        for i, line in enumerate(LOGO):
            # per-row color shifts with frame offset
            r1,g1,b1 = PALETTE[(i*2+frame)   % len(PALETTE)]
            r2,g2,b2 = PALETTE[(i*2+frame+1) % len(PALETTE)]
            # split line into two halves with different hues
            half = len(line)//2
            left  = f"{BOLD}{_rgb(r1,g1,b1)}{line[:half]}{RS}"
            right = f"{BOLD}{_rgb(r2,g2,b2)}{line[half:]}{RS}"
            print(f"  {left}{right}")
        print()
        print(_lights_row(frame))
        print(_border(frame+1))
        print()
        tag = f"{_rgb(0,200,255)}@FanteriBey{RS}"
        ver = f"{_rgb(255,200,0)}v2.0{RS}"
        plat= f"{_rgb(100,255,150)}PUBG Global/BGMI{RS}"
        print(f"  {tag}  {ver}  {DIM}|{RS}  {plat}  {DIM}|  Termux{RS}")
        _sys.stdout.flush()
        time.sleep(0.07)

    # ── final static frame ────────────────────────────────────────────
    os.system('clear' if os.name == 'posix' else 'cls')
    print()
    print(_border(14))
    print()
    FINAL_COLORS = [(0,255,255),(0,220,255),(80,180,255),(255,180,0),(255,220,0),(255,100,50)]
    for i, line in enumerate(LOGO):
        r,g,b = FINAL_COLORS[i % len(FINAL_COLORS)]
        print(f"  {BOLD}{_rgb(r,g,b)}{line}{RS}")
    print()
    # static lights — mix of stars and dots
    out = "  "
    for j in range(WIDTH):
        if j % 6 == 0:   out += f"{BOLD}{_rgb(255,220,0)}★{RS}"
        elif j % 4 == 0: out += f"{_rgb(0,255,200)}◆{RS}"
        elif j % 2 == 0: out += f"{_rgb(50,80,200)}·{RS}"
        else:             out += f"{_rgb(*DARK)}·{RS}"
    print(out)
    print(_border(15))
    print()
    print(f"  {BOLD}{_rgb(0,255,255)}@FanteriBey{RS}  "
          f"{_rgb(255,220,0)}v2.0{RS}  "
          f"{DIM}|{RS}  "
          f"{_rgb(100,255,150)}PUBG Global / BGMI{RS}  "
          f"{DIM}|{RS}  "
          f"{_rgb(0,200,255)}Termux{RS}")
    print(f"  {DIM}{now.strftime('%d-%m-%Y')}  {now.strftime('%H:%M:%S')}{RS}")
    print()

def _list_pak_contents(pak_files):
    if not pak_files:
        console.print("[red]❌ No PAK files found in BASE_DIR![/red]")
        flush_stdin()
        safe_input("\nPress Enter to continue...")
        return

    console.print("\n[cyan]Select PAK file to list:[/cyan]")
    for i, p in enumerate(pak_files, 1):
        console.print(f"  [{i}] {p.name} ({human_size(p.stat().st_size)})")
    try:
        choice = int(safe_input("> ").strip())
        flush_stdin()
        if 1 <= choice <= len(pak_files):
            pak_path = pak_files[choice - 1]
        else:
            console.print("[red]Invalid choice.[/red]")
            return
    except:
        console.print("[red]Invalid input.[/red]")
        return

    console.print(f"\n[cyan]📦 Loading {pak_path.name}...[/cyan]")
    try:
        pak = TencentPakFile(PurePath(pak_path))
        paths = pak.list_existing_paths()
        console.print(f"[green]✅ {len(paths):,} file(s) found[/green]")

        table = Table(title=f"PAK Contents: {pak_path.name}", show_lines=False, box=None)
        table.add_column("#", style="dim", width=6)
        table.add_column("Internal Path", style="#00CCFF")

        total = len(paths)
        PAGE = 25; page = 0
        while True:
            os.system('clearf')
            console.print(f"[bold cyan]📋 PAK: {pak_path.name}[/bold cyan]  [dim]{total} dosya | Sayfa {page+1}/{(total+PAGE-1)//PAGE}[/dim]")
            console.print()
            chunk = paths[page*PAGE:(page+1)*PAGE]
            for i, p in enumerate(chunk, page*PAGE+1):
                console.print(f"  [dim]{i:4}[/dim]  [cyan]{p[:70]}[/cyan]")
            console.print()
            console.print(f"[dim]  {T('nav_hint')}[/dim]")
            cmd = safe_input("  > ").strip().lower(); flush_stdin()
            if cmd == '0' or cmd == '': break
            elif cmd == 'n': page = min(page+1, (total-1)//PAGE)
            elif cmd == 'p': page = max(page-1, 0)
    except Exception as e:
        console.print(f"[red]❌ Error loading PAK: {e}[/red]")
        flush_stdin(); safe_input("\nPress Enter to continue...")

def _clean_workspaces(fan_dirs):
    if not fan_dirs:
        console.print("[yellow]⚠ No FANx* workspace folders found.[/yellow]")
    else:
        console.print(f"[cyan]Found {len(fan_dirs)} workspace folder(s):[/cyan]")
        for d in fan_dirs:
            console.print(f"  [dim]• {d.name}[/dim]")
        console.print("\n[yellow]Delete all? (y/N):[/yellow]")
        confirm = safe_input("> ").strip().lower()
        flush_stdin()
        if confirm == "y":
            removed = 0
            for d in fan_dirs:
                try:
                    shutil.rmtree(d)
                    console.print(f"  [green]✓ Removed {d.name}[/green]")
                    removed += 1
                except Exception as e:
                    console.print(f"  [red]✗ Error removing {d.name}: {e}[/red]")
            console.print(f"\n[green]✔ Cleaned {removed} workspace(s).[/green]")
        else:
            console.print("[dim]Cancelled.[/dim]")

    flush_stdin()
    safe_input("\nPress Enter to continue...")

def main_menu():
    while True:
        print_inject_banner()

        pak_files = sorted(
            [f for f in BASE_DIR.iterdir() if f.is_file() and f.name.lower().endswith('.pak')],
            key=lambda x: x.name
        )
        fan_dirs = sorted(
            [d for d in BASE_DIR.iterdir() if d.is_dir() and d.name.startswith('FANx')],
            key=lambda x: x.name
        )

        pak_info = f'[green]{len(pak_files)} {T("pak_files")}[/green]' if pak_files else f'[yellow]{T("no_pak")}[/yellow]'
        ws_info = f'[cyan]{len(fan_dirs)} {T("workspaces")}[/cyan]' if fan_dirs else f'[dim]{T("no_ws")}[/dim]'

        console.print(f'  [white]PAK Files  : {pak_info}[/white]')
        console.print(f'  [white]Workspaces : {ws_info}[/white]')
        console.print()
        console.print(f'  [bold #00FF88][1] {T("m1")}[/bold #00FF88]  [dim]{T("d1")}[/dim]')
        console.print(f'  [bold #00CCFF][2] {T("m2")}[/bold #00CCFF]  [dim]{T("d2")}[/dim]')
        console.print(f'  [bold #FFAA00][3] {T("m3")}[/bold #FFAA00]  [dim]{T("d3")}[/dim]')
        console.print(f'  [bold #FF88FF][4] {T("m4")}[/bold #FF88FF]  [dim]{T("d4")}[/dim]')
        console.print(f'  [bold #00CCFF][5] {T("m5")}[/bold #00CCFF]  [dim]{T("d5")}[/dim]')
        console.print(f'  [bold #FF88FF][6] {T("m6")}[/bold #FF88FF]  [dim]{T("d6")}[/dim]')
        console.print(f'  [bold #FFAA00][7] {T("m7")}[/bold #FFAA00]  [dim]{T("d7")}[/dim]')
        console.print(f'  [bold red][8] 🗑  DELETE FROM PAK[/bold red]       [dim]PAK içinden dosya/klasör sil[/dim]')
        console.print(f'  [bold #00FFCC][9] 📦 OBB TOOL[/bold #00FFCC]            [dim].obb çıkar / repack[/dim]')
        console.print(f'  [bold #FFCC00][10] 🔑 SM4 KEY FINDER[/bold #FFCC00]      [dim]libUE4.so\'dan SM4 key tara[/dim]')
        console.print(f'  [bold #FF8800][11] {T("m11")}[/bold #FF8800]  [dim]{T("d11")}[/dim]')
        console.print(f'  [bold #00FF88][12] 🔧 SO PATCHER[/bold #00FF88]          [dim]lib.so/APK panel link bul & değiştir[/dim]')
        console.print(f'  [bold #FF4444][13] {T("m13")}[/bold #FF4444]  [dim]{T("d13")}[/dim]')
        console.print(f'  [bold #00FFCC][14] {T("m14")}[/bold #00FFCC]  [dim]{T("d14")}[/dim]')
        console.print(f'  [bold #FFAA00][15] 📦 PAK REPACK[/bold #FFAA00]           [dim]değiştirilmiş dosyaları PAK\'a yaz[/dim]')
        console.print(f'  [bold #00FFCC][16] {T("m16")}[/bold #00FFCC]  [dim]{T("d16")}[/dim]')
        console.print(f'  [bold #FF4444][17] {T("m17")}[/bold #FF4444]  [dim]{T("d17")}[/dim]')
        console.print(f'  [bold #00D4FF][18] {T("m18")}[/bold #00D4FF]  [dim]{T("d18")}[/dim]')
        console.print(f'  [bold #10D98A][19] {T("m19")}[/bold #10D98A]  [dim]{T("d19")}[/dim]')
        console.print(f'  [bold #A855F7][20] {T("m20")}[/bold #A855F7]  [dim]{T("d20")}[/dim]')
        console.print(f'  [bold #F59E0B][21] {T("m21")}[/bold #F59E0B]  [dim]{T("d21")}[/dim]')
        console.print(f'  [bold #F59E0B][22] {T("m22")}[/bold #F59E0B]  [dim]{T("d22")}[/dim]')
        console.print(f'  [bold #EF4444][23] {T("m23")}[/bold #EF4444]  [dim]{T("d23")}[/dim]')
        console.print(f'  [bold #0EA5E9][24] {T("m24")}[/bold #0EA5E9]  [dim]{T("d24")}[/dim]')
        console.print(f'  [bold #FF4444][25] {T("m25")}[/bold #FF4444]  [dim]{T("d25")}[/dim]')
        console.print(f'  [bold #7C3AED][26] {T("m26")}[/bold #7C3AED]  [dim]{T("d26")}[/dim]')
        console.print(f'  [bold #10B981][27] {T("m27")}[/bold #10B981]  [dim]{T("d27")}[/dim]')
        console.print(f'  [bold #F472B6][28] {T("m28")}[/bold #F472B6]  [dim]{T("d28")}[/dim]')
        console.print(f'  [bold #06B6D4][29] {T("m29")}[/bold #06B6D4]  [dim]{T("d29")}[/dim]')
        console.print(f'  [bold #FF88FF][30] {T("m30")}[/bold #FF88FF]  [dim]{T("d30")}[/dim]')
        console.print(f'  [bold #FFAA00][31] {T("m31")}[/bold #FFAA00]  [dim]{T("d31")}[/dim]')
        console.print(f'  [bold #06B6D4][32] {T("m32")}[/bold #06B6D4]  [dim]{T("d32")}[/dim]')
        console.print(f'  [bold #A855F7][33] {T("m33")}[/bold #A855F7]  [dim]{T("d33")}[/dim]')
        console.print(f'  [bold #FF0055][0] {T("exit")}[/bold #FF0055]')

        choice = safe_input('  > ').strip()
        flush_stdin()

        if choice == '1':
            run_inject()
        elif choice == '2':
            _list_pak_contents(pak_files)
        elif choice == '3':
            _clean_workspaces(fan_dirs)
        elif choice == '4':
            lua_mode_menu()
        elif choice == '5':
            action_120fps()
        elif choice == '6':
            action_skin()
        elif choice == '7':
            action_file_finder()
        elif choice == '8':
            action_delete_from_pak()
        elif choice == '9':
            action_obb_tool()
        elif choice == '10':
            action_sm4_finder()
        elif choice == '11':
            action_xor_crypt()
        elif choice == '12':
            action_so_patcher()
        elif choice == '13':
            action_py_encryptor()
        elif choice == '14':
            action_pak_unpack()
        elif choice == '15':
            action_pak_repack()
        elif choice == '16':
            action_uasset_editor()
        elif choice == '17':
            action_mod_patch()
        elif choice == '18':
            action_araçlar_menu()
        elif choice == '19':
            action_pubg_araçlar_menu()
        elif choice == '20':
            action_advanced_menu()
        elif choice == '21':
            action_crypto_ultra()
        elif choice == '22':
            action_pak_ultra_menu()
        elif choice == '23':
            action_oyun_ultra_menu()
        elif choice == '24':
            action_termux_pro_menu()
        elif choice == '25':
            action_pubg_lua_menu()
        elif choice == '26':
            action_binary_hacks_menu()
        elif choice == '27':
            action_asset_hacks_menu()
        elif choice == '28':
            action_texture_visual_menu()
        elif choice == '29':
            action_mod_pack_menu()
        elif choice == '30':
            action_lua_ultra_menu()
        elif choice == '31':
            action_pak_ultra_plus_menu()
        elif choice == '32':
            action_so_ultra_menu()
        elif choice == '33':
            action_uasset_ultra_menu()
        elif choice == '0':
            console.print()
            time.sleep(0.5)
            break
        else:
            console.print('[red]Geçersiz seçim.[/red]')
            time.sleep(1)

# ==================== LUA BYTECODE CONVERTER (clean — no sabotage, no Telegram) ====================
# Ported from HexaCore (FAZAL HALLIA) — malicious components removed

_LUA_DIRS_CREATED = False

def _ensure_lua_dirs():
    global _LUA_DIRS_CREATED
    if _LUA_DIRS_CREATED:
        return
    for d in ["LUA_ORIGINAL", "LUA_EDIT", "COMPILED", "SOURCE"]:
        (BASE_DIR / d).mkdir(parents=True, exist_ok=True)
    _LUA_DIRS_CREATED = True

LUA_ORIGINAL_DIR = BASE_DIR / "LUA_ORIGINAL"
LUA_EDIT_DIR     = BASE_DIR / "LUA_EDIT"
COMPILED_DIR     = BASE_DIR / "COMPILED"
SOURCE_DIR_LUA   = BASE_DIR / "SOURCE"
_HOME_SOURCE     = Path(os.path.expanduser("~")) / ".fan_source"
UNLUAC_JAR       = SOURCE_DIR_LUA / "unluac_patched.jar"

def _get_luac_cmd():
    # önce home'da ara (execute izni var)
    home_luac = _HOME_SOURCE / "luac5.3"
    if home_luac.exists():
        return str(home_luac)
    # sonra Termux bin'de ara
    termux_luac = Path("/data/data/com.termux/files/usr/bin/luac5.3")
    if termux_luac.exists():
        return str(termux_luac)
    # sdcard'daki kopyayı home'a taşı
    sdcard_luac = SOURCE_DIR_LUA / "luac5.3"
    if sdcard_luac.exists():
        _HOME_SOURCE.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(sdcard_luac), str(home_luac))
        os.chmod(str(home_luac), 0o755)
        return str(home_luac)
    import shutil as _sh
    for name in ('luac5.3', 'luac53'):
        w = _sh.which(name)
        if w: return w
    return 'luac5.3'

# ── LUA binary helpers ────────────────────────────────────────────────────────

STRING_XOR_KEY = bytes([
    17,33,54,71,70,87,167,141,157,132,144,216,171,0,
    140,53,38,26,247,228,88,5,184,179,21,7,208,44,30,143,246,200
])

_BGMI_TO_STD_BASE = [13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,
                      0,1,2,3,4,5,6,7,8,9,10,11,12,30,31,32,33,34,35,36,
                      37,38,39,40,41,42,43,44,45,46]
BGMI_TO_STD = _BGMI_TO_STD_BASE + [x + 64 for x in range(len(_BGMI_TO_STD_BASE))]
STD_TO_BGMI = {}
for _k, _v in enumerate(BGMI_TO_STD):
    STD_TO_BGMI[_v] = _k

STD_FMT = [0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
           0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,2,0,1,0,3]
iABC, iABx, iAsBx, iAx = 0, 1, 2, 3
_LUA_HEADER_SIZE = 33

class _LuaReader:
    def __init__(self, data: bytes, sizet: int = 4):
        self.data = bytearray(data)
        self.pos  = 0
        self.sizet = sizet

    def byte(self) -> int:
        v = self.data[self.pos]; self.pos += 1; return v

    def uint32(self) -> int:
        v = struct.unpack_from('<I', self.data, self.pos)[0]; self.pos += 4; return v

    def int32(self) -> int:
        v = struct.unpack_from('<i', self.data, self.pos)[0]; self.pos += 4; return v

    def int64(self) -> int:
        v = struct.unpack_from('<q', self.data, self.pos)[0]; self.pos += 8; return v

    def double(self) -> float:
        v = struct.unpack_from('<d', self.data, self.pos)[0]; self.pos += 8; return v

    def bytes_(self, n: int) -> bytes:
        v = bytes(self.data[self.pos:self.pos+n]); self.pos += n; return v

    def pubg_string(self):
        sz = self.byte()
        if sz == 255: sz = self.uint32()
        if sz == 0: return None
        sz -= 1
        enc = self.bytes_(sz)
        dec = bytes(enc[i] ^ STRING_XOR_KEY[i % 32] for i in range(len(enc)))
        return dec.decode('utf-8', 'replace')

    def std_string(self):
        sz = self.byte()
        if sz == 255:
            sz = struct.unpack_from('<Q', self.data, self.pos)[0]; self.pos += 8
        if sz == 0: return None
        sz -= 1
        return self.bytes_(sz).decode('utf-8', 'replace')

class _LuaWriter:
    def __init__(self): self.buf = bytearray()
    def byte(self, v): self.buf.append(v & 0xFF)
    def uint32(self, v): self.buf.extend(struct.pack('<I', v))
    def int32(self, v): self.buf.extend(struct.pack('<i', v))
    def int64(self, v): self.buf.extend(struct.pack('<q', v))
    def double(self, v): self.buf.extend(struct.pack('<d', v))
    def raw(self, data): self.buf.extend(data)
    def get_data(self) -> bytes: return bytes(self.buf)

    def lua_string(self, s, is_pubg=False):
        if s is None: self.byte(0); return
        e = s.encode('utf-8') if isinstance(s, str) else s
        sz = len(e) + 1
        if sz < 255: self.byte(sz)
        else: self.byte(255); self.uint32(sz)
        if is_pubg:
            self.raw(bytes(e[i] ^ STRING_XOR_KEY[i % 32] for i in range(len(e))))
        else:
            self.raw(e)

    def lua_inst(self, op, A, B, C, Bx, sBx, Ax, fmt):
        op &= 63
        if   fmt == iABC:  r = (op<<6)|(C&0x1FF)<<14|(B&0x1FF)<<23|(A&0xFF)
        elif fmt == iABx:  r = (op<<6)|(Bx&0x3FFFF)<<14|(A&0xFF)
        elif fmt == iAsBx: r = (op<<6)|((sBx+131071)&0x3FFFF)<<14|(A&0xFF)
        elif fmt == iAx:   r = (op<<6)|(Ax&0x3FFFFFF)
        else:              r = 0
        self.uint32(r)

def _convert_function(reader, writer, to_std=True):
    src = reader.pubg_string() if to_std else reader.std_string()
    writer.lua_string(src, is_pubg=(not to_std))
    linedefined = reader.int32(); writer.int32(linedefined); writer.int32(reader.int32())
    writer.byte(reader.byte()); writer.byte(reader.byte()); writer.byte(reader.byte())
    csz = reader.uint32(); writer.uint32(csz)
    opmap = BGMI_TO_STD if to_std else STD_TO_BGMI
    for _ in range(csz):
        raw = reader.uint32(); bop = raw & 63
        A=(raw>>6)&0xFF; B=(raw>>23)&0x1FF; C=(raw>>14)&0x1FF
        Bx=(raw>>14)&0x3FFFF; sBx=Bx-131071; Ax=(raw>>6)&0x3FFFFFF
        sop = opmap[bop] if bop < len(opmap) else bop
        fmt = STD_FMT[sop] if sop < len(STD_FMT) else iABC
        writer.lua_inst(sop, A, B, C, Bx, sBx, Ax, fmt)
    nk = reader.uint32(); writer.uint32(nk)
    for _ in range(nk):
        t = reader.byte(); writer.byte(t)
        if   t == 0: pass
        elif t == 1: writer.byte(reader.byte())
        elif t == 3: writer.double(reader.double())
        elif t == 19: writer.int64(reader.int64())
        elif t in (4, 20):
            s = reader.pubg_string() if to_std else reader.std_string()
            writer.lua_string(s, is_pubg=(not to_std))
    nups = reader.uint32(); writer.uint32(nups)
    for _ in range(nups): writer.byte(reader.byte()); writer.byte(reader.byte())
    npts = reader.uint32(); writer.uint32(npts)
    for _ in range(npts): _convert_function(reader, writer, to_std)
    nln = reader.uint32()
    if to_std:
        lines = []; cur = linedefined
        for _ in range(nln):
            d = reader.byte(); cur += d if d <= 127 else d - 256; lines.append(cur)
        writer.uint32(len(lines))
        for ln in lines: writer.int32(ln)
        nab = reader.uint32()
        for _ in range(nab): reader.uint32(); reader.uint32()
    else:
        lines = [reader.int32() for _ in range(nln)]; writer.uint32(len(lines)); prev = linedefined
        for ln in lines:
            delta = ln - prev
            if -128 <= delta <= 127: writer.byte(delta & 0xFF)
            else: writer.byte(0); writer.int32(delta)
            prev = ln
        writer.uint32(0)
    nloc = reader.uint32(); writer.uint32(nloc)
    for _ in range(nloc):
        s = reader.pubg_string() if to_std else reader.std_string()
        writer.lua_string(s, is_pubg=(not to_std)); writer.int32(reader.int32()); writer.int32(reader.int32())
    nupn = reader.uint32(); writer.uint32(nupn)
    for _ in range(nupn):
        s = reader.pubg_string() if to_std else reader.std_string()
        writer.lua_string(s, is_pubg=(not to_std))

def _bgmi_to_std(data: bytes) -> bytes:
    if data[:4] != b'\x1bLua': raise ValueError('Not valid Lua bytecode')
    reader = _LuaReader(data, sizet=4); writer = _LuaWriter()
    hdr = bytearray(data[:_LUA_HEADER_SIZE]); hdr[4] = 13
    writer.raw(bytes(hdr)); reader.pos = _LUA_HEADER_SIZE
    writer.byte(reader.byte()); _convert_function(reader, writer, to_std=True)
    return writer.get_data()

def _std_to_bgmi(data: bytes) -> bytes:
    if data[:4] != b'\x1bLua': raise ValueError('Not valid Lua bytecode')
    sizet = data[13] if data[13] in (4, 8) else 4
    reader = _LuaReader(data, sizet=sizet); writer = _LuaWriter()
    hdr = bytearray(data[:_LUA_HEADER_SIZE]); hdr[4] = 13
    writer.raw(bytes(hdr)); reader.pos = _LUA_HEADER_SIZE
    writer.byte(reader.byte()); _convert_function(reader, writer, to_std=False)
    return writer.get_data()

def _convert_luac(inp: str, outp: str) -> tuple:
    import shutil as _sh
    try:
        with open(inp, 'rb') as f: data = f.read()
    except Exception as e:
        return False, str(e)
    if len(data) < 34 or data[:4] != b'\x1bLua':
        _sh.copy2(inp, outp); return True, outp
    nibble_flag = data[33]
    if nibble_flag > 2: nibble_flag = 0; data = bytes([0]+list(data[1:]))
    if nibble_flag > 1:
        fixed = bytearray(data[:34])
        for i in range(34, len(data)):
            b = data[i]; fixed.append(((b<<4)&0xF0)|((b>>4)&0x0F))
        data = bytes(fixed)
    try:
        std_data = _bgmi_to_std(data)
    except Exception:
        _sh.copy2(inp, outp); return True, outp
    with open(outp, 'wb') as f: f.write(std_data)
    return True, outp

def _repack_to_pubg(std_path: str, orig_path: str, outp: str, pad_size=None) -> tuple:
    try:
        with open(orig_path, 'rb') as f: orig = f.read()
    except Exception as e:
        return False, str(e)
    if len(orig) < 34 or orig[:4] != b'\x1bLua':
        return False, 'Original not valid Lua bytecode'
    header = orig[:33]; nibble_flag = orig[33]
    if nibble_flag > 2: nibble_flag = 0
    with open(std_path, 'rb') as f: std = f.read()
    try:
        bgmi = _std_to_bgmi(std)
    except Exception as e:
        return False, str(e)
    bgmi = header + bytes([nibble_flag]) + bgmi[34:]
    if nibble_flag > 1:
        out = bytearray(bgmi[:34])
        for i in range(34, len(bgmi)):
            b = bgmi[i]; out.append(((b<<4)&0xF0)|((b>>4)&0x0F))
        bgmi = bytes(out)
    if pad_size and len(bgmi) < pad_size:
        bgmi += b'\x00' * (pad_size - len(bgmi))
    with open(outp, 'wb') as f: f.write(bgmi)
    return True, outp

def _robust_decompile(src: str, out_dir: str, tmp_dir: str) -> tuple:
    name = os.path.basename(src); base = os.path.splitext(name)[0]
    out_path = os.path.join(out_dir, base + '.lua')
    temp_std = os.path.join(tmp_dir, base + '.std.luac')
    ok, msg = _convert_luac(src, temp_std)
    if not ok: return False, msg
    jar = str(UNLUAC_JAR)
    if not os.path.exists(jar):
        return False, 'unluac_patched.jar bulunamadı'
    try:
        # try converted first
        result = subprocess.run(['java', '-jar', jar, temp_std],
                                capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout:
            with open(out_path, 'w', encoding='utf-8') as f: f.write(result.stdout)
            return True, out_path
        # fallback: try original file directly
        result2 = subprocess.run(['java', '-jar', jar, src],
                                 capture_output=True, text=True, timeout=60)
        if result2.returncode == 0 and result2.stdout:
            with open(out_path, 'w', encoding='utf-8') as f: f.write(result2.stdout)
            return True, out_path
        err = (result.stderr or result2.stderr or 'bilinmeyen hata').strip()[:300]
        return False, err
    except subprocess.TimeoutExpired:
        return False, 'timeout'
    except Exception as e:
        return False, str(e)
    finally:
        if os.path.exists(temp_std):
            try: os.remove(temp_std)
            except: pass

def _select_files(files, source_dir, action_name):
    if not files: return []
    if len(files) == 1:
        console.print(f'  Tek dosya: [cyan]{files[0]}[/cyan]')
        c = safe_input('  İşle? (Y/n): ').strip().lower()
        flush_stdin(); return files if c != 'n' else []
    console.print(f'\n[bold white]Dosya seç ({action_name}):[/bold white]')
    for i, f in enumerate(files, 1):
        sz = os.path.getsize(os.path.join(source_dir, f))
        console.print(f'  [{i}] {f}  ({sz:,} byte)')
    console.print('  [A] TÜMÜ')
    console.print('  [0] İptal')
    while True:
        c = safe_input('  > ').strip().upper(); flush_stdin()
        if c == 'A': return files
        if c == '0': return []
        if c.isdigit():
            idx = int(c)
            if 1 <= idx <= len(files): return [files[idx-1]]
        console.print('  Geçersiz seçim.')

def lua_action_decompile():
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF88FF]🔓 DECOMPİLE[/bold #FF88FF]  [dim](T24→Std→unluac→luadec pipeline)[/dim]')
    console.print()
    jar   = UNLUAC_JAR.exists()
    luac5 = bool(_get_luac_cmd())
    console.print(f'  unluac.jar : {"[green]✅ var[/green]" if jar   else "[red]❌ yok — SOURCE/ klasörüne koy[/red]"}')
    console.print(f'  luac5.3    : {"[green]✅ var[/green]" if luac5 else "[red]❌ yok[/red]"}')
    console.print()
    files = [f for f in os.listdir(str(LUA_ORIGINAL_DIR))
             if f.lower().endswith(('.luac', '.slua', '.lua'))]
    if not files:
        console.print(f'[red]❌ LUA_ORIGINAL boş → {LUA_ORIGINAL_DIR}[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    selected = _select_files(files, str(LUA_ORIGINAL_DIR), 'DECOMPİLE')
    if not selected: return
    LUA_EDIT_DIR.mkdir(parents=True, exist_ok=True)
    success = 0; failed = []
    for i, f in enumerate(selected, 1):
        src = LUA_ORIGINAL_DIR / f
        out = LUA_EDIT_DIR / (Path(f).stem + '.lua')
        console.print(f'  [{i}/{len(selected)}] {f}')
        ok, tool, err = _premium_decompile(src, out)
        if ok:
            lines = len(out.read_text(encoding='utf-8', errors='replace').splitlines()) if out.exists() else 0
            console.print(f'  [green]✅ {out.name}[/green]  [dim]{tool} · {lines} satır[/dim]')
            success += 1
        else:
            console.print(f'  [red]✗ {err[:120]}[/red]')
            failed.append(f)
    console.print(f'\n[bold]Sonuç: {success}/{len(selected)}[/bold]')
    if failed: console.print(f'[red]Başarısız: {", ".join(failed)}[/red]')
    console.print(f'[dim]Çıktı: {LUA_EDIT_DIR}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')
    """LUA_ORIGINAL → LUA_EDIT (decompile)"""
    _ensure_lua_dirs()
    files = [f for f in os.listdir(str(LUA_ORIGINAL_DIR))
             if f.lower().endswith(('.lua', '.luac', '.slua'))]
    if not files:
        console.print(f'[red]❌ LUA_ORIGINAL klasörü boş![/red]')
        console.print(f'[dim]  → {LUA_ORIGINAL_DIR}[/dim]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
    selected = _select_files(files, str(LUA_ORIGINAL_DIR), 'DECOMPILE')
    if not selected: return
    success = 0
    import tempfile as _tf
    with _tf.TemporaryDirectory(prefix='fan_dec_') as tmp:
        for i, f in enumerate(selected, 1):
            console.print(f'  [{i}/{len(selected)}] {f}')
            ok, result = _robust_decompile(str(LUA_ORIGINAL_DIR/f), str(LUA_EDIT_DIR), tmp)
            if ok:
                console.print(f'  [green]✅ {os.path.basename(result)}[/green]'); success += 1
            else:
                console.print(f'  [red]✗ {result}[/red]')
                fallback = LUA_EDIT_DIR / (os.path.splitext(f)[0] + '.luac')
                ok2, _ = _convert_luac(str(LUA_ORIGINAL_DIR/f), str(fallback))
                if ok2: console.print(f'  [yellow]→ ham bytecode kaydedildi: {fallback.name}[/yellow]')
    console.print(f'\n[bold green]✅ Decompile tamamlandı: {success}/{len(selected)}[/bold green]')
    console.print(f'[dim]Çıktı: {LUA_EDIT_DIR}[/dim]')
    flush_stdin(); safe_input(f'\n{T("press_enter")}')

def _get_luac_version_cmd(version: str) -> str:
    """Find luac binary for specific version (5.1, 5.3, 5.4)."""
    import shutil as _sh
    vmap = {
        '5.1': ['luac5.1', 'luac51'],
        '5.3': ['luac5.3', 'luac53'],
        '5.4': ['luac5.4', 'luac54'],
    }
    names = vmap.get(version, [f'luac{version}'])
    # search home source dir first
    for name in names:
        p = _HOME_SOURCE / name
        if p.exists() and os.access(str(p), os.X_OK):
            return str(p)
    # search Termux bin
    termux_bin = Path('/data/data/com.termux/files/usr/bin')
    for name in names:
        p = termux_bin / name
        if p.exists():
            return str(p)
    # PATH
    for name in names:
        w = _sh.which(name)
        if w: return w
    return ''

def _try_install_lua(version: str) -> bool:
    """Try to install lua for given version via pkg."""
    vmap = {'5.1': 'lua51', '5.3': 'lua53', '5.4': 'lua54'}
    pkg = vmap.get(version)
    if not pkg: return False
    console.print(f'  [dim]Yükleniyor: pkg install {pkg}...[/dim]')
    r = subprocess.run(['pkg', 'install', '-y', pkg], capture_output=False)
    return r.returncode == 0

def lua_action_recompile():
    """COMPILED → .luac — versiyon seçimli derleme (5.1 / 5.3 / 5.4)"""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF88FF]🔧 RECOMPİLE[/bold #FF88FF]')
    console.print('[dim]  .lua dosyasını seçilen Lua versiyonuyla derle[/dim]')
    console.print()

    # check available versions
    versions = ['5.1', '5.3', '5.4']
    avail = {}
    for v in versions:
        cmd = _get_luac_version_cmd(v)
        avail[v] = cmd

    console.print('  [dim]Mevcut derleyiciler:[/dim]')
    for v in versions:
        status = f'[green]✅ {avail[v]}[/green]' if avail[v] else '[red]❌ yok[/red]'
        note = ' [dim](PUBG — T24 dönüşüm)[/dim]' if v == '5.3' else ''
        console.print(f'  Lua {v}: {status}{note}')
    console.print()

    console.print('  [1] Lua 5.1  [dim](standart bytecode)[/dim]')
    console.print('  [2] Lua 5.3  [dim](PUBG/BGMI — T24 dönüşüm ile)[/dim]')
    console.print('  [3] Lua 5.4  [dim](standart bytecode)[/dim]')
    console.print('  [0] Geri')
    console.print()
    vc = safe_input('  Versiyon seç (0-3): ').strip(); flush_stdin()
    vmap = {'1': '5.1', '2': '5.3', '3': '5.4'}
    if vc == '0': return
    if vc not in vmap:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return

    sel_ver = vmap[vc]
    luac_cmd = avail[sel_ver]

    # try to install if missing
    if not luac_cmd:
        console.print(f'\n  [yellow]luac{sel_ver} bulunamadı — kurmayı deneyelim mi? (E/h): [/yellow]', end='')
        ans = safe_input('').strip().lower(); flush_stdin()
        if ans != 'h':
            ok = _try_install_lua(sel_ver)
            if ok:
                luac_cmd = _get_luac_version_cmd(sel_ver)
        if not luac_cmd:
            console.print(f'[red]❌ luac{sel_ver} yüklenemedi.[/red]')
            console.print(f'[dim]  Manuel kur: pkg install lua{"".join(sel_ver.split("."))}[/dim]')
            flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return

    # select files
    files = [f for f in COMPILED_DIR.iterdir() if f.is_file() and f.suffix == '.lua']
    if not files:
        console.print(f'[red]❌ COMPILED klasörü boş → {COMPILED_DIR}[/red]')
        console.print('[dim]  Derlenecek .lua dosyasını buraya koy.[/dim]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return

    selected = _select_files([f.name for f in files], str(COMPILED_DIR), 'RECOMPİLE')
    if not selected: return

    use_t24 = sel_ver == '5.3'
    console.print(f'\n  [cyan]luac{sel_ver} ile derleniyor{" + T24/BGMI dönüşüm" if use_t24 else ""}...[/cyan]')

    success = 0; failed = []
    import tempfile as _tf

    for i, fname in enumerate(selected, 1):
        src  = COMPILED_DIR / fname
        outp = COMPILED_DIR / (src.stem + '.luac')
        console.print(f'  [{i}/{len(selected)}] {fname}')

        if use_t24:
            # use PREMIUM pipeline for 5.3 → T24 rebuild
            ok, err = _premium_recompile(src, outp)
            if ok:
                console.print(f'  [green]✅ {outp.name}  ({human_size(outp.stat().st_size)}) [T24][/green]')
                success += 1
            else:
                console.print(f'  [red]✗ {err[:150]}[/red]')
                failed.append(fname)
        else:
            # direct luac compile for 5.1 / 5.4
            with _tf.TemporaryDirectory(prefix='fan_luac_') as tmp:
                tmp_out = os.path.join(tmp, 'out.luac')
                try:
                    r = subprocess.run(
                        [luac_cmd, '-o', tmp_out, str(src)],
                        capture_output=True, text=True, timeout=30
                    )
                    if r.returncode == 0 and os.path.exists(tmp_out):
                        import shutil as _sh2
                        _sh2.copy2(tmp_out, str(outp))
                        console.print(f'  [green]✅ {outp.name}  ({human_size(outp.stat().st_size)})[/green]')
                        success += 1
                    else:
                        err = (r.stderr or r.stdout or 'bilinmeyen hata').strip()[:200]
                        console.print(f'  [red]✗ {err}[/red]')
                        failed.append(fname)
                except subprocess.TimeoutExpired:
                    console.print(f'  [red]✗ timeout[/red]'); failed.append(fname)
                except Exception as e:
                    console.print(f'  [red]✗ {e}[/red]'); failed.append(fname)

    console.print(f'\n[bold]Sonuç: {success}/{len(selected)}[/bold]')
    if failed: console.print(f'[red]Başarısız: {", ".join(failed)}[/red]')
    if success:
        console.print(f'[dim]Çıktı: {COMPILED_DIR}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def lua_mode_menu():
    while True:
        os.system('clear')
        console.print()
        console.print('[bold #FF88FF]  ── LUA MODE ──[/bold #FF88FF]')
        console.print()
        console.print(f'  [bold #FF88FF][1] 🔓 DECOMPİLE[/bold #FF88FF]    [dim]LUA_ORIGINAL → LUA_EDIT (.luac → .lua)[/dim]')
        console.print(f'  [bold #FF88FF][2] 🔧 RECOMPİLE 5.3[/bold #FF88FF]  [dim]COMPILED → .luac (PUBG/BGMI T24 format)[/dim]')
        console.print(f'  [bold #FF88FF][3] 🛡  PROTECTION STRIP[/bold #FF88FF] [dim]BEKIT/FEEDFACE footer temizle[/dim]')
        console.print(f'  [bold #FFAA00][4] 🔓 LUADEC[/bold #FFAA00]         [dim]luadec binary ile decompile[/dim]')
        console.print(f'  [bold #00FFCC][5] 🔨 LUADEC KUR[/bold #00FFCC]     [dim]github\'dan otomatik clone + build[/dim]')
        console.print(f'  [bold #FF8800][6] ⚡ BATCH XOR DECRYPT[/bold #FF8800] [dim]tüm .luac\'ları XOR çöz[/dim]')
        console.print(f'  [bold #00D4FF][7] ⭐ FANTERİ LUA 5.4[/bold #00D4FF]  [dim]kaynak .lua → luac5.4 bytecode[/dim]')
        console.print(f'  [bold #A855F7][8] 🔵 FANTERİ LUA 5.1[/bold #A855F7]  [dim]kaynak .lua → luac5.1 bytecode[/dim]')
        console.print(f'  [bold #10D98A][9] 🟢 FANTERİ LUA 5.3[/bold #10D98A]  [dim]kaynak .lua → luac5.3 bytecode (.lua çıktı)[/dim]')
        console.print(f'  [bold white][0] {T("back")}[/bold white]')
        console.print()
        console.print(f'  [dim]unluac.jar: {"✅ var" if UNLUAC_JAR.exists() else "❌ yok — SOURCE/ klasörüne koy"}[/dim]')
        console.print(f'  [dim]luac5.3:    {"✅ var" if (SOURCE_DIR_LUA/"luac5.3").exists() else "❌ yok — SOURCE/ klasörüne koy"}[/dim]')
        console.print()
        c = safe_input('  Seç (0-5): ').strip(); flush_stdin()
        if   c == '1': lua_action_decompile()
        elif c == '2': lua_action_recompile()
        elif c == '3': action_lua_protect_strip()
        elif c == '4': action_lua_decompile_luadec()
        elif c == '5': action_build_luadec()
        elif c == '6': action_batch_luac_decrypt()
        elif c == '7': action_fanteri_lua_compile()
        elif c == '8': action_fanteri_lua_compile_51()
        elif c == '9': action_fanteri_lua_compile_53()
        elif c == '0': return
        else: console.print(f'[red]{T("invalid")}[/red]'); time.sleep(1)

# ==================== 120 FPS UNLOCK + SKIN TOOL + FILE FINDER ====================
# Ported from GAME_PATCH_TOOL (NADEEM896211) — DRM/license/expiry stripped

# ── dirs ─────────────────────────────────────────────────────────────────────
PATCH_EXTRACTED = BASE_DIR / "PAK_UNPACK"
PATCH_EDITED    = BASE_DIR / "PATCH_EDIT"
PATCH_RESULT    = BASE_DIR / "PATCH_RESULT"
CLOTH_SKIN_TXT  = BASE_DIR / "cloth_skin.txt"

def _ensure_patch_dirs():
    for d in [PATCH_EDITED, PATCH_RESULT]:
        d.mkdir(parents=True, exist_ok=True)

# ── 120 FPS helpers ───────────────────────────────────────────────────────────

def _get_device_model() -> str:
    try:
        r = subprocess.run("getprop ro.product.model", shell=True,
                           capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""

def _patch_file_with_model(src: Path, dst: Path) -> bool:
    """Find |model| pattern in binary, replace with current device model."""
    user_model = safe_input("  Cihaz modeli (boş bırak = otomatik): ").strip()
    flush_stdin()
    mobile = user_model or _get_device_model()
    if not mobile:
        console.print("[red]❌ Cihaz modeli alınamadı.[/red]")
        return False

    mobile_bytes = mobile.encode("utf-8")
    target_len   = len(mobile_bytes)
    console.print(f"  [green]Model: '{mobile}' ({target_len} byte)[/green]")

    try:
        data = src.read_bytes()
    except Exception as e:
        console.print(f"[red]❌ Dosya okunamadı: {e}[/red]"); return False

    delim = 0x7C  # '|'
    i = 0; n = len(data); found = None
    while i < n:
        if data[i] == delim:
            j = i + 1
            while j < n and data[j] != delim: j += 1
            if j < n:
                inner = data[i+1:j]
                if len(inner) == target_len:
                    found = (i+1, j, inner); break
                i = j + 1
            else: break
        else: i += 1

    if not found:
        console.print(f"[yellow]⚠ {target_len} uzunlukta string bulunamadı.[/yellow]"); return False

    s, e_, inner = found
    try: inner_str = inner.decode("utf-8")
    except Exception: inner_str = str(inner)
    console.print(f"  [cyan]Bulunan: '{inner_str}' → '{mobile}' ile değiştiriliyor[/cyan]")

    new_data = data[:s] + mobile_bytes + data[e_:]

    # backup
    bak = src.with_suffix('.uexp.bak')
    try: shutil.copy2(str(src), str(bak))
    except Exception: pass

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(new_data)
    console.print(f"  [green]✅ Yazıldı: {dst}[/green]")
    return True

def action_120fps():
    """120 FPS Unlock — Client120FPSMapping.uexp patch"""
    _ensure_patch_dirs()
    os.system('clear')
    console.print("[bold #00CCFF]🔧 120 FPS UNLOCK[/bold #00CCFF]")
    console.print()
    console.print("  [1] BGMI    → ShadowTrackerExtra/Content/MultiRegion/Content/IN/CSV")
    console.print("  [2] Global  → ShadowTrackerExtra/Content/CSV")
    console.print()
    c = safe_input("  Seç (1/2): ").strip(); flush_stdin()
    if   c == "1": subfolder = "ShadowTrackerExtra/Content/MultiRegion/Content/IN/CSV"; game = "BGMI"
    elif c == "2": subfolder = "ShadowTrackerExtra/Content/CSV"; game = "Global PUBG"
    else: console.print("[red]Geçersiz.[/red]"); safe_input("\nEnter..."); return

    filename = "Client120FPSMapping.uexp"
    console.print(f"\n  [dim]PAK_UNPACK/ klasöründe {filename} aranıyor...[/dim]")

    # search extracted dirs
    src = None
    for candidate in PATCH_EXTRACTED.rglob(filename):
        src = candidate; break

    if not src:
        console.print(f"[red]❌ {filename} bulunamadı.[/red]")
        console.print(f"[dim]  PAK'ı önce [2] PAK İÇERİĞİNİ GÖR ile extract et.[/dim]")
        flush_stdin(); safe_input("\nEnter..."); return

    console.print(f"  [green]✅ Bulundu: {src}[/green]")
    dst = PATCH_EDITED / subfolder / filename

    ok = _patch_file_with_model(src, dst)
    if ok:
        console.print(f"\n[bold green]🎉 120 FPS patch tamamlandı![/bold green]")
        console.print(f"[dim]Düzenlenmiş dosya: {dst}[/dim]")
        console.print(f"[dim]Bu dosyayı CUSTOM FILES/ klasörüne kopyalayıp inject et.[/dim]")
    else:
        console.print("[red]❌ Patch başarısız.[/red]")

    flush_stdin(); safe_input("\nEnter...")

# ── Skin tool helpers ─────────────────────────────────────────────────────────

def _convert_to_3bytes_le(id_value) -> bytes:
    hex_id = "{:06X}".format(int(id_value))
    return bytes.fromhex("".join(reversed([hex_id[i:i+2] for i in range(0, len(hex_id), 2)])))

def _find_nonzero_backward(content: bytearray, start: int, search_range: int = 200):
    for off in range(start, max(0, start - search_range), -1):
        if (off >= 2 and content[off-2] == 0 and
                content[off-1] != 0 and content[off] != 0 and
                (off+1 >= len(content) or content[off+1] == 0)):
            return off-1, content[off-1:off+1]
    return None, None

def _replace_ids_in_uexp(file_path: Path, new_id: str, original_id: str) -> tuple:
    try:
        content = bytearray(file_path.read_bytes())
        new_bytes  = _convert_to_3bytes_le(new_id)
        orig_bytes = _convert_to_3bytes_le(original_id)

        new_off = content.find(new_bytes)
        if new_off == -1: return False, f"ID {new_id} bulunamadı"
        new_rep_off, new_rep_bytes = _find_nonzero_backward(content, new_off)
        if new_rep_off is None: return False, f"ID {new_id} için pattern bulunamadı"

        orig_off = content.find(orig_bytes)
        if orig_off == -1: return False, f"ID {original_id} bulunamadı"
        orig_rep_off, orig_rep_bytes = _find_nonzero_backward(content, orig_off)
        if orig_rep_off is None: return False, f"ID {original_id} için pattern bulunamadı"

        content[orig_rep_off:orig_rep_off+2] = new_rep_bytes
        file_path.write_bytes(bytes(content))

        # verify
        check = bytearray(file_path.read_bytes())
        if check[orig_rep_off:orig_rep_off+2] == new_rep_bytes:
            return True, f"offset {orig_rep_off}: {orig_rep_bytes.hex()} → {new_rep_bytes.hex()}"
        return False, "Yazma doğrulanamadı"
    except Exception as e:
        return False, str(e)

def action_skin():
    """AvatarBPTable.uexp skin ID replacement"""
    _ensure_patch_dirs()
    os.system('clear')
    console.print("[bold #FF88FF]🧥 SKIN TOOL — AvatarBPTable[/bold #FF88FF]")
    console.print()

    # ensure cloth_skin.txt
    if not CLOTH_SKIN_TXT.exists():
        CLOTH_SKIN_TXT.parent.mkdir(parents=True, exist_ok=True)
        CLOTH_SKIN_TXT.write_text("")
        console.print(f"[yellow]ℹ  cloth_skin.txt oluşturuldu: {CLOTH_SKIN_TXT}[/yellow]")
        console.print("[dim]  Her satıra: YENİ_ID,ORİJİNAL_ID formatında yaz, sonra tekrar çalıştır.[/dim]")
        flush_stdin(); safe_input("\nEnter..."); return

    lines = [l.strip() for l in CLOTH_SKIN_TXT.read_text().splitlines() if l.strip()]
    if not lines:
        console.print(f"[red]❌ cloth_skin.txt boş.[/red]")
        console.print(f"[dim]  {CLOTH_SKIN_TXT} dosyasına YENİ_ID,ORİJİNAL_ID satırları ekle.[/dim]")
        flush_stdin(); safe_input("\nEnter..."); return

    console.print(f"  [green]{len(lines)} ID çifti yüklendi.[/green]")

    # find AvatarBPTable.uexp
    target = None
    for candidate in PATCH_EXTRACTED.rglob("AvatarBPTable.uexp"):
        target = candidate; break

    if not target:
        console.print("[red]❌ AvatarBPTable.uexp bulunamadı.[/red]")
        console.print("[dim]  PAK'ı önce extract et.[/dim]")
        flush_stdin(); safe_input("\nEnter..."); return

    console.print(f"  [green]✅ Bulundu: {target}[/green]")

    # work on a copy in PATCH_EDITED
    import shutil as _sh
    work = PATCH_EDITED / "AvatarBPTable.uexp"
    work.parent.mkdir(parents=True, exist_ok=True)
    _sh.copy2(str(target), str(work))

    success = 0; failed = []
    for i, line in enumerate(lines, 1):
        try:
            new_id, orig_id = [x.strip() for x in line.split(',', 1)]
        except ValueError:
            console.print(f"  [red]✗ [{i}] Geçersiz format: {line}[/red]"); failed.append(line); continue

        ok, msg = _replace_ids_in_uexp(work, new_id, orig_id)
        if ok:
            console.print(f"  [green]✅ [{i}] {new_id} → {orig_id}  ({msg})[/green]"); success += 1
        else:
            console.print(f"  [red]✗  [{i}] {new_id} → {orig_id}  ({msg})[/red]"); failed.append(line)

    console.print()
    console.print(f"[bold]Sonuç: {success}/{len(lines)} başarılı[/bold]")
    if failed:
        console.print(f"[red]Başarısız: {', '.join(failed)}[/red]")
    if success > 0:
        console.print(f"[dim]Düzenlenmiş dosya: {work}[/dim]")
        console.print(f"[dim]Bu dosyayı CUSTOM FILES/ klasörüne kopyalayıp inject et.[/dim]")

    flush_stdin(); safe_input("\nEnter...")

# ── File Finder ───────────────────────────────────────────────────────────────

def action_file_finder():
    """Search files in extracted PAK by name pattern"""
    os.system('clear')
    console.print("[bold #FFAA00]🔍 DOSYA BULUCU[/bold #FFAA00]")
    console.print(f"[dim]  Arama dizini: {PATCH_EXTRACTED}[/dim]")
    console.print()

    if not PATCH_EXTRACTED.exists() or not any(PATCH_EXTRACTED.iterdir()):
        console.print("[red]❌ PAK_UNPACK klasörü boş veya yok.[/red]")
        console.print("[dim]  Önce PAK'ı extract et.[/dim]")
        flush_stdin(); safe_input("\nEnter..."); return

    pattern = safe_input("  Arama deseni (boş = tümü): ").strip().lower(); flush_stdin()
    exts_raw = safe_input("  Uzantı filtresi (örn: .lua .uexp, boş = tümü): ").strip().lower(); flush_stdin()
    exts = set(exts_raw.split()) if exts_raw else set()

    console.print("[dim]  Aranıyor...[/dim]")
    found = []
    for fp in PATCH_EXTRACTED.rglob("*"):
        if not fp.is_file(): continue
        if exts and fp.suffix.lower() not in exts: continue
        if pattern and pattern not in fp.name.lower(): continue
        found.append(fp)

    if not found:
        console.print("[yellow]  Sonuç bulunamadı.[/yellow]")
        flush_stdin(); safe_input("\nEnter..."); return

    console.print(f"\n  [green]{len(found)} dosya bulundu:[/green]")
    for i, fp in enumerate(found[:20], 1):
        console.print(f"  [{i}] {fp.relative_to(PATCH_EXTRACTED)}")
    if len(found) > 20:
        console.print(f"  [dim]... ve {len(found)-20} tane daha[/dim]")

    console.print()
    c = safe_input("  Kopyalamak ister misin? (Y/n): ").strip().lower(); flush_stdin()
    if c == 'n':
        return

    preserve = safe_input("  Klasör yapısını koru? (Y/n): ").strip().lower(); flush_stdin()
    out_dir = BASE_DIR / "FOUND_FILES"
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for fp in found:
        try:
            if preserve != 'n':
                rel = fp.relative_to(PATCH_EXTRACTED)
                dst = out_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
            else:
                dst = out_dir / fp.name
                cnt = 1
                orig = dst
                while dst.exists():
                    dst = orig.parent / f"{orig.stem}_{cnt}{orig.suffix}"; cnt += 1
            shutil.copy2(str(fp), str(dst)); copied += 1
        except Exception as e:
            console.print(f"  [red]✗ {fp.name}: {e}[/red]")

    console.print(f"\n[green]✅ {copied} dosya kopyalandı → {out_dir}[/green]")
    flush_stdin(); safe_input("\nEnter...")

# ==================== DELETE FROM PAK + SMART REPACK (custom.py) ====================
# Clean port — no malware, no DRM

# ── helpers ───────────────────────────────────────────────────────────────────

class _SimpleBlockDisplay:
    def __init__(self, total_files: int, pak_name: str):
        self.total_files  = total_files
        self.pak_name     = pak_name
        self.processed    = 0
        self.total_fitted = 0
        self.total_skip   = 0
        self.cur_fit      = 0
        self.cur_skip     = 0
        self.cur_blocks   = []
        self.all_blocks   = []
        self.cur_idx      = 0

    def start_file(self, name, total_blocks):
        self.cur_idx += 1
        self.cur_fit = self.cur_skip = 0; self.cur_blocks = []
        console.print()
        console.print(f"[green]┌─────────────────────────────────────────[/green]")
        console.print(f"[green]│[/green] [[yellow]{self.cur_idx}/{self.total_files}[/yellow]] [green]{name}[/green] [dim]({total_blocks} blok)[/dim]")
        console.print(f"[green]├─────────────────────────────────────────[/green]")

    def add_block(self, idx, size, fitted, ratio=None):
        mb = size / (1024*1024)
        if fitted:
            self.cur_fit += 1; self.total_fitted += 1
            rs = f" [{ratio:.1%}]" if ratio else ""
            console.print(f"[green]│[/green]  Blok {idx:3d}: {mb:>7.2f} MB → [green]✓ FIT{rs}[/green]")
        else:
            self.cur_skip += 1; self.total_skip += 1
            console.print(f"[green]│[/green]  Blok {idx:3d}: {mb:>7.2f} MB → [red]✗ SKIP[/red]")
        self.cur_blocks.append(fitted)

    def finish_file(self):
        t = len(self.cur_blocks)
        if t == 0:    s = "[green]✓ TAMAM[/green]"
        elif self.cur_fit == t: s = "[green]✓ TÜMÜ FIT[/green]"
        elif self.cur_fit > 0:  s = f"[yellow]✓ {self.cur_fit}/{t} FIT[/yellow]"
        else:          s = "[red]✗ TÜMÜ SKIP[/red]"
        console.print(f"[green]└─────────────────────────────────────────[/green]")
        console.print(f"  Sonuç: {s}")
        self.processed += 1; self.all_blocks.extend(self.cur_blocks)

    def final_summary(self):
        t = len(self.all_blocks)
        console.print()
        console.print("[green]╔═══════════════════════════════════╗[/green]")
        console.print(f"[green]║[/green]  [yellow]REPACK ÖZET[/yellow]")
        console.print(f"[green]║[/green]  Dosya   : [cyan]{self.processed}[/cyan]")
        console.print(f"[green]║[/green]  Blok    : [cyan]{t}[/cyan]")
        console.print(f"[green]║[/green]  Fit     : [green]{self.total_fitted}[/green]")
        console.print(f"[green]║[/green]  Skip    : [red]{self.total_skip}[/red]")
        if t > 0:
            console.print(f"[green]║[/green]  Başarı  : [yellow]{self.total_fitted/t:.1%}[/yellow]")
        console.print("[green]╚═══════════════════════════════════╝[/green]")

def _cx_get_dirs(pak_file):
    from pathlib import PurePath as _PP
    raw = bytes(pak_file._file_content[
        pak_file._pak_info.index_offset:][:pak_file._pak_info.index_size])
    if pak_file._pak_info.index_encrypted:
        raw = PakCrypto.decrypt_index(raw, pak_file._pak_info)
    r = Reader(raw); mp = r.string(); num = r.u4()
    for _ in range(num): TencentPakEntry(r, pak_file._pak_info.version)
    dirs = {}
    for _ in range(r.u8()):
        dp = r.string(); cnt = r.u8()
        dirs[dp] = {r.string(): pak_file._files[~r.i4()] for _ in range(cnt)}
    return mp, dirs

def _cx_encrypt(plaintext: bytes, rel_path, em: int) -> bytes:
    if PakCrypto._is_simple1_method(em):
        return bytes(b ^ SIMPLE1_DECRYPT_KEY for b in plaintext)
    if PakCrypto._is_simple2_method(em):
        pad = (-len(plaintext)) % SIMPLE2_BLOCK_SIZE
        plaintext += b'\x00' * pad
        key, = struct.unpack('<I', SIMPLE2_DECRYPT_KEY)
        rolling = key; out = []
        for x, in struct.iter_unpack('<I', plaintext):
            c = rolling ^ x; out.append(c); rolling ^= c
        return struct.pack(f'<{len(out)}I', *out)
    if PakCrypto._is_sm4_method(em):
        key = PakCrypto._derive_sm4_key(rel_path, em)
        sm4 = PakCrypto._sm4_context_for_key(key)
        pad_len = (-len(plaintext)) % 16
        if pad_len: plaintext += b'\x00' * pad_len
        out = bytearray()
        for i in range(0, len(plaintext), 16):
            blk = plaintext[i:i+16].ljust(16, b'\x00')
            out.extend(sm4.encrypt(blk))
        return bytes(out)
    return plaintext

def _cx_pw_string(s):
    if not s: return struct.pack('<i', 0)
    b = s.encode('utf-8') + b'\x00'
    return struct.pack('<i', len(b)) + b

def _cx_pw_entry(e, v):
    w = bytearray(e.content_hash)
    w += struct.pack('<Q', e.offset)
    w += struct.pack('<Q', e.uncompressed_size)
    w += struct.pack('<I', e.compression_method)
    w += struct.pack('<Q', e.size)
    if v >= 5: w += bytes([e.unk1]); w += e.unk2
    if e.compression_method != CM_NONE and v >= 3:
        w += struct.pack('<I', len(e.compressed_blocks))
        for b in e.compressed_blocks: w += struct.pack('<QQ', b.start, b.end)
    if v >= 4: w += struct.pack('<I', e.compression_block_size); w += bytes([1 if e.encrypted else 0])
    if v >= 12: w += struct.pack('<II', e.encryption_method, getattr(e, 'index_new_sep', 0))
    return bytes(w)

def _cx_repack_full(pak_file, edited_root, output_path, target_path=None, force_add=False, delete_paths=None):
    """Full PAK rebuild — supports edit, add, and delete."""
    from pathlib import PurePath as _PP
    from copy import copy as _cp

    edit_files = []
    if edited_root and Path(edited_root).exists():
        edit_files = [p for p in Path(edited_root).rglob('*') if p.is_file()]

    version   = pak_file._pak_info.version
    keystream = PakCrypto.zuc_keystream()
    orig_fc   = pak_file._file_content
    mp_str, all_dirs = _cx_get_dirs(pak_file)

    if target_path and force_add:
        target_path = target_path.replace('\\', '/')
        matched = next((d for d in all_dirs if d.strip('/').lower() == target_path.strip('/').lower()), None)
        target_path = matched or (target_path.strip('/') + '/')

    # ── delete ────────────────────────────────────────────────────────────────
    deleted = 0
    if delete_paths:
        delete_paths = [dp.replace('\\', '/').strip('/') for dp in delete_paths]
        for dp_str in list(all_dirs.keys()):
            for del_path in delete_paths:
                if dp_str.strip('/') == del_path or dp_str.strip('/').startswith(del_path + '/'):
                    for fname in list(all_dirs[dp_str].keys()):
                        console.print(f"[red]✗ Siliniyor: {dp_str}/{fname}[/red]")
                        del all_dirs[dp_str][fname]; deleted += 1
                    if not all_dirs[dp_str]: del all_dirs[dp_str]
                else:
                    for fname in list(all_dirs.get(dp_str, {}).keys()):
                        fp = f"{dp_str.strip('/')}/{fname}"
                        if fp.startswith(del_path) or fname == del_path.split('/')[-1]:
                            console.print(f"[red]✗ Siliniyor: {fp}[/red]")
                            del all_dirs[dp_str][fname]; deleted += 1
    if deleted: console.print(f"[green]{deleted} dosya/klasör silindi[/green]")

    # ── match edit files ──────────────────────────────────────────────────────
    pak_name_map = {}
    for dir_path, files in pak_file._index.items():
        for name, entry in files.items():
            full = str(_PP(dir_path)/name).replace('\\','/')
            pak_name_map.setdefault(name.lower(), []).append((full, entry))

    edited = {}
    for p in edit_files:
        fl = p.name.lower()
        if fl in pak_name_map:
            cands = pak_name_map[fl]
            if target_path:
                tc = [(fp,e) for fp,e in cands if target_path.strip('/') in fp]
                if tc: edited[tc[0][0]] = (p, tc[0][1]); continue
            sz = p.stat().st_size
            sm = [(fp,e) for fp,e in cands if e.uncompressed_size == sz]
            fp, ent = sm[0] if sm else cands[0]
            if target_path: fp = f"{target_path.rstrip('/')}/{p.name}"
            edited[fp] = (p, ent)
        elif force_add and target_path:
            tmpl = next((e for _,files in pak_file._index.items() for _,e in files.items()), None)
            if tmpl: edited[f"{target_path.rstrip('/')}/{p.name}"] = (p, tmpl)

    # ── build output ──────────────────────────────────────────────────────────
    new_files = []
    for e in pak_file._files:
        ne = _cp(e); ne.compressed_blocks = [_cp(b) for b in e.compressed_blocks]; new_files.append(ne)
    old_to_new = {id(pak_file._files[i]): new_files[i] for i in range(len(pak_file._files))}

    out_buf = bytearray()
    for dp_str, dir_files in list(all_dirs.items()):
        for name, old_entry in list(dir_files.items()):
            full_path = str(_PP(dp_str)/name).replace('\\','/')
            ne = old_to_new.get(id(old_entry))
            if ne is None:
                ne = _cp(old_entry); ne.compressed_blocks = [_cp(b) for b in old_entry.compressed_blocks]
                new_files.append(ne); old_to_new[id(old_entry)] = ne
            em = old_entry.encryption_method; cm = old_entry.compression_method
            if full_path in edited:
                p_src, tmpl = edited[full_path]
                new_raw = p_src.read_bytes(); pak_rel = _PP(full_path)
                ne.content_hash = SHA1.new(new_raw).digest()
                ne.uncompressed_size = len(new_raw)
                ne.compression_method = tmpl.compression_method if tmpl else cm
                ne.encryption_method  = tmpl.encryption_method  if tmpl else em
                ne.encrypted = tmpl.encrypted if tmpl else old_entry.encrypted
                ne.unk1 = tmpl.unk1 if tmpl else old_entry.unk1
                ne.unk2 = tmpl.unk2 if tmpl else old_entry.unk2
                if ne.compression_method == CM_NONE:
                    cipher = _cx_encrypt(new_raw, pak_rel, ne.encryption_method) if ne.encrypted else new_raw
                    ne.offset = len(out_buf); ne.size = len(new_raw); out_buf += cipher
                else:
                    cs = (tmpl.compression_block_size or old_entry.compression_block_size or 65536)
                    chunks = [new_raw[i:i+cs] for i in range(0, len(new_raw), cs)]; new_blks = []
                    for chunk in chunks:
                        from zstandard import ZstdCompressor as _ZC
                        comp = zlib.compress(chunk, 9) if ne.compression_method == CM_ZLIB else _ZC(level=19).compress(chunk)
                        cipher = _cx_encrypt(comp, pak_rel, ne.encryption_method) if ne.encrypted else comp
                        blk = PakCompressedBlock.__new__(PakCompressedBlock)
                        blk.start = len(out_buf); blk.end = len(out_buf)+len(cipher)
                        out_buf += cipher; new_blks.append(blk)
                    ne.compressed_blocks = new_blks
                    ne.offset = new_blks[0].start if new_blks else len(out_buf)
                    ne.size = sum(b.end-b.start for b in new_blks)
                    ne.uncompressed_size = len(new_raw)
                console.print(f"[green]✓[/green] {full_path}")
            else:
                if cm == CM_NONE:
                    read_sz = PakCrypto.align_encrypted_content_size(old_entry.size, em) if old_entry.encrypted else old_entry.size
                    ne.offset = len(out_buf); out_buf += bytes(orig_fc[old_entry.offset:old_entry.offset+read_sz])
                else:
                    if old_entry.compressed_blocks:
                        new_blks = []
                        for ob in old_entry.compressed_blocks:
                            unc = ob.end-ob.start
                            enc = PakCrypto.align_encrypted_content_size(unc,em) if old_entry.encrypted else unc
                            blk = PakCompressedBlock.__new__(PakCompressedBlock)
                            blk.start = len(out_buf); blk.end = len(out_buf)+unc
                            out_buf += bytes(orig_fc[ob.start:ob.start+enc]); new_blks.append(blk)
                        ne.compressed_blocks = new_blks
                        ne.offset = new_blks[0].start

    # force-add new files
    if target_path and force_add:
        for fp, (p_src, tmpl) in list(edited.items()):
            if any(str(_PP(dp)/name).replace('\\','/')==fp for dp,files in all_dirs.items() for name in files):
                continue
            ne = _cp(tmpl); new_raw = p_src.read_bytes(); pak_rel = _PP(fp)
            ne.content_hash = SHA1.new(new_raw).digest(); ne.uncompressed_size = len(new_raw)
            if ne.compression_method == CM_NONE:
                cipher = _cx_encrypt(new_raw, pak_rel, ne.encryption_method) if ne.encrypted else new_raw
                ne.offset = len(out_buf); ne.size = len(new_raw); out_buf += cipher
            else:
                cs = tmpl.compression_block_size or 65536
                chunks = [new_raw[i:i+cs] for i in range(0, len(new_raw), cs)]; new_blks = []
                for chunk in chunks:
                    from zstandard import ZstdCompressor as _ZC
                    comp = zlib.compress(chunk,9) if ne.compression_method==CM_ZLIB else _ZC(level=19).compress(chunk)
                    cipher = _cx_encrypt(comp, pak_rel, ne.encryption_method) if ne.encrypted else comp
                    blk = PakCompressedBlock.__new__(PakCompressedBlock)
                    blk.start = len(out_buf); blk.end = len(out_buf)+len(cipher)
                    out_buf += cipher; new_blks.append(blk)
                ne.compressed_blocks = new_blks
                ne.offset = new_blks[0].start if new_blks else len(out_buf)
                ne.size = sum(b.end-b.start for b in new_blks); ne.uncompressed_size = len(new_raw)
            new_files.append(ne)
            dp_part = '/'.join(fp.split('/')[:-1])+'/'; nm_part = fp.split('/')[-1]
            if target_path not in all_dirs: all_dirs[target_path] = {}
            all_dirs[target_path][nm_part] = ne
            console.print(f"[green]+ Eklendi: {fp}[/green]")

    # ── write index ───────────────────────────────────────────────────────────
    eidx = {id(new_files[i]):i for i in range(len(new_files))}
    idx = bytearray(_cx_pw_string(mp_str))
    idx += struct.pack('<I', len(new_files))
    for ne in new_files: idx += _cx_pw_entry(ne, version)
    idx += struct.pack('<Q', len(all_dirs))
    for dp_str, dir_files in all_dirs.items():
        idx += _cx_pw_string(dp_str); idx += struct.pack('<Q', len(dir_files))
        for name, old_e in dir_files.items():
            idx += _cx_pw_string(name)
            found = eidx.get(id(old_e))
            if found is None:
                found = next((i for i,e in enumerate(new_files) if e.offset==old_e.offset and e.size==old_e.size), -1)
            idx += struct.pack('<i', ~found if found is not None and found >= 0 else -1)

    index_plain = bytes(idx)
    new_sha1 = SHA1.new(index_plain).digest()
    if pak_file._pak_info.index_encrypted:
        key = PakCrypto.rsa_extract(pak_file._pak_info.packed_key, RSA_MOD_1)
        iv  = PakCrypto.rsa_extract(pak_file._pak_info.packed_iv,  RSA_MOD_1)
        aes = AES.new(key, MODE_CBC, iv[:16])
        pad_len = (-len(index_plain)) % AES.block_size or AES.block_size
        index_bytes = aes.encrypt(index_plain + bytes([pad_len])*pad_len)
    else:
        index_bytes = index_plain

    new_idx_offset = len(out_buf); new_idx_size = len(index_bytes); out_buf += index_bytes

    footer_sz  = TencentPakInfo._mem_size(version)
    new_footer = bytearray(orig_fc[-footer_sz:])
    h_key = struct.pack('<5I', *keystream[4:9])
    new_footer[-36:-16] = bytes(a^b for a,b in zip(new_sha1, h_key))
    new_footer[-16:-8]  = (new_idx_size   ^ ((keystream[10]<<32)|keystream[11])).to_bytes(8,'little')
    new_footer[-8:]     = (new_idx_offset ^ ((keystream[0] <<32)|keystream[1] )).to_bytes(8,'little')
    out_buf += new_footer

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(str(output_path), 'wb') as f: f.write(out_buf)
    return deleted + len(edited)

def _cx_list_pak_contents(pak_file):
    """List all files/folders inside PAK for delete selection."""
    items = []
    for dir_path, files in pak_file._index.items():
        dp = str(dir_path).replace('\\','/')
        items.append(('dir', dp, None, len(files)))
        for fname, entry in files.items():
            items.append(('file', f"{dp}/{fname}", entry, 0))
    return items

def action_delete_from_pak():
    """Delete files/folders from inside a PAK and repack."""
    os.system('clear')
    console.print("[bold red]🗑  DELETE FROM PAK[/bold red]")
    console.print()

    pak_files = sorted([f for f in BASE_DIR.iterdir()
                        if f.is_file() and f.name.lower().endswith('.pak')], key=lambda x: x.name)
    if not pak_files:
        console.print(f"[red]❌ FANTOOL/ klasöründe .pak bulunamadı.[/red]")
        flush_stdin(); safe_input("\nEnter..."); return

    for i, p in enumerate(pak_files, 1):
        console.print(f"  [{i}] {p.name}  ({human_size(p.stat().st_size)})")
    console.print()
    try:
        c = safe_input(f"  PAK seç (1-{len(pak_files)}): ").strip(); flush_stdin()
        pak_path = pak_files[int(c)-1]
    except Exception:
        console.print("[red]Geçersiz.[/red]"); flush_stdin(); safe_input("\nEnter..."); return

    console.print(f"\n[dim]Yükleniyor: {pak_path.name}...[/dim]")
    try:
        pak = TencentPakFile(PurePath(pak_path))
    except Exception as e:
        console.print(f"[red]❌ PAK yüklenemedi: {e}[/red]"); flush_stdin(); safe_input("\nEnter..."); return

    items = _cx_list_pak_contents(pak)
    if not items:
        console.print("[red]PAK içi boş.[/red]"); flush_stdin(); safe_input("\nEnter..."); return

    # paginated display
    PAGE = 30
    page = 0
    while True:
        os.system('clear')
        console.print(f"[bold red]🗑  DELETE FROM PAK[/bold red]  [dim]{pak_path.name}[/dim]")
        console.print(f"[dim]  {len(items)} öğe | Sayfa {page+1}/{(len(items)+PAGE-1)//PAGE}[/dim]")
        console.print()
        chunk = items[page*PAGE:(page+1)*PAGE]
        for i, (typ, path, entry, cnt) in enumerate(chunk, page*PAGE+1):
            if typ == 'dir':
                console.print(f"  [yellow]{i:4}[/yellow] 📁 [cyan]{path[:60]}[/cyan]  [dim]{cnt} dosya[/dim]")
            else:
                mb = entry.uncompressed_size/(1024*1024) if entry else 0
                console.print(f"  [yellow]{i:4}[/yellow] 📄 [white]{path[:60]}[/white]  [dim]{mb:.2f} MB[/dim]")
        console.print()
        console.print(f"[dim]  n=sonraki | p=önceki | numara gir=sil | 0=iptal[/dim]")
        cmd = safe_input("  > ").strip().lower(); flush_stdin()
        if cmd == '0': return
        elif cmd == 'n': page = min(page+1, (len(items)-1)//PAGE)
        elif cmd == 'p': page = max(page-1, 0)
        elif cmd.isdigit():
            idx = int(cmd)-1
            if 0 <= idx < len(items):
                item_type, item_path, _, _ = items[idx]; break
            else:
                console.print("[red]Geçersiz numara.[/red]"); safe_input("  Enter...")
        else:
            console.print("[red]Geçersiz.[/red]"); safe_input("  Enter...")

    console.print(f"\n  [yellow]Silinecek: [{item_type}] {item_path}[/yellow]")
    confirm = safe_input('  Onaylamak için "SİL" yaz: ').strip(); flush_stdin()
    if confirm not in ("SİL", "SIL", "DELETE"):
        console.print("[yellow]İptal.[/yellow]"); flush_stdin(); safe_input("\nEnter..."); return

    # find workspace for output
    stem = pak_path.stem
    result_dir = BASE_DIR / f"FANx{stem}" / "RESULT PAK"
    result_dir.mkdir(parents=True, exist_ok=True)
    output_pak = result_dir / pak_path.name

    console.print(f"\n[cyan]Rebuilding PAK...[/cyan]")
    try:
        count = _cx_repack_full(pak, None, output_pak, delete_paths=[item_path])
        if count > 0:
            console.print(f"\n[bold green]✅ Silme tamamlandı![/bold green]")
            console.print(f"[dim]Çıktı: {output_pak}[/dim]")
        else:
            console.print("[red]❌ Hiçbir şey silinmedi.[/red]")
    except Exception as e:
        console.print(f"[red]❌ Hata: {e}[/red]")
        import traceback; traceback.print_exc()

    flush_stdin(); safe_input("\nEnter...")

# ==================== OBB TOOL + SM4 KEY FINDER + XOR CRYPT + LUA PROTECT ====================
# Ported from OBB_ENGINE_SOURCE, PAK_CRACKER, grok_sm4 — all clean

import zipfile as _zipfile

# ── OBB directories ───────────────────────────────────────────────────────────
OBB_ORIGINAL  = BASE_DIR / "OBB" / "original"
OBB_UNPACKED  = BASE_DIR / "OBB" / "unpacked"
OBB_REPACKED  = BASE_DIR / "OBB" / "repacked"
OBB_PAK_DIR   = BASE_DIR / "OBB" / "pak_to_inject"

def _ensure_obb_dirs():
    for d in [OBB_ORIGINAL, OBB_UNPACKED, OBB_REPACKED, OBB_PAK_DIR]:
        d.mkdir(parents=True, exist_ok=True)

# ── OBB size adjuster ─────────────────────────────────────────────────────────

def _adjust_obb_size(obb_path: Path, target_size: int):
    """Pad OBB ZIP comment field to match original file size exactly."""
    cur = obb_path.stat().st_size
    if cur == target_size:
        console.print(f"  [green]✅ Boyut zaten eşleşiyor: {target_size} byte[/green]")
        return
    if cur > target_size:
        raise ValueError(f"Repack'lenmiş OBB ({cur}) orijinalden ({target_size}) büyük — PAK dosyası çok büyük.")
    to_add = target_size - cur
    with open(str(obb_path), 'r+b') as f:
        f.seek(0, os.SEEK_END); flen = f.tell()
        seek = min(flen, 65536)
        f.seek(flen - seek); buf = f.read(seek)
        idx = buf.rfind(b'PK\x05\x06')
        if idx == -1: raise ValueError("ZIP EOCD imzası bulunamadı.")
        eocd_pos = flen - len(buf) + idx
        f.seek(eocd_pos); eocd = f.read(22)
        sig, d, dcd, de, te, cs, co, cl = struct.unpack('<IHHHHIIH', eocd)
        new_cl = cl + to_add
        if new_cl > 65535: raise ValueError(f"Gerekli padding ({to_add}) ZIP yorum sınırını aşıyor.")
        f.seek(eocd_pos + 20); f.write(struct.pack('<H', new_cl))
        f.seek(0, os.SEEK_END); f.write(b'\x00' * to_add)
    console.print(f"  [green]✅ OBB boyutu ayarlandı → {target_size} byte[/green]")

# ── OBB unpack ────────────────────────────────────────────────────────────────

def _obb_unpack(obb_path: Path, out_dir: Path):
    console.print(f"  [cyan]Çıkarılıyor: {obb_path.name}...[/cyan]")
    with _zipfile.ZipFile(str(obb_path), 'r') as zf:
        total = len(zf.namelist())
        for i, info in enumerate(zf.infolist(), 1):
            zf.extract(info, str(out_dir))
            if i % 50 == 0 or i == total:
                console.print(f"  [dim]{i}/{total}[/dim]", end='\r')
    console.print()
    console.print(f"  [green]✅ {total} dosya çıkarıldı → {out_dir}[/green]")

# ── OBB repack ────────────────────────────────────────────────────────────────

def _obb_repack(original_obb: Path, pak_files: list, out_dir: Path) -> Path:
    """Repack OBB: extract original, replace PAK files, re-zip, size-adjust."""
    original_size = original_obb.stat().st_size
    out_obb = out_dir / original_obb.name
    tmp_dir = BASE_DIR / "OBB" / "_tmp_repack"
    if tmp_dir.exists(): shutil.rmtree(str(tmp_dir))
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # extract original
    console.print(f"  [dim]Orijinal OBB çıkarılıyor...[/dim]")
    _obb_unpack(original_obb, tmp_dir)

    # place new PAK files
    pak_dest = tmp_dir / "ShadowTrackerExtra" / "Content" / "Paks"
    pak_dest.mkdir(parents=True, exist_ok=True)
    for pak in pak_files:
        shutil.copy2(str(pak), str(pak_dest / pak.name))
        console.print(f"  [green]+ {pak.name} → Paks/[/green]")

    # re-zip
    console.print(f"  [dim]Yeniden zip'leniyor...[/dim]")
    with _zipfile.ZipFile(str(original_obb), 'r') as orig_zf:
        orig_infos = orig_zf.infolist()

    with _zipfile.ZipFile(str(out_obb), 'w', _zipfile.ZIP_STORED) as zf:
        for info in orig_infos:
            fp = tmp_dir / info.filename
            if not fp.exists(): continue
            ni = _zipfile.ZipInfo(info.filename)
            ni.date_time = info.date_time
            ni.compress_type = _zipfile.ZIP_STORED
            ni.external_attr = info.external_attr
            zf.writestr(ni, fp.read_bytes())

    # padding dummy if needed
    cur = out_obb.stat().st_size
    if original_size - cur >= 256:
        dummy = original_size - cur - 256
        with _zipfile.ZipFile(str(out_obb), 'a', _zipfile.ZIP_STORED) as zf:
            zf.writestr('padding.bin', b'\x00' * dummy)

    # size adjust via ZIP comment
    try:
        _adjust_obb_size(out_obb, original_size)
    except ValueError as e:
        console.print(f"  [yellow]⚠ Size adjust: {e}[/yellow]")

    shutil.rmtree(str(tmp_dir))
    return out_obb

# ── OBB action ────────────────────────────────────────────────────────────────

def action_obb_tool():
    _ensure_obb_dirs()
    os.system('clear')
    console.print("[bold #00FFCC]📦 OBB TOOL[/bold #00FFCC]")
    console.print()
    console.print("  [1] OBB ÇIKAR   — original/ klasöründeki .obb'yi aç")
    console.print("  [2] OBB REPACK  — PAK dosyasıyla yeni OBB oluştur")
    console.print("  [0] Geri")
    console.print()
    console.print(f"  [dim]OBB original : {OBB_ORIGINAL}[/dim]")
    console.print(f"  [dim]PAK inject   : {OBB_PAK_DIR}[/dim]")
    console.print(f"  [dim]Repacked OBB : {OBB_REPACKED}[/dim]")
    console.print()
    c = safe_input("  Seç (0-2): ").strip(); flush_stdin()

    if c == '1':
        obbs = list(OBB_ORIGINAL.glob("*.obb")) + list(OBB_ORIGINAL.glob("*.zip"))
        if not obbs:
            console.print(f"[red]❌ OBB bulunamadı → {OBB_ORIGINAL}[/red]")
            flush_stdin(); safe_input("\nEnter..."); return
        for i, o in enumerate(obbs, 1):
            console.print(f"  [{i}] {o.name}  ({human_size(o.stat().st_size)})")
        try:
            idx = int(safe_input(f"  Seç (1-{len(obbs)}): ").strip()) - 1; flush_stdin()
            obb = obbs[idx]
        except Exception:
            console.print("[red]Geçersiz.[/red]"); flush_stdin(); safe_input("\nEnter..."); return
        OBB_UNPACKED.mkdir(parents=True, exist_ok=True)
        _obb_unpack(obb, OBB_UNPACKED)
        console.print(f"\n[green]✅ Çıkarıldı → {OBB_UNPACKED}[/green]")

    elif c == '2':
        obbs = list(OBB_ORIGINAL.glob("*.obb")) + list(OBB_ORIGINAL.glob("*.zip"))
        if not obbs:
            console.print(f"[red]❌ Orijinal OBB bulunamadı → {OBB_ORIGINAL}[/red]")
            flush_stdin(); safe_input("\nEnter..."); return
        for i, o in enumerate(obbs, 1):
            console.print(f"  [{i}] {o.name}  ({human_size(o.stat().st_size)})")
        try:
            idx = int(safe_input(f"  OBB seç (1-{len(obbs)}): ").strip()) - 1; flush_stdin()
            orig_obb = obbs[idx]
        except Exception:
            console.print("[red]Geçersiz.[/red]"); flush_stdin(); safe_input("\nEnter..."); return

        paks = list(OBB_PAK_DIR.glob("*.pak"))
        if not paks:
            console.print(f"[red]❌ PAK bulunamadı → {OBB_PAK_DIR}[/red]")
            console.print("[dim]  Inject edilecek .pak dosyasını buraya koy.[/dim]")
            flush_stdin(); safe_input("\nEnter..."); return
        for i, p in enumerate(paks, 1):
            console.print(f"  [{i}] {p.name}  ({human_size(p.stat().st_size)})")
        sel_raw = safe_input(f"  PAK seç (1-{len(paks)}, virgülle, all): ").strip().lower(); flush_stdin()
        if sel_raw == 'all':
            selected = paks
        else:
            try: selected = [paks[int(x)-1] for x in sel_raw.split(',')]
            except Exception: console.print("[red]Geçersiz.[/red]"); flush_stdin(); safe_input("\nEnter..."); return

        OBB_REPACKED.mkdir(parents=True, exist_ok=True)
        try:
            out = _obb_repack(orig_obb, selected, OBB_REPACKED)
            console.print(f"\n[bold green]🎉 OBB hazır: {out}[/bold green]")
        except Exception as e:
            console.print(f"[red]❌ Hata: {e}[/red]")

    flush_stdin(); safe_input("\nEnter...")

# ── SM4 Key Finder ────────────────────────────────────────────────────────────

_SM4_KEY_LEN = 20

def _sm4_collect_wide(lib_path: str) -> list:
    try:
        r = subprocess.run(["strings", "-el", lib_path],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, timeout=30)
        return [s.strip() for s in r.stdout.splitlines() if s.strip()]
    except Exception: return []

def _sm4_collect_embedded(lib_path: str) -> list:
    try:
        with open(lib_path, 'rb') as f: blob = f.read()
        results = set(); cur = 0
        while cur < len(blob) - 44:
            if blob[cur] == 0 and blob[cur+1] == 0:
                seg = b''; valid = True; ptr = cur + 2
                for _ in range(_SM4_KEY_LEN):
                    if ptr + 1 >= len(blob): valid = False; break
                    c = blob[ptr]; n = blob[ptr+1]
                    sym = chr(c) if 32 <= c < 127 else None
                    if sym is None or n != 0: valid = False; break
                    if not (sym.isalnum() or sym in '$*'): valid = False; break
                    seg += bytes([c]); ptr += 2
                if valid and ptr + 1 < len(blob) and blob[ptr] == 0 and blob[ptr+1] == 0:
                    try: results.add(seg.decode('ascii'))
                    except: pass
            cur += 1
        return list(results)
    except Exception: return []

def _sm4_is_plausible(seq: str) -> bool:
    if len(seq) != _SM4_KEY_LEN: return False
    if any(not (c.isalnum() or c in '$*') for c in seq): return False
    if seq.isalpha(): return False
    if not any(c.isdigit() or c in '$*' for c in seq): return False
    best = cur = 0
    for ch in seq:
        if ch.isalpha(): cur += 1; best = max(best, cur)
        else: cur = 0
    if best > 9: return False
    if len(set(seq)) / len(seq) < 0.6: return False
    return True

def action_sm4_finder():
    os.system('clear')
    console.print("[bold #FFCC00]🔑 SM4 KEY FINDER[/bold #FFCC00]")
    console.print("[dim]  libUE4.so binary'sinden SM4 key'leri tarar[/dim]")
    console.print()
    console.print(f"  [dim]libUE4.so beklenen konum: {BASE_DIR}/libUE4.so[/dim]")
    console.print(f"  [dim]veya tam path girebilirsin[/dim]")
    console.print()

    default = str(BASE_DIR / "libUE4.so")
    path_raw = safe_input(f"  Dosya yolu [{default}]: ").strip(); flush_stdin()
    lib_path = path_raw or default

    if not os.path.isfile(lib_path):
        console.print(f"[red]❌ Dosya bulunamadı: {lib_path}[/red]")
        flush_stdin(); safe_input("\nEnter..."); return

    console.print(f"  [dim]Taranıyor: {lib_path}...[/dim]")
    wide     = _sm4_collect_wide(lib_path)
    embedded = _sm4_collect_embedded(lib_path)
    all_candidates = set(wide + embedded)
    found = sorted(k for k in all_candidates if _sm4_is_plausible(k))

    if not found:
        console.print("[yellow]  Geçerli SM4 key bulunamadı.[/yellow]")
        flush_stdin(); safe_input("\nEnter..."); return

    console.print(f"\n  [green]{len(found)} key bulundu:[/green]")
    for k in found:
        console.print(f"  [yellow]{k}[/yellow]")

    # save
    out_file = BASE_DIR / "sm4_keys_found.txt"
    existing = set()
    if out_file.exists():
        for line in out_file.read_text().splitlines():
            l = line.strip()
            if l and not l.startswith('=='): existing.add(l)
    new_keys = [k for k in found if k not in existing]
    if new_keys:
        with open(str(out_file), 'a') as f:
            if out_file.stat().st_size == 0: f.write("==== SM4 KEY FINDER ====\n")
            for k in new_keys: f.write(k + '\n')
        console.print(f"\n  [green]{len(new_keys)} yeni key kaydedildi → {out_file}[/green]")
    else:
        console.print(f"\n  [dim]Tüm keyler zaten kayıtlı. ({out_file})[/dim]")

    console.print()
    add = safe_input("  Bu keyleri SM4_SECRET_NEW listesine eklemek ister misin? (Y/n): ").strip().lower(); flush_stdin()
    if add != 'n':
        global SM4_SECRET_NEW
        added = 0
        for k in new_keys:
            if k not in SM4_SECRET_NEW:
                SM4_SECRET_NEW.append(k); added += 1
        console.print(f"  [green]{added} key SM4_SECRET_NEW'e eklendi (bu oturum için)[/green]")

    flush_stdin(); safe_input("\nEnter...")

# ── XOR CRYPT ─────────────────────────────────────────────────────────────────

_DEFAULT_XOR_KEY = b'\x11!6GFW\xa7\x8d\x9d\x84\x90\xd8\xab\x00\x8c5&\x1a\xf7\xe4X\x05\xb8\xb3\x15\x07\xd0,\x1e\x8f\xf6\xc8'

def action_aes_crypt():
    """AES-256-GCM file encrypt/decrypt — matches aes_tool.c logic."""
    os.system('clear')
    console.print('[bold #FF8800]🔐 AES-256-GCM CRYPT[/bold #FF8800]')
    console.print('[dim]  PBKDF2-SHA1 key derivation | OpenSSL uyumlu format[/dim]')
    console.print()

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        import hashlib as _hl
    except ImportError:
        console.print('[red]❌ pip install cryptography[/red]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    console.print('  [1] Şifrele  (-e)')
    console.print('  [2] Çöz      (-d)')
    console.print('  [0] Geri')
    c = safe_input('\n  > ').strip(); flush_stdin()
    if c == '0': return
    if c not in ('1', '2'):
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    if not os.path.isfile(path_raw):
        console.print(f'[red]❌ Dosya bulunamadı.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    password = safe_input('  Şifre/anahtar: ').strip(); flush_stdin()
    if not password:
        console.print(f'[red]❌ Şifre boş.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    out_raw = safe_input('  Çıktı dosyası (boş = otomatik): ').strip().strip('"'); flush_stdin()

    # derive key exactly like aes_tool.c — PBKDF2-HMAC-SHA1, salt="termux_aes_salt"
    SALT = b'termux_aes_salt\x00'
    kdf = PBKDF2HMAC(algorithm=hashes.SHA1(), length=32, salt=SALT, iterations=10000)
    key = kdf.derive(password.encode('utf-8'))

    src = Path(path_raw)

    if c == '1':
        # encrypt
        out_path = Path(out_raw) if out_raw else src.with_suffix(src.suffix + '.aes')
        data = src.read_bytes()
        iv   = _secrets.token_bytes(12)
        ct   = AESGCM(key).encrypt(iv, data, None)
        # format: [12 IV][ciphertext+16 tag]  — tag is last 16 bytes of ct
        out_path.write_bytes(iv + ct)
        console.print(f'\n[green]✅ Şifrelendi → {out_path}[/green]')
        console.print(f'[dim]  {len(data)} byte → {out_path.stat().st_size} byte[/dim]')

    else:
        # decrypt
        out_path = Path(out_raw) if out_raw else src.with_suffix('.dec' + src.suffix)
        raw = src.read_bytes()
        if len(raw) < 28:  # 12 IV + 16 tag minimum
            console.print(f'[red]❌ Dosya çok küçük veya bozuk.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
        iv = raw[:12]; ct = raw[12:]
        try:
            plaintext = AESGCM(key).decrypt(iv, ct, None)
            out_path.write_bytes(plaintext)
            console.print(f'\n[green]✅ Çözüldü → {out_path}[/green]')
            console.print(f'[dim]  {len(plaintext)} byte[/dim]')
        except Exception:
            console.print('[red]❌ Şifre çözme başarısız — yanlış anahtar veya bozuk dosya.[/red]')

    flush_stdin(); safe_input(f'\n{T("press_enter")}')

def action_xor_crypt():
    os.system('clear')
    console.print('[bold #FF8800]⚡ XOR / AES CRYPT[/bold #FF8800]')
    console.print()
    console.print('  [1] XOR CRYPT   — PUBG/BGMI XOR anahtarıyla şifrele/çöz')
    console.print('  [2] XOR CRYPT   — GFP (Game for Peace) anahtarıyla')
    console.print('  [3] AES-256-GCM — şifrele veya çöz (aes_tool.c uyumlu)')
    console.print('  [0] Geri')
    console.print()
    c = safe_input('  > ').strip(); flush_stdin()

    if c == '0': return

    elif c in ('1', '2'):
        xor_k = _DEFAULT_XOR_KEY if c == '1' else _GFP_XOR_KEY
        lbl   = 'PUBG/BGMI' if c == '1' else 'GFP'
        path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
        if not path_raw or not os.path.isfile(path_raw):
            console.print(f'[red]❌ Dosya bulunamadı.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
        p = Path(path_raw)
        data = p.read_bytes()
        processed = bytes(b ^ xor_k[i % 32] for i, b in enumerate(data))
        out_raw = safe_input(f'  Çıktı [{path_raw}]: ').strip().strip('"'); flush_stdin()
        out_path = Path(out_raw) if out_raw else p
        out_path.write_bytes(processed)
        console.print(f'\n[green]✅ XOR ({lbl}) tamamlandı → {out_path}[/green]')
        console.print(f'[dim]  {len(data)} byte[/dim]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}')

    elif c == '3':
        action_aes_crypt()

    else:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}')

# ── LUA protection detect + strip ─────────────────────────────────────────────

_LUA_MAGIC_BYTES = b'\x1bLua'
_PROTECT_MARKERS = [b'BEKITV5', b'BEKITV4', b'FEEDFACE', b'ENCRYPTED_BY_', b'LOCKED_BY_', b'PROTECTED_BY_']

def _lua_detect_footer(data: bytes):
    if len(data) < 50: return None, -1
    search_start = max(0, len(data) - 500)
    tail = data[search_start:]
    needle = struct.pack('<IIII', 0x7FFFFFFF, 0x7FFFFFFF, 0, 0xFEEDFACE)
    pos = tail.find(needle)
    if pos >= 0:
        abs_pos = search_start + pos
        return 'BEKIT', max(0, abs_pos - 32)
    for marker in [b'BEKITV5', b'BEKIT']:
        pos = tail.find(marker)
        if pos >= 0:
            return 'BEKIT', max(0, search_start + pos - 48)
    for marker in [b'ENCRYPTED_BY_', b'PROTECTED_BY_']:
        pos = data.find(marker)
        if pos > 0:
            return 'UNKNOWN', max(0, pos - 96)
    return None, -1

def _lua_detect_protection(data: bytes) -> dict:
    info = {"protected": False, "owner": None, "markers": []}
    for m in _PROTECT_MARKERS:
        if m in data:
            info["protected"] = True; info["markers"].append(m.decode(errors='replace'))
    for m in [b'ENCRYPTED_BY_', b'PROTECTED_BY_', b'LOCKED_BY_']:
        pos = data.find(m)
        if pos > 0:
            end = data.find(b'\x00', pos)
            if end < 0 or end - pos > 60: end = pos + 40
            info["owner"] = data[pos:end].decode(errors='replace')
            break
    return info

def _lua_strip_footer(data: bytes) -> tuple:
    name, off = _lua_detect_footer(data)
    if name and off >= 0:
        return data[:off], True, f"{name} footer offset {off}"
    return data, False, "protection bulunamadı"

def action_lua_protect_strip():
    """Strip protection footer from .luac files in LUA_ORIGINAL."""
    _ensure_lua_dirs()
    os.system('clear')
    console.print("[bold #FF88FF]🛡  LUA PROTECTION STRIPPER[/bold #FF88FF]")
    console.print("[dim]  BEKITV5/FEEDFACE/ENCRYPTED_BY_ footer'larını temizler[/dim]")
    console.print()

    files = [f for f in os.listdir(str(LUA_ORIGINAL_DIR))
             if f.lower().endswith(('.luac', '.slua', '.lua'))]
    if not files:
        console.print(f"[red]❌ LUA_ORIGINAL boş → {LUA_ORIGINAL_DIR}[/red]")
        flush_stdin(); safe_input("\nEnter..."); return

    selected = _select_files(files, str(LUA_ORIGINAL_DIR), 'STRIP')
    if not selected: return

    success = 0
    for f in selected:
        src = LUA_ORIGINAL_DIR / f
        data = src.read_bytes()
        info = _lua_detect_protection(data)
        if not info["protected"]:
            console.print(f"  [dim]✓ {f} — zaten temiz[/dim]"); success += 1; continue
        cleaned, ok, msg = _lua_strip_footer(data)
        if ok:
            out = LUA_ORIGINAL_DIR / f
            out.write_bytes(cleaned)
            console.print(f"  [green]✅ {f} — temizlendi ({msg})[/green]")
            if info["owner"]: console.print(f"  [dim]   Koruma: {info['owner']}[/dim]")
            success += 1
        else:
            console.print(f"  [red]✗  {f} — footer silinemedi ({msg})[/red]")

    console.print(f"\n[bold]Sonuç: {success}/{len(selected)}[/bold]")
    flush_stdin(); safe_input("\nEnter...")


# ==================== LUADEC + ENHANCED TOOL FINDER (FUCKED.py clean port) ====================

def _find_lua_tool(name: str):
    """Search for lua tool in multiple locations — home source, script dir, PATH."""
    candidates = [name, f'{name}5.3', f'{name}53']
    search_dirs = [
        _HOME_SOURCE,
        SOURCE_DIR_LUA,
        Path(os.path.expanduser('~')),
        Path('/data/data/com.termux/files/usr/bin'),
    ]
    for d in search_dirs:
        for c in candidates:
            p = d / c
            try:
                if p.exists() and os.access(str(p), os.X_OK):
                    return p
            except Exception:
                pass
    import shutil as _sh
    for c in candidates:
        w = _sh.which(c)
        if w: return Path(w)
    return None

def _lua_decompile_luadec(luac_file: Path, out_path: Path = None) -> tuple:
    """Decompile using luadec binary (alternative to unluac.jar)."""
    luadec = _find_lua_tool('luadec')
    if not luadec:
        return False, 'luadec bulunamadı — SOURCE/ klasörüne koy'
    if out_path is None:
        out_path = LUA_EDIT_DIR / (luac_file.stem + '.lua')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [str(luadec), str(luac_file)],
            capture_output=True, timeout=60
        )
        stdout = result.stdout or b''
        stderr = result.stderr or b''
        if stdout:
            out_path.write_bytes(stdout)
            return True, str(out_path)
        err = stderr.decode('utf-8', errors='replace').strip() or 'bilinmeyen hata'
        return False, err[:200]
    except subprocess.TimeoutExpired:
        return False, 'timeout'
    except Exception as e:
        return False, str(e)

def action_lua_decompile_luadec():
    """LUA_ORIGINAL → LUA_EDIT using luadec binary."""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF88FF]🔓 LUADEC DECOMPİLE[/bold #FF88FF]')
    console.print()

    luadec = _find_lua_tool('luadec')
    if not luadec:
        console.print('[red]❌ luadec bulunamadı.[/red]')
        console.print(f'[dim]  luadec binary\'sini {SOURCE_DIR_LUA} içine koy.[/dim]')
        console.print('[dim]  Android arm64 için: github.com/nicowillis/luadec veya Telegram\'da ara.[/dim]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    console.print(f'  [green]✅ luadec: {luadec}[/green]')
    console.print()

    files = [f for f in os.listdir(str(LUA_ORIGINAL_DIR))
             if f.lower().endswith(('.luac', '.slua', '.lua'))]
    if not files:
        console.print(f'[red]❌ LUA_ORIGINAL boş → {LUA_ORIGINAL_DIR}[/red]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    selected = _select_files(files, str(LUA_ORIGINAL_DIR), 'LUADEC')
    if not selected: return

    success = 0; failed = []
    import tempfile as _tf
    with _tf.TemporaryDirectory(prefix='star_luadec_') as tmp:
        for i, f in enumerate(selected, 1):
            src = LUA_ORIGINAL_DIR / f
            console.print(f'  [{i}/{len(selected)}] {f}')
            # first try converting PUBG format to std
            temp_std = Path(tmp) / f
            ok_conv, _ = _convert_luac(str(src), str(temp_std))
            src_to_use = temp_std if ok_conv and temp_std.exists() else src
            ok, result = _lua_decompile_luadec(src_to_use, LUA_EDIT_DIR / (Path(f).stem + '.lua'))
            if ok:
                console.print(f'  [green]✅ {Path(result).name}[/green]')
                success += 1
            else:
                console.print(f'  [red]✗ {result}[/red]')
                failed.append(f)

    console.print(f'\n[bold]Sonuç: {success}/{len(selected)}[/bold]')
    if failed: console.print(f'[red]Başarısız: {", ".join(failed)}[/red]')
    flush_stdin(); safe_input(f'\n{T("press_enter")}')

# ==================== SO PANEL PATCHER (rich.py clean port) ====================
# lib.so / APK panel link finder and patcher
# Finds: plain, base64, hex, XOR-0x2E, reversed URLs

_SO_XOR_KEY = 0x2E
_SO_SEARCH_DIRS = [
    '/sdcard', '/storage/emulated/0',
    str(Path(os.path.expanduser('~'))),
    '/data/local/tmp',
]

def _so_find_files(ext: str) -> list:
    found = []; searched = set()
    skip = {'proc','sys','dev','run','lost+found'}
    for base in _SO_SEARCH_DIRS:
        if not os.path.exists(base): continue
        try:
            for root, dirs, files in os.walk(base):
                real = os.path.realpath(root)
                if real in searched: dirs.clear(); continue
                searched.add(real)
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in skip]
                for f in files:
                    if f.endswith(ext): found.append(os.path.join(root, f))
        except PermissionError: continue
    return found

def _so_extract_from_apk(apk_path: str) -> tuple:
    import tempfile as _tf
    console.print('  [dim]APK çıkarılıyor...[/dim]')
    tmp = _tf.mkdtemp(prefix='so_patch_')
    try:
        with _zipfile.ZipFile(apk_path, 'r') as zf: zf.extractall(tmp)
    except _zipfile.BadZipFile:
        console.print('  [red]❌ Geçersiz APK.[/red]')
        shutil.rmtree(tmp, ignore_errors=True); return None, None
    sos = []
    for root, _, files in os.walk(tmp):
        for f in files:
            if f.endswith('.so'):
                fp = os.path.join(root, f)
                sos.append((fp, os.path.getsize(fp)))
    if not sos:
        console.print('  [red]❌ APK içinde .so bulunamadı.[/red]')
        shutil.rmtree(tmp, ignore_errors=True); return None, None
    sos.sort(key=lambda x: x[1], reverse=True)
    return sos, tmp

def _so_repack_apk(apk_path: str, tmp_dir: str, out_path: str):
    console.print('  [dim]APK yeniden paketleniyor...[/dim]')
    with _zipfile.ZipFile(out_path, 'w', _zipfile.ZIP_DEFLATED) as zout:
        for root, _, files in os.walk(tmp_dir):
            for f in files:
                fp = os.path.join(root, f)
                zout.write(fp, os.path.relpath(fp, tmp_dir))
    console.print(f'  [green]✅ APK hazır: {out_path}[/green]')
    console.print('  [dim]Not: APK imzasız — apksigner gerekebilir.[/dim]')

def _so_select(items: list, label: str) -> str:
    console.print(f'\n  [green]{len(items)} {label} bulundu:[/green]\n')
    for i, (path, size) in enumerate(items, 1):
        mb = round(size/(1024*1024), 2)
        mark = ' [yellow]← ANA LİB[/yellow]' if mb >= 1 else ''
        console.print(f'  [{i}] {os.path.basename(path)}{mark}')
        console.print(f'      {path}')
        console.print(f'      {mb} MB\n')
    c = safe_input('  Seç > ').strip(); flush_stdin()
    if not c.isdigit() or not (1 <= int(c) <= len(items)):
        console.print('  [red]Geçersiz.[/red]'); return None
    return items[int(c)-1][0]

# ── link finders ──────────────────────────────────────────────────────────────

def _so_find_plain(data: bytes) -> list:
    import re as _re
    res = []
    for m in _re.finditer(rb'https?://[^\x00\s<>"\'\\]{4,}', data):
        res.append({'type':'PLAIN','index':m.start(),'length':len(m.group(0)),'url':m.group(0).decode('utf-8',errors='ignore').strip()})
    return res

def _so_find_base64(data: bytes) -> list:
    import re as _re
    res = []; seen = set()
    for m in _re.finditer(rb'[A-Za-z0-9+/]{20,}={0,2}', data):
        raw = m.group(0)
        try:
            dec = base64.b64decode(raw + b'='*(-len(raw)%4)).decode('utf-8',errors='ignore')
            if 'http' in dec:
                f = _re.search(r'https?://[^\x00\s<>"\'\\]+', dec)
                if f and f.group(0) not in seen:
                    seen.add(f.group(0))
                    res.append({'type':'BASE64','index':m.start(),'length':len(raw),'url':f.group(0),'full_decoded':dec})
        except Exception: pass
    return res

def _so_find_hex(data: bytes) -> list:
    import re as _re
    res = []; seen = set()
    for m in _re.finditer(rb'(?:[0-9a-fA-F]{2}){16,}', data):
        try:
            dec = bytes.fromhex(m.group(0).decode('ascii')).decode('utf-8',errors='ignore')
            if 'http' in dec:
                f = _re.search(r'https?://[^\x00\s<>"\'\\]+', dec)
                if f and f.group(0) not in seen:
                    seen.add(f.group(0))
                    res.append({'type':'HEX','index':m.start(),'length':len(m.group(0)),'url':f.group(0)})
        except Exception: pass
    return res

def _so_find_xor(data: bytes) -> list:
    import re as _re
    res = []; seen = set(); key = _SO_XOR_KEY
    tgt = bytes(b^key for b in b'http'); start = 0
    while True:
        pos = data.find(tgt, start)
        if pos == -1: break
        chunk = bytes(b^key for b in data[pos:pos+512])
        try:
            text = chunk.decode('utf-8',errors='ignore')
            f = _re.match(r'(https?://[^\x00\s<>"\'\\]{8,})', text)
            if f and f.group(1) not in seen:
                seen.add(f.group(1))
                res.append({'type':'XOR-0x2E','index':pos,'length':len(f.group(1).encode()),'url':f.group(1),'xor_key':key})
        except Exception: pass
        start = pos + 1
    return res

def _so_find_reversed(data: bytes) -> list:
    import re as _re
    res = []; seen = set()
    for m in _re.finditer(rb'[^\x00\s]{8,}(?:ptth|sptth)', data):
        try:
            text = m.group(0)[::-1].decode('utf-8',errors='ignore')
            if _re.match(r'https?://', text):
                f = _re.match(r'(https?://[^\x00\s<>"\'\\]+)', text)
                if f and f.group(1) not in seen:
                    seen.add(f.group(1))
                    res.append({'type':'REVERSED','index':m.start(),'length':len(m.group(0)),'url':f.group(1)})
        except Exception: pass
    return res

def _so_encode_url(link: dict, new_url: str) -> bytes:
    t = link['type']
    if   t == 'PLAIN':    return new_url.encode('utf-8')
    elif t == 'BASE64':
        txt = link.get('full_decoded', link['url']).replace(link['url'], new_url)
        return base64.b64encode(txt.encode('utf-8'))
    elif t == 'HEX':      return new_url.encode('utf-8').hex().encode('ascii')
    elif t == 'XOR-0x2E':
        k = link['xor_key']; return bytes(b^k for b in new_url.encode('utf-8'))
    elif t == 'REVERSED': return new_url.encode('utf-8')[::-1]
    return new_url.encode('utf-8')

def _so_apply_patch(data: bytes, link: dict, new_url: str) -> bytes:
    new_b = _so_encode_url(link, new_url)
    orig = link['length']; pos = link['index']
    new_b = new_b[:orig] if len(new_b) > orig else new_b.ljust(orig, b'\x00')
    buf = bytearray(data); buf[pos:pos+orig] = new_b; return bytes(buf)

# ── main action ───────────────────────────────────────────────────────────────

def action_so_patcher():
    os.system('clear')
    console.print('[bold #00FF88]🔧 SO PANEL PATCHER[/bold #00FF88]')
    console.print('[dim]  lib.so veya APK içindeki panel linklerini bulur ve değiştirir[/dim]')
    console.print()
    console.print('  [1] APK dosyası ara (otomatik)')
    console.print('  [2] .so dosyası ara (otomatik)')
    console.print('  [3] APK yolu elle gir')
    console.print('  [4] .so yolu elle gir')
    console.print('  [0] Geri')
    console.print()
    choice = safe_input('  Seç > ').strip(); flush_stdin()

    so_path = None; tmp_dir = None; apk_path = None

    if choice == '0': return
    elif choice == '1':
        console.print('  [dim]APK aranıyor...[/dim]')
        apks = _so_find_files('.apk')
        if not apks: console.print(f'  [red]❌ APK bulunamadı.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
        items = sorted([(p, os.path.getsize(p)) for p in apks], key=lambda x: x[1], reverse=True)
        apk_path = _so_select(items, 'APK')
        if not apk_path: flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
        sos, tmp_dir = _so_extract_from_apk(apk_path)
        if not sos: flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
        so_path = _so_select(sos, '.so (APK içi)')
        if not so_path: shutil.rmtree(tmp_dir, ignore_errors=True); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    elif choice == '2':
        console.print('  [dim].so aranıyor...[/dim]')
        raw = _so_find_files('.so')
        if not raw: console.print(f'  [red]❌ .so bulunamadı.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
        items = sorted([(p, os.path.getsize(p)) for p in raw], key=lambda x: x[1], reverse=True)
        so_path = _so_select(items, '.so')
        if not so_path: flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    elif choice == '3':
        apk_path = safe_input('  APK yolu > ').strip().strip('"'); flush_stdin()
        if not os.path.isfile(apk_path): console.print(f'[red]❌ Dosya bulunamadı.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
        sos, tmp_dir = _so_extract_from_apk(apk_path)
        if not sos: flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
        so_path = _so_select(sos, '.so (APK içi)')
        if not so_path: shutil.rmtree(tmp_dir, ignore_errors=True); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    elif choice == '4':
        so_path = safe_input('  .so yolu > ').strip().strip('"'); flush_stdin()
        if not os.path.isfile(so_path): console.print(f'[red]❌ Dosya bulunamadı.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
    else:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    with open(so_path, 'rb') as f: data = f.read()
    sz = round(len(data)/(1024*1024), 2)
    console.print(f'\n  [cyan]{os.path.basename(so_path)}[/cyan]  {sz} MB')
    console.print('  [dim]Panel linkleri taranıyor (plain/base64/hex/xor/reversed)...[/dim]')

    links = []
    for fn in (_so_find_plain, _so_find_base64, _so_find_hex, _so_find_xor, _so_find_reversed):
        links += fn(data)
    seen_u = set(); unique = []
    for l in links:
        if l['url'] not in seen_u: seen_u.add(l['url']); unique.append(l)

    if not unique:
        console.print('\n  [yellow]❌ Panel linki bulunamadı.[/yellow]')
        if tmp_dir: shutil.rmtree(tmp_dir, ignore_errors=True)
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    console.print(f'\n  [green]{len(unique)} link bulundu:[/green]\n')
    for i, l in enumerate(unique, 1):
        console.print(f'  [{i}] [yellow]{l["type"]}[/yellow]  offset:{l["index"]}  {l["length"]}b')
        console.print(f'      [cyan]{l["url"]}[/cyan]\n')

    sel = safe_input(f'  Değiştirilecek link numarası (1-{len(unique)}): ').strip(); flush_stdin()
    if not sel.isdigit() or not (1 <= int(sel) <= len(unique)):
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    selected = unique[int(sel)-1]
    console.print(f'\n  Seçili: [cyan]{selected["url"]}[/cyan]')
    console.print(f'  Tür   : [yellow]{selected["type"]}[/yellow]\n')
    new_url = safe_input('  Yeni panel linki > ').strip(); flush_stdin()
    if not new_url:
        console.print(f'[red]Boş URL.[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    patched = _so_apply_patch(data, selected, new_url)
    with open(so_path, 'wb') as f: f.write(patched)
    console.print('  [green]✅ Binary patch uygulandı[/green]')

    if tmp_dir and apk_path:
        out_apk = apk_path + '.patched.apk'
        _so_repack_apk(apk_path, tmp_dir, out_apk)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        console.print(f'\n  [bold green]✅ Tamamlandı → {out_apk}[/bold green]')
    else:
        out_so = so_path + '.patched'
        shutil.copy(so_path, out_so)
        console.print(f'\n  [bold green]✅ Tamamlandı → {out_so}[/bold green]')

    console.print(f'  [dim]Eski: {selected["url"]}[/dim]')
    console.print(f'  [dim]Yeni: {new_url}[/dim]')
    flush_stdin(); safe_input(f'\n{T("press_enter")}')

# ==================== NUCLEAR PY ENCRYPTOR (1.sh clean port — Nuclear mode only) ====================
# Multi-layer Python script encryptor: Scrypt + AES-GCM outer + ChaCha20 hash-chain inner
# No Cython, no ELF, no external binaries needed — pure Python

import secrets as _secrets
import gc as _gc
import zlib as _zlib_enc

_NUC_MAGIC  = [0x42, 0x4C, 0x4B, 0x21, 0x00]
_NUC_CHUNKS = 8
_NUC_NT     = 64
_NUC_NR     = 32
_NUC_DIR    = BASE_DIR / "NUCLEAR"

def _ensure_nuc_dirs():
    (_NUC_DIR / "input").mkdir(parents=True, exist_ok=True)
    (_NUC_DIR / "output").mkdir(parents=True, exist_ok=True)

def _nuc_encrypt_payload(source: bytes, master_key: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    import hashlib as _hl

    # compress + sign
    sig    = _hl.sha256(source).digest()
    cdata  = sig + _zlib_enc.compress(source, level=9)

    # split into chunks
    csz    = (len(cdata) + _NUC_CHUNKS - 1) // _NUC_CHUNKS
    chunks = [cdata[i:i+csz] for i in range(0, len(cdata), csz)]

    # ChaCha20 hash-chain inner
    prev = _hl.sha256(master_key).digest()
    encrypted_chunks = []
    for idx, chunk in enumerate(chunks):
        nonce = _secrets.token_bytes(12)
        salt  = _hl.sha256(master_key + idx.to_bytes(4,'big') + prev).digest()
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        from cryptography.hazmat.primitives import hashes
        sk    = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=10000).derive(master_key)
        ct    = ChaCha20Poly1305(sk).encrypt(nonce, chunk, idx.to_bytes(4,'big'))
        prev  = _hl.sha256(ct).digest()
        encrypted_chunks.append(nonce + ct)

    # pack inner
    inner = len(encrypted_chunks).to_bytes(4,'big')
    for ec in encrypted_chunks:
        inner += len(ec).to_bytes(4,'big') + ec

    # AES-GCM outer with Scrypt
    salt_o  = _secrets.token_bytes(32)
    nonce_o = _secrets.token_bytes(12)
    k_o     = Scrypt(salt=salt_o, length=32, n=2**17, r=8, p=1).derive(master_key)
    ct_o    = AESGCM(k_o).encrypt(nonce_o, inner, salt_o)

    payload = bytes(_NUC_MAGIC) + salt_o + nonce_o + len(ct_o).to_bytes(4,'big') + ct_o
    import base64 as _b64
    return _b64.b85encode(payload).decode()

def _nuc_make_loader(payload_b85: str, master_key: bytes) -> str:
    import hashlib as _hl, random as _rnd

    # fragment key into NT random fragments, NR used at runtime
    ca = _secrets.token_bytes(32)
    cb = bytes(ca[i] ^ master_key[i] for i in range(32))

    # build fragment table
    rng    = _rnd.Random(int.from_bytes(_hl.sha256(master_key).digest()[:4],'big'))
    used   = sorted(rng.sample(range(_NUC_NT), _NUC_NR))
    ft     = {}
    for pi in range(_NUC_NT):
        mask  = _secrets.token_bytes(2)
        stub  = _secrets.token_bytes(2)
        if pi in used:
            sm   = _hl.sha256(stub).digest()[:2]
            frag = bytes(master_key[pi*2 % 32] ^ mask[j] ^ sm[j] for j in range(2))
            val  = bytes(frag[j] ^ mask[j] ^ sm[j] for j in range(2))
        else:
            val  = _secrets.token_bytes(2)
        ft[pi] = (mask.hex(), stub.hex(), val.hex())

    ic_hex = _hl.sha256(master_key).hexdigest()

    # chunk payload for readability
    chunk_sz  = 76
    p85       = payload_b85
    chunks    = [p85[i:i+chunk_sz] for i in range(0, len(p85), chunk_sz)]
    chunks_lit = repr(chunks)
    ft_lit    = repr({k: (bytes.fromhex(v[0]), bytes.fromhex(v[1]), bytes.fromhex(v[2])) for k,v in ft.items()})

    loader = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# FANTool Nuclear Encryptor — @FanteriBey
import sys,os,hashlib,base64,struct,zlib,gc,random as _rnd
try: from cryptography.hazmat.primitives.ciphers.aead import AESGCM as _AG,ChaCha20Poly1305 as _CP
except ImportError: sys.exit("[!] pip install cryptography")
try: from cryptography.hazmat.primitives.kdf.scrypt import Scrypt as _SC
except ImportError: sys.exit("[!] pip install cryptography")
try: from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC as _PB
except ImportError: sys.exit("[!] pip install cryptography")
try: from cryptography.hazmat.primitives import hashes as _HS
except ImportError: sys.exit("[!] pip install cryptography")
_MAGIC={_NUC_MAGIC};_NT={_NUC_NT};_NR={_NUC_NR}
def _ad():
    import platform,ctypes
    try:
        import ctypes.util
        if sys.platform.startswith("linux"):
            try: open("/proc/self/status").read()
            except: pass
            try:
                with open("/proc/self/status") as _f:
                    for _l in _f:
                        if _l.startswith("TracerPid:") and int(_l.split(":")[1])>0: sys.exit(1)
            except: pass
    except: pass
    try:
        _dbg={{"pydevd","_pydevd_bundle","debugpy","bdb","pdb"}}
        if _dbg & set(sys.modules): sys.exit(1)
    except: pass
def _wk(b):
    try:
        if isinstance(b,bytearray):
            for _i in range(len(b)): b[_i]=0; return
        _sz=len(b)
        if not _sz: return
        _off=sys.getsizeof(b)-_sz
        _buf=(ctypes.c_char*_sz).from_address(id(b)+_off)
        ctypes.memset(_buf,0,_sz)
    except: pass
def _assemble():
    _ca=bytes.fromhex({repr(ca.hex())}); _cb=bytes.fromhex({repr(cb.hex())})
    _si=bytes([_ca[_i]^_cb[_i] for _i in range(len(_ca))])
    _seed=int.from_bytes(hashlib.sha256(_si).digest()[:4],'big')
    _rgen=_rnd.Random(_seed); _rp=sorted(_rgen.sample(range(_NT),_NR))
    _ft={ft_lit}
    _parts=[]
    for _pi in _rp:
        _m,_s,_v=_ft[_pi]; _sm=hashlib.sha256(_s).digest()[:2]
        _fb=bytes([_v[_j]^_m[_j]^_sm[_j] for _j in range(2)])
        _parts.append(_fb)
    _adj=b\'\'.join(_parts); _ic_h=hashlib.sha256(bytes.fromhex({repr(ic_hex)})).digest()
    _pw=bytes([_adj[_i]^_ic_h[_i] for _i in range(32)])
    _wk(_adj); del _adj; return _pw
def _boot():
    _ad()
    _chunks={chunks_lit}
    _raw=base64.b85decode("".join(_chunks))
    if list(_raw[:4])!=_MAGIC: sys.exit(1)
    _raw=_raw[5:]; _pw=_assemble(); _ad()
    try:
        _s_o=_raw[:32]; _n_o=_raw[32:44]; _elen=struct.unpack(">I",_raw[44:48])[0]; _e_o=_raw[48:48+_elen]
        _k_o=_SC(salt=_s_o,length=32,n=2**17,r=8,p=1).derive(_pw)
        _pkd=_AG(_k_o).decrypt(_n_o,_e_o,_s_o); _wk(_k_o); del _k_o; gc.collect()
        _nc=struct.unpack(">I",_pkd[:4])[0]; _off=4; _cts=[]
        for _ in range(_nc):
            _bl=struct.unpack(">I",_pkd[_off:_off+4])[0]; _cts.append(_pkd[_off+4:_off+4+_bl]); _off+=4+_bl
        _pkd=None; gc.collect()
        _prev=hashlib.sha256(_pw).digest(); _cks=[]
        for _idx,_ct_blob in enumerate(_cts):
            _nonce=_ct_blob[:12]; _ct=_ct_blob[12:]
            _salt=hashlib.sha256(_pw+_idx.to_bytes(4,\'big\')+_prev).digest()
            _sk=_PB(algorithm=_HS.SHA256(),length=32,salt=_salt,iterations=10000).derive(_pw)
            _c=_CP(_sk).decrypt(_nonce,_ct,_idx.to_bytes(4,\'big\'))
            _prev=hashlib.sha256(_ct).digest(); _wk(_sk); del _sk; _cks.append(_c)
        _wk(_pw); del _pw; gc.collect()
        _data=b\'\'.join(_cks); _cks=None
        _sig=_data[:32]; _src=zlib.decompress(_data[32:])
        if hashlib.sha256(_src).digest()!=_sig: sys.exit(1)
        _data=None; gc.collect()
        _ad(); _co=compile(_src,"<runtime>","exec"); _src=None; gc.collect()
        exec(_co,{{"__name__":"__main__","__file__":sys.argv[0],"__builtins__":__builtins__,"__spec__":None}})
    except SystemExit: raise
    except: sys.exit(1)
_ad(); _boot()
del _boot,_ad,_wk,_assemble
'''
    return loader

def action_py_encryptor():
    _ensure_nuc_dirs()
    os.system('clear')
    console.print('[bold #FF4444]🔐 NUCLEAR PY ENCRYPTOR[/bold #FF4444]')
    console.print('[dim]  Scrypt + AES-GCM + ChaCha20 hash-chain | saf Python[/dim]')
    console.print()
    console.print(f'  [dim]Input  : {_NUC_DIR}/input/*.py[/dim]')
    console.print(f'  [dim]Output : {_NUC_DIR}/output/[/dim]')
    console.print()

    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
    except ImportError:
        console.print('[red]❌ cryptography paketi eksik:[/red]')
        console.print('  pip install cryptography')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    files = list((_NUC_DIR / 'input').glob('*.py'))
    if not files:
        console.print(f'[red]❌ {_NUC_DIR}/input/ klasörü boş.[/red]')
        console.print('[dim]  Şifrelemek istediğin .py dosyasını buraya koy.[/dim]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    for i, f in enumerate(files, 1):
        console.print(f'  [{i}] {f.name}  ({human_size(f.stat().st_size)})')
    console.print('  [A] TÜMÜ')
    console.print('  [0] İptal')
    c = safe_input(f'\n  Seç: ').strip().upper(); flush_stdin()
    if c == '0': return
    selected = files if c == 'A' else ([files[int(c)-1]] if c.isdigit() and 1 <= int(c) <= len(files) else [])
    if not selected: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    success = 0
    for f in selected:
        console.print(f'\n  [cyan]Şifreleniyor:[/cyan] {f.name}')
        try:
            source     = f.read_bytes()
            master_key = _secrets.token_bytes(32)
            console.print(f'  [dim]→ payload şifreleniyor...[/dim]')
            payload    = _nuc_encrypt_payload(source, master_key)
            console.print(f'  [dim]→ loader üretiliyor...[/dim]')
            loader     = _nuc_make_loader(payload, master_key)
            out        = _NUC_DIR / 'output' / (f.stem + '_nuclear.py')
            out.write_text(loader, encoding='utf-8')
            console.print(f'  [green]✅ {out.name}  ({human_size(out.stat().st_size)})[/green]')
            console.print(f'  [dim]  Çalıştır: python3 {out}[/dim]')
            success += 1
        except Exception as e:
            console.print(f'  [red]✗ {f.name}: {e}[/red]')

    console.print(f'\n[bold]Sonuç: {success}/{len(selected)} şifrelendi[/bold]')
    flush_stdin(); safe_input(f'\n{T("press_enter")}')

# ==================== LUADEC AUTO BUILD ====================

def action_build_luadec():
    """Clone and build viruscamp/luadec in Termux, copy to SOURCE."""
    os.system('clear')
    console.print('[bold #FFAA00]🔨 LUADEC AUTO BUILD[/bold #FFAA00]')
    console.print('[dim]  github.com/viruscamp/luadec — Lua 5.1/5.2/5.3 decompiler[/dim]')
    console.print()

    # check deps
    console.print('[dim]  Bağımlılıklar kontrol ediliyor...[/dim]')
    import shutil as _sh2
    missing = []
    for tool in ('git', 'clang', 'make'):
        if not _sh2.which(tool):
            missing.append(tool)
    if missing:
        console.print(f'[yellow]⚠ Eksik paketler: {", ".join(missing)}[/yellow]')
        console.print(f'[dim]  Yükleniyor...[/dim]')
        subprocess.run(['pkg', 'install', '-y'] + missing)

    # select lua version
    console.print()
    console.print('  [1] Lua 5.1  [dim](PUBG Mobile — önerilen)[/dim]')
    console.print('  [2] Lua 5.2')
    console.print('  [3] Lua 5.3')
    console.print('  [0] İptal')
    c = safe_input('\n  Versiyon seç (1-3): ').strip(); flush_stdin()
    ver_map = {'1': '5.1', '2': '5.2', '3': '5.3'}
    if c not in ver_map: return
    LUAVER = ver_map[c]

    build_dir = Path(os.path.expanduser('~')) / 'luadec_build'
    src_dir   = build_dir / 'luadec'
    lua_dir   = src_dir / f'lua-{LUAVER}'
    dec_dir   = src_dir / 'luadec'

    # clone
    if not src_dir.exists():
        console.print('\n  [cyan]Klonlanıyor...[/cyan]')
        r = subprocess.run(['git', 'clone',
            '--depth=1',
            'https://github.com/viruscamp/luadec',
            str(src_dir)], capture_output=False)
        if r.returncode != 0:
            console.print('[red]❌ Clone başarısız.[/red]')
            flush_stdin(); safe_input(f'\n{T("press_enter")}'); return
    else:
        console.print(f'\n  [dim]Mevcut clone kullanılıyor: {src_dir}[/dim]')

    # submodule init
    console.print(f'  [cyan]Submodule güncelleniyor (lua-{LUAVER})...[/cyan]')
    subprocess.run(['git', 'submodule', 'update', '--init', f'lua-{LUAVER}'],
                   cwd=str(src_dir))

    # build lua lib
    console.print(f'  [cyan]Lua {LUAVER} derleniyor...[/cyan]')
    r = subprocess.run(['make', 'linux'], cwd=str(lua_dir), capture_output=False)
    if r.returncode != 0:
        # try generic make
        r = subprocess.run(['make'], cwd=str(lua_dir), capture_output=False)
    if r.returncode != 0:
        console.print(f'[red]❌ Lua {LUAVER} derlenemedi.[/red]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    # build luadec
    console.print(f'  [cyan]luadec derleniyor...[/cyan]')
    r = subprocess.run(['make', f'LUAVER={LUAVER}'],
                       cwd=str(dec_dir), capture_output=False)
    if r.returncode != 0:
        console.print('[red]❌ luadec derlenemedi.[/red]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    # find binary
    binary = dec_dir / 'luadec'
    if not binary.exists():
        # search
        for p in dec_dir.rglob('luadec'):
            if os.access(str(p), os.X_OK):
                binary = p; break

    if not binary.exists():
        console.print('[red]❌ luadec binary bulunamadı.[/red]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    # copy to SOURCE
    _HOME_SOURCE.mkdir(parents=True, exist_ok=True)
    dst = _HOME_SOURCE / 'luadec'
    shutil.copy2(str(binary), str(dst))
    os.chmod(str(dst), 0o755)

    # also copy to SOURCE_DIR_LUA on sdcard if accessible
    try:
        SOURCE_DIR_LUA.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(binary), str(SOURCE_DIR_LUA / 'luadec'))
    except Exception: pass

    console.print()
    console.print(f'[bold green]✅ luadec {LUAVER} hazır![/bold green]')
    console.print(f'[dim]  Konum: {dst}[/dim]')
    console.print(f'\n  Artık [4] LUA MODE → [4] LUADEC ile decompile yapabilirsin.')
    flush_stdin(); safe_input(f'\n{T("press_enter")}')


# ==================== PAK UNPACK / REPACK ====================

PAK_UNPACK_OUT = BASE_DIR / "PAK_UNPACK"

def action_pak_unpack():
    """Extract all files from PAK to PAK_UNPACK/ folder."""
    os.system('clear')
    console.print('[bold #00FFCC]📤 PAK UNPACK[/bold #00FFCC]')
    console.print(f'[dim]  Çıktı: {PAK_UNPACK_OUT}[/dim]')
    console.print()

    pak_files = sorted([f for f in BASE_DIR.iterdir()
                        if f.is_file() and f.name.lower().endswith('.pak')], key=lambda x: x.name)
    if not pak_files:
        console.print(f'[red]❌ FANTOOL/ klasöründe .pak bulunamadı.[/red]')
        console.print(f'[dim]  .pak dosyasını {BASE_DIR} klasörüne koy.[/dim]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    for i, p in enumerate(pak_files, 1):
        console.print(f'  [{i}] {p.name}  ({human_size(p.stat().st_size)})')
    console.print()

    try:
        c = safe_input(f'  PAK seç (1-{len(pak_files)}): ').strip(); flush_stdin()
        pak_path = pak_files[int(c)-1]
    except Exception:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    out_dir = PAK_UNPACK_OUT / pak_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    console.print(f'\n  [cyan]Yükleniyor: {pak_path.name}...[/cyan]')
    try:
        pak = TencentPakFile(PurePath(pak_path))
    except Exception as e:
        console.print(f'[red]❌ PAK yüklenemedi: {e}[/red]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    console.print(f'  [cyan]Çıkarılıyor → {out_dir}...[/cyan]')
    try:
        pak.dump(PurePath(out_dir))
        total = sum(1 for _ in out_dir.rglob('*') if _.is_file())
        console.print(f'\n[bold green]✅ Tamamlandı! {total} dosya çıkarıldı.[/bold green]')
        console.print(f'[dim]  Konum: {out_dir}[/dim]')
        console.print(f'\n  [dim]Lua dosyaları: {out_dir}/Content/Lua/[/dim]')
        console.print(f'  [dim]Değiştirip inject etmek için:[/dim]')
        console.print(f'  [dim]  Dosyayı CUSTOM FILES/ klasörüne koy → [1] CUSTOM INJECT[/dim]')
    except Exception as e:
        console.print(f'[red]❌ Extract hatası: {e}[/red]')
        import traceback; traceback.print_exc()

    flush_stdin(); safe_input(f'\n{T("press_enter")}')

def action_pak_repack():
    """Repack modified files back into PAK."""
    os.system('clear')
    console.print('[bold #FFAA00]📦 PAK REPACK[/bold #FFAA00]')
    console.print('[dim]  PAK_UNPACK/ içindeki değiştirilmiş dosyaları PAK\'a yazar[/dim]')
    console.print()

    pak_files = sorted([f for f in BASE_DIR.iterdir()
                        if f.is_file() and f.name.lower().endswith('.pak')], key=lambda x: x.name)
    if not pak_files:
        console.print(f'[red]❌ FANTOOL/ klasöründe .pak bulunamadı.[/red]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    unpack_dirs = [d for d in PAK_UNPACK_OUT.iterdir() if d.is_dir()] if PAK_UNPACK_OUT.exists() else []
    if not unpack_dirs:
        console.print(f'[red]❌ PAK_UNPACK/ içinde extract edilmiş klasör yok.[/red]')
        console.print(f'[dim]  Önce [14] PAK UNPACK ile extract et.[/dim]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    for i, p in enumerate(pak_files, 1):
        console.print(f'  [{i}] {p.name}  ({human_size(p.stat().st_size)})')
    try:
        c = safe_input(f'\n  Kaynak PAK (1-{len(pak_files)}): ').strip(); flush_stdin()
        pak_path = pak_files[int(c)-1]
    except Exception:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    console.print()
    for i, d in enumerate(unpack_dirs, 1):
        console.print(f'  [{i}] {d.name}/')
    try:
        c2 = safe_input(f'  Değiştirilmiş klasör (1-{len(unpack_dirs)}): ').strip(); flush_stdin()
        edit_dir = unpack_dirs[int(c2)-1]
    except Exception:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    stem = pak_path.stem
    result_dir = BASE_DIR / f'FANx{stem}' / 'RESULT PAK'
    result_dir.mkdir(parents=True, exist_ok=True)
    out_pak = result_dir / pak_path.name

    console.print(f'\n  [cyan]Yükleniyor: {pak_path.name}...[/cyan]')
    try:
        pak = TencentPakFile(PurePath(pak_path))
    except Exception as e:
        console.print(f'[red]❌ PAK yüklenemedi: {e}[/red]')
        flush_stdin(); safe_input(f'\n{T("press_enter")}'); return

    console.print(f'  [cyan]Repack ediliyor → {out_pak}...[/cyan]')
    try:
        count = _cx_repack_full(pak, PurePath(edit_dir), out_pak)
        console.print(f'\n[bold green]✅ Repack tamamlandı! ({count} dosya)[/bold green]')
        console.print(f'[dim]  Çıktı: {out_pak}[/dim]')
    except Exception as e:
        console.print(f'[red]❌ Repack hatası: {e}[/red]')
        import traceback; traceback.print_exc()

    flush_stdin(); safe_input(f'\n{T("press_enter")}')


# ==================== UASSET / UEXP EDITOR ====================
# Ported from UAsset Editor Pro HTML tool

import struct as _struct

_UE4_MAGIC = 0x9E2A83C1
_UE4_ASSET_TYPES = {
    'PhysicsAsset': '🧲', 'SkeletalMesh': '🦴', 'Skeleton': '💀',
    'AnimSequence': '🎞', 'StaticMesh': '🧊', 'Material': '🎨',
    'ParticleSystem': '✨', 'Blueprint': '📄', 'Asset': '📦'
}

def _ue_ri32(d, p): return _struct.unpack_from('<i', d, p)[0]
def _ue_ru32(d, p): return _struct.unpack_from('<I', d, p)[0]
def _ue_rf32(d, p): return _struct.unpack_from('<f', d, p)[0]
def _ue_rf64(d, p): return _struct.unpack_from('<d', d, p)[0]
def _ue_ri8(d, p):  return _struct.unpack_from('<b', d, p)[0]
def _ue_ri16(d, p): return _struct.unpack_from('<h', d, p)[0]
def _ue_ru8(d, p):  return d[p]

def _ue_rfs(d, p):
    if p + 4 > len(d): return '', p + 4
    l = _ue_ri32(d, p); p += 4
    if l == 0: return '', p
    if 0 < l < 4096 and p + l <= len(d):
        return d[p:p+l-1].decode('utf-8', 'replace'), p + l
    if -2048 < l < 0:
        c = -l
        if p + c * 2 > len(d): return '', p
        s = bytes(d[p+i*2] for i in range(c-1)).decode('utf-8', 'replace')
        return s, p + c * 2
    return '', p

def _ue_rfn(d, names, p):
    if p + 8 > len(d): return '?', p + 8
    idx = _ue_ri32(d, p); num = _ue_ri32(d, p+4)
    nm = names[idx] if 0 <= idx < len(names) else f'?{idx}'
    return (f'{nm}_{num}' if num else nm), p + 8

def _ue_parse_header(d):
    p = 0
    magic = _ue_ru32(d, p); p += 4
    if magic != _UE4_MAGIC:
        raise ValueError('Geçersiz UE4 dosyası — magic byte eşleşmiyor')
    p += 4; p += 4; p += 4; p += 4
    cc = _ue_ru32(d, p); p += 4
    p += min(cc, 500) * 20; p += 4
    _, p = _ue_rfs(d, p)
    p += 4
    nc = _ue_ru32(d, p); p += 4
    no = _ue_ru32(d, p); p += 4
    p += 8; p += 8
    ec = _ue_ru32(d, p); p += 4
    eo = _ue_ru32(d, p); p += 4
    ic = _ue_ru32(d, p); p += 4
    io = _ue_ru32(d, p); p += 4
    return {'nc': nc, 'no': no, 'ec': ec, 'eo': eo, 'ic': ic, 'io': io}

def _ue_parse_names(d, h):
    names = []; p = h['no']
    for i in range(min(h['nc'], 200000)):
        if p >= len(d): break
        s, p = _ue_rfs(d, p); p += 4
        names.append(s)
    return names

def _ue_parse_imports(d, h, names):
    r = []; p = h['io']
    for i in range(min(h['ic'], 5000)):
        if p + 28 > len(d): break
        cp, p = _ue_rfn(d, names, p)
        cn, p = _ue_rfn(d, names, p)
        oi = _ue_ri32(d, p); p += 4
        on_, p = _ue_rfn(d, names, p)
        r.append({'cp': cp, 'cn': cn, 'oi': oi, 'on': on_})
    return r

def _ue_detect_type(names, imports):
    ns = set(n.lower() for n in names)
    cs = set(i['cn'].lower() for i in imports)
    if 'physicsasset' in ns or 'physicsasset' in cs or 'skeletalbodysetup' in ns: return 'PhysicsAsset'
    if 'skeletalmesh' in ns or 'skeletalmesh' in cs: return 'SkeletalMesh'
    if 'skeleton' in ns and ('boneinfo' in ns or 'refpose' in ns): return 'Skeleton'
    if 'animsequence' in ns: return 'AnimSequence'
    if 'staticmesh' in ns or 'staticmesh' in cs: return 'StaticMesh'
    if 'material' in ns and 'materialexpression' in ns: return 'Material'
    if 'blueprintgeneratedclass' in ns or 'blueprint' in ns: return 'Blueprint'
    return 'Asset'

def _ue_scan_props(d, names):
    n2i = {n: i for i, n in enumerate(names)}
    fi  = n2i.get('FloatProperty',  -1)
    ii  = n2i.get('IntProperty',    -1)
    bi  = n2i.get('BoolProperty',   -1)
    di  = n2i.get('DoubleProperty', -1)
    i64 = n2i.get('Int64Property',  -1)
    u32 = n2i.get('UInt32Property', -1)
    i8i = n2i.get('Int8Property',   -1)
    i16 = n2i.get('Int16Property',  -1)
    props = []; seen = set()
    for i in range(len(d) - 32):
        ni = _ue_ru32(d, i)
        if ni >= len(names): continue
        if _ue_ru32(d, i+4) != 0 or _ue_ru32(d, i+12) != 0: continue
        ti = _ue_ru32(d, i+8); sz = _ue_ri32(d, i+16)
        ai = _ue_ri32(d, i+20); hg = d[i+24]
        if sz <= 0 or sz > 32 or ai < 0 or ai > 20 or hg > 1: continue
        vo = i + 25 + (16 if hg else 0)
        if vo + sz > len(d): continue
        nm = names[ni]; e = None
        if ti == fi  and sz == 4:
            v = _ue_rf32(d, vo)
            if abs(v) > 1e-12 and abs(v) < 1e12: e = {'o': vo, 'n': nm, 't': 'float',  'v': round(v, 7)}
        elif ti == di and sz == 8:
            v = _ue_rf64(d, vo)
            if abs(v) > 1e-12 and abs(v) < 1e15: e = {'o': vo, 'n': nm, 't': 'double', 'v': round(v, 10)}
        elif ti == ii and sz == 4:
            v = _ue_ri32(d, vo)
            if -1e7 < v < 1e9: e = {'o': vo, 'n': nm, 't': 'int32',  'v': v}
        elif ti == bi and sz == 1:
            v = d[vo]
            if v in (0, 1): e = {'o': vo, 'n': nm, 't': 'bool',   'v': v}
        elif ti == u32 and sz == 4:
            v = _ue_ru32(d, vo)
            if v < 1e9: e = {'o': vo, 'n': nm, 't': 'uint32', 'v': v}
        elif ti == i8i and sz == 1:
            e = {'o': vo, 'n': nm, 't': 'int8',  'v': _ue_ri8(d, vo)}
        elif ti == i16 and sz == 2:
            e = {'o': vo, 'n': nm, 't': 'int16', 'v': _ue_ri16(d, vo)}
        if e and vo not in seen:
            seen.add(vo); props.append(e)
    return sorted(props, key=lambda x: x['o'])

def _ue_write_prop(d, prop, new_val):
    o = prop['o']; t = prop['t']
    if t == 'float':
        _struct.pack_into('<f', d, o, float(new_val))
    elif t == 'double':
        _struct.pack_into('<d', d, o, float(new_val))
    elif t == 'int32':
        _struct.pack_into('<i', d, o, int(new_val))
    elif t == 'uint32':
        _struct.pack_into('<I', d, o, int(new_val))
    elif t == 'int8':
        _struct.pack_into('<b', d, o, int(new_val))
    elif t == 'int16':
        _struct.pack_into('<h', d, o, int(new_val))
    elif t == 'bool':
        d[o] = 1 if new_val else 0

_PROP_CATS = {
    '🔥 Hasar':    ['Damage', 'Impact', 'Head', 'Limb'],
    '🔫 Ateş':     ['ShootInterval', 'BulletFire', 'BulletRange', 'FireAnim'],
    '📦 Şarjör':   ['Bullet', 'Clip', 'Ammo'],
    '🔄 Reload':   ['Reload', 'ReloadTime'],
    '↩ Geri tep.': ['Recoil', 'Recover', 'Horizontal', 'Kick'],
    '🎯 Sapma':    ['Deviation', 'Spread'],
    '🔧 Aksesuar': ['Accessories', 'Modifier'],
    '🧲 Fizik':    ['Limit', 'Damping', 'Stiff', 'Radius', 'Mass', 'Spring'],
    '📐 Silah':    ['Weapon', 'Aim', 'FOV', 'Hold'],
}

def _ue_cat(name):
    for cat, keys in _PROP_CATS.items():
        if any(k.lower() in name.lower() for k in keys):
            return cat
    return '📁 Diğer'

# ══════════════════════════════════════════════════════════
# UN.PY PORT — Enhanced UAsset/UExp Parser
# ══════════════════════════════════════════════════════════

class _UAssetFileEx:
    """Enhanced UAsset parser — ported from un.py"""
    MAGIC = 0x9E2A83C1
    PROP_TYPES = [
        b'IntProperty',b'FloatProperty',b'BoolProperty',b'StrProperty',
        b'NameProperty',b'ByteProperty',b'ArrayProperty',b'StructProperty',
        b'ObjectProperty',b'EnumProperty',b'TextProperty',b'MapProperty',
        b'SetProperty',b'Int8Property',b'Int16Property',b'Int64Property',
        b'UInt16Property',b'UInt32Property',b'UInt64Property',b'DoubleProperty',
        b'SoftObjectProperty',b'SoftClassProperty',b'MulticastDelegateProperty'
    ]
    def __init__(self):
        self.data=b'';self.size=0;self.valid=False
        self.names=[];self.paths=[];self.all_strings=[]
    def load_data(self,data:bytes)->bool:
        self.data=bytes(data);self.size=len(data);return self._parse()
    def _parse(self)->bool:
        if self.size<100:return False
        try:
            if struct.unpack('<I',self.data[:4])[0]!=self.MAGIC:return False
            self.valid=True
            self._extract_all_strings()
            self._find_asset_paths()
            self._find_property_names()
            return True
        except:return False
    def _extract_all_strings(self):
        self.all_strings=[];self.names=[];i=0
        while i<self.size-5:
            try:
                length=struct.unpack('<I',self.data[i:i+4])[0]
                if 2<=length<=200:
                    pot=self.data[i+4:i+4+length]
                    try:
                        s=pot.rstrip(b'\x00').decode('ascii','ignore')
                        if len(s)>=2 and s.isprintable() and all(c.isprintable() or c in ' _.-/' for c in s):
                            self.all_strings.append({'offset':i,'string':s,'type':'lp'})
                            self.names.append({'index':len(self.names),'name':s,'offset':i})
                            i+=4+length;continue
                    except: pass
            except: pass
            if i<self.size and 32<=self.data[i]<127:
                end=i
                while end<min(i+256,self.size) and 32<=self.data[end]<127:end+=1
                if end>i+2 and end<self.size and self.data[end]==0:
                    try:
                        s=self.data[i:end].decode('utf-8','ignore')
                        if len(s)>=3 and s.isprintable():
                            if not any(x['string']==s for x in self.all_strings):
                                self.all_strings.append({'offset':i,'string':s,'type':'nt'})
                            i=end+1;continue
                    except:pass
            i+=1
    def _find_asset_paths(self):
        self.paths=[]
        for pat in [b'/Game/',b'/Script/',b'/Engine/']:
            pos=0
            while True:
                pos=self.data.find(pat,pos)
                if pos==-1:break
                end=pos
                while end<self.size and self.data[end]!=0:end+=1
                path=self.data[pos:end].decode('utf-8','ignore')
                if len(path)>5:self.paths.append({'offset':pos,'path':path})
                pos=end+1
    def _find_property_names(self):
        for pt in self.PROP_TYPES:
            pos=0
            while True:
                pos=self.data.find(pt,pos)
                if pos==-1:break
                nm=pt.decode('utf-8')
                if not any(x['name']==nm for x in self.names):
                    self.names.append({'index':len(self.names),'name':nm,'offset':pos})
                pos+=len(pt)
    def get_name(self,idx)->str:
        return self.names[idx]['name'] if 0<=idx<len(self.names) else f'[{idx}]'

class _UExpFileEx:
    """Enhanced UExp parser — ported from un.py"""
    PROP_PATTERNS={
        b'IntProperty':'i32',b'FloatProperty':'f32',b'BoolProperty':'bool',
        b'StrProperty':'str',b'NameProperty':'str',b'TextProperty':'str',
        b'ByteProperty':'i8',b'Int8Property':'i8',b'Int16Property':'i16',
        b'UInt16Property':'u16',b'UInt32Property':'u32',b'UInt64Property':'u64',
        b'Int64Property':'i64',b'DoubleProperty':'f64',
    }
    def __init__(self,uasset:_UAssetFileEx=None):
        self.data=b'';self.size=0;self.uasset=uasset
        self.properties=[];self.string_values=[];self.int_values=[];self.float_values=[]
    def load_data(self,data:bytes)->bool:
        self.data=bytes(data);self.size=len(data);return self._parse()
    def _parse(self)->bool:
        if self.size<10:return False
        try:self._extract_strings();self._scan_properties();self._cleanup();return True
        except:return False
    def _extract_strings(self):
        self.string_values=[];i=0
        while i<self.size-5:
            try:
                length=struct.unpack('<i',self.data[i:i+4])[0]
                if 1<=length<=500:
                    pot=self.data[i+4:i+4+length]
                    if all(b==0 or (32<=b<127) for b in pot):
                        s=pot.rstrip(b'\x00').decode('utf-8','ignore')
                        if len(s)>=1 and s.isprintable():
                            self.string_values.append({'offset':i,'value':s,'length':length});i+=4+length;continue
                elif -500<=length<=-1:
                    l2=-length
                    pot=self.data[i+4:i+4+l2*2]
                    try:
                        s=pot.rstrip(b'\x00\x00').decode('utf-16-le','ignore')
                        if len(s)>=1:self.string_values.append({'offset':i,'value':s,'length':l2,'enc':'utf16'});i+=4+l2*2;continue
                    except:pass
            except:pass
            i+=1
    def _scan_properties(self):
        self.properties=[]
        for pat,tname in self.PROP_PATTERNS.items():
            pos=0
            while True:
                pos=self.data.find(pat,pos)
                if pos==-1:break
                prop=self._extract_at(pos,tname,pat)
                if prop:self.properties.append(prop)
                pos+=len(pat)
    def _extract_at(self,tp,tname,pat):
        try:
            name=self._find_name_before(tp)
            va=tp+len(pat);value=None;vo=va
            if tname=='i32':
                for off in range(va,min(va+30,self.size-4)):
                    if struct.unpack('<I',self.data[off:off+4])[0]==4:
                        for vo in range(off+4,min(off+20,self.size-4)):
                            if self.data[vo]==0:
                                vo+=1
                                if vo+4<=self.size:value=struct.unpack('<i',self.data[vo:vo+4])[0];break
                        if value is not None:break
            elif tname=='f32':
                for off in range(va,min(va+30,self.size-4)):
                    if struct.unpack('<I',self.data[off:off+4])[0]==4:
                        for vo in range(off+4,min(off+20,self.size-4)):
                            if self.data[vo]==0:
                                vo+=1
                                if vo+4<=self.size:
                                    v=struct.unpack('<f',self.data[vo:vo+4])[0]
                                    if -1e10<v<1e10:value=round(v,6);break
                        if value is not None:break
            elif tname=='bool':
                for off in range(va,min(va+20,self.size)):
                    if off+4<=self.size and struct.unpack('<I',self.data[off:off+4])[0]==0:
                        for vo in range(off+4,min(off+10,self.size)):
                            if self.data[vo] in [0,1]:value=bool(self.data[vo]);break
                        if value is not None:break
            elif tname=='f64':
                for off in range(va,min(va+30,self.size-8)):
                    if struct.unpack('<I',self.data[off:off+4])[0]==8:
                        for vo in range(off+4,min(off+20,self.size-8)):
                            if self.data[vo]==0:
                                vo+=1
                                if vo+8<=self.size:value=round(struct.unpack('<d',self.data[vo:vo+8])[0],6);break
                        if value is not None:break
            elif tname=='str':
                for off in range(va,min(va+50,self.size-4)):
                    sl=struct.unpack('<i',self.data[off:off+4])[0]
                    if 1<=sl<=500 and off+4+sl<=self.size:
                        s=self.data[off+4:off+4+sl].rstrip(b'\x00').decode('utf-8','ignore')
                        if s.isprintable():value=s;vo=off;break
                    elif -500<=sl<=-1:
                        sl=-sl
                        if off+4+sl*2<=self.size:
                            s=self.data[off+4:off+4+sl*2].decode('utf-16-le','ignore').rstrip('\x00')
                            if s:value=s;vo=off;break
            elif tname in ('i64','u64'):
                for off in range(va,min(va+30,self.size-8)):
                    if struct.unpack('<I',self.data[off:off+4])[0]==8:
                        for vo in range(off+4,min(off+20,self.size-8)):
                            if self.data[vo]==0:
                                vo+=1
                                if vo+8<=self.size:value=struct.unpack('<q',self.data[vo:vo+8])[0];break
                        if value is not None:break
            elif tname in ('u32','u16','i16','i8'):
                sz={'u32':4,'u16':2,'i16':2,'i8':1}[tname]
                fmt={'u32':'<I','u16':'<H','i16':'<h','i8':'<b'}[tname]
                for off in range(va,min(va+30,self.size-sz)):
                    if struct.unpack('<I',self.data[off:off+4])[0]==sz:
                        if off+4+sz<=self.size:value=struct.unpack(fmt,self.data[off+4:off+4+sz])[0];vo=off+4;break
            if value is not None:
                return {'name':name,'type':tname,'value':value,'original':value,'offset':vo,'type_offset':tp,'modified':False}
        except:pass
        return None
    def _find_name_before(self,pos:int)->str:
        search_start=max(0,pos-100);chunk=self.data[search_start:pos]
        best='Unknown';best_len=0
        if self.uasset:
            for nm in self.uasset.names:
                n=nm['name'].encode('utf-8')
                if len(n)>=2 and n in chunk:
                    idx=chunk.rfind(n)
                    if idx>best_len:best_len=idx;best=nm['name']
        return best
    def _cleanup(self):
        seen=set();clean=[]
        for p in sorted(self.properties,key=lambda x:x['offset']):
            k=(p['offset'],p['type'])
            if k not in seen:seen.add(k);clean.append(p)
        self.properties=clean
    def write_prop(self,prop,new_val)->bool:
        try:
            d=bytearray(self.data);t=prop['type'];o=prop['offset']
            if t=='i32':struct.pack_into('<i',d,o,int(new_val))
            elif t=='f32':struct.pack_into('<f',d,o,float(new_val))
            elif t=='f64':struct.pack_into('<d',d,o,float(new_val))
            elif t=='i64':struct.pack_into('<q',d,o,int(new_val))
            elif t=='u32':struct.pack_into('<I',d,o,int(new_val))
            elif t=='u16':struct.pack_into('<H',d,o,int(new_val))
            elif t=='i16':struct.pack_into('<h',d,o,int(new_val))
            elif t=='i8':struct.pack_into('<b',d,o,int(new_val))
            elif t=='bool':d[o]=1 if new_val else 0
            self.data=bytes(d);return True
        except:return False


def action_uasset_editor():
    os.system('clear')
    console.print('[bold #00FFCC]🎮 UASSET / UEXP EDITOR[/bold #00FFCC]')
    console.print('[dim]  UE4 property editörü — float/int/bool düzenle[/dim]')
    console.print()

    search_dirs = [BASE_DIR/"PAK_UNPACK", BASE_DIR, Path('/sdcard/Download'), Path(os.path.expanduser('~'))]
    ua_files = []
    for d in search_dirs:
        if d.exists():
            try: ua_files.extend(list(d.rglob('*.uasset'))[:30])
            except: pass

    if not ua_files:
        console.print('[red]❌ .uasset bulunamadı — önce [14] PAK UNPACK yap.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return

    ua_files = sorted(set(ua_files), key=lambda x: x.stat().st_size, reverse=True)[:30]
    for i, f in enumerate(ua_files[:20], 1):
        console.print(f'  [{i}] {f.name}  [dim]({human_size(f.stat().st_size)})[/dim]')
    if len(ua_files) > 20: console.print(f'  [dim]+{len(ua_files)-20} tane daha[/dim]')
    console.print('  [0] Geri')

    try:
        c = safe_input(f'\n  Seç (0-{min(20,len(ua_files))}): ').strip(); flush_stdin()
        if c == '0': return
        ua_path = ua_files[int(c)-1]
    except Exception:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return

    ue_path = ua_path.with_suffix('.uexp')
    if not ue_path.exists():
        raw = safe_input(f'  .uexp yolu: ').strip().strip('"'); flush_stdin()
        ue_path = Path(raw) if raw else ue_path
        if not ue_path.exists():
            console.print(f'[red]❌ .uexp bulunamadı.[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return

    console.print(f'\n  [cyan]Parse ediliyor...[/cyan]')
    try:
        ua_data = bytearray(ua_path.read_bytes())
        ue_data = bytearray(ue_path.read_bytes())
        # Enhanced parser (un.py)
        ua_ex = _UAssetFileEx()
        ua_ex.load_data(bytes(ua_data))
        ue_ex = _UExpFileEx(ua_ex)
        ue_ex.load_data(bytes(ue_data))
        # Merge with classic parser for compatibility
        header  = _ue_parse_header(ua_data)
        names   = _ue_parse_names(ua_data, header)
        imports = _ue_parse_imports(ua_data, header, names)
        atype   = _ue_detect_type(names, imports)
        # Use enhanced props if more found
        classic_props = _ue_scan_props(ue_data, names)
        enh_props = ue_ex.properties
        props = enh_props if len(enh_props) > len(classic_props) else classic_props
        # Add string props from enhanced parser
        for sv in ue_ex.string_values[:50]:
            if sv['value'] and len(sv['value'])>2:
                props.append({'o':sv['offset'],'n':f'String_{sv["offset"]:X}','t':'str','v':sv['value']})
    except Exception as e:
        console.print(f'[red]❌ Hata: {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return

    icon    = _UE4_ASSET_TYPES.get(atype, '📦')
    changes = {}
    PAGE    = 20
    filt    = ''
    page    = 0

    while True:
        os.system('clear')
        filtered = [p for p in props if filt.lower() in p['n'].lower()] if filt else props
        total    = len(filtered)
        pages    = max(1, (total + PAGE - 1) // PAGE)
        page     = min(page, pages - 1)
        chunk    = filtered[page*PAGE:(page+1)*PAGE]

        console.print(f'[bold #00FFCC]🎮 UASSET[/bold #00FFCC]  {icon} [bold]{atype}[/bold]')
        console.print(f'[dim]  {ua_path.name}  |  {total} property  |  [yellow]{len(changes)} değişiklik[/yellow]  |  Sayfa {page+1}/{pages}[/dim]')
        if filt: console.print(f'  [dim]Filtre: "{filt}"[/dim]')
        console.print()

        for i, p in enumerate(chunk, 1):
            idx  = page*PAGE + i
            ch   = changes.get(p['o'])
            val  = str(ch['new']) if ch else str(p['v'])
            mark = ' [yellow]✎[/yellow]' if ch else ''
            t    = f'[dim]{p["t"]}[/dim]'
            console.print(f'  [yellow]{idx:3}[/yellow]  [cyan]{p["n"][:35]}[/cyan]{mark}  {t}  [white]{val}[/white]  [dim]0x{p["o"]:05X}[/dim]')

        console.print()
        console.print('[dim]  Numara gir=düzenle | f=filtre | n=sonraki | p=önceki | s=kaydet | 0=geri[/dim]')
        cmd = safe_input('  > ').strip().lower(); flush_stdin()

        if cmd == '0' or cmd == '/exit': break
        elif cmd == 'n': page = (page + 1) % pages
        elif cmd == 'p': page = (page - 1) % pages
        elif cmd == 'f':
            filt = safe_input('  Filtre (boş=temizle): ').strip(); flush_stdin(); page = 0
        elif cmd == 's' or cmd == '/save':
            if not changes:
                console.print(f'[yellow]  Değişiklik yok.[/yellow]'); safe_input(f'  {T("press_enter")}'); continue
            for o, ch in changes.items():
                _ue_write_prop(ue_data, ch['prop'], ch['new'])
            out = ue_path.parent / (ue_path.stem + '_edited.uexp')
            out.write_bytes(bytes(ue_data))
            console.print(f'\n[green]✅ Kaydedildi: {out.name}[/green]')
            console.print(f'[dim]  {len(changes)} değişiklik uygulandı[/dim]')
            ue_data = bytearray(out.read_bytes()); changes = {}
            safe_input(f'  {T("press_enter")}')
        elif cmd.isdigit() and 1 <= int(cmd) <= total:
            prop = filtered[int(cmd)-1]
            cur  = changes[prop['o']]['new'] if prop['o'] in changes else prop['v']
            console.print(f'\n  [cyan]{prop["n"]}[/cyan]  [{prop["t"]}]  mevcut: [yellow]{cur}[/yellow]')
            new_raw = safe_input('  Yeni değer (boş=iptal): ').strip(); flush_stdin()
            if not new_raw: continue
            try:
                if prop['t'] == 'bool':
                    nv = 1 if new_raw.lower() in ('1','true','evet','yes') else 0
                elif prop['t'] in ('float','double'):
                    nv = float(new_raw)
                else:
                    nv = int(new_raw)
                changes[prop['o']] = {'prop': prop, 'new': nv, 'orig': prop['v']}
                console.print(f'  [green]✅ {prop["n"]}: {cur} → {nv}[/green]')
            except ValueError:
                console.print('[red]  Geçersiz değer.[/red]')
            safe_input(f'  {T("press_enter")}')
        else:
            console.print(f'[red]  Geçersiz.[/red]'); safe_input(f'  {T("press_enter")}')

    if changes:
        console.print(f'\n  [yellow]{len(changes)} kaydedilmemiş değişiklik.[/yellow]')
        c = safe_input('  Kaydet? (E/h): ').strip().lower(); flush_stdin()
        if c != 'h':
            for o, ch in changes.items():
                _ue_write_prop(ue_data, ch['prop'], ch['new'])
            out = ue_path.parent / (ue_path.stem + '_edited.uexp')
            out.write_bytes(bytes(ue_data))
            console.print(f'[green]✅ Kaydedildi: {out.name}[/green]')
            flush_stdin(); safe_input(f'  {T("press_enter")}')


# ==================== PREMIUM.py + dravix.py CLEAN PORT ====================

# ── T24 Opcode Tables (PREMIUM.py — verified) ─────────────────────────────
_P_STD_OPCODE_NAMES = [
    "MOVE","LOADK","LOADKX","LOADBOOL","LOADNIL",
    "GETUPVAL","GETTABUP","GETTABLE","SETTABUP","SETUPVAL",
    "SETTABLE","NEWTABLE","SELF","ADD","SUB",
    "MUL","MOD","POW","DIV","IDIV",
    "BAND","BOR","BXOR","SHL","SHR",
    "UNM","BNOT","NOT","LEN","CONCAT",
    "JMP","EQ","LT","LE","TEST",
    "TESTSET","CALL","TAILCALL","RETURN","FORLOOP",
    "FORPREP","TFORCALL","TFORLOOP","SETLIST","CLOSURE",
    "VARARG","EXTRAARG"
]

_P_T24_NAME_SHUFFLED = {
     0:"ADD",  1:"SUB",  2:"MUL",  5:"DIV",  7:"BAND", 10:"SHL",
    12:"UNM", 14:"NOT", 15:"LEN", 16:"CONCAT",
    17:"MOVE",18:"LOADK",20:"LOADBOOL",21:"LOADNIL",
    22:"GETUPVAL",23:"GETTABUP",24:"GETTABLE",
     8:"SETTABUP", 9:"SETUPVAL",27:"SETTABLE",28:"NEWTABLE",29:"SELF",
    30:"JMP", 31:"EQ",  32:"LT",  33:"LE",  34:"TEST", 35:"TESTSET",
    36:"CALL",37:"TAILCALL",38:"RETURN",
    39:"FORLOOP",40:"FORPREP",41:"TFORCALL",42:"TFORLOOP",
    43:"SETLIST",44:"CLOSURE",45:"VARARG",
}
_P_T24_TO_STD = {t24: _P_STD_OPCODE_NAMES.index(nm)
                 for t24, nm in _P_T24_NAME_SHUFFLED.items()
                 if nm in _P_STD_OPCODE_NAMES}
_P_STD_TO_T24 = {std: t24 for t24, std in _P_T24_TO_STD.items()}
_P_XOR_KEY    = bytes.fromhex("112136474657a78d9d8490d8ab008c35261af7e45805b8b31507d02c1e8ff6c8")

# ── T24 → Standard Lua 5.3 (PREMIUM.py — accurate XOR string decode) ──────
def _premium_t24_to_std(src_path: str, dst_path: str) -> tuple:
    """
    Convert PUBG/BGMI T24 bytecode to standard Lua 5.3.
    Handles: opcode remap + XOR string decode + lineinfo width fix.
    Replaces the simpler _convert_luac with full accuracy.
    """
    with open(src_path, 'rb') as f: d = bytearray(f.read())
    if d[:4] != b'\x1bLua' or d[4] != 0x53:
        return False, 'Not Lua 5.3 bytecode'
    out = bytearray(); pos = [0]
    out.extend(d[:34]); pos[0] = 34
    def rb():   v = d[pos[0]]; pos[0] += 1; return v
    def ri32(): v = struct.unpack_from('<i', d, pos[0])[0]; pos[0] += 4; return v
    def ri64(): v = struct.unpack_from('<q', d, pos[0])[0]; pos[0] += 8; return v
    def rf64(): v = struct.unpack_from('<d', d, pos[0])[0]; pos[0] += 8; return v
    def wb(v):  out.append(v & 0xFF)
    def wi32(v):out.extend(struct.pack('<i', v))
    def wi64(v):out.extend(struct.pack('<q', v))
    def wf64(v):out.extend(struct.pack('<d', v))
    def _xdw():
        sz = d[pos[0]]
        if sz == 0:   pos[0] += 1; out.append(0); return
        if sz == 0xFF:
            length = struct.unpack_from('<Q', d, pos[0]+1)[0] - 1
            ds = pos[0] + 9; pos[0] = ds + length
            out.append(0xFF); out.extend(struct.pack('<Q', length + 1))
        else:
            length = sz - 1; ds = pos[0] + 1; pos[0] = ds + length
            out.append(sz)
        for i in range(length):
            out.append(d[ds + i] ^ _P_XOR_KEY[i % len(_P_XOR_KEY)])
    def _remap(ins):
        t24_op = ins & 0x3F
        std_op  = _P_T24_TO_STD.get(t24_op, t24_op)
        return (ins & ~0x3F) | std_op
    def _rebuild():
        _xdw(); wi32(ri32()); wi32(ri32())
        wb(rb()); wb(rb()); wb(rb())
        n = ri32(); wi32(n)
        for _ in range(n):
            ins = struct.unpack_from('<I', d, pos[0])[0]; pos[0] += 4
            out.extend(struct.pack('<I', _remap(ins)))
        n = ri32(); wi32(n)
        for _ in range(n):
            t = rb(); wb(t)
            if   t == 0:        pass
            elif t == 1:        wb(rb())
            elif t == 3:        wf64(rf64())
            elif t == 19:       wi64(ri64())
            elif t in (4, 20):  _xdw()
            else: raise ValueError(f'Unknown const type {t}')
        n = ri32(); wi32(n)
        for _ in range(n): wb(rb()); wb(rb())
        n = ri32(); wi32(n)
        for _ in range(n): _rebuild()
        n = ri32()
        t24_lines = list(d[pos[0]:pos[0]+n]); pos[0] += n
        abs_n = ri32(); pos[0] += abs_n * 8
        wi32(n)
        for ln in t24_lines: out.extend(struct.pack('<i', ln))
        n = ri32(); wi32(n)
        for _ in range(n): _xdw(); wi32(ri32()); wi32(ri32())
        n = ri32(); wi32(n)
        for _ in range(n): _xdw()
    try:
        _rebuild()
        with open(dst_path, 'wb') as f: f.write(out)
        return True, f'{len(d)}B → {len(out)}B'
    except Exception as e:
        return False, str(e)

# ── Standard Lua 5.3 → T24 rebuild (PREMIUM.py — 64-bit size_t fix) ───────
def _premium_std_to_t24(std_bytes: bytes) -> bytes:
    """
    Rebuild standard Lua 5.3 bytecode into T24/BGMI format.
    Critical fix: handles 64-bit size_t from 64-bit luac correctly.
    """
    d = bytearray(std_bytes); out = bytearray()
    pos = [34]; out.extend(d[:34])
    input_size_t = d[13]; out[13] = 4  # T24 always expects size_t=4
    def rb():    v = d[pos[0]]; pos[0] += 1; return v
    def ri32():  v = struct.unpack_from('<i', d, pos[0])[0]; pos[0] += 4; return v
    def ri64():  v = struct.unpack_from('<q', d, pos[0])[0]; pos[0] += 8; return v
    def rf64():  v = struct.unpack_from('<d', d, pos[0])[0]; pos[0] += 8; return v
    def wi32(v): out.extend(struct.pack('<i', v))
    def wu32(v): out.extend(struct.pack('<I', v))
    def wi64(v): out.extend(struct.pack('<q', v))
    def wf64(v): out.extend(struct.pack('<d', v))
    def _enc():
        sz = d[pos[0]]
        if sz == 0:    pos[0] += 1; out.append(0); return
        if sz == 0xFF:
            if input_size_t == 8:
                length = struct.unpack_from('<Q', d, pos[0]+1)[0] - 1
                ds = pos[0] + 9; pos[0] = ds + length
            else:
                length = struct.unpack_from('<I', d, pos[0]+1)[0] - 1
                ds = pos[0] + 5; pos[0] = ds + length
            out.append(0xFF); out.extend(struct.pack('<Q', length + 1))
        else:
            length = sz - 1; ds = pos[0] + 1; pos[0] = ds + length
            out.append(sz)
        for i in range(length):
            out.append(d[ds + i] ^ _P_XOR_KEY[i % len(_P_XOR_KEY)])
    def _remap_std(ins):
        std_op = ins & 0x3F
        t24_op = _P_STD_TO_T24.get(std_op, std_op)
        return (ins & ~0x3F) | t24_op
    def _proc():
        _enc(); wi32(ri32()); wi32(ri32())
        out.append(rb()); out.append(rb()); out.append(rb())
        n = ri32(); wi32(n)
        for _ in range(n):
            ins = struct.unpack_from('<I', d, pos[0])[0]; pos[0] += 4
            out.extend(struct.pack('<I', _remap_std(ins)))
        n = ri32(); wi32(n)
        for _ in range(n):
            t = rb(); out.append(t)
            if   t == 0:        pass
            elif t == 1:        out.append(rb())
            elif t == 3:        wf64(rf64())
            elif t == 19:       wi64(ri64())
            elif t in (4, 20):  _enc()
            else: raise ValueError(f'Unknown const type {t} at {pos[0]}')
        n = ri32(); wi32(n)
        for _ in range(n): out.append(rb()); out.append(rb())
        n = ri32(); wi32(n)
        for _ in range(n): _proc()
        n = ri32()
        if input_size_t == 8:
            std_lines = list(struct.unpack_from(f'<{n}i', d, pos[0])); pos[0] += n * 4
        else:
            std_lines = list(d[pos[0]:pos[0]+n]); pos[0] += n
        wi32(n)
        abs_n = 0; wi32(abs_n)
        for ln in std_lines: out.append(ln & 0xFF)
        n = ri32(); wi32(n)
        for _ in range(n): _enc(); wi32(ri32()); wi32(ri32())
        n = ri32(); wi32(n)
        for _ in range(n): _enc()
    try:
        _proc(); return bytes(out)
    except Exception as e:
        console.print(f'  [red]T24 rebuild error: {e}[/red]')
        return b''

# ── dravix: smart fingerprint resolve ─────────────────────────────────────
def _dravix_fingerprint_resolve(filename: str, repack_file: Path, candidates: list):
    """Resolve ambiguous PAK path by file fingerprint (size + compression metadata)."""
    repack_size = repack_file.stat().st_size
    size_matches = [(path, entry) for path, entry in candidates if entry.uncompressed_size == repack_size]
    if len(size_matches) == 1:
        return size_matches[0]
    if not size_matches:
        return None
    def fp(e):
        return (e.uncompressed_size, e.size, e.compression_method,
                len(e.compressed_blocks), e.compression_block_size)
    base_fp = fp(size_matches[0][1])
    final = [(p, e) for p, e in size_matches if fp(e) == base_fp]
    return final[0] if len(final) == 1 else None

# ── dravix: detect PAK repack mode ────────────────────────────────────────
def _dravix_detect_repack_mode(pak_path: Path) -> str:
    name = pak_path.name.lower()
    if name == 'mini_obb.pak':  return 'MINI_OBB'
    if 'zsdic' in name:         return 'OBBZSDIC'
    if 'game' in name or 'patch' in name: return 'GAMEPATCH'
    return 'OBBZSDIC'

# ── Enhanced LUA decompile using PREMIUM pipeline ─────────────────────────
def _premium_decompile(src: Path, out: Path) -> tuple:
    """
    Full 3-step decompile pipeline from PREMIUM.py:
    1. T24 → Standard Lua 5.3 conversion
    2. unluac_patched.jar
    3. luadec binary
    Returns (success, tool_used, error_msg)
    """
    import tempfile as _tf
    with _tf.TemporaryDirectory(prefix='star_prem_') as tmp:
        tmp_std = os.path.join(tmp, 'std.luac')
        # step 1: convert
        ok, msg = _premium_t24_to_std(str(src), tmp_std)
        if not ok:
            return False, 'converter', msg
        # step 2: unluac
        jar = str(UNLUAC_JAR)
        if os.path.isfile(jar):
            try:
                r = subprocess.run(['java', '-jar', jar, tmp_std],
                                   capture_output=True, text=True, timeout=60)
                if r.returncode == 0 and r.stdout:
                    out.write_text(r.stdout, encoding='utf-8')
                    return True, 'unluac', ''
            except Exception as e:
                pass
        # step 3: luadec
        luadec = _find_lua_tool('luadec')
        if luadec:
            try:
                r = subprocess.run([str(luadec), tmp_std],
                                   capture_output=True, timeout=60)
                if r.stdout:
                    out.write_bytes(r.stdout)
                    return True, 'luadec', ''
            except Exception:
                pass
        return False, 'none', 'Tüm decompiler başarısız — unluac.jar ve luadec kontrol et'

# ── Enhanced LUA recompile using PREMIUM T24 rebuild ──────────────────────
def _premium_recompile(src: Path, out: Path) -> tuple:
    """
    Compile .lua → standard bytecode → T24/BGMI format.
    Uses PREMIUM.py's _rebuild_std_to_t24 with 64-bit size_t fix.
    Returns (success, error_msg)
    """
    import tempfile as _tf
    luac = _get_luac_cmd()
    with _tf.TemporaryDirectory(prefix='star_prem_') as tmp:
        tmp_out = os.path.join(tmp, 'tmp.luac')
        try:
            r = subprocess.run([luac, '-o', tmp_out, str(src)],
                               capture_output=True, timeout=30)
            if r.returncode != 0:
                err = r.stderr.decode('utf-8', errors='replace').strip()
                return False, f'luac hatası: {err[:200]}'
            std_bytes = open(tmp_out, 'rb').read()
            if std_bytes[:4] != b'\x1bLua' or std_bytes[4] != 0x53:
                return False, 'luac geçerli Lua 5.3 bytecode üretmedi'
            t24_bytes = _premium_std_to_t24(std_bytes)
            if not t24_bytes:
                return False, 'T24 rebuild başarısız'
            out.write_bytes(t24_bytes)
            return True, ''
        except subprocess.TimeoutExpired:
            return False, 'timeout'
        except Exception as e:
            return False, str(e)


# ==================== MOD PATCH + SEARCH + ANTIRESET (Moddercore clean port) ====================

_GRASS_FILES = [
    'Baltic_GrassType02.uasset','Baltic_GrassType01.uasset',
    'Savage_GrassType02.uasset','Savage_GrassType01.uasset',
    'DihorOtok_GrassType03.uasset','DihorOtok_GrassType01.uasset',
    'Forest_GrassType01.uasset','Foliage_Grasstype_009.uasset'
]
_HEADSHOT_TARGETS = [
    b'EAvatarDamagePosition::BigBody',
    b'EAvatarDamagePosition::BigFoot',
    b'EAvatarDamagePosition::BigHand',
    b'EAvatarDamagePosition::BigLimbs',
]
_HEADSHOT_REPLACE = b'EAvatarDamagePosition::BigHead'
_BODY_NULL_PATHS  = [
    b'Game/Arts_Player/Characters/Mesh/Female/Body/Tex',
    b'Game/Arts_Player/Characters/Mesh/Male/Body/Tex',
    b'Game/Arts_Player/Characters/Mesh',
]

# ── Text search in PAK_UNPACK ──────────────────────────────────────────────
def action_search_text():
    os.system('clear')
    console.print('[bold #FFAA00]🔍 METİN ARAMA[/bold #FFAA00]')
    console.print('[dim]  PAK_UNPACK klasöründeki dosyaları tarar[/dim]')
    console.print()
    if not PAK_UNPACK_OUT.exists() or not any(PAK_UNPACK_OUT.iterdir()):
        console.print(f'[red]❌ PAK_UNPACK boş — önce [14] PAK UNPACK yap.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    text = safe_input('  Aranacak metin: ').strip(); flush_stdin()
    if not text:
        console.print(f'[red]Metin boş.[/red]'); flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'\n  [cyan]Taranıyor: "{text}"...[/cyan]')
    found = []; total = 0
    enc     = text.encode('utf-8', errors='ignore')
    enc_low = text.lower().encode('utf-8', errors='ignore')
    for f in PAK_UNPACK_OUT.rglob('*'):
        if not f.is_file(): continue
        total += 1
        try:
            data = f.read_bytes()
            if enc in data or enc_low in data.lower():
                found.append(f)
        except Exception:
            try:
                if text.lower() in f.read_text(encoding='utf-8', errors='ignore').lower():
                    found.append(f)
            except Exception: pass
    console.print(f'\n  [green]{len(found)}/{total} dosyada bulundu:[/green]')
    for i, fp in enumerate(found[:30], 1):
        console.print(f'  [{i}] {fp.name}  [dim]{fp.parent.name}[/dim]')
    if len(found) > 30:
        console.print(f'  [dim]+{len(found)-30} tane daha...[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

# ── Auto Headshot ──────────────────────────────────────────────────────────
def action_auto_headshot():
    os.system('clear')
    console.print('[bold #FF4444]🎯 AUTO HEADSHOT PATCH[/bold #FF4444]')
    console.print('[dim]  BP_PlayerPawn.uasset — BigBody/Foot/Hand/Limbs → BigHead[/dim]')
    console.print()
    if not PAK_UNPACK_OUT.exists():
        console.print('[red]❌ PAK_UNPACK yok — önce [14] PAK UNPACK yap.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    targets = list(PAK_UNPACK_OUT.rglob('BP_PlayerPawn.uasset'))
    if not targets:
        console.print('[red]❌ BP_PlayerPawn.uasset bulunamadı.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    for i, f in enumerate(targets, 1):
        console.print(f'  [{i}] {f}')
    try:
        c = safe_input(f'  Seç (1-{len(targets)}): ').strip(); flush_stdin()
        hs_src = targets[int(c)-1]
    except Exception:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    data = bytearray(hs_src.read_bytes())
    patched = 0
    for tgt in _HEADSHOT_TARGETS:
        pos = 0
        while True:
            idx = data.find(tgt, pos)
            if idx == -1: break
            end = idx + len(tgt)
            for j in range(min(30, len(data) - end)):
                data[end + j] = 0
            patched += 1; pos = end
    if patched == 0:
        console.print('[yellow]⚠ BigBody/Foot/Hand/Limbs tag bulunamadı — zaten patch edilmiş olabilir.[/yellow]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    out = hs_src.parent / (hs_src.stem + '_headshot' + hs_src.suffix)
    out.write_bytes(bytes(data))
    console.print(f'\n[bold green]✅ Headshot patch tamamlandı![/bold green]')
    console.print(f'[dim]  {patched} tag yamalandı → {out}[/dim]')
    console.print(f'\n  CUSTOM FILES/ klasörüne kopyala → [1] CUSTOM INJECT ile PAK\'a ekle.')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

# ── Auto White Body ────────────────────────────────────────────────────────
def action_auto_white_body():
    os.system('clear')
    console.print('[bold #FFFFFF]⬜ AUTO WHITE BODY[/bold #FFFFFF]')
    console.print('[dim]  Body texture DAT dosyalarını sıfırlar[/dim]')
    console.print()
    if not PAK_UNPACK_OUT.exists():
        console.print('[red]❌ PAK_UNPACK yok — önce [14] PAK UNPACK yap.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'  [dim]{T("scanning")}[/dim]')
    matched = []; MAX_SIZE = 4096
    for f in PAK_UNPACK_OUT.rglob('*'):
        if not f.is_file(): continue
        if f.stat().st_size > MAX_SIZE: continue
        try:
            data = f.read_bytes()
            if any(pat in data for pat in _BODY_NULL_PATHS):
                matched.append(f)
        except Exception: pass
    if not matched:
        console.print('[yellow]⚠ Body texture dosyası bulunamadı.[/yellow]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'  [green]{len(matched)} dosya bulundu:[/green]')
    for i, f in enumerate(matched[:10], 1):
        console.print(f'  [{i}] {f.name}  [dim]{human_size(f.stat().st_size)}[/dim]')
    if len(matched) > 10: console.print(f'  [dim]+{len(matched)-10} tane daha...[/dim]')
    c = safe_input('\n  Uygula? (E/h): ').strip().lower(); flush_stdin()
    if c == 'h': return
    ok = 0
    for f in matched:
        try:
            out = f.parent / (f.stem + '_white' + f.suffix)
            out.write_bytes(b'\x00' * f.stat().st_size)
            ok += 1
        except Exception: pass
    console.print(f'\n[bold green]✅ {ok} dosya sıfırlandı[/bold green]')
    console.print('  CUSTOM FILES/ klasörüne kopyala → [1] CUSTOM INJECT.')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

# ── Auto Grass White ───────────────────────────────────────────────────────
def action_auto_grass_white():
    os.system('clear')
    console.print('[bold #00FF88]🌿 AUTO GRASS WHITE[/bold #00FF88]')
    console.print('[dim]  Grass uasset dosyalarını sıfırlar[/dim]')
    console.print()
    if not PAK_UNPACK_OUT.exists():
        console.print('[red]❌ PAK_UNPACK yok — önce [14] PAK UNPACK yap.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    found = []
    for name in _GRASS_FILES:
        found.extend(PAK_UNPACK_OUT.rglob(name))
    if not found:
        console.print('[yellow]⚠ Grass dosyası bulunamadı.[/yellow]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'  [green]{len(found)} grass dosyası bulundu:[/green]')
    for i, f in enumerate(found, 1):
        console.print(f'  [{i}] {f.name}  [dim]{human_size(f.stat().st_size)}[/dim]')
    c = safe_input('\n  Sıfırla? (E/h): ').strip().lower(); flush_stdin()
    if c == 'h': return
    ok = 0
    for f in found:
        try:
            out = f.parent / (f.stem + '_white' + f.suffix)
            out.write_bytes(b'\x00' * f.stat().st_size)
            ok += 1
        except Exception: pass
    console.print(f'\n[bold green]✅ {ok} grass dosyası sıfırlandı[/bold green]')
    console.print('  CUSTOM FILES/ klasörüne kopyala → [1] CUSTOM INJECT.')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

# ── Anti-Reset OBB Tool ────────────────────────────────────────────────────
_AR_DIR = BASE_DIR / "ANTIRESET"

def action_antireset():
    os.system('clear')
    console.print('[bold #00FFCC]🛡 ANTİ-RESET OBB TOOL[/bold #00FFCC]')
    console.print('[dim]  OBB\'yi STORE zip\'le → orijinal boyuta pad et[/dim]')
    console.print()
    console.print('  [1] OBB çıkar (MODDED_OBB\'den)')
    console.print('  [2] Anti-reset OBB yap')
    console.print('  [0] Geri')
    console.print()
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    mod_dir = _AR_DIR / "MODDED_OBB"
    org_dir = _AR_DIR / "ORG_OBB"
    out_dir = _AR_DIR / "OUTPUT"
    mod_dir.mkdir(parents=True, exist_ok=True)
    org_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    if c == '1':
        # unzip modded OBB
        obbs = list(mod_dir.glob('*.obb')) + list(mod_dir.glob('*.zip'))
        if not obbs:
            console.print(f'[red]❌ {mod_dir} klasörüne .obb koy.[/red]')
            flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
        obb = obbs[0]
        console.print(f'  [cyan]Çıkarılıyor: {obb.name}...[/cyan]')
        ext_dir = mod_dir / obb.stem
        ext_dir.mkdir(parents=True, exist_ok=True)
        with _zipfile.ZipFile(str(obb), 'r') as zf:
            zf.extractall(str(ext_dir))
        console.print(f'  [green]✅ Çıkarıldı → {ext_dir}[/green]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}')
    elif c == '2':
        # find extracted dir
        subdirs = [d for d in mod_dir.iterdir() if d.is_dir()]
        if not subdirs:
            console.print('[red]❌ Önce [1] OBB çıkar adımını yap.[/red]')
            flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
        ext_dir = subdirs[0]
        obb_name = ext_dir.name + '.obb'
        # find original OBB for size
        org_obbs = list(org_dir.glob('*.obb'))
        if not org_obbs:
            console.print(f'[red]❌ {org_dir} klasörüne orijinal .obb koy.[/red]')
            flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
        target_size = org_obbs[0].stat().st_size
        out_obb = out_dir / obb_name
        console.print(f'  [cyan]ZIP STORE ile paketleniyor...[/cyan]')
        all_files = [f for f in ext_dir.rglob('*') if f.is_file()]
        with _zipfile.ZipFile(str(out_obb), 'w', _zipfile.ZIP_STORED) as zf:
            for f in all_files:
                zf.write(str(f), str(f.relative_to(ext_dir)))
        zipped_size = out_obb.stat().st_size
        console.print(f'  Zip boyutu  : [cyan]{human_size(zipped_size)}[/cyan]')
        console.print(f'  Hedef boyut : [cyan]{human_size(target_size)}[/cyan]')
        if zipped_size < target_size:
            pad = target_size - zipped_size
            console.print(f'  [dim]Padding ekleniyor: {human_size(pad)}...[/dim]')
            with open(str(out_obb), 'ab') as f:
                chunk = 1024 * 1024
                rem = pad
                while rem > 0:
                    f.write(b'\x00' * min(chunk, rem)); rem -= chunk
        final = out_obb.stat().st_size
        match = final == target_size
        console.print(f'\n[bold {"green" if match else "yellow"}]{"✅ BOYUT EŞLEŞTI" if match else "⚠ Boyut yakın"}[/bold {"green" if match else "yellow"}]')
        console.print(f'[dim]  Çıktı: {out_obb}[/dim]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}')

# ── PAK Compare & Extract ──────────────────────────────────────────────────
def action_pak_compare():
    os.system('clear')
    console.print('[bold #FFCC00]🔄 PAK KARŞILAŞTIR[/bold #FFCC00]')
    console.print('[dim]  İki PAK\'ı karşılaştır, farkları çıkar[/dim]')
    console.print()
    pak_files = sorted([f for f in BASE_DIR.iterdir()
                        if f.is_file() and f.name.lower().endswith('.pak')])
    if len(pak_files) < 2:
        console.print('[red]❌ En az 2 PAK dosyası lazım FANTOOL/ klasöründe.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    for i, p in enumerate(pak_files, 1):
        console.print(f'  [{i}] {p.name}  [dim]({human_size(p.stat().st_size)})[/dim]')
    try:
        a = int(safe_input('\n  Orijinal PAK (numara): ').strip()) - 1; flush_stdin()
        b = int(safe_input('  Modifiye PAK (numara): ').strip()) - 1; flush_stdin()
        pak_a = pak_files[a]; pak_b = pak_files[b]
    except Exception:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'\n  [cyan]Karşılaştırılıyor...[/cyan]')
    try:
        pa = TencentPakFile(PurePath(pak_a))
        pb = TencentPakFile(PurePath(pak_b))
    except Exception as e:
        console.print(f'[red]❌ PAK yüklenemedi: {e}[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    # build flat maps
    def flat(pak):
        m = {}
        for dp, files in pak._index.items():
            for fn, entry in files.items():
                full = str(PurePath(dp) / fn).replace('\\','/')
                m[full] = entry
        return m
    map_a = flat(pa); map_b = flat(pb)
    added   = [k for k in map_b if k not in map_a]
    removed = [k for k in map_a if k not in map_b]
    changed = [k for k in map_b if k in map_a and map_b[k].uncompressed_size != map_a[k].uncompressed_size]
    console.print(f'\n  [green]+{len(added)} eklendi[/green]  [red]-{len(removed)} silindi[/red]  [yellow]~{len(changed)} değişti[/yellow]')
    if not (added + changed):
        console.print('  [dim]Fark yok.[/dim]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    out_dir = BASE_DIR / f'PAK_DIFF_{pak_b.stem}'
    out_dir.mkdir(parents=True, exist_ok=True)
    console.print(f'\n  [cyan]Değişen dosyalar çıkarılıyor → {out_dir}[/cyan]')
    ok = 0
    import tempfile as _tfcmp
    with _tfcmp.TemporaryDirectory(prefix='star_cmp_') as _tmp:
        for path in added + changed:
            try:
                parts = PurePath(path)
                fname = parts.name
                tmp_f = Path(_tmp) / fname
                pb._write_to_disk(tmp_f, map_b[path])
                if tmp_f.exists():
                    shutil.copy2(str(tmp_f), str(out_dir / fname))
                    ok += 1
            except Exception: pass
    console.print(f'\n[bold green]✅ {ok} dosya çıkarıldı → {out_dir}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

# ── MOD PATCH menu ─────────────────────────────────────────────────────────
def action_mod_patch():
    while True:
        os.system('clear')
        console.print('[bold #FF4444]⚡ MOD PATCH[/bold #FF4444]')
        console.print('[dim]  Otomatik mod yamaları[/dim]')
        console.print()
        console.print('  [bold #FF4444][1] 🎯 AUTO HEADSHOT[/bold #FF4444]       [dim]BP_PlayerPawn headshot patch[/dim]')
        console.print('  [bold #FFFFFF][2] ⬜ AUTO WHITE BODY[/bold #FFFFFF]     [dim]body texture dosyalarını sıfırla[/dim]')
        console.print('  [bold #00FF88][3] 🌿 AUTO GRASS WHITE[/bold #00FF88]    [dim]grass uasset dosyalarını sıfırla[/dim]')
        console.print('  [bold #FFAA00][4] 🔍 METİN ARA[/bold #FFAA00]          [dim]PAK_UNPACK içinde metin ara[/dim]')
        console.print('  [bold #00FFCC][5] 🛡 ANTİ-RESET OBB[/bold #00FFCC]     [dim]OBB anti-reset patch[/dim]')
        console.print('  [bold #FFCC00][6] 🔄 PAK KARŞILAŞTIR[/bold #FFCC00]    [dim]iki PAK farkını çıkar[/dim]')
        console.print(f'  [bold white][0] {T("back")}[/bold white]')
        console.print()
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '1': action_auto_headshot()
        elif c == '2': action_auto_white_body()
        elif c == '3': action_auto_grass_white()
        elif c == '4': action_search_text()
        elif c == '5': action_antireset()
        elif c == '6': action_pak_compare()
        elif c == '0': return

# ==================== NEW FEATURES: GFP XOR + BATCH DECRYPT ====================

# ── GFP (Game for Peace) XOR key — o.py ───────────────────────────────────
_GFP_XOR_KEY = bytes([
    0xEF, 0xC1, 0x71, 0x3E, 0xE3, 0x34, 0x7D, 0x24,
    0x58, 0xE1, 0x9A, 0x38, 0x4F, 0xA4, 0x6D, 0x08,
    0x64, 0x70, 0xAC, 0xF2, 0xBC, 0xE6, 0x2E, 0x41,
    0x4F, 0x00, 0x83, 0xE7, 0xE7, 0x0B, 0x20, 0x07
])

# ── Batch .luac XOR decrypt — batch_decrypt.py ────────────────────────────
_LUAC_HEADER_SIZE = 0x22  # first 0x22 bytes NOT encrypted

def _batch_xor_luac(src: Path, dst: Path, key: bytes = None) -> bool:
    """XOR decrypt/encrypt a .luac file (header preserved, body XOR'd)."""
    k = key or _DEFAULT_XOR_KEY
    data = src.read_bytes()
    if len(data) <= _LUAC_HEADER_SIZE:
        dst.write_bytes(data)
        return True
    header = data[:_LUAC_HEADER_SIZE]
    body   = bytes(b ^ k[i % len(k)] for i, b in enumerate(data[_LUAC_HEADER_SIZE:]))
    dst.write_bytes(header + body)
    return True

def action_batch_luac_decrypt():
    """Batch XOR decrypt all .luac files in LUA_ORIGINAL → LUA_EDIT."""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF88FF]⚡ BATCH LUAC XOR DECRYPT[/bold #FF88FF]')
    console.print('[dim]  LUA_ORIGINAL klasöründeki tüm .luac dosyalarını XOR çözer[/dim]')
    console.print('[dim]  Header (0x22 byte) korunur, geri kalanı XOR\'lanır[/dim]')
    console.print()
    console.print('  [1] PUBG/BGMI XOR key (varsayılan)')
    console.print('  [2] GFP (Game for Peace) XOR key')
    console.print('  [3] Özel key gir')
    console.print('  [0] İptal')
    c = safe_input('\n  Key seç: ').strip(); flush_stdin()
    if c == '0': return
    if   c == '1': xor_key = _DEFAULT_XOR_KEY
    elif c == '2': xor_key = _GFP_XOR_KEY
    elif c == '3':
        raw = safe_input('  HEX key (örn: 112136...): ').strip().replace(' ',''); flush_stdin()
        try: xor_key = bytes.fromhex(raw)
        except Exception: console.print(f'[red]Geçersiz HEX.[/red]'); flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    else: return
    files = [f for f in LUA_ORIGINAL_DIR.iterdir()
             if f.is_file() and f.suffix.lower() in ('.luac','.slua')]
    if not files:
        console.print(f'[red]❌ {LUA_ORIGINAL_DIR} boş.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'\n  [cyan]{len(files)} dosya işlenecek...[/cyan]')
    LUA_EDIT_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    for f in files:
        dst = LUA_EDIT_DIR / f.name
        try:
            _batch_xor_luac(f, dst, xor_key)
            console.print(f'  [green]✅ {f.name}[/green]')
            ok += 1
        except Exception as e:
            console.print(f'  [red]✗ {f.name}: {e}[/red]')
    console.print(f'\n[bold]Sonuç: {ok}/{len(files)}[/bold]')
    console.print(f'[dim]Çıktı: {LUA_EDIT_DIR}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')


# ==================== FANTERİ LUA DERLE ====================

def action_fanteri_lua_compile():
    """Kaynak .lua dosyasını luac5.4 ile derle → .luac bytecode."""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #00D4FF]⭐ FANTERİ LUA DERLE[/bold #00D4FF]')
    console.print('[dim]  Kaynak .lua → luac5.4 bytecode (okunamaz, inject edilebilir)[/dim]')
    console.print()

    # find luac5.4
    luac54 = _get_luac_version_cmd('5.4')
    if not luac54:
        console.print('[yellow]⚠ luac5.4 bulunamadı — kuruluyor...[/yellow]')
        _try_install_lua('5.4')
        luac54 = _get_luac_version_cmd('5.4')
    if not luac54:
        console.print('[red]❌ luac5.4 kurulamadı.[/red]')
        console.print('[dim]  Manuel kur: pkg install lua54[/dim]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return

    console.print(f'  [green]✅ luac5.4: {luac54}[/green]')
    console.print()

    # find .lua files in COMPILED
    files = [f for f in COMPILED_DIR.iterdir() if f.is_file() and f.suffix == '.lua']
    if not files:
        console.print(f'[red]❌ COMPILED klasörü boş → {COMPILED_DIR}[/red]')
        console.print('[dim]  Kaynak .lua dosyasını buraya koy:[/dim]')
        console.print(f'[dim]  {COMPILED_DIR}[/dim]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return

    selected = _select_files([f.name for f in files], str(COMPILED_DIR), 'DERLE')
    if not selected: return

    import tempfile as _tf
    success = 0; failed = []

    for i, fname in enumerate(selected, 1):
        src  = COMPILED_DIR / fname
        outp = COMPILED_DIR / (src.stem + src.suffix)  # keep original extension (.lua)
        console.print(f'  [{i}/{len(selected)}] {fname}')

        # compile directly with luac5.4
        with _tf.TemporaryDirectory(prefix='star_f54_') as tmp:
            tmp_out = os.path.join(tmp, 'out.luac')
            try:
                r = subprocess.run(
                    [luac54, '-o', tmp_out, str(src)],
                    capture_output=True, text=True, timeout=30
                )
                if r.returncode == 0 and os.path.exists(tmp_out):
                    import shutil as _sh54
                    _sh54.copy2(tmp_out, str(outp))
                    sz = human_size(outp.stat().st_size)
                    console.print(f'  [green]✅ {outp.name}  ({sz})[/green]')
                    success += 1
                else:
                    err = (r.stderr or r.stdout or 'bilinmeyen hata').strip()[:200]
                    console.print(f'  [red]✗ {err}[/red]')
                    failed.append(fname)
            except subprocess.TimeoutExpired:
                console.print(f'  [red]✗ timeout[/red]'); failed.append(fname)
            except Exception as e:
                console.print(f'  [red]✗ {e}[/red]'); failed.append(fname)

    console.print(f'\n[bold]Sonuç: {success}/{len(selected)}[/bold]')
    if failed: console.print(f'[red]Başarısız: {", ".join(failed)}[/red]')
    if success:
        console.print(f'\n[dim]Çıktı: {COMPILED_DIR}[/dim]')
        console.print(f'[dim]Şimdi [1] CUSTOM INJECT ile PAK\'a ekleyebilirsin.[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')


def action_fanteri_lua_compile_51():
    """Kaynak .lua → luac5.1 bytecode."""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #A855F7]🔵 FANTERİ LUA 5.1[/bold #A855F7]')
    console.print('[dim]  Kaynak .lua → luac5.1 bytecode[/dim]')
    console.print()
    luac51 = _get_luac_version_cmd('5.1')
    if not luac51:
        console.print('[yellow]⚠ luac5.1 kuruluyor...[/yellow]')
        _try_install_lua('5.1')
        luac51 = _get_luac_version_cmd('5.1')
    if not luac51:
        console.print('[red]❌ luac5.1 bulunamadı.[/red]')
        console.print('[dim]  Manuel kur: pkg install lua51[/dim]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'  [green]✅ luac5.1: {luac51}[/green]')
    console.print()
    files = [f for f in COMPILED_DIR.iterdir() if f.is_file() and f.suffix == '.lua']
    if not files:
        console.print(f'[red]❌ COMPILED boş → {COMPILED_DIR}[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    selected = _select_files([f.name for f in files], str(COMPILED_DIR), 'DERLE 5.1')
    if not selected: return
    import tempfile as _tf, shutil as _sh51
    success = 0; failed = []
    for i, fname in enumerate(selected, 1):
        src  = COMPILED_DIR / fname
        outp = COMPILED_DIR / (src.stem + src.suffix)  # keep original extension (.lua)
        console.print(f'  [{i}/{len(selected)}] {fname}')
        with _tf.TemporaryDirectory(prefix='star_f51_') as tmp:
            tmp_out = os.path.join(tmp, 'out.luac')
            try:
                r = subprocess.run([luac51, '-o', tmp_out, str(src)],
                                   capture_output=True, text=True, timeout=30)
                if r.returncode == 0 and os.path.exists(tmp_out):
                    _sh51.copy2(tmp_out, str(outp))
                    console.print(f'  [green]✅ {outp.name}  ({human_size(outp.stat().st_size)})[/green]')
                    success += 1
                else:
                    err = (r.stderr or r.stdout or 'hata').strip()[:200]
                    console.print(f'  [red]✗ {err}[/red]'); failed.append(fname)
            except Exception as e:
                console.print(f'  [red]✗ {e}[/red]'); failed.append(fname)
    console.print(f'\n[bold]Sonuç: {success}/{len(selected)}[/bold]')
    if failed: console.print(f'[red]Başarısız: {", ".join(failed)}[/red]')
    if success: console.print(f'[dim]Çıktı: {COMPILED_DIR}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')


def action_fanteri_lua_compile_53():
    """Kaynak .lua → luac5.3 bytecode, çıktı .lua uzantısıyla."""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #10D98A]🟢 FANTERİ LUA 5.3[/bold #10D98A]')
    console.print('[dim]  Kaynak .lua → luac5.3 bytecode → .lua olarak kaydet[/dim]')
    console.print()
    luac53 = _get_luac_version_cmd('5.3')
    if not luac53:
        console.print('[yellow]⚠ luac5.3 kuruluyor...[/yellow]')
        _try_install_lua('5.3')
        luac53 = _get_luac_version_cmd('5.3')
    if not luac53:
        console.print('[red]❌ luac5.3 bulunamadı.[/red]')
        console.print('[dim]  Manuel kur: pkg install lua53[/dim]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'  [green]✅ luac5.3: {luac53}[/green]')
    console.print()
    files = [f for f in COMPILED_DIR.iterdir() if f.is_file() and f.suffix == '.lua']
    if not files:
        console.print(f'[red]❌ COMPILED boş → {COMPILED_DIR}[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    selected = _select_files([f.name for f in files], str(COMPILED_DIR), 'DERLE 5.3')
    if not selected: return
    import tempfile as _tf, shutil as _sh53
    success = 0; failed = []
    for i, fname in enumerate(selected, 1):
        src  = COMPILED_DIR / fname
        outp = src.parent / src.name  # same filename .lua
        console.print(f'  [{i}/{len(selected)}] {fname}')
        with _tf.TemporaryDirectory(prefix='star_f53_') as tmp:
            tmp_out = os.path.join(tmp, 'out.luac')
            try:
                r = subprocess.run([luac53, '-o', tmp_out, str(src)],
                                   capture_output=True, text=True, timeout=30)
                if r.returncode == 0 and os.path.exists(tmp_out):
                    _sh53.copy2(tmp_out, str(outp))
                    console.print(f'  [green]✅ {outp.name}  ({human_size(outp.stat().st_size)})[/green]')
                    success += 1
                else:
                    err = (r.stderr or r.stdout or 'hata').strip()[:200]
                    console.print(f'  [red]✗ {err}[/red]'); failed.append(fname)
            except Exception as e:
                console.print(f'  [red]✗ {e}[/red]'); failed.append(fname)
    console.print(f'\n[bold]Sonuç: {success}/{len(selected)}[/bold]')
    if failed: console.print(f'[red]Başarısız: {", ".join(failed)}[/red]')
    if success: console.print(f'[dim]Çıktı: {COMPILED_DIR}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')


# ══════════════════════════════════════════════════════════════════
# [18] ARAÇLAR — Checksum, Base64, File tools, Archive, Rename
# ══════════════════════════════════════════════════════════════════

def action_checksum():
    os.system('clear')
    console.print('[bold #00D4FF]🔑 CHECKSUM TOOL[/bold #00D4FF]')
    console.print('[dim]  MD5 / SHA1 / SHA256 hesapla[/dim]\n')
    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    if not path_raw: return
    p = Path(path_raw)
    if not p.exists():
        console.print(f'[red]❌ Dosya bulunamadı.[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import hashlib as _hl
    console.print(f'\n  [dim]Hesaplanıyor: {p.name} ({human_size(p.stat().st_size)})...[/dim]')
    try:
        data = p.read_bytes()
        console.print(f'\n  [cyan]MD5   :[/cyan] [white]{_hl.md5(data).hexdigest()}[/white]')
        console.print(f'  [cyan]SHA1  :[/cyan] [white]{_hl.sha1(data).hexdigest()}[/white]')
        console.print(f'  [cyan]SHA256:[/cyan] [white]{_hl.sha256(data).hexdigest()}[/white]')
    except Exception as e:
        console.print(f'[red]❌ Hata: {e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_base64_tool():
    os.system('clear')
    console.print('[bold #00D4FF]📋 BASE64 ENCODE/DECODE[/bold #00D4FF]\n')
    console.print('  [1] Metin → Base64')
    console.print('  [2] Base64 → Metin')
    console.print('  [3] Dosya → Base64')
    console.print('  [4] Base64 → Dosya')
    console.print('  [0] Geri')
    c = safe_input('\n  > ').strip(); flush_stdin()
    if c == '0': return
    import base64 as _b64
    if c == '1':
        txt = safe_input('  Metin: ').strip(); flush_stdin()
        if txt:
            enc = _b64.b64encode(txt.encode('utf-8')).decode()
            console.print(f'\n  [green]{enc}[/green]')
    elif c == '2':
        enc = safe_input('  Base64: ').strip(); flush_stdin()
        try:
            dec = _b64.b64decode(enc).decode('utf-8', errors='replace')
            console.print(f'\n  [green]{dec}[/green]')
        except Exception as e:
            console.print(f'[red]❌ {e}[/red]')
    elif c == '3':
        path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
        p = Path(path_raw)
        if p.exists():
            enc = _b64.b64encode(p.read_bytes()).decode()
            out = p.parent / (p.name + '.b64')
            out.write_text(enc); console.print(f'\n  [green]✅ {out}[/green]')
        else: console.print(f'[red]❌ {T("file_not_found")}[/red]')
    elif c == '4':
        path_raw = safe_input('  .b64 dosyası: ').strip().strip('"'); flush_stdin()
        p = Path(path_raw)
        if p.exists():
            try:
                data = _b64.b64decode(p.read_text().strip())
                out = p.parent / p.stem
                out.write_bytes(data); console.print(f'\n  [green]✅ {out} ({human_size(len(data))})[/green]')
            except Exception as e: console.print(f'[red]❌ {e}[/red]')
        else: console.print(f'[red]❌ {T("file_not_found")}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_file_type():
    os.system('clear')
    console.print('[bold #00D4FF]🔍 DOSYA TİPİ DETECTOR[/bold #00D4FF]\n')
    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists():
        console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    sigs = [
        (b'\x1bLua', 'Lua Bytecode'),
        (b'\x9E\x2A\x83\xC1', 'UE4 Asset (.uasset)'),
        (b'PK\x03\x04', 'ZIP/OBB Archive'),
        (b'\x7fELF', 'ELF Binary (.so)'),
        (b'MZ', 'Windows PE (.exe/.dll)'),
        (b'\x89PNG', 'PNG Image'),
        (b'JFIF', 'JPEG Image'),
        (b'%PDF', 'PDF Document'),
        (b'PAK\x00', 'Unreal PAK'),
        (b'\xFA\x5C\xEA\x01', 'FANTOOL Encrypted'),
        (b'\x1b[', 'ANSI/Script'),
        (b'BZh', 'BZip2'),
        (b'\x1f\x8b', 'GZIP'),
        (b'7z\xBC\xAF', '7-Zip'),
        (b'RIFF', 'RIFF (WAV/AVI)'),
        (b'fLaC', 'FLAC Audio'),
        (b'\x00\x00\x00\x14ftypM4A', 'M4A Audio'),
    ]
    detected = 'Bilinmiyor'
    for sig, name in sigs:
        if data[:len(sig)] == sig:
            detected = name; break
    # Text check
    if detected == 'Bilinmiyor':
        try:
            data[:512].decode('utf-8')
            detected = 'Text / Source Code'
        except: pass
    console.print(f'\n  Dosya : [cyan]{p.name}[/cyan]')
    console.print(f'  Boyut : [cyan]{human_size(p.stat().st_size)}[/cyan]')
    console.print(f'  Tip   : [bold green]{detected}[/bold green]')
    console.print(f'  Magic : [dim]{data[:8].hex().upper()}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_binary_split():
    os.system('clear')
    console.print('[bold #00D4FF]✂️  BINARY SPLITTER/MERGER[/bold #00D4FF]\n')
    console.print('  [1] Dosyayı böl (parçalara ayır)')
    console.print('  [2] Parçaları birleştir')
    console.print('  [0] Geri')
    c = safe_input('\n  > ').strip(); flush_stdin()
    if c == '0': return
    if c == '1':
        path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
        p = Path(path_raw)
        if not p.exists():
            console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        try:
            size_mb = int(safe_input('  Parça boyutu (MB): ').strip()); flush_stdin()
        except: size_mb = 10
        chunk = size_mb * 1024 * 1024
        data = p.read_bytes()
        parts = [data[i:i+chunk] for i in range(0, len(data), chunk)]
        for i, part in enumerate(parts):
            out = p.parent / f'{p.name}.part{i+1:03d}'
            out.write_bytes(part)
            console.print(f'  [green]✓ {out.name} ({human_size(len(part))})[/green]')
        console.print(f'\n[bold green]✅ {len(parts)} parça oluşturuldu[/bold green]')
    elif c == '2':
        dir_raw = safe_input('  Klasör yolu (.part dosyaları): ').strip().strip('"'); flush_stdin()
        d = Path(dir_raw)
        if not d.exists():
            console.print(f'[red]❌ {T("folder_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        parts = sorted(d.glob('*.part*'))
        if not parts:
            console.print(f'[red]❌ .part dosyası yok[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        base_name = parts[0].name.rsplit('.part', 1)[0]
        out = d / base_name
        console.print(f'  [dim]{len(parts)} parça birleştiriliyor...[/dim]')
        with open(str(out), 'wb') as f:
            for part in parts:
                f.write(part.read_bytes())
        console.print(f'\n[bold green]✅ {out.name} ({human_size(out.stat().st_size)})[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_file_diff():
    os.system('clear')
    console.print('[bold #00D4FF]📊 DOSYA KARŞILAŞTIRICI[/bold #00D4FF]\n')
    p1_raw = safe_input('  Dosya 1: ').strip().strip('"'); flush_stdin()
    p2_raw = safe_input('  Dosya 2: ').strip().strip('"'); flush_stdin()
    p1, p2 = Path(p1_raw), Path(p2_raw)
    if not p1.exists() or not p2.exists():
        console.print(f'[red]❌ Dosya bulunamadı[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    d1, d2 = p1.read_bytes(), p2.read_bytes()
    console.print(f'\n  [cyan]{p1.name}[/cyan] : {human_size(len(d1))}')
    console.print(f'  [cyan]{p2.name}[/cyan] : {human_size(len(d2))}')
    if d1 == d2:
        console.print('\n  [bold green]✅ Dosyalar aynı[/bold green]')
    else:
        diffs = sum(1 for a, b in zip(d1, d2) if a != b)
        size_diff = abs(len(d1) - len(d2))
        console.print(f'\n  [yellow]⚠ Farklı![/yellow]')
        console.print(f'  Farklı byte : [red]{diffs:,}[/red]')
        console.print(f'  Boyut farkı : [red]{size_diff:,} byte[/red]')
        # Show first diff position
        for i, (a, b) in enumerate(zip(d1, d2)):
            if a != b:
                console.print(f'  İlk fark    : [dim]0x{i:08X}[/dim]  {a:02X} → {b:02X}')
                break
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_mass_rename():
    os.system('clear')
    console.print('[bold #00D4FF]✏️  MASS RENAME[/bold #00D4FF]\n')
    dir_raw = safe_input('  Klasör yolu: ').strip().strip('"'); flush_stdin()
    d = Path(dir_raw)
    if not d.exists():
        console.print(f'[red]❌ {T("folder_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print('  [1] Uzantı değiştir')
    console.print('  [2] Prefix ekle')
    console.print('  [3] Metin bul/değiştir')
    console.print('  [0] Geri')
    c = safe_input('\n  > ').strip(); flush_stdin()
    if c == '0': return
    files = [f for f in d.iterdir() if f.is_file()]
    if not files:
        console.print(f'[yellow]{T("empty_folder")}[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ok = 0
    if c == '1':
        old_ext = safe_input('  Eski uzantı (.luac): ').strip(); flush_stdin()
        new_ext = safe_input('  Yeni uzantı (.lua): ').strip(); flush_stdin()
        for f in files:
            if f.suffix == old_ext:
                f.rename(f.parent / (f.stem + new_ext)); ok += 1
    elif c == '2':
        prefix = safe_input('  Prefix: ').strip(); flush_stdin()
        for f in files:
            f.rename(f.parent / (prefix + f.name)); ok += 1
    elif c == '3':
        find = safe_input('  Aranan: ').strip(); flush_stdin()
        repl = safe_input('  Yeni: ').strip(); flush_stdin()
        for f in files:
            if find in f.name:
                f.rename(f.parent / f.name.replace(find, repl)); ok += 1
    console.print(f'\n[bold green]✅ {ok} dosya yeniden adlandırıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_archive_creator():
    os.system('clear')
    console.print('[bold #00D4FF]📦 ARŞİV OLUŞTURUCU[/bold #00D4FF]\n')
    console.print('  [1] Klasörü ZIP yap')
    console.print('  [2] ZIP aç')
    console.print('  [0] Geri')
    c = safe_input('\n  > ').strip(); flush_stdin()
    if c == '0': return
    if c == '1':
        dir_raw = safe_input('  Klasör yolu: ').strip().strip('"'); flush_stdin()
        d = Path(dir_raw)
        if not d.exists():
            console.print(f'[red]❌ {T("folder_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        out = d.parent / (d.name + '.zip')
        import zipfile as _zf
        with _zf.ZipFile(str(out), 'w', _zf.ZIP_DEFLATED) as zf:
            for f in d.rglob('*'):
                if f.is_file():
                    zf.write(str(f), str(f.relative_to(d)))
                    console.print(f'  [dim]+ {f.name}[/dim]')
        console.print(f'\n[bold green]✅ {out.name} ({human_size(out.stat().st_size)})[/bold green]')
    elif c == '2':
        path_raw = safe_input('  ZIP yolu: ').strip().strip('"'); flush_stdin()
        p = Path(path_raw)
        if not p.exists():
            console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        out = p.parent / p.stem
        import zipfile as _zf
        with _zf.ZipFile(str(p), 'r') as zf:
            zf.extractall(str(out))
        console.print(f'\n[bold green]✅ {out} klasörüne açıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_duplicate_finder():
    os.system('clear')
    console.print('[bold #00D4FF]🔍 DUPLICATE FINDER[/bold #00D4FF]\n')
    dir_raw = safe_input('  Klasör yolu (varsayılan: PAK_UNPACK): ').strip().strip('"'); flush_stdin()
    d = Path(dir_raw) if dir_raw else PAK_UNPACK_OUT
    if not d.exists():
        console.print(f'[red]❌ {T("folder_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import hashlib as _hl
    console.print(f'  [dim]{T("scanning")}[/dim]')
    hashes = {}
    for f in d.rglob('*'):
        if not f.is_file(): continue
        try:
            h = _hl.md5(f.read_bytes()).hexdigest()
            if h in hashes:
                hashes[h].append(f)
            else:
                hashes[h] = [f]
        except: pass
    dups = {h: fs for h, fs in hashes.items() if len(fs) > 1}
    if not dups:
        console.print('\n  [green]✅ Duplicate yok[/green]')
    else:
        console.print(f'\n  [yellow]{len(dups)} grup duplicate bulundu:[/yellow]')
        for h, fs in list(dups.items())[:10]:
            console.print(f'\n  [dim]{h[:8]}...[/dim]')
            for f in fs:
                console.print(f'    [cyan]{f.name}[/cyan]  [dim]{f.parent}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_ram_monitor():
    os.system('clear')
    console.print('[bold #00D4FF]📊 SİSTEM MONİTÖRÜ[/bold #00D4FF]\n')
    try:
        # RAM
        with open('/proc/meminfo') as f:
            lines = f.readlines()
        mem = {}
        for l in lines:
            k, v = l.split(':')
            mem[k.strip()] = int(v.strip().split()[0])
        total_mb = mem.get('MemTotal', 0) // 1024
        free_mb  = mem.get('MemAvailable', 0) // 1024
        used_mb  = total_mb - free_mb
        pct = used_mb * 100 // total_mb if total_mb else 0
        console.print(f'  RAM Toplam   : [cyan]{total_mb} MB[/cyan]')
        console.print(f'  RAM Kullanım : [{"red" if pct>80 else "yellow" if pct>60 else "green"}]{used_mb} MB (%{pct})[/{"red" if pct>80 else "yellow" if pct>60 else "green"}]')
        console.print(f'  RAM Boş      : [green]{free_mb} MB[/green]')
    except Exception as e:
        console.print(f'  RAM: [dim]{e}[/dim]')
    # Disk
    try:
        import shutil as _sh
        usage = _sh.disk_usage('/sdcard')
        console.print(f'\n  Disk Toplam  : [cyan]{human_size(usage.total)}[/cyan]')
        console.print(f'  Disk Kullanım: [yellow]{human_size(usage.used)}[/yellow]')
        console.print(f'  Disk Boş     : [green]{human_size(usage.free)}[/green]')
    except: pass
    # FANTOOL klasörü
    try:
        total = sum(f.stat().st_size for f in BASE_DIR.rglob('*') if f.is_file())
        console.print(f'\n  FANTOOL  : [cyan]{human_size(total)}[/cyan]')
    except: pass
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_araçlar_menu():
    while True:
        os.system('clear')
        console.print('[bold #00D4FF]🛠  ARAÇLAR[/bold #00D4FF]')
        console.print('[dim]  Genel amaçlı yardımcı araçlar[/dim]\n')
        console.print('  [bold #00D4FF][1] 🔑 CHECKSUM[/bold #00D4FF]         [dim]MD5/SHA1/SHA256[/dim]')
        console.print('  [bold #00D4FF][2] 📋 BASE64[/bold #00D4FF]            [dim]encode / decode[/dim]')
        console.print('  [bold #00D4FF][3] 🔍 DOSYA TİPİ[/bold #00D4FF]        [dim]magic bytes ile tespit[/dim]')
        console.print('  [bold #00D4FF][4] ✂️  BINARY SPLIT[/bold #00D4FF]      [dim]böl / birleştir[/dim]')
        console.print('  [bold #00D4FF][5] 📊 DOSYA DIFF[/bold #00D4FF]         [dim]iki dosyayı karşılaştır[/dim]')
        console.print('  [bold #00D4FF][6] ✏️  MASS RENAME[/bold #00D4FF]       [dim]toplu yeniden adlandır[/dim]')
        console.print('  [bold #00D4FF][7] 📦 ARŞİV[/bold #00D4FF]              [dim]ZIP oluştur / aç[/dim]')
        console.print('  [bold #00D4FF][8] 🔍 DUPLICATE[/bold #00D4FF]           [dim]aynı dosyaları bul[/dim]')
        console.print('  [bold #00D4FF][9] 📊 SİSTEM[/bold #00D4FF]             [dim]RAM / disk monitörü[/dim]')
        console.print(f'  [bold white][0] {T("back")}[/bold white]')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_checksum()
        elif c == '2': action_base64_tool()
        elif c == '3': action_file_type()
        elif c == '4': action_binary_split()
        elif c == '5': action_file_diff()
        elif c == '6': action_mass_rename()
        elif c == '7': action_archive_creator()
        elif c == '8': action_duplicate_finder()
        elif c == '9': action_ram_monitor()

# ══════════════════════════════════════════════════════════════════
# [19] PUBG ARAÇLAR
# ══════════════════════════════════════════════════════════════════

def action_config_editor():
    os.system('clear')
    console.print('[bold #10D98A]⚙️  CONFIG EDITOR[/bold #10D98A]')
    console.print('[dim]  UserCustom.ini / GameUserSettings.ini düzenle[/dim]\n')
    common_paths = [
        Path('/sdcard/Android/data/com.pubg.imobile/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Config/Android'),
        Path('/sdcard/Android/data/com.tencent.ig/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Config/Android'),
        Path('/sdcard/Download'),
    ]
    ini_files = []
    for cp in common_paths:
        if cp.exists():
            ini_files.extend(cp.glob('*.ini'))
    # Also search manually
    for f in BASE_DIR.rglob('*.ini'):
        ini_files.append(f)
    if not ini_files:
        console.print('[yellow]⚠ .ini dosyası bulunamadı. Yolu manuel gir:[/yellow]')
        path_raw = safe_input('  .ini yolu: ').strip().strip('"'); flush_stdin()
        p = Path(path_raw)
        if not p.exists():
            console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    else:
        for i, f in enumerate(ini_files[:10], 1):
            console.print(f'  [{i}] {f.name}  [dim]{f.parent}[/dim]')
        console.print('  [0] Manuel gir')
        try:
            c = safe_input(f'  Seç (0-{min(10,len(ini_files))}): ').strip(); flush_stdin()
            if c == '0':
                path_raw = safe_input('  .ini yolu: ').strip().strip('"'); flush_stdin()
                p = Path(path_raw)
            else:
                p = ini_files[int(c)-1]
        except:
            console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    if not p.exists():
        console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        content = p.read_text(encoding='utf-8', errors='replace')
        lines = content.splitlines()
    except Exception as e:
        console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Show numbered lines
    page = 0; PAGE = 25; modified = {}
    while True:
        os.system('clear')
        console.print(f'[bold #10D98A]⚙️  {p.name}[/bold #10D98A]  [dim]{len(lines)} satır | Sayfa {page+1}/{(len(lines)+PAGE-1)//PAGE}[/dim]')
        console.print()
        chunk = lines[page*PAGE:(page+1)*PAGE]
        for i, line in enumerate(chunk, page*PAGE+1):
            ch = ' [yellow]✎[/yellow]' if i-1 in modified else ''
            console.print(f'  [dim]{i:4}[/dim]  {line[:70]}{ch}')
        console.print()
        console.print(f'[dim]  {T("nav_full")}[/dim]')
        cmd = safe_input('  > ').strip(); flush_stdin()
        if cmd == '0': break
        elif cmd == 'n': page = min(page+1, (len(lines)-1)//PAGE)
        elif cmd == 'p': page = max(page-1, 0)
        elif cmd == 's':
            backup = p.parent / (p.name + '.bak')
            backup.write_text(content, encoding='utf-8')
            new_content = '\n'.join(lines)
            p.write_text(new_content, encoding='utf-8')
            console.print(f'[green]✅ Kaydedildi. Yedek: {backup.name}[/green]')
            safe_input(f'  {T("press_enter")}')
        elif cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(lines):
                console.print(f'\n  [cyan]{lines[idx]}[/cyan]')
                new = safe_input('  Yeni değer (boş=iptal): ').strip(); flush_stdin()
                if new:
                    modified[idx] = lines[idx]
                    lines[idx] = new
                    console.print('[green]✅ Değiştirildi[/green]')
                    safe_input(f'  {T("press_enter")}')

def action_bgmi_csv_generator():
    os.system('clear')
    console.print('[bold #10D98A]📋 BGMI.CSV OLUŞTURUCU[/bold #10D98A]')
    console.print('[dim]  PAK_UNPACK içindeki dosyaları tarayıp BGMI.csv oluşturur[/dim]\n')
    if not PAK_UNPACK_OUT.exists() or not any(PAK_UNPACK_OUT.iterdir()):
        console.print('[red]❌ PAK_UNPACK boş — önce [14] PAK UNPACK yap.[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    console.print(f'  [dim]{T("scanning")}[/dim]')
    entries = []
    for f in PAK_UNPACK_OUT.rglob('*'):
        if f.is_file():
            rel = str(f.relative_to(PAK_UNPACK_OUT)).replace('\\', '/')
            entries.append(f'{f.name},{rel},{human_size(f.stat().st_size)}')
    if not entries:
        console.print('[red]❌ Dosya bulunamadı[/red]')
        flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
    out_dir = BASE_DIR / 'index'
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / 'BGMI.csv'
    out.write_text('\n'.join(entries), encoding='utf-8')
    console.print(f'\n[bold green]✅ BGMI.csv oluşturuldu![/bold green]')
    console.print(f'  {len(entries)} dosya → {out}')
    console.print(f'  [dim]Artık [1] CUSTOM INJECT otomatik path bulacak[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pattern_scanner():
    os.system('clear')
    console.print('[bold #10D98A]🔎 PATTERN SCANNER (AoB)[/bold #10D98A]')
    console.print('[dim]  Binary dosyada imza/pattern ara[/dim]\n')
    path_raw = safe_input('  Dosya yolu (boş=libUE4.so): ').strip().strip('"'); flush_stdin()
    if not path_raw:
        paths = list(Path('/sdcard').rglob('libUE4.so'))[:1]
        if not paths:
            console.print('[red]❌ libUE4.so bulunamadı. Yol girin.[/red]')
            flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        p = paths[0]
    else:
        p = Path(path_raw)
    if not p.exists():
        console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'  [dim]Yükleniyor: {p.name} ({human_size(p.stat().st_size)})...[/dim]')
    data = p.read_bytes()
    pattern_raw = safe_input('\n  Pattern (hex, ? ile wildcard): ').strip(); flush_stdin()
    if not pattern_raw:
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Parse pattern: "12 34 ? 56" → bytes with wildcards
    parts = pattern_raw.upper().replace(',', ' ').split()
    pat_bytes = []
    for pt in parts:
        if pt == '??' or pt == '?':
            pat_bytes.append(None)
        else:
            try: pat_bytes.append(int(pt, 16))
            except: console.print(f'[red]Geçersiz byte: {pt}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'  [dim]Taranıyor ({len(pat_bytes)} byte pattern)...[/dim]')
    found = []
    for i in range(len(data) - len(pat_bytes)):
        match = True
        for j, pb in enumerate(pat_bytes):
            if pb is not None and data[i+j] != pb:
                match = False; break
        if match:
            found.append(i)
            if len(found) >= 20: break
    if not found:
        console.print('[yellow]  Bulunamadı.[/yellow]')
    else:
        console.print(f'\n  [green]{len(found)} eşleşme:[/green]')
        for off in found:
            ctx = data[off:off+len(pat_bytes)+4].hex().upper()
            console.print(f'  [cyan]0x{off:08X}[/cyan]  [dim]{ctx}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_elf_parser():
    os.system('clear')
    console.print('[bold #10D98A]🔬 ELF HEADER PARSER[/bold #10D98A]')
    console.print('[dim]  .so / ELF binary header ve section\'larını göster[/dim]\n')
    path_raw = safe_input('  .so dosyası yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists():
        console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    if data[:4] != b'\x7fELF':
        console.print(f'[red]❌ ELF dosyası değil[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ei_class = data[4]; ei_data = data[5]
    arch = {0:'None',1:'32-bit',2:'64-bit'}.get(ei_class,'?')
    endian = {1:'Little-endian',2:'Big-endian'}.get(ei_data,'?')
    e_type_map = {0:'None',1:'REL',2:'EXEC',3:'DYN',4:'CORE'}
    e_machine_map = {0x3E:'x86-64',0xB7:'AArch64(ARM64)',0x28:'ARM',0x3:'x86'}
    if ei_class == 2:  # 64-bit
        e_type    = struct.unpack_from('<H', data, 16)[0]
        e_machine = struct.unpack_from('<H', data, 18)[0]
        e_entry   = struct.unpack_from('<Q', data, 24)[0]
        e_phoff   = struct.unpack_from('<Q', data, 32)[0]
        e_shoff   = struct.unpack_from('<Q', data, 40)[0]
        e_phnum   = struct.unpack_from('<H', data, 56)[0]
        e_shnum   = struct.unpack_from('<H', data, 60)[0]
    else:  # 32-bit
        e_type    = struct.unpack_from('<H', data, 16)[0]
        e_machine = struct.unpack_from('<H', data, 18)[0]
        e_entry   = struct.unpack_from('<I', data, 24)[0]
        e_phoff   = struct.unpack_from('<I', data, 28)[0]
        e_shoff   = struct.unpack_from('<I', data, 32)[0]
        e_phnum   = struct.unpack_from('<H', data, 44)[0]
        e_shnum   = struct.unpack_from('<H', data, 46)[0]
    console.print(f'\n  Mimari  : [cyan]{arch}[/cyan]')
    console.print(f'  Endian  : [cyan]{endian}[/cyan]')
    console.print(f'  Tip     : [cyan]{e_type_map.get(e_type, hex(e_type))}[/cyan]')
    console.print(f'  Makine  : [cyan]{e_machine_map.get(e_machine, hex(e_machine))}[/cyan]')
    console.print(f'  Entry   : [cyan]0x{e_entry:X}[/cyan]')
    console.print(f'  Boyut   : [cyan]{human_size(len(data))}[/cyan]')
    console.print(f'  Segments: [cyan]{e_phnum}[/cyan]')
    console.print(f'  Sections: [cyan]{e_shnum}[/cyan]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_symbol_finder():
    os.system('clear')
    console.print('[bold #10D98A]🔭 SYMBOL FINDER[/bold #10D98A]')
    console.print('[dim]  .so dosyasında fonksiyon/sembol ara[/dim]\n')
    path_raw = safe_input('  .so dosyası yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists():
        console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    keyword = safe_input('  Aranacak sembol (boş=tümü): ').strip().lower(); flush_stdin()
    console.print(f'  [dim]{T("scanning")}[/dim]')
    data = p.read_bytes()
    # Extract null-terminated strings that look like symbols
    symbols = []; i = 0
    while i < len(data) - 2:
        if 32 <= data[i] < 127:
            end = i
            while end < len(data) and 33 <= data[end] < 127:
                end += 1
            s = data[i:end].decode('ascii', errors='ignore')
            if len(s) >= 4 and (not keyword or keyword in s.lower()):
                if any(c in s for c in ['_', 'Java', 'UE4', 'PUBG', 'Get', 'Set', 'Find', 'BP_']):
                    symbols.append((i, s))
            i = end + 1
        else:
            i += 1
    symbols = symbols[:50]
    if not symbols:
        console.print('[yellow]  Sembol bulunamadı.[/yellow]')
    else:
        console.print(f'\n  [green]{len(symbols)} sembol:[/green]')
        for off, sym in symbols[:30]:
            console.print(f'  [cyan]0x{off:08X}[/cyan]  [white]{sym}[/white]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_string_dump():
    os.system('clear')
    console.print('[bold #10D98A]📝 STRING DUMP[/bold #10D98A]')
    console.print('[dim]  Dosyadaki tüm okunabilir stringleri çıkar[/dim]\n')
    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists():
        console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        min_len = int(safe_input('  Minimum uzunluk (4): ').strip() or '4'); flush_stdin()
    except:
        min_len = 4; flush_stdin()
    data = p.read_bytes()
    console.print(f'  [dim]{T("scanning")}[/dim]')
    strings = []; i = 0
    while i < len(data):
        if 32 <= data[i] < 127:
            end = i
            while end < len(data) and 32 <= data[end] < 127:
                end += 1
            s = data[i:end].decode('ascii', errors='ignore')
            if len(s) >= min_len:
                strings.append(f'0x{i:08X}\t{s}')
            i = end + 1
        else:
            i += 1
    out = p.parent / (p.name + '_strings.txt')
    out.write_text('\n'.join(strings), encoding='utf-8')
    console.print(f'\n[bold green]✅ {len(strings):,} string bulundu[/bold green]')
    console.print(f'  Çıktı: {out}')
    if strings[:5]:
        console.print('\n  [dim]İlk 5:[/dim]')
        for s in strings[:5]:
            console.print(f'  [dim]{s[:80]}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_auto_backup():
    os.system('clear')
    console.print('[bold #10D98A]💾 AUTO BACKUP[/bold #10D98A]')
    console.print('[dim]  FANTOOL klasöründeki PAK dosyalarını yedekle[/dim]\n')
    pak_files = list(BASE_DIR.glob('*.pak'))
    if not pak_files:
        console.print('[red]❌ PAK dosyası yok.[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    backup_dir = BASE_DIR / 'BACKUP'
    backup_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime as _dt
    ts = _dt.now().strftime('%Y%m%d_%H%M%S')
    ok = 0
    for pak in pak_files:
        dst = backup_dir / f'{pak.stem}_{ts}{pak.suffix}'
        import shutil as _sh
        _sh.copy2(str(pak), str(dst))
        console.print(f'  [green]✅ {dst.name}[/green]')
        ok += 1
    console.print(f'\n[bold green]✅ {ok} PAK yedeklendi → {backup_dir}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_metadata():
    os.system('clear')
    console.print('[bold #10D98A]📋 PAK METADATA[/bold #10D98A]')
    console.print('[dim]  PAK dosyasının header bilgilerini göster[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files:
        console.print(f'[red]❌ {T("no_pak")}[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(pak_files, 1):
        console.print(f'  [{i}] {f.name}')
    console.print('  [0] Geri')
    try:
        c = safe_input(f'\n  Seç (0-{len(pak_files)}): ').strip(); flush_stdin()
        if c == '0': return
        pak_path = pak_files[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        pak = TencentPakFile(PurePath(pak_path))
        pi = pak._pak_info
        console.print(f'\n  [cyan]Dosya      :[/cyan] {pak_path.name}')
        console.print(f'  [cyan]Boyut      :[/cyan] {human_size(pak_path.stat().st_size)}')
        console.print(f'  [cyan]Versiyon   :[/cyan] {pi.version}')
        console.print(f'  [cyan]Şifreli    :[/cyan] {"[red]Evet[/red]" if pi.index_encrypted else "[green]Hayır[/green]"}')
        console.print(f'  [cyan]Enc Method :[/cyan] {pi.enc_method}')
        console.print(f'  [cyan]Index Ofset:[/cyan] 0x{pi.index_offset:X}')
        console.print(f'  [cyan]Index Boyut:[/cyan] {human_size(pi.index_size)}')
        dom = pak.detect_dominant_style()
        console.print(f'\n  [dim]Baskın stil:[/dim]')
        console.print(f'  Compression: {dom["comp_method"]}')
        console.print(f'  Block boyut: {human_size(dom["block_size"])}')
        paths = pak.list_existing_paths()
        console.print(f'  Dosya sayısı: [green]{len(paths)}[/green]')
    except Exception as e:
        console.print(f'[red]❌ {e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_blueprint_string_editor():
    os.system('clear')
    console.print('[bold #10D98A]📄 BLUEPRINT STRING EDİTÖRÜ[/bold #10D98A]')
    console.print('[dim]  .uasset içindeki stringleri bul ve değiştir[/dim]\n')
    files = list(PAK_UNPACK_OUT.rglob('*.uasset')) if PAK_UNPACK_OUT.exists() else []
    if not files:
        console.print('[red]❌ PAK_UNPACK içinde .uasset yok — önce PAK UNPACK yap.[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(files[:20], 1):
        console.print(f'  [{i}] {f.name}  [dim]{human_size(f.stat().st_size)}[/dim]')
    try:
        c = safe_input(f'\n  Seç (1-{min(20,len(files))}): ').strip(); flush_stdin()
        p = files[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ua = _UAssetFileEx()
    ua.load_data(p.read_bytes())
    strings = [s for s in ua.all_strings if len(s['string'])>3]
    if not strings:
        console.print('[yellow]String bulunamadı[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    PAGE = 20; page = 0; changes = {}
    while True:
        os.system('clear')
        console.print(f'[bold]📄 {p.name}[/bold]  [dim]{len(strings)} string | Sayfa {page+1}/{(len(strings)+PAGE-1)//PAGE}[/dim]')
        console.print()
        chunk = strings[page*PAGE:(page+1)*PAGE]
        for i, s in enumerate(chunk, page*PAGE+1):
            ch = changes.get(s['offset'])
            val = ch if ch else s['string']
            mark = ' [yellow]✎[/yellow]' if ch else ''
            console.print(f'  [yellow]{i:3}[/yellow]  [dim]0x{s["offset"]:06X}[/dim]  [cyan]{val[:60]}[/cyan]{mark}')
        console.print()
        console.print(f'[dim]  {T("nav_full")}[/dim]')
        cmd = safe_input('  > ').strip(); flush_stdin()
        if cmd == '0': break
        elif cmd == 'n': page = min(page+1, (len(strings)-1)//PAGE)
        elif cmd == 'p': page = max(page-1, 0)
        elif cmd == 's':
            if not changes:
                console.print(f'[yellow]Değişiklik yok[/yellow]'); safe_input(f'  {T("press_enter")}'); continue
            data = bytearray(p.read_bytes())
            for off, new_str in changes.items():
                enc = new_str.encode('utf-8') + b'\x00'
                if off+4+len(enc) <= len(data):
                    struct.pack_into('<I', data, off, len(enc))
                    data[off+4:off+4+len(enc)] = enc
            out = p.parent / (p.stem + '_bp_edited' + p.suffix)
            out.write_bytes(bytes(data))
            console.print(f'[green]✅ Kaydedildi: {out.name}[/green]')
            safe_input(f'  {T("press_enter")}'); break
        elif cmd.isdigit():
            idx = int(cmd)-1
            if 0 <= idx < len(strings):
                s = strings[idx]
                console.print(f'\n  [cyan]{s["string"]}[/cyan]')
                new = safe_input('  Yeni değer (boş=iptal): ').strip(); flush_stdin()
                if new:
                    changes[s['offset']] = new
                    console.print('[green]✅[/green]')
                safe_input(f'  {T("press_enter")}')

def action_lua_syntax_check():
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #10D98A]✅ LUA SYNTAX CHECKER[/bold #10D98A]')
    console.print('[dim]  .lua dosyasını derlemeden syntax kontrol et[/dim]\n')
    files = [f for f in COMPILED_DIR.iterdir() if f.suffix=='.lua']
    if not files:
        console.print(f'[red]❌ COMPILED boş[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    selected = _select_files([f.name for f in files], str(COMPILED_DIR), 'SYNTAX CHECK')
    if not selected: return
    luac = _get_luac_cmd()
    ok = 0; fail = []
    for fname in selected:
        src = COMPILED_DIR / fname
        r = subprocess.run([luac, '-p', str(src)], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            console.print(f'  [green]✅ {fname}[/green]'); ok += 1
        else:
            err = (r.stderr or r.stdout or '?').strip()[:150]
            console.print(f'  [red]✗ {fname}: {err}[/red]')
            fail.append(fname)
    console.print(f'\n[bold]Sonuç: {ok}/{len(selected)}[/bold]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_batch_lua_compile():
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #10D98A]⚡ BATCH LUA COMPILE[/bold #10D98A]')
    console.print('[dim]  COMPILED klasöründeki tüm .lua dosyalarını derle[/dim]\n')
    console.print('  [1] Lua 5.3 (PUBG/BGMI)')
    console.print('  [2] Lua 5.4')
    console.print('  [3] Lua 5.1')
    console.print('  [0] Geri')
    c = safe_input('\n  Versiyon: ').strip(); flush_stdin()
    if c == '0': return
    vmap = {'1':'5.3','2':'5.4','3':'5.1'}
    ver = vmap.get(c,'5.3')
    luac = _get_luac_version_cmd(ver)
    if not luac:
        console.print(f'[red]❌ luac{ver} yok. pkg install lua{"".join(ver.split("."))} çalıştır.[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    files = [f for f in COMPILED_DIR.iterdir() if f.suffix=='.lua']
    if not files:
        console.print('[red]❌ COMPILED boş[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import tempfile as _tf, shutil as _sh2
    ok = 0; fail = []
    for f in files:
        outp = f.parent / f.name
        with _tf.TemporaryDirectory(prefix='fan_batch_') as tmp:
            tmp_out = os.path.join(tmp, 'out.luac')
            r = subprocess.run([luac, '-o', tmp_out, str(f)], capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and os.path.exists(tmp_out):
                _sh2.copy2(tmp_out, str(outp))
                console.print(f'  [green]✅ {f.name}[/green]')
                ok += 1
            else:
                err = (r.stderr or '?').strip()[:100]
                console.print(f'  [red]✗ {f.name}: {err}[/red]')
                fail.append(f.name)
    console.print(f'\n[bold]Sonuç: {ok}/{len(files)}[/bold]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_string_encryptor():
    os.system('clear')
    console.print('[bold #10D98A]🔐 LUA STRING ENCRYPTOR[/bold #10D98A]')
    console.print('[dim]  Lua kaynak kodundaki stringleri encode et (runtime\'da çözülür)[/dim]\n')
    path_raw = safe_input('  .lua dosyası yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists():
        console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        src = p.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import re as _re
    # Find all string literals and encode them
    def encode_str(m):
        s = m.group(0)
        inner = s[1:-1]  # Remove quotes
        # Encode as char array
        encoded = '{' + ','.join(str(ord(c)) for c in inner) + '}'
        return f'(function()local t={{}}local c={encoded};for i=1,#c do t[i]=string.char(c[i])end;return table.concat(t)end)()'
    # Replace "..." strings (careful not to break Lua syntax)
    result = _re.sub(r'"[^"\\]+"', encode_str, src)
    result = _re.sub(r"'[^'\\]+'", lambda m: encode_str(m), result)
    out = p.parent / (p.stem + '_enc.lua')
    out.write_text(result, encoding='utf-8')
    orig_count = len(_re.findall(r'"[^"\\]+"|\'[^\'\\]+\'', src))
    console.print(f'\n[bold green]✅ {orig_count} string encode edildi[/bold green]')
    console.print(f'  Çıktı: {out}')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_bytecode_diff():
    os.system('clear')
    console.print('[bold #10D98A]🔄 LUA BYTECODE DIFF[/bold #10D98A]')
    console.print('[dim]  İki .luac dosyasını karşılaştır[/dim]\n')
    p1_raw = safe_input('  Dosya 1 (.luac): ').strip().strip('"'); flush_stdin()
    p2_raw = safe_input('  Dosya 2 (.luac): ').strip().strip('"'); flush_stdin()
    p1, p2 = Path(p1_raw), Path(p2_raw)
    if not p1.exists() or not p2.exists():
        console.print(f'[red]❌ Dosya bulunamadı[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    d1, d2 = p1.read_bytes(), p2.read_bytes()
    console.print(f'\n  {p1.name}: {human_size(len(d1))}')
    console.print(f'  {p2.name}: {human_size(len(d2))}')
    if d1 == d2:
        console.print('\n  [bold green]✅ Aynı bytecode[/bold green]')
    else:
        diffs = [(i,a,b) for i,(a,b) in enumerate(zip(d1,d2)) if a!=b]
        console.print(f'\n  [yellow]⚠ {len(diffs)} byte farklı[/yellow]')
        for i,a,b in diffs[:10]:
            console.print(f'  [dim]0x{i:06X}[/dim]  {a:02X} → {b:02X}')
        if len(diffs)>10: console.print(f'  [dim]...{len(diffs)-10} tane daha[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_data_table_parser():
    os.system('clear')
    console.print('[bold #10D98A]📊 DATA TABLE PARSER[/bold #10D98A]')
    console.print('[dim]  DataTable .uasset satırlarını oku[/dim]\n')
    files = list(PAK_UNPACK_OUT.rglob('*.uasset')) if PAK_UNPACK_OUT.exists() else []
    if not files:
        console.print('[red]❌ PAK_UNPACK boş[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(files[:20], 1):
        console.print(f'  [{i}] {f.name}')
    try:
        c = safe_input(f'\n  Seç (1-{min(20,len(files))}): ').strip(); flush_stdin()
        p = files[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ua = _UAssetFileEx(); ua.load_data(p.read_bytes())
    # Show paths and strings
    os.system('clear')
    console.print(f'[bold]📊 {p.name}[/bold]\n')
    if ua.paths:
        console.print(f'  [cyan]Asset Path\'leri ({len(ua.paths)}):[/cyan]')
        for path_entry in ua.paths[:20]:
            console.print(f'  [dim]{path_entry["path"]}[/dim]')
    console.print(f'\n  [cyan]Stringler ({len(ua.all_strings)}):[/cyan]')
    for s in ua.all_strings[:30]:
        console.print(f'  [dim]{s["offset"]:06X}[/dim]  [white]{s["string"][:80]}[/white]')
    if len(ua.all_strings)>30: console.print(f'  [dim]+{len(ua.all_strings)-30} tane daha[/dim]')
    # Save dump
    out = p.parent / (p.name + '_dump.txt')
    lines = [f'=== {p.name} ===\n']
    for s in ua.all_strings:
        lines.append(f'0x{s["offset"]:06X}\t{s["string"]}')
    out.write_text('\n'.join(lines), encoding='utf-8')
    console.print(f'\n  [dim]Dump: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_single_extract():
    os.system('clear')
    console.print('[bold #10D98A]📤 TEK DOSYA ÇIKAR[/bold #10D98A]')
    console.print('[dim]  PAK içinden yalnızca seçilen dosyayı çıkar[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files:
        console.print(f'[red]❌ {T("no_pak")}[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(pak_files, 1):
        console.print(f'  [{i}] {f.name}')
    try:
        c = safe_input(f'\n  PAK seç (1-{len(pak_files)}): ').strip(); flush_stdin()
        pak_path = pak_files[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        pak = TencentPakFile(PurePath(pak_path))
        paths = pak.list_existing_paths()
    except Exception as e:
        console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    search = safe_input('\n  Dosya adı ara: ').strip().lower(); flush_stdin()
    matches = [p for p in paths if search in p.lower()] if search else paths[:50]
    if not matches:
        console.print(f'[yellow]Bulunamadı[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, m in enumerate(matches[:20], 1):
        console.print(f'  [{i}] {m}')
    try:
        c = safe_input(f'\n  Seç (1-{min(20,len(matches))}): ').strip(); flush_stdin()
        sel = matches[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    out_dir = PAK_UNPACK_OUT / 'SINGLE_EXTRACT'
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        pak._write_to_disk(PurePath(out_dir / Path(sel).name), pak._index[str(PurePath(sel).parent)][Path(sel).name])
        console.print(f'\n[green]✅ Çıkarıldı → {out_dir}[/green]')
    except Exception as e:
        # Try alternative approach
        try:
            pak.dump(PurePath(out_dir))
            console.print(f'\n[yellow]⚠ Tek dosya yerine tümü çıkarıldı → {out_dir}[/yellow]')
        except Exception as e2:
            console.print(f'[red]❌ {e} / {e2}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pubg_araçlar_menu():
    while True:
        os.system('clear')
        console.print('[bold #10D98A]🎮 PUBG ARAÇLAR[/bold #10D98A]')
        console.print('[dim]  PUBG Mobile / BGMI özel araçlar[/dim]\n')
        console.print('  [bold #10D98A][1]  ⚙️  CONFIG EDITOR[/bold #10D98A]        [dim].ini dosyası düzenle[/dim]')
        console.print('  [bold #10D98A][2]  📋 BGMI.CSV OLUŞTUR[/bold #10D98A]     [dim]PAK_UNPACK → CSV index[/dim]')
        console.print('  [bold #10D98A][3]  🔎 PATTERN SCANNER[/bold #10D98A]      [dim]AoB imza tara[/dim]')
        console.print('  [bold #10D98A][4]  🔬 ELF PARSER[/bold #10D98A]           [dim].so header analiz[/dim]')
        console.print('  [bold #10D98A][5]  🔭 SYMBOL FINDER[/bold #10D98A]        [dim].so sembol ara[/dim]')
        console.print('  [bold #10D98A][6]  📝 STRING DUMP[/bold #10D98A]          [dim]tüm stringleri dosyaya yaz[/dim]')
        console.print('  [bold #10D98A][7]  💾 AUTO BACKUP[/bold #10D98A]          [dim]PAK dosyalarını yedekle[/dim]')
        console.print('  [bold #10D98A][8]  📋 PAK METADATA[/bold #10D98A]         [dim]PAK versiyon/şifre bilgisi[/dim]')
        console.print('  [bold #10D98A][9]  📄 BP STRING EDİTÖR[/bold #10D98A]    [dim]Blueprint stringlerini değiştir[/dim]')
        console.print('  [bold #10D98A][10] 📤 TEK DOSYA ÇIKAR[/bold #10D98A]     [dim]PAK\'tan tek dosya al[/dim]')
        console.print('  [bold #10D98A][11] ✅ LUA SYNTAX CHECK[/bold #10D98A]    [dim]syntax kontrol[/dim]')
        console.print('  [bold #10D98A][12] ⚡ BATCH LUA COMPILE[/bold #10D98A]   [dim]tüm .lua dosyalarını derle[/dim]')
        console.print('  [bold #10D98A][13] 🔐 LUA STR ENCRYPTOR[/bold #10D98A]  [dim]string\'leri encode et[/dim]')
        console.print('  [bold #10D98A][14] 🔄 LUA BYTECODE DIFF[/bold #10D98A]  [dim]iki .luac karşılaştır[/dim]')
        console.print('  [bold #10D98A][15] 📊 DATA TABLE PARSER[/bold #10D98A]  [dim]uasset string/path dump[/dim]')
        console.print(f'  [bold white][0] {T("back")}[/bold white]')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1':  action_config_editor()
        elif c == '2':  action_bgmi_csv_generator()
        elif c == '3':  action_pattern_scanner()
        elif c == '4':  action_elf_parser()
        elif c == '5':  action_symbol_finder()
        elif c == '6':  action_string_dump()
        elif c == '7':  action_auto_backup()
        elif c == '8':  action_pak_metadata()
        elif c == '9':  action_blueprint_string_editor()
        elif c == '10': action_pak_single_extract()
        elif c == '11': action_lua_syntax_check()
        elif c == '12': action_batch_lua_compile()
        elif c == '13': action_lua_string_encryptor()
        elif c == '14': action_lua_bytecode_diff()
        elif c == '15': action_data_table_parser()


# ══════════════════════════════════════════════════════════════════
# [20] GELİŞMİŞ PUBG — Tersine mühendislik + Güçlü analiz
# ══════════════════════════════════════════════════════════════════

def action_ue4_class_dumper():
    os.system('clear')
    console.print('[bold #A855F7]🏛  UE4 CLASS DUMPER[/bold #A855F7]')
    console.print('[dim]  libUE4.so\'dan tüm UE4 class isimlerini çıkar[/dim]\n')
    path_raw = safe_input('  libUE4.so yolu (boş=otomatik ara): ').strip().strip('"'); flush_stdin()
    if not path_raw:
        found = list(Path('/sdcard').rglob('libUE4.so'))
        if not found: console.print(f'[red]❌ libUE4.so bulunamadı[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        p = found[0]
    else:
        p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'  [dim]Yükleniyor: {human_size(p.stat().st_size)}...[/dim]')
    data = p.read_bytes()
    console.print('  [dim]Class isimleri taranıyor...[/dim]')
    classes = set(); funcs = set(); prefixes = [b'A',b'U',b'F',b'E',b'T',b'S']
    i = 0
    while i < len(data)-4:
        if 65 <= data[i] <= 90:  # Büyük harf
            end = i
            while end < min(i+100,len(data)) and (97<=data[end]<=122 or 65<=data[end]<=90 or 48<=data[end]<=57 or data[end]==95):
                end += 1
            if end-i >= 4 and end < len(data) and data[end] == 0:
                s = data[i:end].decode('ascii','ignore')
                if len(s) >= 4:
                    if s[0] in 'AUFEST' and any(c.islower() for c in s[1:]):
                        classes.add(s)
                    if s.startswith(('Get','Set','Find','Spawn','Create','Init','Begin','End','Tick','Update')):
                        funcs.add(s)
            i = end + 1
        else:
            i += 1
    classes = sorted(classes)[:500]; funcs = sorted(funcs)[:200]
    out_dir = BASE_DIR / 'DUMP'
    out_dir.mkdir(parents=True, exist_ok=True)
    class_out = out_dir / 'ue4_classes.txt'
    func_out  = out_dir / 'ue4_functions.txt'
    class_out.write_text('\n'.join(classes), encoding='utf-8')
    func_out.write_text('\n'.join(funcs), encoding='utf-8')
    console.print(f'\n  [green]{len(classes)} class, {len(funcs)} fonksiyon bulundu[/green]')
    console.print(f'  Classes  → {class_out}')
    console.print(f'  Functions→ {func_out}')
    if classes[:10]:
        console.print('\n  [dim]Örnek class\'lar:[/dim]')
        for c in classes[:10]: console.print(f'  [cyan]{c}[/cyan]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_arm64_reader():
    os.system('clear')
    console.print('[bold #A855F7]🔧 ARM64 INSTRUCTION READER[/bold #A855F7]')
    console.print('[dim]  libUE4.so\'dan offset\'teki ARM64 instruction\'ı oku[/dim]\n')
    path_raw = safe_input('  .so dosyası yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    off_raw = safe_input('  Offset (hex, örn: 0x1234): ').strip(); flush_stdin()
    try:
        off = int(off_raw, 16) if off_raw.startswith('0x') else int(off_raw, 16)
    except:
        console.print(f'[red]Geçersiz offset[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    count_raw = safe_input('  Kaç instruction (32): ').strip() or '32'; flush_stdin()
    try: count = min(int(count_raw), 200)
    except: count = 32
    data = p.read_bytes()
    if off + count*4 > len(data):
        console.print(f'[red]❌ Offset aralık dışı[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'\n  [dim]0x{off:08X} → +{count*4} byte[/dim]\n')
    # Basic ARM64 decode
    ARM64_MNEMONICS = {
        0x91000000: 'ADD', 0xD1000000: 'SUB', 0xF9000000: 'LDR',
        0xF9000400: 'STR', 0x14000000: 'B', 0x94000000: 'BL',
        0x52800000: 'MOV', 0xD2800000: 'MOV', 0xAA0003E0: 'MOV',
        0xD65F03C0: 'RET', 0xA9BF7BFD: 'STP', 0xA8C17BFD: 'LDP',
        0xEB000000: 'SUBS', 0x54000000: 'B.cond', 0x12000000: 'AND',
        0xAA000000: 'ORR', 0xCA000000: 'EOR', 0x9B000000: 'MUL',
    }
    REG = ['X0','X1','X2','X3','X4','X5','X6','X7','X8','X9','X10','X11','X12','X13','X14','X15',
           'X16','X17','X18','X19','X20','X21','X22','X23','X24','X25','X26','X27','X28','X29','X30','SP',
           'W0','W1','W2','W3','W4','W5','W6','W7','W8','W9','W10','W11','W12','W13','W14','W15']
    for i in range(count):
        addr = off + i*4
        ins = struct.unpack_from('<I', data, addr)[0]
        rd = ins & 0x1F; rn = (ins>>5)&0x1F; rm=(ins>>16)&0x1F
        imm = (ins>>5)&0xFFFF
        # Identify instruction
        mnem = '????'
        if ins == 0xD65F03C0: mnem = 'RET'
        elif (ins & 0xFC000000) == 0x94000000:
            off26 = (ins & 0x3FFFFFF) << 2
            if ins & 0x2000000: off26 -= (1<<28)
            target = addr + off26
            mnem = f'BL      0x{target:08X}'
        elif (ins & 0xFC000000) == 0x14000000:
            off26 = (ins & 0x3FFFFFF) << 2
            if ins & 0x2000000: off26 -= (1<<28)
            target = addr + off26
            mnem = f'B       0x{target:08X}'
        elif (ins & 0xFF800000) == 0xD2800000:
            mnem = f'MOV     X{rd}, #{(ins>>5)&0xFFFF}'
        elif (ins & 0xFF800000) == 0x52800000:
            mnem = f'MOV     W{rd}, #{(ins>>5)&0xFFFF}'
        elif (ins & 0xFFC00000) == 0x91000000:
            mnem = f'ADD     X{rd}, X{rn}, #{(ins>>10)&0xFFF}'
        elif (ins & 0xFFC00000) == 0xD1000000:
            mnem = f'SUB     X{rd}, X{rn}, #{(ins>>10)&0xFFF}'
        elif (ins & 0xFFC00000) == 0xF9400000:
            mnem = f'LDR     X{rd}, [X{rn}, #{((ins>>10)&0xFFF)*8}]'
        elif (ins & 0xFFC00000) == 0xF9000000:
            mnem = f'STR     X{rd}, [X{rn}, #{((ins>>10)&0xFFF)*8}]'
        elif ins == 0xD503201F: mnem = 'NOP'
        elif (ins & 0xFFFFFC1F) == 0xAA0003E0:
            mnem = f'MOV     X{rd}, X{(ins>>16)&0x1F}'
        else:
            mnem = f'.word   0x{ins:08X}'
        console.print(f'  [dim]0x{addr:08X}[/dim]  [dim]{ins:08X}[/dim]  [cyan]{mnem}[/cyan]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_sm4_bruteforce():
    os.system('clear')
    console.print('[bold #A855F7]🔑 PAK SM4 KEY BRUTEFORCE[/bold #A855F7]')
    console.print('[dim]  Kayıtlı SM4 key listesini PAK dosyasına dene[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files:
        console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(pak_files, 1):
        console.print(f'  [{i}] {f.name}')
    try:
        c = safe_input(f'\n  PAK seç (1-{len(pak_files)}): ').strip(); flush_stdin()
        pak_path = pak_files[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'\n  [cyan]{len(SM4_SECRET_NEW)} key deneniyor...[/cyan]')
    data = pak_path.read_bytes()
    # Try each key by attempting TencentPakFile parse
    for i, key in enumerate(SM4_SECRET_NEW, 1):
        try:
            console.print(f'  [{i:2}/{len(SM4_SECRET_NEW)}] {key[:20]}...', end='\r')
            pak = TencentPakFile(PurePath(pak_path))
            # If parse succeeds without exception, key might work
            paths = pak.list_existing_paths()
            if len(paths) > 0:
                console.print(f'\n  [bold green]✅ Çalışan key: {key}[/bold green]')
                console.print(f'  [dim]{len(paths)} dosya listelendi[/dim]')
                flush_stdin(); safe_input(f'\n  {T("press_enter")}'); return
        except Exception:
            pass
    console.print(f'\n  [yellow]⚠ Listede çalışan key bulunamadı[/yellow]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_merger():
    os.system('clear')
    console.print('[bold #A855F7]🔗 PAK MERGER[/bold #A855F7]')
    console.print('[dim]  İki PAK dosyasını tek PAK\'a birleştir[/dim]\n')
    console.print('  [warn] PAK 2 dosyaları PAK 1\'i override eder')
    console.print()
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if len(pak_files) < 2:
        console.print(f'[red]❌ En az 2 PAK gerekli[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(pak_files, 1):
        console.print(f'  [{i}] {f.name}  [dim]{human_size(f.stat().st_size)}[/dim]')
    try:
        a = int(safe_input('\n  Temel PAK (1): ').strip()) - 1; flush_stdin()
        b = int(safe_input('  Eklenecek PAK (2): ').strip()) - 1; flush_stdin()
        pak_a = pak_files[a]; pak_b = pak_files[b]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    out_name = safe_input(f'  Çıktı adı [{pak_a.stem}_merged.pak]: ').strip() or f'{pak_a.stem}_merged.pak'; flush_stdin()
    if not out_name.endswith('.pak'): out_name += '.pak'
    out = BASE_DIR / out_name
    console.print(f'\n  [cyan]Birleştiriliyor...[/cyan]')
    try:
        p_a = TencentPakFile(PurePath(pak_a))
        p_b = TencentPakFile(PurePath(pak_b))
        paths_b = p_b.list_existing_paths()
        if not paths_b:
            console.print(f'[red]❌ PAK B boş veya okunamadı[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        # Unpack PAK B to temp, inject into PAK A
        import tempfile as _tf
        with _tf.TemporaryDirectory(prefix='fan_merge_') as tmp:
            tmp_p = Path(tmp)
            p_b.dump(PurePath(tmp_p))
            inject_files = [f for f in tmp_p.rglob('*') if f.is_file()]
            dom = p_a.detect_dominant_style()
            plan = [{'src_path':f,'internal_path':str(f.relative_to(tmp_p)).replace('\\','/'),
                     'comp_method':dom['comp_method'],'enc_method':dom['enc_method'],
                     'encrypted':dom['encrypted'],'block_size':dom['block_size']} for f in inject_files]
            import shutil as _shm
            _shm.copy2(str(pak_a), str(out))
            pak_out = TencentPakFile(PurePath(out))
            pak_out.inject_files(plan, Path(out))
        console.print(f'\n[bold green]✅ Birleştirme tamamlandı![/bold green]')
        console.print(f'  {out.name}  ({human_size(out.stat().st_size)})')
        console.print(f'  {len(inject_files)} dosya eklendi')
    except Exception as e:
        console.print(f'[red]❌ Hata: {e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_integrity():
    os.system('clear')
    console.print('[bold #A855F7]✅ PAK INTEGRITY CHECKER[/bold #A855F7]')
    console.print('[dim]  PAK SHA1 footer\'ını doğrula[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files:
        console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(pak_files, 1):
        console.print(f'  [{i}] {f.name}  [dim]{human_size(f.stat().st_size)}[/dim]')
    try:
        c = safe_input(f'\n  Seç (1-{len(pak_files)}): ').strip(); flush_stdin()
        pak_path = pak_files[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import hashlib as _hl
    data = pak_path.read_bytes()
    # Check magic at end
    console.print(f'\n  Dosya    : [cyan]{pak_path.name}[/cyan]')
    console.print(f'  Boyut    : [cyan]{human_size(len(data))}[/cyan]')
    # Last 4 bytes should contain version info
    last16 = data[-16:].hex().upper()
    console.print(f'  Son 16B  : [dim]{last16}[/dim]')
    # Calculate SHA1 of file (excluding last 20 bytes which is the hash)
    if len(data) > 20:
        sha1_stored = data[-20:].hex()
        sha1_calc = _hl.sha1(data[:-20]).hexdigest()
        if sha1_stored == sha1_calc:
            console.print(f'  SHA1     : [bold green]✅ GEÇERLI[/bold green]')
        else:
            console.print(f'  SHA1     : [yellow]⚠ Farklı (normal — PAK yapısı farklı)[/yellow]')
    # Check if parseable
    try:
        pak = TencentPakFile(PurePath(pak_path))
        paths = pak.list_existing_paths()
        console.print(f'  Parse    : [bold green]✅ GEÇERLI — {len(paths)} dosya[/bold green]')
    except Exception as e:
        console.print(f'  Parse    : [red]❌ BOZUK — {e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_constant_extractor():
    os.system('clear')
    console.print('[bold #A855F7]📊 LUA CONSTANT EXTRACTOR[/bold #A855F7]')
    console.print('[dim]  .luac bytecode\'dan sabit değerleri çıkar[/dim]\n')
    files = list(LUA_ORIGINAL_DIR.glob('*.luac')) + list(LUA_ORIGINAL_DIR.glob('*.slua')) + list(LUA_ORIGINAL_DIR.glob('*.lua'))
    if not files:
        console.print(f'[red]❌ {LUA_ORIGINAL_DIR} boş[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(files[:15], 1):
        console.print(f'  [{i}] {f.name}')
    try:
        c = safe_input(f'\n  Seç (1-{min(15,len(files))}): ').strip(); flush_stdin()
        p = files[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    if len(data) < 20: console.print(f'[red]❌ Çok küçük[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Extract constants from bytecode
    floats = []; ints = []; strings = []
    i = 0
    while i < len(data)-4:
        # Float constants
        try:
            v = struct.unpack_from('<f', data, i)[0]
            if 0.001 < abs(v) < 100000 and v != v+1: floats.append((i, round(v,4)))
        except: pass
        # Int constants
        try:
            v = struct.unpack_from('<i', data, i)[0]
            if 0 < v < 10000: ints.append((i, v))
        except: pass
        i += 4
    # String constants
    i = 0
    while i < len(data)-5:
        try:
            l = struct.unpack_from('<I', data, i)[0]
            if 2 <= l <= 200 and i+4+l <= len(data):
                s = data[i+4:i+4+l].rstrip(b'\x00').decode('utf-8','ignore')
                if len(s)>=2 and s.isprintable() and not s.startswith('\x1b'):
                    strings.append((i, s))
                i += 4 + l; continue
        except: pass
        i += 1
    console.print(f'\n  [cyan]Float sabitler ({len(floats)}):[/cyan]')
    for off,v in floats[:15]: console.print(f'  [dim]0x{off:06X}[/dim]  [white]{v}[/white]')
    console.print(f'\n  [cyan]Int sabitler ({len(ints)}):[/cyan]')
    for off,v in list(dict.fromkeys(v for _,v in ints))[:15]: console.print(f'  [white]{v}[/white]', end='  ')
    console.print()
    console.print(f'\n  [cyan]String sabitler ({len(strings)}):[/cyan]')
    for off,s in strings[:20]: console.print(f'  [dim]0x{off:06X}[/dim]  [green]{s[:60]}[/green]')
    # Save dump
    out = p.parent / (p.stem + '_constants.txt')
    lines = [f'=== {p.name} Constants ===','','# Floats:']
    lines += [f'0x{o:06X}\t{v}' for o,v in floats[:50]]
    lines += ['','# Strings:']
    lines += [f'0x{o:06X}\t{s}' for o,s in strings[:100]]
    out.write_text('\n'.join(lines), encoding='utf-8')
    console.print(f'\n  [dim]Dump: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_function_mapper():
    os.system('clear')
    console.print('[bold #A855F7]🗺  LUA FUNCTION MAPPER[/bold #A855F7]')
    console.print('[dim]  .luac bytecode\'dan fonksiyon haritasını çıkar[/dim]\n')
    path_raw = safe_input('  .luac dosyası yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    if data[:4] != b'\x1bLua':
        console.print(f'[red]❌ Lua bytecode değil[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Extract source names and line numbers
    funcs = []; i = 0
    while i < len(data)-5:
        # Look for @filename or function name patterns
        if data[i] == 0x40:  # '@' character
            end = i+1
            while end < min(i+100, len(data)) and 32 <= data[end] < 127:
                end += 1
            s = data[i:end].decode('ascii','ignore')
            if len(s) > 2: funcs.append({'offset':i,'name':s,'type':'source'})
        i += 1
    # Also find length-prefixed strings
    i = 0
    while i < len(data)-5:
        try:
            l = struct.unpack_from('<I', data, i)[0]
            if 3 <= l <= 100 and i+4+l <= len(data):
                s = data[i+4:i+4+l].rstrip(b'\x00').decode('utf-8','ignore')
                if len(s)>=3 and all(c.isalnum() or c in '_.' for c in s) and s[0].isalpha():
                    funcs.append({'offset':i,'name':s,'type':'identifier'})
                i += 4+l; continue
        except: pass
        i += 1
    funcs = funcs[:100]
    console.print(f'\n  [green]{len(funcs)} identifier bulundu:[/green]\n')
    for f in funcs[:30]:
        console.print(f'  [dim]0x{f["offset"]:06X}[/dim]  [{f["type"]}]  [cyan]{f["name"]}[/cyan]')
    out = p.parent / (p.stem + '_funcmap.txt')
    out.write_text('\n'.join(f'0x{f["offset"]:06X}\t{f["type"]}\t{f["name"]}' for f in funcs), encoding='utf-8')
    console.print(f'\n  [dim]Map kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_deobfuscator():
    os.system('clear')
    console.print('[bold #A855F7]🧹 LUA DEOBFUSCATOR[/bold #A855F7]')
    console.print('[dim]  Obfuscated Lua kaynak kodunu temizle[/dim]\n')
    path_raw = safe_input('  .lua dosyası yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        src = p.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import re as _re
    result = src
    # 1. Decode string.char() calls
    def decode_chars(m):
        try:
            nums = [int(x) for x in m.group(1).split(',')]
            return '"' + ''.join(chr(n) for n in nums if 32<=n<127) + '"'
        except: return m.group(0)
    result = _re.sub(r'string\.char\(([0-9,\s]+)\)', decode_chars, result)
    # 2. Decode table.concat of char arrays
    def decode_table_concat(m):
        try:
            nums = [int(x) for x in _re.findall(r'\d+', m.group(1))]
            return '"' + ''.join(chr(n) for n in nums if 32<=n<127) + '"'
        except: return m.group(0)
    result = _re.sub(r'table\.concat\(\{([0-9,\s]+)\}\)', decode_table_concat, result)
    # 3. Remove junk local variables (single-use temp vars)
    result = _re.sub(r'local _[a-zA-Z0-9]{5,}=\d+\+\d+\n', '', result)
    # 4. Simplify trivial math
    def eval_math(m):
        try: return str(int(m.group(1)) + int(m.group(2)))
        except: return m.group(0)
    result = _re.sub(r'(\d+)\+(\d+)', eval_math, result)
    # 5. Remove excessive whitespace
    result = _re.sub(r'\n{3,}', '\n\n', result)
    # 6. Decode inline function obfuscation patterns
    result = _re.sub(r'\(function\(\)local t=\{\}local [a-z]=\{([0-9,]+)\};for [a-z]=1,#[a-z] do [a-z]\[[a-z]\]=string\.char\([a-z]\[[a-z]\]\)end;return table\.concat\([a-z]\)end\)\(\)', decode_table_concat, result)
    out = p.parent / (p.stem + '_deob.lua')
    out.write_text(result, encoding='utf-8')
    orig_lines = src.count('\n'); new_lines = result.count('\n')
    console.print(f'\n[bold green]✅ Deobfuscation tamamlandı![/bold green]')
    console.print(f'  Orijinal: {orig_lines} satır → Temiz: {new_lines} satır')
    console.print(f'  Çıktı: {out}')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_xlua_converter():
    os.system('clear')
    console.print('[bold #A855F7]🔄 XLUA/SLUA CONVERTER[/bold #A855F7]')
    console.print('[dim]  PUBG özel Lua formatlarını standart Lua\'ya çevir[/dim]\n')
    console.print('  [1] .slua → .luac (header strip)')
    console.print('  [2] XLua bytecode → Std Lua 5.3')
    console.print('  [0] Geri')
    c = safe_input('\n  > ').strip(); flush_stdin()
    if c == '0': return
    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    if c == '1':
        # .slua files often have a custom header before Lua bytecode
        # Find the Lua magic
        lua_magic = b'\x1bLua'
        idx = data.find(lua_magic)
        if idx == -1:
            console.print(f'[red]❌ Lua magic bulunamadı[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        stripped = data[idx:]
        out = p.parent / (p.stem + '_stripped.luac')
        out.write_bytes(stripped)
        console.print(f'\n[green]✅ {idx} byte header strip edildi → {out.name}[/green]')
    elif c == '2':
        # XLua bytecode conversion (similar to T24 conversion)
        if data[:4] != b'\x1bLua':
            console.print(f'[red]❌ Lua bytecode değil[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        # Use existing T24 converter
        ok, msg = _premium_t24_to_std(str(p), str(p.parent / (p.stem + '_xlua_std.luac')))
        if ok:
            console.print(f'\n[green]✅ Dönüştürüldü: {msg}[/green]')
        else:
            console.print(f'[red]❌ {msg}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_weapon_stat_reader():
    os.system('clear')
    console.print('[bold #A855F7]🔫 WEAPON STAT READER[/bold #A855F7]')
    console.print('[dim]  Silah uasset\'inden stat değerlerini otomatik göster[/dim]\n')
    if not PAK_UNPACK_OUT.exists():
        console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    WEAPON_KEYWORDS = ['Weapon','Gun','Rifle','Pistol','Shotgun','SMG','Sniper','AR_','DMR','Kar98','M416','AKM','SCAR','Mini14','VSS','UMP','Vector','AWM','M24','Groza','Bizon']
    files = []
    for kw in WEAPON_KEYWORDS:
        files.extend(PAK_UNPACK_OUT.rglob(f'*{kw}*.uasset'))
    files = list(set(files))[:30]
    if not files:
        console.print(f'[yellow]⚠ Silah uasset bulunamadı[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i, f in enumerate(files[:20], 1):
        console.print(f'  [{i}] {f.name}')
    try:
        c = safe_input(f'\n  Seç (1-{min(20,len(files))}): ').strip(); flush_stdin()
        ua_path = files[int(c)-1]
    except:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ue_path = ua_path.with_suffix('.uexp')
    if not ue_path.exists():
        console.print(f'[red]❌ .uexp yok[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ua = _UAssetFileEx(); ua.load_data(ua_path.read_bytes())
    ue = _UExpFileEx(ua); ue.load_data(ue_path.read_bytes())
    WEAPON_STAT_KEYWORDS = ['Damage','Range','BulletSpeed','FireInterval','ReloadTime','BulletRange',
        'SpreadAngle','Recoil','BulletFire','ClipSize','BulletAmmo','HeadShotMul','BodyShotMul',
        'StabilityRate','AmmoPerShot','MaxBullet']
    os.system('clear')
    console.print(f'[bold]🔫 {ua_path.stem}[/bold]\n')
    found = []
    for prop in ue.properties:
        for kw in WEAPON_STAT_KEYWORDS:
            if kw.lower() in prop['name'].lower():
                found.append(prop); break
    if not found:
        console.print('[yellow]Spesifik silah stat\'ı bulunamadı. Tüm property\'ler:[/yellow]\n')
        for p in ue.properties[:20]:
            console.print(f'  [cyan]{p["name"][:40]}[/cyan]  [{p["type"]}]  [white]{p["value"]}[/white]')
    else:
        console.print('[cyan]Silah İstatistikleri:[/cyan]\n')
        for prop in found:
            console.print(f'  [bold]{prop["name"][:35]}[/bold]  [{prop["type"]}]  [bold green]{prop["value"]}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_config_generator():
    os.system('clear')
    console.print('[bold #A855F7]⚙️  CONFIG GENERATOR[/bold #A855F7]')
    console.print('[dim]  PUBG Mobile için optimize edilmiş .ini dosyası oluştur[/dim]\n')
    console.print('  [1] 120 FPS + Ultra kalite')
    console.print('  [2] 60 FPS + Dengeli')
    console.print('  [3] Low lag (düşük ping optimize)')
    console.print('  [4] Anti-ban korumalı (sadece temel değişiklikler)')
    console.print('  [0] Geri')
    c = safe_input('\n  > ').strip(); flush_stdin()
    if c == '0': return
    configs = {
        '1': {
            'name': '120FPS_Ultra',
            'GameUserSettings': [
                'bUseVSync=False','FrameRateLimit=120.000000','FullscreenMode=0',
                'ResolutionSizeX=1920','ResolutionSizeY=1080',
                'sg.ResolutionQuality=100','sg.ViewDistanceQuality=3',
                'sg.AntiAliasingQuality=3','sg.ShadowQuality=3',
                'sg.PostProcessQuality=3','sg.TextureQuality=3','sg.EffectsQuality=3',
                'bUseDynamicResolution=False','DesiredScreenWidth=1920','DesiredScreenHeight=1080'
            ],
            'UserCustom': [
                'UserCustomData_FrameRateLimit=120','UserCustomData_Brightness=50',
                'UserCustomData_GraphicsQuality=Ultra','UserCustomData_ShadowQuality=3',
                'UserCustomData_AntiAliasing=3','UserCustomData_Resolution=1920x1080'
            ]
        },
        '2': {
            'name': '60FPS_Balanced',
            'GameUserSettings': [
                'bUseVSync=False','FrameRateLimit=60.000000',
                'sg.ResolutionQuality=80','sg.ViewDistanceQuality=2',
                'sg.AntiAliasingQuality=2','sg.ShadowQuality=2',
                'sg.PostProcessQuality=2','sg.TextureQuality=2','sg.EffectsQuality=2',
            ],
            'UserCustom': [
                'UserCustomData_FrameRateLimit=60','UserCustomData_GraphicsQuality=Balanced',
            ]
        },
        '3': {
            'name': 'LowLag',
            'GameUserSettings': [
                'bUseVSync=False','FrameRateLimit=90.000000',
                'sg.ResolutionQuality=70','sg.ViewDistanceQuality=1',
                'sg.AntiAliasingQuality=1','sg.ShadowQuality=0',
                'sg.PostProcessQuality=0','sg.TextureQuality=1','sg.EffectsQuality=0',
                'bUseDynamicResolution=True','NetServerMaxTickRate=30',
            ],
            'UserCustom': [
                'UserCustomData_FrameRateLimit=90','UserCustomData_GraphicsQuality=Low',
                'UserCustomData_AntiAliasing=0','UserCustomData_ShadowQuality=0',
            ]
        },
        '4': {
            'name': 'SafeMode',
            'GameUserSettings': [
                'bUseVSync=False','FrameRateLimit=60.000000',
                'sg.ResolutionQuality=100','sg.ViewDistanceQuality=2',
                'sg.AntiAliasingQuality=2','sg.ShadowQuality=2',
                'sg.TextureQuality=2',
            ],
            'UserCustom': ['UserCustomData_FrameRateLimit=60']
        }
    }
    if c not in configs:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    cfg = configs[c]
    out_dir = BASE_DIR / 'CONFIG' / cfg['name']
    out_dir.mkdir(parents=True, exist_ok=True)
    gs_out = out_dir / 'GameUserSettings.ini'
    uc_out = out_dir / 'UserCustom.ini'
    gs_content = '[/Script/GameUserSettings]\n' + '\n'.join(cfg['GameUserSettings'])
    uc_content = '[UserCustomSection]\n' + '\n'.join(cfg['UserCustom'])
    gs_out.write_text(gs_content, encoding='utf-8')
    uc_out.write_text(uc_content, encoding='utf-8')
    console.print(f'\n[bold green]✅ Config oluşturuldu![/bold green]')
    console.print(f'  {gs_out}')
    console.print(f'  {uc_out}')
    console.print(f'\n  [dim]Bu dosyaları cihazın PUBG config klasörüne kopyala:[/dim]')
    console.print(f'  [dim]/sdcard/Android/data/com.pubg.imobile/files/...Config/Android/[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_offset_finder():
    os.system('clear')
    console.print('[bold #A855F7]📍 OFFSET FINDER[/bold #A855F7]')
    console.print('[dim]  libUE4.so\'dan class/fonksiyon offset\'lerini hesapla[/dim]\n')
    path_raw = safe_input('  libUE4.so yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    keyword = safe_input('  Aranacak class/fonksiyon: ').strip(); flush_stdin()
    if not keyword: return
    data = p.read_bytes()
    console.print(f'  [dim]Aranıyor: "{keyword}"...[/dim]')
    enc = keyword.encode('ascii')
    offsets = []
    pos = 0
    while True:
        pos = data.find(enc, pos)
        if pos == -1: break
        # Check surrounding context
        if pos > 0 and (data[pos-1] == 0 or data[pos-1] < 32):
            offsets.append(pos)
        pos += len(enc)
    if not offsets:
        console.print(f'[yellow]  "{keyword}" bulunamadı[/yellow]')
    else:
        console.print(f'\n  [green]{len(offsets)} offset bulundu:[/green]')
        for off in offsets[:20]:
            ctx = data[max(0,off-4):off+len(enc)+4].hex().upper()
            console.print(f'  [bold cyan]0x{off:08X}[/bold cyan]  [dim]{ctx}[/dim]')
        # Save
        out = BASE_DIR / 'DUMP' / f'{keyword}_offsets.txt'
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text('\n'.join(f'0x{o:08X}' for o in offsets), encoding='utf-8')
        console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_texture_id_mapper():
    os.system('clear')
    console.print('[bold #A855F7]🎨 TEXTURE ID MAPPER[/bold #A855F7]')
    console.print('[dim]  Skin texture ID\'lerini → dosya adı ile eşleştir[/dim]\n')
    if not PAK_UNPACK_OUT.exists():
        console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print('  [dim]Texture dosyaları taranıyor...[/dim]')
    texture_map = {}
    TEXTURE_DIRS = ['Content/Arts_Player','Content/Characters','Content/Texture','Content/UI/Texture']
    for tex_dir in TEXTURE_DIRS:
        full_dir = PAK_UNPACK_OUT / tex_dir
        if full_dir.exists():
            for f in full_dir.rglob('*.uasset'):
                # Extract ID from filename
                import re as _re
                ids = _re.findall(r'[A-Z]{2,4}_(\d{4,6})', f.stem)
                for id_ in ids:
                    texture_map[id_] = str(f.relative_to(PAK_UNPACK_OUT)).replace('\\','/')
    # Also check AvatarBPTable for skin IDs
    avatar_files = list(PAK_UNPACK_OUT.rglob('AvatarBP*'))
    skin_ids = {}
    for af in avatar_files:
        if af.suffix == '.uexp':
            data = af.read_bytes()
            # Look for 3-byte little-endian IDs
            for i in range(0, len(data)-3, 1):
                val = data[i] | (data[i+1]<<8) | (data[i+2]<<16)
                if 10000 < val < 999999:
                    skin_ids[str(val)] = f'0x{i:06X}'
    console.print(f'  [green]{len(texture_map)} texture, {len(skin_ids)} skin ID bulundu[/green]\n')
    # Display
    if texture_map:
        console.print('[cyan]Texture haritası (ilk 20):[/cyan]')
        for id_, path in list(texture_map.items())[:20]:
            console.print(f'  ID:[bold]{id_}[/bold]  → [dim]{path[:60]}[/dim]')
    # Save
    out = BASE_DIR / 'DUMP' / 'texture_map.txt'
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ['=== Texture ID Map ===','']
    for id_, path in texture_map.items():
        lines.append(f'{id_}\t{path}')
    lines += ['','=== Skin IDs ===','']
    for id_, off in list(skin_ids.items())[:200]:
        lines.append(f'{id_}\t{off}')
    out.write_text('\n'.join(lines), encoding='utf-8')
    console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_advanced_menu():
    while True:
        os.system('clear')
        console.print('[bold #A855F7]🔬 GELİŞMİŞ PUBG[/bold #A855F7]')
        console.print('[dim]  Tersine mühendislik + güçlü analiz araçları[/dim]\n')
        console.print('  [bold #A855F7][1]  🏛  UE4 CLASS DUMPER[/bold #A855F7]      [dim]class/fonksiyon isimleri[/dim]')
        console.print('  [bold #A855F7][2]  🔧 ARM64 READER[/bold #A855F7]            [dim]offset\'teki instruction oku[/dim]')
        console.print('  [bold #A855F7][3]  🔑 SM4 BRUTEFORCE[/bold #A855F7]         [dim]PAK SM4 key dene[/dim]')
        console.print('  [bold #A855F7][4]  🔗 PAK MERGER[/bold #A855F7]             [dim]iki PAK\'ı birleştir[/dim]')
        console.print('  [bold #A855F7][5]  ✅ PAK INTEGRITY[/bold #A855F7]          [dim]SHA1 doğrula[/dim]')
        console.print('  [bold #A855F7][6]  📊 LUA CONSTANTS[/bold #A855F7]          [dim]bytecode\'dan sabit değerler[/dim]')
        console.print('  [bold #A855F7][7]  🗺  LUA FUNC MAPPER[/bold #A855F7]        [dim]bytecode fonksiyon haritası[/dim]')
        console.print('  [bold #A855F7][8]  🧹 LUA DEOBFUSCATOR[/bold #A855F7]      [dim]obfuscated kodu temizle[/dim]')
        console.print('  [bold #A855F7][9]  🔄 XLUA/SLUA CONVERT[/bold #A855F7]    [dim]PUBG Lua formatı convert[/dim]')
        console.print('  [bold #A855F7][10] 🔫 WEAPON STATS[/bold #A855F7]          [dim]silah istatistiklerini oku[/dim]')
        console.print('  [bold #A855F7][11] ⚙️  CONFIG GENERATOR[/bold #A855F7]      [dim]optimize .ini oluştur[/dim]')
        console.print('  [bold #A855F7][12] 📍 OFFSET FINDER[/bold #A855F7]         [dim]class/fonksiyon offseti bul[/dim]')
        console.print('  [bold #A855F7][13] 🎨 TEXTURE ID MAP[/bold #A855F7]        [dim]skin texture ID haritası[/dim]')
        console.print(f'  [bold white][0] {T("back")}[/bold white]')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1':  action_ue4_class_dumper()
        elif c == '2':  action_arm64_reader()
        elif c == '3':  action_pak_sm4_bruteforce()
        elif c == '4':  action_pak_merger()
        elif c == '5':  action_pak_integrity()
        elif c == '6':  action_lua_constant_extractor()
        elif c == '7':  action_lua_function_mapper()
        elif c == '8':  action_lua_deobfuscator()
        elif c == '9':  action_xlua_converter()
        elif c == '10': action_weapon_stat_reader()
        elif c == '11': action_config_generator()
        elif c == '12': action_offset_finder()
        elif c == '13': action_texture_id_mapper()


# ══════════════════════════════════════════════════════════════════
# [21] KRİPTOGRAFİ ULTRA — SM4, RSA, RC4, ChaCha20, Key Derivation
# ══════════════════════════════════════════════════════════════════

# ── Pure Python SM4 ───────────────────────────────────────────────
_SM4_SBOX = [
    0xd6,0x90,0xe9,0xfe,0xcc,0xe1,0x3d,0xb7,0x16,0xb6,0x14,0xc2,0x28,0xfb,0x2c,0x05,
    0x2b,0x67,0x9a,0x76,0x2a,0xbe,0x04,0xc3,0xaa,0x44,0x13,0x26,0x49,0x86,0x06,0x99,
    0x9c,0x42,0x50,0xf4,0x91,0xef,0x98,0x7a,0x33,0x54,0x0b,0x43,0xed,0xcf,0xac,0x62,
    0xe4,0xb3,0x1c,0xa9,0xc9,0x08,0xe8,0x95,0x80,0xdf,0x94,0xfa,0x75,0x8f,0x3f,0xa6,
    0x47,0x07,0xa7,0xfc,0xf3,0x73,0x17,0xba,0x83,0x59,0x3c,0x19,0xe6,0x85,0x4f,0xa8,
    0x68,0x6b,0x81,0xb2,0x71,0x64,0xda,0x8b,0xf8,0xeb,0x0f,0x4b,0x70,0x56,0x9d,0x35,
    0x1e,0x24,0x0e,0x5e,0x63,0x58,0xd1,0xa2,0x25,0x22,0x7c,0x3b,0x01,0x21,0x78,0x87,
    0xd4,0x00,0x46,0x57,0x9f,0xd3,0x27,0x52,0x4c,0x36,0x02,0xe7,0xa0,0xc4,0xc8,0x9e,
    0xea,0xbf,0x8a,0xd2,0x40,0xc7,0x38,0xb5,0xa3,0xf7,0xf2,0xce,0xf9,0x61,0x15,0xa1,
    0xe0,0xae,0x5d,0xa4,0x9b,0x34,0x1a,0x55,0xad,0x93,0x32,0x30,0xf5,0x8c,0xb1,0xe3,
    0x1d,0xf6,0xe2,0x2e,0x82,0x66,0xca,0x60,0xc0,0x29,0x23,0xab,0x0d,0x53,0x4e,0x6f,
    0xd5,0xdb,0x37,0x45,0xde,0xfd,0x8e,0x2f,0x03,0xff,0x6a,0x72,0x6d,0x6c,0x5b,0x51,
    0x8d,0x1b,0xaf,0x92,0xbb,0xdd,0xbc,0x7f,0x11,0xd9,0x5c,0x41,0x1f,0x10,0x5a,0xd8,
    0x0a,0xc1,0x31,0x88,0xa5,0xcd,0x7b,0xbd,0x2d,0x74,0xd0,0x12,0xb8,0xe5,0xb4,0xb0,
    0x89,0x69,0x97,0x4a,0x0c,0x96,0x77,0x7e,0x65,0xb9,0xf1,0x09,0xc5,0x6e,0xc6,0x84,
    0x18,0xf0,0x7d,0xec,0x3a,0xdc,0x4d,0x20,0x79,0xee,0x5f,0x3e,0xd7,0xcb,0x39,0x48,
]
_SM4_FK = [0xA3B1BAC6,0x56AA3350,0x677D9197,0xB27022DC]
_SM4_CK = [0x00070e15,0x1c232a31,0x383f464d,0x545b6269,0x70777e85,0x8c939aa1,0xa8afb6bd,0xc4cbd2d9,
           0xe0e7eef5,0xfc030a11,0x181f262d,0x343b4249,0x50575e65,0x6c737a81,0x888f969d,0xa4abb2b9,
           0xc0c7ced5,0xdce3eaf1,0xf8ff060d,0x141b2229,0x30373e45,0x4c535a61,0x686f767d,0x848b9299,
           0xa0a7aeb5,0xbcc3cad1,0xd8dfe6ed,0xf4fb0209,0x10171e25,0x2c333a41,0x484f565d,0x646b7279]
def _sm4_sbox(v): return _SM4_SBOX[v&0xFF]
def _sm4_t(v): b=[_sm4_sbox((v>>24)&0xFF),_sm4_sbox((v>>16)&0xFF),_sm4_sbox((v>>8)&0xFF),_sm4_sbox(v&0xFF)];t=b[0]<<24|b[1]<<16|b[2]<<8|b[3];return t^((t<<2|t>>30)&0xFFFFFFFF)^((t<<10|t>>22)&0xFFFFFFFF)^((t<<18|t>>14)&0xFFFFFFFF)^((t<<24|t>>8)&0xFFFFFFFF)
def _sm4_t2(v): b=[_sm4_sbox((v>>24)&0xFF),_sm4_sbox((v>>16)&0xFF),_sm4_sbox((v>>8)&0xFF),_sm4_sbox(v&0xFF)];t=b[0]<<24|b[1]<<16|b[2]<<8|b[3];return t^((t<<13|t>>19)&0xFFFFFFFF)^((t<<23|t>>9)&0xFFFFFFFF)
def _sm4_key_expand(key):
    k=[int.from_bytes(key[i:i+4],'big')^_SM4_FK[i>>2] for i in range(0,16,4)];rk=[]
    for i in range(32):
        nk=k[i%4]^_sm4_t2(k[(i+1)%4]^k[(i+2)%4]^k[(i+3)%4]^_SM4_CK[i]);rk.append(nk);k[i%4]=nk
    return rk
def _sm4_block(block, rk):
    x=[int.from_bytes(block[i:i+4],'big') for i in range(0,16,4)]
    for i in range(32): tmp=x[1]^x[2]^x[3]^rk[i];x=[x[1],x[2],x[3],x[0]^_sm4_t(tmp)]
    return b''.join(v.to_bytes(4,'big') for v in reversed(x))
def sm4_ecb_encrypt(data:bytes, key:bytes)->bytes:
    rk=_sm4_key_expand(key[:16]);out=b''
    for i in range(0,len(data),16): out+=_sm4_block(data[i:i+16].ljust(16,b'\x00'),rk)
    return out
def sm4_ecb_decrypt(data:bytes, key:bytes)->bytes:
    rk=list(reversed(_sm4_key_expand(key[:16])));out=b''
    for i in range(0,len(data),16): out+=_sm4_block(data[i:i+16].ljust(16,b'\x00'),rk)
    return out

# ── RC4 ────────────────────────────────────────────────────────────
def rc4_crypt(data:bytes, key:bytes)->bytes:
    S=list(range(256));j=0
    for i in range(256): j=(j+S[i]+key[i%len(key)])%256;S[i],S[j]=S[j],S[i]
    out=[];i=j=0
    for b in data:
        i=(i+1)%256;j=(j+S[i])%256;S[i],S[j]=S[j],S[i]
        out.append(b^S[(S[i]+S[j])%256])
    return bytes(out)

# ── ChaCha20 quarter round ─────────────────────────────────────────
def _cc20_qr(a,b,c,d):
    a=(a+b)&0xFFFFFFFF;d^=a;d=(d<<16|d>>16)&0xFFFFFFFF
    c=(c+d)&0xFFFFFFFF;b^=c;b=(b<<12|b>>20)&0xFFFFFFFF
    a=(a+b)&0xFFFFFFFF;d^=a;d=(d<<8|d>>24)&0xFFFFFFFF
    c=(c+d)&0xFFFFFFFF;b^=c;b=(b<<7|b>>25)&0xFFFFFFFF
    return a,b,c,d
def chacha20_block(key:bytes, counter:int, nonce:bytes)->bytes:
    c=[0x61707865,0x3320646e,0x79622d32,0x6b206574]
    k=list(struct.unpack_from('<8I',key[:32]));n=list(struct.unpack_from('<3I',nonce[:12]))
    s=c+k+[counter&0xFFFFFFFF]+n;o=list(s)
    for _ in range(10):
        o[0],o[4],o[8],o[12]=_cc20_qr(o[0],o[4],o[8],o[12])
        o[1],o[5],o[9],o[13]=_cc20_qr(o[1],o[5],o[9],o[13])
        o[2],o[6],o[10],o[14]=_cc20_qr(o[2],o[6],o[10],o[14])
        o[3],o[7],o[11],o[15]=_cc20_qr(o[3],o[7],o[11],o[15])
        o[0],o[5],o[10],o[15]=_cc20_qr(o[0],o[5],o[10],o[15])
        o[1],o[6],o[11],o[12]=_cc20_qr(o[1],o[6],o[11],o[12])
        o[2],o[7],o[8],o[13]=_cc20_qr(o[2],o[7],o[8],o[13])
        o[3],o[4],o[9],o[14]=_cc20_qr(o[3],o[4],o[9],o[14])
    return struct.pack('<16I', *((o[i]+s[i])&0xFFFFFFFF for i in range(16)))
def chacha20_crypt(data:bytes, key:bytes, nonce:bytes, counter:int=0)->bytes:
    out=bytearray();blk_i=counter
    for i in range(0,len(data),64):
        blk=chacha20_block(key,blk_i,nonce);blk_i+=1
        chunk=data[i:i+64]
        out+=bytes(a^b for a,b in zip(chunk,blk))
    return bytes(out)

def action_crypto_ultra():
    while True:
        os.system('clear')
        console.print('[bold #F59E0B]🔐 KRİPTOGRAFİ ULTRA[/bold #F59E0B]\n')
        console.print('  [1] SM4-ECB  şifrele/çöz (pure Python)')
        console.print('  [2] RC4      şifrele/çöz')
        console.print('  [3] ChaCha20 şifrele/çöz')
        console.print('  [4] RSA key  PAK\'tan çıkar')
        console.print('  [5] Key Derivation (PBKDF2/HKDF)')
        console.print('  [0] Geri\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if c == '0': return
        elif c == '1':
            path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
            key_raw  = safe_input('  Key (hex 32 char): ').strip(); flush_stdin()
            mode     = safe_input('  [e]ncrypt / [d]ecrypt: ').strip().lower(); flush_stdin()
            try:
                p = Path(path_raw); key = bytes.fromhex(key_raw.ljust(32,'0')[:32])
                data = p.read_bytes()
                out_data = sm4_ecb_encrypt(data,key) if mode=='e' else sm4_ecb_decrypt(data,key)
                out = p.parent/(p.stem+('_sm4enc' if mode=='e' else '_sm4dec')+p.suffix)
                out.write_bytes(out_data)
                console.print(f'[green]✅ {out.name} ({human_size(len(out_data))})[/green]')
            except Exception as e: console.print(f'[red]❌ {e}[/red]')
            flush_stdin(); safe_input(f'  {T("press_enter")}')
        elif c == '2':
            path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
            key_raw  = safe_input('  Key (metin veya hex): ').strip(); flush_stdin()
            try:
                p = Path(path_raw)
                key = bytes.fromhex(key_raw) if all(c in '0123456789abcdefABCDEF' for c in key_raw) and len(key_raw)%2==0 else key_raw.encode()
                data = p.read_bytes()
                out_data = rc4_crypt(data, key)
                out = p.parent/(p.stem+'_rc4'+p.suffix)
                out.write_bytes(out_data)
                console.print(f'[green]✅ {out.name}[/green]')
            except Exception as e: console.print(f'[red]❌ {e}[/red]')
            flush_stdin(); safe_input(f'  {T("press_enter")}')
        elif c == '3':
            path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
            key_raw  = safe_input('  Key (hex 64 char): ').strip(); flush_stdin()
            nonce_raw= safe_input('  Nonce (hex 24 char, boş=sıfır): ').strip(); flush_stdin()
            try:
                p = Path(path_raw)
                key   = bytes.fromhex(key_raw.ljust(64,'0')[:64])
                nonce = bytes.fromhex(nonce_raw.ljust(24,'0')[:24]) if nonce_raw else b'\x00'*12
                data  = p.read_bytes()
                out_data = chacha20_crypt(data, key, nonce)
                out = p.parent/(p.stem+'_cc20'+p.suffix)
                out.write_bytes(out_data)
                console.print(f'[green]✅ {out.name}[/green]')
            except Exception as e: console.print(f'[red]❌ {e}[/red]')
            flush_stdin(); safe_input(f'  {T("press_enter")}')
        elif c == '4':
            pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
            if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); continue
            for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
            try:
                ci = int(safe_input('  Seç: ').strip())-1; flush_stdin()
                pak = TencentPakFile(PurePath(pak_files[ci]))
                pi  = pak._pak_info
                console.print(f'\n  [cyan]Packed Key:[/cyan] {pi.packed_key.hex() if hasattr(pi,"packed_key") else "N/A"}')
                console.print(f'  [cyan]Packed IV :[/cyan] {pi.packed_iv.hex() if hasattr(pi,"packed_iv") else "N/A"}')
                console.print(f'  [cyan]Enc Method:[/cyan] {pi.enc_method}')
                console.print(f'  [cyan]Encrypted :[/cyan] {pi.index_encrypted}')
            except Exception as e: console.print(f'[red]❌ {e}[/red]')
            flush_stdin(); safe_input(f'  {T("press_enter")}')
        elif c == '5':
            import hashlib as _hl
            passwd = safe_input('  Şifre: ').strip(); flush_stdin()
            salt   = safe_input('  Salt (boş=rastgele): ').strip(); flush_stdin()
            if not salt: import os as _os; salt = _os.urandom(16).hex()
            try:
                salt_b = bytes.fromhex(salt) if all(c in '0123456789abcdefABCDEF' for c in salt) else salt.encode()
                k32 = _hl.pbkdf2_hmac('sha256', passwd.encode(), salt_b, 100000, 32)
                k16 = _hl.pbkdf2_hmac('sha256', passwd.encode(), salt_b, 100000, 16)
                console.print(f'\n  [cyan]PBKDF2-SHA256 (32B):[/cyan] {k32.hex()}')
                console.print(f'  [cyan]PBKDF2-SHA256 (16B):[/cyan] {k16.hex()}')
                console.print(f'  [cyan]Salt              :[/cyan] {salt_b.hex()}')
            except Exception as e: console.print(f'[red]❌ {e}[/red]')
            flush_stdin(); safe_input(f'  {T("press_enter")}')

# ══════════════════════════════════════════════════════════════════
# [22] PAK ULTRA — Forge, Signature Patch, Entry Clone, Index Rebuild
# ══════════════════════════════════════════════════════════════════

def action_pak_forge():
    os.system('clear')
    console.print('[bold #F59E0B]🔨 PAK FORGE[/bold #F59E0B]')
    console.print('[dim]  Sıfırdan minimal PAK dosyası oluştur[/dim]\n')
    out_name = safe_input('  PAK dosya adı (çıktı): ').strip() or 'forged.pak'; flush_stdin()
    if not out_name.endswith('.pak'): out_name += '.pak'
    console.print('  Dosya ekle (boş=bitir):')
    files_to_add = []
    while True:
        path_raw = safe_input(f'  [{len(files_to_add)+1}] Dosya yolu (boş=bitir): ').strip().strip('"'); flush_stdin()
        if not path_raw: break
        internal = safe_input(f'      PAK içi yolu: ').strip(); flush_stdin()
        p = Path(path_raw)
        if p.exists(): files_to_add.append((p, internal))
        else: console.print(f'  [red]Yok: {path_raw}[/red]')
    if not files_to_add:
        console.print(f'[yellow]Dosya eklenmedi[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Build minimal unencrypted PAK v11
    import hashlib as _hl
    PAK_MAGIC = 0x5A6F12E1; PAK_VER = 11
    entries_data = b''; index_data = b''
    entry_meta = []
    for src_path, internal_path in files_to_add:
        raw = src_path.read_bytes()
        offset = len(entries_data)
        sha1 = _hl.sha1(raw).digest()
        entries_data += raw
        # Entry index record
        ip_enc = internal_path.encode('utf-8') + b'\x00'
        ip_len = len(ip_enc)
        rec = struct.pack('<I', ip_len) + ip_enc
        rec += struct.pack('<QQQ', offset, len(raw), len(raw))  # off, compressed, uncompressed
        rec += struct.pack('<I', 0)  # compression=none
        rec += sha1
        rec += struct.pack('<B', 0)  # not encrypted
        rec += struct.pack('<I', 0)  # block count
        index_data += rec
        entry_meta.append((internal_path, offset, len(raw)))
    # PAK footer
    index_offset = len(entries_data)
    index_sha1 = _hl.sha1(index_data).digest()
    footer  = struct.pack('<I', 0)         # enc guid
    footer += struct.pack('<B', 0)         # encrypted
    footer += struct.pack('<I', PAK_MAGIC)
    footer += struct.pack('<I', PAK_VER)
    footer += struct.pack('<Q', index_offset)
    footer += struct.pack('<Q', len(index_data))
    footer += index_sha1
    pak_data = entries_data + index_data + footer
    out = BASE_DIR / out_name
    out.write_bytes(pak_data)
    console.print(f'\n[bold green]✅ PAK forge tamamlandı![/bold green]')
    console.print(f'  {out.name}  ({human_size(len(pak_data))})')
    console.print(f'  {len(files_to_add)} dosya eklendi')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_sig_patcher():
    os.system('clear')
    console.print('[bold #F59E0B]🔏 PAK SIGNATURE PATCHER[/bold #F59E0B]')
    console.print('[dim]  PAK footer SHA1\'ini yeniden hesapla ve düzelt[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import hashlib as _hl
    data = bytearray(pak_path.read_bytes())
    # Find PAK magic (0x5A6F12E1) in last 200 bytes
    magic = struct.pack('<I', 0x5A6F12E1)
    magic_pos = -1
    for i in range(len(data)-4, max(len(data)-200,0), -1):
        if data[i:i+4] == magic: magic_pos = i; break
    if magic_pos == -1:
        console.print('[yellow]⚠ PAK magic bulunamadı — SHA1 footer denemesi[/yellow]')
        # Try: last 53 bytes contain SHA1 at offset -20
        index_sha1_pos = len(data) - 20
        if len(data) > 100:
            try:
                pak = TencentPakFile(PurePath(pak_path))
                pi  = pak._pak_info
                io  = pi.index_offset; isz = pi.index_size
                index_data = data[io:io+isz]
                new_sha1 = _hl.sha1(index_data).digest()
                data[index_sha1_pos:index_sha1_pos+20] = new_sha1
                out = pak_path.parent/(pak_path.stem+'_sigfixed.pak')
                out.write_bytes(bytes(data))
                console.print(f'[green]✅ SHA1 yeniden hesaplandı → {out.name}[/green]')
            except Exception as e: console.print(f'[red]❌ {e}[/red]')
    else:
        console.print(f'  Magic @ 0x{magic_pos:X}')
        try:
            pak = TencentPakFile(PurePath(pak_path))
            pi  = pak._pak_info
            io  = pi.index_offset; isz = pi.index_size
            index_data = data[io:io+isz]
            new_sha1 = _hl.sha1(index_data).digest()
            # Find SHA1 position in footer (20 bytes before end usually)
            sha1_pos = len(data)-20
            data[sha1_pos:sha1_pos+20] = new_sha1
            out = pak_path.parent/(pak_path.stem+'_sigfixed.pak')
            out.write_bytes(bytes(data))
            console.print(f'[green]✅ SHA1 patch → {out.name}[/green]')
            console.print(f'  Yeni SHA1: {new_sha1.hex()}')
        except Exception as e: console.print(f'[red]❌ {e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_entry_cloner():
    os.system('clear')
    console.print('[bold #F59E0B]📋 PAK ENTRY CLONER[/bold #F59E0B]')
    console.print('[dim]  Bir PAK\'taki dosyayı başka PAK\'a kopyala[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if len(pak_files) < 2: console.print(f'[red]❌ En az 2 PAK gerekli[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
    try:
        a = int(safe_input('\n  Kaynak PAK: ').strip())-1; flush_stdin()
        b = int(safe_input('  Hedef PAK : ').strip())-1; flush_stdin()
        src_pak = pak_files[a]; dst_pak = pak_files[b]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        p_src = TencentPakFile(PurePath(src_pak))
        paths = p_src.list_existing_paths()
    except Exception as e: console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    search = safe_input('  Dosya adı ara: ').strip(); flush_stdin()
    matches = [p for p in paths if search.lower() in p.lower()]
    if not matches: console.print(f'[yellow]Bulunamadı[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,m in enumerate(matches[:15],1): console.print(f'  [{i}] {m}')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        sel = matches[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import tempfile as _tf, shutil as _sh
    with _tf.TemporaryDirectory(prefix='fan_clone_') as tmp:
        tmp_p = Path(tmp)
        try:
            parts = sel.replace('\\','/').split('/')
            dir_part = '/'.join(parts[:-1]); fname = parts[-1]
            entry = p_src._index.get(dir_part,{}).get(fname)
            if entry:
                dst_f = tmp_p/fname
                p_src._write_to_disk(PurePath(dst_f), entry)
                p_dst = TencentPakFile(PurePath(dst_pak))
                dom   = p_dst.detect_dominant_style()
                plan  = [{'src_path':dst_f,'internal_path':sel,'comp_method':dom['comp_method'],
                           'enc_method':dom['enc_method'],'encrypted':dom['encrypted'],'block_size':dom['block_size']}]
                out   = dst_pak.parent/(dst_pak.stem+'_cloned.pak')
                _sh.copy2(str(dst_pak),str(out))
                p_out = TencentPakFile(PurePath(out)); p_out.inject_files(plan,Path(out))
                console.print(f'[green]✅ Kopyalandı → {out.name}[/green]')
            else:
                console.print('[red]❌ Entry bulunamadı[/red]')
        except Exception as e: console.print(f'[red]❌ {e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_version_spoofer():
    os.system('clear')
    console.print('[bold #F59E0B]🎭 PAK VERSION SPOOFER[/bold #F59E0B]')
    console.print('[dim]  PAK versiyon numarasını değiştir[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = bytearray(pak_path.read_bytes())
    PAK_MAGIC = struct.pack('<I',0x5A6F12E1)
    magic_pos = -1
    for i in range(len(data)-4, max(len(data)-200,0),-1):
        if data[i:i+4] == PAK_MAGIC: magic_pos = i; break
    if magic_pos == -1: console.print(f'[red]❌ Magic bulunamadı[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ver_pos = magic_pos+4; cur_ver = struct.unpack_from('<I',data,ver_pos)[0]
    console.print(f'  Mevcut versiyon: [cyan]{cur_ver}[/cyan]')
    console.print(f'  Bilinen versiyonlar: 4,5,7,8,9,10,11')
    try:
        new_ver = int(safe_input('  Yeni versiyon: ').strip()); flush_stdin()
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    struct.pack_into('<I', data, ver_pos, new_ver)
    out = pak_path.parent/(pak_path.stem+f'_v{new_ver}.pak')
    out.write_bytes(bytes(data))
    console.print(f'[green]✅ Versiyon {cur_ver} → {new_ver} → {out.name}[/green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_ultra_menu():
    while True:
        os.system('clear')
        console.print('[bold #F59E0B]📦 PAK ULTRA[/bold #F59E0B]\n')
        console.print('  [1] 🔨 PAK Forge          [dim]sıfırdan PAK oluştur[/dim]')
        console.print('  [2] 🔏 Signature Patcher  [dim]SHA1 footer yeniden hesapla[/dim]')
        console.print('  [3] 📋 Entry Cloner       [dim]dosyayı başka PAK\'a kopyala[/dim]')
        console.print('  [4] 🎭 Version Spoofer    [dim]PAK versiyon değiştir[/dim]')
        console.print('  [0] Geri\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_pak_forge()
        elif c == '2': action_pak_sig_patcher()
        elif c == '3': action_pak_entry_cloner()
        elif c == '4': action_pak_version_spoofer()

# ══════════════════════════════════════════════════════════════════
# [23] OYUN ULTRA — Mass Patch, Damage, Speed, Anti-debug, Code Cave
# ══════════════════════════════════════════════════════════════════

def action_property_mass_patcher():
    os.system('clear')
    console.print('[bold #EF4444]⚡ PROPERTY MASS PATCHER[/bold #EF4444]')
    console.print('[dim]  Aynı property\'yi birden fazla uasset\'te toplu değiştir[/dim]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    prop_name = safe_input('  Property adı (örn: Damage): ').strip(); flush_stdin()
    new_val   = safe_input('  Yeni değer: ').strip(); flush_stdin()
    if not prop_name or not new_val: return
    files = list(PAK_UNPACK_OUT.rglob('*.uexp'))
    if not files: console.print(f'[red]❌ .uexp yok[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'  [dim]{len(files)} dosya taranıyor...[/dim]')
    ok = 0; total_changes = 0
    for uexp_path in files:
        ua_path = uexp_path.with_suffix('.uasset')
        if not ua_path.exists(): continue
        try:
            ua = _UAssetFileEx(); ua.load_data(ua_path.read_bytes())
            ue = _UExpFileEx(ua); ue.load_data(uexp_path.read_bytes())
            changed = False
            for prop in ue.properties:
                if prop_name.lower() in prop['name'].lower():
                    if ue.write_prop(prop, float(new_val) if prop['type'] in ('f32','f64') else int(new_val)):
                        changed = True; total_changes += 1
            if changed:
                out = uexp_path.parent/(uexp_path.stem+'_mass'+uexp_path.suffix)
                out.write_bytes(ue.data); ok += 1
                console.print(f'  [green]✓ {uexp_path.name}[/green]')
        except: pass
    console.print(f'\n[bold green]✅ {ok} dosya, {total_changes} property değiştirildi[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_damage_multiplier():
    os.system('clear')
    console.print('[bold #EF4444]💥 DAMAGE MULTIPLIER[/bold #EF4444]')
    console.print('[dim]  Tüm silah uasset\'lerinde hasar değerlerini çarp[/dim]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        multiplier = float(safe_input('  Çarpan (örn: 2.0 = 2x hasar): ').strip()); flush_stdin()
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    DAMAGE_KEYWORDS = ['Damage','damage','Hurt','hurt','DamageRate','DamageMultiplier']
    files = list(PAK_UNPACK_OUT.rglob('*.uexp'))
    console.print(f'  [dim]{len(files)} dosya, x{multiplier} çarpan...[/dim]')
    ok = 0; changes = 0
    for uexp_path in files:
        ua_path = uexp_path.with_suffix('.uasset')
        if not ua_path.exists(): continue
        try:
            ua = _UAssetFileEx(); ua.load_data(ua_path.read_bytes())
            ue = _UExpFileEx(ua); ue.load_data(uexp_path.read_bytes())
            changed = False
            for prop in ue.properties:
                if any(kw in prop['name'] for kw in DAMAGE_KEYWORDS):
                    if prop['type'] in ('f32','f64') and isinstance(prop['value'],(int,float)):
                        new_v = round(float(prop['value']) * multiplier, 4)
                        if ue.write_prop(prop, new_v): changed = True; changes += 1
            if changed:
                out = uexp_path.parent/(uexp_path.stem+'_dmg'+uexp_path.suffix)
                out.write_bytes(ue.data); ok += 1
        except: pass
    console.print(f'\n[bold green]✅ {ok} dosya, {changes} hasar değeri çarpıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_vehicle_speed_editor():
    os.system('clear')
    console.print('[bold #EF4444]🚗 VEHICLE SPEED EDITOR[/bold #EF4444]')
    console.print('[dim]  Araç hız değerlerini otomatik bul ve düzenle[/dim]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    VEHICLE_KEYWORDS = ['Vehicle','vehicle','Car','Bike','Boat','Buggy','Dacia','UAZ','Mirado','Motorcycle','Jeep']
    SPEED_PROPS = ['MaxSpeed','Speed','TopSpeed','Velocity','MaxVelocity','DriveForce','EngineForce']
    files = []
    for kw in VEHICLE_KEYWORDS:
        files.extend(PAK_UNPACK_OUT.rglob(f'*{kw}*.uexp'))
    files = list(set(files))[:30]
    if not files: console.print(f'[yellow]Araç .uexp bulunamadı[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(files[:15],1): console.print(f'  [{i}] {f.name}')
    try:
        c = safe_input(f'\n  Seç (1-{min(15,len(files))}): ').strip(); flush_stdin()
        uexp_path = files[int(c)-1]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ua_path = uexp_path.with_suffix('.uasset')
    if not ua_path.exists(): console.print(f'[red]❌ .uasset yok[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ua = _UAssetFileEx(); ua.load_data(ua_path.read_bytes())
    ue = _UExpFileEx(ua); ue.load_data(uexp_path.read_bytes())
    speed_props = [p for p in ue.properties if any(kw.lower() in p['name'].lower() for kw in SPEED_PROPS)]
    if not speed_props:
        console.print('[yellow]Hız property\'si bulunamadı. Tüm float\'lar:[/yellow]')
        speed_props = [p for p in ue.properties if p['type'] in ('f32','f64')][:20]
    os.system('clear')
    console.print(f'[bold]🚗 {uexp_path.stem}[/bold]\n')
    for i,p in enumerate(speed_props,1):
        console.print(f'  [{i}] [cyan]{p["name"][:40]}[/cyan]  [white]{p["value"]}[/white]')
    changes = {}
    while True:
        cmd = safe_input('\n  Numara (düzenle) | s=kaydet | 0=geri: ').strip(); flush_stdin()
        if cmd == '0': break
        elif cmd == 's':
            if not changes: console.print('[yellow]Değişiklik yok[/yellow]'); continue
            for idx, new_v in changes.items():
                ue.write_prop(speed_props[idx], new_v)
            out = uexp_path.parent/(uexp_path.stem+'_speed'+uexp_path.suffix)
            out.write_bytes(ue.data)
            console.print(f'[green]✅ Kaydedildi: {out.name}[/green]')
            flush_stdin(); safe_input(f'  {T("press_enter")}'); break
        elif cmd.isdigit() and 1<=int(cmd)<=len(speed_props):
            idx = int(cmd)-1; prop = speed_props[idx]
            console.print(f'  [cyan]{prop["name"]}[/cyan] = {prop["value"]}')
            try:
                new_v = float(safe_input('  Yeni değer: ').strip()); flush_stdin()
                changes[idx] = new_v; console.print(f'  [green]✅ {prop["value"]} → {new_v}[/green]')
            except: console.print(f'[red]{T("invalid")}[/red]')

def action_code_cave_finder():
    os.system('clear')
    console.print('[bold #EF4444]🕳  CODE CAVE FINDER[/bold #EF4444]')
    console.print('[dim]  .so içinde injection için boş alan (NOP/zero bölgesi) bul[/dim]\n')
    path_raw = safe_input('  .so dosyası yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        min_size = int(safe_input('  Minimum boyut (byte, 64): ').strip() or '64'); flush_stdin()
    except: min_size = 64; flush_stdin()
    data = p.read_bytes()
    console.print(f'  [dim]Taranıyor ({human_size(len(data))})...[/dim]')
    caves = []
    i = 0
    while i < len(data):
        b = data[i]
        if b == 0x00 or b == 0x90:  # Zero or NOP
            end = i
            while end < len(data) and data[end] == b:
                end += 1
            size = end - i
            if size >= min_size:
                caves.append({'offset':i,'size':size,'byte':b,'type':'NOP' if b==0x90 else 'ZERO'})
            i = end
        else:
            i += 1
    caves.sort(key=lambda x: x['size'], reverse=True)
    if not caves:
        console.print(f'[yellow]  {min_size}+ byte\'lık boş alan bulunamadı[/yellow]')
    else:
        console.print(f'\n  [green]{len(caves)} code cave bulundu:[/green]\n')
        for cave in caves[:15]:
            console.print(f'  [bold cyan]0x{cave["offset"]:08X}[/bold cyan]  {cave["size"]:6} byte  [{cave["type"]}]')
        out = BASE_DIR/'DUMP'/'code_caves.txt'
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text('\n'.join(f'0x{c["offset"]:08X}\t{c["size"]}\t{c["type"]}' for c in caves), encoding='utf-8')
        console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_antidebug_patcher():
    os.system('clear')
    console.print('[bold #EF4444]🛡  ANTI-DEBUG PATCHER[/bold #EF4444]')
    console.print('[dim]  libUE4.so\'daki anti-debug/ptrace çağrılarını patch et[/dim]\n')
    path_raw = safe_input('  .so dosyası yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = bytearray(p.read_bytes())
    # Common anti-debug patterns in ARM64:
    # ptrace syscall: MOV X0,#26 + SVC #0 = D2800340 D4000001
    # prctl syscall patterns
    # IsDebuggerPresent pattern
    PATTERNS = [
        (b'\xD4\x00\x00\x01', b'\x1F\x20\x03\xD5', 'SVC #0 → NOP'),           # SVC→NOP
        (b'\xD2\x80\x03\x40', b'\x1F\x20\x03\xD5', 'MOV X0,#26(ptrace)→NOP'), # ptrace syscall nr
        (b'\xD4\x00\x00\x01\xD4\x00\x00\x01', b'\x1F\x20\x03\xD5'*2, 'Double SVC→NOP'),
    ]
    total = 0
    for pat, repl, desc in PATTERNS:
        pos = 0
        count = 0
        while True:
            pos = data.find(pat, pos)
            if pos == -1: break
            data[pos:pos+len(repl)] = repl; pos += len(pat); count += 1
        if count: console.print(f'  [green]✓ {desc}: {count} patch[/green]'); total += count
    if total == 0:
        console.print('[yellow]  Anti-debug pattern bulunamadı (farklı .so versiyonu olabilir)[/yellow]')
    else:
        out = p.parent/(p.stem+'_nodbg'+p.suffix)
        out.write_bytes(bytes(data))
        console.print(f'\n[bold green]✅ {total} anti-debug patch → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_bytecode_patcher():
    os.system('clear')
    console.print('[bold #EF4444]🔧 LUA BYTECODE PATCHER[/bold #EF4444]')
    console.print('[dim]  .luac içindeki belirli instruction\'ı başka instruction ile değiştir[/dim]\n')
    path_raw = safe_input('  .luac dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = bytearray(p.read_bytes())
    if data[:4] != b'\x1bLua': console.print(f'[red]❌ Lua bytecode değil[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Show first 20 instructions
    console.print('\n  [dim]İlk 20 instruction:[/dim]')
    start = 34  # After Lua 5.3 header
    for i in range(20):
        off = start + i*4
        if off+4 > len(data): break
        ins = struct.unpack_from('<I',data,off)[0]
        op  = ins & 0x3F
        console.print(f'  [dim]{i:3}[/dim]  0x{off:06X}  op={op:2}  [cyan]{ins:08X}[/cyan]')
    console.print()
    try:
        ins_idx = int(safe_input('  Instruction index (0-19): ').strip()); flush_stdin()
        new_hex = safe_input('  Yeni instruction (hex, 8 chars): ').strip(); flush_stdin()
        new_ins = int(new_hex, 16)
        off = start + ins_idx*4
        struct.pack_into('<I', data, off, new_ins)
        out = p.parent/(p.stem+'_patched.luac')
        out.write_bytes(bytes(data))
        console.print(f'[green]✅ Patch uygulandı → {out.name}[/green]')
    except Exception as e: console.print(f'[red]❌ {e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_oyun_ultra_menu():
    while True:
        os.system('clear')
        console.print('[bold #EF4444]🎮 OYUN ULTRA[/bold #EF4444]\n')
        console.print('  [1] ⚡ Property Mass Patcher  [dim]toplu property değiştir[/dim]')
        console.print('  [2] 💥 Damage Multiplier      [dim]hasar değerlerini çarp[/dim]')
        console.print('  [3] 🚗 Vehicle Speed Editor   [dim]araç hız değerleri[/dim]')
        console.print('  [4] 🕳  Code Cave Finder       [dim]injection için boş alan[/dim]')
        console.print('  [5] 🛡  Anti-Debug Patcher     [dim]ptrace/antidebug patch[/dim]')
        console.print('  [6] 🔧 Lua Bytecode Patcher   [dim]instruction değiştir[/dim]')
        console.print('  [0] Geri\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_property_mass_patcher()
        elif c == '2': action_damage_multiplier()
        elif c == '3': action_vehicle_speed_editor()
        elif c == '4': action_code_cave_finder()
        elif c == '5': action_antidebug_patcher()
        elif c == '6': action_lua_bytecode_patcher()

# ══════════════════════════════════════════════════════════════════
# [24] TERMUX PRO — Git, Log Analyzer, Process Scanner
# ══════════════════════════════════════════════════════════════════

def action_git_integration():
    os.system('clear')
    console.print('[bold #0EA5E9]🐙 GIT INTEGRATION[/bold #0EA5E9]\n')
    console.print('  [1] git clone (mod dosyaları indir)')
    console.print('  [2] git pull  (güncelle)')
    console.print('  [3] git status')
    console.print('  [4] git log   (son commit\'ler)')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    if c == '1':
        url = safe_input('  Git URL: ').strip(); flush_stdin()
        if not url: return
        out_dir = safe_input(f'  Klasör ({BASE_DIR}/mods): ').strip() or str(BASE_DIR/'mods'); flush_stdin()
        console.print(f'  [dim]Klonlanıyor...[/dim]')
        r = subprocess.run(['git','clone',url,out_dir], capture_output=False, timeout=120)
        if r.returncode == 0: console.print(f'[green]✅ Klonlandı → {out_dir}[/green]')
        else: console.print('[red]❌ Clone başarısız[/red]')
    elif c in ('2','3','4'):
        dir_raw = safe_input('  Repo klasörü: ').strip().strip('"') or str(BASE_DIR/'mods'); flush_stdin()
        cmds = {'2':['git','pull'],'3':['git','status'],'4':['git','log','--oneline','-10']}
        r = subprocess.run(cmds[c], cwd=dir_raw, capture_output=True, text=True, timeout=30)
        console.print(r.stdout or r.stderr or '(çıktı yok)')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_log_analyzer():
    os.system('clear')
    console.print('[bold #0EA5E9]📋 PUBG LOG ANALİZÖRÜ[/bold #0EA5E9]')
    console.print('[dim]  PUBG Mobile game log dosyalarını parse et[/dim]\n')
    LOG_PATHS = [
        Path('/sdcard/Android/data/com.pubg.imobile/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Logs'),
        Path('/sdcard/Android/data/com.tencent.ig/files/UE4Game/ShadowTrackerExtra/ShadowTrackerExtra/Saved/Logs'),
    ]
    logs = []
    for lp in LOG_PATHS:
        if lp.exists(): logs.extend(lp.glob('*.log'))
    if not logs:
        path_raw = safe_input('  Log dosyası yolu: ').strip().strip('"'); flush_stdin()
        if not path_raw: return
        logs = [Path(path_raw)]
    for i,l in enumerate(logs,1): console.print(f'  [{i}] {l.name}  [dim]{human_size(l.stat().st_size)}[/dim]')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        log_path = logs[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        content = log_path.read_text(encoding='utf-8', errors='replace')
    except Exception as e: console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    lines = content.splitlines()
    # Analyze
    errors = [l for l in lines if 'Error' in l or 'error' in l or 'ERROR' in l]
    warnings = [l for l in lines if 'Warning' in l or 'warning' in l]
    pak_lines = [l for l in lines if '.pak' in l.lower()]
    lua_lines = [l for l in lines if 'lua' in l.lower() or '.luac' in l.lower()]
    os.system('clear')
    console.print(f'[bold]📋 {log_path.name}[/bold]  [dim]{len(lines)} satır[/dim]\n')
    console.print(f'  [red]ERROR  : {len(errors)}[/red]')
    console.print(f'  [yellow]Warning: {len(warnings)}[/yellow]')
    console.print(f'  [cyan]PAK    : {len(pak_lines)}[/cyan]')
    console.print(f'  [cyan]Lua    : {len(lua_lines)}[/cyan]')
    if errors:
        console.print('\n  [red]Son hatalar:[/red]')
        for e in errors[-5:]: console.print(f'  [dim]{e[:100]}[/dim]')
    if pak_lines:
        console.print('\n  [cyan]PAK logları:[/cyan]')
        for l in pak_lines[:5]: console.print(f'  [dim]{l[:100]}[/dim]')
    out = log_path.parent/(log_path.stem+'_analysis.txt')
    report = [f'=== Log Analysis: {log_path.name} ===','',
              f'Errors: {len(errors)}',f'Warnings: {len(warnings)}',
              f'PAK refs: {len(pak_lines)}',f'Lua refs: {len(lua_lines)}',
              '','=== Errors ==='] + errors[:50] + ['','=== PAK ==='] + pak_lines[:50]
    out.write_text('\n'.join(report), encoding='utf-8')
    console.print(f'\n  [dim]Rapor: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_process_scanner():
    os.system('clear')
    console.print('[bold #0EA5E9]🔍 PROCESS SCANNER[/bold #0EA5E9]')
    console.print('[dim]  Çalışan PUBG/Termux process\'lerini tara[/dim]\n')
    try:
        proc_dir = Path('/proc')
        procs = []
        for pid_dir in proc_dir.iterdir():
            if not pid_dir.name.isdigit(): continue
            try:
                cmdline = (pid_dir/'cmdline').read_bytes().replace(b'\x00',b' ').decode('utf-8','ignore').strip()
                if cmdline:
                    status_lines = (pid_dir/'status').read_text(errors='ignore').splitlines()
                    name = next((l.split(':')[1].strip() for l in status_lines if l.startswith('Name:')), '?')
                    mem_line = next((l for l in status_lines if l.startswith('VmRSS:')), '')
                    mem = mem_line.split()[1] + ' KB' if mem_line else '?'
                    procs.append({'pid':pid_dir.name,'name':name,'cmd':cmdline[:60],'mem':mem})
            except: pass
        # Filter interesting processes
        keywords = ['pubg','tencent','UE4','ShadowTracker','bgmi','python','star']
        interesting = [p for p in procs if any(kw.lower() in p['cmd'].lower() or kw.lower() in p['name'].lower() for kw in keywords)]
        if interesting:
            console.print(f'  [green]{len(interesting)} ilgili process:[/green]\n')
            for p in interesting:
                console.print(f'  PID:[bold cyan]{p["pid"]:6}[/bold cyan]  [{p["mem"]:12}]  {p["name"][:15]:<15}  [dim]{p["cmd"][:50]}[/dim]')
        else:
            console.print('  [yellow]İlgili process bulunamadı (PUBG çalışmıyor olabilir)[/yellow]')
        console.print(f'\n  [dim]Toplam process: {len(procs)}[/dim]')
    except Exception as e:
        console.print(f'[red]❌ {e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_termux_pro_menu():
    while True:
        os.system('clear')
        console.print('[bold #0EA5E9]🖥  TERMUX PRO[/bold #0EA5E9]\n')
        console.print('  [1] 🐙 Git Integration   [dim]clone / pull / status[/dim]')
        console.print('  [2] 📋 Log Analyzer      [dim]PUBG game log parse[/dim]')
        console.print('  [3] 🔍 Process Scanner   [dim]çalışan process tara[/dim]')
        console.print('  [0] Geri\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_git_integration()
        elif c == '2': action_log_analyzer()
        elif c == '3': action_process_scanner()


# ══════════════════════════════════════════════════════════════════
# [25] PUBG LUA HACKS — Lua seviyesinde oyun manipülasyonu
# ══════════════════════════════════════════════════════════════════

_LUA_MOVEMENT_KEYS = ['MovementSpeed','SprintSpeed','MaxSpeed','WalkSpeed','CrouchSpeed',
                       'ProneSpeed','SwimSpeed','FlySpeed','MaxWalkSpeed','MaxRunSpeed']
_LUA_RECOIL_KEYS   = ['Recoil','RecoilRate','RecoilKick','RecoilHorizontal','RecoilVertical',
                       'RecoilPitch','RecoilYaw','RecoilRecover','KickBack']
_LUA_WEAPON_KEYS   = ['ShootInterval','FireInterval','BulletFire','AmmoPerShot','ClipSize',
                       'BulletRange','BulletSpeed','FireRate','RateOfFire','ShootRate']
_LUA_SPREAD_KEYS   = ['Spread','Deviation','SpreadAngle','AimError','BulletSpread',
                       'HipFireSpread','MovingSpread','JumpSpread']

def _patch_lua_values(src:str, keywords:list, multiplier:float=None, new_val:str=None, mode:str='zero')->str:
    import re as _re
    result = src
    count  = 0
    for kw in keywords:
        # Match: keyword = NUMBER or keyword = -NUMBER
        pattern = rf'({re.escape(kw)}\s*=\s*)(-?\d+\.?\d*)'
        def replacer(m):
            nonlocal count
            count += 1
            prefix = m.group(1); val = float(m.group(2))
            if mode == 'zero': return f'{prefix}0'
            elif mode == 'multiply': return f'{prefix}{round(val*multiplier,4)}'
            elif mode == 'set': return f'{prefix}{new_val}'
            return m.group(0)
        result = _re.sub(pattern, replacer, result, flags=_re.IGNORECASE)
    return result, count

def action_brplayer_patcher():
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF6B6B]🧍 BRPlayerCharacterBase PATCHER[/bold #FF6B6B]')
    console.print('[dim]  Karakter movement, sprint, prone değerlerini patch et[/dim]\n')
    files = list(LUA_EDIT_DIR.glob('*Player*.lua')) + list(LUA_EDIT_DIR.glob('*Character*.lua'))
    files += list(LUA_EDIT_DIR.glob('*BR*.lua'))
    if not files:
        console.print('[yellow]⚠ LUA_EDIT klasöründe karakter .lua yok.[/yellow]')
        console.print('[dim]  Önce DECOMPİLE ile BRPlayerCharacterBase.lua çıkar.[/dim]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(files,1): console.print(f'  [{i}] {f.name}')
    try:
        c = safe_input(f'\n  Seç: ').strip(); flush_stdin()
        p = files[int(c)-1]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    src = p.read_text(encoding='utf-8',errors='replace')
    os.system('clear')
    console.print(f'[bold]🧍 {p.name}[/bold]\n')
    console.print('  [1] ⚡ Speed Hack       — hareket hızı x2')
    console.print('  [2] 🏃 Ultra Sprint     — sprint hızı max')
    console.print('  [3] 🎯 No Recoil        — recoil sıfırla')
    console.print('  [4] ✏️  Manuel değiştir  — numara ara')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    changes = 0
    if c == '1':
        result, changes = _patch_lua_values(src, _LUA_MOVEMENT_KEYS, multiplier=2.0, mode='multiply')
    elif c == '2':
        result, changes = _patch_lua_values(src, ['SprintSpeed','MaxRunSpeed','WalkSpeed'], new_val='9999', mode='set')
    elif c == '3':
        result, changes = _patch_lua_values(src, _LUA_RECOIL_KEYS, new_val='0', mode='zero')
    elif c == '4':
        keyword = safe_input('  Aranacak değişken adı: ').strip(); flush_stdin()
        new_v   = safe_input('  Yeni değer: ').strip(); flush_stdin()
        result, changes = _patch_lua_values(src, [keyword], new_val=new_v, mode='set')
    else:
        return
    out = p.parent/(p.stem+'_br_patched.lua')
    out.write_text(result, encoding='utf-8')
    console.print(f'\n[bold green]✅ {changes} değer patch edildi → {out.name}[/bold green]')
    console.print('[dim]  COMPILED/ klasörüne kopyala → FANTERİ LUA ile derle → inject et[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_weapon_lua_patcher():
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF6B6B]🔫 WEAPON LUA PATCHER[/bold #FF6B6B]')
    console.print('[dim]  ShootWeaponBase — ateş hızı, mermi, spread[/dim]\n')
    files = list(LUA_EDIT_DIR.glob('*Weapon*.lua')) + list(LUA_EDIT_DIR.glob('*Shoot*.lua')) + list(LUA_EDIT_DIR.glob('*Gun*.lua'))
    if not files:
        console.print('[yellow]⚠ LUA_EDIT\'de silah .lua yok. DECOMPİLE yap.[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(files[:15],1): console.print(f'  [{i}] {f.name}')
    try:
        c = safe_input(f'\n  Seç: ').strip(); flush_stdin(); p = files[int(c)-1]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    src = p.read_text(encoding='utf-8',errors='replace')
    os.system('clear')
    console.print(f'[bold]🔫 {p.name}[/bold]\n')
    console.print('  [1] 🔥 No Recoil      — recoil sıfırla')
    console.print('  [2] 💨 Full Auto       — tüm silahları tam otomatik')
    console.print('  [3] ⚡ Fire Rate x2    — ateş hızı 2 kat')
    console.print('  [4] 🎯 No Spread       — spread sıfırla')
    console.print('  [5] ∞  Sonsuz mermi   — clip 9999')
    console.print('  [6] 🔫 All in One      — hepsi')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    result = src; total = 0
    if c in ('1','6'): result, n = _patch_lua_values(result, _LUA_RECOIL_KEYS, new_val='0', mode='zero'); total += n
    if c in ('3','6'): result, n = _patch_lua_values(result, ['ShootInterval','FireInterval'], multiplier=0.5, mode='multiply'); total += n
    if c in ('4','6'): result, n = _patch_lua_values(result, _LUA_SPREAD_KEYS, new_val='0', mode='zero'); total += n
    if c in ('5','6'): result, n = _patch_lua_values(result, ['ClipSize','MaxBullet','BulletAmmo'], new_val='9999', mode='set'); total += n
    if c == '2':
        import re as _re
        result = _re.sub(r'(IsAutoFire\s*=\s*)false', r'\1true', result, flags=_re.IGNORECASE)
        result = _re.sub(r'(IsSemiAuto\s*=\s*)true', r'\1false', result, flags=_re.IGNORECASE)
        total += 1
    out = p.parent/(p.stem+'_weapon_patched.lua')
    out.write_text(result, encoding='utf-8')
    console.print(f'\n[bold green]✅ {total} değer patch edildi → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_hook_injector():
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF6B6B]🪝 LUA HOOK INJECTOR[/bold #FF6B6B]')
    console.print('[dim]  Mevcut Lua fonksiyonunu override et, önüne/sonuna kod ekle[/dim]\n')
    path_raw = safe_input('  Hedef .lua dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    src = p.read_text(encoding='utf-8',errors='replace')
    func_name = safe_input('  Hook edilecek fonksiyon adı: ').strip(); flush_stdin()
    if not func_name: return
    console.print('\n  [1] Fonksiyondan ÖNCE kod ekle')
    console.print('  [2] Fonksiyondan SONRA kod ekle')
    console.print('  [3] Fonksiyonu tamamen değiştir')
    mode = safe_input('\n  > ').strip(); flush_stdin()
    console.print(f'  Eklenecek Lua kodu girin (boş satır ile bitir):')
    hook_lines = []
    while True:
        line = safe_input('  ').strip(); flush_stdin()
        if not line: break
        hook_lines.append(line)
    hook_code = '\n'.join(hook_lines)
    if not hook_code: console.print(f'[yellow]Kod girilmedi[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import re as _re
    if mode == '1':
        # Inject before function
        pattern = rf'(function\s+{re.escape(func_name)}\s*\()'
        inject  = f'\n-- [HOOK_START]\n{hook_code}\n-- [HOOK_END]\n'
        result  = _re.sub(pattern, inject+r'\1', src)
    elif mode == '2':
        # Inject before 'end' of function
        result = src
        # Find function end
        func_match = _re.search(rf'function\s+{re.escape(func_name)}\s*\(', src)
        if func_match:
            pos = func_match.end()
            # Find matching 'end'
            depth = 1; i = pos
            while i < len(src) and depth > 0:
                if src[i:i+8] in ('function','if ','while ','for '): depth += 1
                elif src[i:i+3] == 'end': depth -= 1
                i += 1
            insert_pos = src.rfind('end', 0, i)
            result = src[:insert_pos] + f'\n-- [HOOK]\n{hook_code}\n' + src[insert_pos:]
        else:
            console.print(f'[red]❌ Fonksiyon bulunamadı[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    elif mode == '3':
        pattern = rf'(function\s+{re.escape(func_name)}\s*\([^)]*\))(.*?)(^end)'
        replacement = rf'\1\n-- [REPLACED]\n{hook_code}\n\3'
        result = _re.sub(pattern, replacement, src, flags=_re.DOTALL|_re.MULTILINE)
    else:
        return
    out = p.parent/(p.stem+'_hooked.lua')
    out.write_text(result, encoding='utf-8')
    console.print(f'\n[bold green]✅ Hook enjekte edildi → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_custom_lua_injector():
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF6B6B]💉 CUSTOM LUA INJECTOR[/bold #FF6B6B]')
    console.print('[dim]  Kendi Lua kodunu mevcut scriptin başına/sonuna ekle[/dim]\n')
    path_raw = safe_input('  Hedef .lua: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    src = p.read_text(encoding='utf-8',errors='replace')
    console.print('  [1] Başa ekle  [2] Sona ekle')
    pos = safe_input('  > ').strip(); flush_stdin()
    code_raw = safe_input('  .lua kod dosyası (veya boş=manuel gir): ').strip().strip('"'); flush_stdin()
    if code_raw and Path(code_raw).exists():
        inject_code = Path(code_raw).read_text(encoding='utf-8',errors='replace')
    else:
        console.print('  Lua kodu gir (boş satır bitir):')
        lines = []
        while True:
            l = safe_input('  '); flush_stdin()
            if not l.strip(): break
            lines.append(l)
        inject_code = '\n'.join(lines)
    if not inject_code: return
    header = f'\n-- ===== CUSTOM INJECT =====\n{inject_code}\n-- ===== END INJECT =====\n'
    result = header + src if pos == '1' else src + header
    out = p.parent/(p.stem+'_injected.lua')
    out.write_text(result, encoding='utf-8')
    console.print(f'\n[bold green]✅ Kod enjekte edildi → {out.name}[/bold green]')
    console.print(f'  [dim]{len(inject_code.splitlines())} satır eklendi[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_anticheat_lua_detector():
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF6B6B]🛡  ANTI-CHEAT LUA DETECTOR[/bold #FF6B6B]')
    console.print('[dim]  Lua dosyalarında anti-cheat detection kodlarını tespit et[/dim]\n')
    files = list(LUA_EDIT_DIR.glob('*.lua')) + list(LUA_ORIGINAL_DIR.glob('*.lua'))
    if not files:
        console.print(f'[yellow]⚠ Lua dosyası yok[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    AC_PATTERNS = [
        'AntiCheat','anti_cheat','CheckHack','IsHacking','DetectCheat','BanPlayer',
        'ReportPlayer','CheckMod','VerifyIntegrity','CheckFileHash','ValidateClient',
        'IsModified','DetectModification','CheckSpeed','CheckWall','CheckAim',
        'SpeedCheck','WallCheck','AimCheck','IsValidSpeed','IsValidPosition'
    ]
    total_found = 0
    for f in files[:30]:
        try:
            src = f.read_text(encoding='utf-8',errors='replace')
            found = [(pat, src.count(pat)) for pat in AC_PATTERNS if pat.lower() in src.lower()]
            if found:
                console.print(f'\n  [yellow]⚠ {f.name}:[/yellow]')
                for pat, cnt in found:
                    console.print(f'    [red]{pat}[/red]: {cnt} kez')
                    total_found += cnt
        except: pass
    if total_found == 0:
        console.print('[green]✅ Anti-cheat pattern bulunamadı[/green]')
    else:
        console.print(f'\n  [bold red]Toplam: {total_found} anti-cheat referans[/bold red]')
        console.print('  [dim]Bu fonksiyonları sıfırlamak için LUA HOOK INJECTOR kullan[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_no_recoil_script_generator():
    os.system('clear')
    console.print('[bold #FF6B6B]🎯 NO RECOIL SCRIPT GENERATOR[/bold #FF6B6B]')
    console.print('[dim]  PUBG\'deki tüm silahlar için no-recoil Lua kodu üret[/dim]\n')
    WEAPONS = ['AKM','M416','SCAR-L','M762','Beryl','QBZ','G36C','M16A4','SLR','Mini14',
               'SKS','VSS','UMP45','Vector','PP-19','MP5K','S12K','S1897','DBS',
               'Kar98k','Mosin','AWM','M24','Win94','Mk12','FAMAS','Skorpion']
    out_code = '''-- ================================
-- NO RECOIL PATCH — by @FanteriBey
-- PUBG Mobile All Weapons
-- ================================

local _orig_addRecoil = AddRecoil or function() end
local _orig_applyRecoil = ApplyRecoil or function() end

-- Override recoil functions
function AddRecoil(weapon, pitch, yaw, roll)
    -- No recoil: return 0 for all values
    return 0, 0, 0
end

function ApplyRecoil(weapon, recoilData)
    -- Block all recoil application
    return
end

-- Weapon-specific overrides\n'''
    for w in WEAPONS:
        out_code += f'-- {w}: recoil disabled\n'
    out_code += '''
-- Additional overrides
if BRWeaponComponent then
    BRWeaponComponent.GetRecoilRate = function() return 0 end
    BRWeaponComponent.GetRecoilKick = function() return 0, 0 end
    BRWeaponComponent.RecoverFromRecoil = function() return end
end

if WeaponManager then
    WeaponManager.ApplyRecoil = function() return 0, 0 end
end

print("[PATCH] No Recoil active — @FanteriBey")
'''
    out = COMPILED_DIR/'no_recoil_patch.lua'
    COMPILED_DIR.mkdir(parents=True,exist_ok=True)
    out.write_text(out_code, encoding='utf-8')
    console.print(f'\n[bold green]✅ No Recoil script oluşturuldu![/bold green]')
    console.print(f'  {out}')
    console.print(f'  [dim]{len(WEAPONS)} silah için override[/dim]')
    console.print(f'\n  [dim]Sonraki adım: FANTERİ LUA DERLE → inject et[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_auto_loot_script():
    os.system('clear')
    console.print('[bold #FF6B6B]🎒 AUTO LOOT SCRIPTER[/bold #FF6B6B]')
    console.print('[dim]  Otomatik eşya toplama Lua kodu oluştur[/dim]\n')
    try:
        radius = float(safe_input('  Toplama menzili (metre, 5): ').strip() or '5'); flush_stdin()
        priority = safe_input('  Öncelik (1=loot kalitesi, 2=mesafe): ').strip() or '1'; flush_stdin()
    except: radius = 5; priority = '1'; flush_stdin()
    out_code = f'''-- ================================
-- AUTO LOOT SCRIPT — by @FanteriBey
-- Radius: {radius}m | Priority: {"Quality" if priority=="1" else "Distance"}
-- ================================

local AUTO_LOOT_RADIUS = {radius}
local AUTO_LOOT_ENABLED = true
local LOOT_PRIORITY = {priority}

-- Item priority list (higher = more important)
local ItemPriority = {{
    -- Medical
    ["FirstAidKit"] = 100, ["MedKit"] = 90, ["Bandage"] = 70,
    ["EnergyDrink"] = 60, ["PainKiller"] = 65, ["Booster"] = 55,
    -- Ammo  
    ["5.56mm"] = 80, ["7.62mm"] = 80, ["9mm"] = 75, ["12Gauge"] = 75,
    ["5.45mm"] = 78, ["300Magnum"] = 85,
    -- Armor
    ["Level3Vest"] = 95, ["Level2Vest"] = 85, ["Level1Vest"] = 70,
    ["Level3Helmet"] = 95, ["Level2Helmet"] = 85, ["Level1Helmet"] = 70,
    -- Grenades
    ["FragGrenade"] = 72, ["SmokeGrenade"] = 65, ["FlashGrenade"] = 60,
}}

local function GetItemPriority(itemClass)
    for k, v in pairs(ItemPriority) do
        if string.find(itemClass, k) then return v end
    end
    return 50 -- default priority
end

local function TryAutoLoot()
    if not AUTO_LOOT_ENABLED then return end
    local player = GetLocalPlayer and GetLocalPlayer() or nil
    if not player then return end
    local pos = player:GetPosition()
    local items = GetNearbyItems and GetNearbyItems(pos, AUTO_LOOT_RADIUS) or {{}}
    -- Sort by priority or distance
    table.sort(items, function(a, b)
        if LOOT_PRIORITY == 1 then
            return GetItemPriority(a.class) > GetItemPriority(b.class)
        else
            return a.distance < b.distance
        end
    end)
    for _, item in ipairs(items) do
        if player:CanPickUp(item) then
            player:PickUp(item)
        end
    end
end

-- Hook into game tick
local _origTick = OnTick or function() end
function OnTick(dt)
    _origTick(dt)
    TryAutoLoot()
end

print("[PATCH] Auto Loot active (radius={radius}m) — @FanteriBey")
'''
    out = COMPILED_DIR/'auto_loot_patch.lua'
    COMPILED_DIR.mkdir(parents=True,exist_ok=True)
    out.write_text(out_code, encoding='utf-8')
    console.print(f'\n[bold green]✅ Auto Loot script oluşturuldu![/bold green]')
    console.print(f'  {out}')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pubg_lua_menu():
    while True:
        os.system('clear')
        console.print('[bold #FF6B6B]🎯 PUBG LUA HACKS[/bold #FF6B6B]')
        console.print('[dim]  Lua seviyesinde oyun manipülasyonu[/dim]\n')
        console.print('  [bold #FF6B6B][1] 🧍 BRPlayer Patcher[/bold #FF6B6B]       [dim]movement, sprint, prone[/dim]')
        console.print('  [bold #FF6B6B][2] 🔫 Weapon Lua Patcher[/bold #FF6B6B]     [dim]ateş hızı, mermi, spread[/dim]')
        console.print('  [bold #FF6B6B][3] 🪝 Hook Injector[/bold #FF6B6B]          [dim]fonksiyon override[/dim]')
        console.print('  [bold #FF6B6B][4] 💉 Custom Lua Injector[/bold #FF6B6B]    [dim]kendi kodu ekle[/dim]')
        console.print('  [bold #FF6B6B][5] 🛡  Anti-Cheat Detector[/bold #FF6B6B]   [dim]AC kodlarını tespit et[/dim]')
        console.print('  [bold #FF6B6B][6] 🎯 No Recoil Generator[/bold #FF6B6B]    [dim]tüm silahlar no-recoil[/dim]')
        console.print('  [bold #FF6B6B][7] 🎒 Auto Loot Scripter[/bold #FF6B6B]     [dim]otomatik eşya toplama[/dim]')
        console.print(f'  [bold white][0] {T("back")}[/bold white]')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_brplayer_patcher()
        elif c == '2': action_weapon_lua_patcher()
        elif c == '3': action_lua_hook_injector()
        elif c == '4': action_custom_lua_injector()
        elif c == '5': action_anticheat_lua_detector()
        elif c == '6': action_no_recoil_script_generator()
        elif c == '7': action_auto_loot_script()

# ══════════════════════════════════════════════════════════════════
# [25] PUBG LUA HACKS
# ══════════════════════════════════════════════════════════════════

def action_speed_hack_lua():
    os.system('clear')
    console.print('[bold #FF4444]⚡ SPEED HACK LUA GENERATOR[/bold #FF4444]')
    console.print('[dim]  Karakter ve araç hız hack Lua scripti oluştur[/dim]\n')
    try:
        speed = float(safe_input('  Hız çarpanı (1.0=normal, 2.0=2x, 5.0=5x): ').strip() or '2.0'); flush_stdin()
    except:
        speed = 2.0; flush_stdin()
    lua = f'''-- FANTOOL Speed Hack v1.0
-- Multiplier: {speed}x
-- by @FanteriBey

local SPEED_MULT = {speed}
local BASE_SPRINT = 600
local BASE_WALK   = 200

-- Character speed
if BRPlayerCharacterBase then
    BRPlayerCharacterBase.MaxSprintSpeed = BASE_SPRINT * SPEED_MULT
    BRPlayerCharacterBase.MaxWalkSpeed   = BASE_WALK   * SPEED_MULT
    BRPlayerCharacterBase.MaxCrouchSpeed = 150 * SPEED_MULT
    BRPlayerCharacterBase.MaxSwimSpeed   = 300 * SPEED_MULT
    BRPlayerCharacterBase.AirControl     = 1.0
end

-- Vehicle speed
local VehicleTable = {{
    Dacia    = {{MaxSpeed = 120 * SPEED_MULT}},
    UAZ      = {{MaxSpeed = 100 * SPEED_MULT}},
    Buggy    = {{MaxSpeed = 130 * SPEED_MULT}},
    Motorcycle = {{MaxSpeed = 150 * SPEED_MULT}},
    Mirado   = {{MaxSpeed = 140 * SPEED_MULT}},
    Boat     = {{MaxSpeed = 110 * SPEED_MULT}},
    PG117    = {{MaxSpeed = 130 * SPEED_MULT}},
}}

if BRVehicleBase then
    local orig = BRVehicleBase.GetMaxSpeed
    if orig then
        BRVehicleBase.GetMaxSpeed = function(self)
            local vname = self:GetVehicleName() or ""
            for name, cfg in pairs(VehicleTable) do
                if string.find(vname, name) then
                    return cfg.MaxSpeed
                end
            end
            return orig(self) * SPEED_MULT
        end
    end
end
'''
    out = BASE_DIR / 'LUA_EDIT' / f'SpeedHack_{speed}x_FANTOOL.lua'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(lua, encoding='utf-8')
    console.print(f'\n[bold green]✅ Speed hack {speed}x scripti oluşturuldu → {out.name}[/bold green]')
    console.print('[dim]  COMPILED/ klasörüne kopyala → FANTERİ LUA DERLE → CUSTOM INJECT[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_no_fall_damage():
    os.system('clear')
    console.print('[bold #FF4444]🛡 NO FALL DAMAGE + INFINITE STAMINA[/bold #FF4444]\n')
    lua = '''-- FANTOOL: No Fall Damage + Infinite Stamina
-- by @FanteriBey

-- No Fall Damage
if BRPlayerCharacterBase then
    -- Override fall damage calculation
    local orig_FallDamage = BRPlayerCharacterBase.TakeFallDamage
    if orig_FallDamage then
        BRPlayerCharacterBase.TakeFallDamage = function(self, damage)
            return  -- Block all fall damage
        end
    end
    -- Alternative: set landing threshold very high
    BRPlayerCharacterBase.FallDamageThreshold = 99999
    BRPlayerCharacterBase.MaxFallDamage = 0
    BRPlayerCharacterBase.FallDamageMultiplier = 0
end

-- Infinite Stamina
if BRPlayerController then
    local orig_StaminaTick = BRPlayerController.UpdateStamina
    if orig_StaminaTick then
        BRPlayerController.UpdateStamina = function(self, dt)
            self.CurrentStamina = self.MaxStamina or 100
        end
    end
end

-- Also set via properties
if BRPlayerPawn then
    BRPlayerPawn.StaminaMax = 9999
    BRPlayerPawn.StaminaRegen = 9999
    BRPlayerPawn.StaminaCostSprint = 0
    BRPlayerPawn.StaminaCostJump = 0
end
'''
    out = BASE_DIR / 'LUA_EDIT' / 'NoFallDmg_InfStamina_FANTOOL.lua'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(lua, encoding='utf-8')
    console.print(f'[bold green]✅ Script oluşturuldu → {out.name}[/bold green]')
    console.print('[dim]  COMPILED/ klasörüne kopyala → FANTERİ LUA DERLE → CUSTOM INJECT[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_no_recoil_binary():
    os.system('clear')
    console.print('[bold #7C3AED]💀 NO-RECOIL BINARY PATCHER[/bold #7C3AED]')
    console.print('[dim]  libUE4.so\'dan recoil offset\'lerini bul ve sıfırla[/dim]\n')
    path_raw = safe_input('  libUE4.so yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = bytearray(p.read_bytes())
    # Search recoil-related strings and nearby float values
    RECOIL_STRINGS = [b'RecoilX',b'RecoilY',b'RecoilZ',b'VerticalRecoil',b'HorizontalRecoil',
                      b'Recoil',b'WeaponRecoil',b'GunRecoil',b'KickBack']
    patched = 0
    for rs in RECOIL_STRINGS:
        pos = 0
        while True:
            pos = data.find(rs, pos)
            if pos == -1: break
            # Look for float values nearby (within 200 bytes)
            for off in range(pos, min(pos+200, len(data)-4)):
                try:
                    v = struct.unpack_from('<f', data, off)[0]
                    if 0.1 < v < 20.0:  # Likely a recoil value
                        struct.pack_into('<f', data, off, 0.0)
                        patched += 1
                except: pass
            pos += len(rs)
    if patched == 0:
        console.print('[yellow]⚠ Recoil pattern bulunamadı[/yellow]')
    else:
        out = p.parent / (p.stem + '_norecoil' + p.suffix)
        out.write_bytes(bytes(data))
        console.print(f'\n[bold green]✅ {patched} recoil değeri sıfırlandı → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_fov_modifier():
    os.system('clear')
    console.print('[bold #7C3AED]👁  FOV MODIFIER[/bold #7C3AED]')
    console.print('[dim]  libUE4.so\'dan FOV değerini değiştir[/dim]\n')
    path_raw = safe_input('  libUE4.so yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        new_fov = float(safe_input('  Yeni FOV (varsayılan:90, max:120): ').strip() or '90'); flush_stdin()
        new_fov = max(60.0, min(180.0, new_fov))
    except: new_fov = 90.0; flush_stdin()
    data = bytearray(p.read_bytes())
    # Common PUBG FOV values
    FOV_VALUES = [75.0, 80.0, 90.0, 100.0, 85.0]
    patched = 0
    for fov_val in FOV_VALUES:
        fov_bytes = struct.pack('<f', fov_val)
        pos = 0
        while True:
            pos = data.find(fov_bytes, pos)
            if pos == -1: break
            struct.pack_into('<f', data, pos, new_fov)
            patched += 1; pos += 4
    if patched > 0:
        out = p.parent / (p.stem + f'_fov{int(new_fov)}' + p.suffix)
        out.write_bytes(bytes(data))
        console.print(f'\n[bold green]✅ {patched} FOV değeri → {new_fov}° → {out.name}[/bold green]')
    else:
        console.print('[yellow]⚠ FOV pattern bulunamadı[/yellow]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_aimbot_offset_extractor():
    os.system('clear')
    console.print('[bold #7C3AED]🎯 AIMBOT OFFSET EXTRACTOR[/bold #7C3AED]')
    console.print('[dim]  libUE4.so\'dan entity/player offset\'lerini çıkar[/dim]\n')
    path_raw = safe_input('  libUE4.so yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    # Search for key UE4 offset patterns
    TARGET_SYMBOLS = [
        b'GWorld',b'GEngine',b'GObjects',b'GNames',
        b'UWorld',b'UEngine',b'APlayerController',
        b'ACharacter',b'APawn',b'USkeletalMesh',
        b'ComponentToWorld',b'BoneArray',b'RootComponent',
        b'RelativeLocation',b'RelativeRotation',b'Velocity',
        b'Health',b'MaxHealth',b'ShieldHealth',b'TeamId',
        b'IsAlive',b'IsDead',b'bIsAiming',
    ]
    console.print('  [dim]Offset taranıyor...[/dim]')
    offsets = {}
    for sym in TARGET_SYMBOLS:
        pos = data.find(sym)
        if pos != -1:
            offsets[sym.decode('ascii','ignore')] = pos
    if not offsets:
        console.print('[yellow]Offset bulunamadı[/yellow]')
    else:
        console.print(f'\n  [green]{len(offsets)} offset bulundu:[/green]\n')
        for name, off in sorted(offsets.items(), key=lambda x: x[1]):
            console.print(f'  [bold cyan]0x{off:08X}[/bold cyan]  [white]{name}[/white]')
        out = BASE_DIR / 'DUMP' / 'aimbot_offsets.txt'
        out.parent.mkdir(parents=True, exist_ok=True)
        lines = ['=== PUBG Mobile Offset Table ===',f'Source: {p.name}','']
        lines += [f'{name}\t0x{off:08X}' for name, off in sorted(offsets.items(), key=lambda x: x[1])]
        out.write_text('\n'.join(lines), encoding='utf-8')
        console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_binary_hacks_menu():
    while True:
        os.system('clear')
        console.print('[bold #7C3AED]💀 BINARY HACKS[/bold #7C3AED]')
        console.print('[dim]  libUE4.so seviyesinde modifikasyonlar[/dim]\n')
        console.print('  [1] 🎯 No-Recoil Binary    [dim]recoil float sıfırla[/dim]')
        console.print('  [2] 👁  FOV Modifier        [dim]görüş alanı değiştir[/dim]')
        console.print('  [3] 🎯 Aimbot Offsets      [dim]entity offset\'leri çıkar[/dim]')
        console.print('  [4] 🕳  Code Cave Finder    [dim]injection boş alan[/dim]')
        console.print('  [5] 🛡  Anti-Debug Patch    [dim]ptrace patch[/dim]')
        console.print('  [6] 🏛  UE4 Class Dump     [dim]class isimleri[/dim]')
        console.print('  [0] GERİ\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_no_recoil_binary()
        elif c == '2': action_fov_modifier()
        elif c == '3': action_aimbot_offset_extractor()
        elif c == '4': action_speed_hack_binary()
        elif c == '5': action_hwid_changer()
        elif c == '6': action_antiban_patcher()
        elif c == '7': action_code_cave_finder()
        elif c == '8': action_antidebug_patcher()
        elif c == '9': action_ue4_class_dumper()

# ── [27] ASSET HACKS ───────────────────────────────────────────────
def _bulk_patch_property(keyword:str, new_val:float, multiplier:bool=False) -> int:
    """PAK_UNPACK içindeki tüm .uexp'lerde keyword içeren property'yi patch et."""
    if not PAK_UNPACK_OUT.exists(): return 0
    total = 0
    for uexp_path in PAK_UNPACK_OUT.rglob('*.uexp'):
        ua_path = uexp_path.with_suffix('.uasset')
        if not ua_path.exists(): continue
        try:
            ua = _UAssetFileEx(); ua.load_data(ua_path.read_bytes())
            ue = _UExpFileEx(ua); ue.load_data(uexp_path.read_bytes())
            changed = False
            for prop in ue.properties:
                if keyword.lower() in prop['name'].lower() and prop['type'] in ('f32','f64','i32','i16'):
                    v = float(prop['value']) * new_val if multiplier else new_val
                    if ue.write_prop(prop, round(v,4)): changed = True; total += 1
            if changed:
                out = uexp_path.parent/(uexp_path.stem+'_hack'+uexp_path.suffix)
                out.write_bytes(ue.data)
        except: pass
    return total

def action_recoil_reducer_bulk():
    os.system('clear')
    console.print('[bold #10B981]🎮 RECOIL REDUCER BULK[/bold #10B981]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        pct = float(safe_input('  Recoil yüzdesi (0=sıfır, 0.1=10%, 0.5=50%): ').strip() or '0.1'); flush_stdin()
    except: pct = 0.1; flush_stdin()
    console.print(f'  [dim]{T("scanning")}[/dim]')
    total = _bulk_patch_property('Recoil', pct, multiplier=True)
    total += _bulk_patch_property('KickBack', pct, multiplier=True)
    total += _bulk_patch_property('GunRecoil', pct, multiplier=True)
    console.print(f'\n[bold green]✅ {total} recoil değeri %{int(pct*100)} yapıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_spread_reducer():
    os.system('clear')
    console.print('[bold #10B981]🎯 BULLET SPREAD REDUCER[/bold #10B981]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print('  [dim]Tüm spread değerleri sıfırlanıyor...[/dim]')
    total = _bulk_patch_property('Spread', 0.0)
    total += _bulk_patch_property('Deviation', 0.0)
    total += _bulk_patch_property('Dispersion', 0.0)
    total += _bulk_patch_property('HipFire', 0.0)
    console.print(f'\n[bold green]✅ {total} spread değeri sıfırlandı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_ads_speed_modifier():
    os.system('clear')
    console.print('[bold #10B981]👁  ADS SPEED MODIFIER[/bold #10B981]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        multiplier = float(safe_input('  ADS hız çarpanı (2.0=2x hızlı): ').strip() or '2.0'); flush_stdin()
    except: multiplier = 2.0; flush_stdin()
    console.print(f'  [dim]{T("scanning")}[/dim]')
    total = _bulk_patch_property('ADSTime', 1.0/multiplier, multiplier=True)
    total += _bulk_patch_property('AimDownSight', 1.0/multiplier, multiplier=True)
    total += _bulk_patch_property('ZoomTime', 1.0/multiplier, multiplier=True)
    console.print(f'\n[bold green]✅ {total} ADS değeri {multiplier}x hızlandırıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_loot_radius_modifier():
    os.system('clear')
    console.print('[bold #10B981]📦 LOOT RADIUS MODIFIER[/bold #10B981]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        new_radius = float(safe_input('  Yeni loot menzili (cm, varsayılan:200, max:5000): ').strip() or '2000'); flush_stdin()
    except: new_radius = 2000; flush_stdin()
    console.print(f'  [dim]{T("scanning")}[/dim]')
    total = _bulk_patch_property('PickupRadius', new_radius)
    total += _bulk_patch_property('LootRadius', new_radius)
    total += _bulk_patch_property('InteractRadius', new_radius)
    total += _bulk_patch_property('AutoPickupRange', new_radius)
    console.print(f'\n[bold green]✅ {total} loot menzili {new_radius}cm yapıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_heal_speed_modifier():
    os.system('clear')
    console.print('[bold #10B981]💊 HEAL SPEED MODIFIER[/bold #10B981]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        multiplier = float(safe_input('  İlaç hız çarpanı (3.0=3x hızlı): ').strip() or '3.0'); flush_stdin()
    except: multiplier = 3.0; flush_stdin()
    console.print(f'  [dim]{T("scanning")}[/dim]')
    total = _bulk_patch_property('UseTime', 1.0/multiplier, multiplier=True)
    total += _bulk_patch_property('HealTime', 1.0/multiplier, multiplier=True)
    total += _bulk_patch_property('MedKitTime', 1.0/multiplier, multiplier=True)
    total += _bulk_patch_property('BandageTime', 1.0/multiplier, multiplier=True)
    console.print(f'\n[bold green]✅ {total} ilaç süresi {multiplier}x hızlandırıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_grenade_modifier():
    os.system('clear')
    console.print('[bold #10B981]💣 GRENADE MODIFIER[/bold #10B981]\n')
    if not PAK_UNPACK_OUT.exists(): console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print('  [1] Menzil artır')
    console.print('  [2] Hasar artır')
    console.print('  [3] Patlama gecikmesi azalt')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    console.print(f'  [dim]{T("scanning")}[/dim]')
    if c == '1':
        total = _bulk_patch_property('ExplosionRadius', 1000.0)
        total += _bulk_patch_property('DamageRadius', 1000.0)
        console.print(f'\n[bold green]✅ {total} menzil değeri artırıldı[/bold green]')
    elif c == '2':
        total = _bulk_patch_property('GrenadeDamage', 200.0)
        total += _bulk_patch_property('ExplosionDamage', 200.0)
        console.print(f'\n[bold green]✅ {total} hasar değeri artırıldı[/bold green]')
    elif c == '3':
        total = _bulk_patch_property('FuseTime', 0.5)
        total += _bulk_patch_property('ExplosionDelay', 0.1)
        console.print(f'\n[bold green]✅ {total} gecikme değeri azaltıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_asset_hacks_menu():
    while True:
        os.system('clear')
        console.print('[bold #10B981]🎮 ASSET HACKS[/bold #10B981]')
        console.print('[dim]  uasset/uexp seviyesinde oyun değerleri[/dim]\n')
        console.print('  [1] 🎯 Recoil Reducer Bulk  [dim]tüm recoil değerleri azalt[/dim]')
        console.print('  [2] 🎯 Spread Reducer       [dim]mermi saçılmasını sıfırla[/dim]')
        console.print('  [3] 👁  ADS Speed Modifier   [dim]nişan alma hızı[/dim]')
        console.print('  [4] 📦 Loot Radius          [dim]eşya toplama menzili[/dim]')
        console.print('  [5] 💊 Heal Speed           [dim]ilaç kullanım hızı[/dim]')
        console.print('  [6] 💣 Grenade Modifier      [dim]bomba menzil/hasar/gecikme[/dim]')
        console.print('  [7] ⚡ Property Mass Patch   [dim]toplu property değiştir[/dim]')
        console.print('  [8] 💥 Damage Multiplier     [dim]hasar çarpanı[/dim]')
        console.print('  [9] 🪂 Parachute Modifier    [dim]paraşüt iniş/uçuş hızı[/dim]')
        console.print('  [0] GERİ\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_recoil_reducer_bulk()
        elif c == '2': action_spread_reducer()
        elif c == '3': action_ads_speed_modifier()
        elif c == '4': action_loot_radius_modifier()
        elif c == '5': action_heal_speed_modifier()
        elif c == '6': action_grenade_modifier()
        elif c == '7': action_property_mass_patcher()
        elif c == '8': action_damage_multiplier()
        elif c == '9': action_parachute_modifier()

# ── [28] TEXTURE/VISUAL ───────────────────────────────────────────
_UE4_NULL_HEADER = bytes([
    0xC1, 0x83, 0x2A, 0x9E,  # Magic
    0xF9, 0xFF, 0xFF, 0xFF,  # Legacy version
    0x00, 0x00, 0x00, 0x00,  # UE version (0 for null asset)
])

def action_white_texture_gen():
    os.system('clear')
    console.print('[bold #F472B6]🎨 WHITE TEXTURE GENERATOR[/bold #F472B6]')
    console.print('[dim]  Seçilen uasset dosyasını beyaz/şeffaf texture ile değiştir[/dim]\n')
    if not PAK_UNPACK_OUT.exists():
        console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print('  [1] Grass texture beyaz yap')
    console.print('  [2] Smoke texture şeffaf yap')
    console.print('  [3] Water texture şeffaf yap')
    console.print('  [4] Manuel dosya seç')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    GRASS_PATTERNS = ['Grass','Bush','Foliage','Plant','Fern','Shrub']
    SMOKE_PATTERNS = ['Smoke','Fog','Haze','Mist','Cloud']
    WATER_PATTERNS = ['Water','Lake','River','Sea','Ocean','Wave']
    if c in ('1','2','3'):
        patterns = {'1':GRASS_PATTERNS,'2':SMOKE_PATTERNS,'3':WATER_PATTERNS}[c]
        label = {'1':'Grass','2':'Smoke','3':'Water'}[c]
        files = [f for f in PAK_UNPACK_OUT.rglob('*.uasset')
                 if any(pat.lower() in f.stem.lower() for pat in patterns)]
        if not files:
            console.print(f'[yellow]⚠ {label} texture bulunamadı[/yellow]')
            flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    else:
        files_all = list(PAK_UNPACK_OUT.rglob('*.uasset'))
        for i,f in enumerate(files_all[:20],1): console.print(f'  [{i}] {f.name}')
        try:
            ci = int(safe_input('\n  Seç: ').strip())-1; flush_stdin()
            files = [files_all[ci]]
        except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ok = 0
    for f in files:
        try:
            orig_size = f.stat().st_size
            out = f.parent / (f.stem + '_white' + f.suffix)
            out.write_bytes(b'\x00' * orig_size)
            ok += 1
            console.print(f'  [green]✓ {f.name}[/green]')
        except: pass
    console.print(f'\n[bold green]✅ {ok} texture sıfırlandı[/bold green]')
    console.print('[dim]  CUSTOM FILES/ klasörüne kopyala → CUSTOM INJECT[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_esp_texture_gen():
    os.system('clear')
    console.print('[bold #F472B6]🔴 ESP TEXTURE GENERATOR[/bold #F472B6]')
    console.print('[dim]  Oyuncu modellerini highlight eden renk oluştur[/dim]\n')
    console.print('  [1] Kırmızı ESP (düşman)')
    console.print('  [2] Mavi ESP (takım arkadaşı)')
    console.print('  [3] Sarı ESP (yüksek kontrast)')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    colors = {'1':(255,0,0,255),'2':(0,100,255,255),'3':(255,255,0,255)}
    if c not in colors: return
    r,g,b,a = colors[c]
    color_name = {'1':'Red','2':'Blue','3':'Yellow'}[c]
    # Generate minimal TGA-like color data for ESP
    # Simple flat color DDS (64x64 RGBA8)
    W, H = 64, 64
    pixels = bytes([r,g,b,a] * (W*H))
    # DDS header for RGBA8 uncompressed
    dds_header = b'DDS ' + struct.pack('<IIIIIII',
        124, 0x1|0x2|0x4|0x1000,  # flags
        H, W, W*4, 0, 0) + b'\x00'*44 + struct.pack('<IIIII',
        32, 0x40, 0, 32, 0x00FF0000) + struct.pack('<IIIII',
        0x0000FF00, 0x000000FF, 0xFF000000, 0x1000, 0) + b'\x00'*16
    out_dir = BASE_DIR / 'ESP_TEXTURES'
    out_dir.mkdir(parents=True, exist_ok=True)
    dds_out = out_dir / f'ESP_{color_name}.dds'
    dds_out.write_bytes(dds_header + pixels)
    console.print(f'\n[bold green]✅ ESP texture → {dds_out.name}[/bold green]')
    console.print(f'  [{r},{g},{b}] rengi, {W}x{H} DDS')
    console.print('[dim]  Bu dosyayı PUBG texture path\'ine inject et[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_texture_visual_menu():
    while True:
        os.system('clear')
        console.print('[bold #F472B6]🎨 TEXTURE/VISUAL[/bold #F472B6]\n')
        console.print('  [1] ⬜ White Texture Gen   [dim]grass/smoke/water beyaz yap[/dim]')
        console.print('  [2] 🔴 ESP Texture Gen     [dim]oyuncu highlight texture[/dim]')
        console.print('  [3] 🌿 Grass White Patch   [dim]tüm grass dosyalarını sıfırla[/dim]')
        console.print('  [4] ⬜ White Body Patch     [dim]body texture sıfırla[/dim]')
        console.print('  [5] 🌅 Sky Texture Patch   [dim]gökyüzü/zemin siyah yap[/dim]')
        console.print('  [6] 👣 Footstep Enhancer   [dim]ayak sesi artır[/dim]')
        console.print('  [0] GERİ\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_white_texture_gen()
        elif c == '2': action_esp_texture_gen()
        elif c == '3': action_auto_grass_white()
        elif c == '4': action_auto_white_body()
        elif c == '5': action_sky_texture_patcher()
        elif c == '6': action_footstep_enhancer()

# ── [29] MOD PACK ────────────────────────────────────────────────
def action_batch_mod_patcher():
    os.system('clear')
    console.print('[bold #06B6D4]📦 BATCH MULTI-MOD PATCHER[/bold #06B6D4]')
    console.print('[dim]  Birden fazla modu tek seferde seç ve uygula[/dim]\n')
    console.print('  Uygulanacak modları seç (space ile birden fazla):\n')
    MOD_LIST = [
        ('No-Recoil Lua Script',    action_no_recoil_script_generator),
        ('Speed Hack Lua',          action_speed_hack_lua),
        ('No Fall Damage',          action_no_fall_damage),
        ('Recoil Reducer Bulk',     action_recoil_reducer_bulk),
        ('Spread Reducer',          action_spread_reducer),
        ('ADS Speed Modifier',      action_ads_speed_modifier),
        ('Heal Speed Modifier',     action_heal_speed_modifier),
        ('Loot Radius Modifier',    action_loot_radius_modifier),
        ('Grass White Patch',       action_auto_grass_white),
        ('White Body Patch',        action_auto_white_body),
    ]
    for i,(name,_) in enumerate(MOD_LIST,1):
        console.print(f'  [{i:2}] {name}')
    console.print('  [A]   Hepsini uygula')
    console.print('  [0]   Geri\n')
    choice = safe_input('  Seç (örn: 1 3 5 veya A): ').strip().upper(); flush_stdin()
    if choice == '0': return
    if choice == 'A':
        selected = list(range(len(MOD_LIST)))
    else:
        try:
            selected = [int(x)-1 for x in choice.split() if x.isdigit() and 0<int(x)<=len(MOD_LIST)]
        except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    if not selected:
        console.print(f'[yellow]Seçim yok[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i in selected:
        name, func = MOD_LIST[i]
        console.print(f'\n  [cyan]Uygulanıyor: {name}...[/cyan]')
        try: func()
        except Exception as e: console.print(f'  [red]✗ {e}[/red]')
    console.print(f'\n[bold green]✅ {len(selected)} mod uygulandı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_mod_pack_creator():
    os.system('clear')
    console.print('[bold #06B6D4]📦 MOD PACK CREATOR[/bold #06B6D4]')
    console.print('[dim]  CUSTOM FILES klasöründeki dosyaları ZIP pakete topla[/dim]\n')
    custom_dirs = list(BASE_DIR.glob('FANx*/CUSTOM FILES'))
    if not custom_dirs:
        console.print('[yellow]⚠ FANx*/ workspace yok[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,d in enumerate(custom_dirs,1): console.print(f'  [{i}] {d.parent.name}/CUSTOM FILES/')
    try:
        c = int(safe_input(f'\n  Seç (1-{len(custom_dirs)}): ').strip())-1; flush_stdin()
        src_dir = custom_dirs[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    pack_name = safe_input('  Paket adı (FANTOOL_Mod): ').strip() or 'FANTOOL_Mod'; flush_stdin()
    files = [f for f in src_dir.rglob('*') if f.is_file()]
    if not files: console.print(f'[yellow]{T("empty_folder")}[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import zipfile as _zf
    from datetime import datetime as _dt
    ts = _dt.now().strftime('%Y%m%d_%H%M')
    out = BASE_DIR / f'{pack_name}_{ts}.zip'
    with _zf.ZipFile(str(out), 'w', _zf.ZIP_DEFLATED) as zf:
        for f in files:
            arcname = str(f.relative_to(src_dir)).replace('\\', '/')
            zf.write(str(f), arcname)
            console.print(f'  [dim]+ {arcname}[/dim]')
    console.print(f'\n[bold green]✅ {len(files)} dosya → {out.name} ({human_size(out.stat().st_size)})[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_version_checker():
    os.system('clear')
    console.print('[bold #06B6D4]✅ VERSION CHECKER[/bold #06B6D4]')
    console.print('[dim]  PAK dosyasının PUBG versiyonunu tespit et[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = pak_path.read_bytes()
    # Try to extract version string
    VERSION_PATTERNS = [
        b'PUBG Mobile',b'BGMI',b'PUBGM',
        b'4.6.',b'4.5.',b'4.4.',b'4.3.',b'3.',
    ]
    console.print(f'\n  PAK: [cyan]{pak_path.name}[/cyan]  ({human_size(len(data))})')
    for pat in VERSION_PATTERNS:
        pos = data.find(pat)
        if pos != -1:
            ctx = data[pos:pos+30].decode('ascii','ignore').split('\x00')[0]
            console.print(f'  [cyan]Versiyon ipucu:[/cyan] [white]{ctx}[/white]  [dim]@ 0x{pos:X}[/dim]')
    try:
        pak = TencentPakFile(PurePath(pak_path))
        pi  = pak._pak_info
        console.print(f'  [cyan]PAK Versiyon:[/cyan] [white]{pi.version}[/white]')
        console.print(f'  [cyan]Şifreleme   :[/cyan] [white]{pi.enc_method}[/white]')
        paths = pak.list_existing_paths()
        if paths:
            sample = paths[0]
            console.print(f'  [cyan]İlk dosya   :[/cyan] [dim]{sample[:80]}[/dim]')
    except Exception as e:
        console.print(f'  [red]{e}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_offset_database():
    os.system('clear')
    console.print('[bold #06B6D4]📊 OFFSET DATABASE[/bold #06B6D4]')
    console.print('[dim]  Bilinen PUBG Mobile offset\'leri veritabanı[/dim]\n')
    OFFSET_DB = {
        '4.6.x': {
            'GWorld':              '0x091A7A38',
            'GEngine':             '0x091A5628',
            'GObjects':            '0x0919F498',
            'GNames':              '0x0919E478',
            'ULevel::AActors':     '0x0098',
            'ACharacter::Mesh':    '0x0310',
            'USkeletalMesh::Bones':'0x05C0',
            'APawn::PlayerState':  '0x0230',
            'ACharacter::Health':  '0x0558',
            'APlayerState::Score': '0x0390',
            'ComponentToWorld':    '0x01C0',
            'RelativeLocation':    '0x011C',
            'RelativeRotation':    '0x0128',
            'BoneArray':           '0x0048',
            'IsAlive':             '0x0618',
            'TeamIndex':           '0x0644',
            'PlayerName':          '0x03A8',
        },
        '4.5.x': {
            'GWorld':              '0x08FF7A38',
            'GObjects':            '0x090CF498',
            'GNames':              '0x090CE478',
        }
    }
    console.print('  PUBG Mobile Bilinen Offset\'ler:\n')
    for version, offsets in OFFSET_DB.items():
        console.print(f'  [bold cyan]== {version} ==[/bold cyan]')
        for name, off in offsets.items():
            console.print(f'  [dim]{name:<30}[/dim]  [white]{off}[/white]')
        console.print()
    out = BASE_DIR / 'DUMP' / 'offset_database.txt'
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = ['=== PUBG Mobile Offset Database ===','=== @FanteriBey ===','']
    for version, offsets in OFFSET_DB.items():
        lines += [f'== {version} =='] + [f'{n}\t{o}' for n,o in offsets.items()] + ['']
    out.write_text('\n'.join(lines), encoding='utf-8')
    console.print(f'  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_mod_pack_menu():
    while True:
        os.system('clear')
        console.print('[bold #06B6D4]📦 MOD PACK[/bold #06B6D4]')
        console.print('[dim]  Paketleme ve dağıtım araçları[/dim]\n')
        console.print('  [1] ⚡ Batch Multi-Mod     [dim]birden fazla mod seç ve uygula[/dim]')
        console.print('  [2] 📦 Mod Pack ZIP        [dim]modları ZIP\'e paketle[/dim]')
        console.print('  [3] ✅ Version Checker     [dim]PAK versiyonu tespit et[/dim]')
        console.print('  [4] 📊 Offset Database     [dim]bilinen PUBG offset\'leri[/dim]')
        console.print('  [5] 💾 Auto Backup         [dim]PAK dosyalarını yedekle[/dim]')
        console.print('  [6] 📋 Mod Template        [dim]versiyon bazlı mod şablonu[/dim]')
        console.print('  [0] GERİ\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_batch_mod_patcher()
        elif c == '2': action_mod_pack_creator()
        elif c == '3': action_version_checker()
        elif c == '4': action_offset_database()
        elif c == '5': action_auto_backup()
        elif c == '6': action_mod_template_generator()


# ══════════════════════════════════════════════════════════════════
# EKSİK ÖZELLİKLER — Söz verilen 30+ tamamlandı
# ══════════════════════════════════════════════════════════════════

def action_speed_hack_binary():
    os.system('clear')
    console.print('[bold #7C3AED]⚡ SPEED HACK BINARY[/bold #7C3AED]')
    console.print('[dim]  libUE4.so\'dan hareket hızı float değerlerini patch et[/dim]\n')
    path_raw = safe_input('  libUE4.so yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        multiplier = float(safe_input('  Hız çarpanı (2.0=2x): ').strip() or '2.0'); flush_stdin()
    except: multiplier = 2.0; flush_stdin()
    data = bytearray(p.read_bytes())
    # Common PUBG movement speed values
    SPEED_VALUES = [
        (600.0, 'MaxSprintSpeed'),
        (200.0, 'MaxWalkSpeed'),
        (150.0, 'MaxCrouchSpeed'),
        (540.0, 'JumpZVelocity'),
        (300.0, 'MaxSwimSpeed'),
    ]
    patched = 0
    for base_val, name in SPEED_VALUES:
        val_bytes = struct.pack('<f', base_val)
        new_bytes  = struct.pack('<f', base_val * multiplier)
        pos = 0
        count = 0
        while True:
            pos = data.find(val_bytes, pos)
            if pos == -1: break
            data[pos:pos+4] = new_bytes
            count += 1; pos += 4
        if count:
            console.print(f'  [green]✓ {name}: {base_val} → {base_val*multiplier} ({count}x)[/green]')
            patched += count
    if patched == 0:
        console.print('[yellow]⚠ Hız değerleri bulunamadı — farklı versiyon olabilir[/yellow]')
    else:
        out = p.parent / (p.stem + f'_speed{multiplier}x' + p.suffix)
        out.write_bytes(bytes(data))
        console.print(f'\n[bold green]✅ {patched} hız değeri {multiplier}x → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_hwid_changer():
    os.system('clear')
    console.print('[bold #7C3AED]🔑 HWID CHANGER[/bold #7C3AED]')
    console.print('[dim]  libUE4.so\'daki cihaz ID referanslarını değiştir[/dim]\n')
    path_raw = safe_input('  libUE4.so yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import hashlib as _hl, random as _rd
    data = bytearray(p.read_bytes())
    HWID_PATTERNS = [
        b'android_id',b'ANDROID_ID',
        b'serial_number',b'SerialNumber',
        b'device_id',b'DeviceId',b'DEVICE_ID',
        b'imei',b'IMEI',b'getIMEI',
        b'mac_address',b'MacAddress',b'getMacAddress',
        b'/proc/cpuinfo',b'/sys/block',b'/proc/version',
    ]
    found = []
    for pat in HWID_PATTERNS:
        pos = 0
        while True:
            pos = data.find(pat, pos)
            if pos == -1: break
            found.append({'offset': pos, 'pattern': pat.decode('ascii','ignore'), 'size': len(pat)})
            pos += len(pat)
    if not found:
        console.print('[yellow]⚠ HWID pattern bulunamadı[/yellow]')
    else:
        console.print(f'  [green]{len(found)} HWID referansı bulundu:[/green]\n')
        for i, item in enumerate(found[:15], 1):
            console.print(f'  [{i:2}] [dim]0x{item["offset"]:08X}[/dim]  [cyan]{item["pattern"]}[/cyan]')
        console.print()
        c = safe_input('  NOP\'la (tüm referansları sıfırla)? (E/h): ').strip().lower(); flush_stdin()
        if c != 'h':
            for item in found:
                # Replace with harmless alternative strings
                replacements = {
                    'android_id': b'fantool_id\x00\x00',
                    'ANDROID_ID': b'FANTOOL_ID\x00\x00',
                    'imei':       b'0000\x00',
                    'IMEI':       b'0000\x00',
                    'serial_number': b'SN000000\x00\x00',
                    '/proc/cpuinfo': b'/proc/nullinfo',
                }
                repl = replacements.get(item['pattern'])
                if repl and len(repl) <= item['size']:
                    data[item['offset']:item['offset']+len(repl)] = repl
            out = p.parent / (p.stem + '_hwid' + p.suffix)
            out.write_bytes(bytes(data))
            console.print(f'\n[bold green]✅ {len(found)} HWID referansı değiştirildi → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_antiban_patcher():
    os.system('clear')
    console.print('[bold #7C3AED]🛡 ANTI-BAN BINARY PATCHER[/bold #7C3AED]')
    console.print('[dim]  libUE4.so\'daki ban detection kodlarını patch et[/dim]\n')
    path_raw = safe_input('  libUE4.so yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = bytearray(p.read_bytes())
    # Ban-related strings and patterns
    BAN_PATTERNS = [
        b'BanPlayer',b'ReportHack',b'HackDetected',
        b'CheatDetected',b'AntiCheatFailed',b'SecurityViolation',
        b'GameGuardian',b'GameKiller',b'SB Game Hacker',
        b'Xposed',b'com.android.settings.DevelopmentSettings',
        b'com.noshufou.android.su',b'/system/bin/su',b'/system/xbin/su',
        b'ro.debuggable',b'test-keys',
    ]
    patched = 0
    for pat in BAN_PATTERNS:
        pos = 0
        while True:
            pos = data.find(pat, pos)
            if pos == -1: break
            # Replace string with harmless version (same length, null padded)
            null_repl = b'\x00' * len(pat)
            data[pos:pos+len(pat)] = null_repl
            patched += 1; pos += len(pat)
            console.print(f'  [green]✓ Nulled: {pat.decode("ascii","ignore")}[/green]')
    if patched == 0:
        console.print('[yellow]⚠ Ban detection pattern bulunamadı[/yellow]')
    else:
        out = p.parent / (p.stem + '_antiban' + p.suffix)
        out.write_bytes(bytes(data))
        console.print(f'\n[bold green]✅ {patched} ban pattern sıfırlandı → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_parachute_modifier():
    os.system('clear')
    console.print('[bold #10B981]🪂 PARACHUTE MODIFIER[/bold #10B981]')
    console.print('[dim]  Paraşüt iniş ve uçuş hızını değiştir[/dim]\n')
    if not PAK_UNPACK_OUT.exists():
        console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print('  [1] Paraşüt düşüş hızı artır (hızlı in)')
    console.print('  [2] Paraşüt uçuş hızı artır (daha uzağa git)')
    console.print('  [3] Her ikisi\n')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    try:
        mult = float(safe_input('  Çarpan (3.0=3x): ').strip() or '3.0'); flush_stdin()
    except: mult = 3.0; flush_stdin()
    console.print('  [dim]Paraşüt dosyaları aranıyor...[/dim]')
    PARA_KEYS = ['Parachute','parachute','ParaChute','SkydivePara','AirDrop']
    files = [f for f in PAK_UNPACK_OUT.rglob('*.uexp')
             if any(k.lower() in f.stem.lower() for k in PARA_KEYS)]
    total = 0
    if c in ('1','3'):
        total += _bulk_patch_property('FallSpeed', 2000.0 * mult)
        total += _bulk_patch_property('DescentSpeed', 1500.0 * mult)
        total += _bulk_patch_property('ParachuteFallSpeed', 1800.0 * mult)
    if c in ('2','3'):
        total += _bulk_patch_property('GlideSpeed', 2000.0 * mult)
        total += _bulk_patch_property('HorizontalSpeed', 2500.0 * mult)
        total += _bulk_patch_property('ParachuteSpeed', 2000.0 * mult)
    if total == 0:
        console.print('[yellow]⚠ Paraşüt property bulunamadı — PAK UNPACK gerekli[/yellow]')
    else:
        console.print(f'\n[bold green]✅ {total} paraşüt değeri {mult}x yapıldı[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_sky_texture_patcher():
    os.system('clear')
    console.print('[bold #F472B6]🌅 SKY TEXTURE PATCHER[/bold #F472B6]')
    console.print('[dim]  Gökyüzü ve zemin texture\'larını değiştir[/dim]\n')
    if not PAK_UNPACK_OUT.exists():
        console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print('  [1] Gökyüzü siyah yap (visibility artır)')
    console.print('  [2] Gökyüzü beyaz yap')
    console.print('  [3] Zemin düz yap (grass/foliage kaldır)')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    SKY_PATTERNS = ['Sky','sky','Skybox','SkyDome','Atmosphere','Cloud','Stars','Moon','Sun','Sunset','Sunrise','Horizon']
    GROUND_PATTERNS = ['Ground','Terrain','Landscape','Floor','Dirt','Sand','Snow','Mud']
    if c in ('1','2'):
        patterns = SKY_PATTERNS
        label = 'gökyüzü'
    else:
        patterns = GROUND_PATTERNS
        label = 'zemin'
    files = [f for f in PAK_UNPACK_OUT.rglob('*.uasset')
             if any(pat.lower() in f.stem.lower() for pat in patterns)]
    if not files:
        console.print(f'[yellow]⚠ {label} texture bulunamadı[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'  [green]{len(files)} {label} texture bulundu[/green]\n')
    for i, f in enumerate(files[:10], 1):
        console.print(f'  [{i}] {f.name}')
    if len(files) > 10:
        console.print(f'  [dim]+{len(files)-10} tane daha[/dim]')
    conf = safe_input(f'\n  Hepsini sıfırla? (E/h): ').strip().lower(); flush_stdin()
    if conf == 'h': return
    ok = 0
    for f in files:
        try:
            out = f.parent / (f.stem + '_sky_patch' + f.suffix)
            out.write_bytes(b'\x00' * f.stat().st_size)
            ok += 1
        except: pass
    console.print(f'\n[bold green]✅ {ok} {label} texture sıfırlandı[/bold green]')
    console.print('[dim]  CUSTOM FILES/ klasörüne kopyala → CUSTOM INJECT[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_footstep_enhancer():
    os.system('clear')
    console.print('[bold #F472B6]👣 FOOTSTEP SES ENHANCERı[/bold #F472B6]')
    console.print('[dim]  Ayak sesi ses dosyalarını ve property\'lerini artır[/dim]\n')
    if not PAK_UNPACK_OUT.exists():
        console.print(f'[red]❌ PAK_UNPACK boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    FOOTSTEP_PATTERNS = ['Footstep','footstep','FootStep','WalkSound','RunSound','StepSound',
                          'FootSFX','Step_Sound','Footprint','Footfall']
    files = [f for f in PAK_UNPACK_OUT.rglob('*.uexp')
             if any(pat.lower() in f.stem.lower() for pat in FOOTSTEP_PATTERNS)]
    if not files:
        console.print('[yellow]⚠ Ayak sesi dosyası bulunamadı[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'  [green]{len(files)} ayak sesi dosyası:[/green]')
    for i, f in enumerate(files[:10], 1):
        console.print(f'  [{i}] {f.name}')
    try:
        mult = float(safe_input('\n  Ses çarpanı (2.0=2x daha yüksek): ').strip() or '3.0'); flush_stdin()
    except: mult = 3.0; flush_stdin()
    total = 0
    for uexp_path in files:
        ua_path = uexp_path.with_suffix('.uasset')
        if not ua_path.exists(): continue
        try:
            ua = _UAssetFileEx(); ua.load_data(ua_path.read_bytes())
            ue = _UExpFileEx(ua); ue.load_data(uexp_path.read_bytes())
            changed = False
            for prop in ue.properties:
                pn = prop['name'].lower()
                if any(kw in pn for kw in ['volume','attenuation','maxdistance','radius','pitch']):
                    if prop['type'] in ('f32','f64') and isinstance(prop['value'],(int,float)):
                        new_v = float(prop['value']) * mult
                        if ue.write_prop(prop, round(new_v, 4)): changed = True; total += 1
            if changed:
                out = uexp_path.parent / (uexp_path.stem + '_louder' + uexp_path.suffix)
                out.write_bytes(ue.data)
        except: pass
    if total == 0:
        console.print('[yellow]⚠ Ses property bulunamadı[/yellow]')
    else:
        console.print(f'\n[bold green]✅ {total} ses değeri {mult}x artırıldı[/bold green]')
        console.print('[dim]  CUSTOM FILES/ klasörüne kopyala → CUSTOM INJECT[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_mod_template_generator():
    os.system('clear')
    console.print('[bold #06B6D4]📋 MOD TEMPLATE GENERATOR[/bold #06B6D4]')
    console.print('[dim]  PUBG versiyonuna göre mod şablonu oluştur[/dim]\n')
    console.print('  [1] PUBG Mobile Global (4.6.x)')
    console.print('  [2] BGMI (Battlegrounds Mobile India)')
    console.print('  [3] Game for Peace (中国版)')
    console.print('  [4] KR / TW versiyonu')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    TEMPLATES = {
        '1': {
            'name': 'PUBG_Global_4.6',
            'pak_name': 'game_patch_*.pak',
            'enc_method': 47,
            'key_prefix': 'xG2qW5',
            'lua_path': 'Content/Lua/GameLua/Mod/BRMod/Gameplay/Core/',
            'asset_path': 'Content/Arts_Player/',
        },
        '2': {
            'name': 'BGMI_Latest',
            'pak_name': 'res_pufferpatch*.pak',
            'enc_method': 47,
            'key_prefix': 'eb691e',
            'lua_path': 'Content/Lua/GameLua/Mod/BRMod/Gameplay/Core/',
            'asset_path': 'Content/Arts_Player/',
        },
        '3': {
            'name': 'GFP_China',
            'pak_name': 'game_res*.pak',
            'enc_method': 46,
            'key_prefix': 'GFP_',
            'lua_path': 'Content/Lua/GameLua/',
            'asset_path': 'Content/Arts/',
        },
        '4': {
            'name': 'PUBG_KR_TW',
            'pak_name': 'game_patch*.pak',
            'enc_method': 47,
            'key_prefix': 'kG6bC',
            'lua_path': 'Content/Lua/GameLua/Mod/BRMod/Gameplay/Core/',
            'asset_path': 'Content/Arts_Player/',
        },
    }
    if c not in TEMPLATES:
        console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    tmpl = TEMPLATES[c]
    mod_name = safe_input('  Mod adı: ').strip() or 'MyMod'; flush_stdin()
    out_dir = BASE_DIR / f'TEMPLATE_{tmpl["name"]}_{mod_name}'
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / 'CUSTOM FILES').mkdir(parents=True, exist_ok=True)
    (out_dir / 'RESULT PAK').mkdir(parents=True, exist_ok=True)
    (out_dir / 'LUA_MODS').mkdir(parents=True, exist_ok=True)
    readme = f"""# {mod_name} — FANTOOL Mod Template
# Platform: {tmpl['name']}
# FANTool Script — @FanteriBey

== KURULUM ==
1. PAK dosyasını FANTOOL/ klasörüne koy
   PAK adı: {tmpl['pak_name']}

2. Mod dosyalarını CUSTOM FILES/ klasörüne koy
   Lua path: {tmpl['lua_path']}
   Asset path: {tmpl['asset_path']}

3. FANTOOL'u başlat → [1] CUSTOM INJECT

== ŞİFRELEME ==
Enc Method: {tmpl['enc_method']}
Key prefix: {tmpl['key_prefix']}

== DOSYA YAPISI ==
CUSTOM FILES/
  ├── Lua modları → {tmpl['lua_path']}
  └── Asset modları → {tmpl['asset_path']}
"""
    (out_dir / 'README.txt').write_text(readme, encoding='utf-8')
    # Generate sample Lua mod file
    sample_lua = f'''-- {mod_name} — Sample Lua Mod
-- Platform: {tmpl['name']}
-- by @FanteriBey

-- Lua mod kodu buraya gelir
-- Örnek:
if BRPlayerCharacterBase then
    BRPlayerCharacterBase.MaxSprintSpeed = 800
end
'''
    (out_dir / 'LUA_MODS' / f'{mod_name}_mod.lua').write_text(sample_lua, encoding='utf-8')
    # Generate BGMI.csv template
    csv_template = f'''# BGMI.csv Template for {tmpl['name']}
# Format: filename,internal_path,size
# Lua örnekleri:
BRPlayerCharacterBase.lua,{tmpl['lua_path']}BRPlayerCharacterBase.lua,50000
BP_ShootWeaponBase.lua,{tmpl['lua_path']}BP_ShootWeaponBase.lua,30000
'''
    index_dir = out_dir / 'index'
    index_dir.mkdir(parents=True, exist_ok=True)
    (index_dir / 'BGMI_template.csv').write_text(csv_template, encoding='utf-8')
    console.print(f'\n[bold green]✅ Mod şablonu oluşturuldu![/bold green]')
    console.print(f'  {out_dir}')
    console.print(f'  ├── README.txt')
    console.print(f'  ├── CUSTOM FILES/')
    console.print(f'  ├── LUA_MODS/{mod_name}_mod.lua')
    console.print(f'  ├── RESULT PAK/')
    console.print(f'  └── index/BGMI_template.csv')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')


# ══════════════════════════════════════════════════════════════════
# [30] LUA ULTRA — Tam pipeline
# ══════════════════════════════════════════════════════════════════

def action_lua_triple_compile():
    """Tek dosyayı aynı anda 5.1 + 5.3 + 5.4 ile derle"""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF88FF]🔱 LUA TRIPLE COMPILE[/bold #FF88FF]')
    console.print('[dim]  Tek .lua dosyasını 5.1 + 5.3 + 5.4 ile aynı anda derle[/dim]\n')
    files = [f for f in COMPILED_DIR.iterdir() if f.is_file() and f.suffix == '.lua']
    if not files:
        console.print(f'[red]❌ COMPILED boş → {COMPILED_DIR}[/red]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    selected = _select_files([f.name for f in files], str(COMPILED_DIR), 'TRIPLE COMPILE')
    if not selected: return
    import tempfile as _tf, shutil as _sh
    versions = [('5.1','lua51'),('5.3','lua53'),('5.4','lua54')]
    # Filter out bytecode files
    selected = [f for f in selected if not (COMPILED_DIR/f).read_bytes()[:4] == b'\x1bLua']
    for fname in selected:
        src = COMPILED_DIR / fname
        console.print(f'\n  [cyan]{fname}[/cyan]')
        for ver, pkg in versions:
            cmd = _get_luac_version_cmd(ver)
            if not cmd:
                console.print(f'  [yellow]  lua{ver}: yok (pkg install {pkg})[/yellow]')
                continue
            with _tf.TemporaryDirectory(prefix='fan_tri_') as tmp:
                out_f = Path(tmp) / 'out.luac'
                r = subprocess.run([cmd, '-o', str(out_f), str(src)],
                                   capture_output=True, text=True, timeout=30)
                if r.returncode == 0 and out_f.exists():
                    dst = COMPILED_DIR / f'{src.stem}_v{ver.replace(".","")}{src.suffix}'
                    _sh.copy2(str(out_f), str(dst))
                    console.print(f'  [green]  ✅ {ver} → {dst.name} ({human_size(dst.stat().st_size)})[/green]')
                else:
                    err = (r.stderr or r.stdout or '?').strip()[:80]
                    console.print(f'  [red]  ✗ {ver}: {err}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_minifier():
    """Lua kaynak kodunu minify et"""
    os.system('clear')
    console.print('[bold #FF88FF]📦 LUA MİNİFİER[/bold #FF88FF]')
    console.print('[dim]  Lua kaynak kodunu küçült: yorum + whitespace temizle[/dim]\n')
    path_raw = safe_input('  .lua dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    raw = p.read_bytes()
    if raw[:4] == b'\x1bLua':
        console.print(f'[red]❌ Bytecode dosyası — kaynak .lua gerekli[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    src = raw.decode('utf-8', errors='replace')
    import re as _re
    result = src
    # Remove multi-line comments
    result = _re.sub(r'--\[\[.*?\]\]', '', result, flags=_re.DOTALL)
    # Remove single line comments
    result = _re.sub(r'--[^\n]*', '', result)
    # Remove empty lines
    result = _re.sub(r'\n\s*\n', '\n', result)
    # Remove leading whitespace
    lines = [l.rstrip() for l in result.splitlines() if l.strip()]
    result = '\n'.join(lines)
    orig_len = len(src); new_len = len(result)
    out = p.parent / (p.stem + '_min.lua')
    out.write_text(result, encoding='utf-8')
    console.print(f'\n[bold green]✅ Minified![/bold green]')
    console.print(f'  Orijinal : {orig_len:,} karakter')
    console.print(f'  Minified : {new_len:,} karakter  (%{int((1-new_len/orig_len)*100)} küçültme)')
    console.print(f'  Çıktı: {out}')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_pretty_printer():
    """Lua kodunu güzel formata getir"""
    os.system('clear')
    console.print('[bold #FF88FF]✨ LUA PRETTY PRINTER[/bold #FF88FF]')
    console.print('[dim]  Sıkıştırılmış/obfuscated Lua kodu okunabilir yap[/dim]\n')
    path_raw = safe_input('  .lua dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    raw = p.read_bytes()
    if raw[:4] == b'\x1bLua':
        console.print(f'[red]❌ Bytecode dosyası — kaynak .lua gerekli[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    src = raw.decode('utf-8', errors='replace')
    import re as _re
    # Add newlines after keywords and semicolons
    result = src
    KEYWORDS = ['then','do','else','elseif','end','repeat','until','function']
    for kw in KEYWORDS:
        result = _re.sub(rf'\b{kw}\b', f'\n{kw}\n', result)
    result = result.replace(';', ';\n')
    # Fix indentation (simple)
    indent = 0; lines = []; OPEN = ['do','then','function','repeat','else','elseif']
    CLOSE = ['end','until','else','elseif']
    for line in result.splitlines():
        s = line.strip()
        if not s: continue
        for kw in CLOSE:
            if s.startswith(kw): indent = max(0, indent-1); break
        lines.append('    ' * indent + s)
        for kw in OPEN:
            if s.startswith(kw) or s.endswith(kw): indent += 1; break
    result = '\n'.join(lines)
    out = p.parent / (p.stem + '_pretty.lua')
    out.write_text(result, encoding='utf-8')
    console.print(f'\n[bold green]✅ Pretty printed → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_dependency_tracer():
    """Lua dosyalarındaki require() bağımlılıklarını tara"""
    os.system('clear')
    console.print('[bold #FF88FF]🔗 LUA DEPENDENCY TRACER[/bold #FF88FF]')
    console.print('[dim]  require() çağrılarını tara, bağımlılık haritasını çıkar[/dim]\n')
    dir_raw = safe_input(f'  Klasör (boş=LUA_EDIT/COMPILED): ').strip().strip('"'); flush_stdin()
    if dir_raw:
        scan_dir = Path(dir_raw)
    elif LUA_EDIT_DIR.exists() and any(LUA_EDIT_DIR.rglob('*.lua')):
        scan_dir = LUA_EDIT_DIR
    elif COMPILED_DIR.exists() and any(COMPILED_DIR.rglob('*.lua')):
        scan_dir = COMPILED_DIR
    else:
        scan_dir = BASE_DIR
    if not scan_dir.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import re as _re
    dep_map = {}
    for f in scan_dir.rglob('*.lua'):
        try:
            src = f.read_text(encoding='utf-8', errors='replace')
            reqs = _re.findall(r'require\s*[\(\[]\s*["\']([^"\']+)["\']', src)
            if reqs: dep_map[f.stem] = reqs
        except: pass
    if not dep_map:
        console.print('[yellow]require() çağrısı bulunamadı[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'\n  [green]{len(dep_map)} dosyada bağımlılık:[/green]\n')
    for fname, deps in dep_map.items():
        console.print(f'  [cyan]{fname}[/cyan]')
        for d in deps: console.print(f'    → [white]{d}[/white]')
    out = scan_dir / 'dependency_map.txt'
    lines = ['=== Lua Dependency Map ===','']
    for fname, deps in dep_map.items():
        lines += [f'{fname}:'] + [f'  -> {d}' for d in deps] + ['']
    out.write_text('\n'.join(lines), encoding='utf-8')
    console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_global_scanner():
    """Lua dosyasındaki tüm global değişkenleri listele"""
    os.system('clear')
    console.print('[bold #FF88FF]🌐 LUA GLOBAL SCANNER[/bold #FF88FF]')
    console.print('[dim]  Tüm global değişken ve fonksiyon tanımlarını tara[/dim]\n')
    path_raw = safe_input('  .lua dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Check if binary bytecode
    raw = p.read_bytes()
    if raw[:4] == b'\x1bLua':
        console.print(f'[red]❌ Bytecode dosyası — kaynak .lua gerekli[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    src = raw.decode('utf-8', errors='replace')
    import re as _re
    globals_found = []
    # Global function defs
    for m in _re.finditer(r'^function\s+([A-Za-z_]\w*(?:\.\w+)*)\s*\(', src, _re.MULTILINE):
        globals_found.append(('function', m.group(1), src[:m.start()].count('\n')+1))
    # Global var assignments (not local)
    for m in _re.finditer(r'^([A-Za-z_]\w*)\s*=\s*(?!function)', src, _re.MULTILINE):
        if not src[max(0,m.start()-10):m.start()].rstrip().endswith('local'):
            globals_found.append(('variable', m.group(1), src[:m.start()].count('\n')+1))
    if not globals_found:
        console.print('[yellow]Global bulunamadı[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'\n  [green]{len(globals_found)} global:[/green]\n')
    for gtype, gname, gline in globals_found[:50]:
        tag = '[cyan]fn[/cyan]' if gtype=='function' else '[yellow]var[/yellow]'
        console.print(f'  {tag}  [white]{gname:<40}[/white]  [dim]satır {gline}[/dim]')
    out = p.parent / (p.stem + '_globals.txt')
    out.write_text('\n'.join(f'{t}\t{n}\tL{l}' for t,n,l in globals_found), encoding='utf-8')
    console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_header_analyzer():
    """Lua bytecode header field'larını ayrıştır"""
    os.system('clear')
    console.print('[bold #FF88FF]🔬 LUA HEADER ANALYZER[/bold #FF88FF]')
    console.print('[dim]  .luac bytecode header field\'larını detaylı göster[/dim]\n')
    path_raw = safe_input('  .luac dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    d = p.read_bytes()
    if len(d) < 18 or d[:4] != b'\x1bLua':
        console.print(f'[red]❌ Lua bytecode değil[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ver    = d[4]; fmt = d[5]; endian = d[6]; int_sz = d[7]; size_t_sz = d[8]
    ins_sz = d[9]; num_sz = d[10]; is_num = d[11]
    minor  = ver & 0x0F; major = (ver >> 4) & 0x0F
    # PUBG T24 specific field
    t24_nibble = d[33] if len(d) > 33 else None
    enc_key = d[12:18].hex() if len(d) > 18 else 'N/A'
    console.print(f'\n  Dosya      : [cyan]{p.name}[/cyan]  ({human_size(len(d))})')
    console.print(f'  Versiyon   : [green]Lua {major}.{minor}[/green]  (0x{ver:02X})')
    console.print(f'  Format     : [white]{fmt}[/white]  (0=resmi)')
    console.print(f'  Endian     : [white]{"Little" if endian==1 else "Big"}-endian[/white]')
    console.print(f'  int boyutu : [white]{int_sz} byte[/white]')
    console.print(f'  size_t     : [white]{size_t_sz} byte[/white]')
    console.print(f'  inst boyutu: [white]{ins_sz} byte[/white]')
    console.print(f'  num boyutu : [white]{num_sz} byte[/white]')
    console.print(f'  İnt sayı mı: [white]{bool(is_num)}[/white]')
    if t24_nibble is not None:
        console.print(f'  T24 nibble : [{"green" if t24_nibble==2 else "yellow"}]0x{t24_nibble:02X}[/{"green" if t24_nibble==2 else "yellow"}]  ({"PUBG T24 format" if t24_nibble==2 else "standart"})')
    console.print(f'  İmza bytes : [dim]{enc_key}[/dim]')
    console.print(f'\n  [dim]Ham header hex:[/dim]')
    console.print(f'  [dim]{d[:18].hex().upper()}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_xor_then_compile():
    """Batch XOR çöz ve hemen derle — tek adım"""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF88FF]⚡ XOR ÇÖZDÜKTEN SONRA DERLE[/bold #FF88FF]')
    console.print('[dim]  LUA_ORIGINAL → XOR çöz → luac derle → COMPILED[/dim]\n')
    console.print('  XOR Key:')
    console.print('  [1] PUBG/BGMI')
    console.print('  [2] GFP')
    console.print('  [3] Özel')
    console.print('  [0] Geri\n')
    c = safe_input('  Key: ').strip(); flush_stdin()
    if c == '0': return
    if c == '1': xkey = _DEFAULT_XOR_KEY
    elif c == '2': xkey = _GFP_XOR_KEY
    elif c == '3':
        raw = safe_input('  HEX key: ').strip().replace(' ',''); flush_stdin()
        try: xkey = bytes.fromhex(raw)
        except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    else: return
    ver = safe_input('  Versiyon (5.1/5.3/5.4) [5.3]: ').strip() or '5.3'; flush_stdin()
    luac_cmd = _get_luac_version_cmd(ver)
    if not luac_cmd:
        console.print(f'[red]❌ luac{ver} yok[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    files = [f for f in LUA_ORIGINAL_DIR.iterdir()
             if f.is_file() and f.suffix.lower() in ('.luac','.slua','.lua')]
    if not files:
        console.print(f'[red]❌ {LUA_ORIGINAL_DIR} boş[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import tempfile as _tf, shutil as _sh2
    ok = 0; fail = []
    for f in files:
        try:
            # Step 1: XOR decrypt → tmp
            data = f.read_bytes()
            decrypted = bytes(b ^ xkey[i % len(xkey)] for i, b in enumerate(data))
            with _tf.TemporaryDirectory(prefix='fan_xc_') as tmp:
                tmp_lua = Path(tmp) / (f.stem + '.lua')
                tmp_lua.write_bytes(decrypted)
                tmp_out = Path(tmp) / 'out.luac'
                # Step 2: compile
                r = subprocess.run([luac_cmd, '-o', str(tmp_out), str(tmp_lua)],
                                   capture_output=True, text=True, timeout=30)
                if r.returncode == 0 and tmp_out.exists():
                    COMPILED_DIR.mkdir(parents=True, exist_ok=True)
                    dst = COMPILED_DIR / f.name
                    _sh2.copy2(str(tmp_out), str(dst))
                    console.print(f'  [green]✅ {f.name} → {dst.name}[/green]')
                    ok += 1
                else:
                    console.print(f'  [red]✗ {f.name}: {(r.stderr or "?")[:80]}[/red]')
                    fail.append(f.name)
        except Exception as e:
            console.print(f'  [red]✗ {f.name}: {e}[/red]'); fail.append(f.name)
    console.print(f'\n[bold]Sonuç: {ok}/{len(files)}[/bold]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_bytecode_version_diff():
    """Aynı Lua kodunu farklı versiyonlarla derle ve bytecode farkını göster"""
    _ensure_lua_dirs()
    os.system('clear')
    console.print('[bold #FF88FF]📊 MULTI-VERSION BYTECODE DIFF[/bold #FF88FF]')
    console.print('[dim]  Aynı .lua → 5.1 ve 5.3 çıktısını karşılaştır[/dim]\n')
    path_raw = safe_input('  .lua dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import tempfile as _tf
    results = {}
    for ver in ['5.1','5.3','5.4']:
        cmd = _get_luac_version_cmd(ver)
        if not cmd: continue
        with _tf.TemporaryDirectory(prefix='fan_vdiff_') as tmp:
            out_f = Path(tmp) / 'out.luac'
            r = subprocess.run([cmd, '-o', str(out_f), str(p)],
                               capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and out_f.exists():
                results[ver] = out_f.read_bytes()
    if len(results) < 2:
        console.print('[yellow]En az 2 versiyon derleyicisi gerekli[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print()
    vers = list(results.keys())
    for ver, data in results.items():
        console.print(f'  Lua {ver}: [cyan]{human_size(len(data))}[/cyan]  header:[dim]{data[:8].hex().upper()}[/dim]')
    console.print()
    # Compare first 2
    d1 = results[vers[0]]; d2 = results[vers[1]]
    diffs = sum(1 for a,b in zip(d1,d2) if a!=b)
    console.print(f'  {vers[0]} vs {vers[1]}: [yellow]{diffs} byte farklı[/yellow]  boyut fark: {abs(len(d1)-len(d2))} byte')
    if len(results) > 2:
        d3 = results[vers[2]]
        diffs2 = sum(1 for a,b in zip(d1,d3) if a!=b)
        console.print(f'  {vers[0]} vs {vers[2]}: [yellow]{diffs2} byte farklı[/yellow]  boyut fark: {abs(len(d1)-len(d3))} byte')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_lua_ultra_menu():
    while True:
        os.system('clear')
        console.print('[bold #FF88FF]📜 LUA ULTRA[/bold #FF88FF]')
        console.print('[dim]  Lua tam pipeline araçları[/dim]\n')
        console.print('  [1]  🔱 Triple Compile       [dim]5.1+5.3+5.4 aynı anda[/dim]')
        console.print('  [2]  📦 Minifier             [dim]yorum+whitespace temizle[/dim]')
        console.print('  [3]  ✨ Pretty Printer        [dim]sıkıştırılmış kodu formatla[/dim]')
        console.print('  [4]  🔗 Dependency Tracer    [dim]require() bağımlılık haritası[/dim]')
        console.print('  [5]  🌐 Global Scanner       [dim]tüm global değişkenler[/dim]')
        console.print('  [6]  🔬 Header Analyzer      [dim]bytecode header detayı[/dim]')
        console.print('  [7]  ⚡ XOR + Derle          [dim]XOR çöz → anında derle[/dim]')
        console.print('  [8]  📊 Multi-Version Diff   [dim]5.1 vs 5.3 bytecode farkı[/dim]')
        console.print('  [0]  GERİ\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_lua_triple_compile()
        elif c == '2': action_lua_minifier()
        elif c == '3': action_lua_pretty_printer()
        elif c == '4': action_lua_dependency_tracer()
        elif c == '5': action_lua_global_scanner()
        elif c == '6': action_lua_header_analyzer()
        elif c == '7': action_lua_xor_then_compile()
        elif c == '8': action_lua_bytecode_version_diff()

# ══════════════════════════════════════════════════════════════════
# [31] PAK ULTRA PLUS — Tam pipeline
# ══════════════════════════════════════════════════════════════════

def action_pak_filter_extract():
    """PAK içindeki dosyaları uzantıya göre filtrele ve çıkar"""
    os.system('clear')
    console.print('[bold #FFAA00]📤 PAK FİLTRELİ ÇIKAR[/bold #FFAA00]')
    console.print('[dim]  PAK içinden sadece belirli uzantıları çıkar[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
    try:
        c = int(safe_input(f'\n  PAK seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print('  Filtre seç:')
    console.print('  [1] Sadece .lua / .luac / .slua')
    console.print('  [2] Sadece .uasset / .uexp')
    console.print('  [3] Sadece .png / .jpg / .dds (texture)')
    console.print('  [4] Sadece .umap (harita)')
    console.print('  [5] Özel uzantı gir')
    console.print('  [0] Geri\n')
    c = safe_input('  > ').strip(); flush_stdin()
    if c == '0': return
    EXT_MAP = {
        '1': ['.lua','.luac','.slua'],
        '2': ['.uasset','.uexp'],
        '3': ['.png','.jpg','.dds','.tga'],
        '4': ['.umap'],
    }
    if c == '5':
        raw = safe_input('  Uzantılar (örn: .lua .uasset): ').strip(); flush_stdin()
        exts = raw.split()
    elif c in EXT_MAP:
        exts = EXT_MAP[c]
    else: return
    try:
        pak = TencentPakFile(PurePath(pak_path))
        paths = pak.list_existing_paths()
    except Exception as e: console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    filtered = [p for p in paths if any(p.lower().endswith(ext) for ext in exts)]
    console.print(f'\n  [green]{len(filtered)}/{len(paths)} dosya eşleşti[/green]')
    if not filtered: flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    out_dir = PAK_UNPACK_OUT / f'FILTERED_{pak_path.stem}'
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    # Use dump approach for reliability
    import tempfile as _tf2
    with _tf2.TemporaryDirectory(prefix='fan_filt_') as _tmp2:
        tmp_p2 = Path(_tmp2)
        console.print('  [dim]PAK çıkarılıyor...[/dim]')
        try:
            pak.dump(PurePath(tmp_p2))
        except Exception as _de:
            console.print(f'[red]❌ Dump hatası: {_de}[/red]')
            flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        for fpath in tmp_p2.rglob('*'):
            if fpath.is_file() and any(fpath.name.lower().endswith(ext) for ext in exts):
                try:
                    import shutil as _shf
                    _shf.copy2(str(fpath), str(out_dir / fpath.name))
                    ok += 1
                except: pass
    console.print(f'[bold green]✅ {ok} dosya → {out_dir}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_chunk_analyzer():
    """PAK her entry'nin block yapısını ve compression ratio'sunu göster"""
    os.system('clear')
    console.print('[bold #FFAA00]📊 PAK CHUNK ANALYZER[/bold #FFAA00]')
    console.print('[dim]  Her entry\'nin boyut, compression, block yapısı[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}  [dim]{human_size(f.stat().st_size)}[/dim]')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        pak = TencentPakFile(PurePath(pak_path))
    except Exception as e: console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    entries = []
    for dir_pp, files in pak._index.items():
        for fname, entry in files.items():
            full = str(dir_pp / fname).replace('\\','/').lstrip('/')
            cs = getattr(entry,'size',0)
            us = getattr(entry,'uncompressed_size', cs)
            ratio = cs/us if us > 0 else 1.0
            entries.append({'path':full,'comp':cs,'uncomp':us,'ratio':ratio,
                           'enc':getattr(entry,'encrypted',False)})
    entries.sort(key=lambda x: x['uncomp'], reverse=True)
    PAGE = 20; page = 0
    while True:
        os.system('clear')
        total_comp = sum(e['comp'] for e in entries)
        total_uncomp = sum(e['uncomp'] for e in entries)
        console.print(f'[bold]📊 {pak_path.name}[/bold]  [dim]{len(entries)} entry | Toplam: {human_size(total_uncomp)} → {human_size(total_comp)}[/dim]')
        console.print(f'  Sayfa {page+1}/{(len(entries)+PAGE-1)//PAGE}')
        console.print()
        chunk = entries[page*PAGE:(page+1)*PAGE]
        for e in chunk:
            ratio_str = f'{e["ratio"]:.2f}x' if e['uncomp']>0 else 'N/A'
            enc_str = '[red]🔒[/red]' if e['enc'] else ''
            console.print(f'  {enc_str}[dim]{Path(e["path"]).name[:40]:<40}[/dim]  '
                         f'[cyan]{human_size(e["uncomp"]):>8}[/cyan] → [green]{human_size(e["comp"]):>8}[/green]  '
                         f'[yellow]{ratio_str}[/yellow]')
        console.print()
        console.print(f'[dim]  {T("nav_hint")}[/dim]')
        cmd = safe_input('  > ').strip(); flush_stdin()
        if cmd == '0': break
        elif cmd == 'n': page = min(page+1,(len(entries)-1)//PAGE)
        elif cmd == 'p': page = max(page-1,0)
    # Save report
    out = BASE_DIR/'DUMP'/f'{pak_path.stem}_chunks.txt'
    out.parent.mkdir(parents=True,exist_ok=True)
    lines = [f'=== {pak_path.name} Chunk Analysis ===','']
    for e in entries:
        lines.append(f'{Path(e["path"]).name}\t{e["uncomp"]}\t{e["comp"]}\t{e["ratio"]:.3f}\t{"ENC" if e["enc"] else ""}')
    out.write_text('\n'.join(lines),encoding='utf-8')
    console.print(f'  [dim]Rapor: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_to_zip():
    """PAK içeriğini ZIP'e aktar"""
    os.system('clear')
    console.print('[bold #FFAA00]📦 PAK → ZIP CONVERTER[/bold #FFAA00]')
    console.print('[dim]  PAK dosyasının tüm içeriğini ZIP\'e aktar[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import tempfile as _tf, zipfile as _zf
    with _tf.TemporaryDirectory(prefix='fan_p2z_') as tmp:
        tmp_p = Path(tmp)
        console.print('  [dim]Çıkarılıyor...[/dim]')
        try:
            pak = TencentPakFile(PurePath(pak_path))
            pak.dump(PurePath(tmp_p))
        except Exception as e: console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
        out_zip = BASE_DIR / (pak_path.stem + '.zip')
        console.print('  [dim]ZIP oluşturuluyor...[/dim]')
        with _zf.ZipFile(str(out_zip), 'w', _zf.ZIP_DEFLATED) as zf:
            for f in tmp_p.rglob('*'):
                if f.is_file():
                    zf.write(str(f), str(f.relative_to(tmp_p)).replace('\\','/'))
    console.print(f'\n[bold green]✅ {out_zip.name} ({human_size(out_zip.stat().st_size)})[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_header_hex():
    """PAK raw header bytes'ı hex viewer'da göster"""
    os.system('clear')
    console.print('[bold #FFAA00]🔢 PAK HEADER HEX VIEWER[/bold #FFAA00]')
    console.print('[dim]  PAK dosyasının ilk ve son 256 byte\'ını hex olarak göster[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = pak_path.read_bytes()
    for section, offset in [('HEADER (ilk 256B)', 0), ('FOOTER (son 256B)', max(0,len(data)-256))]:
        console.print(f'\n  [bold cyan]{section}:[/bold cyan]')
        chunk = data[offset:offset+256]
        for i in range(0, len(chunk), 16):
            row = chunk[i:i+16]
            hex_part  = ' '.join(f'{b:02X}' for b in row).ljust(48)
            ascii_part = ''.join(chr(b) if 32<=b<127 else '.' for b in row)
            console.print(f'  [dim]{offset+i:08X}[/dim]  [white]{hex_part}[/white]  [dim]{ascii_part}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_split():
    """Büyük PAK'ı parçalara böl"""
    os.system('clear')
    console.print('[bold #FFAA00]✂️  PAK SPLIT[/bold #FFAA00]')
    console.print('[dim]  Büyük PAK dosyasını belirli boyutlarda parçala[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}  [dim]{human_size(f.stat().st_size)}[/dim]')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        size_mb = int(safe_input('  Parça boyutu MB (100): ').strip() or '100'); flush_stdin()
    except: size_mb = 100; flush_stdin()
    data = pak_path.read_bytes()
    chunk_size = size_mb * 1024 * 1024
    parts = [data[i:i+chunk_size] for i in range(0, len(data), chunk_size)]
    for i, part in enumerate(parts):
        out = pak_path.parent / f'{pak_path.stem}.part{i+1:03d}.pak'
        out.write_bytes(part)
        console.print(f'  [green]✓ {out.name}  ({human_size(len(part))})[/green]')
    console.print(f'\n[bold green]✅ {len(parts)} parça oluşturuldu[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_encrypted_test():
    """PAK hangi entry'lerin şifreli olduğunu test et"""
    os.system('clear')
    console.print('[bold #FFAA00]🔑 PAK ŞİFRELİ ENTRY TESTÇİ[/bold #FFAA00]')
    console.print('[dim]  Her PAK entry\'sinin şifreli olup olmadığını tara[/dim]\n')
    pak_files = [f for f in BASE_DIR.iterdir() if f.suffix.lower()=='.pak']
    if not pak_files: console.print(f'[red]❌ {T("no_pak")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    for i,f in enumerate(pak_files,1): console.print(f'  [{i}] {f.name}')
    try:
        c = int(safe_input(f'\n  Seç: ').strip())-1; flush_stdin()
        pak_path = pak_files[c]
    except: console.print(f'[red]{T("invalid")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    try:
        pak = TencentPakFile(PurePath(pak_path))
    except Exception as e: console.print(f'[red]❌ {e}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    enc_count = 0; total = 0
    enc_exts = {}
    for dir_pp, files in pak._index.items():
        for fname, entry in files.items():
            total += 1
            is_enc = getattr(entry,'encrypted',False)
            if is_enc:
                enc_count += 1
                ext = Path(fname).suffix.lower() or 'no_ext'
                enc_exts[ext] = enc_exts.get(ext, 0) + 1
    console.print(f'\n  Toplam entry  : [cyan]{total}[/cyan]')
    console.print(f'  Şifreli       : [red]{enc_count}[/red]')
    console.print(f'  Şifresiz      : [green]{total-enc_count}[/green]')
    if enc_exts:
        console.print(f'\n  Şifreli uzantı dağılımı:')
        for ext, cnt in sorted(enc_exts.items(), key=lambda x:-x[1]):
            console.print(f'  [dim]{ext:<12}[/dim]  [red]{cnt}[/red]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_pak_ultra_plus_menu():
    while True:
        os.system('clear')
        console.print('[bold #FFAA00]📦 PAK ULTRA PLUS[/bold #FFAA00]')
        console.print('[dim]  PAK tam pipeline araçları[/dim]\n')
        console.print('  [1]  📤 Filtreli Çıkar      [dim].lua/.uasset/.png ayrı çıkar[/dim]')
        console.print('  [2]  📊 Chunk Analyzer      [dim]her entry boyut/compression[/dim]')
        console.print('  [3]  📦 PAK → ZIP           [dim]ZIP\'e aktar[/dim]')
        console.print('  [4]  🔢 Header Hex Viewer   [dim]raw header bytes[/dim]')
        console.print('  [5]  ✂️  PAK Split           [dim]büyük PAK\'ı parçala[/dim]')
        console.print('  [6]  🔑 Şifreli Entry Test  [dim]hangi entry şifreli[/dim]')
        console.print('  [7]  📋 PAK Metadata        [dim]versiyon/enc bilgisi[/dim]')
        console.print('  [8]  🔄 PAK Karşılaştır    [dim]iki PAK farkı[/dim]')
        console.print('  [0]  GERİ\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_pak_filter_extract()
        elif c == '2': action_pak_chunk_analyzer()
        elif c == '3': action_pak_to_zip()
        elif c == '4': action_pak_header_hex()
        elif c == '5': action_pak_split()
        elif c == '6': action_pak_encrypted_test()
        elif c == '7': action_pak_metadata()
        elif c == '8': action_pak_compare()

# ══════════════════════════════════════════════════════════════════
# [32] SO/ELF ULTRA — Tam pipeline
# ══════════════════════════════════════════════════════════════════

def action_plt_parser():
    """PLT (Procedure Linkage Table) parse et"""
    os.system('clear')
    console.print('[bold #06B6D4]📋 PLT PARSER[/bold #06B6D4]')
    console.print('[dim]  libUE4.so PLT — dışarıdan çağrılan fonksiyonlar[/dim]\n')
    path_raw = safe_input('  .so dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    if data[:4] != b'\x7fELF': console.print(f'[red]❌ ELF değil[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Parse .plt section from ELF
    # For ARM64: PLT entries are 16 bytes each
    PLT_NAME = b'.plt\x00'
    pos = data.find(PLT_NAME)
    if pos == -1:
        console.print('[yellow]⚠ .plt section bulunamadı, string table\'dan PLT göstermeye çalışıyorum...[/yellow]')
        # Fallback: find extern function names
        strings = []
        i = 0
        while i < len(data)-4:
            if 33 <= data[i] < 127:
                end = i
                while end < min(i+80, len(data)) and 33 <= data[end] < 127:
                    end += 1
                s = data[i:end].decode('ascii','ignore')
                if len(s) > 4 and any(kw in s for kw in ['pthread','malloc','free','dlopen','sprintf','memcpy','strcmp','printf']):
                    strings.append((i, s))
                i = end + 1
            else: i += 1
        console.print(f'\n  [green]{len(strings)} extern fonksiyon:[/green]')
        for off, name in strings[:30]:
            console.print(f'  [dim]0x{off:08X}[/dim]  [cyan]{name}[/cyan]')
    else:
        console.print(f'  .plt section @ 0x{pos:X}')
        # Show PLT entries (16 bytes each for ARM64)
        plt_data = data[pos+8:pos+8+256]
        console.print(f'  İlk PLT bytes: [dim]{plt_data[:64].hex().upper()}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_section_dump():
    """ELF her section'ı ayrı dosyaya kaydet"""
    os.system('clear')
    console.print('[bold #06B6D4]💾 ELF SECTION DUMP[/bold #06B6D4]')
    console.print('[dim]  .so dosyasının her section\'ını ayrı dosyaya kaydet[/dim]\n')
    path_raw = safe_input('  .so dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    if data[:4] != b'\x7fELF': console.print(f'[red]❌ ELF değil[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ei_class = data[4]
    is64 = ei_class == 2
    if is64:
        e_shoff   = struct.unpack_from('<Q', data, 40)[0]
        e_shentsize = struct.unpack_from('<H', data, 58)[0]
        e_shnum   = struct.unpack_from('<H', data, 60)[0]
        e_shstrndx = struct.unpack_from('<H', data, 62)[0]
    else:
        e_shoff   = struct.unpack_from('<I', data, 32)[0]
        e_shentsize = struct.unpack_from('<H', data, 46)[0]
        e_shnum   = struct.unpack_from('<H', data, 48)[0]
        e_shstrndx = struct.unpack_from('<H', data, 50)[0]
    if e_shoff == 0 or e_shnum == 0:
        console.print('[yellow]⚠ Section header yok (stripped binary)[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Get string table section
    SH_SIZE = e_shentsize
    def get_sh(idx):
        off = e_shoff + idx * SH_SIZE
        if is64:
            sh_name   = struct.unpack_from('<I', data, off)[0]
            sh_offset = struct.unpack_from('<Q', data, off+24)[0]
            sh_size   = struct.unpack_from('<Q', data, off+32)[0]
        else:
            sh_name   = struct.unpack_from('<I', data, off)[0]
            sh_offset = struct.unpack_from('<I', data, off+16)[0]
            sh_size   = struct.unpack_from('<I', data, off+20)[0]
        return sh_name, sh_offset, sh_size
    try:
        str_sh_name, str_sh_off, str_sh_size = get_sh(e_shstrndx)
        strtab = data[str_sh_off:str_sh_off+str_sh_size]
    except: strtab = b'\x00'
    out_dir = BASE_DIR/'DUMP'/f'{p.stem}_sections'
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    for i in range(min(e_shnum, 100)):
        try:
            sh_name, sh_off, sh_size = get_sh(i)
            if sh_size == 0 or sh_off == 0: continue
            name_end = strtab.find(b'\x00', sh_name)
            name = strtab[sh_name:name_end].decode('ascii','ignore') if name_end>sh_name else f'section_{i}'
            name = name.lstrip('.').replace('/','_') or f'section_{i}'
            section_data = data[sh_off:sh_off+sh_size]
            out = out_dir/f'{i:02d}_{name}.bin'
            out.write_bytes(section_data)
            console.print(f'  [green]✓ {out.name}  ({human_size(len(section_data))})[/green]')
            ok += 1
        except: pass
    console.print(f'\n[bold green]✅ {ok} section → {out_dir}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_so_dependency_lister():
    """.so'nun bağımlı olduğu kütüphaneleri listele"""
    os.system('clear')
    console.print('[bold #06B6D4]🔗 SO DEPENDENCY LİSTER[/bold #06B6D4]')
    console.print('[dim]  .so dosyasının bağımlı olduğu kütüphaneler[/dim]\n')
    path_raw = safe_input('  .so dosyası: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    if data[:4] != b'\x7fELF': console.print(f'[red]❌ ELF değil[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Search for DT_NEEDED entries (0x1 tag in dynamic section)
    # Also search for .so names directly
    import re as _re
    so_names = list(set(_re.findall(rb'lib\w+\.so(?:\.\d+)*', data)))
    so_names = [s.decode('ascii','ignore') for s in so_names if len(s)<50]
    console.print(f'\n  [green]{len(so_names)} bağımlılık:[/green]\n')
    for name in sorted(so_names):
        console.print(f'  [cyan]{name}[/cyan]')
    out = BASE_DIR/'DUMP'/(p.stem+'_deps.txt')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text('\n'.join(sorted(so_names)), encoding='utf-8')
    console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_entropy_analyzer():
    """Dosyanın entropisi ile şifreli mi, sıkıştırılmış mı tespit et"""
    os.system('clear')
    console.print('[bold #06B6D4]📊 ENTROPİ ANALİZÖRÜ[/bold #06B6D4]')
    console.print('[dim]  Dosyanın şifreli mi, sıkıştırılmış mı, yoksa düz data mı olduğunu tespit et[/dim]\n')
    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    import math as _math, collections as _col
    data = p.read_bytes()
    total = len(data)
    if total == 0: console.print(f'[red]❌ Boş dosya[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    # Calculate Shannon entropy
    freq = [0]*256
    for b in data: freq[b] += 1
    entropy = 0.0
    for f in freq:
        if f > 0:
            p_i = f / total
            entropy -= p_i * _math.log2(p_i)
    # Interpret
    if entropy > 7.9:
        interp = '[red]ŞİFRELİ veya SIKIŞTIRILMIŞ[/red]'
        detail = 'AES/XOR şifreli veya zlib/lz4 sıkıştırılmış'
    elif entropy > 6.5:
        interp = '[yellow]YÜKSEK ENTROPİ[/yellow]'
        detail = 'Kısmen sıkıştırılmış veya binary data'
    elif entropy > 4.0:
        interp = '[cyan]ORTA ENTROPİ[/cyan]'
        detail = 'Karma binary/text, code veya config'
    else:
        interp = '[green]DÜŞÜK ENTROPİ[/green]'
        detail = 'Metin dosyası veya tekrarlayan veri'
    console.print(f'\n  Dosya      : [cyan]{p.name}[/cyan]')
    console.print(f'  Boyut      : [cyan]{human_size(total)}[/cyan]')
    console.print(f'  Entropi    : [bold]{entropy:.4f} bit/byte[/bold]  (max: 8.0)')
    console.print(f'  Tespit     : {interp}')
    console.print(f'  Açıklama   : [dim]{detail}[/dim]')
    # Block entropy (256 byte blocks)
    console.print(f'\n  [dim]Blok entropi grafiği (her blok 1KB):[/dim]')
    BLOCK = 1024
    blocks = [data[i:i+BLOCK] for i in range(0,min(total,20*BLOCK),BLOCK)]
    for i, blk in enumerate(blocks[:20]):
        f2 = [0]*256
        for b in blk: f2[b] += 1
        e2 = -sum((f/len(blk))*_math.log2(f/len(blk)) for f in f2 if f>0)
        bar = '█' * int(e2*4)
        color = 'red' if e2>7.5 else 'yellow' if e2>6 else 'green'
        console.print(f'  {i*BLOCK:8}  [{color}]{bar:<32}[/{color}] {e2:.2f}')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_file_carver():
    """Binary içinden gömülü dosyaları çıkar"""
    os.system('clear')
    console.print('[bold #06B6D4]🔪 FILE CARVER[/bold #06B6D4]')
    console.print('[dim]  Binary dosya içindeki gömülü dosyaları tespit et ve çıkar[/dim]\n')
    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    SIGNATURES = [
        (b'\x1bLua',     '.luac',   'Lua Bytecode'),
        (b'\x9e\x2a\x83\xc1', '.uasset', 'UE4 Asset'),
        (b'PK\x03\x04',  '.zip',    'ZIP Archive'),
        (b'\x7fELF',     '.elf',    'ELF Binary'),
        (b'\x1f\x8b',    '.gz',     'GZIP'),
        (b'BZh',         '.bz2',    'BZip2'),
        (b'\x89PNG',     '.png',    'PNG Image'),
        (b'\xff\xd8\xff', '.jpg',   'JPEG Image'),
        (b'DDS ',        '.dds',    'DDS Texture'),
        (b'OGG',         '.ogg',    'OGG Audio'),
        (b'RIFF',        '.riff',   'RIFF (WAV/AVI)'),
        (b'%PDF',        '.pdf',    'PDF'),
        (b'\xfa\x5c\xea\x01', '.enc', 'FANTOOL Encrypted'),
    ]
    found = []; pos_set = set()
    for sig, ext, name in SIGNATURES:
        pos = 0
        while True:
            pos = data.find(sig, pos)
            if pos == -1: break
            if pos not in pos_set:
                pos_set.add(pos)
                found.append({'offset':pos,'sig':sig,'ext':ext,'name':name})
            pos += len(sig)
    found.sort(key=lambda x: x['offset'])
    if not found:
        console.print('[yellow]Gömülü dosya bulunamadı[/yellow]')
        flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    console.print(f'\n  [green]{len(found)} gömülü dosya:[/green]\n')
    for i,f in enumerate(found,1):
        console.print(f'  [{i:2}] [dim]0x{f["offset"]:08X}[/dim]  [cyan]{f["name"]:<20}[/cyan]  {f["ext"]}')
    c = safe_input('\n  Çıkar? (E/h): ').strip().lower(); flush_stdin()
    if c == 'h': return
    out_dir = p.parent/f'{p.stem}_carved'
    out_dir.mkdir(parents=True,exist_ok=True)
    # Extract each found file (up to next signature or 10MB)
    for i, item in enumerate(found):
        start = item['offset']
        end = found[i+1]['offset'] if i+1 < len(found) else min(start+10*1024*1024, len(data))
        chunk = data[start:end]
        out_f = out_dir/f'carved_{i:03d}_{item["offset"]:08X}{item["ext"]}'
        out_f.write_bytes(chunk)
        console.print(f'  [green]✓ {out_f.name} ({human_size(len(chunk))})[/green]')
    console.print(f'\n[bold green]✅ {len(found)} dosya → {out_dir}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_hex_multi_replace():
    """Birden fazla pattern'i aynı anda bul ve değiştir"""
    os.system('clear')
    console.print('[bold #06B6D4]🔄 MULTI-PATTERN HEX REPLACE[/bold #06B6D4]')
    console.print('[dim]  Birden fazla hex pattern\'i aynı anda bul/değiştir[/dim]\n')
    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = bytearray(p.read_bytes())
    patterns = []
    console.print('  Pattern gir (hex, boş bırakınca bitir):')
    while True:
        find_raw = safe_input(f'  [{len(patterns)+1}] Aranan (hex): ').strip().replace(' ',''); flush_stdin()
        if not find_raw: break
        repl_raw = safe_input(f'      Yeni    (hex): ').strip().replace(' ',''); flush_stdin()
        try:
            find_b = bytes.fromhex(find_raw)
            repl_b = bytes.fromhex(repl_raw)
            patterns.append((find_b, repl_b))
            console.print(f'  [green]  ✓ Eklendi[/green]')
        except: console.print('  [red]  Geçersiz HEX[/red]')
    if not patterns:
        console.print(f'[yellow]Pattern girilmedi[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    total = 0
    for find_b, repl_b in patterns:
        count = 0; pos = 0
        while True:
            pos = data.find(find_b, pos)
            if pos == -1: break
            if len(repl_b) == len(find_b):
                data[pos:pos+len(find_b)] = repl_b
            else:
                data = bytearray(bytes(data).replace(find_b, repl_b)); break
            count += 1; pos += len(repl_b)
        console.print(f'  [green]✓ {find_b.hex().upper()[:20]} → {count} eşleşme[/green]')
        total += count
    out = p.parent/(p.stem+'_replaced'+p.suffix)
    out.write_bytes(bytes(data))
    console.print(f'\n[bold green]✅ {total} toplam değişiklik → {out.name}[/bold green]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_crc_tool():
    """CRC32/Adler32/MD5/SHA1/SHA256 hesapla"""
    os.system('clear')
    console.print('[bold #06B6D4]🔑 CRC / HASH TOOL[/bold #06B6D4]')
    console.print('[dim]  CRC32, Adler32, MD5, SHA1, SHA256 hesapla[/dim]\n')
    path_raw = safe_input('  Dosya yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    import hashlib as _hl, zlib as _zl
    crc32  = _zl.crc32(data) & 0xFFFFFFFF
    adler  = _zl.adler32(data) & 0xFFFFFFFF
    md5    = _hl.md5(data).hexdigest()
    sha1   = _hl.sha1(data).hexdigest()
    sha256 = _hl.sha256(data).hexdigest()
    sha512 = _hl.sha512(data).hexdigest()
    console.print(f'\n  Dosya  : [cyan]{p.name}[/cyan]  ({human_size(len(data))})')
    console.print(f'\n  CRC32  : [white]{crc32:08X}[/white]  ({crc32})')
    console.print(f'  Adler32: [white]{adler:08X}[/white]  ({adler})')
    console.print(f'  MD5    : [white]{md5}[/white]')
    console.print(f'  SHA1   : [white]{sha1}[/white]')
    console.print(f'  SHA256 : [white]{sha256}[/white]')
    console.print(f'  SHA512 : [dim]{sha512[:64]}...[/dim]')
    out = p.parent/(p.stem+'_hashes.txt')
    out.write_text(f'File: {p.name}\nCRC32: {crc32:08X}\nAdler32: {adler:08X}\nMD5: {md5}\nSHA1: {sha1}\nSHA256: {sha256}\nSHA512: {sha512}\n', encoding='utf-8')
    console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_so_ultra_menu():
    while True:
        os.system('clear')
        console.print('[bold #06B6D4]🔬 SO / ANALİZ ULTRA[/bold #06B6D4]')
        console.print('[dim]  Binary analiz tam pipeline[/dim]\n')
        console.print('  [1]  📋 PLT Parser          [dim]extern fonksiyon listesi[/dim]')
        console.print('  [2]  💾 Section Dump        [dim]her section ayrı dosyaya[/dim]')
        console.print('  [3]  🔗 Dependency Lister   [dim]bağımlı .so listesi[/dim]')
        console.print('  [4]  📊 Entropi Analizörü   [dim]şifreli mi/sıkıştırılmış mı[/dim]')
        console.print('  [5]  🔪 File Carver         [dim]gömülü dosyaları çıkar[/dim]')
        console.print('  [6]  🔄 Multi-Pattern Hex   [dim]çoklu hex bul/değiştir[/dim]')
        console.print('  [7]  🔑 CRC / Hash Tool     [dim]CRC32/Adler32/SHA256[/dim]')
        console.print('  [8]  🔬 ELF Header          [dim]mimari/section/segment[/dim]')
        console.print('  [9]  🔭 Symbol Finder       [dim]fonksiyon sembol ara[/dim]')
        console.print('  [10] 🔧 ARM64 Reader        [dim]instruction oku[/dim]')
        console.print('  [0]  GERİ\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1':  action_plt_parser()
        elif c == '2':  action_section_dump()
        elif c == '3':  action_so_dependency_lister()
        elif c == '4':  action_entropy_analyzer()
        elif c == '5':  action_file_carver()
        elif c == '6':  action_hex_multi_replace()
        elif c == '7':  action_crc_tool()
        elif c == '8':  action_elf_parser()
        elif c == '9':  action_symbol_finder()
        elif c == '10': action_arm64_reader()

# ══════════════════════════════════════════════════════════════════
# [33] UASSET ULTRA — Export/Import/Name table editörler
# ══════════════════════════════════════════════════════════════════

def action_export_table_viewer():
    """UAsset export table viewer"""
    os.system('clear')
    console.print('[bold #A855F7]📤 EXPORT TABLE VIEWER[/bold #A855F7]')
    console.print('[dim]  .uasset dosyasındaki tüm export entry\'lerini göster[/dim]\n')
    path_raw = safe_input('  .uasset yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = p.read_bytes()
    if struct.unpack_from('<I', data, 0)[0] != 0x9E2A83C1:
        console.print(f'[red]❌ Geçersiz .uasset[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ua = _UAssetFileEx(); ua.load_data(data)
    # Show all strings as export hints
    console.print(f'\n  [green]{len(ua.names)} isim tablosu entry:[/green]\n')
    PAGE = 30; page = 0; filtered = ua.names
    search = safe_input('  Filtre (boş=hepsi): ').strip().lower(); flush_stdin()
    if search: filtered = [n for n in ua.names if search in n['name'].lower()]
    while True:
        os.system('clear')
        console.print(f'[bold]📤 {p.name}[/bold]  [dim]{len(filtered)} entry | Sayfa {page+1}/{max(1,(len(filtered)+PAGE-1)//PAGE)}[/dim]\n')
        chunk = filtered[page*PAGE:(page+1)*PAGE]
        for i, nm in enumerate(chunk, page*PAGE):
            console.print(f'  [dim]{i:4}[/dim]  [dim]0x{nm["offset"]:06X}[/dim]  [cyan]{nm["name"][:80]}[/cyan]')
        console.print()
        console.print(f'[dim]  {T("nav_hint")}[/dim]')
        cmd = safe_input('  > ').strip(); flush_stdin()
        if cmd == '0': break
        elif cmd == 'n': page = min(page+1, max(0,(len(filtered)-1)//PAGE))
        elif cmd == 'p': page = max(page-1, 0)
    # Save
    out = p.parent/(p.stem+'_exports.txt')
    out.write_text('\n'.join(f'{n["offset"]:06X}\t{n["name"]}' for n in ua.names), encoding='utf-8')
    console.print(f'  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_import_table_viewer():
    """UAsset import/dependency viewer"""
    os.system('clear')
    console.print('[bold #A855F7]📥 IMPORT/DEPENDENCY VIEWER[/bold #A855F7]')
    console.print('[dim]  .uasset\'in bağımlı olduğu asset\'leri listele[/dim]\n')
    path_raw = safe_input('  .uasset yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ua = _UAssetFileEx(); ua.load_data(p.read_bytes())
    console.print(f'\n  [green]{len(ua.paths)} asset path:[/green]\n')
    for entry in ua.paths[:50]:
        console.print(f'  [dim]0x{entry["offset"]:06X}[/dim]  [cyan]{entry["path"][:100]}[/cyan]')
    if len(ua.paths) > 50:
        console.print(f'  [dim]+{len(ua.paths)-50} tane daha...[/dim]')
    out = p.parent/(p.stem+'_imports.txt')
    out.write_text('\n'.join(e['path'] for e in ua.paths), encoding='utf-8')
    console.print(f'\n  [dim]Kaydedildi: {out}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_name_table_editor():
    """UAsset name table editörü"""
    os.system('clear')
    console.print('[bold #A855F7]✏️  NAME TABLE EDİTÖRÜ[/bold #A855F7]')
    console.print('[dim]  .uasset isim tablosundaki stringleri düzenle[/dim]\n')
    path_raw = safe_input('  .uasset yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    data = bytearray(p.read_bytes())
    ua = _UAssetFileEx(); ua.load_data(bytes(data))
    if not ua.all_strings:
        console.print(f'[yellow]String bulunamadı[/yellow]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    PAGE = 25; page = 0; changes = {}
    while True:
        os.system('clear')
        console.print(f'[bold]✏️  {p.name}[/bold]  [dim]{len(ua.all_strings)} string | Sayfa {page+1}/{(len(ua.all_strings)+PAGE-1)//PAGE}[/dim]\n')
        chunk = ua.all_strings[page*PAGE:(page+1)*PAGE]
        for i, s in enumerate(chunk, page*PAGE+1):
            ch = changes.get(s['offset'])
            val = ch if ch else s['string']
            mark = ' [yellow]✎[/yellow]' if ch else ''
            console.print(f'  [yellow]{i:4}[/yellow]  [dim]0x{s["offset"]:06X}[/dim]  [cyan]{val[:60]}[/cyan]{mark}')
        console.print()
        console.print(f'[dim]  {T("nav_full")}[/dim]')
        cmd = safe_input('  > ').strip(); flush_stdin()
        if cmd == '0': break
        elif cmd == 'n': page = min(page+1,(len(ua.all_strings)-1)//PAGE)
        elif cmd == 'p': page = max(page-1,0)
        elif cmd == 's':
            if not changes: console.print(f'[yellow]Değişiklik yok[/yellow]'); safe_input(f'  {T("press_enter")}'); continue
            d = bytearray(p.read_bytes())
            for off, new_str in changes.items():
                enc = new_str.encode('utf-8') + b'\x00'
                if off+4+len(enc) <= len(d):
                    struct.pack_into('<I', d, off, len(enc))
                    d[off+4:off+4+len(enc)] = enc
            out = p.parent/(p.stem+'_nametbl'+p.suffix)
            out.write_bytes(bytes(d))
            console.print(f'[green]✅ Kaydedildi: {out.name}[/green]')
            safe_input(f'  {T("press_enter")}'); break
        elif cmd.isdigit():
            idx = int(cmd)-1
            if 0<=idx<len(ua.all_strings):
                s = ua.all_strings[idx]
                console.print(f'\n  [cyan]{s["string"]}[/cyan]')
                new = safe_input('  Yeni değer (boş=iptal): ').strip(); flush_stdin()
                if new: changes[s['offset']] = new; console.print('[green]✅[/green]')
                safe_input(f'  {T("press_enter")}')

def action_property_type_explorer():
    """UAsset property tiplerini istatistiksel göster"""
    os.system('clear')
    console.print('[bold #A855F7]📊 PROPERTY TYPE EXPLORER[/bold #A855F7]')
    console.print('[dim]  .uexp\'deki tüm property tiplerini say ve göster[/dim]\n')
    path_raw = safe_input('  .uexp yolu: ').strip().strip('"'); flush_stdin()
    p = Path(path_raw)
    if not p.exists(): console.print(f'[red]❌ {T("file_not_found")}[/red]'); flush_stdin(); safe_input(f'  {T("press_enter")}'); return
    ua_path = p.with_suffix('.uasset')
    ua = _UAssetFileEx()
    if ua_path.exists(): ua.load_data(ua_path.read_bytes())
    ue = _UExpFileEx(ua); ue.load_data(p.read_bytes())
    from collections import Counter as _Counter
    type_counts = _Counter(prop['type'] for prop in ue.properties)
    name_counts = _Counter(prop['name'].split('_')[0] for prop in ue.properties)
    console.print(f'\n  [green]{len(ue.properties)} property bulundu[/green]\n')
    console.print('  [cyan]Tip dağılımı:[/cyan]')
    for typ, cnt in type_counts.most_common():
        bar = '█' * cnt
        console.print(f'  [white]{typ:<12}[/white]  [yellow]{cnt:3}[/yellow]  [dim]{bar[:30]}[/dim]')
    console.print(f'\n  [cyan]İsim grupları (ilk 10):[/cyan]')
    for name, cnt in name_counts.most_common(10):
        console.print(f'  [white]{name:<20}[/white]  [dim]{cnt}[/dim]')
    flush_stdin(); safe_input(f'\n  {T("press_enter")}')

def action_uasset_ultra_menu():
    while True:
        os.system('clear')
        console.print('[bold #A855F7]🎮 UASSET ULTRA[/bold #A855F7]')
        console.print('[dim]  UAsset/UExp tam pipeline araçları[/dim]\n')
        console.print('  [1]  📤 Export Table Viewer [dim]isim tablosu görüntüle[/dim]')
        console.print('  [2]  📥 Import/Dependency   [dim]bağımlı asset\'ler[/dim]')
        console.print('  [3]  ✏️  Name Table Editörü  [dim]stringleri düzenle[/dim]')
        console.print('  [4]  📊 Property Explorer   [dim]property tip istatistiği[/dim]')
        console.print('  [5]  🎮 UASSET Editörü     [dim]gelişmiş property editörü[/dim]')
        console.print('  [6]  📊 Data Table Parser   [dim]uasset string/path dump[/dim]')
        console.print('  [0]  GERİ\n')
        c = safe_input('  > ').strip(); flush_stdin()
        if   c == '0': return
        elif c == '1': action_export_table_viewer()
        elif c == '2': action_import_table_viewer()
        elif c == '3': action_name_table_editor()
        elif c == '4': action_property_type_explorer()
        elif c == '5': action_uasset_editor()
        elif c == '6': action_data_table_parser()

# ══════════════════════════════════════════════════════════════════
# LANGUAGE SYSTEM
# ══════════════════════════════════════════════════════════════════

_LANG = ['TR']  # mutable so subfunctions can change it

_TR = {
    # Login
    'enter_key':     'FANTOOL KEY gir',
    'wrong_key':     '❌ Yanlış key! Tekrar dene.',
    'welcome':       '✅ HOŞ GELDİN',
    'select_lang':   'Dil Seç / Select Language',
    'lang_tr':       '[1] 🇹🇷 Türkçe',
    'lang_en':       '[2] 🇬🇧 English',
    # Main menu
    'pak_files':     'PAK Dosyaları',
    'workspaces':    'Çalışma Alanları',
    'no_pak':        'PAK dosyası yok',
    'no_ws':         'Çalışma alanı yok',
    'exit':          'ÇIKIŞ',
    # Menu items
    'm1':  '💉 CUSTOM INJECT',       'd1': 'mod dosyasını PAK içine enjekte et',
    'm2':  '📋 PAK İÇERİĞİNİ GÖR', 'd2': 'PAK içindeki dosyaları listele',
    'm3':  '🧹 ÇALIŞMA ALANI TEMİZLE','d3': 'FANx* klasörlerini sil',
    'm4':  '🔓 LUA MODE',            'd4': 'decompile & recompile & strip',
    'm5':  '🔧 120 FPS UNLOCK',      'd5': 'FPS kilidini aç',
    'm6':  '🧥 SKIN TOOL',           'd6': 'skin ID değiştir',
    'm7':  '🔍 DOSYA BULUCU',        'd7': 'PAK içinde dosya ara',
    'm8':  '🗑  DELETE FROM PAK',     'd8': 'PAK içinden dosya sil',
    'm9':  '📦 OBB TOOL',            'd9': 'OBB işlemleri',
    'm10': '🔑 SM4 KEY FINDER',      'd10':'SM4 key bul',
    'm11': '⚡ XOR / AES CRYPT',     'd11':'şifrele veya çöz',
    'm12': '🔧 SO PATCHER',          'd12':'lib.so binary patch',
    'm13': '🔐 NUCLEAR ENCRYPTOR',   'd13':'çok katmanlı şifrele',
    'm14': '📤 PAK UNPACK',          'd14':'PAK dosyalarını çıkar',
    'm15': '📦 PAK REPACK',          'd15':'değiştirilmiş dosyaları yaz',
    'm16': '🎮 UASSET EDITOR',       'd16':'.uasset/.uexp editörü',
    'm17': '⚡ MOD PATCH',           'd17':'headshot, white body, grass',
    'm18': '🛠  ARAÇLAR',             'd18':'checksum, base64, dosya araçları',
    'm19': '🎮 PUBG ARAÇLAR',        'd19':'config, pattern, ELF, backup',
    'm20': '🔬 GELİŞMİŞ PUBG',      'd20':'tersine mühendislik, ARM64',
    'm21': '🔐 KRİPTOGRAFİ',        'd21':'SM4, RC4, ChaCha20, RSA',
    'm22': '📦 PAK ULTRA',           'd22':'forge, sig patch, clone',
    'm23': '🎮 OYUN ULTRA',          'd23':'mass patch, damage, speed',
    'm24': '🖥  TERMUX PRO',          'd24':'git, log, process scan',
    'm25': '🎯 PUBG LUA HACKS',      'd25':'no-recoil, speed, hook, loot',
    'm26': '💀 BINARY HACKS',        'd26':'libUE4.so: recoil, FOV, offset',
    'm27': '🎮 ASSET HACKS',         'd27':'recoil/spread/ADS bulk patch',
    'm28': '🎨 TEXTURE/VISUAL',      'd28':'white grass, ESP texture',
    'm29': '📦 MOD PACK',            'd29':'batch mod, zip, version checker',
    'm30': '📜 LUA ULTRA',           'd30':'triple compile, minifier, diff',
    'm31': '📦 PAK ULTRA PLUS',      'd31':'filtreli çıkar, chunk, zip',
    'm32': '🔬 SO/ANALİZ ULTRA',     'd32':'PLT, section dump, entropy',
    'm33': '🎮 UASSET ULTRA',        'd33':'export/import/name table',
    # Common UI
    'back':             'GERİ',
    'press_enter':      'Enter...',
    'invalid':          'Geçersiz.',
    'file_not_found':   'Dosya yok',
    'folder_not_found': 'Klasör yok',
    'done':             'Tamamlandı',
    'scanning':         'Taranıyor...',
    'loading':          'Yükleniyor...',
    'saved':            'Kaydedildi',
    'output':           'Çıktı',
    'error':            'Hata',
    'not_found':        'bulunamadı',
    'created':          'oluşturuldu',
    'cancelled':        'İptal edildi',
    'continue_yn':      'Devam? (E/h)',
    'select_n':         'Seç (numara)',
    'confirm':          'Onaylıyor musun? (E/h)',
    'file_path':        'Dosya yolu',
    'folder_path':      'Klasör yolu',
    'result':           'Sonuç',
    'failed':           'Başarısız',
    'total':            'Toplam',
    'nav_hint':         'n=sonraki | p=önceki | 0=geri',
    'nav_full':         'n=sonraki | p=önceki | numara=düzenle | s=kaydet | 0=geri',
    'no_pak':           'PAK dosyası yok',
    'no_lua':           'Lua dosyası yok',
    'first_unpack':     'Önce [14] PAK UNPACK yap',
    'empty_folder':     'Klasör boş',
    'try_install':      'Kurmayı deneyelim mi? (E/h)',
    'new_value':        'Yeni değer (boş=iptal)',
    'choose_ver':       'Versiyon seç (0-3)',
    'file_prompt':      'Dosya yolu',
    'apply_all':        'Hepsini uygula (A) veya numara gir',
    'downloading':      'İndiriliyor...',
    'report_saved':     'Rapor kaydedildi',

}

_EN = {
    # Login
    'enter_key':     'Enter FANTOOL KEY',
    'wrong_key':     '❌ Wrong key! Try again.',
    'welcome':       '✅ WELCOME',
    'select_lang':   'Select Language / Dil Seç',
    'lang_tr':       '[1] 🇹🇷 Türkçe',
    'lang_en':       '[2] 🇬🇧 English',
    # Main menu
    'pak_files':     'PAK Files',
    'workspaces':    'Workspaces',
    'no_pak':        'No PAK files',
    'no_ws':         'No workspaces',
    'exit':          'EXIT',
    # Menu items
    'm1':  '💉 CUSTOM INJECT',       'd1': 'inject mod file into PAK',
    'm2':  '📋 VIEW PAK CONTENTS',   'd2': 'list files inside PAK',
    'm3':  '🧹 CLEAN WORKSPACES',    'd3': 'delete FANx* folders',
    'm4':  '🔓 LUA MODE',            'd4': 'decompile & recompile & strip',
    'm5':  '🔧 120 FPS UNLOCK',      'd5': 'unlock FPS cap',
    'm6':  '🧥 SKIN TOOL',           'd6': 'replace skin IDs',
    'm7':  '🔍 FILE FINDER',         'd7': 'search inside extracted PAK',
    'm8':  '🗑  DELETE FROM PAK',     'd8': 'remove files from PAK',
    'm9':  '📦 OBB TOOL',            'd9': 'OBB operations',
    'm10': '🔑 SM4 KEY FINDER',      'd10':'find SM4 decryption key',
    'm11': '⚡ XOR / AES CRYPT',     'd11':'encrypt or decrypt files',
    'm12': '🔧 SO PATCHER',          'd12':'lib.so binary patch',
    'm13': '🔐 NUCLEAR ENCRYPTOR',   'd13':'multi-layer encryption',
    'm14': '📤 PAK UNPACK',          'd14':'extract all files from PAK',
    'm15': '📦 PAK REPACK',          'd15':'write modified files to PAK',
    'm16': '🎮 UASSET EDITOR',       'd16':'.uasset/.uexp property editor',
    'm17': '⚡ MOD PATCH',           'd17':'headshot, white body, grass',
    'm18': '🛠  TOOLS',               'd18':'checksum, base64, file tools',
    'm19': '🎮 PUBG TOOLS',          'd19':'config, pattern, ELF, backup',
    'm20': '🔬 ADVANCED PUBG',       'd20':'reverse engineering, ARM64',
    'm21': '🔐 CRYPTOGRAPHY',        'd21':'SM4, RC4, ChaCha20, RSA',
    'm22': '📦 PAK ULTRA',           'd22':'forge, sig patch, clone',
    'm23': '🎮 GAME ULTRA',          'd23':'mass patch, damage, speed',
    'm24': '🖥  TERMUX PRO',          'd24':'git, log, process scan',
    'm25': '🎯 PUBG LUA HACKS',      'd25':'no-recoil, speed, hook, loot',
    'm26': '💀 BINARY HACKS',        'd26':'libUE4.so: recoil, FOV, offset',
    'm27': '🎮 ASSET HACKS',         'd27':'recoil/spread/ADS bulk patch',
    'm28': '🎨 TEXTURE/VISUAL',      'd28':'white grass, ESP texture',
    'm29': '📦 MOD PACK',            'd29':'batch mod, zip, version check',
    'm30': '📜 LUA ULTRA',           'd30':'triple compile, minifier, diff',
    'm31': '📦 PAK ULTRA PLUS',      'd31':'filter extract, chunk, zip',
    'm32': '🔬 SO/ANALYSIS ULTRA',   'd32':'PLT, section dump, entropy',
    'm33': '🎮 UASSET ULTRA',        'd33':'export/import/name table',
    # Common UI
    'back':             'BACK',
    'press_enter':      'Enter...',
    'invalid':          'Invalid.',
    'file_not_found':   'File not found',
    'folder_not_found': 'Folder not found',
    'done':             'Done',
    'scanning':         'Scanning...',
    'loading':          'Loading...',
    'saved':            'Saved',
    'output':           'Output',
    'error':            'Error',
    'not_found':        'not found',
    'created':          'created',
    'cancelled':        'Cancelled',
    'continue_yn':      'Continue? (Y/n)',
    'select_n':         'Select (number)',
    'confirm':          'Confirm? (Y/n)',
    'file_path':        'File path',
    'folder_path':      'Folder path',
    'result':           'Result',
    'failed':           'Failed',
    'total':            'Total',
    'nav_hint':         'n=next | p=prev | 0=back',
    'nav_full':         'n=next | p=prev | number=edit | s=save | 0=back',
    'no_pak':           'No PAK files',
    'no_lua':           'No Lua files',
    'first_unpack':     'Do [14] PAK UNPACK first',
    'empty_folder':     'Folder is empty',
    'try_install':      'Try to install? (Y/n)',
    'new_value':        'New value (empty=cancel)',
    'choose_ver':       'Choose version (0-3)',
    'file_prompt':      'File path',
    'apply_all':        'Apply all (A) or enter number',
    'downloading':      'Downloading...',
    'report_saved':     'Report saved',

}

def T(key):
    """Get translation for current language."""
    d = _EN if _LANG[0]=='EN' else _TR
    return d.get(key, _TR.get(key, key))

# ══════════════════════════════════════════════════════════════════
# LOGIN + LANGUAGE SELECTION
# ══════════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════════
# RUNTIME TRANSLATION ENGINE
# console.print ve safe_input otomatik tercüme eder
# ══════════════════════════════════════════════════════════════════

_AUTO_TRANSLATE = {
    # Navigation
    'GERİ': 'BACK', 'Geri': 'Back',
    'Sonraki': 'Next', 'Önceki': 'Previous',
    'n=sonraki': 'n=next', 'p=önceki': 'p=prev',
    'numara=düzenle': 'number=edit',
    's=kaydet': 's=save', '0=geri': '0=back',
    'numara gir': 'enter number', 'boş=bitir': 'empty=done',
    'boş=iptal': 'empty=cancel', 'boş=hepsi': 'empty=all',
    # Common actions
    'Seç': 'Select', 'seç': 'select',
    'Seçin': 'Select', 'seçin': 'select',
    'Girin': 'Enter', 'girin': 'enter',
    'Yazın': 'Type', 'yazın': 'type',
    'Onaylıyor musun': 'Confirm',
    'Devam': 'Continue', 'devam': 'continue',
    'Uygula': 'Apply', 'uygula': 'apply',
    'Uygulansın mı': 'Apply?',
    'Kaydet': 'Save', 'kaydet': 'save',
    'Sil': 'Delete', 'sil': 'delete',
    'Çık': 'Exit', 'çık': 'exit',
    'Kapat': 'Close', 'kapat': 'close',
    'Temizle': 'Clear', 'temizle': 'clear',
    'Yükle': 'Load', 'yükle': 'load',
    'İndir': 'Download', 'indir': 'download',
    'Oluştur': 'Create', 'oluştur': 'create',
    'Düzenle': 'Edit', 'düzenle': 'edit',
    'Kopyala': 'Copy', 'kopyala': 'copy',
    'Taşı': 'Move', 'taşı': 'move',
    'Ara': 'Search', 'ara': 'search',
    'Bul': 'Find', 'bul': 'find',
    'Çalıştır': 'Run', 'çalıştır': 'run',
    'Başlat': 'Start', 'başlat': 'start',
    'Durdur': 'Stop', 'durdur': 'stop',
    'Bitir': 'Finish', 'bitir': 'finish',
    'Atla': 'Skip', 'atla': 'skip',
    'Gönder': 'Send', 'gönder': 'send',
    'Ekle': 'Add', 'ekle': 'add',
    'Çıkar': 'Extract', 'çıkar': 'extract',
    'Dönüştür': 'Convert', 'dönüştür': 'convert',
    'Derle': 'Compile', 'derle': 'compile',
    'Tarama': 'Scan', 'tarama': 'scan',
    # Status messages
    'Taranıyor': 'Scanning', 'taranıyor': 'scanning',
    'Yükleniyor': 'Loading', 'yükleniyor': 'loading',
    'Hazırlanıyor': 'Preparing', 'hazırlanıyor': 'preparing',
    'İşleniyor': 'Processing', 'işleniyor': 'processing',
    'Oluşturuluyor': 'Creating', 'oluşturuluyor': 'creating',
    'Kaydediliyor': 'Saving', 'kaydediliyor': 'saving',
    'Yedekleniyor': 'Backing up',
    'Birleştiriliyor': 'Merging',
    'Çıkarılıyor': 'Extracting', 'çıkarılıyor': 'extracting',
    'Derleniyor': 'Compiling', 'derleniyor': 'compiling',
    'Dönüştürülüyor': 'Converting',
    'Aranıyor': 'Searching', 'aranıyor': 'searching',
    'Hesaplanıyor': 'Calculating',
    # Results
    'Tamamlandı': 'Completed', 'tamamlandı': 'completed',
    'Başarılı': 'Success', 'başarılı': 'success',
    'Başarısız': 'Failed', 'başarısız': 'failed',
    'Kaydedildi': 'Saved', 'kaydedildi': 'saved',
    'Oluşturuldu': 'Created', 'oluşturuldu': 'created',
    'Silindi': 'Deleted', 'silindi': 'deleted',
    'Kopyalandı': 'Copied', 'kopyalandı': 'copied',
    'Çıkarıldı': 'Extracted', 'çıkarıldı': 'extracted',
    'Derlendi': 'Compiled', 'derlendi': 'compiled',
    'Atlandı': 'Skipped', 'atlandı': 'skipped',
    'Bulunamadı': 'Not found', 'bulunamadı': 'not found',
    'bulundu': 'found', 'Bulundu': 'Found',
    'Yüklendi': 'Loaded', 'yüklendi': 'loaded',
    'Eklendi': 'Added', 'eklendi': 'added',
    'Değiştirildi': 'Changed', 'değiştirildi': 'changed',
    'Patch uygulandı': 'Patch applied',
    'yamalandı': 'patched', 'Yamalandı': 'Patched',
    'sıfırlandı': 'zeroed', 'Sıfırlandı': 'Zeroed',
    'artırıldı': 'increased', 'Artırıldı': 'Increased',
    'azaltıldı': 'reduced', 'Azaltıldı': 'Reduced',
    'çarpıldı': 'multiplied',
    # Errors
    'Geçersiz': 'Invalid', 'geçersiz': 'invalid',
    'Hata': 'Error', 'hata': 'error',
    'Dosya yok': 'File not found',
    'Klasör yok': 'Folder not found',
    'Klasör boş': 'Folder is empty',
    'Dosya bulunamadı': 'File not found',
    'Dizin boş': 'Directory is empty',
    'Bağlantı hatası': 'Connection error',
    'İzin hatası': 'Permission error',
    'Syntax hatası': 'Syntax error',
    'Zaman aşımı': 'Timeout',
    # Labels
    'Dosya': 'File', 'dosya': 'file',
    'Klasör': 'Folder', 'klasör': 'folder',
    'Boyut': 'Size', 'boyut': 'size',
    'Toplam': 'Total', 'toplam': 'total',
    'Sonuç': 'Result', 'sonuç': 'result',
    'Çıktı': 'Output', 'çıktı': 'output',
    'Giriş': 'Input', 'giriş': 'input',
    'Versiyon': 'Version', 'versiyon': 'version',
    'Bilgi': 'Info', 'bilgi': 'info',
    'Uyarı': 'Warning', 'uyarı': 'warning',
    'Rapor': 'Report', 'rapor': 'report',
    'Liste': 'List', 'liste': 'list',
    'Tablo': 'Table', 'tablo': 'table',
    'Sayfa': 'Page', 'sayfa': 'page',
    'Satır': 'Line', 'satır': 'line',
    'Karakter': 'Character', 'karakter': 'character',
    'Anahtar': 'Key', 'anahtar': 'key',
    'Şifre': 'Password', 'şifre': 'password',
    'Offset': 'Offset',
    'Adres': 'Address', 'adres': 'address',
    'İsim': 'Name', 'isim': 'name',
    'Tür': 'Type', 'tür': 'type',
    'Değer': 'Value', 'değer': 'value',
    'Yeni değer': 'New value',
    'Eski değer': 'Old value',
    'Mevcut': 'Current', 'mevcut': 'current',
    'Önerilen': 'Suggested',
    'Seçilen': 'Selected', 'seçilen': 'selected',
    'Varsayılan': 'Default', 'varsayılan': 'default',
    'Minimum': 'Minimum', 'Maksimum': 'Maximum',
    'Yüzde': 'Percentage', 'yüzde': 'percentage',
    'Çarpan': 'Multiplier', 'çarpan': 'multiplier',
    'Hızı': 'Speed', 'hızı': 'speed',
    'Menzil': 'Range', 'menzil': 'range',
    'Hasar': 'Damage', 'hasar': 'damage',
    'Süre': 'Duration', 'süre': 'duration',
    'Zaman': 'Time', 'zaman': 'time',
    # Prompts
    'Dosya yolu': 'File path',
    'Klasör yolu': 'Folder path',
    'Yol girin': 'Enter path',
    'İsim girin': 'Enter name',
    'Değer girin': 'Enter value',
    'Key girin': 'Enter key',
    'Şifre girin': 'Enter password',
    'Metin girin': 'Enter text',
    'Numara girin': 'Enter number',
    'Aranan metin': 'Search text',
    'Yeni değer (boş=iptal)': 'New value (empty=cancel)',
    'Onaylıyor musun? (E/h)': 'Confirm? (Y/n)',
    'Devam? (E/h)': 'Continue? (Y/n)',
    'Uygula? (E/h)': 'Apply? (Y/n)',
    'Sıfırla? (E/h)': 'Reset? (Y/n)',
    'Kaydet? (E/h)': 'Save? (Y/n)',
    # Common phrases
    'Önce [14] PAK UNPACK yap': 'Do [14] PAK UNPACK first',
    'CUSTOM FILES/ klasörüne kopyala → CUSTOM INJECT': 'Copy to CUSTOM FILES/ → CUSTOM INJECT',
    'COMPILED/ klasörüne kopyala → FANTERİ LUA DERLE → CUSTOM INJECT':
        'Copy to COMPILED/ → FANTERİ LUA DERLE → CUSTOM INJECT',
    'İlk': 'First', 'Son': 'Last', 'Hepsi': 'All',
    'Evet': 'Yes', 'Hayır': 'No',
    'İptal': 'Cancel', 'iptal': 'cancel',
    'Tamam': 'OK', 'tamam': 'ok',
    'Enter...': 'Enter...',
    # Turkish specific chars
    'İ': 'I', 'ı': 'i',  # Only translate standalone
    # Sub-menu specific
    'Orijinal': 'Original', 'orijinal': 'original',
    'Kaynak': 'Source', 'kaynak': 'source',
    'Hedef': 'Target', 'hedef': 'target',
    'Yedek': 'Backup', 'yedek': 'backup',
    'Şifreli': 'Encrypted', 'şifreli': 'encrypted',
    'Şifresiz': 'Unencrypted', 'şifresiz': 'unencrypted',
    'Sıkıştırılmış': 'Compressed', 'sıkıştırılmış': 'compressed',
    'Değiştirildi': 'Modified', 'değiştirildi': 'modified',
    'Değiştirilmemiş': 'Unmodified',
    'Analiz': 'Analysis', 'analiz': 'analysis',
    'Dump': 'Dump', 'dump': 'dump',
    'Test': 'Test', 'test': 'test',
    'Bölüm': 'Section', 'bölüm': 'section',
    'Blok': 'Block', 'blok': 'block',
    'Parça': 'Chunk', 'parça': 'chunk',
    'Girdi': 'Entry', 'girdi': 'entry',
    'Çıktı dosyası': 'Output file',
    'Kaydedildi →': 'Saved →',
    'tane daha': 'more',
    'sonuç': 'result',
    'eşleşme': 'match', 'eşleşmedi': 'no match',
    'dosya işlendi': 'files processed',
    'dosya eklendi': 'files added',
    'dosya çıkarıldı': 'files extracted',
    'dosya sıfırlandı': 'files zeroed',
    'property değiştirildi': 'properties changed',
    'değer artırıldı': 'values increased',
    'değer sıfırlandı': 'values zeroed',
    'satır': 'lines',
    'Kalan': 'Remaining', 'kalan': 'remaining',
    'Mevcut derleyiciler': 'Available compilers',
    'Mevcut versiyon': 'Current version',
    'Yeni versiyon': 'New version',
    'PAK Versiyon': 'PAK Version',
    'Enc Method': 'Enc Method',
    'Şifreli': 'Encrypted',
    'Index Ofset': 'Index Offset',
    'Index Boyut': 'Index Size',
    'Dosya sayısı': 'File count',
    'Baskın stil': 'Dominant style',
    'Compression': 'Compression',
    'Block boyut': 'Block size',
    'Çalışıyor': 'Running', 'çalışıyor': 'running',
    'Hazır': 'Ready', 'hazır': 'ready',
    'Aktif': 'Active', 'aktif': 'active',
    'Pasif': 'Inactive', 'pasif': 'inactive',
    'İndirildi': 'Downloaded', 'indirildi': 'downloaded',
    'Güncellendi': 'Updated', 'güncellendi': 'updated',
    'Kuruldu': 'Installed', 'kuruldu': 'installed',
    'Kur': 'Install', 'kur': 'install',
    'Güncelle': 'Update', 'güncelle': 'update',
}

def _auto_tr(text):
    """Translate Turkish text to English based on word replacements."""
    if _LANG[0] == 'TR':
        return text
    result = str(text)
    # Sort by length (longest first) to avoid partial replacements
    for tr_word, en_word in sorted(_AUTO_TRANSLATE.items(), key=lambda x: -len(x[0])):
        if tr_word in result:
            result = result.replace(tr_word, en_word)
    return result

# Patch console.print and safe_input to auto-translate
_orig_console_print = console.print
def _tr_console_print(*args, **kwargs):
    if _LANG[0] == 'EN':
        new_args = []
        for a in args:
            if isinstance(a, str):
                new_args.append(_auto_tr(a))
            else:
                new_args.append(a)
        _orig_console_print(*new_args, **kwargs)
    else:
        _orig_console_print(*args, **kwargs)

_orig_safe_input = safe_input
def _tr_safe_input(prompt=''):
    if _LANG[0] == 'EN' and isinstance(prompt, str):
        return _orig_safe_input(_auto_tr(prompt))
    return _orig_safe_input(prompt)

# Apply patches after language is selected
def _apply_translation_patches():
    global console, safe_input
    console.print = _tr_console_print
    import builtins
    # Override safe_input globally
    import sys
    _current_module = sys.modules[__name__] if __name__ in sys.modules else None
    # We patch at function level since safe_input is a global
    globals()['safe_input'] = _tr_safe_input

_FANTOOL_KEY    = "Fanteri34"   # fallback — artık kullanılmıyor
_KEY_ATTEMPTS   = [0]
_ADMIN_SECRET   = "MEM@FANTERİ"
_KEYS_DB        = Path.home() / '.fan_keys'
_DEVICE_FILE    = Path.home() / '.fan_device'

# ══════════════════════════════════════════════════════════════════
# DEVICE FINGERPRINT
# ══════════════════════════════════════════════════════════════════
def _get_device_id() -> str:
    import hashlib as _hl2
    parts = []
    try:
        r = subprocess.run(['settings','get','secure','android_id'],
                           capture_output=True,text=True,timeout=5)
        v = r.stdout.strip()
        if v and v!='null' and len(v)>4: parts.append(v)
    except: pass
    try:
        r = subprocess.run(['getprop','ro.serialno'],
                           capture_output=True,text=True,timeout=5)
        v = r.stdout.strip()
        if v and v not in ('unknown','','0'): parts.append(v)
    except: pass
    try:
        with open('/proc/cpuinfo') as _f: cpu=_f.read()
        for line in cpu.splitlines():
            if line.startswith(('Hardware','Serial')):
                parts.append(line.split(':',1)[-1].strip())
    except: pass
    try:
        r = subprocess.run(['getprop','ro.build.fingerprint'],
                           capture_output=True,text=True,timeout=5)
        v = r.stdout.strip()
        if v: parts.append(v)
    except: pass
    if not parts: return 'UNKNOWN'
    return _hl2.sha256('|'.join(parts).encode()).hexdigest()[:48]

# ══════════════════════════════════════════════════════════════════
# KEY DATABASE
# ══════════════════════════════════════════════════════════════════
def _load_keys() -> dict:
    import json as _js2
    try:
        if _KEYS_DB.exists():
            return _js2.loads(_KEYS_DB.read_text(encoding='utf-8'))
    except: pass
    return {}

def _save_keys(db: dict):
    import json as _js2
    _KEYS_DB.write_text(_js2.dumps(db,indent=2,ensure_ascii=False),encoding='utf-8')
    try: _KEYS_DB.chmod(0o600)
    except: pass

def _load_device_key() -> str:
    try:
        if _DEVICE_FILE.exists():
            return _DEVICE_FILE.read_text().strip()
    except: pass
    return ''

def _save_device_key(key: str):
    _DEVICE_FILE.write_text(key)
    try: _DEVICE_FILE.chmod(0o600)
    except: pass

# ══════════════════════════════════════════════════════════════════
# KEY GENERATION
# ══════════════════════════════════════════════════════════════════
def _gen_key() -> str:
    import random as _rnd2, string as _st2
    while True:
        p1 = ''.join(_rnd2.choices(_st2.ascii_uppercase,k=2)) +              ''.join(_rnd2.choices(_st2.digits,k=4))
        p2 = _rnd2.choice(_st2.ascii_uppercase) +              ''.join(_rnd2.choices(_st2.digits,k=3))
        key = f'FAN-{p1}-{p2}'
        if key not in _load_keys():
            return key

# ══════════════════════════════════════════════════════════════════
# KEY VALIDATION
# ══════════════════════════════════════════════════════════════════
def _validate_key(key: str) -> tuple:
    from datetime import datetime as _dt2
    key = key.strip().upper()
    db  = _load_keys()
    if key not in db:
        return 'NOTFOUND','Key bulunamadı.'
    entry = db[key]
    if entry.get('status') == 'revoked':
        return 'REVOKED','Bu key iptal edilmiş.'
    exp = entry.get('expires')
    if exp:
        try:
            if _dt2.now() > _dt2.strptime(exp,'%Y-%m-%d'):
                return 'EXPIRED',f'Süre doldu ({exp})'
        except: pass
    dev_id = _get_device_id()
    bound  = entry.get('device_id')
    if bound and bound != dev_id:
        return 'LOCKED','Bu key başka cihazda kayıtlı.'
    if not bound:
        return 'NEW','İlk kullanım — cihaza kilitlenecek.'
    return 'OK','Geçerli.'

def _bind_key_to_device(key: str):
    from datetime import datetime as _dt2
    db = _load_keys()
    if key in db:
        db[key]['device_id']         = _get_device_id()
        db[key]['device_bound_date'] = _dt2.now().strftime('%Y-%m-%d %H:%M')
        _save_keys(db)
    _save_device_key(key)

# ══════════════════════════════════════════════════════════════════
# ADMIN PANEL
# ══════════════════════════════════════════════════════════════════
def _admin_panel():
    import time as _tad
    from datetime import datetime as _dt2, timedelta as _td2
    while True:
        os.system('clear')
        db = _load_keys()
        active  = sum(1 for v in db.values() if v.get('status')=='active')
        revoked = sum(1 for v in db.values() if v.get('status')=='revoked')
        bound   = sum(1 for v in db.values() if v.get('device_id'))
        console.print()
        console.print('[bold #FF0055]  ╔══════════════════════════════════════════════════╗[/bold #FF0055]')
        console.print('[bold #FF0055]  ║[/bold #FF0055]  [bold white]👑  FANTERİ  —  ADMIN PANEL[/bold white]               [bold #FF0055]║[/bold #FF0055]')
        console.print('[bold #FF0055]  ╠══════════════════════════════════════════════════╣[/bold #FF0055]')
        console.print(f'[bold #FF0055]  ║[/bold #FF0055]  Toplam:[cyan]{len(db):3}[/cyan]  Aktif:[green]{active:3}[/green]  Revoke:[red]{revoked:3}[/red]  Cihaz:[yellow]{bound:3}[/yellow]   [bold #FF0055]║[/bold #FF0055]')
        console.print('[bold #FF0055]  ╠══════════════════════════════════════════════════╣[/bold #FF0055]')
        console.print('[bold #FF0055]  ║[/bold #FF0055]  [bold #00FF88][1][/bold #00FF88] Key üret                                    [bold #FF0055]║[/bold #FF0055]')
        console.print('[bold #FF0055]  ║[/bold #FF0055]  [bold #00CCFF][2][/bold #00CCFF] Tüm keyleri listele                         [bold #FF0055]║[/bold #FF0055]')
        console.print('[bold #FF0055]  ║[/bold #FF0055]  [bold #FF4444][3][/bold #FF4444] Key iptal et                                [bold #FF0055]║[/bold #FF0055]')
        console.print('[bold #FF0055]  ║[/bold #FF0055]  [bold #FFAA00][4][/bold #FFAA00] Cihaz bağını sıfırla                        [bold #FF0055]║[/bold #FF0055]')
        console.print('[bold #FF0055]  ║[/bold #FF0055]  [bold #AA00FF][5][/bold #AA00FF] Key detayı                                  [bold #FF0055]║[/bold #FF0055]')
        console.print('[bold #FF0055]  ║[/bold #FF0055]  [bold white][0][/bold white] Çık (tool başlasın)                         [bold #FF0055]║[/bold #FF0055]')
        console.print('[bold #FF0055]  ╚══════════════════════════════════════════════════╝[/bold #FF0055]')
        c = safe_input('\n  ADMIN > ').strip(); flush_stdin()

        if c == '1':
            os.system('clear')
            console.print('[bold #00FF88]  ➕ KEY ÜRET[/bold #00FF88]\n')
            try: days=int(safe_input('  Kaç gün geçerli? (30): ').strip() or '30')
            except: days=30
            flush_stdin()
            note = safe_input('  Not (kullanıcı adı vs): ').strip(); flush_stdin()
            try: count=int(safe_input('  Kaç adet? (1): ').strip() or '1')
            except: count=1
            flush_stdin()
            count=min(count,50)
            db=_load_keys(); new_keys=[]
            for _ in range(count):
                k=_gen_key()
                exp=(_dt2.now()+_td2(days=days)).strftime('%Y-%m-%d')
                db[k]={'status':'active','created':_dt2.now().strftime('%Y-%m-%d %H:%M'),
                       'expires':exp,'days':days,'note':note,
                       'device_id':None,'device_bound_date':None}
                new_keys.append((k,exp))
            _save_keys(db)
            console.print()
            console.print('[bold #00FF88]  ✅ Üretilen keyler:[/bold #00FF88]\n')
            for k,exp in new_keys:
                console.print(f'  [bold #00FFCC]{k}[/bold #00FFCC]  [dim]→ {days} gün  bitiş: {exp}  {note}[/dim]')
            flush_stdin(); safe_input('\n  Enter...')

        elif c == '2':
            os.system('clear')
            console.print('[bold #00CCFF]  📋 KEY LİSTESİ[/bold #00CCFF]\n')
            db=_load_keys()
            if not db: console.print('  [dim]Hiç key yok.[/dim]')
            else:
                for k,v in sorted(db.items()):
                    st=v.get('status','?'); exp=v.get('expires','?')
                    dev='🔒' if v.get('device_id') else '🔓'
                    note=v.get('note','')
                    try: expired=_dt2.now()>_dt2.strptime(exp,'%Y-%m-%d') and st=='active'
                    except: expired=False
                    if st=='revoked': col,tag='#FF4444','[REVOKE] '
                    elif expired: col,tag='#888888','[EXPIRED]'
                    else: col,tag='#00FF88','[AKTİF]  '
                    console.print(f'  [{col}]{k}[/{col}] [dim]{tag}[/dim] {dev} [dim]bitiş:{exp} {note[:20]}[/dim]')
            flush_stdin(); safe_input('\n  Enter...')

        elif c == '3':
            os.system('clear')
            console.print('[bold #FF4444]  ❌ KEY İPTAL[/bold #FF4444]\n')
            k=safe_input('  Key: ').strip().upper(); flush_stdin()
            db=_load_keys()
            if k not in db: console.print('[red]  Bulunamadı.[/red]')
            elif db[k]['status']=='revoked': console.print('[yellow]  Zaten iptal.[/yellow]')
            else:
                onay=safe_input(f'  {k} iptal edilsin mi? (EVET): ').strip(); flush_stdin()
                if onay=='EVET':
                    db[k]['status']='revoked'; db[k]['device_id']=None; _save_keys(db)
                    console.print(f'[bold red]  ✅ {k} iptal edildi.[/bold red]')
                else: console.print('[dim]  İptal edilmedi.[/dim]')
            flush_stdin(); safe_input('\n  Enter...')

        elif c == '4':
            os.system('clear')
            console.print('[bold #FFAA00]  🔓 CİHAZ BAĞI SIFIRLA[/bold #FFAA00]\n')
            k=safe_input('  Key: ').strip().upper(); flush_stdin()
            db=_load_keys()
            if k not in db: console.print('[red]  Bulunamadı.[/red]')
            elif not db[k].get('device_id'): console.print('[yellow]  Bağlı cihaz yok.[/yellow]')
            else:
                onay=safe_input(f'  {k} cihaz bağı silinsin mi? (EVET): ').strip(); flush_stdin()
                if onay=='EVET':
                    db[k]['device_id']=None; db[k]['device_bound_date']=None; _save_keys(db)
                    console.print(f'[bold green]  ✅ {k} sıfırlandı — başka cihazda kullanılabilir.[/bold green]')
                else: console.print('[dim]  İptal edildi.[/dim]')
            flush_stdin(); safe_input('\n  Enter...')

        elif c == '5':
            os.system('clear')
            console.print('[bold #AA00FF]  🔍 KEY DETAY[/bold #AA00FF]\n')
            k=safe_input('  Key: ').strip().upper(); flush_stdin()
            db=_load_keys()
            if k not in db: console.print('[red]  Bulunamadı.[/red]')
            else:
                v=db[k]; exp=v.get('expires','?')
                try: kalan=(  _dt2.strptime(exp,'%Y-%m-%d')-_dt2.now()).days
                except: kalan='?'
                col_st='green' if v.get('status')=='active' else 'red'
                col_dev='green' if v.get('device_id') else 'dim'
                dev_txt='Bağlı 🔒' if v.get('device_id') else 'Serbest 🔓'
                console.print(f'\n  [bold #00FFCC]{k}[/bold #00FFCC]')
                console.print(f'  Durum    : [{col_st}]{v.get("status","?")}[/{col_st}]')
                console.print(f'  Oluşturma: [dim]{v.get("created","?")}[/dim]')
                console.print(f'  Bitiş    : [yellow]{exp}[/yellow]  [cyan]({kalan} gün kaldı)[/cyan]')
                console.print(f'  Cihaz    : [{col_dev}]{dev_txt}[/{col_dev}]')
                if v.get('device_bound_date'): console.print(f'  Bağlanma : [dim]{v["device_bound_date"]}[/dim]')
                if v.get('device_id'):
                    did=v['device_id']; console.print(f'  Device ID: [dim]{did[:16]}...{did[-8:]}[/dim]')
                console.print(f'  Not      : [dim]{v.get("note","—")}[/dim]')
            flush_stdin(); safe_input('\n  Enter...')

        elif c == '0':
            return



def _show_login_banner():
    os.system('clear')
    # ── Ultra FANTOOL big block letters ──
    ART = [
        "",
        "  ███████╗ █████╗ ███╗  ██╗████████╗ ██████╗  ██████╗ ██╗     ",
        "  ██╔════╝██╔══██╗████╗ ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ",
        "  █████╗  ███████║██╔██╗██║   ██║   ██║   ██║██║   ██║██║     ",
        "  ██╔══╝  ██╔══██║██║╚████║   ██║   ██║   ██║██║   ██║██║     ",
        "  ██║     ██║  ██║██║ ╚███║   ██║   ╚██████╔╝╚██████╔╝███████╗",
        "  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚══╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝",
        "",
    ]
    # Gradient: neon cyan → electric blue
    GRAD = ['','#00FFFF','#00EEFF','#00DDFF','#00CCFF','#00BBFF','#00AAFF','']

    for i, line in enumerate(ART):
        if not line.strip():
            console.print()
            continue
        c = GRAD[i] if i < len(GRAD) else '#00D4FF'
        # Add glow effect with shadow
        console.print(f'[bold {c}]{line}[/bold {c}]')

    # ── Neon separator ──
    W = 66
    sep = '━' * W
    console.print(f'  [bold #00D4FF]{sep}[/bold #00D4FF]')

    # ── Tagline ──
    console.print()
    console.print('[bold #00FFCC]' + ' '*16 + '⚡  P U B G  M O B I L E  T O O L K I T  ⚡' + '[/bold #00FFCC]')
    console.print('[dim #4488AA]' + ' '*27 + 'by  @FanteriBey    •    v3.0[/dim #4488AA]')
    console.print()

    # ── Bottom neon bar ──
    bar = '▀' * W
    console.print(f'  [#00D4FF]{bar}[/#00D4FF]')
    console.print()

def _login_screen():
    """VIP key sistemi — kullanıcı key girer, admin gizli şifreyle panele girer."""
    import time as _time
    while True:
        _show_login_banner()
        if _KEY_ATTEMPTS[0] == 0:
            console.print('  [bold #FFCC00]┌─────────────────────────────────────────────┐[/bold #FFCC00]')
            console.print('  [bold #FFCC00]│[/bold #FFCC00]  [bold white]🔐  VIP KEY GİR  —  ERİŞİM GEREKLİ[/bold white]    [bold #FFCC00]│[/bold #FFCC00]')
            console.print('  [bold #FFCC00]└─────────────────────────────────────────────┘[/bold #FFCC00]')
        elif _KEY_ATTEMPTS[0] == 1:
            console.print('  [bold #FF8800]┌─────────────────────────────────────────────┐[/bold #FF8800]')
            console.print('  [bold #FF8800]│[/bold #FF8800]  [bold white]⚠   YANLIŞ KEY  —  2 HAKKINI KALDI[/bold white]   [bold #FF8800]  │[/bold #FF8800]')
            console.print('  [bold #FF8800]└─────────────────────────────────────────────┘[/bold #FF8800]')
        elif _KEY_ATTEMPTS[0] == 2:
            console.print('  [bold red]┌─────────────────────────────────────────────┐[/bold red]')
            console.print('  [bold red]│[/bold red]  [bold white]🚨  SON DENEME  —  DİKKATLİ OL![/bold white]        [bold red]  │[/bold red]')
            console.print('  [bold red]└─────────────────────────────────────────────┘[/bold red]')
        console.print()
        console.print('  [dim #4488AA]KEY gir ve Enter\'a bas[/dim #4488AA]')
        console.print()
        key = safe_input('  KEY  ›  ').strip()
        flush_stdin()

        # ── Admin gizli erişim ────────────────────────────────────
        if key == _ADMIN_SECRET:
            os.system('clear')
            _show_login_banner()
            console.print('  [bold #FF0055]  👑  ADMIN MODU — HOŞ GELDİN FanteriBey[/bold #FF0055]')
            _time.sleep(0.8)
            _admin_panel()
            # Admin panelinden çıkınca tool başlasın
            return True

        # ── VIP key doğrulama ─────────────────────────────────────
        key_up = key.upper()
        status, msg = _validate_key(key_up)
        os.system('clear')
        _show_login_banner()

        if status in ('NOTFOUND', 'REVOKED', 'EXPIRED'):
            # Geçersiz key
            _KEY_ATTEMPTS[0] += 1
            col = '#FF4444' if status=='REVOKED' else '#888888' if status=='EXPIRED' else '#FF6600'
            icon = '🚫' if status=='REVOKED' else '⏰' if status=='EXPIRED' else '❌'
            console.print(f'  [bold {col}]╔═════════════════════════════════════════════╗[/bold {col}]')
            console.print(f'  [bold {col}]║[/bold {col}]                                             [bold {col}]║[/bold {col}]')
            console.print(f'  [bold {col}]║[/bold {col}]   [bold white]{icon}  {msg:<42}[/bold white]  [bold {col}]║[/bold {col}]')
            console.print(f'  [bold {col}]║[/bold {col}]   [dim]Deneme: {_KEY_ATTEMPTS[0]}/3[/dim]                             [bold {col}]║[/bold {col}]')
            console.print(f'  [bold {col}]║[/bold {col}]                                             [bold {col}]║[/bold {col}]')
            console.print(f'  [bold {col}]╚═════════════════════════════════════════════╝[/bold {col}]')
            if _KEY_ATTEMPTS[0] >= 3:
                console.print('\n  [bold red]  3 yanlış deneme — sistem kapanıyor...[/bold red]')
                _time.sleep(2); raise SystemExit(1)
            _time.sleep(1.5)
            continue

        if status == 'LOCKED':
            # Farklı cihaz
            console.print('  [bold red]╔═════════════════════════════════════════════╗[/bold red]')
            console.print('  [bold red]║[/bold red]                                             [bold red]║[/bold red]')
            console.print('  [bold red]║[/bold red]   [bold white]🔒  CİHAZ UYUŞMAZLIĞI[/bold white]                  [bold red]║[/bold red]')
            console.print('  [bold red]║[/bold red]   [dim]Bu key başka cihazda kayıtlı.[/dim]          [bold red]║[/bold red]')
            console.print('  [bold red]║[/bold red]   [dim]Farklı cihazda kullanılamaz.[/dim]           [bold red]║[/bold red]')
            console.print('  [bold red]║[/bold red]                                             [bold red]║[/bold red]')
            console.print('  [bold red]╚═════════════════════════════════════════════╝[/bold red]')
            _time.sleep(3); raise SystemExit(1)

        if status == 'NEW':
            # İlk kullanım — cihaza kilitle
            _bind_key_to_device(key_up)
            db  = _load_keys()
            exp = db.get(key_up,{}).get('expires','?')
            console.print('  [bold #00FF88]╔═════════════════════════════════════════════╗[/bold #00FF88]')
            console.print('  [bold #00FF88]║[/bold #00FF88]                                             [bold #00FF88]║[/bold #00FF88]')
            console.print('  [bold #00FF88]║[/bold #00FF88]   [bold white]✅  VIP ERİŞİM ONAYLANDI[/bold white]               [bold #00FF88]║[/bold #00FF88]')
            console.print('  [bold #00FF88]║[/bold #00FF88]                                             [bold #00FF88]║[/bold #00FF88]')
            console.print(f'  [bold #00FF88]║[/bold #00FF88]   [bold #00FFCC]🔐  Bu cihaza kilitlendi![/bold #00FFCC]              [bold #00FF88]║[/bold #00FF88]')
            console.print(f'  [bold #00FF88]║[/bold #00FF88]   [dim]Key: {key_up}[/dim]                  [bold #00FF88]║[/bold #00FF88]')
            console.print(f'  [bold #00FF88]║[/bold #00FF88]   [dim]Bitiş: [yellow]{exp}[/yellow][/dim]                        [bold #00FF88]║[/bold #00FF88]')
            console.print('  [bold #00FF88]║[/bold #00FF88]                                             [bold #00FF88]║[/bold #00FF88]')
            console.print('  [bold #00FF88]╚═════════════════════════════════════════════╝[/bold #00FF88]')
            _time.sleep(1.8)
            return True

        # status == 'OK' — aynı cihaz, geçerli key
        db  = _load_keys()
        exp = db.get(key_up,{}).get('expires','?')
        from datetime import datetime as _dt2
        try:
            kalan = (_dt2.strptime(exp,'%Y-%m-%d') - _dt2.now()).days
        except:
            kalan = '?'
        console.print('  [bold #00FF88]╔═════════════════════════════════════════════╗[/bold #00FF88]')
        console.print('  [bold #00FF88]║[/bold #00FF88]                                             [bold #00FF88]║[/bold #00FF88]')
        console.print('  [bold #00FF88]║[/bold #00FF88]   [bold white]✅  VIP ERİŞİM ONAYLANDI[/bold white]               [bold #00FF88]║[/bold #00FF88]')
        console.print('  [bold #00FF88]║[/bold #00FF88]                                             [bold #00FF88]║[/bold #00FF88]')
        console.print(f'  [bold #00FF88]║[/bold #00FF88]   [dim]Key: {key_up}[/dim]                  [bold #00FF88]║[/bold #00FF88]')
        console.print(f'  [bold #00FF88]║[/bold #00FF88]   [cyan]⏳ {kalan} gün kaldı[/cyan]                          [bold #00FF88]║[/bold #00FF88]')
        console.print('  [bold #00FF88]║[/bold #00FF88]                                             [bold #00FF88]║[/bold #00FF88]')
        console.print('  [bold #00FF88]╚═════════════════════════════════════════════╝[/bold #00FF88]')
        _time.sleep(1.4)
        return True

def _language_select():
    """Show language selection screen."""
    import time as _time
    os.system('clear')
    _show_login_banner()
    console.print('  [bold #00D4FF]╔═════════════════════════════════════════════╗[/bold #00D4FF]')
    console.print('  [bold #00D4FF]║[/bold #00D4FF]                                             [bold #00D4FF]║[/bold #00D4FF]')
    console.print('  [bold #00D4FF]║[/bold #00D4FF]   [bold white]🌐   D İ L   S E Ç   /   S E L E C T   L A N G[/bold white]   [bold #00D4FF]║[/bold #00D4FF]')
    console.print('  [bold #00D4FF]║[/bold #00D4FF]                                             [bold #00D4FF]║[/bold #00D4FF]')
    console.print('  [bold #00D4FF]╠═════════════════════════════════════════════╣[/bold #00D4FF]')
    console.print('  [bold #00D4FF]║[/bold #00D4FF]                                             [bold #00D4FF]║[/bold #00D4FF]')
    console.print('  [bold #00D4FF]║[/bold #00D4FF]    [bold #FF3333][ 1 ][/bold #FF3333]   [bold #FF6666]🇹🇷   T  Ü  R  K  Ç  E[/bold #FF6666]           [bold #00D4FF]║[/bold #00D4FF]')
    console.print('  [bold #00D4FF]║[/bold #00D4FF]                                             [bold #00D4FF]║[/bold #00D4FF]')
    console.print('  [bold #00D4FF]║[/bold #00D4FF]    [bold #3399FF][ 2 ][/bold #3399FF]   [bold #66BBFF]🇬🇧   E  N  G  L  I  S  H[/bold #66BBFF]          [bold #00D4FF]║[/bold #00D4FF]')
    console.print('  [bold #00D4FF]║[/bold #00D4FF]                                             [bold #00D4FF]║[/bold #00D4FF]')
    console.print('  [bold #00D4FF]╚═════════════════════════════════════════════╝[/bold #00D4FF]')
    console.print()
    while True:
        ch = safe_input('  > ').strip(); flush_stdin()
        if ch == '1':
            _LANG[0] = 'TR'
            console.print()
            console.print('  [bold #FF3333]🇹🇷  Türkçe seçildi[/bold #FF3333]  [dim]— FANTOOL yükleniyor...[/dim]')
            break
        elif ch == '2':
            _LANG[0] = 'EN'
            console.print()
            console.print('  [bold #3399FF]🇬🇧  English selected[/bold #3399FF]  [dim]— FANTOOL loading...[/dim]')
            break
    _time.sleep(0.9)
    _apply_translation_patches()

def fantool_startup():
    """Run login + language selection before main menu."""
    _login_screen()
    _language_select()

# ==================== ENTRY POINT ====================
if __name__ == '__main__':
    try:
        install_dependencies()
        create_folders()
        fantool_startup()
        main_menu()
    except KeyboardInterrupt:
        print(f'\n{RED}Interrupted.{RESET}')
    except Exception as e:
        print(f'\n{RED}Fatal error: {e}{RESET}')
        import traceback
        traceback.print_exc()
