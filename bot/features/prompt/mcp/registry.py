from typing import Dict, List
from .base import BaseTool

class MCPRegistry:
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self.tools.get(name)

    def get_all_tools(self) -> List[BaseTool]:
        return list(self.tools.values())

    def get_system_prompt_addition(self) -> str:
        prompt = "5. Actions Supported (DO NOT HALLUCINATE ACTIONS NOT IN THIS LIST):\n"
        for tool in self.get_all_tools():
            schema_fields = ", ".join(tool.schema.model_fields.keys())
            prompt += f"   - {tool.name}: {{{schema_fields}}} - {tool.description}\n"
        return prompt

registry = MCPRegistry()
