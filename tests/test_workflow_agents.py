"""Integration tests for workflow agents."""
import pytest
from src.adk_ide.agents.workflow import LoopAgent, SequentialAgent, ParallelAgent
from src.adk_ide.agents.base import ADKIDEAgent


class MockAgent(ADKIDEAgent):
    """Mock agent for testing."""

    def __init__(self, name: str, delay: float = 0.0):
        super().__init__(name=name, description=f"Mock agent {name}")
        self.delay = delay
        self.call_count = 0

    async def run(self, request):
        self.call_count += 1
        import asyncio
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        return {"status": "success", "agent": self.name, "call_count": self.call_count}


@pytest.mark.asyncio
async def test_sequential_agent():
    """Test SequentialAgent executes agents in order."""
    agent1 = MockAgent("agent1")
    agent2 = MockAgent("agent2")
    agent3 = MockAgent("agent3")
    
    seq_agent = SequentialAgent([agent1, agent2, agent3])
    result = await seq_agent.run({"test": "data"})
    
    assert result["status"] == "success"
    assert len(result["results"]) == 3
    assert agent1.call_count == 1
    assert agent2.call_count == 1
    assert agent3.call_count == 1


@pytest.mark.asyncio
async def test_parallel_agent():
    """Test ParallelAgent executes agents concurrently."""
    agent1 = MockAgent("agent1", delay=0.1)
    agent2 = MockAgent("agent2", delay=0.1)
    agent3 = MockAgent("agent3", delay=0.1)
    
    parallel_agent = ParallelAgent([agent1, agent2, agent3])
    import time
    start = time.time()
    result = await parallel_agent.run({"test": "data"})
    duration = time.time() - start
    
    assert result["status"] == "success"
    assert len(result["results"]) == 3
    # Should complete faster than sequential (3 * 0.1 = 0.3s)
    assert duration < 0.25  # Allow some overhead
    assert agent1.call_count == 1
    assert agent2.call_count == 1
    assert agent3.call_count == 1


@pytest.mark.asyncio
async def test_loop_agent_max_iterations():
    """Test LoopAgent respects max_iterations."""
    agent1 = MockAgent("agent1")
    agent2 = MockAgent("agent2")
    
    loop_agent = LoopAgent([agent1, agent2], max_iterations=3)
    result = await loop_agent.run({"test": "data"})
    
    assert result["status"] == "completed"
    assert result["iterations"] == 3
    assert result["termination_reason"] == "max_iterations_reached"
    # Each iteration calls both agents
    assert agent1.call_count == 3
    assert agent2.call_count == 3


@pytest.mark.asyncio
async def test_loop_agent_escalate_termination():
    """Test LoopAgent terminates on escalate signal."""
    class EscalatingAgent(ADKIDEAgent):
        def __init__(self, escalate_on_call: int = 2):
            super().__init__(name="escalating", description="Escalates after N calls")
            self.escalate_on_call = escalate_on_call
            self.call_count = 0

        async def run(self, request):
            self.call_count += 1
            if self.call_count >= self.escalate_on_call:
                return {"status": "success", "escalate": True}
            return {"status": "success", "escalate": False}

    agent1 = EscalatingAgent(escalate_on_call=2)
    agent2 = MockAgent("agent2")
    
    loop_agent = LoopAgent([agent1, agent2], max_iterations=5)
    result = await loop_agent.run({"test": "data"})
    
    assert result["status"] == "completed"
    assert result["iterations"] == 2
    assert result["termination_reason"] == "escalate_signal"
    assert agent1.call_count == 2

