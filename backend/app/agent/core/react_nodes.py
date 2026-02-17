"""
ReAct Pattern Nodes

Implements the Reasoning, Action, and Observation nodes for the agent.
"""

from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from ..state.agent_state import AgentState, Phase
from ..prompts.system_prompts import get_system_prompt
from ..tools.error_handling import truncate_output


class ReActNodes:
    """
    ReAct pattern implementation with think, act, and observe nodes.
    """
    
    def __init__(self, model_provider: str = "openai", model_name: str = "gpt-4"):
        """
        Initialize ReAct nodes with LLM.
        
        Args:
            model_provider: "openai" or "anthropic"
            model_name: Model identifier (e.g., "gpt-4", "claude-3-opus-20240229")
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM based on provider"""
        if self.model_provider == "openai":
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=0.7,
                max_tokens=2000,
            )
        elif self.model_provider == "anthropic":
            self.llm = ChatAnthropic(
                model=self.model_name,
                temperature=0.7,
                max_tokens=2000,
            )
        else:
            raise ValueError(f"Unknown model provider: {self.model_provider}")
    
    async def think(self, state: AgentState) -> Dict[str, Any]:
        """
        THINK node: Agent reasons about what to do next.
        
        Analyzes the current state and decides:
        - Which tool to use (if any)
        - What parameters to pass
        - Whether to stop
        
        Returns:
            Updated state with next_action, selected_tool, tool_input
        """
        # Get system prompt for current phase
        system_prompt = get_system_prompt(state["current_phase"])
        
        # Build message history
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        
        # If we have an observation from previous action, add it
        if state.get("observation"):
            messages.append(AIMessage(content=f"OBSERVATION: {state['observation']}"))
        
        # Ask LLM to think and decide next action
        # Get available tools for current phase
        from ..tools.tool_registry import get_global_registry
        
        registry = get_global_registry()
        available_tools = registry.get_tools_for_phase(state["current_phase"])
        
        tool_descriptions = []
        for tool_name, tool in available_tools.items():
            tool_descriptions.append(f"- {tool_name}: {tool.description}")
        
        tools_list = "\n".join(tool_descriptions) if tool_descriptions else "No tools available"
        
        thinking_prompt = f"""
Based on the conversation and any observations, think about what to do next.

You should:
1. Analyze the current situation
2. Decide if you need to use a tool or if you can respond directly
3. If using a tool, specify which one and what parameters

Available tools in {state["current_phase"].value} phase:
{tools_list}

Format your response as:
THOUGHT: [Your reasoning]
ACTION: [tool_name or "respond"]
TOOL_INPUT: [JSON parameters if using a tool, or your response if responding directly]
"""
        
        messages.append(HumanMessage(content=thinking_prompt))
        
        # Get LLM response
        response = await self.llm.ainvoke(messages)
        response_text = response.content
        
        # Parse the response to extract action and tool info
        thought, action, tool_input = self._parse_llm_response(response_text)
        
        # Update state
        updates = {
            "messages": state["messages"] + [AIMessage(content=f"THOUGHT: {thought}")],
        }
        
        if action == "respond":
            # Agent wants to respond directly, not use a tool
            updates["next_action"] = "end"
            updates["should_stop"] = True
            updates["messages"].append(AIMessage(content=tool_input))
        else:
            # Agent wants to use a tool
            updates["next_action"] = "act"
            updates["selected_tool"] = action
            updates["tool_input"] = tool_input
        
        return updates
    
    async def act(self, state: AgentState) -> Dict[str, Any]:
        """
        ACT node: Execute the selected tool.
        
        Takes the tool selection from the think node and executes it.
        
        Returns:
            Updated state with tool outputs and next_action set to "observe"
        """
        tool_name = state.get("selected_tool")
        tool_input = state.get("tool_input", {})
        
        if not tool_name:
            return {
                "next_action": "think",
                "observation": "No tool was selected. Let me think again."
            }
        
        # Get tool from registry
        from ..tools.tool_registry import get_global_registry
        
        registry = get_global_registry()
        current_phase = state.get("current_phase", Phase.INFORMATIONAL)
        
        # Check if tool is allowed in current phase
        if not registry.is_tool_allowed(tool_name, current_phase):
            return {
                "next_action": "think",
                "observation": f"Tool '{tool_name}' is not available in {current_phase.value} phase."
            }
        
        tool = registry.get_tool(tool_name)
        if not tool:
            return {
                "next_action": "think",
                "observation": f"Unknown tool: {tool_name}. Let me try again."
            }
        
        # Execute the tool
        try:
            output = await tool.execute(**tool_input)
            # Truncate if too long
            output = truncate_output(output, max_chars=3000)
        except Exception as e:
            output = f"Tool execution error: {str(e)}"
        
        # Store tool output
        tool_outputs = state.get("tool_outputs", {})
        tool_outputs[tool_name] = output
        
        return {
            "tool_outputs": tool_outputs,
            "observation": output,
            "next_action": "observe"
        }
    
    async def observe(self, state: AgentState) -> Dict[str, Any]:
        """
        OBSERVE node: Process tool output and decide next step.
        
        Analyzes the tool output and updates the agent's understanding.
        
        Returns:
            Updated state with next_action set to "think" (continue loop)
        """
        observation = state.get("observation", "")
        
        # Add observation to messages
        updates = {
            "messages": state["messages"] + [
                AIMessage(content=f"Tool output: {observation}")
            ],
            "next_action": "think",  # Continue the ReAct loop
        }
        
        return updates
    
    def _parse_llm_response(self, response: str) -> tuple:
        """
        Parse LLM response to extract thought, action, and tool input.
        
        Returns:
            (thought, action, tool_input)
        """
        lines = response.strip().split("\n")
        
        thought = ""
        action = "respond"
        tool_input = {}
        
        for line in lines:
            if line.startswith("THOUGHT:"):
                thought = line.replace("THOUGHT:", "").strip()
            elif line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()
            elif line.startswith("TOOL_INPUT:"):
                input_str = line.replace("TOOL_INPUT:", "").strip()
                try:
                    import json
                    tool_input = json.loads(input_str) if input_str else {}
                except:
                    tool_input = input_str if action == "respond" else {}
        
        return thought, action, tool_input
