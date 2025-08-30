# GravityCommit - File Documentation

This document provides a comprehensive explanation of every file in the GravityCommit project, including their purpose, main functions/classes, and connections to other files.

## Project Overview

GravityCommit is an automatic commit package for Python projects that monitors project activity and commits changes at specified intervals when the project is open in an editor.

## Root Level Files

### `setup.py`
**Purpose**: Package configuration and installation setup for the GravityCommit package.

**Main Functions**:
- Defines package metadata (name, version, author, description)
- Specifies dependencies (gitpython, schedule, psutil, click)
- Configures entry points for CLI command `autocommit`
- Sets up package discovery and installation

**Connections**:
- Reads `README.md` for long description
- References `autocommit/` package directory
- Creates console script entry point to `autocommit.cli:main`

### `README.md`
**Purpose**: Comprehensive documentation and user guide for the GravityCommit package.

**Content**:
- Installation instructions
- Usage examples for all CLI commands
- Feature descriptions
- System requirements
- Troubleshooting guide
- Development information

**Connections**:
- Referenced by `setup.py` for package description
- Contains usage examples that reference CLI commands in `autocommit/cli.py`

### `LICENSE`
**Purpose**: MIT License file defining the legal terms for using and distributing the software.

**Content**:
- Standard MIT License text
- Copyright notice for Shakour
- Permission grants and limitations

**Connections**:
- Referenced in `README.md` license section
- Required for package distribution

### `TODO.md`
**Purpose**: Development roadmap and task tracking for the GravityCommit project.

**Content**:
- Organized by phases (Package Structure, Core Components, CLI, Service Management, Testing, Documentation)
- Checkboxes for completed and pending tasks
- Progress tracking

**Connections**:
- Internal development file, no external connections
- Tracks implementation status of components in `autocommit/` package

## `autocommit/` Package Directory

### `autocommit/__init__.py`
**Purpose**: Package initialization and public API definition for the autocommit module.

**Main Functions**:
- Defines package version and author
- Imports all core classes for public use
- Defines `__all__` list for controlled imports

**Connections**:
- Imports from all core modules (`config_manager.py`, `commit_generator.py`, etc.)
- Serves as entry point for `from autocommit import ConfigManager` style imports
- Referenced by `setup.py` for package discovery

### `autocommit/cli.py`
**Purpose**: Command Line Interface implementation providing user commands for GravityCommit.

**Main Functions**:
- `cli()`: Main CLI group using Click framework
- `setup()`: Command to configure auto-commits for a project
- `remove()`: Command to remove auto-commit configuration
- `status()`: Command to check current status
- `daemon()`: Internal command to run the background service

**Connections**:
- Entry point defined in `setup.py` as `autocommit=autocommit.cli:main`
- Uses all core modules: `ConfigManager`, `DaemonManager`, `ProjectMonitor`, `GitOperations`, `CommitGenerator`, `Scheduler`
- Called by users through terminal commands

### `autocommit/config_manager.py`
**Purpose**: Manages configuration settings for GravityCommit projects.

**Main Classes**:
- `ConfigManager`: Handles project-specific configuration

**Main Functions**:
- `set_interval()`: Sets commit interval in minutes
- `get_interval()`: Retrieves current interval (default: 10 minutes)
- `remove_config()`: Deletes configuration file
- `_load_config()`: Loads settings from `.autocommit` file
- `_save_config()`: Saves settings to `.autocommit` file

**Connections**:
- Used by `cli.py` in setup and status commands
- Configuration file stored in project root as `.autocommit`
- Provides settings to `Scheduler` for timing intervals

### `autocommit/commit_generator.py`
**Purpose**: Generates intelligent commit messages based on file changes.

**Main Classes**:
- `CommitGenerator`: Analyzes changes and creates commit messages

**Main Functions**:
- `generate_commit()`: Main method to create commit message from changes
- `analyze_changes()`: Categorizes changed files (added, modified, deleted)
- `_generate_add_message()`: Creates messages for added files
- `_generate_modify_message()`: Creates messages for modified files
- `_generate_delete_message()`: Creates messages for deleted files
- `_categorize_files()`: Groups files by extension type

**Connections**:
- Used by `cli.py` daemon command during commit process
- Receives staged files list from `GitOperations.stage_changes()`
- Provides commit message to `GitOperations.commit()`

### `autocommit/git_operations.py`
**Purpose**: Handles all Git repository operations and status checking.

**Main Classes**:
- `GitOperations`: Interface to Git repository operations

**Main Functions**:
- `__init__()`: Initializes Git repository connection
- `stage_changes()`: Stages all changes and returns staged files
- `commit()`: Commits staged changes with message
- `check_status()`: Returns repository status (staged, unstaged, untracked)
- `has_changes()`: Checks if there are uncommitted changes
- `get_staged_files()`: Returns list of currently staged files

**Connections**:
- Used by `cli.py` daemon command for all Git operations
- Provides change information to `CommitGenerator.analyze_changes()`
- Called by scheduler callback in daemon mode

### `autocommit/scheduler.py`
**Purpose**: Manages timed execution of commit checks at specified intervals.

**Main Classes**:
- `Scheduler`: Handles periodic task execution

**Main Functions**:
- `start()`: Begins scheduled execution with callback function
- `stop()`: Stops scheduled execution
- `set_interval()`: Updates execution interval
- `_run_scheduler()`: Background thread running schedule loop
- `_run_callback()`: Executes user-provided callback function

