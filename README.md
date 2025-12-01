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
## 🎭 Orchestrator Options for Azure AI Foundry Agents

Azure AI Foundry already provides a native agent orchestrator.
You may optionally swap in external orchestrators depending on your needs.

### **Option 1: Managed / Native Azure AI Foundry Agent (Recommended / Default)**

**What it is:**
- Azure's built-in agent runtime
- Handles planning, memory, tool calling, context management, and multi-step reasoning
- No external framework required

**Use when:**
- ✅ You want the simplest, most Azure-aligned approach
- ✅ You want built-in multi-step tool calling
- ✅ You prefer serverless agent behavior
- ✅ You want minimal code and no orchestration maintenance

**Pros:**
- ✅ Automatic planning
- ✅ Built-in memory + tools
- ✅ Simplest architecture
- ✅ No extra dependencies

**Cons:**
- ❌ Less low-level control

---

### **Option 2: Semantic Kernel (Microsoft Orchestrator)**

**What it is:**
- Microsoft's agent framework with planners, memory connectors, skills, and deep Azure integrations

**Use when:**
- ✅ You want multi-step planning with more control than AI Foundry
- ✅ You need connectors (AI Search, Cosmos DB, Storage, SQL, etc.)
- ✅ Your org is already using Microsoft tooling
- ✅ You want a structured, enterprise-ready agent stack

**Pros:**
- ✅ Planners
- ✅ Built-in memory + safety

- ✅ Azure-native ecosystem

**Cons:**
- ❌ More dependencies
- ❌ More opinionated patterns

---

### **Option 3: LangChain (Open-Source Orchestrator)**

**What it is:**
- Large ecosystem for LLM apps, ideal for RAG-heavy agents and integrations

**Use when:**
- ✅ You need many integrations (Pinecone, Weaviate, loaders, crawlers)
- ✅ Your team already uses LangChain
- ✅ You're building complex RAG or retrieval workflows
- ✅ You want rapid prototyping

**Pros:**
- ✅ Huge ecosystem
- ✅ Excellent for RAG pipelines
- ✅ Many pre-built chains

**Cons:**
- ❌ Heavy dependencies
- ❌ Frequent version churn
- ❌ More complexity than needed for basic agents

---

### **Option 4: M365 Agent Toolkit (M365/Teams-Specific)**

**What it is:**
- Toolkit for building agents that operate inside Teams, Outlook, and other M365 apps

**Use when:**
- ✅ Your agent must run inside Teams/M365
- ✅ You need built-in connectors (Graph API, Calendar, Mail, SharePoint)
- ✅ You want M365 auth handled for you

**Pros:**
- ✅ Native Teams/Outlook integration
- ✅ Pre-built M365 connectors
- ✅ Handles authentication and card formats

**Cons:**
- ❌ Not suitable for general-purpose agents
- ❌ Tightly bound to M365 ecosystem

---

### **Option 5: Custom / Manual Orchestration (Not Recommended)**

**What it is:**
- You manually build the orchestration loop using the Azure Models API (ChatCompletions)
- You handle: planning, tool routing, memory, retries, context, validation—everything

**Use when:**
- ✅ You need extremely specialized control
- ✅ You're integrating with legacy systems
- ✅ You're experimenting or prototyping low-level LLM behavior

**Pros:**
- ✅ Full transparency and customization

**Cons:**
- ❌ Not recommended for production
- ❌ SK or LangChain do this far better
- ❌ High maintenance and complexity
- ❌ No built-in planning or memory

---

### **📊 Summary Table**

| Option | Orchestration Provided By | Best For | Multi-Step Planning | Dependencies |
|--------|---------------------------|----------|---------------------|------------|
| 1. Azure AI Foundry Agent | Azure | General agents, simplest path | Yes (built-in) | None |
| 2. Semantic Kernel | SK Planner | Enterprise + Azure-native apps | Yes | Semantic Kernel |
| 3. LangChain | LC AgentExecutor | RAG-heavy + integrations | Yes | LangChain |
| 4. M365 Agent Toolkit | Toolkit | Teams/M365 apps | Yes | M365 SDKs |
| 5. Custom Manual | You | Highly custom logic | No (you build it) | None |

---

## **Why This Project Uses Direct Azure OpenAI:**
1. **Educational**: Shows core agent patterns without framework magic
2. **Transparent**: You see exactly what happens at each step
3. **Flexible**: Easy to customize without fighting framework constraints
4. **Lightweight**: Minimal dependencies

**When to Switch to BYO Framework:**
- You need automatic multi-step planning
- You want framework-provided memory/telemetry instead of building it
- You need extensive integrations (LangChain's 300+ connectors)
- Your team prefers configuration over custom code

**How to Switch:** This project uses strategy pattern. To swap orchestrators: implement new class in `orchestrator.py`, change `ORCHESTRATOR_TYPE` in `.env`.

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

