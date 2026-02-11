import React, { useState } from "react";
import {
  Container,
  Box,
  Typography,
  Chip,
  CircularProgress,
  Alert,
} from "@mui/material";
import UploadPage from "./components/UploadPage";
import ChatPage from "./components/ChatPage";

interface PdfData {
  id: string;
  name: string;
}

function App() {
  const [currentPage, setCurrentPage] = useState<"upload" | "chat">("upload");
  const [pdfData, setPdfData] = useState<PdfData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendOnline, setBackendOnline] = useState<boolean>(false);
  const [checkingBackend, setCheckingBackend] = useState<boolean>(true);

  React.useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/health");
        setBackendOnline(response.ok);
      } catch {
        setBackendOnline(false);
      } finally {
        setCheckingBackend(false);
      }
    };
    
    checkBackend();
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleUploadSuccess = (data: any) => {
    setPdfData({ 
      id: data.id || "demo-id", 
      name: data.filename || "uploaded.pdf" 
    });
    setCurrentPage("chat");
    setError(null);
  };

  const handleUploadError = (err: string) => {
    setError(err);
  };

  const handleBackToUpload = () => {
    setCurrentPage("upload");
    setPdfData(null);
    setError(null);
  };

  return (
    <Container maxWidth="lg">
      {/* Backend Status */}
      <Box sx={{ mb: 3, textAlign: "center" }}>
        <Chip
          label={
            checkingBackend
              ? "Backend kontrol ediliyor..."
              : backendOnline
              ? "✅ Backend Online"
              : "❌ Backend Offline"
          }
          color={backendOnline ? "success" : "error"}
          variant="outlined"
          icon={checkingBackend ? <CircularProgress size={16} /> : undefined}
        />
      </Box>

      {/* Title */}
      <Typography
        variant="h3"
        component="h1"
        align="center"
        gutterBottom
        sx={{ fontWeight: "bold", mb: 4 }}
      >
        📄 PDF AI Assistant
      </Typography>

      {/* Error */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Page Content */}
      {currentPage === "upload" ? (
        <UploadPage
          onUploadSuccess={handleUploadSuccess}
          onUploadError={handleUploadError}
          isBackendOnline={backendOnline}
        />
      ) : (
        pdfData && (
          <ChatPage
            pdfId={pdfData.id}
            pdfName={pdfData.name}
            onBackToUpload={handleBackToUpload}
          />
        )
      )}

      {/* Warning */}
      {!backendOnline && !checkingBackend && (
        <Alert severity="warning" sx={{ mt: 3 }}>
          Backend bağlantısı yok. Demo modda çalışıyorsunuz.
        </Alert>
      )}
    </Container>
  );
}

export default App;
