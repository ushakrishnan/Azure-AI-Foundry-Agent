# M365 Integration Implementation Guide

## Overview

This guide provides a detailed roadmap for extending the ChefAI Azure AI Foundry agent to work within Microsoft 365 environments (Teams, Outlook, SharePoint) while maintaining the current clean architecture.

**Goal:** Add M365 as a deployment channel without replacing the existing agent core.

---

## Architecture Approach

### Current State
```
User Input (CLI) → Orchestrator → Tools → Memory → Response (CLI)
                         ↓
                  Azure AI Foundry
```

### Target State
```
User Input (CLI/Teams/Outlook) → M365 Adapter → Orchestrator → Tools → Memory → Response Formatter → Output (CLI/Teams Card/Email)
                                                        ↓
                                                 Azure AI Foundry
                                                        ↓
                                                 M365 Graph API (optional)
```

**Key Principle:** The orchestrator, tools, and memory remain unchanged. We add adapters on input/output.

---

## Implementation Phases

### **Phase 1: Authentication & Authorization (Week 1-2)**

#### 1.1 Azure AD App Registration

**Steps:**
1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Create new registration:
   - Name: `ChefAI-M365-Agent`
   - Supported account types: `Accounts in this organizational directory only`
   - Redirect URI: `https://localhost:5000/auth/callback` (for local testing)

3. Configure API permissions:
   - Microsoft Graph API:
     - `User.Read` (delegated) - Basic user profile
     - `Calendars.Read` (delegated) - For calendar tool
     - `Mail.Read` (delegated) - For email tool
     - `Files.Read.All` (delegated) - For document tool
     - `Chat.ReadWrite` (delegated) - For Teams messages
   
4. Grant admin consent for the organization

5. Create client secret:
   - Certificates & secrets → New client secret
   - Description: `ChefAI-M365-Secret`
   - Expires: 24 months
   - **Save the secret value immediately**

**Configuration:**
Add to `.env`:
```env
# M365 Integration
M365_ENABLED=true
M365_CLIENT_ID=your_app_client_id
M365_CLIENT_SECRET=your_client_secret
M365_TENANT_ID=your_tenant_id
M365_REDIRECT_URI=https://localhost:5000/auth/callback
```

#### 1.2 Implement MSAL Authentication

**File:** `m365/auth.py`

```python
from msal import ConfidentialClientApplication
from config import Config

class M365Auth:
    def __init__(self):
        self.app = ConfidentialClientApplication(
            Config.M365_CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{Config.M365_TENANT_ID}",
            client_credential=Config.M365_CLIENT_SECRET
        )
    
    def get_auth_url(self):
        """Generate OAuth2 authorization URL"""
        return self.app.get_authorization_request_url(
            scopes=Config.M365_SCOPES,
            redirect_uri=Config.M365_REDIRECT_URI
        )
    
    def acquire_token(self, auth_code):
        """Exchange authorization code for access token"""
        result = self.app.acquire_token_by_authorization_code(
            auth_code,
            scopes=Config.M365_SCOPES,
            redirect_uri=Config.M365_REDIRECT_URI
        )
        return result.get("access_token")
    
    def acquire_token_silent(self, account):
        """Get token from cache or refresh"""
        result = self.app.acquire_token_silent(
            scopes=Config.M365_SCOPES,
            account=account
        )
        return result.get("access_token")
```

**Dependencies to add:**
```bash
pip install msal msgraph-sdk
```

---

### **Phase 2: M365 Message Adapters (Week 2-3)**

#### 2.1 Teams Bot Framework Integration

**File:** `m365/adapters/teams_adapter.py`

