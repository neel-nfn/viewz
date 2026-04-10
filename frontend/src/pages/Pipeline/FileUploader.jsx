import { useState } from "react";
import { apiPost } from "../../services/apiClient";

export default function FileUploader({ taskId, type = "script" }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);

  async function handleUpload() {
    if (!file || !taskId) return;

    setUploading(true);
    try {
      // Read file as base64
      const reader = new FileReader();
      reader.onload = async (e) => {
        const base64Data = e.target.result.split(",")[1]; // Remove data:... prefix
        
        try {
          await apiPost("/attachments/upload", {
            task_id: taskId,
            file_data: base64Data,
            file_name: file.name,
            type: type
          });
          setUploaded(true);
          setFile(null);
          setTimeout(() => setUploaded(false), 3000);
        } catch (err) {
          alert(`Upload failed: ${err.message}`);
        } finally {
          setUploading(false);
        }
      };
      reader.readAsDataURL(file);
    } catch (e) {
      alert(`Error: ${e.message}`);
      setUploading(false);
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          type="file"
          className="file-input file-input-bordered flex-1"
          onChange={(e) => setFile(e.target.files[0])}
          accept={type === "script" ? ".txt,.doc,.docx" : type === "thumbnail" ? "image/*" : "*/*"}
        />
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!file || uploading}
        >
          {uploading ? "Uploading..." : "Upload"}
        </button>
      </div>
      {uploaded && (
        <div className="alert alert-success">
          <span>File uploaded successfully!</span>
        </div>
      )}
    </div>
  );
}

