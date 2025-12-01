# 🍳 ChefAI - Azure AI Foundry Cooking Assistant

A sophisticated Python-based conversational AI agent for recipe search and ingredient extraction, powered by **Azure AI Foundry** with a clean, extensible architecture.

## ✨ Features

### 🔍 **Intelligent Recipe Search**
- Search by ingredients, cuisine, dietary restrictions
- Filter by cooking time and difficulty level
- Get personalized recommendations based on preferences

### 📝 **Ingredient Extraction**
- NER-style parsing with regex patterns
- LLM fallback for complex cases
- Automatic dietary constraint detection

### 🧠 **Conversation Memory**
- Maintains context across multiple turns
- Remembers dietary restrictions and preferences
- Auto-detects and stores user constraints

### 🎯 **Clean Architecture**
- **Orchestrator**: Strategy pattern for swappable orchestration (Managed, Semantic Kernel, LangChain)
- **Tools**: Modular, extensible tool system
- **Memory**: Pluggable memory backends (In-Memory, Redis, Cosmos DB)
- **Observability**: Comprehensive logging for monitoring

---

## 🎭 Orchestrator Options: Understanding Your Choices

This Azure AI Foundry agent supports **both Managed and Bring Your Own Orchestrator (BYO)** patterns. You decide which orchestration approach fits your needs.

### **Option 1: Managed Orchestrator (Current Default)**

**What it is:**
- Uses Azure AI Foundry's native function calling capabilities
- Simple, direct integration with Azure OpenAI API
- No external orchestration frameworks required
- Minimal dependencies, maximum control

**When to use:**
- ✅ You want simplicity and direct Azure AI Foundry integration
- ✅ You're building a new agent from scratch
- ✅ You need full control over orchestration logic
- ✅ You want to minimize external dependencies
- ✅ Your team is comfortable with raw OpenAI API patterns

**Why this approach:**
- Direct access to Azure AI Foundry capabilities
- No framework lock-in
- Easier to debug and customize
- Lower learning curve if familiar with OpenAI APIs
- **This is "Managed"** in the sense that Azure handles the orchestration logic natively

---

### **Option 2: BYO Orchestrator - Semantic Kernel**

**What it is:**
- Microsoft's official SDK for building AI agents
- Native Azure integration with enterprise features
- Planner-based orchestration with automatic reasoning

**When to use:**
- ✅ You're building enterprise Microsoft solutions
- ✅ You need seamless Azure service integration
- ✅ You want automatic multi-step planning capabilities
- ✅ Your organization standardizes on Microsoft SDKs
- ✅ You need built-in memory, telemetry, and safety features

**Trade-offs:**
- More opinionated framework
- Additional abstraction layer
- Steeper learning curve for Semantic Kernel concepts
- Better for complex multi-agent scenarios
**How to switch:** See "Swap Orchestrator to Semantic Kernel" section below.

---

### **Option 3: BYO Orchestrator - LangChain**
### **Option 2: LangChain Orchestrator**

**What it is:**
- Popular open-source framework for LLM applications
- Rich ecosystem of integrations and tools
- Chain-based orchestration with LCEL (LangChain Expression Language)

**When to use:**
- ✅ You need extensive third-party integrations (vector DBs, APIs, tools)
- ✅ Your team already uses LangChain in other projects
- ✅ You want access to LangChain's large community and examples
- ✅ You're building complex RAG (Retrieval Augmented Generation) pipelines
- ✅ You need quick prototyping with pre-built components

**Trade-offs:**
- Heavier dependency footprint
- Can be over-engineered for simple scenarios
- Abstraction may hide Azure-specific optimizations
- Framework updates can introduce breaking changes

**How to switch:** See "Swap Orchestrator to LangChain" section below.

---

### **Option 4: M365 Agent Toolkit (Different Architecture)**

**What it is:**
- Microsoft 365-focused agent development toolkit
- Integrates with Teams, SharePoint, Outlook, and other M365 services
- Pre-built templates for M365-specific agent patterns

