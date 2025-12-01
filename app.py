"""
ChefAI - Azure AI Foundry Cooking Assistant Agent
Main application with chat loop, orchestrator wiring, and observability
"""

import sys
import logging
from datetime import datetime
from typing import Dict, Any

from config import Config
from orchestrator import OrchestratorFactory
from memory import MemoryFactory
from tools import ingredient_extractor, recipe_search

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class ChefAIAgent:
    """
    Main Chef AI Agent class.
    
    Architecture:
    - Orchestrator: Routes messages and manages tool calling
    - Tools: Ingredient extractor and recipe search
    - Memory: Maintains conversation state and preferences
    - Observability: Logs all interactions for monitoring
    """
    
    def __init__(self):
        """Initialize the Chef AI Agent"""
        logger.info("="*60)
        logger.info("Initializing ChefAI Agent")
        logger.info("="*60)
        
        try:
            # Validate configuration
            Config.validate()
            
            # Initialize orchestrator
            logger.info(f"Creating orchestrator: {Config.ORCHESTRATOR_TYPE}")
            self.orchestrator = OrchestratorFactory.create()
            
            # Initialize memory
            logger.info(f"Creating memory store: {Config.MEMORY_BACKEND}")
            self.memory = MemoryFactory.create()
            
            # Register available tools
            self.tools = {
                "ingredient_extractor": ingredient_extractor,
                "recipe_search": recipe_search
            }
            logger.info(f"Registered {len(self.tools)} tools: {list(self.tools.keys())}")
            
            self.running = True
            
            logger.info("ChefAI Agent initialized successfully")
            logger.info(f"Model: {Config.MODEL_DEPLOYMENT_NAME}")
            logger.info(f"Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
            
        except Exception as e:
            logger.error(f"Initialization failed: {str(e)}", exc_info=True)
            raise
    
    def display_welcome(self):
        """Display welcome message to user"""
        welcome = """
╔══════════════════════════════════════════════════════════════╗
║              🍳 Welcome to ChefAI! 🍳                       ║
║         Your Azure AI Foundry Cooking Assistant              ║
╚══════════════════════════════════════════════════════════════╝

I'm your intelligent cooking companion! I can help you with:

  🔍 Recipe Search
     • Find recipes by ingredients, cuisine, or dietary needs
     • Filter by cooking time and difficulty
     • Get personalized recommendations

  📝 Ingredient Extraction
     • Parse ingredients from recipe text
     • Identify quantities and measurements
     • Detect dietary constraints

  💡 Smart Recommendations
     • Remember your preferences across the conversation
     • Suggest recipes based on what you have
     • Provide cooking tips and substitutions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example prompts to try:
  • "Find gluten-free dinner recipes under 30 minutes"
  • "I have salmon, lemon, and asparagus"
  • "Show me easy vegan Italian recipes"
  • "What can I make that's dairy-free and Mediterranean?"

Type 'exit', 'quit', or 'bye' to end the session.
Type 'clear' to reset conversation memory.
Type 'preferences' to see your saved preferences.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        print(welcome)
        logger.info("Welcome message displayed")
    
    def process_special_commands(self, user_input: str) -> bool:
        """
        Handle special commands like exit, clear, preferences.
        
        Returns:
            True if a special command was handled, False otherwise
        """
        user_lower = user_input.lower().strip()
        
        # Exit commands
        if user_lower in ["exit", "quit", "bye", "goodbye"]:
            self._handle_exit()
            return True
        
        # Clear memory
        if user_lower == "clear":
            self.memory.clear()
            print("\n✅ Conversation memory cleared. Starting fresh!\n")
            logger.info("Memory cleared by user command")
            return True
        
        # Show preferences
        if user_lower == "preferences":
            self._show_preferences()
            return True
        
        # Show help
        if user_lower in ["help", "?"]:
            self._show_help()
            return True
        
        return False
    
    def _handle_exit(self):
        """Handle exit command"""
        metadata = self.memory.get_session_metadata()
        
        print("\n" + "="*60)
        print("🍳 Thank you for using ChefAI!")
        print("="*60)
        print(f"\nSession Summary:")
        print(f"  • Interactions: {metadata['interaction_count']}")
        print(f"  • Tools used: {', '.join(metadata['tools_used']) if metadata['tools_used'] else 'None'}")
        print(f"  • Session duration: Started {metadata['session_start']}")
        print("\nHappy cooking! 👨‍🍳👩‍🍳")
        print("="*60 + "\n")
        
        logger.info(f"Session ended. Summary: {metadata}")
        self.running = False
    
    def _show_preferences(self):
        """Display current user preferences"""
        prefs = self.memory.get_user_preferences()
        
        print("\n" + "="*60)
        print("Your Current Preferences:")
        print("="*60)
        
        if prefs["dietary_restrictions"]:
            print(f"  🥗 Dietary: {', '.join(prefs['dietary_restrictions'])}")
        else:
            print(f"  🥗 Dietary: No restrictions")
        
        if prefs["favorite_cuisines"]:
            print(f"  🌍 Cuisines: {', '.join(prefs['favorite_cuisines'])}")
        else:
            print(f"  🌍 Cuisines: No preferences set")
        
        if prefs["disliked_ingredients"]:
            print(f"  ❌ Dislikes: {', '.join(prefs['disliked_ingredients'])}")
        
        if prefs["time_constraints"]:
            print(f"  ⏱️  Max time: {prefs['time_constraints']} minutes")
        
        print(f"  👨‍🍳 Skill level: {prefs['cooking_skill_level']}")
        print(f"  🍽️  Servings: {prefs['servings_preference']}")
        
        print("="*60 + "\n")
    
    def _show_help(self):
        """Display help information"""
        help_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ChefAI Commands and Tips
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Special Commands:
  exit, quit, bye     - End the session
  clear               - Reset conversation memory
  preferences         - View your saved preferences
  help, ?             - Show this help message

Recipe Search Examples:
  "Find vegetarian pasta recipes"
  "Show me Mexican food under 30 minutes"
  "I need an easy gluten-free dinner"
  "What Asian recipes use chicken?"

Ingredient-Based Search:
  "I have tomatoes, basil, and mozzarella"
  "What can I make with salmon and asparagus?"
  "Recipes using quinoa and chickpeas"

Combining Filters:
  "Vegan Italian recipes under 25 minutes"
  "Easy dairy-free Mediterranean food"
  "Quick gluten-free Asian dishes"

Tips:
  • I remember your preferences across the conversation
  • Ask follow-up questions to refine results
  • Be specific about dietary needs and constraints
  • Mention time limits if you're in a hurry

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        print(help_text)
    
    def log_interaction(self, user_input: str, result: Dict[str, Any]):
        """
        Log interaction for observability.
        
        Logs:
        - User input
        - Selected tools and arguments
        - Model response
        - Decision rationale
        - Timestamp and metadata
        """
        if not Config.ENABLE_DETAILED_LOGGING:
            return
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "tools_called": [tc["tool"] for tc in result.get("tool_calls", [])],
            "tool_details": result.get("tool_calls", []),
            "rationale": result.get("rationale", ""),
            "response_length": len(result.get("response", ""))
        }
        
        logger.info("="*60)
        logger.info("INTERACTION LOG")
        logger.info("="*60)
        logger.info(f"User: {log_entry['user_input'][:100]}...")
        logger.info(f"Tools: {log_entry['tools_called']}")
        logger.info(f"Rationale: {log_entry['rationale']}")
        logger.info(f"Response length: {log_entry['response_length']} chars")
        
        if log_entry['tool_details']:
            for i, tool_call in enumerate(log_entry['tool_details'], 1):
                logger.info(f"  Tool {i}: {tool_call['tool']}")
                logger.info(f"    Args: {tool_call['arguments']}")
                logger.info(f"    Result: {str(tool_call.get('result', {}))[:200]}...")
        
        logger.info("="*60)
    
    def run(self):
        """Main chat loop"""
        self.display_welcome()
        
        logger.info("Entering main chat loop")
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                # Handle empty input
                if not user_input:
                    print("⚠️  Please enter a message.")
                    continue
                
                # Check for special commands
                if self.process_special_commands(user_input):
                    continue
                
                # Show processing indicator
                print("\n🤖 ChefAI: ", end="", flush=True)
                
                logger.info(f"Processing user input: {user_input[:100]}...")
                
                # Get conversation history for context
                conversation_history = self.memory.get_conversation_history()
                
                # Process message through orchestrator
                result = self.orchestrator.process_message(
                    user_message=user_input,
                    conversation_history=conversation_history,
                    available_tools=self.tools,
                    memory=self.memory
                )
                
                # Display response
                response = result.get("response", "I apologize, I couldn't process that request.")
                print(response)
                
                # Log interaction for observability
                self.log_interaction(user_input, result)
                
                # Store in memory
                self.memory.add_interaction(
                    user_message=user_input,
                    assistant_response=response,
                    metadata=result
                )
                
                logger.info("Interaction completed successfully")
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user")
                self._handle_exit()
                break
            
            except EOFError:
                print("\n\n⚠️  Input stream closed")
                self._handle_exit()
                break
            
            except Exception as e:
                logger.error(f"Error in chat loop: {str(e)}", exc_info=True)
                print(f"\n❌ An error occurred: {str(e)}")
                print("Please try again or type 'exit' to quit.")


def main():
    """Main entry point"""
    try:
        logger.info("Starting ChefAI application")
        
        # Create and run agent
        agent = ChefAIAgent()
        agent.run()
        
        logger.info("ChefAI application ended normally")
        
    except ValueError as e:
        # Configuration errors
        print("\n" + "="*60)
        print("❌ Configuration Error")
        print("="*60)
        print(f"\n{str(e)}\n")
        print("Please check your .env file and ensure all required")
        print("variables are set. See .env.example for reference.")
        print("\nSetup instructions:")
        print("  1. Copy .env.example to .env")
        print("  2. Get your Azure AI Foundry credentials")
        print("  3. Update AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY")
        print("  4. Run the application again")
        print("="*60 + "\n")
        
        logger.error(f"Configuration error: {str(e)}")
        sys.exit(1)
    
    except Exception as e:
        # Unexpected errors
        print("\n" + "="*60)
        print("❌ Fatal Error")
        print("="*60)
        print(f"\n{str(e)}\n")
        print("Check the log file for details: " + Config.LOG_FILE)
        print("="*60 + "\n")
        
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
