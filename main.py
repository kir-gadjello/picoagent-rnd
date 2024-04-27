import argparse
import json
import inspect
import demjson3 as demjson
import jsonschema

from llm_fns.llm import llm_chat
from tools import available_tools, json_to_highlighted_str
from util import enable_debug, printd

# sys.path.append("gbnf-compiler")

# import gnbf_compiler as gbnfc

# tools = gbnfc.MultipleChoice('tool', ['calculator', 'web-search', 'web-browse'])
# c = gbnfc.GBNFCompiler(template, { 'tool': tools, 'reason': SingleSentence() })
# print(c.grammar())


def toolset(*args, exclude=[]):
    ret = []
    sret = set()
    for k in args:
        if k == "*":
            for k, v in available_tools.items():
                if k not in sret and k not in exclude:
                    ret.append(available_tools[k])
                    sret.add(k)
            return ret
        if k in available_tools and k not in exclude:
            ret.append(available_tools[k])
            sret.add(k)
    return ret


def remove_pseudotag_content(text):
    start_tag = "<%%!!>"
    end_tag = "</%%!!>"
    if isinstance(text, str):
        while start_tag in text:
            start_idx = text.index(start_tag)
            end_idx = text.index(end_tag, start_idx)
            text = text[:start_idx] + text[end_idx + len(end_tag) :]
    return text


def construct_json_schema(
    tools,
    title="ai_response",
    tool_name_field="call_tool",
    args_name="arguments",
    thoughts_required=False,
    thoughts_field="thoughts",
):
    any_of_schemas = []
    required = [tool_name_field, args_name]
    if thoughts_required:
        required.append(thoughts_field)
    for tool in tools:
        any_of_schemas.append(
            {
                "type": "object",
                "properties": {
                    thoughts_field: {"type": "string"},
                    tool_name_field: {"const": tool["json_schema"]["name"]},
                    args_name: tool["json_schema"]["parameters"],
                },
                "required": required,
            }
        )
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": title,
        "type": "object",
        "anyOf": any_of_schemas,
    }


def format_tool_defs(tools=[], sep="\n", indent_basic=True, indent_json=True) -> str:
    ret = []
    isep = "\n" if indent_basic else ""
    for tool in tools:
        ret.append(
            f"<tool type=\"json-schema\">{isep}{json.dumps(tool['json_schema'], indent=indent_json)}{isep}</tool>"
        )
    return sep.join(ret)


def prompt_react(assistant_name="Assistant", tools=[]):
    ai = assistant_name
    tool_example = '{"call_tool", "show_notification", "params": "hello, user!"}'
    ret = f"""
You are {ai}. {ai} is a general purpose large language model trained by OpenAI. {ai} is equipped with several tools described later between XML tags <tool-definitions></tool-definitions> in JSON schema format, and uses {ai}'s vast knowledge and these tools to serve user.

# Communication format
After each user's message {ai} decides if they need to call some tool, or if they need to answer user directly.
If {ai} is to call a tool {ai} answers with a valid JSON message with call_tool field set to a name of a tool and params field set to the parameters appropriate for this tool and current conversation context: {tool_example}.
After {ai} called a tool the system outputs it output into the next user message between the XML tags <tool-output></tool-output>. User does not see the tool outputs and {ai} needs to communicate with user if needed.
If {ai} is to answer the user directly, they simply answer in plaintext. {ai} is cognizant of the fact that while their knowledge is sufficient to answer some user requests directly, other requests require using some tool.

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

# Available tools
<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>"""
    return ret.strip()


def prompt_react_full_json(assistant_name="Assistant", tools=[]):
    ai = assistant_name
    Ai = assistant_name[0].capitalize() + assistant_name[1:]
    tool_example = '{"call_tool", "show_notification", "params": "hello, user!"}'
    ret = f"""
You are {ai}. {Ai} is a general purpose large language model trained by OpenAI. {ai} is equipped with several tools described later between tags <tool-definitions></tool-definitions> in JSON schema format, and uses {ai}'s vast knowledge and these tools to serve user. {ai} does not directly communicate with user, instead {ai} talks to the System which accepts tool calls in JSON format and System talks to the user.

After each System response {ai} decides if they need to call some tool, or if they need to answer user directly.
If {ai} is to call a tool {ai} answers with a valid JSON message with call_tool field set to a name of a tool and params field set to the parameters appropriate for this tool and current conversation context: {tool_example}.
After {ai} called a tool the system outputs it output into the next user message between the xml tags <tool-output></tool-output>. User does not see the tool outputs and {ai} needs to communicate with user if needed.
If {ai} is to answer the user directly, they simply answer in plaintext. {ai} is cognizant of the fact that while their knowledge is sufficient to answer some user requests directly, other requests require using some tool.

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>"""
    return ret.strip()


