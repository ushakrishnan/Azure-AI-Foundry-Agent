"""
Azure AI Foundry Chef AI Agent - Configuration Module
Handles environment variables, Azure AI Foundry settings, and model configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for Azure AI Foundry Chef AI Agent"""
    
    # ========== Azure AI Foundry Configuration ==========
    # TODO: Set these in your .env file
    # Get from: Azure AI Foundry Portal > Project Settings > Endpoints
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    
    # Model deployment name in Azure AI Foundry
    # Common options: gpt-4, gpt-4-turbo, gpt-35-turbo
    MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME", "gpt-4")
    
    # API version for Azure OpenAI
    API_VERSION = os.getenv("API_VERSION", "2024-08-01-preview")
    
    # ========== Agent Configuration ==========
    MAX_CONVERSATION_HISTORY = 10  # Keep last N messages for context
    TEMPERATURE = 0.7
    MAX_TOKENS = 1500
    
    # Orchestrator type: "managed" (default) or "semantic_kernel" or "langchain"
    ORCHESTRATOR_TYPE = os.getenv("ORCHESTRATOR_TYPE", "managed")
    
    # ========== Tool Configuration ==========
    # Enable/disable specific tools
    ENABLE_INGREDIENT_EXTRACTION = True
    ENABLE_RECIPE_SEARCH = True
    
    # Recipe search parameters
    MAX_RECIPE_RESULTS = 5
    RECIPE_DATA_PATH = "data/recipes.json"
    
    # ========== Memory Configuration ==========
    # Memory backend: "in_memory" (default), "redis", "cosmos_db"
    MEMORY_BACKEND = os.getenv("MEMORY_BACKEND", "in_memory")
    
    # TODO: For production, configure external memory stores
    REDIS_URL = os.getenv("REDIS_URL")  # e.g., "redis://localhost:6379"
    COSMOS_DB_ENDPOINT = os.getenv("COSMOS_DB_ENDPOINT")
    COSMOS_DB_KEY = os.getenv("COSMOS_DB_KEY")
    
    # ========== Observability Configuration ==========
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = "chef_ai_agent.log"
    ENABLE_DETAILED_LOGGING = os.getenv("ENABLE_DETAILED_LOGGING", "true").lower() == "true"
    
    # TODO: For Azure Monitor integration
    # APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    # ========== System Prompts ==========
    SYSTEM_PROMPT = """You are ChefAI, an intelligent cooking assistant powered by Azure AI Foundry.

Your capabilities include:
- Recipe search with advanced filters (dietary restrictions, cuisine, cooking time, difficulty)
- Ingredient extraction and parsing from natural language
- Personalized recommendations based on user preferences and constraints
- Follow-up clarifications to refine recipe results
- Nutritional guidance and substitution suggestions

When interacting with users:
- Be warm, helpful, and conversational
- Ask clarifying questions when preferences are unclear
- Remember user constraints from earlier in the conversation
- Provide concise, actionable responses
- Use the available tools to fetch accurate information

Available tools:
- ingredient_extractor: Parse ingredients, quantities, and dietary constraints from text
- recipe_search: Search recipes with filters (diet, cuisine, time, difficulty)

Always use tools when appropriate to provide accurate, data-driven responses."""

    TOOL_SELECTION_PROMPT = """Based on the user's message and conversation context, determine which tool(s) to use:

1. Use 'ingredient_extractor' when:
   - User mentions ingredients they have
   - User provides a recipe text to parse
   - Need to extract dietary constraints or preferences

2. Use 'recipe_search' when:
   - User asks for recipe suggestions
   - User specifies cuisine, diet, time, or difficulty preferences
   - Need to find recipes matching criteria

3. Use both tools when:
   - User provides ingredients AND wants recipe suggestions
   
4. Use no tools when:
   - General cooking questions or tips
   - Clarifying user preferences
   - Simple follow-up responses"""

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.AZURE_OPENAI_ENDPOINT:
            errors.append(
                "AZURE_OPENAI_ENDPOINT not found. "
                "Get it from Azure AI Foundry Portal > Project Settings"
            )
        
        if not cls.AZURE_OPENAI_API_KEY:
            errors.append(
                "AZURE_OPENAI_API_KEY not found. "
                "Get it from Azure AI Foundry Portal > Project Settings"
            )
        
        if errors:
            raise ValueError(
                "Configuration errors:\n" + "\n".join(f"  - {err}" for err in errors) +
                "\n\nPlease set these in your .env file. See .env.example for reference."
            )
        
        return True
    
    @classmethod
    def get_azure_client_config(cls):
        """Get configuration dict for Azure OpenAI client"""
        return {
            "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT,
            "api_key": cls.AZURE_OPENAI_API_KEY,
            "api_version": cls.API_VERSION,
        }
