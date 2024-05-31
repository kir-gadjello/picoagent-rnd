# Picoagent-RnD

Web &amp; CLI capable LLM agent (very early research prototype). Fresh implementation that does not rely on and isn't constrained by legacy frameworks.

Note: Once the code stabilizes, the "-RnD" suffix will be removed.

# Motivation

I believe that LLM agents have massive long-term potential. It appears that contexts arising from agentic usecases remain challenging for even the most intelligent chat-tuned LLMs, but this will improve over time as new open and private models, datasets, agent engines, and training regimens become available, as seen recently with [SWE-Bench](https://huggingface.co/spaces/OpenDevin/evaluation). In terms of the Gartner cycle, we are still climbing out of the Trough of Disillusionment that followed the early 2023 bubble, but this sentiment is already out of date.

The aim of this project is to explore the solution space of a "second generation" agent engine which synergizes *well* (via specialized prompts, agent loop hyperparams and finetunes) with the empirically observed cognitive profile of the best available open-weights LLMs, to demonstrate good (or at least significantly superior, compared to the first generation) performance on a diverse set of outcome-oriented tasks, some of which are:
* using cli to manipulate data and run programs
* debugging failing programs in the context of a git repo with tests
* basic project-level software development, i.e. [SWE-bench-lite](https://www.swebench.com/lite.html)
* basic web browsing, i.e. searching for useful github projects and tools according to fine-grained user requirements
* question answering over unstructured data directories and databases

# Project desiderata

## Stage 0: Proof-of-Concept
1. A showcase of 0-shot agentic capability of modern LLMs like Llama3 8B & 70B.
2. 0-shot tool use with several non-toy usecases
3. Basic ReAct-like agentic loop with optional basic critic
3. (A11y+OCR)-based web agent scaffolding
4. Adaptive context length management a-la MemGPT: log & web page summarization
5. Realistic VibeEval-like evals for terminal & basic web tasks

## Stage 1: Pushing the envelope
1. Evals stressing foundational agent capabilities, such as effective context size and robustness to lost-in-the-middle failure modes, ICL-RL etc
2. Advanced scaffolding and optimized toolkit + function calling format
3. Episodic memory (better than MemGPT)
4. Episodic RL (effective [👍,👎] without backprop)
5. Adaptive computation effort
6. Advanced critic, offline batch self-criticism
7. Agentic finetune & dataset...
8. Nontrivial SWE-bench score with the same general purpose agent engine

# Current state and recommendations

## Architecture

The current agent demo uses a ReAct-like interaction template with inner monologue and JSON grammar to implement function calling. Available tools are defined in `tool_defs.py` and get automatically converted into LLM prompt specifications and JSON schemas for the llama.cpp grammar engine. Even in this very simple configuration the agent is capable of chaining diverse behaviors, as examples show.

## LLM requirements
Use of a self-hosted or OpenAI-like API (GROQ, Together) with a recently released strong chat LLM is recommended. Main LLMs I use developing this project are [8B](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct) and [70B](https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct) variants of Meta's Llama-3-Instruct via local llama.cpp.

Currently, the 0-shot function calling framework heavily relies on JSON grammar feature of llama.cpp; I intend to relax this requirement in the future.

I aim to make all Stage 0 and as much of Stage 1 project features as possible supported with Llama-3-70B-Instruct (even quantized to fit in a single 24GiB GPU), with the rest of the features requiring no more than a special finetune of the same 70B model.

## Install
Currently you can start working with the project by cloning this git repo and creating a python virtual environment (venv, pyenv, conda) and installing the dependencies (soon: running inside docker environment):
`pip install -r requirements.txt'`

Make sure you have valid `OPENAI_API_BASE` and `OPENAI_API_KEY` environment variables pointing to a working LLM backend. For now the recommended inference engine is [llama.cpp](https://github.com/ggerganov/llama.cpp) and the tested LLM checkpoint is [Meta-Llama-3-70B-Instruct-IQ2_XS.gguf](https://huggingface.co/lmstudio-community/Meta-Llama-3-70B-Instruct-BPE-fix-GGUF/blob/main/Meta-Llama-3-70B-Instruct-IQ2_XS.gguf).

## Examples

CLI chat-style invocations of the current basic agent demo:
* `python main.py -v "browse HN and tell me the most salient AI/LLM stories of today"`
* `python main.py -v "find a ready to use github repo implementing suffix trees in python"`
* `python main.py -v "write and run a basic python http api with helloworld endpoint"`
* `python main.py -v "help me answer questions about my obsidian vault located at <...>"`

# Source code licensing, etc

Picoagent uses some basic functions from [MemGPT](https://github.com/cpacker/MemGPT) project, where the author is a minor contributor (thanks btw!) - these parts of source code inherit the MemGPT license. The license for the code written by Kirill Gadjello in this project is GPLv3, as included in LICENSE file (mostly to encourage the occasional hacker to share prompts & hyperparameters, which is important for the LLM agent craft).

I plan to rewrite the useful part of said functions once it becomes apparent that this project is about to exit the experimentation phase.

# Honorable mentions

A necessarily incomplete and in-flux list of projects that influenced me:

## Projects
* [MemGPT](https://github.com/cpacker/MemGPT)
* [OpenDevin](https://github.com/OpenDevin/OpenDevin) 
* [Aider](https://github.com/paul-gauthier/aider) 
* [read_agent_demo](https://github.com/read-agent/read-agent.github.io/blob/main/assets/read_agent_demo.ipynb) 
* [WebLlama/WebLINX](https://github.com/McGill-NLP/webllama) 
* [Functionary](https://github.com/MeetKai/functionary) 
* [OpenCodeInterpreter](https://github.com/OpenCodeInterpreter/OpenCodeInterpreter) 

## Research
* [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)
* [A Human-Inspired Reading Agent with Gist Memory of Very Long Contexts](https://arxiv.org/abs/2402.09727)
* [WebGPT: Browser-assisted question-answering with human feedback](https://arxiv.org/abs/2112.09332)
* [MemGPT](https://arxiv.org/abs/2310.08560)
* [Language Agent Tree Search Unifies Reasoning Acting and Planning in Language Models](https://arxiv.org/abs/2310.04406)
* [Tree of Thoughts: Deliberate Problem Solving with Large Language Models](https://arxiv.org/abs/2305.10601)
* [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366)
* [WebLINX: Real-World Website Navigation with Multi-Turn Dialogue](https://arxiv.org/abs/2402.05930)
* [SWE-bench: Can Language Models Resolve Real-World GitHub Issues?](https://arxiv.org/abs/2310.06770)
* [OpenCodeInterpreter: Integrating Code Generation with Execution and Refinement](https://arxiv.org/abs/2402.14658)
* [Towards General Computer Control: A Multimodal Agent for Red Dead Redemption II as a Case Study](https://arxiv.org/abs/2403.03186)
* [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
* [Agent-FLAN](https://arxiv.org/abs/2403.12881)
* [In-context Reinforcement Learning with Algorithm Distillation](https://arxiv.org/abs/2210.14215)

