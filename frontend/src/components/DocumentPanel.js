import React, { useState, useEffect } from "react";
import { toast } from "react-hot-toast";

const DocumentPanel = ({
  roomId,
  username,
  code,
  setCode,
  language,
  onLanguageChange,
}) => {
  const [documents, setDocuments] = useState([]);
  const [versions, setVersions] = useState([]);
  const [currentDoc, setCurrentDoc] = useState(null);
  const [showVersions, setShowVersions] = useState(false);
  const [title, setTitle] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const apiUrl = `${process.env.REACT_APP_BACKEND_URL}/api/docs`;

  // Load user documents
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`${apiUrl}`);
      if (!response.ok) throw new Error("Failed to fetch documents");
      const data = await response.json();
      setDocuments(data);
    } catch (error) {
      toast.error("Error loading documents");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchVersions = async (docId) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${apiUrl}/${docId}/versions`);
      if (!response.ok) throw new Error("Failed to fetch versions");
      const data = await response.json();
      setVersions(data);
      setShowVersions(true);
    } catch (error) {
      toast.error("Error loading versions");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const openDocument = async (docId) => {
    try {
      setIsLoading(true);
      const response = await fetch(`${apiUrl}/${docId}`);
      if (!response.ok) throw new Error("Failed to open document");
      const data = await response.json();

      setCurrentDoc(data);
      setTitle(data.title);

      setCode(data.content);

      if (data.language !== language) {
        onLanguageChange({
          target: {
            value: data.language,
            mode: getEditorMode(data.language),
          },
        });
      }

      toast.success(`Opened "${data.title}"`);
    } catch (error) {
      toast.error("Error opening document");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveDocument = async () => {
    try {
      setIsLoading(true);

      if (!title.trim()) {
        toast.error("Please enter a document title");
        return;
      }

      if (currentDoc) {
        const response = await fetch(`${apiUrl}/${currentDoc.id}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: title,
            language: language,
            content: code,
          }),
        });

        if (!response.ok) throw new Error("Failed to save document");
        const data = await response.json();
        setCurrentDoc(data);
        toast.success("Document saved");
      } else {
        // Create new
        const response = await fetch(`${apiUrl}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title: title,
            language: language,
            content: code,
          }),
        });

        if (!response.ok) throw new Error("Failed to create document");
        const data = await response.json();
        setCurrentDoc(data);
        toast.success("Document created");

        fetchDocuments();
      }
    } catch (error) {
      toast.error("Error saving document");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const saveVersion = async () => {
    if (!currentDoc) {
      toast.error("Save document first");
      return;
    }

    try {
      setIsLoading(true);
      console.log("Saving version for document:", currentDoc.id);

      const response = await fetch(
        `${apiUrl}/${currentDoc.id}?create_version=true`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            title,
            language,
            content: code,
          }),
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error saving version:", errorText);
        throw new Error("Failed to save version");
      }

      const data = await response.json();
      setCurrentDoc(data);
      toast.success("Version saved");

      if (showVersions) {
        fetchVersions(currentDoc.id);
      }
    } catch (error) {
      toast.error("Error saving version: " + error.message);
      console.error("Error saving version:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteDocument = async () => {
    if (!currentDoc) return;

    if (
      !window.confirm(`Are you sure you want to delete "${currentDoc.title}"?`)
    ) {
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(`${apiUrl}/${currentDoc.id}`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Failed to delete document");

      toast.success("Document deleted");
      newDocument();
      fetchDocuments();
    } catch (error) {
      toast.error("Error deleting document");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const restoreVersion = async (versionId) => {
    if (!currentDoc) return;

    try {
      setIsLoading(true);
      const response = await fetch(
        `${apiUrl}/${currentDoc.id}/restore/${versionId}`,
        {
          method: "POST",
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error restoring version:", errorText);
        throw new Error("Failed to restore version");
      }

      const data = await response.json();
      setCurrentDoc(data);

      setCode(data.content);

      toast.success("Version restored");
      setShowVersions(false);
    } catch (error) {
      toast.error("Error restoring version");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const viewVersion = async (versionId) => {
    if (!currentDoc) return;

    try {
      setIsLoading(true);
      const response = await fetch(
        `${apiUrl}/${currentDoc.id}/versions/${versionId}/content`
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error viewing version:", errorText);
        throw new Error("Failed to view version");
      }

      const data = await response.json();

      setCode(data.content);

      toast.success("Viewing old version - changes not saved");
    } catch (error) {
      toast.error("Error viewing version");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const confirmRestoreVersion = async (versionId) => {
    if (!currentDoc) return;

    if (
      !window.confirm(
        "Are you sure you want to restore this version? This will replace the current document content."
      )
    ) {
      return;
    }

    try {
      setIsLoading(true);
      const response = await fetch(
        `${apiUrl}/${currentDoc.id}/restore/${versionId}`,
        { method: "POST" }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error restoring version:", errorText);
        throw new Error("Failed to restore version");
      }

      const data = await response.json();
      setCurrentDoc(data);

      setCode(data.content);

      toast.success("Version restored");
      setShowVersions(false);
    } catch (error) {
      toast.error("Error restoring version");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };
  const newDocument = () => {
    setCurrentDoc(null);
    setTitle("");
    setCode("");
    setShowVersions(false);
  };

  const getEditorMode = (lang) => {
    const modeMap = {
      python: "python",
      cpp: "clike",
      java: "clike",
      javascript: "javascript",
      bash: "shell",
      markdown: "markdown",
    };
    return modeMap[lang] || lang;
  };

  return (
    <div className="document-panel">
      <h3>Document Management</h3>

      <div className="document-controls">
        <input
          type="text"
          placeholder="Document Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="doc-title-input"
        />

        <div className="doc-buttons">
          <button className="btn doc-btn" onClick={newDocument}>
            New
          </button>
          <button
            className="btn doc-btn"
            onClick={saveDocument}
            disabled={isLoading || !title.trim()}
          >
            Save
          </button>
          <button
            className="btn doc-btn"
            onClick={saveVersion}
            disabled={isLoading || !currentDoc}
          >
            Save Version
          </button>
          <button
            className="btn doc-btn"
            onClick={() => {
              if (currentDoc) {
                fetchVersions(currentDoc.id);
              } else {
                toast.error("Save document first");
              }
            }}
            disabled={isLoading || !currentDoc}
          >
            Versions
          </button>
          <button
            className="btn doc-btn delete-btn"
            onClick={deleteDocument}
            disabled={isLoading || !currentDoc}
          >
            Delete
          </button>
        </div>
      </div>

      {!showVersions ? (
        <div className="documents-list">
          <h4>My Documents</h4>
          {isLoading ? (
            <p>Loading...</p>
          ) : documents.length === 0 ? (
            <p>No documents yet</p>
          ) : (
            <ul>
              {documents.map((doc) => (
                <li key={doc.id} onClick={() => openDocument(doc.id)}>
                  {doc.title} ({doc.language})
                </li>
              ))}
            </ul>
          )}
        </div>
      ) : (
        <div className="versions-list">
          <div className="version-header">
            <h4>Document Versions</h4>
            <button
              className="btn small-btn"
              onClick={() => setShowVersions(false)}
            >
              Back
            </button>
          </div>

          {isLoading ? (
            <p>Loading...</p>
          ) : versions.length === 0 ? (
            <p>No versions available</p>
          ) : (
            <ul>
              {versions.map((version) => (
                <li key={version.id} className="version-item">
                  <span onClick={() => viewVersion(version.id)}>
                    Version {version.version_number} (
                    {new Date(version.created_at).toLocaleString()})
                  </span>
                  <button
                    className="btn small-btn restore-btn"
                    onClick={() => confirmRestoreVersion(version.id)}
                  >
                    Restore
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentPanel;
