"""
Tests for Document Intelligence Agent and Workflow
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.agents.document_intelligence_agent import DocumentIntelligenceAgent
from src.workflows.document_intelligence_workflow import DocumentIntelligenceWorkflow
from src.config.settings import settings


class TestDocumentIntelligenceAgent:
    """Test cases for DocumentIntelligenceAgent"""

    def setup_method(self):
        """Setup test fixtures"""
        # Create a temporary directory for test documents
        self.temp_dir = tempfile.mkdtemp()
        self.test_document_path = os.path.join(self.temp_dir, "test_document.txt")
        
        # Create a test document
        with open(self.test_document_path, 'w') as f:
            f.write("Test document content for processing")

    def teardown_method(self):
        """Cleanup test fixtures"""
        # Clean up temporary files
        if os.path.exists(self.test_document_path):
            os.remove(self.test_document_path)
        os.rmdir(self.temp_dir)

    @patch('src.agents.document_intelligence_agent.Extractor')
    @patch('src.agents.document_intelligence_agent.Process')
    def test_agent_initialization(self, mock_process, mock_extractor):
        """Test that the agent initializes correctly"""
        agent = DocumentIntelligenceAgent()
        
        assert agent is not None
        assert hasattr(agent, 'logger')
        assert hasattr(agent, 'classifications')
        assert len(agent.classifications) == 4  # Invoice, License, Passport, BusinessCard

    def test_validate_document_valid_format(self):
        """Test document validation with valid format"""
        with patch('src.agents.document_intelligence_agent.Extractor'):
            with patch('src.agents.document_intelligence_agent.Process'):
                agent = DocumentIntelligenceAgent()
                
                # Test with .txt file (supported format)
                is_valid = agent.validate_document(self.test_document_path)
                assert is_valid is True

    def test_validate_document_invalid_format(self):
        """Test document validation with invalid format"""
        with patch('src.agents.document_intelligence_agent.Extractor'):
            with patch('src.agents.document_intelligence_agent.Process'):
                agent = DocumentIntelligenceAgent()
                
                # Test with unsupported format
                invalid_path = self.test_document_path.replace('.txt', '.xyz')
                is_valid = agent.validate_document(invalid_path)
                assert is_valid is False

    def test_get_supported_formats(self):
        """Test getting supported document formats"""
        with patch('src.agents.document_intelligence_agent.Extractor'):
            with patch('src.agents.document_intelligence_agent.Process'):
                agent = DocumentIntelligenceAgent()
                
                formats = agent.get_supported_formats()
                assert isinstance(formats, list)
                assert '.pdf' in formats
                assert '.txt' in formats
                assert '.jpg' in formats

    def test_classify_document(self):
        """Test document classification"""
        with patch('src.agents.document_intelligence_agent.Extractor'):
            with patch('src.agents.document_intelligence_agent.Process'):
                agent = DocumentIntelligenceAgent()
                
                # Test classification of a file with 'invoice' in name
                invoice_path = self.test_document_path.replace('test_document', 'invoice')
                with open(invoice_path, 'w') as f:
                    f.write("Invoice content")
                
                doc_type = agent.classify_document(invoice_path)
                assert doc_type == "Invoice"
                
                # Cleanup
                os.remove(invoice_path)

    @patch('src.agents.document_intelligence_agent.AnalyzerEngine')
    @patch('src.agents.document_intelligence_agent.AnonymizerEngine')
    def test_mask_pii_enabled(self, mock_anonymizer_engine, mock_analyzer_engine):
        """Test PII masking when enabled"""
        # Mock the PII detection and masking
        mock_analyzer = Mock()
        mock_anonymizer = Mock()
        mock_analyzer_engine.return_value = mock_analyzer
        mock_anonymizer_engine.return_value = mock_anonymizer
        
        mock_analyzer.analyze.return_value = []
        mock_anonymizer.anonymize.return_value = Mock(text="Masked text")
        
        with patch('src.agents.document_intelligence_agent.Extractor'):
            with patch('src.agents.document_intelligence_agent.Process'):
                with patch.object(settings, 'ENABLE_PII_MASKING', True):
                    agent = DocumentIntelligenceAgent()
                    agent.analyzer = mock_analyzer
                    agent.anonymizer = mock_anonymizer
                    
                    result = agent.mask_pii("John Doe's email is john@example.com")
                    assert result == "Masked text"

    def test_mask_pii_disabled(self):
        """Test PII masking when disabled"""
        with patch('src.agents.document_intelligence_agent.Extractor'):
            with patch('src.agents.document_intelligence_agent.Process'):
                with patch.object(settings, 'ENABLE_PII_MASKING', False):
                    agent = DocumentIntelligenceAgent()
                    
                    original_text = "John Doe's email is john@example.com"
                    result = agent.mask_pii(original_text)
                    assert result == original_text


class TestDocumentIntelligenceWorkflow:
    """Test cases for DocumentIntelligenceWorkflow"""

    def setup_method(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_document_path = os.path.join(self.temp_dir, "test_invoice.txt")
        
        # Create a test document
        with open(self.test_document_path, 'w') as f:
            f.write("INVOICE #123\nDate: 2024-06-16\nTotal: $100.00")

    def teardown_method(self):
        """Cleanup test fixtures"""
        if os.path.exists(self.test_document_path):
            os.remove(self.test_document_path)
        os.rmdir(self.temp_dir)

    @patch('src.workflows.document_intelligence_workflow.DocumentIntelligenceAgent')
    def test_workflow_initialization(self, mock_agent):
        """Test that the workflow initializes correctly"""
        workflow = DocumentIntelligenceWorkflow()
        
        assert workflow is not None
        assert hasattr(workflow, 'agent')
        assert hasattr(workflow, 'workflow')

    def test_get_supported_formats(self):
        """Test getting supported formats from workflow"""
        with patch('src.workflows.document_intelligence_workflow.DocumentIntelligenceAgent') as mock_agent_class:
            mock_agent = Mock()
            mock_agent.get_supported_formats.return_value = ['.pdf', '.txt']
            mock_agent_class.return_value = mock_agent
            
            workflow = DocumentIntelligenceWorkflow()
            formats = workflow.get_supported_formats()
            
            assert formats == ['.pdf', '.txt']

    @patch('src.workflows.document_intelligence_workflow.DocumentIntelligenceAgent')
    def test_process_document_success(self, mock_agent_class):
        """Test successful document processing"""
        # Mock the agent and its methods
        mock_agent = Mock()
        mock_agent.validate_document.return_value = True
        mock_agent.classify_document.return_value = "Invoice"
        mock_agent.extract_with_pagination.return_value = [{"invoice_number": "123"}]
        mock_agent_class.return_value = mock_agent
        
        workflow = DocumentIntelligenceWorkflow()
        
        result = workflow.process_document(
            document_path=self.test_document_path,
            use_vision=False,
            enable_pii_masking=True
        )
        
        assert result['status'] == 'completed'
        assert result['document_type'] == 'Invoice'
        assert len(result['extracted_data']) == 1
        assert result['error_message'] == ''

    @patch('src.workflows.document_intelligence_workflow.DocumentIntelligenceAgent')
    def test_process_document_validation_error(self, mock_agent_class):
        """Test document processing with validation error"""
        # Mock the agent to return validation failure
        mock_agent = Mock()
        mock_agent.validate_document.return_value = False
        mock_agent_class.return_value = mock_agent
        
        workflow = DocumentIntelligenceWorkflow()
        
        result = workflow.process_document(
            document_path=self.test_document_path,
            use_vision=False,
            enable_pii_masking=True
        )
        
        assert result['status'] == 'error'
        assert 'Unsupported document format' in result['error_message']

    @patch('src.workflows.document_intelligence_workflow.DocumentIntelligenceAgent')
    def test_batch_process_documents(self, mock_agent_class):
        """Test batch processing of multiple documents"""
        # Create another test document
        test_document_2 = os.path.join(self.temp_dir, "test_license.txt")
        with open(test_document_2, 'w') as f:
            f.write("Driver License\nName: John Doe\nLicense: 123456")
        
        # Mock the agent
        mock_agent = Mock()
        mock_agent.validate_document.return_value = True
        mock_agent.classify_document.side_effect = ["Invoice", "Driver License"]
        mock_agent.extract_with_pagination.side_effect = [
            [{"invoice_number": "123"}],
            [{"name": "John Doe"}]
        ]
        mock_agent_class.return_value = mock_agent
        
        workflow = DocumentIntelligenceWorkflow()
        
        results = workflow.batch_process_documents([
            self.test_document_path,
            test_document_2
        ])
        
        assert len(results) == 2
        assert results[self.test_document_path]['status'] == 'completed'
        assert results[test_document_2]['status'] == 'completed'
        
        # Cleanup
        os.remove(test_document_2)


class TestConvenienceFunctions:
    """Test convenience functions"""

    @patch('src.workflows.document_intelligence_workflow.DocumentIntelligenceWorkflow')
    def test_process_document_with_local_llm(self, mock_workflow_class):
        """Test the convenience function for processing documents"""
        from src.workflows.document_intelligence_workflow import process_document_with_local_llm
        
        # Mock the workflow
        mock_workflow = Mock()
        mock_workflow.process_document.return_value = {
            'status': 'completed',
            'document_type': 'Invoice',
            'extracted_data': [{'invoice_number': '123'}],
            'error_message': ''
        }
        mock_workflow_class.return_value = mock_workflow
        
        result = process_document_with_local_llm(
            document_path="test.pdf",
            use_vision=False,
            enable_pii_masking=True
        )
        
        assert result['status'] == 'completed'
        assert result['document_type'] == 'Invoice'
        mock_workflow.process_document.assert_called_once_with(
            "test.pdf", False, True
        )


if __name__ == "__main__":
    pytest.main([__file__])
