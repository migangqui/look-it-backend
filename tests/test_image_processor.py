"""
Tests for image_processor module
"""

import pytest
from io import BytesIO
from PIL import Image
from unittest.mock import Mock, patch, MagicMock

# Mock ConfigService before importing anything that uses it
mock_config = Mock()
mock_config.get.return_value = "mock_value"

with patch('app.core.config_service.ConfigService', return_value=mock_config):
    from app.core.image_processor import resize_image, process_image
    from app.settings import azure_cv_client


class TestResizeImage:
    """Test cases for resize_image function"""
    
    def create_test_image(self, width: int, height: int, format: str = 'PNG') -> bytes:
        """Helper function to create a test image"""
        img = Image.new('RGB', (width, height), color='red')
        output = BytesIO()
        img.save(output, format=format)
        output.seek(0)
        return output.getvalue()
    
    def test_resize_image_smaller_than_max_size(self):
        """Test that images smaller than max_size are not resized"""
        # Create a 500x500 image
        image_bytes = self.create_test_image(500, 500)
        
        result = resize_image(image_bytes, max_size=1024)
        
        # Should return original (or very similar size)
        assert len(result) > 0
        result_img = Image.open(BytesIO(result))
        assert result_img.size == (500, 500)
    
    def test_resize_image_larger_than_max_size(self):
        """Test that images larger than max_size are resized"""
        # Create a 2000x2000 image
        image_bytes = self.create_test_image(2000, 2000)
        
        result = resize_image(image_bytes, max_size=1024)
        
        # Should be resized to max 1024x1024
        result_img = Image.open(BytesIO(result))
        assert result_img.size[0] <= 1024
        assert result_img.size[1] <= 1024
        assert result_img.size[0] == result_img.size[1]  # Square maintained
    
    def test_resize_image_maintains_aspect_ratio_landscape(self):
        """Test that landscape images maintain aspect ratio"""
        # Create a 2000x1000 landscape image
        image_bytes = self.create_test_image(2000, 1000)
        
        result = resize_image(image_bytes, max_size=1024)
        
        result_img = Image.open(BytesIO(result))
        # Should maintain 2:1 aspect ratio
        assert result_img.size[0] == 1024
        assert result_img.size[1] == 512
        assert result_img.size[0] / result_img.size[1] == 2.0
    
    def test_resize_image_maintains_aspect_ratio_portrait(self):
        """Test that portrait images maintain aspect ratio"""
        # Create a 1000x2000 portrait image
        image_bytes = self.create_test_image(1000, 2000)
        
        result = resize_image(image_bytes, max_size=1024)
        
        result_img = Image.open(BytesIO(result))
        # Should maintain 1:2 aspect ratio
        assert result_img.size[0] == 512
        assert result_img.size[1] == 1024
        assert result_img.size[1] / result_img.size[0] == 2.0
    
    def test_resize_image_invalid_bytes(self):
        """Test that invalid image bytes raise an exception"""
        invalid_bytes = b"not an image"
        
        with pytest.raises(Exception) as exc_info:
            resize_image(invalid_bytes)
        
        assert "Error resizing image" in str(exc_info.value)
    
    def test_resize_image_empty_bytes(self):
        """Test that empty bytes raise an exception"""
        empty_bytes = b""
        
        with pytest.raises(Exception) as exc_info:
            resize_image(empty_bytes)
        
        assert "Error resizing image" in str(exc_info.value)


