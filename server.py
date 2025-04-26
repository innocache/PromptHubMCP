import httpx
import os
import glob
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP(name="Prompt Server")

@mcp.tool()
async def findprompt(keywords: str) -> str:
    """Fetch relevant prompts for the given keywords."""
    # Get all markdown files in prompts directory
    print("Searching for prompts...")
    prompts_dir = Path(".github/prompts")
    if not prompts_dir.exists():
        return "Error: Prompts directory not found"
        
    markdown_files = list(prompts_dir.glob("**/*.md"))
    if not markdown_files:
        return "No markdown files found in the prompts directory"
    
    # Calculate relevance scores for each file
    search_results = []
    keywords_list = keywords.lower().split()
    
    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().lower()
                
                # Simple scoring: count keyword occurrences
                score = 0
                for keyword in keywords_list:
                    score += content.count(keyword)
                
                # Add file to results if it contains at least one keyword
                if score > 0:
                    search_results.append({
                        "file_name": file_path.name,
                        "file_path": str(file_path),
                        "score": score
                    })
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
    
    # Sort by score (highest first) and take top 3
    search_results.sort(key=lambda x: x["score"], reverse=True)
    top_results = search_results[:3]
    
    # Format the results
    if not top_results:
        return "No matching prompts found for the given keywords"
    
    result_text = f"Top {len(top_results)} matching prompts:\n"
    for i, result in enumerate(top_results, 1):
        result_text += f"{i}. {result['file_name']} (score: {result['score']})\n"
    print(result_text)
    return result_text

@mcp.tool()
async def getprompt(prompt_name: str) -> str:
    """Fetch a specific prompt by name."""
    # Get all markdown files in prompts directory
    print("Fetching prompt...")
    prompts_dir = Path(".github/prompts")
    if not prompts_dir.exists():
        return "Error: Prompts directory not found"
        
    markdown_files = list(prompts_dir.glob("**/*.md"))
    
    # Search for the specific prompt
    for file_path in markdown_files:
        if prompt_name.lower() in file_path.name.lower():
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    print(f"Prompt found: {file_path.name}")
                    return content
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return f"No prompt found with the name '{prompt_name}'"

if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=3001)