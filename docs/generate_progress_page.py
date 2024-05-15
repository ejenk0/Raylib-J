import glob
import os
import re
import requests

# Configuration
RAYLIB_HEADER_URL_RAW = (
    "https://raw.githubusercontent.com/raysan5/raylib/master/src/raylib.h"
)
RAYLIB_HEADER_URL_RICH = "https://github.com/raysan5/raylib/blob/master/src/raylib.h"
RAYMATH_HEADER_URL_RAW = (
    "https://raw.githubusercontent.com/raysan5/raylib/master/src/raymath.h"
)
RAYMATH_HEADER_URL_RICH = "https://github.com/raysan5/raylib/blob/master/src/raymath.h"
JAVA_FILES_DIR = (
    "../src/main/java/com/raylib/java"  # Directory containing the Java files
)

# Step 1: Download the header files
response = requests.get(RAYLIB_HEADER_URL_RAW)
response.raise_for_status()  # Raise an error for bad status codes
lib_header_content = response.text
lib_header_lines = list(response.iter_lines(decode_unicode=True, delimiter="\n"))

response = requests.get(RAYMATH_HEADER_URL_RAW)
response.raise_for_status()  # Raise an error for bad status codes
math_header_content = response.text
math_header_lines = list(response.iter_lines(decode_unicode=True, delimiter="\n"))


def get_function_names(header_content):
    return re.findall(
        r"^(?:\w+\s+){2}(?:\*?\s*)(\w+)\s*\(",
        header_content,
        re.MULTILINE,
    )


# Step 2: Parse the header file to find all function names
function_names = get_function_names(lib_header_content)
math_function_names = get_function_names(math_header_content)


# Step 3: Search the Java files for the existence of those function names
def search_java_files(
    function_names: list[str], directory: str, collect_results: list[dict[str, any]]
):
    files = glob.glob(directory + "/**/*.java", recursive=True)

    for file in files:
        if not file.endswith(".java"):
            continue

        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            for function in function_names:
                if re.search(r"\b" + re.escape(function) + r"\b", content):
                    for result in collect_results:
                        if "section:" in result:
                            continue
                        if result["name"] == function:
                            result["exists"] = True
                            break


results = (
    ["section:raylib"]
    + [
        {
            "name": function,
            "exists": False,
            "url": f"{RAYLIB_HEADER_URL_RICH}#L{next(i for i, line in enumerate(lib_header_lines) if function in line) - 1}",
        }
        for function in function_names
    ]
    + ["section:raymath"]
    + [
        {
            "name": function,
            "exists": False,
            "url": f"{RAYMATH_HEADER_URL_RICH}#L{next(i for i, line in enumerate(math_header_lines) if function in line) - 3}",
        }
        for function in math_function_names
    ]
)

search_java_files(function_names + math_function_names, JAVA_FILES_DIR, results)

# Step 4: Output the findings in HTML
total_functions = sum((0 if isinstance(result, str) else 1) for result in results)
existing_functions = sum(
    (0 if isinstance(result, str) else int(result["exists"])) for result in results
)
missing_functions = total_functions - existing_functions

existing_percentage = (existing_functions / total_functions) * 100
missing_percentage = (missing_functions / total_functions) * 100

html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Raylib Function Check Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        .function {{ margin: 10px 0; }}
        .exists {{ color: white; background-color: green; }}
        .missing {{ color: red; }}
    </style>
</head>
<body>
    <h1>Raylib-J Function Coverage Report</h1>
    <p>Total Raylib functions: {total_functions}</p>
    <p>Implemented functions: {existing_percentage:.2f}%</p>
    <p>Missing functions: {missing_percentage:.2f}%</p>
    <ul>
"""

for result in results:
    if isinstance(result, str) and result.startswith("section:"):
        html_content += f"<li><h2>{result[8:]}</h2></li>"
        continue
    if isinstance(result, dict):
        class_name = "exists" if result["exists"] else "missing"
        html_content += f'<li class="function"><a href="{result["url"]}" class="{class_name}" target="_blank">{result["name"]}</a></li>'

html_content += """
    </ul>
</body>
</html>
"""

with open("function_check_report.html", "w") as file:
    file.write(html_content)

print("HTML report generated successfully!")