class TestProcessImage:
    """Test cases for process_image function"""
    
    def create_test_image(self, width: int = 500, height: int = 500) -> bytes:
        """Helper function to create a test image"""
        img = Image.new('RGB', (width, height), color='blue')
        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)
        return output.getvalue()
    
    def create_mock_azure_tags(self, tags_data: list):
        """Helper to create mock Azure CV tags"""
        class MockTag:
            def __init__(self, name, confidence):
                self.name = name
                self.confidence = confidence
        
        class MockTagsResult:
            def __init__(self, tags):
                self.tags = [MockTag(name, conf) for name, conf in tags]
        
        return MockTagsResult(tags_data)
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_success(self, mock_remove, mock_azure_client):
        """Test successful image processing"""
        # Setup
        image_bytes = self.create_test_image()
        processed_bytes = b"processed_image_data"
        
        # Mock rembg
        mock_remove.return_value = processed_bytes
        
        # Mock Azure CV
        mock_tags_result = self.create_mock_azure_tags([
            ('shirt', 0.95),
            ('clothing', 0.90),
            ('blue', 0.85),
            ('casual', 0.80)
        ])
        mock_azure_client.tag_image_in_stream.return_value = mock_tags_result
        
        # Execute
        result = process_image(image_bytes)
        
        # Assert
        assert result['processed_image_bytes'] == processed_bytes
        assert result['type'] == 'shirt'
        assert result['color'] == 'blue'
        assert 'clothing' not in result['tags']
        assert 'shirt' in result['tags']
        assert 'blue' in result['tags']
        
        # Verify calls
        mock_remove.assert_called_once()
        mock_azure_client.tag_image_in_stream.assert_called_once()
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_filters_clothing_tag(self, mock_remove, mock_azure_client):
        """Test that 'clothing' tag is filtered out"""
        # Setup
        image_bytes = self.create_test_image()
        processed_bytes = b"processed_image_data"
        
        mock_remove.return_value = processed_bytes
        
        # Mock Azure CV with 'clothing' as first tag
        mock_tags_result = self.create_mock_azure_tags([
            ('clothing', 0.95),
            ('pants', 0.90),
            ('black', 0.85)
        ])
        mock_azure_client.tag_image_in_stream.return_value = mock_tags_result
        
        # Execute
        result = process_image(image_bytes)
        
        # Assert
        assert result['type'] == 'pants'  # Should skip 'clothing'
        assert 'clothing' not in result['tags']
        assert 'pants' in result['tags']
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_no_color_detected(self, mock_remove, mock_azure_client):
        """Test processing when no color is detected"""
        # Setup
        image_bytes = self.create_test_image()
        processed_bytes = b"processed_image_data"
        
        mock_remove.return_value = processed_bytes
        
        # Mock Azure CV without color tags
        mock_tags_result = self.create_mock_azure_tags([
            ('jacket', 0.95),
            ('outerwear', 0.90),
            ('casual', 0.85)
        ])
        mock_azure_client.tag_image_in_stream.return_value = mock_tags_result
        
        # Execute
        result = process_image(image_bytes)
        
        # Assert
        assert result['type'] == 'jacket'
        assert result['color'] is None
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_empty_bytes(self, mock_remove, mock_azure_client):
        """Test that empty bytes raise ValueError"""
        empty_bytes = b""
        
        with pytest.raises(ValueError) as exc_info:
            process_image(empty_bytes)
        
        assert "Image bytes cannot be empty" in str(exc_info.value)
        mock_remove.assert_not_called()
        mock_azure_client.tag_image_in_stream.assert_not_called()
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_rembg_failure(self, mock_remove, mock_azure_client):
        """Test handling of rembg processing failure"""
        # Setup
        image_bytes = self.create_test_image()
        
        # Mock rembg to raise exception
        mock_remove.side_effect = Exception("rembg processing failed")
        
        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            process_image(image_bytes)
        
        assert "Error processing image with rembg" in str(exc_info.value)
        mock_azure_client.tag_image_in_stream.assert_not_called()
    
    @patch('app.core.image_processor.remove')
    def test_process_image_azure_client_not_initialized(self, mock_remove):
        """Test handling when Azure CV client is not initialized"""
        # Setup
        image_bytes = self.create_test_image()
        processed_bytes = b"processed_image_data"
        
        mock_remove.return_value = processed_bytes
        
        # Patch azure_cv_client to be None
        with patch('app.core.image_processor.azure_cv_client', None):
            with pytest.raises(Exception) as exc_info:
                process_image(image_bytes)
            
            assert "Azure Computer Vision client is not initialized" in str(exc_info.value)
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_azure_cv_failure(self, mock_remove, mock_azure_client):
        """Test handling of Azure CV API failure"""
        # Setup
        image_bytes = self.create_test_image()
        processed_bytes = b"processed_image_data"
        
        mock_remove.return_value = processed_bytes
        mock_azure_client.tag_image_in_stream.side_effect = Exception("Azure API error")
        
        # Execute & Assert
        with pytest.raises(Exception) as exc_info:
            process_image(image_bytes)
        
        assert "Error classifying image with Azure Computer Vision" in str(exc_info.value)
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_no_tags_from_azure(self, mock_remove, mock_azure_client):
        """Test handling when Azure CV returns no tags"""
        # Setup
        image_bytes = self.create_test_image()
        processed_bytes = b"processed_image_data"
        
        mock_remove.return_value = processed_bytes
        
        # Mock Azure CV with no tags
        mock_tags_result = self.create_mock_azure_tags([])
        mock_azure_client.tag_image_in_stream.return_value = mock_tags_result
        
        # Execute & Assert
        # Note: ValueError is caught and re-raised as Exception in the code
        with pytest.raises(Exception) as exc_info:
            process_image(image_bytes)
        
        assert "Could not classify garment type from Azure Computer Vision" in str(exc_info.value)
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_only_clothing_tag(self, mock_remove, mock_azure_client):
        """Test handling when only 'clothing' tag is returned"""
        # Setup
        image_bytes = self.create_test_image()
        processed_bytes = b"processed_image_data"
        
        mock_remove.return_value = processed_bytes
        
        # Mock Azure CV with only 'clothing' tag
        mock_tags_result = self.create_mock_azure_tags([
            ('clothing', 0.95)
        ])
        mock_azure_client.tag_image_in_stream.return_value = mock_tags_result
        
        # Execute & Assert
        # Note: ValueError is caught and re-raised as Exception in the code
        with pytest.raises(Exception) as exc_info:
            process_image(image_bytes)
        
        assert "Could not classify garment type from Azure Computer Vision" in str(exc_info.value)
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_rembg_empty_result(self, mock_remove, mock_azure_client):
        """Test handling when rembg returns empty result"""
        # Setup
        image_bytes = self.create_test_image()
        
        mock_remove.return_value = b""
        
        # Execute & Assert
        with pytest.raises(ValueError) as exc_info:
            process_image(image_bytes)
        
        assert "rembg processing did not produce valid results" in str(exc_info.value)
        mock_azure_client.tag_image_in_stream.assert_not_called()
    
    @patch('app.core.image_processor.azure_cv_client')
    @patch('app.core.image_processor.remove')
    def test_process_image_different_color_keywords(self, mock_remove, mock_azure_client):
        """Test color detection with different color keywords"""
        # Setup
        image_bytes = self.create_test_image()
        processed_bytes = b"processed_image_data"
        
        mock_remove.return_value = processed_bytes
        
        # Test different colors
        color_tests = [
            ('red', 'red'),
            ('blue', 'blue'),
            ('green', 'green'),
            ('yellow', 'yellow'),
            ('black', 'black'),
            ('white', 'white'),
            ('gray', 'gray'),
            ('grey', 'grey'),
            ('brown', 'brown'),
            ('pink', 'pink'),
            ('purple', 'purple'),
            ('orange', 'orange'),
        ]
        
        for color_tag, expected_color in color_tests:
            mock_tags_result = self.create_mock_azure_tags([
                ('shirt', 0.95),
                (color_tag, 0.90)
            ])
            mock_azure_client.tag_image_in_stream.return_value = mock_tags_result
            
            result = process_image(image_bytes)
            assert result['color'] == color_tag, f"Failed for color: {color_tag}"

