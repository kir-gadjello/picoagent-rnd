import json
import os
import re
import subprocess
from typing import Optional
from bs4 import BeautifulSoup
import requests
import urllib.parse

MEMGPT_WORKDIR = os.environ.get('MEMGPT_WORKDIR', os.path.expanduser('~'))
JSON_LOADS_STRICT = True
JSON_ENSURE_ASCII = True

def send_message(self, message: str) -> Optional[str]:
    """
    Sends a message to the human user.

    Args:
        message (str): Message contents for the user. All unicode (including emojis) are supported.

    Returns:
        None is always returned as this function does not produce a response.
    """
    # self.interface.assistant_message(message)  # , msg_obj=self._messages[-1])
    return None

def noexport_remove_high_entropy_strings(s):
    """
    Remove high-entropy substrings from a string.

    Args:
        s (str): The input string.

    Returns:
        str: The input string with high-entropy substrings removed.
    """
    patterns = [
        r"[a-zA-Z0-9+/]{20,}",  # base64-like strings
        r"[0-9a-fA-F]{20,}",  # hex-encoded strings
        r"[a-zA-Z0-9_-]{20,}",  # other high-entropy strings (e.g., tokens, hashes)
        r'1\n([2-9]\n|1[0-9]\n|2[0-9]\n|3[0-9]\n|4[0-9]\n|5[0-9]\n|6[0-9]\n|7[0-9]\n|8[0-9]\n|9[0-9]\n|100\n)*'
    ]


    for pattern in patterns:
        s = re.sub(pattern, "", s)

    return s

def browse_url(self, url: str) -> str:
    """
    Open url in web browser to extract the main content of a webpage.

    Args:
        url (str): The URL of the webpage to extract.

    Returns:
        str: The extracted url content string, or an error message if failed.
    """
    try:
        readability_url = f"https://r.jina.ai/{url}"
        print(f"[HTTP] launching GET request to {readability_url}")
        response = requests.get(readability_url)
        if response.status_code == 200:
            content = response.text
            content = noexport_remove_high_entropy_strings(content)
            return content
        else:
            return f"Failed to extract content: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def read_from_text_file(self, filename: str, line_start: Optional[int] = 0, num_lines: Optional[int] = 1):
    """
    Read lines from a text file.

    Args:
        filename (str): The name of the file to read.
        line_start (int): Line to start reading from.
        num_lines (Optional[int]): How many lines to read (defaults to 1).

    Returns:
        str: Text read from the file
    """
    max_chars = 500
    trunc_message = True
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file '{filename}' does not exist.")

    if line_start < 1 or num_lines < 1:
        raise ValueError("Both line_start and num_lines must be positive integers.")

    lines = []
    chars_read = 0
    with open(filename, "r", encoding="utf-8") as file:
        for current_line_number, line in enumerate(file, start=1):
            if line_start <= current_line_number < line_start + num_lines:
                chars_to_add = len(line)
                if max_chars is not None and chars_read + chars_to_add > max_chars:
                    # If adding this line exceeds MAX_CHARS, truncate the line if needed and stop reading further.
                    excess_chars = (chars_read + chars_to_add) - max_chars
                    lines.append(line[:-excess_chars].rstrip("\n"))
                    if trunc_message:
                        lines.append(f"[SYSTEM ALERT - max chars ({max_chars}) reached during file read]")
                    break
                else:
                    lines.append(line.rstrip("\n"))
                    chars_read += chars_to_add
            if current_line_number >= line_start + num_lines - 1:
                break

    return "\n".join(lines)


