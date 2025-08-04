# Document ingestion router

This is a FastAPI application to be used to route document loading requests from OpenWebUI to a tika server.

The current [`TikaLoader` class](https://github.com/open-webui/open-webui/blob/5eca495d3e3b3066e7831141ed2adffbd6d179b4/backend/open_webui/retrieval/loaders/main.py#L91) for OWUI:

```python
class TikaLoader:
    def __init__(self, url, file_path, mime_type=None, extract_images=None):
        self.url = url
        self.file_path = file_path
        self.mime_type = mime_type

        self.extract_images = extract_images

    def load(self) -> list[Document]:
        with open(self.file_path, "rb") as f:
            data = f.read()

        if self.mime_type is not None:
            headers = {"Content-Type": self.mime_type}
        else:
            headers = {}

        if self.extract_images == True:
            headers["X-Tika-PDFextractInlineImages"] = "true"

        endpoint = self.url
        if not endpoint.endswith("/"):
            endpoint += "/"
        endpoint += "tika/text"

        r = requests.put(endpoint, data=data, headers=headers)

        if r.ok:
            raw_metadata = r.json()
            text = raw_metadata.get("X-TIKA:content", "<No text content found>").strip()

            if "Content-Type" in raw_metadata:
                headers["Content-Type"] = raw_metadata["Content-Type"]

            log.debug("Tika extracted text: %s", text)

            return [Document(page_content=text, metadata=headers)]
        else:
            raise Exception(f"Error calling Tika: {r.reason}")
```

Sends all documents to the `tika/text` endpoint, but for most documents it is better to use the `tika` endpoint, which return HTML formatted text that can easily be translated to markdown.
The important exception to this is pdf-documents where the plain text endpoint is preferable. [As our simple testing shows](https://github.com/itk-ai/owui_doc_ingestion).

Thus, this is an endpoint built to be used by the [OWUI `ExternalDocumentLoader`](https://github.com/open-webui/open-webui/blob/main/backend/open_webui/retrieval/loaders/external_document.py):

```python
class ExternalDocumentLoader(BaseLoader):
    def __init__(
            self,
            file_path,
            url: str,
            api_key: str,
            mime_type=None,
            **kwargs,
    ) -> None:
        self.url = url
        self.api_key = api_key

        self.file_path = file_path
        self.mime_type = mime_type

    def load(self) -> List[Document]:
        with open(self.file_path, "rb") as f:
            data = f.read()

        headers = {}
        if self.mime_type is not None:
            headers["Content-Type"] = self.mime_type

        if self.api_key is not None:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            headers["X-Filename"] = os.path.basename(self.file_path)
        except:
            pass

        url = self.url
        if url.endswith("/"):
            url = url[:-1]

        try:
            response = requests.put(f"{url}/process", data=data, headers=headers)
        except Exception as e:
            log.error(f"Error connecting to endpoint: {e}")
            raise Exception(f"Error connecting to endpoint: {e}")

        if response.ok:

            response_data = response.json()
            if response_data:
                if isinstance(response_data, dict):
                    return [
                        Document(
                            page_content=response_data.get("page_content"),
                            metadata=response_data.get("metadata"),
                        )
                    ]
                elif isinstance(response_data, list):
                    documents = []
                    for document in response_data:
                        documents.append(
                            Document(
                                page_content=document.get("page_content"),
                                metadata=document.get("metadata"),
                            )
                        )
                    return documents
                else:
                    raise Exception("Error loading document: Unable to parse content")

            else:
                raise Exception("Error loading document: No content returned")
        else:
            raise Exception(
                f"Error loading document: {response.status_code} {response.text}"
            )
```

and simply route the request to the appropiate tika endpoint.

## Developement method

This is co-created with the pycharm AI assistant using the Claude 3.5 Sonnet.

- The summary of the project requirements can be seen [here](AI_project_description.md)
- The [AI suggested project structure](AI_project_structure.md)
- The [AI project implementation plan](AI_project_implementation_plan.md)