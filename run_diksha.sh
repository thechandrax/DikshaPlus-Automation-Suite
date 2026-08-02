#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# DIKSHA+ DIRECT INSTANT LAUNCHER FOR TERMUX (0 Installs, Instant Execution)
# Run: ./run_diksha.sh
# ==============================================================================

export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
export PLAYWRIGHT_BROWSERS_PATH=0
export PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(which chromium)
export PLAYWRIGHT_NODEJS_PATH=$(which node)
export HEADLESS=True

# Auto-install Playwright ARM64 for Termux if missing
python -c "import playwright" 2>/dev/null || {
    echo "📦 Installing Playwright ARM64 wheel into Termux site-packages..."
    SP_PATH=$(python -c "import site; print(site.getsitepackages()[0])")
    pip install --no-deps --platform manylinux2014_aarch64 --only-binary=:all: --target "$SP_PATH" playwright
}

# Auto-patch coreBundle.js to bypass 'Unsupported platform: android' & fix calculateHostPlatform
python -c "
import sys
from pathlib import Path
for sp in sys.path:
    cb = Path(sp) / 'playwright' / 'driver' / 'package' / 'lib' / 'coreBundle.js'
    if cb.exists():
        t = cb.read_text(encoding='utf-8', errors='ignore')
        t = t.replace('function calculateHostPlatform(){', 'function calculateHostPlatform(){if(process.platform===\"android\")return\"linux-arm64\";')
        t = t.replace('throw new Error(\"Unsupported platform: \" + process.platform);', '/* patched android */')
        t = t.replace('throw new Error(\`Unsupported platform: \${process.platform}\`);', '/* patched android */')
        t = t.replace('throw new Error(\"Unsupported platform: \"', 'console.warn(\"Termux Android platform bypass: \"')
        t = t.replace('path.join(hostPlatform', 'path.join(hostPlatform || \"linux-arm64\"')
        t = t.replace('path.join(hostPlatform,', 'path.join(hostPlatform || \"linux-arm64\",')
        cb.write_text(t, encoding='utf-8')
" 2>/dev/null || true




echo "========================================================================"
echo " ⚡ LAUNCHING DIKSHA+ AUTOMATION SUITE"
echo "========================================================================"
echo ""

python main.py
