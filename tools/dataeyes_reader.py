from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

READER_ENDPOINT = "https://api.shuyanai.com/v1/reader"


class DataEyesReaderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("dataeyes_api_key")

        if not api_key:
            yield self.create_text_message("DataEyes API key is missing. Please set the 'dataeyes_api_key' in credentials.")
            return

        url = tool_parameters.get("url", "")
        timeout = tool_parameters.get("timeout", 10)

        if not url:
            yield self.create_text_message("Please provide url to extract.")
            return

        if not isinstance(timeout, int):
            try:
                timeout = int(timeout)
            except Exception:
                timeout = 10

        params = {"url": url, "timeout": timeout}
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.get(READER_ENDPOINT, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            yield self.create_text_message(f"Request failed: {str(e)}")
            return

        if result.get("code") == 0 and "data" in result:
            data = result["data"]
            yield self.create_json_message(data)

            title = data.get("title", "")
            markdown = data.get("markdown", "")
            formatted_result = f"URL: {url}\nTitle: {title}\nMarkdown Content:\n{markdown}"
            yield self.create_text_message(formatted_result)
        else:
            yield self.create_text_message(f"Error: {result.get('msg')}")
