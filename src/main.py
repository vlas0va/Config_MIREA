import csv
import sys
import os
import re
import tarfile
import zipfile
import tempfile
import urllib.request
from pathlib import Path


def load_config(config_path: str) -> dict:
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = {}
    with open(config_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row_num, row in enumerate(reader, start=1):
            if len(row) != 2:
                raise ValueError(f"Invalid config format at line {row_num}")
            key, value = row[0].strip(), row[1].strip()
            if not key:
                raise ValueError(f"Empty key at line {row_num}")
            config[key] = value
    return config


def validate_config(config: dict) -> None:
    required_keys = {
        'package_name', 'repository_url', 'repo_mode',
        'output_image', 'ascii_tree_mode'
    }
    if not required_keys.issubset(config.keys()):
        missing = required_keys - config.keys()
        raise KeyError(f"Missing config keys: {missing}")

    if not config['package_name'].replace('_', '').replace('-', '').isalnum():
        raise ValueError("Invalid package_name")

    repo_mode = config['repo_mode']
    repo_url = config['repository_url']

    if repo_mode == 'url':
        if not repo_url.startswith(('http://', 'https://')):
            raise ValueError("repository_url must be a valid HTTP/HTTPS URL when repo_mode is 'url'")
    elif repo_mode == 'file':
        if not repo_url:
            raise ValueError("repository_url cannot be empty when repo_mode is 'file'")
    else:
        raise ValueError("repo_mode must be 'url' or 'file'")

    if not config['output_image'].endswith(('.png', '.svg', '.pdf')):
        raise ValueError("output_image must be .png/.svg/.pdf")
    if config['ascii_tree_mode'].lower() not in ('true', 'false'):
        raise ValueError("ascii_tree_mode must be 'true' or 'false'")


def extract_dependencies_from_setup_py(content: str) -> list:
    match = re.search(r'install_requires\s*=\s*(\[.*?\])', content, re.DOTALL)
    if not match:
        return []
    try:
        deps_str = match.group(1)
        deps = []
        for line in deps_str.strip('[]').split(','):
            line = line.strip().strip('\'"')
            if line and not line.startswith('#'):
                dep_name = re.split(r'[<>=!~]', line, maxsplit=1)[0].strip()
                if dep_name:
                    deps.append(dep_name)
        return deps
    except Exception:
        return []


def extract_dependencies_from_setup_cfg(content: str) -> list:
    import configparser
    cfg = configparser.ConfigParser()
    cfg.read_string(content)
    if 'options' in cfg and 'install_requires' in cfg['options']:
        raw = cfg['options']['install_requires']
        deps = [line.strip() for line in raw.split('\n') if line.strip()]
        result = []
        for d in deps:
            name = re.split(r'[<>=!~]', d, maxsplit=1)[0].strip()
            if name:
                result.append(name)
        return result
    return []


def extract_dependencies_from_pyproject(content: str) -> list:
    in_deps = False
    deps = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('dependencies') and '=' in line:
            in_deps = True
            value_part = line.split('=', 1)[1].strip()
            if value_part.startswith('[') and value_part.endswith(']'):
                items = value_part.strip('[]').split(',')
                for item in items:
                    item = item.strip().strip('\'"')
                    if item:
                        name = re.split(r'[<>=!~]', item, maxsplit=1)[0]
                        deps.append(name)
            continue
        if in_deps and line.startswith(']'):
            break
        if in_deps and line and not line.startswith('#'):
            item = line.strip(' ,\'"')
            if item:
                name = re.split(r'[<>=!~]', item, maxsplit=1)[0]
                deps.append(name)
    return deps


def fetch_and_extract_package(url_or_path: str, repo_mode: str, temp_dir: str) -> Path:
    archive_path = None
    if repo_mode == 'url':
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                urllib.request.urlretrieve(url_or_path, tmp.name)
                archive_path = tmp.name
        except Exception as e:
            raise RuntimeError(f"Failed to download package: {e}")
    else:
        if not os.path.isfile(url_or_path):
            raise FileNotFoundError(f"Package file not found: {url_or_path}")
        archive_path = url_or_path

    extracted_dir = Path(temp_dir) / "extracted"
    extracted_dir.mkdir()

    if tarfile.is_tarfile(archive_path):
        with tarfile.open(archive_path) as tar:
            tar.extractall(path=extracted_dir)
    elif zipfile.is_zipfile(archive_path):
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(path=extracted_dir)
    else:
        raise ValueError("Unsupported archive format. Expected .tar.gz or .zip")

    contents = list(extracted_dir.iterdir())
    if len(contents) == 1 and contents[0].is_dir():
        return contents[0]
    return extracted_dir


def find_and_parse_deps(package_root: Path) -> list:
    deps = []

    setup_py = package_root / "setup.py"
    if setup_py.exists():
        with open(setup_py, 'r', encoding='utf-8', errors='ignore') as f:
            deps = extract_dependencies_from_setup_py(f.read())
        return deps

    setup_cfg = package_root / "setup.cfg"
    if setup_cfg.exists():
        with open(setup_cfg, 'r', encoding='utf-8', errors='ignore') as f:
            deps = extract_dependencies_from_setup_cfg(f.read())
        return deps

    pyproject = package_root / "pyproject.toml"
    if pyproject.exists():
        with open(pyproject, 'r', encoding='utf-8', errors='ignore') as f:
            deps = extract_dependencies_from_pyproject(f.read())
        return deps

    return []


def main():
    config_path = 'config.csv'
    try:
        config = load_config(config_path)
        validate_config(config)

        # Этап 1: вывод параметров
        print("Config parameters:")
        for key, value in config.items():
            print(f"{key}: {value}")

        # Этап 2: сбор зависимостей
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = fetch_and_extract_package(
                config['repository_url'],
                config['repo_mode'],
                tmpdir
            )
            dependencies = find_and_parse_deps(package_dir)

        print("\nDirect dependencies:")
        if dependencies:
            for dep in sorted(set(dependencies)):
                print(dep)
        else:
            print("(none)")

    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()