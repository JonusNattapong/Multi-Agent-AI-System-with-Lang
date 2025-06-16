#!/usr/bin/env python3
"""
Test suite for agents
"""

import unittest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from agents import ResearchAgent, WritingAgent, ReviewAgent, AgentState
from tools import WebSearchTool, SaveContentTool

class TestAgents(unittest.TestCase):
    """Test cases for agent functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.research_agent = ResearchAgent()
        self.writing_agent = WritingAgent()
        self.review_agent = ReviewAgent()
        
        self.test_state = AgentState(
            current_task="Test task for unit testing",
            context={"test_mode": True},
            metadata={"test": True}
        )
    
    def test_agent_initialization(self):
        """Test that agents initialize correctly"""
        # Test research agent
        self.assertEqual(self.research_agent.name, "research_agent")
        self.assertEqual(self.research_agent.role, "Research Specialist")
        self.assertIsNotNone(self.research_agent.llm)
        
        # Test writing agent
        self.assertEqual(self.writing_agent.name, "writing_agent")
        self.assertEqual(self.writing_agent.role, "Content Creator")
        self.assertIsNotNone(self.writing_agent.llm)
        
        # Test review agent
        self.assertEqual(self.review_agent.name, "review_agent")
        self.assertEqual(self.review_agent.role, "Quality Assurance Specialist")
        self.assertIsNotNone(self.review_agent.llm)
    
    def test_agent_state_creation(self):
        """Test AgentState creation and properties"""
        state = AgentState(
            current_task="Test task",
            context={"key": "value"},
            metadata={"test": True}
        )
        
        self.assertEqual(state.current_task, "Test task")
        self.assertEqual(state.context["key"], "value")
        self.assertEqual(state.metadata["test"], True)
        self.assertEqual(len(state.messages), 0)
        self.assertEqual(len(state.agent_outputs), 0)
    
    def test_agent_tool_addition(self):
        """Test adding tools to agents"""
        search_tool = WebSearchTool()
        save_tool = SaveContentTool()
        
        # Add tools to research agent
        self.research_agent.add_tool(search_tool)
        self.research_agent.add_tool(save_tool)
        
        self.assertEqual(len(self.research_agent.tools), 2)
        self.assertIn(search_tool, self.research_agent.tools)
        self.assertIn(save_tool, self.research_agent.tools)
    
    def test_system_message_generation(self):
        """Test system message generation"""
        system_msg = self.research_agent.get_system_message()
        
        self.assertIsNotNone(system_msg.content)
        self.assertIn("research", system_msg.content.lower())
    
    def test_message_preparation(self):
        """Test message preparation for LLM calls"""
        messages = self.research_agent.prepare_messages(self.test_state)
        
        self.assertGreater(len(messages), 0)
        # Should have system message, context, and task
        self.assertGreaterEqual(len(messages), 3)
    
    def test_agent_str_representation(self):
        """Test string representations of agents"""
        research_str = str(self.research_agent)
        self.assertIn("research_agent", research_str)
        self.assertIn("Research Specialist", research_str)
        
        research_repr = repr(self.research_agent)
        self.assertIn("ResearchAgent", research_repr)
        self.assertIn("research_agent", research_repr)

class TestAgentProcessing(unittest.TestCase):
    """Test agent processing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.research_agent = ResearchAgent()
        self.writing_agent = WritingAgent()
        self.review_agent = ReviewAgent()
    
    def test_research_agent_processing(self):
        """Test research agent processing"""
        # Note: This would require actual LLM calls
        # In a real test environment, you'd mock the LLM calls
        state = AgentState(
            current_task="Research artificial intelligence basics",
            context={"depth": "basic"}
        )
        
        # Mock the LLM call for testing
        original_invoke = self.research_agent.invoke_llm
        self.research_agent.invoke_llm = lambda messages: "Mock research result about AI basics"
        
        try:
            result_state = self.research_agent.process(state)
            
            self.assertIn("research_agent", result_state.agent_outputs)
            self.assertIn("research_findings", result_state.context)
            self.assertTrue(result_state.metadata.get("research_agent_completed"))
            
        finally:
            # Restore original method
            self.research_agent.invoke_llm = original_invoke
    
    def test_writing_agent_processing(self):
        """Test writing agent processing"""
        state = AgentState(
            current_task="Write about renewable energy",
            context={"research_findings": "Solar and wind power are growing rapidly"}
        )
        
        # Mock the LLM call
        original_invoke = self.writing_agent.invoke_llm
        self.writing_agent.invoke_llm = lambda messages: "Mock article about renewable energy"
        
        try:
            result_state = self.writing_agent.process(state)
            
            self.assertIn("writing_agent", result_state.agent_outputs)
            self.assertIn("written_content", result_state.context)
            self.assertTrue(result_state.metadata.get("writing_agent_completed"))
            
        finally:
            self.writing_agent.invoke_llm = original_invoke
    
    def test_review_agent_processing(self):
        """Test review agent processing"""
        state = AgentState(
            current_task="Review content quality",
            context={"written_content": "This is sample content to review"}
        )
        
        # Mock the LLM call
        original_invoke = self.review_agent.invoke_llm
        self.review_agent.invoke_llm = lambda messages: "Mock review feedback: Content is good"
        
        try:
            result_state = self.review_agent.process(state)
            
            self.assertIn("review_agent", result_state.agent_outputs)
            self.assertIn("review_feedback", result_state.context)
            self.assertTrue(result_state.metadata.get("review_agent_completed"))
            
        finally:
            self.review_agent.invoke_llm = original_invoke

class TestAgentChain(unittest.TestCase):
    """Test chaining agents together"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agents = [
            ResearchAgent(),
            WritingAgent(), 
            ReviewAgent()
        ]
        
        # Mock all LLM calls
        self.original_methods = []
        mock_responses = [
            "Mock research findings",
            "Mock written content",
            "Mock review feedback"
        ]
        
        for i, agent in enumerate(self.agents):
            original = agent.invoke_llm
            self.original_methods.append(original)
            agent.invoke_llm = lambda messages, response=mock_responses[i]: response
    
    def tearDown(self):
        """Restore original methods"""
        for agent, original in zip(self.agents, self.original_methods):
            agent.invoke_llm = original
    
    def test_agent_chain_processing(self):
        """Test processing through a chain of agents"""
        state = AgentState(
            current_task="Create content about climate change",
            context={"target_audience": "general public"}
        )
        
        # Process through agent chain
        for agent in self.agents:
            state = agent.process(state)
        
        # Verify all agents processed
        self.assertEqual(len(state.agent_outputs), 3)
        self.assertIn("research_agent", state.agent_outputs)
        self.assertIn("writing_agent", state.agent_outputs)
        self.assertIn("review_agent", state.agent_outputs)
        
        # Verify context updates
        self.assertIn("research_findings", state.context)
        self.assertIn("written_content", state.context)
        self.assertIn("review_feedback", state.context)
        
        # Verify metadata
        self.assertTrue(state.metadata.get("research_agent_completed"))
        self.assertTrue(state.metadata.get("writing_agent_completed"))
        self.assertTrue(state.metadata.get("review_agent_completed"))

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestAgents))
    test_suite.addTest(unittest.makeSuite(TestAgentProcessing))
    test_suite.addTest(unittest.makeSuite(TestAgentChain))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with error code if tests failed
    sys.exit(0 if result.wasSuccessful() else 1)
