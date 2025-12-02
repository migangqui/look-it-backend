# Tests

This directory contains unit tests for the application.

## Running Tests

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_image_processor.py
```

### Run specific test class
```bash
pytest tests/test_image_processor.py::TestResizeImage
```

### Run specific test function
```bash
pytest tests/test_image_processor.py::TestProcessImage::test_process_image_success
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

## Test Structure

- `test_image_processor.py`: Tests for image processing functionality including:
  - Image resizing with aspect ratio preservation
  - Background removal with rembg
  - Azure Computer Vision integration
  - Tag filtering and color detection

