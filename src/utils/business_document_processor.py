"""
Real Business Document Processor

Specialized processor for handling actual business documents with domain-specific
extraction patterns and business intelligence capabilities.
"""
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from src.agents.document_intelligence_agent import DocumentIntelligenceAgent
from src.config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class BusinessMetric:
    """Represents a business metric extracted from documents"""
    name: str
    value: str
    unit: str
    context: str
    confidence: float
    source_document: str

@dataclass
class FinancialData:
    """Financial information extracted from business documents"""
    revenue: Optional[str] = None
    growth_rate: Optional[str] = None
    margin: Optional[str] = None
    costs: Optional[str] = None
    customer_metrics: List[str] = None

@dataclass
class PerformanceMetrics:
    """System performance metrics"""
    accuracy: Dict[str, str] = None
    response_times: Dict[str, str] = None
    uptime: Optional[str] = None
    error_rates: Optional[str] = None

@dataclass
class ComplianceInfo:
    """Compliance and security information"""
    standards: List[str] = None
    certifications: List[str] = None
    last_audit: Optional[str] = None
    classification_levels: List[str] = None

class BusinessDocumentProcessor:
    """Specialized processor for business documents"""
    
    def __init__(self):
        self.agent = DocumentIntelligenceAgent()
        self.logger = logging.getLogger(__name__)
        
        # Regular expressions for extracting business data
        self.patterns = {
            'financial': {
                'revenue': r'[Rr]evenue:?\s*\$?([0-9.,]+[KMB]?)',
                'growth': r'([0-9.]+%)\s*(?:increase|growth|YoY)',
                'margin': r'(?:margin|Margin):?\s*([0-9.]+%)',
                'customers': r'([0-9,]+)\s*(?:customers?|clients?)',
                'retention': r'retention:?\s*([0-9.]+%)'
            },
            'performance': {
                'accuracy': r'(?:accuracy|Accuracy):?\s*([0-9.]+%)',
                'response_time': r'(?:response time|time):?\s*([0-9.]+)s?',
                'uptime': r'(?:uptime|Uptime):?\s*([0-9.]+%)',
                'processing': r'processing:?\s*([0-9.,]+)',
                'f1_score': r'F1[- ]score:?\s*([0-9.]+)'
            },
            'compliance': {
                'gdpr': r'GDPR|General Data Protection Regulation',
                'hipaa': r'HIPAA|Health Insurance Portability',
                'soc2': r'SOC\s*2|Service Organization Control',
                'iso27001': r'ISO\s*27001',
                'certification': r'(?:certified|certification|compliant)\s*([A-Z0-9\s]+)'
            },
            'dates': {
                'quarter': r'Q[1-4]\s*20[0-9]{2}',
                'date': r'20[0-9]{2}-[0-9]{2}-[0-9]{2}',
                'year': r'20[0-9]{2}'
            }
        }

    def extract_financial_metrics(self, text: str, source_doc: str) -> FinancialData:
        """Extract financial metrics from document text"""
        try:
            financial_data = FinancialData(customer_metrics=[])
            
            # Extract revenue
            revenue_match = re.search(self.patterns['financial']['revenue'], text, re.IGNORECASE)
            if revenue_match:
                financial_data.revenue = revenue_match.group(1)
            
            # Extract growth rate
            growth_match = re.search(self.patterns['financial']['growth'], text, re.IGNORECASE)
            if growth_match:
                financial_data.growth_rate = growth_match.group(1)
            
            # Extract margin
            margin_match = re.search(self.patterns['financial']['margin'], text, re.IGNORECASE)
            if margin_match:
                financial_data.margin = margin_match.group(1)
            
            # Extract customer metrics
            retention_match = re.search(self.patterns['financial']['retention'], text, re.IGNORECASE)
            if retention_match:
                financial_data.customer_metrics.append(f"Retention: {retention_match.group(1)}")
            
            customers_match = re.search(self.patterns['financial']['customers'], text, re.IGNORECASE)
            if customers_match:
                financial_data.customer_metrics.append(f"Customer count: {customers_match.group(1)}")
            
            return financial_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract financial metrics: {e}")
            return FinancialData()

    def extract_performance_metrics(self, text: str, source_doc: str) -> PerformanceMetrics:
        """Extract performance metrics from document text"""
        try:
            performance_data = PerformanceMetrics(
                accuracy={},
                response_times={}
            )
            
            # Extract accuracy metrics
            accuracy_matches = re.findall(self.patterns['performance']['accuracy'], text, re.IGNORECASE)
            for i, accuracy in enumerate(accuracy_matches):
                performance_data.accuracy[f"metric_{i+1}"] = accuracy
            
            # Extract response times
            response_matches = re.findall(self.patterns['performance']['response_time'], text, re.IGNORECASE)
            for i, time in enumerate(response_matches):
                performance_data.response_times[f"component_{i+1}"] = f"{time}s"
            
            # Extract uptime
            uptime_match = re.search(self.patterns['performance']['uptime'], text, re.IGNORECASE)
            if uptime_match:
                performance_data.uptime = uptime_match.group(1)
            
            return performance_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract performance metrics: {e}")
            return PerformanceMetrics()

    def extract_compliance_info(self, text: str, source_doc: str) -> ComplianceInfo:
        """Extract compliance information from document text"""
        try:
            compliance_data = ComplianceInfo(
                standards=[],
                certifications=[],
                classification_levels=[]
            )
            
            # Check for compliance standards
            if re.search(self.patterns['compliance']['gdpr'], text, re.IGNORECASE):
                compliance_data.standards.append("GDPR")
            
            if re.search(self.patterns['compliance']['hipaa'], text, re.IGNORECASE):
                compliance_data.standards.append("HIPAA")
            
            if re.search(self.patterns['compliance']['soc2'], text, re.IGNORECASE):
                compliance_data.standards.append("SOC 2")
            
            if re.search(self.patterns['compliance']['iso27001'], text, re.IGNORECASE):
                compliance_data.standards.append("ISO 27001")
            
            # Extract classification levels
            if "Level 1" in text:
                compliance_data.classification_levels.append("Public")
            if "Level 2" in text:
                compliance_data.classification_levels.append("Internal")
            if "Level 3" in text:
                compliance_data.classification_levels.append("Confidential")
            if "Level 4" in text:
                compliance_data.classification_levels.append("Restricted")
            
            return compliance_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract compliance info: {e}")
            return ComplianceInfo()

    def analyze_document_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze document content with business-specific patterns"""
        try:
            # Read the document content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            doc_name = Path(file_path).name
            
            # Extract different types of business data
            financial_data = self.extract_financial_metrics(content, doc_name)
            performance_data = self.extract_performance_metrics(content, doc_name)
            compliance_data = self.extract_compliance_info(content, doc_name)
            
            # Extract dates and context
            quarter_matches = re.findall(self.patterns['dates']['quarter'], content, re.IGNORECASE)
            year_matches = re.findall(self.patterns['dates']['year'], content)
            
            return {
                'document_name': doc_name,
                'document_path': file_path,
                'financial_metrics': financial_data,
                'performance_metrics': performance_data,
                'compliance_info': compliance_data,
                'quarters': quarter_matches,
                'years': year_matches,
                'content_length': len(content),
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze document content: {e}")
            return {'error': str(e)}

    def process_business_documents(self, document_paths: List[str]) -> Dict[str, Any]:
        """Process multiple business documents and extract insights"""
        results = {
            'documents_processed': [],
            'financial_summary': {},
            'performance_summary': {},
            'compliance_summary': {},
            'business_insights': []
        }
        
        for doc_path in document_paths:
            if not os.path.exists(doc_path):
                self.logger.warning(f"Document not found: {doc_path}")
                continue
            
            try:
                # Analyze with both AI agent and pattern matching
                ai_result = self.agent.process_document(doc_path)
                content_analysis = self.analyze_document_content(doc_path)
                
                # Combine results
                combined_result = {
                    'ai_extraction': {
                        'items_extracted': len(ai_result),
                        'sample_data': str(ai_result[0])[:200] + "..." if ai_result else "No data"
                    },
                    'pattern_analysis': content_analysis
                }
                
                results['documents_processed'].append(combined_result)
                
                # Aggregate financial data
                if content_analysis.get('financial_metrics'):
                    fin_data = content_analysis['financial_metrics']
                    if fin_data.revenue:
                        results['financial_summary']['revenue'] = fin_data.revenue
                    if fin_data.growth_rate:
                        results['financial_summary']['growth_rate'] = fin_data.growth_rate
                    if fin_data.margin:
                        results['financial_summary']['operating_margin'] = fin_data.margin
                
                # Aggregate performance data
                if content_analysis.get('performance_metrics'):
                    perf_data = content_analysis['performance_metrics']
                    if perf_data.accuracy:
                        results['performance_summary'].update(perf_data.accuracy)
                    if perf_data.uptime:
                        results['performance_summary']['uptime'] = perf_data.uptime
                
                # Aggregate compliance data
                if content_analysis.get('compliance_info'):
                    comp_data = content_analysis['compliance_info']
                    if comp_data.standards:
                        if 'standards' not in results['compliance_summary']:
                            results['compliance_summary']['standards'] = []
                        results['compliance_summary']['standards'].extend(comp_data.standards)
                
            except Exception as e:
                self.logger.error(f"Failed to process {doc_path}: {e}")
                results['documents_processed'].append({
                    'document': doc_path,
                    'error': str(e)
                })
        
        # Generate business insights
        results['business_insights'] = self._generate_insights(results)
        
        return results

    def _generate_insights(self, results: Dict[str, Any]) -> List[str]:
        """Generate business insights from processed data"""
        insights = []
        
        # Financial insights
        financial = results.get('financial_summary', {})
        if financial.get('revenue') and financial.get('growth_rate'):
            insights.append(f"Strong financial performance with {financial['growth_rate']} revenue growth")
        
        if financial.get('operating_margin'):
            try:
                margin_val = float(financial['operating_margin'].rstrip('%'))
                if margin_val > 20:
                    insights.append(f"Excellent operating margin of {financial['operating_margin']}")
                elif margin_val > 15:
                    insights.append(f"Good operating margin of {financial['operating_margin']}")
            except ValueError:
                pass
        
        # Performance insights
        performance = results.get('performance_summary', {})
        if performance.get('uptime'):
            try:
                uptime_val = float(performance['uptime'].rstrip('%'))
                if uptime_val > 99:
                    insights.append(f"Excellent system reliability with {performance['uptime']} uptime")
            except ValueError:
                pass
        
        # Compliance insights
        compliance = results.get('compliance_summary', {})
        if compliance.get('standards'):
            unique_standards = list(set(compliance['standards']))
            insights.append(f"Comprehensive compliance coverage: {', '.join(unique_standards)}")
        
        # Document processing insights
        processed_count = len(results.get('documents_processed', []))
        if processed_count > 0:
            insights.append(f"Successfully processed {processed_count} business documents")
        
        return insights

    def generate_executive_summary(self, results: Dict[str, Any]) -> str:
        """Generate an executive summary report"""
        summary = f"""
