import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

interface UploadPageProps {
  onUploadSuccess: (data: any) => void;
  onUploadError: (error: string) => void;
  isBackendOnline: boolean;
}

const UploadPage: React.FC<UploadPageProps> = ({
  onUploadSuccess,
  onUploadError,
  isBackendOnline,
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [backendChecked, setBackendChecked] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      if (file.type === "application/pdf") {
        setSelectedFile(file);
      } else {
        onUploadError("Lütfen PDF dosyası seçin.");
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      onUploadError("Lütfen önce dosya seçin.");
      return;
    }

    setIsUploading(true);

    // Önce backend kontrolü
    if (!isBackendOnline) {
      onUploadError("Backend bağlantısı yok. Lütfen backend'i başlatın.");
      setIsUploading(false);
      return;
    }

    // GERÇEK BACKEND'E YÜKLE
    try {
      console.log("📤 Backend'e yükleniyor:", selectedFile.name);
      
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      console.log("📥 Upload response:", response.status);
      
      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log("✅ Upload success:", data);
      
      onUploadSuccess(data);
      
    } catch (error: any) {
      console.error("❌ Upload error:", error);
      onUploadError(`Yükleme hatası: ${error.message}\n\nBackend: http://localhost:8000 kontrol edin.`);
      
      // Acil durum demo fallback
      setTimeout(() => {
        onUploadSuccess({
          id: "emergency_demo_" + Date.now(),
          filename: selectedFile.name,
          message: "ACİL DEMO: Backend hatası, demo moda geçildi"
        });
      }, 500);
      
    } finally {
      setIsUploading(false);
    }
  };

  const testBackend = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/health");
      const data = await response.json();
      alert(`✅ Backend çalışıyor!\n\nStatus: ${data.status}\nAI: ${data.ai_status}\nModel: ${data.model}`);
      setBackendChecked(true);
    } catch (error) {
      alert(`❌ Backend çalışmıyor!\n\nHata: ${error}\n\nBackend terminalini kontrol edin.`);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 4, maxWidth: 600, mx: "auto" }}>
      <Typography variant="h4" gutterBottom align="center">
        📄 PDF AI Assistant
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph align="center">
        PDF yükleyin, OpenAI GPT-4 ile analiz edin
      </Typography>

      <Box sx={{ mt: 4, mb: 3, textAlign: "center" }}>
        <Button
          variant="outlined"
          onClick={testBackend}
          sx={{ mb: 2 }}
        >
          {backendChecked ? "✅ Backend Test Edildi" : "🔗 Backend Bağlantısını Test Et"}
        </Button>
      </Box>

      <Box sx={{ mt: 4, mb: 3 }}>
        <input
          accept=".pdf"
          style={{ display: "none" }}
          id="pdf-upload"
          type="file"
          onChange={handleFileChange}
          disabled={isUploading || !isBackendOnline}
        />
        <label htmlFor="pdf-upload">
          <Button
            variant="outlined"
            component="span"
            fullWidth
            startIcon={<CloudUploadIcon />}
            disabled={isUploading || !isBackendOnline}
            sx={{ py: 2, mb: 2 }}
          >
            {selectedFile ? selectedFile.name : "PDF Seç"}
          </Button>
        </label>
      </Box>

      <Button
        variant="contained"
        color="primary"
        fullWidth
        onClick={handleUpload}
        disabled={!selectedFile || isUploading || !isBackendOnline}
        sx={{ py: 1.5, mb: 2 }}
      >
        {isUploading ? (
          <>
            <CircularProgress size={24} sx={{ mr: 1 }} />
            OpenAI'ye Yükleniyor...
          </>
        ) : (
          "📤 Yükle & GPT-4 ile Analiz Et"
        )}
      </Button>

      <Alert 
        severity={isBackendOnline ? "success" : "error"}
        action={
          <Button color="inherit" size="small" onClick={testBackend}>
            Test Et
          </Button>
        }
      >
        {isBackendOnline 
          ? `✅ Gerçek backend bağlantısı aktif - OpenAI GPT-4 hazır`
          : `❌ Backend bağlantısı yok - Backend terminalini kontrol edin`}
      </Alert>
      
      {!isBackendOnline && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          <strong>Backend'i başlatmak için:</strong>
          <ol>
            <li>Yeni PowerShell terminali aç</li>
            <li><code>cd "C:\Users\p\Desktop\pdf-ai-app\backend"</code></li>
            <li><code>python openai_backend.py</code></li>
            <li>Backend'in "✅ OpenAI model initialized" mesajını bekleyin</li>
          </ol>
        </Alert>
      )}
    </Paper>
  );
};

export default UploadPage;
