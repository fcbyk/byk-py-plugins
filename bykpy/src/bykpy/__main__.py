"""支持 ``python -m bykpy`` 运行。"""

import sys


if __name__ == "__main__":
    # --scan-plugins: Rust 调用的无头模式，仅扫描插件并写缓存，不启动 CLI
    if len(sys.argv) >= 2 and sys.argv[1] == "--scan-plugins":
        from pathlib import Path

        from bykpy.infra.cache import _build_cache
        from bykpy.infra.persistence import write_json

        cache_dir = Path.home() / ".byk" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        data = _build_cache()
        write_json(cache_dir / "app.json", data)
        sys.exit(0)

    from bykpy.app import create_cli

    create_cli()()
