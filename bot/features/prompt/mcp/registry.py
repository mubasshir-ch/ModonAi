from typing import Dict, List
from .base import BaseTool

class MCPRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        # Store using lowercase keys for case-insensitive lookup
        self.tools[tool.name.lower()] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self.tools.get(name.lower())

    def get_all_tools(self, read_only: bool = None) -> List[BaseTool]:
        if read_only is None:
            return list(self.tools.values())
        return [tool for tool in self.tools.values() if tool.read_only == read_only]

    def get_system_prompt_addition(self, read_only: bool = None) -> str:
        if read_only is True:
            prompt = "5. Actions Supported for Investigation (READ-ONLY):\n"
        elif read_only is False:
            prompt = "5. Actions Supported for Execution (MUTATIONS):\n"
        else:
            prompt = "5. Actions Supported (DO NOT HALLUCINATE ACTIONS NOT IN THIS LIST):\n"
            
        for tool in self.get_all_tools(read_only):
            schema_fields = ", ".join(tool.schema.model_fields.keys())
            prompt += f"   - {tool.name}: {{{schema_fields}}} - {tool.description}\n"
        return prompt

registry = MCPRegistry()
