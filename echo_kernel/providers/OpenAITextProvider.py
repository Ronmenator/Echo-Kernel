from typing import Dict, List, Optional
import openai
import json
from ..ITextProvider import ITextProvider

class OpenAITextProvider(ITextProvider):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    async def generate_text(self, prompt: str, system_message: str = "", context: Dict = None, 
                          temperature: float = 0.7, max_tokens: int = 1000, top_p: float = 1,
                          frequency_penalty: float = 0, presence_penalty: float = 0, tools: Optional[List[Dict]] = None,
                          tool_implementations: Optional[Dict] = None) -> str:
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        if context and "messages" in context:
            messages.extend(context["messages"])
            
        messages.append({"role": "user", "content": prompt})
        
        while True:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                tools=[{"type": "function", "function": tool} for tool in tools] if tools else None,
                tool_choice="auto" if tools else None
            )
            
            message = response.choices[0].message
            message_content = message.content
            
            # Check for tool calls
            if hasattr(message, 'tool_calls') and message.tool_calls:
                # Add the assistant's message with tool calls to the conversation
                messages.append(message)
                
                # Process each tool call
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = tool_call.function.arguments
                    
                    # Execute the tool
                    tool_result = await self.call_tool(function_name, function_args, tool_implementations)
                    
                    # Add the tool response to the conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": str(tool_result)
                    })
            else:
                # No more tool calls, return the final response
                return message_content

    async def call_tool(self, tool_name: str, args: str, tool_implementations: Optional[Dict] = None) -> str:
        if tool_implementations and tool_name in tool_implementations:
            try:
                # Parse the JSON string into a dictionary
                args_dict = json.loads(args)
                tool = tool_implementations[tool_name]
                # Pass the values as keyword arguments
                return tool(**args_dict)
            except Exception as e:
                return f"Error executing tool {tool_name}: {str(e)}"
        else:
            return f"Tool {tool_name} not found" 