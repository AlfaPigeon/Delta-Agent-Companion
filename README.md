# AI Companion - Delta Agent

An intelligent AI companion system featuring a dynamic behavior tree state machine, adaptive memory system, tool integration, and multi-modal interaction capabilities through Eleven Labs and optional chat UI.


> Note:
> I am just vibe coding this for fun but I will clean up later xd. Don't worry I am an expert.
> You can join in if you want but since this is vibe coded don't trust, read and test your way through.
>
> 
> Don't forget to update todo.md(You can edit it if you think it is wrong)
> You can suggest stuctural changes o blueprint.md
>
> I will only merge if you progress the project:
>    - clean up (no vibe code accepted)
>       - Your implementation fallows the best practices as much as possible given context
>       - You either remove unnessesary code or add a nessesary code for functionality
>    - feature addition (vibe code is accepted if not breaking cleaned up code)
>       - You are adding an interesting module(You can vibe code)
>       - What your adding is modular
>       - it should not break already clean code
> 
> By mathematical induction this should produce me an ai girlfriend next year or so.


## 🚀 Features

### Core Features
- **Dynamic Behavior Tree**: Self-modifying state machine that adapts to user needs
- **Adaptive Memory System**: Intelligent memory management with reinforcement learning
- **Tool Integration**: Dynamic tool discovery and execution
- **Multi-modal Interaction**: Voice (Eleven Labs) and text interfaces
- **System Tray Operation**: Background operation with minimal resource usage
- **Context Awareness**: Environment and user activity monitoring

### Advanced Features
- **Memory Consolidation**: Automatic memory optimization and compression
- **State Persistence**: Recoverable system state across sessions
- **Debug Mode**: Comprehensive debugging and development tools
- **Configuration Management**: Runtime configuration updates
- **Performance Monitoring**: Resource usage and optimization metrics

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Companion Core                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Behavior    │  │   Memory    │  │    Tool     │         │
│  │ Tree Engine │  │   System    │  │  Manager    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    LLM      │  │ Environment │  │   Context   │         │
│  │ Processor   │  │   Monitor   │  │  Manager    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Eleven Labs │  │   Chat UI   │  │  System     │         │
│  │ Integration │  │ (Optional)  │  │   Tray      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI for API endpoints
- **Database**: SQLite for local storage, Redis for caching
- **AI/ML**: Transformers, LangChain, OpenAI/Anthropic APIs
- **Voice**: Eleven Labs API

### Frontend
- **Desktop UI**: Electron with React/TypeScript
- **Styling**: Tailwind CSS or Material-UI
- **State Management**: Redux Toolkit
- **Real-time Communication**: WebSocket/Socket.io

## 📁 Project Structure

```
ai-companion/
├── src/
│   ├── core/                 # Core system components
│   ├── behavior-tree/        # Behavior tree state machine
│   ├── memory/              # Memory system implementation
│   ├── tools/               # Tool management system
│   ├── llm/                 # LLM integration layer
│   ├── ui/                  # User interface components
│   └── config/              # Configuration management
├── tools/                   # Available tools directory
├── data/                    # Data storage
├── tests/                   # Test suites
├── docs/                    # Documentation
└── config/                  # Configuration files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 16+ (for UI components)
- Eleven Labs API key (for voice features)
- OpenAI/Anthropic API key (for LLM features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AlfaPigeon/Delta-Agent-Companion.git
   cd Delta-Agent-Companion
   ```

2. **Set up Python environment**
   ```bash
   cd ai-companion
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure the system**
   ```bash
   cp config/config.yaml.example config/config.yaml
   # Edit config/config.yaml with your API keys and preferences
   ```

4. **Run the companion**
   ```bash
   python main.py
   ```

### Configuration

Edit `config/config.yaml` to customize your AI companion:

```yaml
llm:
  provider: "openai"  # or "anthropic"
  api_key: "your-api-key"
  model: "gpt-4"

voice:
  eleven_labs_api_key: "your-eleven-labs-key"
  voice_id: "default"

memory:
  max_memories: 10000
  consolidation_threshold: 100

behavior_tree:
  auto_modify: true
  backup_states: true
```

## 🧠 Core Components

### Behavior Tree Engine
The behavior tree system uses a dynamic state machine that can modify itself based on context and user interactions. States are defined in JSON format and can be added, modified, or removed at runtime.

### Memory System
The memory system implements multiple memory types:
- **Episodic Memory**: Event-based memories with temporal context
- **Semantic Memory**: Factual information and learned patterns
- **Working Memory**: Active context and immediate processing data
- **Procedural Memory**: Tool usage patterns and behavioral sequences

### Tool Management
Tools are dynamically discovered and can be executed safely in a sandboxed environment. Each tool is defined by a JSON schema that describes its capabilities and requirements.

## 🧪 Testing

Run the test suite:

```bash
# Unit tests
python -m pytest tests/unit/

# Integration tests
python -m pytest tests/integration/

# Memory system tests
python test_memory.py

# Behavior tree tests
python test_behavior_tree.py
```

## 📊 Performance Metrics

### Target Performance
- Response time < 2 seconds for voice interactions
- Memory usage < 500MB in idle state
- Tool execution success rate > 95%
- System uptime > 99.5%

## 🛡️ Security

- Encryption for sensitive memory data
- Secure tool execution sandboxing
- User privacy controls
- Data retention policies
- Permission-based tool access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/AlfaPigeon/Delta-Agent-Companion/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AlfaPigeon/Delta-Agent-Companion/discussions)

## 🗺️ Roadmap

### Completed Features
- ✅ Dynamic Behavior Tree implementation
- ✅ Basic Memory System
- ✅ Tool Integration framework
- ✅ Configuration system

### In Progress
- 🔄 Eleven Labs voice integration
- 🔄 Memory consolidation algorithms
- 🔄 Context awareness system

### Planned Features
- 📋 Multi-user support
- 📋 Plugin system
- 📋 Cloud synchronization
- 📋 Mobile companion app
- 📋 Emotional intelligence features

---

*For detailed implementation information, see [blueprint.md](blueprint.md)*
