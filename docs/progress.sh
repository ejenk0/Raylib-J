#!/bin/zsh

# Function to check function names from a header file
check_functions() {
    local header_url=$1
    local search_dir=$2

    # Fetch the header file from the given URL
    curl -s "$header_url" -o temp_header.h

    # Extract function names using grep and awk, then strip leading '*' characters if they exist
    function_names=$(grep -E '^\w+\s+\*?\w+\s+\*?\w+\(.*\)' temp_header.h | awk '{print $3}' | sed 's/(.*//' | sed 's/^*//')

    # Clean up the downloaded file
    rm temp_header.h

    # Define ANSI color codes
    RED='\033[0;31m'
    NC='\033[0m' # No Color

    # Check if each function name exists in any .java file in the specified directory and subdirectories
    echo "$function_names" | while read -r function; do
        matches=$(grep -rl "$function" "$search_dir")
        if [ -n "$matches" ]; then
            echo -n "Function $function exists in: "
            echo "$matches" | tr '\n' ' ' | sed 's/ $//'
            echo ""
        else
            echo -e "${RED}Function $function does not exist in $search_dir${NC}"
        fi
    done
}


# Call the function for raylib.h
echo "Checking functions in raylib.h"
echo ""
check_functions "https://raw.githubusercontent.com/raysan5/raylib/master/src/raylib.h" "src/main/java/com/raylib/java"

# Call the function for raymath.h
echo ""
echo "Checking functions in raymath.h"
echo ""
check_functions "https://raw.githubusercontent.com/raysan5/raylib/master/src/raymath.h" "src/main/java/com/raylib/java/raymath"