```python
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import Activity, ActivityTypes

class TeamsAdapter(ActivityHandler):
    """Adapter for Microsoft Teams bot interface"""
    
    def __init__(self, chef_agent):
        self.agent = chef_agent
        super().__init__()
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming Teams message"""
        # Extract user message
        user_message = turn_context.activity.text
        user_id = turn_context.activity.from_property.id
        
        # Get agent response (same orchestrator logic)
        result = self.agent.orchestrator.process_message(
            user_message=user_message,
            conversation_history=self.agent.memory.get_conversation_history(),
            available_tools=self.agent.tools,
            memory=self.agent.memory
        )
        
        # Format response as Teams card
        card = self._create_adaptive_card(result)
        
        # Send response
        await turn_context.send_activity(Activity(
            type=ActivityTypes.message,
            attachments=[card]
        ))
        
        # Store in memory
        self.agent.memory.add_interaction(
            user_message=user_message,
            assistant_response=result['response'],
            metadata={'channel': 'teams', 'user_id': user_id}
        )
    
    def _create_adaptive_card(self, result):
        """Format agent response as Teams Adaptive Card"""
        card_json = {
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "🍳 ChefAI",
                    "weight": "bolder",
                    "size": "large"
                },
                {
                    "type": "TextBlock",
                    "text": result['response'],
                    "wrap": True
                }
            ]
        }
        
        # Add recipe cards if tools returned recipes
        if result.get('tool_calls'):
            for tool_call in result['tool_calls']:
                if tool_call['tool'] == 'recipe_search':
                    recipes = tool_call['result'].get('recipes', [])
                    for recipe in recipes[:3]:  # Show top 3
                        card_json['body'].append({
                            "type": "Container",
                            "items": [
                                {
                                    "type": "TextBlock",
                                    "text": recipe['title'],
                                    "weight": "bolder"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"⏱️ {recipe['time_minutes']} min | "
                                           f"👨‍🍳 {recipe['difficulty']} | "
                                           f"🍽️ {recipe['servings']} servings",
                                    "isSubtle": True,
                                    "spacing": "none"
                                }
                            ]
                        })
        
        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive",
            content=card_json
        )
```

**Teams Bot Setup:**
1. Create bot in [Azure Portal](https://portal.azure.com):
   - Create resource → Bot Service
   - Choose messaging endpoint: `https://your-app.azurewebsites.net/api/messages`
   - Link to Azure AD app created in Phase 1

2. Register bot in Teams:
   - Teams Developer Portal → Apps → New app
   - Add bot capabilities
   - Configure bot ID and scopes

3. Create Teams app manifest (`teams-manifest.json`):
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/teams/v1.16/MicrosoftTeams.schema.json",
  "manifestVersion": "1.16",
  "version": "1.0.0",
  "id": "your-app-id",
  "packageName": "com.chefai.teamsbot",
  "developer": {
    "name": "Your Organization",
    "websiteUrl": "https://your-website.com",
    "privacyUrl": "https://your-website.com/privacy",
    "termsOfUseUrl": "https://your-website.com/terms"
  },
  "name": {
    "short": "ChefAI",
    "full": "ChefAI Cooking Assistant"
  },
  "description": {
    "short": "AI cooking assistant",
    "full": "Azure AI Foundry-powered cooking assistant for recipe search and ingredient extraction"
  },
  "icons": {
    "outline": "outline.png",
    "color": "color.png"
  },
  "accentColor": "#FF6B6B",
  "bots": [
    {
      "botId": "your-bot-id",
      "scopes": ["personal", "team"],
      "supportsFiles": false,
      "isNotificationOnly": false,
      "commandLists": [
        {
          "scopes": ["personal", "team"],
          "commands": [
            {
              "title": "help",
              "description": "Show help information"
            },
            {
              "title": "preferences",
              "description": "View your cooking preferences"
            }
          ]
        }
      ]
    }
  ],
  "permissions": ["identity", "messageTeamMembers"],
  "validDomains": []
}
```

#### 2.2 Outlook Add-in Integration

**File:** `m365/adapters/outlook_adapter.py`

```python
class OutlookAdapter:
    """Adapter for Outlook actionable messages"""
    
    def __init__(self, chef_agent):
        self.agent = chef_agent
    
    def create_actionable_message(self, result):
        """Format agent response as Outlook actionable message"""
        card = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": "ChefAI Recipe Suggestions",
            "themeColor": "FF6B6B",
            "sections": [
                {
                    "activityTitle": "🍳 ChefAI",
                    "activitySubtitle": "Your cooking assistant",
                    "activityImage": "https://your-cdn.com/chef-icon.png",
                    "text": result['response']
                }
            ]
        }
        
        # Add action buttons
        if result.get('tool_calls'):
            card['potentialAction'] = [
                {
                    "@type": "ActionCard",
                    "name": "View Recipe Details",
                    "inputs": [
                        {
                            "@type": "TextInput",
                            "id": "recipe_id",
                            "title": "Select recipe"
                        }
                    ],
                    "actions": [
                        {
                            "@type": "HttpPOST",
                            "name": "Get Details",
                            "target": "https://your-api.com/recipes/details"
                        }
                    ]
                }
            ]
        
        return card
