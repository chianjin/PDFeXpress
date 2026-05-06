"""Auto-output helpers unit tests."""
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest

from utils.auto_output_helpers import (
    setup_auto_output_list_to_folder,
    setup_auto_output_list_to_single,
    setup_auto_output_single_to_single,
    setup_auto_output_single_to_folder,
)


class TestSetupAutoOutputListToFolder:
    """Test setup_auto_output_list_to_folder function."""

    def test_default_behavior(self):
        """Test default behavior: output to parent folder of first file."""
        file_list_view = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        first_file_var = Mock()
        first_file_var.get.return_value = '/test/path/document.pdf'
        file_list_view.get_first_file_var.return_value = first_file_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Call function
        setup_auto_output_list_to_folder(file_list_view, output_path_picker)
        
        # Trigger the trace callback
        callback = first_file_var.trace_add.call_args[0][1]
        callback()
        
        # Verify output path is set to parent directory
        expected_path = Path('/test/path')
        output_path_picker.set_path.assert_called_once_with(expected_path)

    def test_custom_path_generator(self):
        """Test custom path generator: output to subfolder."""
        file_list_view = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        first_file_var = Mock()
        first_file_var.get.return_value = '/test/path/document.pdf'
        file_list_view.get_first_file_var.return_value = first_file_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Custom path generator: create subfolder with stem name
        def custom_generator(first_file: Path) -> Path:
            return first_file.parent / first_file.stem
        
        # Call function
        setup_auto_output_list_to_folder(
            file_list_view, 
            output_path_picker, 
            path_generator=custom_generator
        )
        
        # Trigger the trace callback
        callback = first_file_var.trace_add.call_args[0][1]
        callback()
        
        # Verify output path is set to subfolder
        expected_path = Path('/test/path/document')
        output_path_picker.set_path.assert_called_once_with(expected_path)

    def test_auto_output_disabled(self):
        """Test that nothing happens when auto output is disabled."""
        file_list_view = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        first_file_var = Mock()
        file_list_view.get_first_file_var.return_value = first_file_var
        
        output_path_picker.is_auto_output_enabled.return_value = False
        
        # Call function
        setup_auto_output_list_to_folder(file_list_view, output_path_picker)
        
        # Trigger the trace callback
        callback = first_file_var.trace_add.call_args[0][1]
        callback()
        
        # Verify set_path was not called
        output_path_picker.set_path.assert_not_called()

    def test_empty_first_file(self):
        """Test behavior when first file is empty."""
        file_list_view = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        first_file_var = Mock()
        first_file_var.get.return_value = ''
        file_list_view.get_first_file_var.return_value = first_file_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Call function
        setup_auto_output_list_to_folder(file_list_view, output_path_picker)
        
        # Trigger the trace callback
        callback = first_file_var.trace_add.call_args[0][1]
        callback()
        
        # Verify path is cleared
        output_path_picker.path.set.assert_called_once_with('')


class TestSetupAutoOutputListToSingle:
    """Test setup_auto_output_list_to_single function."""

    def test_default_behavior(self):
        """Test default behavior: use original filename."""
        file_list_view = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        first_file_var = Mock()
        first_file_var.get.return_value = '/test/path/document.pdf'
        file_list_view.get_first_file_var.return_value = first_file_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Call function
        setup_auto_output_list_to_single(file_list_view, output_path_picker)
        
        # Trigger the trace callback
        callback = first_file_var.trace_add.call_args[0][1]
        callback()
        
        # Verify output path uses original filename
        expected_path = Path('/test/path/document.pdf')
        output_path_picker.set_path.assert_called_once_with(expected_path)

    def test_custom_name_generator(self):
        """Test custom name generator."""
        file_list_view = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        first_file_var = Mock()
        first_file_var.get.return_value = '/test/path/document.pdf'
        file_list_view.get_first_file_var.return_value = first_file_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Custom name generator
        def custom_name(first_file: Path) -> str:
            return f"{first_file.stem}_merged.pdf"
        
        # Call function
        setup_auto_output_list_to_single(
            file_list_view, 
            output_path_picker, 
            name_generator=custom_name
        )
        
        # Trigger the trace callback
        callback = first_file_var.trace_add.call_args[0][1]
        callback()
        
        # Verify output path uses custom name
        expected_path = Path('/test/path/document_merged.pdf')
        output_path_picker.set_path.assert_called_once_with(expected_path)


class TestSetupAutoOutputSingleToSingle:
    """Test setup_auto_output_single_to_single function."""

    def test_default_behavior(self):
        """Test default behavior: output to parent folder."""
        input_path_picker = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        input_path_var = Mock()
        input_path_var.get.return_value = '/test/path/document.pdf'
        input_path_picker.path = input_path_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Call function
        setup_auto_output_single_to_single(input_path_picker, output_path_picker)
        
        # Trigger the trace callback
        callback = input_path_var.trace_add.call_args[0][1]
        callback()
        
        # Verify output path is set to parent directory
        expected_path = Path('/test/path')
        output_path_picker.set_path.assert_called_once_with(expected_path)

    def test_custom_path_generator(self):
        """Test custom path generator."""
        input_path_picker = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        input_path_var = Mock()
        input_path_var.get.return_value = '/test/path/document.pdf'
        input_path_picker.path = input_path_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Custom path generator
        def custom_generator(input_path: Path) -> Path:
            return input_path.parent / f"{input_path.stem}_encrypted{input_path.suffix}"
        
        # Call function
        setup_auto_output_single_to_single(
            input_path_picker, 
            output_path_picker, 
            path_generator=custom_generator
        )
        
        # Trigger the trace callback
        callback = input_path_var.trace_add.call_args[0][1]
        callback()
        
        # Verify output path uses custom name
        expected_path = Path('/test/path/document_encrypted.pdf')
        output_path_picker.set_path.assert_called_once_with(expected_path)


class TestSetupAutoOutputSingleToFolder:
    """Test setup_auto_output_single_to_folder function."""

    def test_default_behavior(self):
        """Test default behavior: output to parent folder."""
        input_path_picker = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        input_path_var = Mock()
        input_path_var.get.return_value = '/test/path/document.pdf'
        input_path_picker.path = input_path_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Call function
        setup_auto_output_single_to_folder(input_path_picker, output_path_picker)
        
        # Trigger the trace callback
        callback = input_path_var.trace_add.call_args[0][1]
        callback()
        
        # Verify output path is set to parent directory
        expected_path = Path('/test/path')
        output_path_picker.set_path.assert_called_once_with(expected_path)

    def test_custom_path_generator(self):
        """Test custom path generator for subfolder."""
        input_path_picker = Mock()
        output_path_picker = Mock()
        
        # Setup mocks
        input_path_var = Mock()
        input_path_var.get.return_value = '/test/path/document.pdf'
        input_path_picker.path = input_path_var
        
        output_path_picker.is_auto_output_enabled.return_value = True
        
        # Custom path generator: create subfolder
        def custom_generator(input_path: Path) -> Path:
            return input_path.parent / f"{input_path.stem}_pages"
        
        # Call function
        setup_auto_output_single_to_folder(
            input_path_picker, 
            output_path_picker, 
            path_generator=custom_generator
        )
        
        # Trigger the trace callback
        callback = input_path_var.trace_add.call_args[0][1]
        callback()
        
        # Verify output path is set to subfolder
        expected_path = Path('/test/path/document_pages')
        output_path_picker.set_path.assert_called_once_with(expected_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