**Connections**:
- Used by `cli.py` daemon command to run periodic checks
- Receives interval from `ConfigManager.get_interval()`
- Executes callback that uses `ProjectMonitor`, `GitOperations`, and `CommitGenerator`

### `autocommit/project_monitor.py`
**Purpose**: Monitors system processes to detect when project is open in editors.

**Main Classes**:
- `ProjectMonitor`: Detects editor processes running the project

**Main Functions**:
- `is_project_open()`: Checks if project is currently open in an editor
- `get_editor_processes()`: Returns list of running editor processes
- `_is_editor_process()`: Determines if a process is a supported editor

**Connections**:
- Used by `cli.py` daemon command and status command
- Supports detection of: VS Code, Atom, Sublime, Vim, Emacs, PyCharm, IntelliJ, etc.
- Provides status to scheduler callback to determine if commits should run

### `autocommit/daemon_manager.py`
**Purpose**: Manages system service installation and lifecycle for background operation.

**Main Classes**:
- `DaemonManager`: Handles system service operations

**Main Functions**:
- `install_service()`: Installs system service (Linux systemd/Windows service)
- `uninstall_service()`: Removes system service
- `is_running()`: Checks if service is currently running
- `_install_linux_service()`: Linux-specific systemd installation
- `_generate_systemd_service()`: Creates systemd service file content

**Connections**:
- Used by `cli.py` setup and remove commands
- Creates system service that runs `cli.py` daemon command
- Manages service lifecycle for automatic startup

## `Docs/` Directory

### `Docs/init_doc.md`
**Purpose**: Original design document and requirements specification for GravityCommit.

**Content**:
- Detailed design diagrams (Mermaid format)
- Component architecture
- Process flows for installation and operation
- UML class diagrams
- State diagrams
- Data flow diagrams

**Connections**:
- Served as blueprint for implementing all components
- Contains design specifications that guided development of all modules
- Referenced during development to ensure compliance with original design

## `gravitycommit.egg-info/` Directory (Generated)

### `gravitycommit.egg-info/PKG-INFO`
**Purpose**: Package metadata file generated by setuptools.

**Content**:
- Package information from `setup.py`
- Dependencies and requirements
- Author and version information

**Connections**:
- Generated automatically by `pip install` or `python setup.py develop`
- Used by package managers for installation and dependency resolution

### `gravitycommit.egg-info/entry_points.txt`
**Purpose**: Defines console script entry points.

**Content**:
- `autocommit=autocommit.cli:main`
- Maps command name to Python function

**Connections**:
- Generated from `setup.py` entry_points configuration
- Enables `autocommit` command to be run from terminal

### `gravitycommit.egg-info/requires.txt`
**Purpose**: Lists package dependencies.

**Content**:
- gitpython>=3.1.0
- schedule>=1.1.0
- psutil>=5.8.0
- click>=8.0.0

**Connections**:
- Generated from `setup.py` install_requires
- Used by pip for dependency installation

### `gravitycommit.egg-info/SOURCES.txt`
**Purpose**: Lists all source files in the package.

**Content**:
- Complete file manifest
- setup.py
- autocommit/*.py
- README.md
- LICENSE

**Connections**:
- Generated automatically during package build
- Used for package distribution and installation

### `gravitycommit.egg-info/dependency_links.txt`
**Purpose**: External dependency links (empty in this case).

### `gravitycommit.egg-info/not-zip-safe`
**Purpose**: Indicates package is not safe for zipping (marker file).

### `gravitycommit.egg-info/top_level.txt`
**Purpose**: Lists top-level Python packages.

**Content**:
- autocommit

**Connections**:
- Tells Python where to find the package modules
- Generated from `setup.py` packages configuration

## Data Flow and Component Interactions

### Main User Flow:
1. User runs `autocommit setup project/ --interval 15`
   - `cli.py` → `ConfigManager` (save settings)
   - `cli.py` → `DaemonManager` (install service)

2. System service starts `autocommit daemon project/`
   - `cli.py` → `Scheduler` (start timed execution)
   - `Scheduler` → callback function every 15 minutes

3. Callback execution:
   - `ProjectMonitor.is_project_open()` → check if editors are running
   - `GitOperations.has_changes()` → check for uncommitted changes
   - `GitOperations.stage_changes()` → stage all changes
   - `CommitGenerator.generate_commit()` → create commit message
   - `GitOperations.commit()` → perform commit

### Configuration Flow:
- `ConfigManager` ↔ `.autocommit` file in project root
- Settings loaded by `cli.py` and passed to `Scheduler`

### Service Management Flow:
- `DaemonManager` ↔ system service manager (systemd/Windows Service)
- Service configuration points to `cli.py` daemon command

## Dependencies and External Libraries

- **gitpython**: Used by `GitOperations` for Git repository manipulation
- **schedule**: Used by `Scheduler` for timed task execution
- **psutil**: Used by `ProjectMonitor` for process detection
- **click**: Used by `cli.py` for command-line interface

All dependencies are specified in `setup.py` and installed automatically.

## File Permissions and Execution

- `autocommit/cli.py`: Executable script (shebang `#!/usr/bin/env python3`)
- `setup.py`: Executable for package installation
- Configuration files: Created with appropriate permissions
- System service files: Require elevated permissions for installation

This documentation provides a complete overview of the GravityCommit codebase, showing how each file contributes to the overall functionality and how components interact to provide automatic commit capabilities.
