set shell := ["powershell.exe", "-NoLogo", "-Command"]

default:list


clean:
    uv run python just.py clean


info:
    uv run python just.py info



list:
    uv run python just.py list
    