```

**Outlook Add-in Manifest (`outlook-manifest.xml`):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<OfficeApp xmlns="http://schemas.microsoft.com/office/appforoffice/1.1">
  <Id>your-add-in-id</Id>
  <Version>1.0.0.0</Version>
  <ProviderName>Your Organization</ProviderName>
  <DefaultLocale>en-US</DefaultLocale>
  <DisplayName DefaultValue="ChefAI Assistant" />
  <Description DefaultValue="AI cooking assistant for Outlook" />
  <IconUrl DefaultValue="https://your-cdn.com/icon-32.png" />
  <HighResolutionIconUrl DefaultValue="https://your-cdn.com/icon-64.png" />
  <SupportUrl DefaultValue="https://your-website.com/support" />
  <Hosts>
    <Host Name="Mailbox" />
  </Hosts>
  <Requirements>
    <Sets>
      <Set Name="Mailbox" MinVersion="1.1" />
    </Sets>
  </Requirements>
  <FormSettings>
    <Form xsi:type="ItemRead">
      <DesktopSettings>
        <SourceLocation DefaultValue="https://your-app.com/outlook-addin.html" />
        <RequestedHeight>250</RequestedHeight>
      </DesktopSettings>
    </Form>
  </FormSettings>
  <Permissions>ReadWriteMailbox</Permissions>
  <Rule xsi:type="RuleCollection" Mode="Or">
    <Rule xsi:type="ItemIs" ItemType="Message" FormType="Read" />
  </Rule>
</OfficeApp>
```

---

### **Phase 3: M365-Specific Tools (Week 3-4)**

#### 3.1 Calendar Tool

**File:** `m365/tools/calendar_tool.py`

```python
from msgraph import GraphServiceClient
from azure.identity import ClientSecretCredential

class CalendarTool:
    """Tool to search user's calendar for meal planning"""
    
    schema = {
        "type": "function",
        "function": {
            "name": "calendar_search",
            "description": "Search user's calendar to suggest recipes based on free time and scheduled meals",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_range": {
                        "type": "string",
                        "description": "Date range to search (e.g., 'this week', 'today')"
                    },
                    "max_cooking_time": {
                        "type": "integer",
                        "description": "Maximum cooking time based on calendar availability"
                    }
                },
                "required": ["date_range"]
            }
        }
    }
    
    def __init__(self, access_token):
        self.client = GraphServiceClient(
            credential=access_token,
            scopes=['https://graph.microsoft.com/.default']
        )
    
    async def execute(self, date_range: str, max_cooking_time: int = None):
        """Get calendar events and calculate available cooking time"""
        # Get calendar events
        events = await self.client.me.calendar_view.get(
            start_date_time=self._parse_date_range(date_range)['start'],
            end_date_time=self._parse_date_range(date_range)['end']
        )
        
        # Calculate free time blocks
        free_blocks = self._calculate_free_time(events)
        
        # Return context for recipe suggestions
        return {
            "free_time_blocks": free_blocks,
            "suggested_max_cooking_time": max_cooking_time or self._estimate_cooking_time(free_blocks),
            "scheduled_meals": self._extract_meal_events(events)
        }
```

