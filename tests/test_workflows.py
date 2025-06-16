#!/usr/bin/env python3
"""
Test suite for workflows
"""

import unittest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from workflows import ContentCreationWorkflow, ResearchWorkflow
from agents import AgentState

class TestContentCreationWorkflow(unittest.TestCase):
    """Test cases for content creation workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.workflow = ContentCreationWorkflow()
        
        # Mock all agent LLM calls
        self.original_methods = {}
        mock_responses = {
            "research_agent": "Mock research findings for testing",
            "writing_agent": "Mock written content for testing",
            "review_agent": "Mock review feedback: Content is excellent"
        }
        
        for agent_name in ["research_agent", "writing_agent", "review_agent"]:
            agent = getattr(self.workflow, agent_name)
            self.original_methods[agent_name] = agent.invoke_llm
            agent.invoke_llm = lambda messages, response=mock_responses[agent_name]: response
    
    def tearDown(self):
        """Restore original methods"""
        for agent_name, original_method in self.original_methods.items():
            agent = getattr(self.workflow, agent_name)
            agent.invoke_llm = original_method
    
    def test_workflow_initialization(self):
        """Test workflow initialization"""
        self.assertIsNotNone(self.workflow.research_agent)
        self.assertIsNotNone(self.workflow.writing_agent)
        self.assertIsNotNone(self.workflow.review_agent)
        self.assertIsNotNone(self.workflow.workflow)
    
    def test_workflow_run(self):
        """Test running the workflow"""
        task = "Create content about sustainable transportation"
        context = {"target_audience": "environmental enthusiasts"}
        
        result = self.workflow.run(task, context)
        
        self.assertTrue(result["success"])
        self.assertIn("final_content", result)
        self.assertIn("review_feedback", result)
        self.assertIn("research_findings", result)
        self.assertIn("metadata", result)
        
        # Check metadata indicates completion
        self.assertTrue(result["metadata"].get("workflow_completed"))
    
    def test_workflow_with_feedback_loop(self):
        """Test workflow with feedback loop"""
        task = "Write product description for eco-friendly water bottle"
        
        result = self.workflow.run_with_feedback_loop(task, max_iterations=2)
        
        self.assertTrue(result["success"])
        self.assertIn("iterations", result)
        self.assertIn("final_content", result)
        self.assertLessEqual(result["iterations"], 2)
    
    def test_individual_workflow_steps(self):
        """Test individual workflow steps"""
        state = AgentState(
            current_task="Test task",
            context={"test": True}
        )
        
        # Test research step
        research_state = self.workflow.research_step(state)
        self.assertIn("research_agent", research_state.agent_outputs)
        
        # Test write step
        write_state = self.workflow.write_step(research_state)
        self.assertIn("writing_agent", write_state.agent_outputs)
        
        # Test review step
        review_state = self.workflow.review_step(write_state)
        self.assertIn("review_agent", review_state.agent_outputs)
        
        # Test finalize step
        final_state = self.workflow.finalize_step(review_state)
        self.assertIn("final_result", final_state.context)
        self.assertTrue(final_state.metadata.get("workflow_completed"))

class TestResearchWorkflow(unittest.TestCase):
    """Test cases for research workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.workflow = ResearchWorkflow()
        
        # Mock research agent LLM calls
        self.original_method = self.workflow.research_agent.invoke_llm
        mock_responses = [
            "Mock initial research findings",
            "Mock deep dive analysis", 
            "Mock synthesis of findings",
            "Mock validation results"
        ]
        
        self.response_index = 0
        def mock_invoke(messages):
            response = mock_responses[self.response_index % len(mock_responses)]
            self.response_index += 1
            return response
        
        self.workflow.research_agent.invoke_llm = mock_invoke
    
    def tearDown(self):
        """Restore original method"""
        self.workflow.research_agent.invoke_llm = self.original_method
    
    def test_research_workflow_initialization(self):
        """Test research workflow initialization"""
        self.assertIsNotNone(self.workflow.research_agent)
        self.assertIsNotNone(self.workflow.workflow)
    
    def test_research_workflow_run(self):
        """Test running the research workflow"""
        topic = "Machine learning applications in healthcare"
        
        result = self.workflow.run(topic)
        
        self.assertTrue(result["success"])
        self.assertIn("final_report", result)
        self.assertIn("initial_findings", result)
        self.assertIn("deep_dive_findings", result)
        self.assertIn("synthesis", result)
        self.assertIn("validation", result)
        self.assertEqual(result["research_topic"], topic)
    
    def test_collaborative_research(self):
        """Test collaborative research on multiple topics"""
        topics = [
            "AI in medical diagnosis",
            "Machine learning for drug discovery",
            "Healthcare data analytics"
        ]
        
        result = self.workflow.run_collaborative_research(topics)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["total_topics"], len(topics))
        self.assertIn("individual_results", result)
        self.assertIn("collaborative_synthesis", result)
        
        # Check that all topics were processed
        for topic in topics:
            self.assertIn(topic, result["individual_results"])
    
    def test_individual_research_steps(self):
        """Test individual research workflow steps"""
        state = AgentState(
            current_task="Test research topic",
            context={}
        )
        
        # Test initial research step
        initial_state = self.workflow.initial_research_step(state)
        self.assertIn("initial_findings", initial_state.context)
        
        # Test deep dive step
        deep_dive_state = self.workflow.deep_dive_step(initial_state)
        self.assertIn("deep_dive_findings", deep_dive_state.context)
        
        # Test synthesis step
        synthesis_state = self.workflow.synthesis_step(deep_dive_state)
        self.assertIn("research_synthesis", synthesis_state.context)
        
        # Test validation step
        validation_state = self.workflow.validation_step(synthesis_state)
        self.assertIn("validation_results", validation_state.context)
        
        # Test finalize step
        final_state = self.workflow.finalize_step(validation_state)
        self.assertIn("final_research_report", final_state.context)
        self.assertTrue(final_state.metadata.get("research_workflow_completed"))