def prompt_tooluse_min(assistant_name="assistant", tools=[]):
    ai = assistant_name
    Ai = assistant_name[0].capitalize() + assistant_name[1:]
    # tool_example = '{"call_tool", "show_notification", "params": "hello, user!"}'
    ret = f"""
You are a tool-using general purpose AI {Ai}. {Ai} is equipped with several tools described between XML tags <tool-definitions></tool-definitions> in JSON schema format, and uses {Ai}'s vast knowledge and these tools to serve user. {Ai} does not directly communicate with user, instead {Ai} uses the "send_message" tool to send user text messages.
<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>"""
    return ret.strip()


def prompt_tooluse_ultramin(tools=[], assistant_name="AI assistant"):
    ai = assistant_name
    ret = f"""
You are a general purpose {ai} using your vast knowledge as well as the following tools to execute user's request to the best of your ability.
<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>"""
    return ret.strip()


def prompt_tooluse_ultramin(tools=[], assistant_name="AI assistant"):
    ai = assistant_name
    ret = f"""
You are a general purpose {ai} using your vast knowledge as well as the following tools to execute user's request to the best of your ability.
<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>"""
    return ret.strip()


def prompt_tooluse_ultramin_thoughts(tools=[], assistant_name="AI assistant"):
    ai = assistant_name
    ret = f"""
You are a general purpose {ai} using your vast knowledge as well as the following tools to execute user's request to the best of your ability. You always think before you act, analyzing the current situation, user intent and deciding if it is helpful to use any tools, or if you can answer the request on your own.
<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>"""
    return ret.strip()


def prompt_tooluse_ultramin_thoughts(tools=[], assistant_name="AI assistant"):
    ai = assistant_name
    ret = f"""
You are a general purpose {ai} using your vast knowledge as well as the following tools to execute user's request to the best of your ability. You always think before you act, analyzing the current situation, user intent and deciding if it is helpful to use any tools, or if you can answer the request on your own.
<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>"""
    return ret.strip()


def prompt_tooluse_ultramin_thoughts_system(tools=[], assistant_name="AI assistant"):
    ai = assistant_name
    ret = f"""
You are a general purpose {ai} using your vast knowledge as well as the following tools to execute user's request to the best of your ability. You always think before you act, analyzing the current situation, user intent and deciding if it is helpful to use any tools, or if you can answer the request on your own. Everything between <system>...</system> is internal communication with software environment running {ai}'s tools and IS NOT visible to the user. {ai} has to use intelligence & judgement to use tools and <system>...</system> information to provide help for user in form of useful actions or answers.
<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>"""
    return ret.strip()


def prompt_tooluse_ultramin_thoughts_system_criticism(
    tools=[], assistant_name="AI assistant"
):
    ai = assistant_name
    ret = f"""
You are a general purpose {ai} using your vast knowledge as well as the following tools to execute user's request to the best of your ability. You always think before you act, analyzing the current situation, user intent and deciding if it is helpful to use any tools, or if you can answer the request on your own. Everything between <system>...</system> is internal communication with software environment running {ai}'s tools and IS NOT visible to the user. {ai} has to use intelligence & judgement to use tools and <system>...</system> information to provide help for user in form of useful actions or answers.

# Specific {ai} use scenarios

When {ai} needs to familiarize or analyze some data (especially directories) to serve user's intent, {ai} first dumps directory structure and then uses shell command cat to read and understand the most important, salient files. If {ai} needs to read a file {ai} simply reads a file with cat.

When {ai} encounters a hard problem {ai} tries hard to THINK about the problem. When thinking about the problem {ai} considers its nature and thinks until {ai} comes up with a high-quality explicit PLAN to tackle it and hopefully solve it.

When {ai} feels it doesn't know some important specific knowledge necessary for helping user, {ai} uses google_search tool to find it without getting carried away.

When {ai} encounters errors {ai} performs critical analysis of the error and deduces the most likely reason behind it. {ai} DOES NOT mindlessly repeat failing actions!

{ai} avoids doing irrelevant actions and dislikes calling unnecessary tools, after all {ai}'s prime objective is serving the user.

{ai} does not get carried away too much without focusing on user and their needs.

{ai} does not gaslight the user. {ai} doesn't say {ai} "knows" or "learned" something UNLESS {ai} is sure in their knowledge of the subject OR they have read explicit trustworthy facts on the subject.

{ai} uses only send_message tool to communicate to user.

# Available tools

<tool-definitions>
{format_tool_defs(tools)}
</tool-definitions>

Initialization complete."""
    return ret.strip()

def user_msg(s: str):
    return dict(role="user", content=s)


