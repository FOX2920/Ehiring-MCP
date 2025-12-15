# FastMCP Cloud

> The fastest way to deploy your MCP server

[FastMCP Cloud](https://fastmcp.cloud) is a managed platform for hosting MCP servers, built by the FastMCP team. While the FastMCP framework will always be fully open-source, we created FastMCP Cloud to solve the deployment challenges we've seen developers face. Our goal is to provide the absolute fastest way to make your MCP server available to LLM clients like Claude and Cursor.

FastMCP Cloud is a young product and we welcome your feedback. Please join our [Discord](https://discord.com/invite/aGsSC3yDF4) to share your thoughts and ideas, and you can expect to see new features and improvements every week.

<Note>
  FastMCP Cloud supports both **FastMCP 2.0** servers and also **FastMCP 1.0** servers that were created with the official MCP Python SDK.
</Note>

<Tip>
  FastMCP Cloud is completely free while in beta!
</Tip>

## Prerequisites

To use FastMCP Cloud, you'll need a [GitHub](https://github.com) account. In addition, you'll need a GitHub repo that contains a FastMCP server instance. If you don't want to create one yet, you can proceed to [step 1](#step-1-create-a-project) and use the FastMCP Cloud quickstart repo.

Your repo can be public or private, but must include at least a Python file that contains a FastMCP server instance.

<Tip>
  To ensure your file is compatible with FastMCP Cloud, you can run `fastmcp inspect <file.py:server_object>` to see what FastMCP Cloud will see when it runs your server.
</Tip>

If you have a `requirements.txt` or `pyproject.toml` in the repo, FastMCP Cloud will automatically detect your server's dependencies and install them for you. Note that your file *can* have an `if __name__ == "__main__"` block, but it will be ignored by FastMCP Cloud.

For example, a minimal server file might look like:

```python  theme={"theme":{"light":"snazzy-light","dark":"dark-plus"}}
from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"
```

## Getting Started

There are just three steps to deploying a server to FastMCP Cloud:

### Step 1: Create a Project

Visit [fastmcp.cloud](https://fastmcp.cloud) and sign in with your GitHub account. Then, create a project. Each project corresponds to a GitHub repo, and you can create one from either your own repo or using the FastMCP Cloud quickstart repo.

<img src="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/quickstart.png?fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=a98be26fc2265a8b74476d1747287e53" alt="FastMCP Cloud Quickstart Screen" data-og-width="2656" width="2656" data-og-height="1808" height="1808" data-path="assets/images/fastmcp_cloud/quickstart.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/quickstart.png?w=280&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=6574699628440718a296eecb1c9c1d34 280w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/quickstart.png?w=560&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=740b6cb6a21b2bd165f0348b7f70f1bb 560w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/quickstart.png?w=840&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=183e219af3c0d9bcc87a7e192f9d861a 840w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/quickstart.png?w=1100&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=5b22225c6d1f2fd48e461f6e7c8a4137 1100w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/quickstart.png?w=1650&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=9de436ae99e8e175268ab0415ae69373 1650w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/quickstart.png?w=2500&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=b2320ef39fff5ff3a00d5c09787fefc8 2500w" />

Next, you'll be prompted to configure your project.

<img src="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/create_project.png?fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=4c221cd0734a6fd7b634970ac0aff73a" alt="FastMCP Cloud Configuration Screen" data-og-width="2656" width="2656" data-og-height="1808" height="1808" data-path="assets/images/fastmcp_cloud/create_project.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/create_project.png?w=280&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=168c690ac8a8e5098b05c8e23cf9173b 280w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/create_project.png?w=560&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=16cd0ee3977040439e9982e8aa438ffe 560w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/create_project.png?w=840&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=4b0265a257b6a9510c85863da1b5e17a 840w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/create_project.png?w=1100&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=e898cfe81f01bf14312d98902be41b5c 1100w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/create_project.png?w=1650&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=d97a7ddad8e60c86e303faa8e37d784c 1650w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/create_project.png?w=2500&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=51b9fa2763dc5064c1eef4f8f90af77a 2500w" />

The configuration screen lets you specify:

* **Name**: The name of your project. This will be used to generate a unique URL for your server.
* **Entrypoint**: The Python file containing your FastMCP server (e.g., `echo.py`). This field has the same syntax as the `fastmcp run` command, for example `echo.py:my_server` to specify a specific object in the file.
* **Authentication**: If disabled, your server is open to the public. If enabled, only other members of your FastMCP Cloud organization will be able to connect.

Note that FastMCP Cloud will automatically detect yours server's Python dependencies from either a `requirements.txt` or `pyproject.toml` file.

### Step 2: Deploy Your Server

Once you configure your project, FastMCP Cloud will:

1. Clone the repository
2. Build your FastMCP server
3. Deploy it to a unique URL
4. Make it immediately available for connections

<img src="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/deployment.png?fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=cdb7389c54a0d9d7853807b4bf996d63" alt="FastMCP Cloud Deployment Screen" data-og-width="2656" width="2656" data-og-height="1808" height="1808" data-path="assets/images/fastmcp_cloud/deployment.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/deployment.png?w=280&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=a218792290c0798cd9e79f479904d245 280w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/deployment.png?w=560&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=a06622288cdbf1c267175e36965c4fb1 560w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/deployment.png?w=840&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=69c5e285cb70f1192f96caafa79eb26e 840w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/deployment.png?w=1100&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=831d6f9609c2a70d59ae087f4064b140 1100w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/deployment.png?w=1650&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=3247286a4749d1cfbe408ac6c3e02fce 1650w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/deployment.png?w=2500&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=f6b3a204d808cad20b40f200e2e40d7a 2500w" />

FastMCP Cloud will monitor your repo and redeploy your server whenever you push a change to the `main` branch. In addition, FastMCP Cloud will build and deploy servers for every PR your open, hosting them on unique URLs, so you can test changes before updating your production server.

### Step 3: Connect to Your Server

Once your server is deployed, it will be accessible at a URL like:

```
https://your-project-name.fastmcp.app/mcp
```

You should be able to connect to it as soon as you see the deployment succeed! FastMCP Cloud provides instant connection options for popular LLM clients:

<img src="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/connect.png?fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=ec716be49f8e43028eb872ff3ac95624" alt="FastMCP Cloud Connection Screen" data-og-width="2568" width="2568" data-og-height="1720" height="1720" data-path="assets/images/fastmcp_cloud/connect.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/connect.png?w=280&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=10053e00e12a0d29376fa9e36f6db5e4 280w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/connect.png?w=560&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=d8ea20e041da1d97f4cc681a36d7a09b 560w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/connect.png?w=840&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=8da73612790ad0cbd5e97958ba590ee5 840w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/connect.png?w=1100&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=6db33a68f39c1796ce24fff8781a9add 1100w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/connect.png?w=1650&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=beb88faa10fd0c9dba4ef5ec2b8ce955 1650w, https://mintcdn.com/fastmcp/hUosZw7ujHZFemrG/assets/images/fastmcp_cloud/connect.png?w=2500&fit=max&auto=format&n=hUosZw7ujHZFemrG&q=85&s=fb9b2640011b3757a9a0cdcb4b4449c4 2500w" />


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://gofastmcp.com/llms.txt