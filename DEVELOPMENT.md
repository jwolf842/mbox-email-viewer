# Development Guide

This guide covers setting up the development environment and building MBOX Email Viewer from source.

## Prerequisites

- Python 3.10 or 3.11 (3.12+ not supported due to PyQt5 compatibility)
- Windows 10 or 11
- Git

## Setting Up Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/jwolf842/mbox-email-viewer.git
cd mbox-email-viewer
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate.bat  # On Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For development, you might also want:
```bash
pip install pytest black flake8  # Testing and code formatting
```

### 4. Run in Development Mode

```bash
python src/main.py
```

## Project Structure

```
mbox-email-viewer/
├── src/
│   ├── main.py              # Application entry point
│   ├── ui/
│   │   ├── __init__.py
│   │   └── main_window.py   # Main window UI (PyQt5)
│   └── core/
│       ├── __init__.py
│       ├── mbox_loader.py   # MBOX file loading
│       ├── email_processor.py # Email parsing and extraction
│       ├── search_engine.py  # Search and filter functionality
│       └── exporter.py      # Export functionality (CSV, Excel, etc.)
├── assets/
│   └── icon.ico            # Application icon
├── tests/                  # Unit tests (if applicable)
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── build scripts...        # Various build automation scripts
```

## Building the Application

### Building the Executable

Using PyInstaller directly:
```bash
pyinstaller --onefile --windowed \
    --name "MBOX Email Viewer" \
    --icon assets\icon.ico \
    --add-data "assets;assets" \
    --hidden-import email.mime.multipart \
    --hidden-import email.mime.text \
    --hidden-import email.mime.base \
    src\main.py
```

Or use the provided build script:
```bash
build_all.bat
```

The executable will be created in the `dist/` folder.

### Creating the Installer

1. Install [Inno Setup](https://jrsoftware.org/isdl.php)
2. Open `installer_setup.iss` in Inno Setup Compiler
3. Build → Compile
4. Installer will be created in `installer_output/`

## Code Style Guidelines

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to all classes and methods
- Keep methods focused and under 50 lines
- Use type hints where it improves clarity

Example:
```python
def process_email(self, email_data: dict) -> tuple[bool, str]:
    """
    Process a single email and extract attachments.
    
    Args:
        email_data: Dictionary containing email information
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Implementation
```

## Testing

Run tests (when implemented):
```bash
pytest tests/
```

Manual testing checklist:
- [ ] Load various MBOX file sizes
- [ ] Test all search combinations
- [ ] Verify all export formats
- [ ] Test attachment extraction
- [ ] Check memory usage with large files

## Common Development Tasks

### Adding a New Export Format

1. Add the export method to `src/core/exporter.py`
2. Add UI button in `src/ui/main_window.py`
3. Connect button to export method
4. Add format to `export_data()` method

### Modifying the UI

- UI is built with PyQt5
- Main window is in `src/ui/main_window.py`
- Follow existing patterns for consistency
- Test on different screen resolutions

### Performance Optimization

For large MBOX files:
- Processing happens in a separate thread
- Use generators where possible
- Consider chunking for very large exports

## Debugging

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **PyQt5 errors**: Check Python version compatibility
3. **Large file issues**: Monitor memory usage, consider streaming

### Debug Mode

Add to `main.py` for verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Release Process

1. Update version in:
   - `installer_setup.iss`
   - `src/main.py` (if version constant exists)
   - `CHANGELOG.md`

2. Run full test suite
3. Build executable: `build_all.bat`
4. Create installer: `create_installer.bat`
5. Test on clean Windows system
6. Create GitHub release

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Commit with clear messages
5. Push and create Pull Request

## Resources

- [PyQt5 Documentation](https://doc.qt.io/qtforpython/)
- [Python Email Package](https://docs.python.org/3/library/email.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)

## License

This project is licensed under the MIT License - see LICENSE file for details.