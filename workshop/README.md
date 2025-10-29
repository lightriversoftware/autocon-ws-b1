# Workshop Quickstart

## Setup

1. **Install dependencies**

   ```bash
   uv sync
   ```

2. **Activate virtual environment**

   Activate the created virtual environment. Please note that this should be different than the virtual environment used for the `network_simulator`.

   ```bash
   source .venv/bin/activate
   ```

3. **Configure environment variables**

   Edit `.env` file with your Azure OpenAI credentials:

   ```
   AZURE_OPENAI_API_KEY=your_api_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your_deployment_name
   BACKEND_URL=http://localhost:8000
   ```

4. **Verify setup**
   ```bash
   python ex0_verify_setup.py
   ```
