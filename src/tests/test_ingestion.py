import json
import os
import pytest
from fastapi.testclient import TestClient

def test_ingest_document(client: TestClient):
    """Test `/ingest` API by uploading a PDF document."""

    # ✅ Use an absolute path for the test file
    file_path = os.path.join(os.path.dirname(__file__), "file-example_PDF_500_kB.pdf")

    with open(file_path, "rb") as file:
        response = client.post(
            "/ingest",
            files={"file": ("file-example_PDF_500_kB.pdf", file, "application/pdf")},  # ✅ Fix: No manual headers
            data={"title": "Test Document", "metadata": json.dumps({"source": "test"})}
        )

    assert response.status_code == 200, f"Error: {response.json()}"
    data = response.json()

    assert data["status"] == "success"
    assert "document_id" in data
    assert data["chunks_created"] > 0