**When to use:**
- ✅ You're building agents for Microsoft Teams or M365 environments
- ✅ You need M365 authentication and permissions integration
- ✅ You want pre-built M365 connectors (calendars, emails, documents)
- ✅ Your use case is primarily M365-centric workflows

**Why this is different:**
- **M365 Toolkit** is optimized for M365 environments with built-in connectors
- **This project (ChefAI)** is a general-purpose Azure AI Foundry agent
- To make this an M365 agent, you'd need:
  1. Install M365 Toolkit SDK
  2. Add M365 authentication (MSAL, Azure AD)
  3. Register agent in Teams/M365 developer portal
  4. Implement M365-specific tool adapters
  5. Handle M365 messaging and card formats

**Trade-offs:**
- More setup overhead for non-M365 scenarios
- Tightly coupled to M365 ecosystem
- May not be ideal for standalone web/API agents

**Note:** If your goal is M365 integration, consider starting with the M365 Agent Toolkit templates rather than retrofitting this codebase.

---

### **Understanding "Managed" vs "BYO Orchestrator"**

**Managed Orchestrator:**
- Azure AI Foundry handles the orchestration natively
- You use the platform's built-in function calling
- Orchestration logic is straightforward: call LLM → detect tool needs → execute tools → synthesize response
- **This is the default in this project**

**Bring Your Own Orchestrator (BYO):**
- You plug in an external framework (Semantic Kernel, LangChain)
- The framework handles orchestration logic, planning, and tool execution
- More features but more complexity
- **Options 2 & 3 above (Semantic Kernel, LangChain)**

**Key Point:** This project is designed to support **BOTH** patterns. We implement Managed by default, but the strategy pattern architecture lets you swap to BYO frameworks easily.

---

### **Decision Matrix: Which Orchestrator Should You Choose?**

| Scenario | Recommended Choice | Pattern |
|----------|-------------------|---------|
| Simple agent, direct Azure control | **Managed** ⭐ | Managed |
| Enterprise Microsoft solution | **Semantic Kernel** | BYO |
| Need many third-party integrations | **LangChain** | BYO |
| Microsoft Teams/M365 agent | **M365 Agent Toolkit** | Different Architecture |
| Learning AI agents for first time | **Managed** ⭐ | Managed |
| Complex multi-agent system | **Semantic Kernel** | BYO |
| Quick prototype with existing components | **LangChain** | BYO |
| Maximum flexibility, minimum dependencies | **Managed** ⭐ | Managed |

---

### **Why We Chose "Managed" as Default**

1. **Simplicity**: Direct Azure AI Foundry integration without framework overhead
2. **Transparency**: See exactly what's happening—no "magic" abstractions
3. **Flexibility**: Easy to customize without fighting framework constraints
4. **Educational Value**: Understand core AI agent patterns before adopting frameworks
5. **Production-Ready**: Proven approach used by many Azure AI applications
6. **True "Managed"**: Let Azure handle orchestration natively

**The Philosophy**: 
- Start with **Managed** (Azure-native orchestration)
- Graduate to **BYO** (Semantic Kernel/LangChain) when complexity demands it
- Choose **M365 Toolkit** only if building M365-specific agents

---

### **Future Roadmap: M365 Integration**

**Vision:** Extend this Azure AI Foundry agent to work natively within Microsoft 365 environments (Teams, Outlook, SharePoint) while maintaining the current architecture.

**Why This Matters:**
- Keep the clean orchestrator pattern we've built
- Add M365 as a deployment target, not a replacement
- Enable the agent to work in chat interfaces where users already are
- Access M365 data (emails, calendars, documents) as additional context

**Planned Approach:**
1. Maintain current Azure AI Foundry core
2. Add M365 authentication layer (Azure AD/Entra ID)
3. Implement M365 message adapters (Teams cards, Outlook actionable messages)
4. Create M365-specific tools (calendar lookup, email search, document retrieval)
5. Deploy as Teams app or Outlook add-in

