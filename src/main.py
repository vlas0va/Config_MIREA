import csv
import sys
import os


def load_config(config_path: str) -> dict:
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    config = {}
    with open(config_path, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row_num, row in enumerate(reader, start=1):
            if len(row) != 2:
                raise ValueError(f"Invalid config format at line {row_num}: expected 2 columns, got {len(row)}")
            key, value = row[0].strip(), row[1].strip()
            if not key:
                raise ValueError(f"Empty key at line {row_num}")
            config[key] = value

    return config


def validate_config(config: dict):
    required_keys = {
        'package_name': str,
        'repository_url': str,
        'repo_mode': str,
        'output_image': str,
        'ascii_tree_mode': str,
    }

    for key, expected_type in required_keys.items():
        if key not in config:
            raise KeyError(f"Missing required config key: '{key}'")

    # Validate package_name
    if not config['package_name'] or not config['package_name'].replace('_', '').replace('-', '').isalnum():
        raise ValueError("Invalid package_name: must be non-empty and alphanumeric with optional '-' or '_'")

    # Validate repository_url
    url = config['repository_url']
    if not url.startswith(('http://', 'https://', '/')):
        raise ValueError("repository_url must be an absolute URL or absolute/relative file path")

    # Validate repo_mode
    if config['repo_mode'] not in ('url', 'file'):
        raise ValueError("repo_mode must be 'url' or 'file'")

    # Validate output_image
    if not config['output_image'].endswith(('.png', '.svg', '.pdf')):
        raise ValueError("output_image must have extension .png, .svg, or .pdf")

    # Validate ascii_tree_mode
    if config['ascii_tree_mode'].lower() not in ('true', 'false'):
        raise ValueError("ascii_tree_mode must be 'true' or 'false'")


def main():
    config_path = 'config.csv'
    try:
        config = load_config(config_path)
        validate_config(config)

        print("Config parameters:")
        for key, value in config.items():
            print(f"{key}: {value}")

    except (FileNotFoundError, ValueError, KeyError) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()