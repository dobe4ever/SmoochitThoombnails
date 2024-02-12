from utils import load_json, save_json
import json
from auto_thoombnail import auto_thumbnail
from openai import OpenAI
import os
from telegram import Bot

bot_token = os.environ['BOT_TOKEN']
bot = Bot(token=bot_token)

client = OpenAI()

def run_conversation(userid, text):
    conv=load_json("data/conversation.json")
    conv.append({"role": "user", "content": text})
    print(conv)
    save_json("data/conversation.json", conv)
    #Step 1: send the conversation and available functions to the model
    tools = [
        {
            "type": "function",
            "function": {
                "name": "auto_thumbnail",
                "description": "Generate a thumbnail for an episode",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "episode_num": {"type": "integer", "description": "Episode number"},
                        "line1": {"type": "string", "description": "First line of the title. For titles of three words or less use just 1 line."},
                        "line2": {"type": "string", "description": "The second line of the title. For titles longer than three words, split the title in two lines. Defaults to None."},
                    },
                    "required": ["episode_num", "line1"],
                },
            },
        }
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        #messages=conv,
        messages = [conv[0]] + conv[-10:],
        tools=tools,
        tool_choice="auto",
    )
    response_message = response.choices[0].message
    
    tool_calls = response_message.tool_calls

    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        available_functions = {
            "auto_thumbnail": auto_thumbnail,
        }
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                episode_num=function_args.get("episode_num"),
                line1=function_args.get("line1"),
                line2=function_args.get("line2"),
            )
            conv.append(
                {
                    "role": "system", 
                    "content": "Thumbnail delivered sucessfully"
                }
            )
            conv.append(
                {"role": "assistant", "content": function_response}
            )

            save_json("data/conversation.json", conv)
            
            print(function_response)
            
            with open("uploads/new_thumbnail.png", "rb") as file:
                bot.send_photo(
                    chat_id=userid,
                    photo=file,
                    caption=function_response,
                )
            
            return None

    else:
        content = response_message.content
        conv.append({"role": "assistant", "content": content})
        save_json("data/conversation.json", conv)
        print(response_message.content)
        return response_message.content