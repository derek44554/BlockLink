from importlib import import_module
from pathlib import Path
from types import ModuleType

import yaml
from blocklink.models.routers.route_block_app import RouteApp


APPS_DIR = Path(__file__).resolve().parent / "apps"
MODULE_FILE_NAME = "module.yml"


def find_route_app(module: ModuleType, app_name: str) -> RouteApp:
    preferred_names = ("route_app", "app", f"{app_name}_app")

    for attr_name in preferred_names:
        value = getattr(module, attr_name, None)
        if isinstance(value, RouteApp):
            return value

    route_apps: list[RouteApp] = []
    seen: set[int] = set()

    for value in vars(module).values():
        if isinstance(value, RouteApp) and id(value) not in seen:
            route_apps.append(value)
            seen.add(id(value))

    if len(route_apps) == 1:
        return route_apps[0]

    module_name = module.__name__
    if not route_apps:
        raise RuntimeError(
            f"{module_name} does not expose a RouteApp. "
            f"Define route_app, app, or {app_name}_app in apps/{app_name}/__init__.py."
        )

    raise RuntimeError(
        f"{module_name} exposes multiple RouteApp instances. "
        "Export the one to load as route_app."
    )


def read_module_config(module_dir: Path) -> dict:
    module_file = module_dir / MODULE_FILE_NAME
    with module_file.open("r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    if not isinstance(config, dict):
        raise RuntimeError(f"{module_file} must contain a YAML mapping.")

    return config


def iter_enabled_module_dirs(apps_dir: Path = APPS_DIR) -> list[Path]:
    module_dirs: list[Path] = []

    for module_dir in sorted(apps_dir.iterdir(), key=lambda path: path.name):
        if not module_dir.is_dir():
            continue

        module_file = module_dir / MODULE_FILE_NAME
        if not module_file.exists():
            continue

        config = read_module_config(module_dir)

        if config.get("enabled") is True:
            module_dirs.append(module_dir)

    return module_dirs


def load_apps(apps_dir: Path = APPS_DIR) -> list[RouteApp]:
    route_apps: list[RouteApp] = []

    for module_dir in iter_enabled_module_dirs(apps_dir):
        app_name = module_dir.name
        module = import_module(f"apps.{app_name}")
        route_apps.append(find_route_app(module, app_name))

    return route_apps