**What This Means:**
- **Same agent logic** (orchestrator, tools, memory)
- **Multiple interfaces** (CLI, Teams, Outlook, web)
- **M365 as a channel**, not a rewrite

📋 **Detailed implementation guide:** See `docs/m365-integration-guide.md` for step-by-step instructions.

---

## 📁 Project Structure

```
A365Agent/
│
├── app.py                          # Main application with chat loop
├── config.py                       # Configuration and settings
├── orchestrator.py                 # Orchestrator interface + implementations
├── memory.py                       # Memory storage interface + implementations
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .env                           # Your credentials (not in git)
│
├── tools/                         # Tool implementations
│   ├── __init__.py
│   ├── ingredient_extractor.py    # Ingredient parsing tool
│   └── recipe_search.py           # Recipe search tool
│
├── data/                          # Data files
│   └── recipes.json               # Sample recipe dataset (18 recipes)
│
└── README.md                      # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Azure AI Foundry project with deployed model
- Azure OpenAI API credentials

### Installation

1. **Clone or navigate to the project**
   ```powershell
   cd c:\Usha\UKRepos\A365Agent
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Copy the example file:
   ```powershell
   Copy-Item .env.example .env
   ```

   Edit `.env` and add your Azure AI Foundry credentials:
   ```env
   AZURE_OPENAI_ENDPOINT=https://your-foundry-project.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_api_key_here
   MODEL_DEPLOYMENT_NAME=gpt-4
   ```

   **How to get your credentials:**
   - Go to [Azure AI Foundry Portal](https://ai.azure.com/)
   - Select your project
   - Navigate to **Settings** > **Endpoints**
   - Copy the endpoint URL and API key
   - Note your model deployment name

### Run the Application

```powershell
python app.py
```

---

## 💬 Usage Examples

### Recipe Search by Filters
```
You: Find gluten-free dinner recipes under 30 minutes
ChefAI: I found several great gluten-free options that can be made quickly...
```

### Ingredient-Based Search
```
You: I have salmon, lemon, and asparagus
ChefAI: Based on those ingredients, I recommend...
```

### Multi-Turn Conversation
```
You: Show me vegan Italian recipes
ChefAI: Here are some delicious vegan Italian dishes...

You: Make it under 25 minutes
ChefAI: Filtering for quick options under 25 minutes...
```

### Dietary Refinement
```
You: Find me pasta recipes
ChefAI: Here are some pasta options...

You: Make it dairy-free
ChefAI: Here are dairy-free pasta recipes...
```

### Special Commands

- `exit`, `quit`, `bye` - End the session
- `clear` - Reset conversation memory
- `preferences` - View saved preferences
- `help` - Show help information

---

## 🏗️ Architecture

### Orchestrator Pattern

The orchestrator uses a **strategy pattern** for swappable implementations:

```python
# Default: Managed orchestrator with Azure OpenAI function calling
orchestrator = ManagedOrchestrator()

# Future: Swap to Semantic Kernel
orchestrator = SemanticKernelOrchestrator()

# Future: Swap to LangChain
orchestrator = LangChainOrchestrator()
```

**Current Implementation:**
- `ManagedOrchestrator`: Uses native Azure OpenAI function calling
- Handles tool selection, execution, and response synthesis
- No external orchestration framework required

**Extensibility:** See `orchestrator.py` for implementation guides for Semantic Kernel and LangChain.

### Tool System

Tools are self-describing functions with OpenAI function schemas:

```python
# Each tool has a schema for the LLM
ingredient_extractor.schema = {
    "type": "function",
    "function": {
        "name": "ingredient_extractor",
        "description": "Extract ingredients and dietary constraints from text",
        "parameters": {...}
    }
}
```

**Available Tools:**

1. **ingredient_extractor**
   - Regex-based parsing for speed
   - LLM fallback for complex cases
   - Detects dietary constraints automatically

2. **recipe_search**
   - Searches local JSON dataset
   - Filters: ingredients, diet, cuisine, time, difficulty
   - Returns up to 5 matching recipes

**Add New Tools:**
1. Create tool function in `tools/`
2. Add OpenAI function schema
3. Register in `app.py`

### Memory System

Pluggable memory backends:

```python
# Default: In-memory (development)
memory = InMemoryStore()

# Production: Redis (persistent, distributed)
memory = RedisMemory()

# Production: Cosmos DB (Azure, globally distributed)
memory = CosmosDBMemory()
```

**Memory Features:**
- Conversation history with timestamp
- User preferences (dietary, cuisine, time constraints)
- Auto-extraction of preferences from conversation
- Session metadata and statistics

**Switch Memory Backend:**
Set in `.env`:
```env
MEMORY_BACKEND=in_memory  # or redis, cosmos_db
```

### Observability

All interactions are logged with:
- User input and timestamp
- Selected tools and arguments
- Tool execution results
- Model response and rationale
- Decision reasoning

**Log Levels:**
```env
LOG_LEVEL=INFO              # INFO, DEBUG, WARNING, ERROR
ENABLE_DETAILED_LOGGING=true
```

Logs are written to:
- Console (stdout)
- File: `chef_ai_agent.log`

**Future:** Integrate with Azure Monitor for production observability.

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | ✅ | Azure AI Foundry endpoint URL | `https://your-project.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | ✅ | Azure OpenAI API key | Your API key |
| `MODEL_DEPLOYMENT_NAME` | ✅ | Model deployment name | `gpt-4`, `gpt-35-turbo` |
| `API_VERSION` | ❌ | API version | `2024-08-01-preview` |
| `ORCHESTRATOR_TYPE` | ❌ | Orchestrator backend | `managed`, `semantic_kernel`, `langchain` |
| `MEMORY_BACKEND` | ❌ | Memory storage | `in_memory`, `redis`, `cosmos_db` |
| `LOG_LEVEL` | ❌ | Logging level | `INFO`, `DEBUG` |

### Model Configuration

Adjust in `config.py`:

```python
MAX_CONVERSATION_HISTORY = 10    # Number of turns to keep
TEMPERATURE = 0.7                # Model creativity (0.0-1.0)
MAX_TOKENS = 1500                # Max response length
MAX_RECIPE_RESULTS = 5           # Recipes returned per search
```

---

## 🔌 Extensibility

### Swap Orchestrator to Semantic Kernel

1. **Install Semantic Kernel:**
   ```powershell
   pip install semantic-kernel
   ```

2. **Uncomment implementation in `orchestrator.py`:**
   ```python
   class SemanticKernelOrchestrator(Orchestrator):
       # Implementation provided in comments
   ```

3. **Update config:**
   ```env
   ORCHESTRATOR_TYPE=semantic_kernel
   ```

### Swap Orchestrator to LangChain

1. **Install LangChain:**
   ```powershell
   pip install langchain langchain-openai
   ```

2. **Uncomment implementation in `orchestrator.py`:**
   ```python
   class LangChainOrchestrator(Orchestrator):
       # Implementation provided in comments
   ```

3. **Update config:**
   ```env
   ORCHESTRATOR_TYPE=langchain
   ```

### Integrate External Recipe API

**Replace local search with Spoonacular API:**

1. **Get API key:** Sign up at [Spoonacular](https://spoonacular.com/food-api)

2. **Add to `.env`:**
   ```env
   SPOONACULAR_API_KEY=your_api_key
   ```

3. **Update `tools/recipe_search.py`:**
   ```python
   import requests
   
   def recipe_search(...):
       api_key = Config.SPOONACULAR_API_KEY
       url = "https://api.spoonacular.com/recipes/complexSearch"
       
       params = {
           "apiKey": api_key,
           "includeIngredients": ",".join(ingredients) if ingredients else None,
           "diet": dietary_restrictions[0] if dietary_restrictions else None,
           # ... other params
       }
       
       response = requests.get(url, params=params)
       return format_results(response.json())
   ```

See detailed guide in `tools/recipe_search.py`.

### Add Redis Memory Backend

1. **Install Redis:**
   ```powershell
   pip install redis
   ```

2. **Start Redis:**
   ```powershell
   docker run -d -p 6379:6379 redis
   ```

3. **Uncomment implementation in `memory.py`:**
   ```python
   class RedisMemory(Memory):
       # Implementation provided in comments
   ```

4. **Configure:**
   ```env
   MEMORY_BACKEND=redis
   REDIS_URL=redis://localhost:6379
   ```

### Add Cosmos DB Memory Backend

1. **Install Cosmos SDK:**
   ```powershell
   pip install azure-cosmos
   ```

2. **Create Cosmos DB in Azure Portal**

3. **Uncomment implementation in `memory.py`:**
   ```python
   class CosmosDBMemory(Memory):
       # Implementation provided in comments
   ```

4. **Configure:**
   ```env
   MEMORY_BACKEND=cosmos_db
   COSMOS_DB_ENDPOINT=https://your-cosmos.documents.azure.com:443/
   COSMOS_DB_KEY=your_cosmos_key
   ```

---

## 🧪 Testing

### Test Individual Components

**Test ingredient extractor:**
```powershell
python -m tools.ingredient_extractor
```

**Test recipe search:**
```powershell
python -m tools.recipe_search
```

### Test with Sample Prompts

```
Find gluten-free dinner in under 30 minutes
I have salmon, lemon, and asparagus
Make it dairy-free and Mediterranean
Show me easy vegan recipes
What can I cook with chicken and rice?
```

---

## 📊 Observability

### Log Analysis

View detailed logs:
```powershell
Get-Content chef_ai_agent.log -Tail 50
```

Filter by level:
```powershell
Select-String -Path chef_ai_agent.log -Pattern "ERROR"
```

### Metrics Tracked

- Interaction count
- Tools used per session
- Response times
- Tool call frequency
- Error rates

### Future: Azure Monitor Integration

Uncomment in `config.py`:
```python
APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
```

Install SDK:
```powershell
pip install azure-monitor-opentelemetry
```

---

## 🛠️ Troubleshooting

### Configuration Errors

**Error: "AZURE_OPENAI_ENDPOINT not found"**
- Ensure `.env` file exists (copy from `.env.example`)
- Check environment variable names match exactly
- Verify no extra spaces or quotes

**Error: "Model deployment not found"**
- Check your model deployment name in Azure AI Foundry
- Ensure the model is deployed and running
- Verify the name matches exactly in `.env`

### Runtime Errors

**Error: "Tool schema missing"**
- Ensure tool functions have `.schema` attribute
- Check schema format matches OpenAI function calling spec

**Slow responses:**
- Reduce `MAX_TOKENS` in config
- Use a faster model (e.g., `gpt-35-turbo` instead of `gpt-4`)
- Check network latency to Azure

### Memory Issues

**Conversation context lost:**
- Check `MAX_CONVERSATION_HISTORY` setting
- Verify memory backend is initialized
- Use `preferences` command to check stored data

---

## 📚 Additional Resources

- [Azure AI Foundry Documentation](https://learn.microsoft.com/azure/ai-studio/)
- [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)
- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Semantic Kernel](https://learn.microsoft.com/semantic-kernel/)
- [LangChain](https://python.langchain.com/)

---

## 📝 License

This project is provided as-is for educational and development purposes.

---

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional tools (nutrition lookup, meal planning)
- More orchestrator implementations
- Enhanced observability and monitoring
- UI/Web interface
- Voice input/output
- Multi-user support

---

**Happy Cooking with ChefAI! 🍳👨‍🍳👩‍🍳**
