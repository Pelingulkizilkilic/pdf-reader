import React, { useState } from "react";
import { useDropzone } from "react-dropzone";
import { 
  Box, Button, LinearProgress, Typography, Paper, Alert, Snackbar,
  Container, Chip
} from "@mui/material";
import { CloudUpload, InsertDriveFile, CheckCircle, Storage } from "@mui/icons-material";
import { uploadPDF } from "../services/api";

interface PDFUploadProps {
  onUploadSuccess: (data: any) => void;
}

const PDFUpload: React.FC<PDFUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    onDrop: async (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        await handleUpload(acceptedFiles[0]);
      }
    }
  });

  const handleUpload = async (file: File) => {
    setUploading(true);
    setProgress(0);
    setError(null);
    setFileName(file.name);

    try {
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 80) {
            clearInterval(interval);
            return 80;
          }
          return prev + 10;
        });
      }, 200);

      const response = await uploadPDF(file);
      
      clearInterval(interval);
      setProgress(100);
      setResult(response);
      
      setTimeout(() => {
        onUploadSuccess(response);
        setUploading(false);
      }, 1000);

    } catch (err: any) {
      setError(err.message);
      setUploading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom align="center" color="primary">
          📄 Upload PDF to AI
        </Typography>
        
        <Paper sx={{ p: 2, mb: 3, bgcolor: "info.light", textAlign: "center" }}>
          <Storage sx={{ verticalAlign: "middle", mr: 1 }} />
          <Typography variant="body2">
            Backend: <strong>http://localhost:5000</strong>
          </Typography>
        </Paper>

        <Paper
          {...getRootProps()}
          elevation={3}
          sx={{
            p: 5,
            textAlign: "center",
            cursor: uploading ? "default" : "pointer",
            border: "2px dashed",
            borderColor: isDragActive ? "primary.main" : "grey.400",
            backgroundColor: isDragActive ? "action.hover" : "background.paper",
            transition: "all 0.3s",
            minHeight: 200,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            "&:hover": {
              borderColor: uploading ? "grey.400" : "primary.main",
              backgroundColor: uploading ? "background.paper" : "action.hover"
            }
          }}
        >
          <input {...getInputProps()} disabled={uploading} />
          
          {uploading ? (
            <>
              <CloudUpload sx={{ fontSize: 60, color: "primary.main", mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                Uploading to Backend...
              </Typography>
              <Box sx={{ width: "80%", mt: 3 }}>
                <LinearProgress variant="determinate" value={progress} />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  %{progress} • Processing with AI
                </Typography>
              </Box>
            </>
          ) : result ? (
            <>
              <CheckCircle sx={{ fontSize: 60, color: "success.main", mb: 2 }} />
              <Typography variant="h5" gutterBottom color="success.main">
                ✅ Ready for AI Chat!
              </Typography>
              <Box sx={{ display: "flex", gap: 1, justifyContent: "center", mt: 2, flexWrap: "wrap" }}>
                <Chip label={`PDF: ${result.filename}`} size="small" />
                {result.pages && <Chip label={`${result.pages} pages`} size="small" color="primary" />}
              </Box>
            </>
          ) : (
            <>
              <CloudUpload sx={{ fontSize: 60, color: "primary.main", mb: 2 }} />
              <Typography variant="h5" gutterBottom>
                {isDragActive ? "📂 Drop PDF Here!" : "📤 Upload PDF"}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Drag & drop or click to select
              </Typography>
              <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 2 }}>
                Max 10MB • AI-ready processing
              </Typography>
            </>
          )}
        </Paper>

        {fileName && !uploading && !result && (
          <Box sx={{ mt: 3, textAlign: "center" }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => {
                const input = document.querySelector('input[type="file"]') as HTMLInputElement;
                if (input) input.click();
              }}
              startIcon={<InsertDriveFile />}
            >
              Process: {fileName}
            </Button>
          </Box>
        )}

        {result && (
          <Paper sx={{ p: 3, mt: 3, bgcolor: "success.light", textAlign: "center" }}>
            <Typography variant="h6" gutterBottom>
              🎉 PDF Ready for AI Analysis
            </Typography>
            <Typography variant="body2">
              Click "Sohbet Et" to start asking questions
            </Typography>
          </Paper>
        )}
      </Box>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)}>
        <Alert severity="error" sx={{ width: "100%" }}>
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default PDFUpload;