def append_to_text_file(self, filename: str, content: str):
    """
    Append content to a text file, creating new one if it does not exist.

    Args:
        filename (str): The name of the file to append to.
        content (str): Content to append to the file.

    Returns:
        Optional[str]: None is always returned as this function does not produce a response.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"The file '{filename}' does not exist.")

    with open(filename, "a", encoding="utf-8") as file:
        file.write(content + "\n")


def raw_http_request(self, method: str, url: str, payload_json: Optional[str] = None):
    """
    Generates an HTTP request and returns the response.

    Args:
        method (str): The HTTP method (e.g., 'GET', 'POST').
        url (str): The URL for the request.
        payload_json (Optional[str]): A JSON string representing the request payload.

    Returns:
        dict: The response from the HTTP request.
    """
    try:
        headers = {"Content-Type": "application/json"}

        # For GET requests, ignore the payload
        if method.upper() == "GET":
            print(f"[HTTP] launching GET request to {url}")
            response = requests.get(url, headers=headers)
        else:
            # Validate and convert the payload for other types of requests
            if payload_json:
                payload = json.loads(payload_json, strict=JSON_LOADS_STRICT)
            else:
                payload = {}
            print(f"[HTTP] launching {method} request to {url}, payload=\n{json.dumps(payload, indent=2, ensure_ascii=JSON_ENSURE_ASCII)}")
            response = requests.request(method, url, json=payload, headers=headers)

        return {"status_code": response.status_code, "headers": dict(response.headers), "body": response.text}
    except Exception as e:
        return {"error": str(e)}


def change_directory(self, path: str):
    """
    Change the current working directory.

    Args:
        path (str): The path to change to.

    Returns:
        str: The new current working directory.
    """
    global MEMGPT_WORKDIR
    MEMGPT_WORKDIR = os.path.abspath(os.path.join(MEMGPT_WORKDIR, path))
    os.chdir(MEMGPT_WORKDIR)
    return MEMGPT_WORKDIR


# def list_directory(self, path: str = '.', recursive: bool = False):
#     """
#     List the files and directories in the specified directory path.

#     Args:
#         path (str): The directory to list. Defaults to '.' (current working directory).
#         recursive (bool): If True, list the directory recursively. Defaults to False.

#     Returns:
#         dir_p: A list of file paths contained in the directory listing.
#     """
#     path = os.path.join(MEMGPT_WORKDIR, path)
#     if recursive:
#         return _list_directory_recursive(path)
#     else:
#         return [os.path.relpath(file, MEMGPT_WORKDIR) for file in os.listdir(path)]


# def _list_directory_recursive(directory: str):
#     """
#     Recursively list the files and directories.

#     Args:
#         directory (str): The directory to list.

#     Returns:
#         str: A string representation of the directory listing in a recursive format.
#     """
#     result = []
#     for entry in os.listdir(directory):
#         entry_path = os.path.join(directory, entry)
#         if os.path.isdir(entry_path):
#             result.append(os.path.relpath(entry_path, MEMGPT_WORKDIR) + '/')
#             result.append(_list_directory_recursive(entry_path))
#         else:
#             result.append(os.path.relpath(entry_path, MEMGPT_WORKDIR))
#     return '\n'.join(result)

def grep(self, pattern: str, path: Optional[str] = None, ignore_case: Optional[bool] = True):
    """
    Search for a pattern in files using the system grep command.

    Args:
        pattern (str): The pattern to search for.
        path (Optional[str]): The file or directory path to search in. Defaults to the current working directory.
        ignore_case (bool): Ignore case when searchning. Default true.

    Returns:
        str: The output of the grep command.
    """
    if path is None:
        path = MEMGPT_WORKDIR

    command = ['grep', '-n']
    if ignore_case:
        command += '-i'
    command += [pattern]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=MEMGPT_WORKDIR)
    if process.returncode == 0:
        return process.stdout
    else:
        return process.stderr


# def file_search(self, pattern: str, files: Optional[List[str]] = None):
#     """
#     Search for a pattern in files.

#     Args:
#         pattern (str): The pattern to search for.
#         files (Optional[List[str]]): The files to search in. Defaults to all files in the current working directory.

#     Returns:
#         List[str]: A list of file paths representatiing the search results. Possibly empty.
#     """
#     if files is None:
#         files = os.listdir(MEMGPT_WORKDIR)
#     results = []
#     for file in files:
#         file_path = os.path.join(MEMGPT_WORKDIR, file)
#         if os.path.isfile(file_path):
#             with open(file_path, 'r') as f:
#                 for line_num, line in enumerate(f, start=1):
#                     if pattern in line:
#                         results.append(f'{file}:{line_num}:{line.strip()}')
    
#     return results

