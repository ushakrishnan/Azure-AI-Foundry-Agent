"""
Orchestrator Module - Strategy Pattern for Agent Orchestration
Provides interface for multiple orchestration backends (Managed, Semantic Kernel, LangChain)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import json
import logging
from openai import AzureOpenAI

from config import Config

logger = logging.getLogger(__name__)


class Orchestrator(ABC):
    """
    Abstract base class for orchestrator implementations.
    
    Extensibility: Implement this interface to add new orchestration backends.
    Examples:
    - ManagedOrchestrator (default): Uses Azure OpenAI function calling
    - SemanticKernelOrchestrator: Uses Microsoft Semantic Kernel
    - LangChainOrchestrator: Uses LangChain framework
    """
    
    @abstractmethod
    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        available_tools: Dict[str, Any],
        memory: Any
    ) -> Dict[str, Any]:
        """
        Process a user message and return response with tool calls.
        
        Args:
            user_message: The user's input message
            conversation_history: List of previous messages
            available_tools: Dictionary of available tool functions
            memory: Memory store with user context
            
        Returns:
            Dict containing:
                - response: Final text response to user
                - tool_calls: List of tool invocations made
                - rationale: Decision reasoning for observability
        """
        pass


class ManagedOrchestrator(Orchestrator):
    """
    Default orchestrator using Azure OpenAI function calling.
    
    This implementation uses native Azure OpenAI tool/function calling
    capabilities for agent orchestration. No external frameworks required.
    """
    
    def __init__(self):
        """Initialize the managed orchestrator with Azure OpenAI client"""
        self.client = AzureOpenAI(**Config.get_azure_client_config())
        self.model = Config.MODEL_DEPLOYMENT_NAME
        
        logger.info(f"ManagedOrchestrator initialized with model: {self.model}")
    
    def _build_tool_schemas(self, available_tools: Dict[str, Any]) -> List[Dict]:
        """Build OpenAI function schemas from available tools"""
        schemas = []
        
        for tool_name, tool_func in available_tools.items():
            # Extract schema from tool's metadata
            if hasattr(tool_func, 'schema'):
                schemas.append(tool_func.schema)
            else:
                logger.warning(f"Tool {tool_name} missing schema attribute")
        
        return schemas
    
    def process_message(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        available_tools: Dict[str, Any],
        memory: Any
    ) -> Dict[str, Any]:
        """
        Process message using Azure OpenAI function calling.
        
        Flow:
        1. Build tool schemas for function calling
        2. Call LLM with tools and conversation history
        3. Execute any requested tool calls
        4. Get final response incorporating tool results
        5. Return response with observability data
        """
        
        result = {
            "response": "",
            "tool_calls": [],
            "rationale": ""
        }
        
        try:
            # Build function schemas
            tool_schemas = self._build_tool_schemas(available_tools)
            
            # Prepare messages with memory context
            messages = self._prepare_messages(
                user_message,
                conversation_history,
                memory
            )
            
            # First LLM call - determine if tools needed
            logger.info("First LLM call: Analyzing user request...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tool_schemas if tool_schemas else None,
                tool_choice="auto" if tool_schemas else None,
                max_completion_tokens=Config.MAX_TOKENS
            )
            
            assistant_message = response.choices[0].message
            
            # Check if model wants to call tools
            if assistant_message.tool_calls:
                logger.info(f"Model requested {len(assistant_message.tool_calls)} tool call(s)")
                
                # Execute tool calls
                tool_results = []
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    if tool_name in available_tools:
                        try:
                            tool_result = available_tools[tool_name](**tool_args)
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_name,
                                "content": json.dumps(tool_result)
                            })
                            
                            result["tool_calls"].append({
                                "tool": tool_name,
                                "arguments": tool_args,
                                "result": tool_result
                            })
                            
                        except Exception as e:
                            logger.error(f"Error executing tool {tool_name}: {str(e)}")
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": tool_name,
                                "content": json.dumps({"error": str(e)})
                            })
                
                # Second LLM call with tool results
                logger.info("Second LLM call: Synthesizing response with tool results...")
                
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                messages.extend(tool_results)
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_completion_tokens=Config.MAX_TOKENS
                )
                
                result["response"] = final_response.choices[0].message.content
                result["rationale"] = f"Used tools: {', '.join([tc['tool'] for tc in result['tool_calls']])}"
                
            else:
                # No tools needed, direct response
                logger.info("No tools required, providing direct response")
                result["response"] = assistant_message.content
                result["rationale"] = "Direct response without tool use"
            
            return result
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {str(e)}", exc_info=True)
            result["response"] = "I apologize, but I encountered an error processing your request. Please try again."
            result["rationale"] = f"Error: {str(e)}"
            return result
    
    def _prepare_messages(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        memory: Any
    ) -> List[Dict[str, str]]:
        """Prepare messages with system prompt and memory context"""
        
        messages = [{"role": "system", "content": Config.SYSTEM_PROMPT}]
        
        # Add memory context if available
        if memory and hasattr(memory, 'get_context_summary'):
            context = memory.get_context_summary()
            if context:
                messages.append({
                    "role": "system",
                    "content": f"User context: {context}"
                })
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages


# TODO: Implement SemanticKernelOrchestrator
# Extensibility guide:
# 1. Install semantic-kernel package
# 2. Import required SK components
# 3. Implement process_message using SK's planner and plugins
# 4. Register tools as SK plugins/functions
# Example:
"""
class SemanticKernelOrchestrator(Orchestrator):
    def __init__(self):
        import semantic_kernel as sk
        self.kernel = sk.Kernel()
        # Configure kernel with Azure OpenAI
        # Register plugins for tools
        
    def process_message(self, user_message, conversation_history, available_tools, memory):
        # Use SK planner to orchestrate
        # Convert tools to SK plugins
        # Execute plan and return results
        pass
