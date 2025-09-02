import click
import json
from autocommit.config_manager import ConfigManager
from pathlib import Path

@click.group()
def config_cli():
    """Configuration management commands"""
    pass

@config_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('key')
@click.argument('value')
def set(project_path, key, value):
    """Set a configuration value"""
    config = ConfigManager(str(project_path))

    # Try to parse value as appropriate type
    if value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
    elif value.isdigit():
        value = int(value)
    elif value.replace('.', '').isdigit():
        value = float(value)

    # Set the value based on key
    if key == 'interval':
        config.set_interval(int(value))
    elif key == 'manual_override_open':
        config.set_manual_override_open(bool(value))
    elif key == 'additional_editor_processes':
        config.set_additional_editor_processes([v.strip() for v in value.split(',')])
    elif key == 'custom_env_vars':
        config.set_custom_env_vars([v.strip() for v in value.split(',')])
    else:
        click.echo(f"Unknown configuration key: {key}")

    click.echo(f"✓ Configuration {key} set to {value}")

@config_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
def export(project_path, output_file):
    """Export configuration to a file"""
    config = ConfigManager(str(project_path))

    # Read current config
    config_data = {
        'interval': config.get_interval(),
        'manual_override_open': config.get_manual_override_open(),
        'additional_editor_processes': config.get_additional_editor_processes(),
        'custom_env_vars': config.get_custom_env_vars()
    }

    with open(output_file, 'w') as f:
        json.dump(config_data, f, indent=2)

    click.echo(f"✓ Configuration exported to {output_file}")

@config_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.argument('input_file', type=click.Path(exists=True))
def import_config(project_path, input_file):
    """Import configuration from a file"""
    config = ConfigManager(str(project_path))

    with open(input_file, 'r') as f:
        config_data = json.load(f)

    # Apply configuration
    if 'interval' in config_data:
        config.set_interval(config_data['interval'])
    if 'manual_override_open' in config_data:
        config.set_manual_override_open(config_data['manual_override_open'])
    if 'additional_editor_processes' in config_data:
        config.set_additional_editor_processes(config_data['additional_editor_processes'])
    if 'custom_env_vars' in config_data:
        config.set_custom_env_vars(config_data['custom_env_vars'])

    click.echo(f"✓ Configuration imported from {input_file}")

@config_cli.command()
@click.argument('project_path', type=click.Path(exists=True))
def reset(project_path):
    """Reset configuration to defaults"""
    config = ConfigManager(str(project_path))
    config.remove_config()
    click.echo("✓ Configuration reset to defaults")
