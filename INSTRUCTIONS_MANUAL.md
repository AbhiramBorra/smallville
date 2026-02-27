# Generative Agents Simulation - Complete Instructions Manual

## Table of Contents
1. [Setup and Installation](#setup-and-installation)
2. [Running the Program](#running-the-program)
3. [File Structure and Purpose](#file-structure-and-purpose)
4. [AI Models Used](#ai-models-used)
5. [Customizing AI Models](#customizing-ai-models)
6. [Creating Custom Simulations](#creating-custom-simulations)
7. [Changes Made from Original Code](#changes-made-from-original-code)
8. [Troubleshooting](#troubleshooting)
9. [Development Notes](#development-notes)

**Key Components:**
- **Frontend Server**: Django-based web interface for visualization
- **Backend Server**: Python simulation engine with AI agents
- **AI Integration**: Uses OpenAI GPT models for agent cognition

## Setup and Installation

### Prerequisites
- Create a new Virtual env with Python 3.9.12
- Create a utils.py with the OpenAI API key(Copy paste from README.md)
- Install dependencies
    ```bash
    pip install -r requirements.txt
   ```

## Running the Program

### Step 1: Start the Frontend Server (Django)
```bash
cd environment/frontend_server
python manage.py runserver
```

**Expected output:** "Your environment server is up and running" at http://localhost:8000/

### Step 2: Start the Backend Simulation Server
```bash
cd reverie/backend_server
python reverie.py
```

**Follow the prompts:**
1. **Fork simulation name**: Enter `base_the_ville_isabella_maria_klaus` (3 agents) or `base_the_ville_n25` (25 agents) [This is the part that we need to craft for each of the simulations we want to test ie. 1 bad character, only 1 good character, and 50-50]
2. **New simulation name**: Enter any name (e.g., `test-simulation`)
    - If you want to delete a simulation go to "/Users/abhi/Desktop/Masters/smallville/generative_agents/environment/frontend_server/storage and delete the file with the simulation name".
3. **Options**: Enter `run <steps>` (e.g., `run 100` for 100 simulation steps)
    - 1 simulation step is 10 in-game seconds
4. **Change the start time**: if you want to start the test simulation at a different time instead of the default 00:00:00 then cd into "/Users/abhi/Desktop/Masters/smallville/generative_agents/environment/frontend_server/storage/test-simulation/reverie/meta.json" and change the curr_time variable.

### Step 3: View the Simulation
- Navigate to http://localhost:8000/simulator_home
- Use arrow keys to navigate the map
- Watch agents move and interact in real-time

### Step 4: Save and Exit
- Type `fin` to save and exit
- Type `exit` to exit without saving

## File Structure and Purpose


### Frontend Server (`environment/frontend_server/`)
- **`manage.py`**: Django management script
- **`db.sqlite3`**: Django database
- **`requirements.txt`**: Frontend-specific dependencies

#### Templates (`templates/`)
- **`demo/`**: Replay/demo visualization templates
- **`home/`**: Main simulation interface templates
- **`landing/`**: Project landing page templates
- **`base.html`**: Base template for all pages

#### Storage (`storage/`)
- **`base_the_ville_isabella_maria_klaus/`**: 3-agent base simulation
- **`base_the_ville_n25/`**: 25-agent base simulation
- **Custom simulations**: Created when you run new simulations

#### Static Assets (`static_dirs/`)
- **`assets/the_ville/`**: Map tiles, sprites, and game assets
- **`css/`**: Stylesheets
- **`img/`**: Images and icons

### Backend Server (`reverie/backend_server/`)
- **`reverie.py`**: Main simulation engine and server
- **`maze.py`**: Environment/map management
- **`path_finder.py`**: Agent pathfinding algorithms
- **`utils.py`**: Configuration and API keys
- **`global_methods.py`**: Utility functions

#### Persona System (`persona/`)
- **`persona.py`**: Main agent class with memory, planning, and actions
- **`cognitive_modules/`**: AI modules for different cognitive functions
  - `plan.py`: Agent planning and decision-making
  - `perceive.py`: Environment perception and memory encoding
  - `reflect.py`: Self-reflection and insight generation
  - `retrieve.py`: Memory retrieval and association
- **`memory_structures/`**: Agent memory systems
  - `associative_memory.py`: Episodic and semantic memory
  - `spatial_memory.py`: Spatial knowledge and navigation
  - `scratch.py`: Short-term working memory
- **`prompt_template/`**: GPT prompt templates and processing
  - `run_gpt_prompt.py`: GPT API calls and response processing
  - `gpt_structure.py`: GPT request structure and validation

## AI Models Used

The system primarily uses **OpenAI GPT-4** models for agent cognition:

### Current Model Configuration
- **Primary Model**: `gpt-4.1-nano-2025-04-14`
- **Usage**: All cognitive functions (planning, perception, reflection, conversation)
- **API**: OpenAI GPT API

### Model Usage By Function
| Function | Model | Purpose |
|----------|-------|---------|
| Planning | gpt-4.1-nano-2025-04-14 | Daily schedule generation, action planning |
| Perception | gpt-4.1-nano-2025-04-14 | Event importance scoring, memory encoding |
| Conversation | gpt-4.1-nano-2025-04-14 | Dialogue generation, social interaction |
| Reflection | gpt-4.1-nano-2025-04-14 | Self-analysis, insight generation |
| Location Selection | gpt-4.1-nano-2025-04-14 | Spatial reasoning, navigation decisions |

## Customizing AI Models

### Changing the GPT Model

**File to modify**: `reverie/backend_server/persona/prompt_template/run_gpt_prompt.py`

**Current configuration** (appears multiple times):
```python
gpt_param = {"engine": "gpt-4.1-nano-2025-04-14", "max_tokens": 1000, 
             "temperature": 0, "top_p": 1, "stream": False,
             "frequency_penalty": 0, "presence_penalty": 0, "stop": None}
```

**To change models:**
1. Find all instances of `"engine": "gpt-4.1-nano-2025-04-14"`
2. Replace with your desired model (e.g., `"gpt-3.5-turbo"`, `"gpt-4"`)
3. Adjust `max_tokens` if needed for different models

**Search and replace locations:**
- Line ~436: Task decomposition
- Line ~584: Action sector selection  
- Line ~719: Action arena selection
- Line ~774: Action game object selection
- Line ~842: Pronunciation generation
- Line ~948: Event triple generation
- And many more throughout the file...

### Alternative Model Integration

**For non-OpenAI models:**
1. Modify `gpt_structure.py` to change the API call mechanism
2. Update `GPT_request()` function to use your preferred API
3. Ensure response format compatibility

## Creating Custom Simulations

### Method 1: Fork Existing Simulation
1. Run `python reverie.py`
2. Choose base simulation: `base_the_ville_isabella_maria_klaus` or `base_the_ville_n25`
3. Enter new simulation name
4. Simulation will be created in `environment/frontend_server/storage/your-sim-name/`

### Method 2: Modify Base Characters
**Location**: `environment/frontend_server/storage/base_the_ville_isabella_maria_klaus/personas/`

**For each character, modify:**
- `bootstrap_memory/scratch.json`: Personal details, current status
- `bootstrap_memory/associative_memory/nodes.json`: Memories and experiences
- `bootstrap_memory/spatial_memory.json`: Location knowledge

### Method 3: Create New Base Simulation
1. Copy an existing base simulation folder
2. Modify persona files
3. Update `personas/` folder names to match new characters
4. Update `reverie/meta.json` with new persona names

## Changes Made from Original Code

### 1. Movement Directory Creation (`reverie.py`)
**Issue**: FileNotFoundError when writing movement files
**Solution**: Added automatic directory creation
```python
# Added in ReverieServer.__init__
os.makedirs(f"{sim_folder}/movement", exist_ok=True)
os.makedirs(f"{sim_folder}/environment", exist_ok=True)

# Added before writing movement files
os.makedirs(os.path.dirname(curr_move_file), exist_ok=True)
```

### 2. GPT Response Error Handling (`run_gpt_prompt.py`)
**Issue**: IndexError when parsing empty task strings
**Solution**: Added robust validation for task parsing
```python
# Enhanced error checking in __func_clean_up
for count, i in enumerate(_cr):
    k = [j.strip() for j in i.split("(duration in minutes:")]
    # ensure we got both task and duration parts
    if len(k) < 2:
        print(f"[run_gpt_prompt] malformed line '{i}' -> split result {k}; skipping")
        continue
    task = k[0]
    # guard against empty strings
    if len(task) == 0:
        print(f"[run_gpt_prompt] warning: empty task parsed from response")
        continue
```

### 3. Spatial Memory Error Handling (ie. Model Hallucination)
**Issue**: KeyError when model hallucinates missing arena keys like 'kitchen'
**Recommended Solution**: restart the simulation.

## Troubleshooting

### Common Issues

#### 1. FileNotFoundError: movement directory
**Error**: `FileNotFoundError: movement/0.json`
**Solution**: Already fixed in current code. Restart servers.

#### 2. TypeError: 'NoneType' object is not subscriptable
**Error**: GPT function returns None
**Location**: `perceive.py` calling `run_gpt_prompt_event_poignancy`
**Solution**: Add None checking before accessing array indices

#### 3. KeyError: 'kitchen' in spatial memory
**Error**: Missing arena in spatial memory tree
**Solution**: Either populate missing areas or add graceful error handling

#### 4. API Rate Limiting
**Error**: OpenAI API rate limits
**Solution**: 
- Save simulation frequently with `fin` command
- Reduce simulation step count
- Check API usage limits
- Sign up using student email and enable access to share data
- Message Kyle about group api access

### Debug Output
The system produces various debug outputs:
- **Importance triggers**: Shows agent importance accumulation
- **GPT debug prints**: Shows "asdhfapsh8p9hfaiafdsi;ldfj as DEBUG X" messages
- **Movement logs**: Agent movement and decision logging

## Development Notes

### Performance Considerations
- **API Costs**: Each simulation step requires multiple GPT calls per agent
- **Simulation Speed**: ~10 seconds per game step (dependent on API latency)
- **Memory Usage**: Agents accumulate memories over time

### Authentication
- **OpenAI API Key**: Required in `utils.py`
- **Rate Limits**: Be aware of OpenAI's rate limiting policies
- **Costs**: Monitor API usage for cost management

### Simulation Mechanics
- **Time Scale**: 1 simulation step = 10 seconds of game time
- **Agent Memory**: Persistent across simulation sessions
- **World State**: Saved in JSON format for replay capability

### Extending the System
- **New Agent Types**: Modify persona initialization
- **New Environments**: Update maze and asset files  
- **New Behaviors**: Add cognitive modules in `persona/cognitive_modules/`
- **Integration**: Modify `gpt_structure.py` for different AI providers