"""


# TODO: Implement LangChainOrchestrator
# Extensibility guide:
# 1. Install langchain and langchain-openai packages
# 2. Create LangChain agent with Azure OpenAI
# 3. Convert tools to LangChain tools format
# 4. Use agent executor for orchestration
# Example:
"""
class LangChainOrchestrator(Orchestrator):
    def __init__(self):
        from langchain.agents import AgentExecutor, create_openai_functions_agent
        from langchain_openai import AzureChatOpenAI
        
        self.llm = AzureChatOpenAI(...)
        # Create agent with tools
        
    def process_message(self, user_message, conversation_history, available_tools, memory):
        # Convert available_tools to LangChain tools
        # Execute agent with user message
        # Return formatted results
        pass
"""


class OrchestratorFactory:
    """Factory for creating orchestrator instances"""
    
    @staticmethod
    def create(orchestrator_type: str = None) -> Orchestrator:
        """
        Create an orchestrator instance based on type.
        
        Args:
            orchestrator_type: Type of orchestrator ("managed", "semantic_kernel", "langchain")
            
        Returns:
            Orchestrator instance
            
        Extensibility:
        To add a new orchestrator:
        1. Implement the Orchestrator abstract class
        2. Add a new case in this factory method
        3. Update Config.ORCHESTRATOR_TYPE options
        """
        
        orch_type = orchestrator_type or Config.ORCHESTRATOR_TYPE
        
        if orch_type == "managed":
            return ManagedOrchestrator()
        
        elif orch_type == "semantic_kernel":
            # TODO: Uncomment when SemanticKernelOrchestrator is implemented
            # return SemanticKernelOrchestrator()
            raise NotImplementedError(
                "Semantic Kernel orchestrator not yet implemented. "
                "See orchestrator.py for implementation guide."
            )
        
        elif orch_type == "langchain":
            # TODO: Uncomment when LangChainOrchestrator is implemented
            # return LangChainOrchestrator()
            raise NotImplementedError(
                "LangChain orchestrator not yet implemented. "
                "See orchestrator.py for implementation guide."
            )
        
        else:
            raise ValueError(
                f"Unknown orchestrator type: {orch_type}. "
                f"Valid options: managed, semantic_kernel, langchain"
            )