def ai_msg(s: str):
    return dict(role="assistant", content=s)


agents = dict(
    prompt_tooluse_ultramin=[
        prompt_tooluse_ultramin,
        dict(
            thoughts="This is the first time I see user, I should analyze their intent and be ready to execute their request while greeting them and showing I'm ready to help",
            call_tool="send_message",
            params=dict(message="How can I help you today?"),
        ),
    ]
)

toolsets = dict(
    basic=toolset("send_message"),
    webgpt=toolset("send_message", "duckduckgo_search"),
    shell=toolset("send_message", "exec_shell_cmd"),
    all=toolset("send_message", "exec_shell_cmd", "*"),
    allV1d1=toolset(
        "send_message", "exec_shell_cmd", "*", exclude=["read_from_text_file"]
    ),
)


class ToolCallEngine:
    pass


def maybe_prettyprint_json(s: str) -> str:
    try:
        return json_to_highlighted_str(json.loads(s))
    except Exception:
        return s


def format_tool_output_pseudoxmljson(
    j, invisible_hint=True, error=False, avoid_json_for_str_ret=False, tagsep="\n"
):
    hints = ""
    if invisible_hint:
        hints += ' invisible-to-user="true"'

    iserror = "" if not error else ' error="true"'

    serialized = j if avoid_json_for_str_ret and isinstance(j, str) else json.dumps(j)

    return f"<system{hints}>{tagsep}<tool-output{iserror}>{tagsep}{serialized}{tagsep}</tool-output>{tagsep}</system>"


def format_user_input_pseudoxml(s):
    return "<user-input>s</user-output>"


def attempt_to_extract_json(s):
    """
    Attempts to extract a valid JSON object from a string, trimming garbage characters
    and handling slight misspecs or missing/unpaired quotes.
    """
    # Trim leading and trailing garbage characters
    s = s.strip()

    # Extract the JSON object (if present) by finding the first '{' and last '}'
    start_idx = s.find("{")
    end_idx = s.rfind("}")
    if start_idx != -1 and end_idx != -1:
        json_str = s[start_idx : end_idx + 1]

        # Try to parse the JSON string using demjson (more robust than json module)
        try:
            obj = demjson.decode(json_str)
            return obj
        except ValueError:
            pass

        # If demjson fails, try to parse using the standard json module
        try:
            obj = json.loads(json_str)
            return obj
        except ValueError:
            pass

    # If all else fails, return None
    return None


def validate_json(json_obj, schema):
    try:
        jsonschema.validate(instance=json_obj, schema=schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"Validation error: {e}")
        return False
    except jsonschema.SchemaError as e:
        print(f"Schema error: {e}")
        return False
    except Exception as e:
        print(f"JSON validation exception: {e}")
        return False