#### 3.2 Email/Recipe History Tool

**File:** `m365/tools/email_tool.py`

```python
class EmailRecipeTool:
    """Tool to search emails for previously shared recipes"""
    
    schema = {
        "type": "function",
        "function": {
            "name": "email_recipe_search",
            "description": "Search user's emails for previously received or shared recipes",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to search for in emails"
                    }
                },
                "required": ["keywords"]
            }
        }
    }
    
    async def execute(self, keywords: list):
        """Search emails for recipe content"""
        # Build search query
        query = " AND ".join([f"subject:{kw}" for kw in keywords])
        
        # Search emails
        messages = await self.client.me.messages.get(
            filter=f"contains(subject, 'recipe')",
            search=query,
            top=10
        )
        
        # Extract recipe information
        recipes = []
        for message in messages.value:
            recipes.append({
                "subject": message.subject,
                "from": message.from_property.email_address.address,
                "date": message.received_date_time,
                "snippet": message.body_preview
            })
        
        return {"found_recipes": recipes}
```

#### 3.3 SharePoint Document Tool

**File:** `m365/tools/sharepoint_tool.py`

```python
class SharePointRecipeTool:
    """Tool to access recipe documents from SharePoint"""
    
    schema = {
        "type": "function",
        "function": {
            "name": "sharepoint_recipe_search",
            "description": "Search SharePoint for recipe documents and cookbooks",
            "parameters": {
                "type": "object",
                "properties": {
                    "site_url": {
                        "type": "string",
                        "description": "SharePoint site URL"
                    },
                    "search_term": {
                        "type": "string",
                        "description": "Search term for recipes"
                    }
                },
                "required": ["search_term"]
            }
        }
    }
    
    async def execute(self, search_term: str, site_url: str = None):
        """Search SharePoint for recipe documents"""
        # Get site
        site = await self.client.sites.get_by_url(site_url or "root")
        
        # Search documents
        results = await site.drive.search(search_term).get()
        
        # Filter for recipe-related documents
        recipe_docs = []
        for item in results.value:
            if self._is_recipe_document(item):
                recipe_docs.append({
                    "name": item.name,
                    "url": item.web_url,
                    "last_modified": item.last_modified_date_time
                })
        
        return {"documents": recipe_docs}
```

---

### **Phase 4: Deployment & Hosting (Week 4-5)**

#### 4.1 Azure App Service Deployment

**File:** `azure-deploy.yaml` (Azure Pipelines)

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  azureSubscription: 'your-subscription'
  webAppName: 'chefai-m365-bot'
  pythonVersion: '3.11'

stages:
- stage: Build
  jobs:
  - job: BuildJob
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
    
    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
      displayName: 'Install dependencies'
    
    - task: ArchiveFiles@2
      inputs:
        rootFolderOrFile: '$(System.DefaultWorkingDirectory)'
        includeRootFolder: false
        archiveType: 'zip'
        archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
    
    - publish: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
      artifact: drop

- stage: Deploy
  jobs:
  - deployment: DeployWeb
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureWebApp@1
            inputs:
              azureSubscription: '$(azureSubscription)'
              appName: '$(webAppName)'
              package: '$(Pipeline.Workspace)/drop/$(Build.BuildId).zip'
```

#### 4.2 Bot Service Configuration

**File:** `bot_app.py` (Flask/FastAPI endpoint)

```python
from flask import Flask, request, Response
from botbuilder.core import BotFrameworkAdapter, TurnContext
from botbuilder.schema import Activity
from m365.adapters.teams_adapter import TeamsAdapter
from app import ChefAIAgent