def noexport_check_unsafe_shell_cmd(cmd: str) -> bool:
    """
    Check if the shell command is potentially destructive.

    Args:
        cmd (str): The shell command to check.

    Returns:
        bool: True if the command is potentially destructive, False otherwise.
    """
    # Regular expressions to match potentially destructive commands
    patterns = [
        r'\b(rm|delete|del|erase|unlink|rmdir|mv\s+/(bin|sbin|usr|lib|etc))\b',  # File and directory deletion
        r'\b(chmod|chown)\s+[0-7]{3,4}\b',  # Permission changes
        r'\b(mkdir|mkfifo|mknode|mksock)\s+',  # File system modifications
        r'\b(mv|ln|symlink)\s+',  # File copying and linking
        r'\b(sed|awk)\s+.*\s*(>|>>|\|)\s+',  # Commands that can modify files
        r'\b(perl|python|ruby|php|bash|sh|zsh|ksh)\s+.*\s*(>|>>|\|)\s+',  # Scripting languages that can modify files
        r'\b(dd|tar|zip|gzip|bzip2|xz)\s+',  # Archive and compression tools
        r'\b(chsh|chfn|usermod|groupmod)\s+',  # User and group modifications
        r'\b(apt-get|apt|yum|dnf|pip|gem|npm)\s+',  # Package managers
        # r'\b(cp|mv|ln|symlink)\s+',  # File copying and linking
    ]

    for pattern in patterns:
        if re.search(pattern, cmd):
            return True

    return False

# def exec_shell_cmd(self, cmd: str):
#     """
#     Execute a Unix shell command in the current working directory.

#     Args:
#         cmd (str): The shell command to execute.

#     Returns:
#         CommandResult: An object containing the output of the command as a string and the return code of the command as an integer.
#     """

#     if not os.environ.get("MEMGPT_DISABLE_SAFECMD") and check_unsafe_shell_cmd(cmd):
#         raise RuntimeError(f"Command '{cmd}' is potentially destructive and forbidden for safety reasons. Use MEMGPT_DISABLE_SAFECMD=true to disable safety checks.")
   

#     process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=MEMGPT_WORKDIR)
#     if process.returncode != 0:
#         raise RuntimeError(f"Command '{cmd}' failed with return code {process.returncode}: {process.stderr}")
    
#     return dict(stdout=process.stdout, retcode=process.returncode)

def exec_shell_cmd(self, cmd: str) -> str:
    """
    Execute a Unix shell command in the current working directory.

    Args:
        cmd (str): The shell command to execute.

    Returns:
        A raw string containing the shell command and its return code as an integer followed by stdout log
    """

    if not os.environ.get("MEMGPT_DISABLE_SAFECMD") and noexport_check_unsafe_shell_cmd(cmd):
        raise RuntimeError(f"Command '{cmd}' is potentially destructive and forbidden for safety reasons.<%%!!>Use MEMGPT_DISABLE_SAFECMD=true to disable safety checks.</%%!!>")
   

    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, cwd=MEMGPT_WORKDIR)
    if process.returncode != 0:
        raise RuntimeError(f"Command '{cmd}' failed with return code {process.returncode}: {process.stderr}")
    
    return f"{cmd} returned {process.returncode}\n{process.stdout}"



def google_search(self, query: str):
    """
    Performs a web search using Google and returns a list of results.

    Args:
        query (str): The search query.

    Returns:
        List[Dict[str, str]]: A list of search results, each containing:
            - link (str): The URL of the result.
            - title (str): The title of the result.
            - text (str): A text snippet from the result.
    """

    url = "https://html.duckduckgo.com/lite/"
    payload = {"q": query}
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "html.duckduckgo.com",
        "Origin": "https://html.duckduckgo.com",
        "Referer": "https://html.duckduckgo.com/",
        "User-Agent": os.environ.get(
            "MEMGPT_USERAGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        ),
    }
    response = requests.post(
        url, data=urllib.parse.urlencode(payload).encode("utf-8"), headers=headers
    )

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")

    def parse_results(html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find_all("table")[2]

        titles = table.find_all("a", class_="result-link")
        snippets = table.find_all("td", class_="result-snippet")
        links = table.find_all("span", class_="link-text")
        results = []

        N = min(len(titles), len(snippets), len(links))
        i = 0
        while i < N:
            results.append(
                {
                    "link": links[i].text.strip(),
                    "title": titles[i].text.strip(),
                    "text": snippets[i].text.strip(),
                }
            )
            i += 1
        return results

    return parse_results(response.text)