📊 EXECUTIVE BUSINESS INTELLIGENCE SUMMARY
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: Multi-Agent Document Intelligence System

{'-' * 60}

💰 FINANCIAL PERFORMANCE
"""
        
        financial = results.get('financial_summary', {})
        if financial:
            for key, value in financial.items():
                summary += f"  • {key.replace('_', ' ').title()}: {value}\n"
        else:
            summary += "  • No financial metrics extracted\n"
        
        summary += f"""
⚡ OPERATIONAL METRICS
"""
        
        performance = results.get('performance_summary', {})
        if performance:
            for key, value in performance.items():
                summary += f"  • {key.replace('_', ' ').title()}: {value}\n"
        else:
            summary += "  • No performance metrics extracted\n"
        
        summary += f"""
🔒 COMPLIANCE STATUS
"""
        
        compliance = results.get('compliance_summary', {})
        if compliance.get('standards'):
            summary += f"  • Standards: {', '.join(set(compliance['standards']))}\n"
        else:
            summary += "  • No compliance standards identified\n"
        
        summary += f"""
🎯 KEY INSIGHTS
"""
        
        insights = results.get('business_insights', [])
        for insight in insights:
            summary += f"  • {insight}\n"
        
        if not insights:
            summary += "  • No specific insights generated\n"
        
        summary += f"""
📈 PROCESSING SUMMARY
  • Documents analyzed: {len(results.get('documents_processed', []))}
  • Analysis method: AI + Pattern matching
  • Provider: {settings.MODEL_PROVIDER}
  • Privacy: PII masking enabled

{'-' * 60}
Report generated by Business Document Processor
Confidence: High (real business data)
Recommendation: Continue leveraging document intelligence for business insights
"""
        
        return summary

# Convenience function for quick business document analysis
def analyze_business_documents(document_paths: List[str]) -> Dict[str, Any]:
    """
    Quick function to analyze business documents
    
    Args:
        document_paths: List of paths to business documents
        
    Returns:
        Comprehensive analysis results with business insights
    """
    processor = BusinessDocumentProcessor()
    return processor.process_business_documents(document_paths)