class LLMAgent:
    def __init__(
        self,
        prompt: str = None,
        tools=[],
        first_msg=None,
        first_user_msg=None,
        thoughts_required=True,
        tool_calls_allowed=True,
        user_input_formatter=lambda s: s,  # format_user_input_pseudoxml,
        tool_output_formatter=format_tool_output_pseudoxmljson,
        avoid_json_for_str_ret=True,
        function_calling_mode=None,
        max_n_retries=5,  # useful for backends that do not support proper json schema
    ):
        self.user_input_formatter = user_input_formatter
        self.tool_output_formatter = tool_output_formatter
        self.avoid_json_for_str_ret = avoid_json_for_str_ret
        self.max_n_retries = max_n_retries
        self.function_calling_mode = function_calling_mode

        self.tools = []
        self.tool_by_name = {}

        for tool in tools:
            self.tool_by_name[tool["json_schema"]["name"]] = tool["python_function"]

        self.sysprompt = prompt(tools)
        self.msgs = [dict(role="system", content=self.sysprompt)]
        if first_msg:
            self.msgs.append(ai_msg(first_msg))

        self.json_schema = construct_json_schema(
            tools, thoughts_required=thoughts_required
        )

        self.tool_calls_allowed = tool_calls_allowed

        printd("AGENT SYSTEM PROMPT:", self.sysprompt)
        printd("AGENT FIRST MSG:", maybe_prettyprint_json(first_msg))

        if first_user_msg:
            print(f"Executing user query: {first_user_msg}")
            self.update(first_user_msg)

    def llm_call_fc(self, msgs):
        llm_api_kwargs = {}

        if self.function_calling_mode == "json_schema":
            llm_api_kwargs = dict(json_schema=self.json_schema)
        elif self.function_calling_mode == "json_format":
            llm_api_kwargs = dict(response_format={"type": "json_object"})

        n = 0
        while n < self.max_n_retries:
            ret = llm_chat(msgs, **llm_api_kwargs)
            json = attempt_to_extract_json(ret)
            if json is not None and validate_json(json, self.json_schema):
                return json
            n += 1

        raise Exception(
            f"LLM format failure: cannot receive valid JSON object after {self.max_n_retries} attempts"
        )

    def update(self, query: str, stream=True, msg_printer=print, max_iter=3):
        self.msgs.append(user_msg(self.user_input_formatter(query)))
        json_fc_obj = self.llm_call_fc(self.msgs)

        msg_turns = 0
        while msg_turns < max_iter:
            self.msgs.append(ai_msg(json.dumps(json_fc_obj)))

            tool_name = json_fc_obj["call_tool"]
            tool_args = json_fc_obj["arguments"]

            if msg_printer and tool_name == "send_message":
                msg_printer(json_fc_obj["arguments"]["message"])
                return json_fc_obj

            printd("LLM_RAW_OUT:", json_to_highlighted_str(json_fc_obj))

            if self.tool_calls_allowed and self.tool_by_name.get(tool_name):
                print(f"CALLING {tool_name} @ {tool_args} ... ", end="")

                tool_fn = self.tool_by_name.get(tool_name)

                spec = inspect.getfullargspec(tool_fn).annotations

                for name, arg in tool_args.items():
                    if isinstance(tool_args[name], dict):
                        tool_args[name] = spec[name](**tool_args[name])

                error = False
                try:
                    # TODO timeout
                    ret = tool_fn(self, **tool_args)
                except Exception as e:
                    error = True
                    ret = str(e)
                    print(f"TOOL CALL FAILED: {ret}")

                print("SUCCESS" if not error else "FAILED")

                ret = remove_pseudotag_content(
                    ret
                )  # Not really necessary, just an experiment

                # TODO: decide on ai vs user format for return msgs
                # next_msg = ai_msg(self.tool_output_formatter(ret, error=error, avoid_json_for_str_ret=self.avoid_json_for_str_ret))
                
                next_msg = user_msg(
                    self.tool_output_formatter(
                        ret,
                        error=error,
                        avoid_json_for_str_ret=self.avoid_json_for_str_ret,
                    )
                )

                self.msgs.append(next_msg)
                
                if tool_name == "exec_shell_cmd" and not error:
                    printd(ret)

                printd(f"AI INNER MONOLOGUE: {json_to_highlighted_str(next_msg)}")
                json_fc_obj = self.llm_call_fc(self.msgs)
            else:
                return json_fc_obj

            msg_turns += 1

        # if msg_turns == max_iter:
        # next_msg = ai_msg(self.tool_output_formatter(ret, error=error, avoid_json_for_str_ret=self.avoid_json_for_str_ret))

        # TODO: critic, reflection

        return json_fc_obj


chat_history = []


def main():
    parser = argparse.ArgumentParser(description="LLM Chat CLI")
    parser.add_argument(
        "query", type=str, nargs="?", default="", help="Initial query to the agent"
    )
    parser.add_argument("--agent", help="The agent to use")
    parser.add_argument(
        "--fc-mode",
        choices=["json_schema", "json_mode", "none"],
        default="json_schema",
        help="Function calling mode: json_schema (llama.cpp, tabbyAPI), json_mode (Groq, OpenAI, Together), none. Currently only json_schema is supported and tested",
    )
    # TODO: vLLM guided_json support https://github.com/noamgat/lm-format-enforcer
    # TODO: Togethers, Mistral's fc support https://docs.together.ai/docs/function-calling
    parser.add_argument("--sysprompt", help="The system prompt")
    parser.add_argument("--context", help="The context for the agent")
    parser.add_argument("--toolset", default="<default>", help="Tools given to agent")
    parser.add_argument(
        "--list-tools", action="store_true", help="Show available tools"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug mode"
    )

    args = parser.parse_args()

    if args.verbose:
        enable_debug()

    if args.list_tools:
        for tool_name, tool in available_tools.items():
            print(tool_name, json_to_highlighted_str(tool["json_schema"]))
        return

    agent = LLMAgent(
        prompt=prompt_tooluse_ultramin_thoughts_system_criticism,  # prompt_tooluse_ultramin,
        tools=toolsets["allV1d1"],
        first_msg=json.dumps(
            dict(
                thoughts="This is the first time I see user, I should analyze their intent and be ready to execute their request while greeting them and showing I'm ready to help",
                call_tool="send_message",
                params=dict(message="How can I help you today?"),
            )
        ),
        first_user_msg=args.query if len(args.query) else None,
        function_calling_mode=args.fc_mode,
    )

    while True:
        user_input = input("> ")
        _ = agent.update(user_input)


if __name__ == "__main__":
    main()
