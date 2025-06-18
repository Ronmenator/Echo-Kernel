from typing import Dict, List
from echo_kernel.ITextProvider import ITextProvider
from openai import AzureOpenAI
import json

class AzureOpenAITextProvider(ITextProvider):
    def __init__(self, api_key: str, api_base: str, api_version: str, model: str):
        self.client = AzureOpenAI(api_key=api_key, azure_endpoint=api_base, api_version=api_version)
        self.model = model

    async def generate_text(self, 
                            prompt: str, 
                            system_message: str = "", 
                            context: Dict = None, 
                            temperature: float = 0.7, 
                            max_tokens: int = 1000, 
                            top_p: float = 1, 
                            frequency_penalty: float = 0, 
                            presence_penalty: float = 0, 
                            tools : List = None,
                            tool_implementations: Dict = None) -> str:
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        if context:
            messages.insert(1, {"role": "user", "content": context})

        while True:
            if tools:
                response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        top_p=top_p,
                        frequency_penalty=frequency_penalty,
                        presence_penalty=presence_penalty,
                        tools=tools,
                        tool_choice="auto"
                    )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p,
                    frequency_penalty=frequency_penalty,
                    presence_penalty=presence_penalty
                )

            message_content = response.choices[0].message.content
            tool_content = response.choices[0].message.tool_calls

            # Check for tool call response
            if tool_content:
                messages.append(response.choices[0].message)
                for tool_call in tool_content:
                    tool_name = tool_call.function.name
                    tool_result = await self.call_tool(tool_name, tool_call.function.arguments, tool_implementations)
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_result})
            else:
                break

        return message_content

    async def call_tool(self, tool_name: str, args, tool_implementations: Dict) -> str:
        if tool_name in tool_implementations:
            # Parse the JSON string into a dictionary
            args_dict = json.loads(args)
            tool = tool_implementations[tool_name]
            # Pass the values as keyword arguments
            return tool(**args_dict)
        else:
            return f"Tool {tool_name} not found"