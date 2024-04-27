# LLM function calling notes (draft)

(aka #fc )
### Specifications

OpenAI: https://platform.openai.com/docs/guides/function-calling (addenum: fine-tuning docs showing specific chatml-like format with `role: function`)
Nous Hermes ( #single_fc tool call tier): [github](https://github.com/NousResearch/Hermes-Function-Calling)
OpenChatML ( #multi_fc tool call tier): [github](https://github.com/cognitivecomputations/OpenChatML?tab=readme-ov-file#8-function-calling)
### Support & implementation tiers
**Full support**: extensive general #sft for single & multi #fc scenarios, support at the level of web API stack, client API library support, documentation
...
**No support:** Surprisingly, this is not a death sentence and there are legitimately useful #fc functionality that can be supported with a combination of
1. good llm with strong prompt following and zero-shot generalization (i.e. can generalize to execute intelligent tool choices in context of conversation with user), capable of generating json or a custom parsable format
2. inference/webAPI support for json/grammar-constrained sampling (note that OpenAI also explicitly supports this json format option)
3. solid prompting (tool definitions via popular code idioms, tool calls)
4. benign nature of #fc usage
Examples of zero-shot #fc are [MemGPT](https://memgpt.readme.io/docs/adding_wrappers), [langchain's previous-gen tech](https://github.com/langchain-ai/langchain/blob/cb6e5e56c29477c6da5824c17f1b70af11352685/docs/docs/modules/model_io/chat/structured_output.ipynb#L351),[ this llama.cpp agent](https://github.com/Maximilian-Winter/llama-cpp-agent/tree/master) , [another oss fc example](https://github.com/AIAnytime/Function-Calling-Mistral-7B)[local-llm-function-calling](https://local-llm-function-calling.readthedocs.io/en/latest/about.html) [1](https://github.com/rizerphe/local-llm-function-calling/issues) , [llama-cpp-python](https://github.com/abetlen/llama-cpp-python/blob/main/llama_cpp/llama_chat_format.py)... [LocalAIs fc impl (even parallel fc!)](https://localai.io/features/openai-functions/) [LocalAI example of Hermes-2-Pro fc](https://github.com/mudler/LocalAI/blob/6b411ae2129e7520c0ea03d0685d3eeb788003cf/gallery/noromaid.yaml#L8) [LocalAI llama3 fc example](https://github.com/mudler/LocalAI/blob/6b411ae2129e7520c0ea03d0685d3eeb788003cf/embedded/models/llama3-instruct.yaml#L10)[LocalAI fc example](https://github.com/mudler/LocalAI/blob/6b411ae2129e7520c0ea03d0685d3eeb788003cf/examples/functions/functions-openai.py#L52) [groq fc tu](https://www.reddit.com/r/LocalLLaMA/comments/1cdotw1/llama_3_tool_use_how_does_groq_do_it/)


### Current level of #fc support in (closed, but more interestingly open) #llm #models

Official support
* Large providers (OpenAI (closed), Anthropic (closed), Mistral - of those only Mistral provides official #fc in private and, starting from v0.3, in open-weights models)
* Startups: Functionary
* Community: Hermes-2-Pro (Mistral7B tune, likely decent), [InterSync (Mistral-7B tune)](https://huggingface.co/InterSync/Mistral-7B-Instruct-v0.2-Function-Calling) - didn't check but they boast openai-like semantics, NexusRaven (don't have interesting base models)

Some possibility of support:
https://huggingface.co/InterSync/Mistral-7B-Instruct-v0.2-Function-Calling
(For qwen-1.5): https://huggingface.co/Trelis/Qwen1.5-function-calling-chat-template

Community finetunes of unknown quality:
https://huggingface.co/DavidAU/Meta-Llama-3-8B-Instruct-function-calling-Q8_0-GGUF
https://huggingface.co/Trelis/Meta-Llama-3-8B-Instruct-function-calling
https://huggingface.co/ScaleGenAI/Llama3-8B-Function-Calling #code_interpreter 
https://huggingface.co/Nhoodie/Meta-Llama-3-8b-Lexi-Uninstruct-function-calling-json-mode-Task-Arithmetic-v0.1
https://huggingface.co/hiieu/Meta-Llama-3-8B-Instruct-function-calling-json-mode
https://huggingface.co/AIGym/deepseek-coder-6.7b-chat-and-function-calling
https://huggingface.co/RonanMcGovern/Meta-Llama-3-8B-Instruct-function-calling
https://huggingface.co/dyngnosis/llama3-8b-functioncalling/tree/main
https://huggingface.co/Wsassi/Mistral-7B-Instruct-v0.2-Function-Calling-gguf/tree/main

### Dataset (finetune size tier, open) support

...

### Моя реализация #fc для LLaMA-3 и остальных доступных моделей




