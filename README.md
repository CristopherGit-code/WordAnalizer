# Win-Loss call analysis

### last update: 2025-06-20

Lite platform to filter call reports from RFPs bids and LLM supported analysis

## Features

- Use Oracle DB to filter 77 uploaded documents with call reports
- Filter by manual parameters and text-converted parameters using LLM to parse into Oracle DB json_query
- Merge content from filtered files to feed LLM chat
- Supported data analysis with OCI model based on merged content

## Setup

1. Get the necessary dependencies (use python venv):
    - gradio
    - oci
    - oracledb
    - pathlib
    - envyaml
    - python-box
    - python-dotenv
    - markitdown[all] 
        - requires *Visual c++ runtime 2022* on Windows
        - Check ```onnxruntime``` documentation for details
2. Create .env file to set the environment variables for Oracle DB and OCI client
    - For DB ensure a Cloud Wallet connection type
3. Modify ```wl_analysis.yaml``` to call the env variables and set the parameters
4. Load local word files to DB using ```load_local_files.py```.
    - Ensure to locate correctly the ```source_folder``` and ```template``` paths to the local route
    - Create folder in ```source_folder``` to feed the word files
4. Run form ```Main```

## Basic walkthrough

- [Demo video](walkthrough/WL_Calls_Demo.mp4)
- [UI](UI) folder contains other *gradio* utils
- Used Oracle DB Developer to test json_query