# claude_conversation_history_analysis
## Purpose
My goal is simply to improve my programming skills, particularly with file input/output, simple data analysis, and graphing!
## Getting Started
1. Download the [repository](https://github.com/SamAllen06/claude_conversation_history_analysis.git)
```
git clone https://github.com/SamAllen06/claude_conversation_history_analysis.git
```
2. Download your conversation history from Claude
3. Install the dependencies. (Use the latter if you want to install dependencies that speed up xarray greatly.)
```
pip install claude_conversation_history_analysis
```
```
pip install -e ".[speed]"
```
4. Run the script on your conversation history
```
python src/analyze_input.py your_directory/input.json
```