app = Flask(__name__)

# Initialize bot adapter
adapter = BotFrameworkAdapter(settings)

# Initialize ChefAI agent
chef_agent = ChefAIAgent()
teams_bot = TeamsAdapter(chef_agent)

@app.route('/api/messages', methods=['POST'])
async def messages():
    """Endpoint for Teams messages"""
    body = request.json
    activity = Activity().deserialize(body)
    
    auth_header = request.headers.get('Authorization', '')
    
    async def call_bot(turn_context: TurnContext):
        await teams_bot.on_turn(turn_context)
    
    await adapter.process_activity(activity, auth_header, call_bot)
    return Response(status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3978)
```

---

### **Phase 5: Testing & Validation (Week 5-6)**

#### 5.1 Unit Tests

**File:** `tests/test_m365_integration.py`

```python
import pytest
from m365.adapters.teams_adapter import TeamsAdapter
from m365.tools.calendar_tool import CalendarTool

@pytest.mark.asyncio
async def test_teams_adapter_message():
    """Test Teams message handling"""
    agent = ChefAIAgent()
    adapter = TeamsAdapter(agent)
    
    # Simulate Teams message
    context = create_mock_turn_context("Find vegan recipes")
    
    await adapter.on_message_activity(context)
    
    # Verify response
    assert context.sent_activities
    assert "recipe" in context.sent_activities[0].text.lower()

@pytest.mark.asyncio
async def test_calendar_tool():
    """Test calendar integration"""
    tool = CalendarTool(mock_access_token)
    
    result = await tool.execute(date_range="today")
    
    assert "free_time_blocks" in result
    assert isinstance(result["free_time_blocks"], list)
```

#### 5.2 Integration Testing

1. **Local Testing:**
   ```bash
   # Use ngrok to expose local endpoint
   ngrok http 3978
   
   # Update bot messaging endpoint in Azure Portal
   # Test with Teams desktop client
   ```

2. **Teams App Studio Testing:**
   - Upload app package to Teams
   - Test in personal chat
   - Test in team channel
   - Verify adaptive cards render correctly

3. **Outlook Testing:**
   - Sideload add-in in Outlook
   - Test actionable messages
   - Verify Graph API permissions

---

### **Phase 6: Configuration & Documentation Updates**

#### 6.1 Update Config

**File:** `config.py` additions

```python
# M365 Integration Settings
M365_ENABLED = os.getenv("M365_ENABLED", "false").lower() == "true"
M365_CLIENT_ID = os.getenv("M365_CLIENT_ID")
M365_CLIENT_SECRET = os.getenv("M365_CLIENT_SECRET")
M365_TENANT_ID = os.getenv("M365_TENANT_ID")
M365_REDIRECT_URI = os.getenv("M365_REDIRECT_URI")
M365_SCOPES = [
    "User.Read",
    "Calendars.Read",
    "Mail.Read",
    "Files.Read.All",
    "Chat.ReadWrite"
]

# Teams Bot Settings
TEAMS_APP_ID = os.getenv("TEAMS_APP_ID")
TEAMS_APP_PASSWORD = os.getenv("TEAMS_APP_PASSWORD")

# Outlook Add-in Settings
OUTLOOK_ADDIN_ENDPOINT = os.getenv("OUTLOOK_ADDIN_ENDPOINT")
```

#### 6.2 Update Dependencies

**File:** `requirements-m365.txt`

```txt
# M365 Integration Dependencies
msal>=1.28.0
msgraph-sdk>=1.5.0
botbuilder-core>=4.16.0
botbuilder-schema>=4.16.0
botframework-connector>=4.16.0
flask>=3.0.0
aiohttp>=3.9.0
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Azure AD app registered and configured
- [ ] Client secret stored in Azure Key Vault
- [ ] Graph API permissions granted and consented
- [ ] Teams bot created in Azure Portal
- [ ] Bot messaging endpoint configured
- [ ] Teams app manifest created
- [ ] App icons designed (outline.png, color.png)