class TestWorkflowIntegration(unittest.TestCase):
    """Test integration between workflows"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.content_workflow = ContentCreationWorkflow()
        self.research_workflow = ResearchWorkflow()
        
        # Mock all LLM calls
        self.mock_responses = {
            "research": "Mock research findings",
            "writing": "Mock written content", 
            "review": "Mock review feedback"
        }
        
        # Store original methods
        self.original_methods = {}
        
        # Mock content creation agents
        for agent_name in ["research_agent", "writing_agent", "review_agent"]:
            agent = getattr(self.content_workflow, agent_name)
            self.original_methods[f"content_{agent_name}"] = agent.invoke_llm
            agent.invoke_llm = lambda messages, resp=self.mock_responses.get(agent_name.split("_")[0], "Mock"): resp
        
        # Mock research workflow agent
        self.original_methods["research_workflow"] = self.research_workflow.research_agent.invoke_llm
        self.research_workflow.research_agent.invoke_llm = lambda messages: "Mock research workflow response"
    
    def tearDown(self):
        """Restore original methods"""
        # Restore content workflow agents
        for agent_name in ["research_agent", "writing_agent", "review_agent"]:
            agent = getattr(self.content_workflow, agent_name)
            agent.invoke_llm = self.original_methods[f"content_{agent_name}"]
        
        # Restore research workflow agent
        self.research_workflow.research_agent.invoke_llm = self.original_methods["research_workflow"]
    
    def test_workflow_combination(self):
        """Test combining research and content creation workflows"""
        # First, do research
        research_result = self.research_workflow.run("AI in education")
        
        if research_result["success"]:
            # Use research findings for content creation
            content_context = {
                "research_findings": research_result["synthesis"],
                "target_audience": "educators"
            }
            
            content_result = self.content_workflow.run(
                "Create educational content about AI applications",
                content_context
            )
            
            self.assertTrue(content_result["success"])
            self.assertIn("final_content", content_result)
    
    def test_error_handling(self):
        """Test error handling in workflows"""
        # Test with invalid task
        result = self.content_workflow.run("")
        
        # Should still succeed with mocked responses
        # In real implementation, you'd test actual error conditions
        self.assertIn("success", result)

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestContentCreationWorkflow))
    test_suite.addTest(unittest.makeSuite(TestResearchWorkflow))
    test_suite.addTest(unittest.makeSuite(TestWorkflowIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