### Deployment
- [ ] Code deployed to Azure App Service
- [ ] Environment variables configured in App Service
- [ ] Bot service connected to App Service endpoint
- [ ] SSL/TLS certificate configured
- [ ] Health check endpoint responding

### Post-Deployment
- [ ] Teams app package uploaded to Teams Admin Center
- [ ] App published to organization app store
- [ ] Outlook add-in registered in Exchange Admin Center
- [ ] User documentation published
- [ ] Monitoring and alerts configured

---

## Security Considerations

1. **Token Management:**
   - Store access tokens in secure, encrypted memory
   - Implement token refresh logic
   - Never log tokens

2. **User Privacy:**
   - Only request minimum necessary permissions
   - Clear data retention policies
   - Allow users to revoke consent

3. **Data Protection:**
   - Encrypt conversation data at rest
   - Use HTTPS for all communications
   - Implement rate limiting

4. **Compliance:**
   - GDPR compliance for EU users
   - Data residency requirements
   - Regular security audits

---

## Monitoring & Operations

### Key Metrics to Track

1. **Usage Metrics:**
   - Messages per day (Teams/Outlook)
   - Tool invocation frequency
   - Response time percentiles

2. **Error Metrics:**
   - Authentication failures
   - Graph API errors
   - Bot framework errors

3. **Performance Metrics:**
   - End-to-end latency
   - Azure AI Foundry response time
   - Memory usage

### Logging Strategy

```python
# Structured logging for M365 integration
logger.info("M365 message received", extra={
    "channel": "teams",
    "user_id": user_id,
    "message_length": len(message),
    "tools_used": tool_names,
    "response_time_ms": elapsed_ms
})
```

---

## Rollback Plan

If issues arise:

1. **Immediate:**
   - Disable M365 integration via environment variable
   - Revert to CLI-only mode
   - Notify users via Teams message

2. **Investigation:**
   - Review Application Insights logs
   - Check Bot Framework status
   - Verify Graph API permissions

3. **Recovery:**
   - Deploy previous stable version
   - Clear bot state if corrupted
   - Re-authenticate users if needed

---

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Authentication | 1-2 weeks | Azure AD app, MSAL integration |
| Phase 2: Message Adapters | 1-2 weeks | Teams bot, Outlook add-in |
| Phase 3: M365 Tools | 1-2 weeks | Calendar, Email, SharePoint tools |
| Phase 4: Deployment | 1 week | Azure deployment, bot registration |
| Phase 5: Testing | 1-2 weeks | Integration tests, UAT |
| Phase 6: Documentation | 1 week | User guide, admin guide |
| **Total** | **6-9 weeks** | Production-ready M365 agent |

---

## Success Criteria

- [ ] Agent responds correctly in Teams personal chat
- [ ] Agent responds correctly in Teams team channel
- [ ] Outlook add-in loads and displays responses
- [ ] Calendar tool successfully queries user calendar
- [ ] Email tool finds recipe-related emails
- [ ] SharePoint tool accesses documents
- [ ] All Graph API calls use proper authentication
- [ ] Adaptive cards render correctly across devices
- [ ] Response time < 3 seconds for 95th percentile
- [ ] Zero authentication errors in production

---

## Resources

- [Microsoft Graph API Documentation](https://learn.microsoft.com/graph/)
- [Bot Framework Documentation](https://learn.microsoft.com/azure/bot-service/)
- [Teams App Development](https://learn.microsoft.com/microsoftteams/platform/)
- [Outlook Add-ins](https://learn.microsoft.com/office/dev/add-ins/outlook/)
- [Adaptive Cards Designer](https://adaptivecards.io/designer/)
- [Azure AD App Registration Guide](https://learn.microsoft.com/azure/active-directory/develop/quickstart-register-app)
