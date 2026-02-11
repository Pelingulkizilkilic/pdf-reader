import React, { useState, useRef, useEffect } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  IconButton,
  Avatar,
  CircularProgress,
  Chip,
  Alert,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";

interface Message {
  id: string;
  text: string;
  sender: "user" | "ai";
  timestamp: Date;
}

interface ChatPageProps {
  pdfId: string;
  pdfName: string;
  onBackToUpload: () => void;
}

const ChatPage: React.FC<ChatPageProps> = ({ pdfId, pdfName, onBackToUpload }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      text: `📄 "${pdfName}" yüklendi!\n\nGerçek PDF analizine hazır. Sorularınızı sorabilirsiniz.`,
      sender: "ai",
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [analysisMode, setAnalysisMode] = useState<"real" | "demo">("real");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputText,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    try {
      // GERÇEK BACKEND'E SOR
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          pdfId: pdfId,
          question: inputText
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      console.log("Backend response:", data);

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.answer || "Cevap alınamadı.",
        sender: "ai",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiResponse]);
      setAnalysisMode("real");
      
    } catch (error: any) {
      console.error("Backend error:", error);
      
      // FALLBACK: AKILLI DEMO CEVAP
      const question = inputText.toLowerCase();
      let demoAnswer = "";
      
      if (question.includes("şifre") || question.includes("parola")) {
        demoAnswer = "🔐 PDF ŞİFRE ANALİZİ:\n\nPDF'nizde şifre taraması yapıldı.\nGerçek analiz için backend bağlantısı gerekiyor.";
      } 
      else if (question.includes("özet") || question.includes("summary")) {
        demoAnswer = "📋 PDF ÖZETİ:\n\nPDF içeriği analiz edilemedi.\nBackend bağlantısını kontrol edin.";
      }
      else {
        demoAnswer = `🤖 DEMO MOD:\n\nSoru: "${inputText}"\n\nPDF analizi için backend bağlantısı gerekiyor.\nBackend: http://localhost:8000`;
      }
      
      const fallbackResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: demoAnswer,
        sender: "ai",
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, fallbackResponse]);
      setAnalysisMode("demo");
      
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ height: "80vh", display: "flex", flexDirection: "column" }}>
      <Paper elevation={2} sx={{ p: 2, mb: 2, display: "flex", alignItems: "center" }}>
        <IconButton onClick={onBackToUpload} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h6">{pdfName}</Typography>
          <Typography variant="body2" color="text.secondary">
            PDF ID: {pdfId}
          </Typography>
        </Box>
        <Chip
          label={analysisMode === "real" ? "✅ Gerçek Analiz" : "⚠️ Demo Mod"}
          color={analysisMode === "real" ? "success" : "warning"}
          size="small"
        />
      </Paper>

      {analysisMode === "demo" && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          Backend bağlantısı yok. Demo modda çalışıyorum.
          Gerçek PDF analizi için backend'i başlatın.
        </Alert>
      )}

      <Paper
        elevation={1}
        sx={{
          flexGrow: 1,
          p: 2,
          mb: 2,
          overflow: "auto",
          backgroundColor: "#f9f9f9",
        }}
      >
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              display: "flex",
              mb: 2,
              justifyContent: message.sender === "user" ? "flex-end" : "flex-start",
            }}
          >
            {message.sender === "ai" && (
              <Avatar sx={{ bgcolor: "primary.main", mr: 1 }}>
                <SmartToyIcon />
              </Avatar>
            )}
            <Box
              sx={{
                maxWidth: "70%",
                bgcolor: message.sender === "user" ? "primary.main" : "white",
                color: message.sender === "user" ? "white" : "text.primary",
                p: 2,
                borderRadius: 2,
                boxShadow: 1,
              }}
            >
              <Typography variant="body1" style={{ whiteSpace: "pre-line" }}>
                {message.text}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  display: "block",
                  mt: 1,
                  opacity: 0.7,
                }}
              >
                {message.timestamp.toLocaleTimeString()}
              </Typography>
            </Box>
            {message.sender === "user" && (
              <Avatar sx={{ bgcolor: "secondary.main", ml: 1 }}>
                <PersonIcon />
              </Avatar>
            )}
          </Box>
        ))}
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 2 }}>
            <Avatar sx={{ bgcolor: "primary.main", mr: 1 }}>
              <SmartToyIcon />
            </Avatar>
            <Box sx={{ bgcolor: "white", p: 2, borderRadius: 2, display: "flex", alignItems: "center" }}>
              <CircularProgress size={20} sx={{ mr: 1 }} />
              <Typography>PDF analiz ediliyor...</Typography>
            </Box>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </Paper>

      <Paper elevation={2} sx={{ p: 2 }}>
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={3}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="PDF'niz hakkında soru sorun..."
            variant="outlined"
            disabled={isLoading}
          />
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isLoading}
            sx={{ minWidth: 100 }}
          >
            {isLoading ? <CircularProgress size={24} /> : <SendIcon />}
          </Button>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: "block" }}>
          {analysisMode === "real" 
            ? "✅ Gerçek PDF analizi aktif - Backend bağlantısı var" 
            : "⚠️ Demo mod - Backend: http://localhost:8000 başlatın"}
        </Typography>
      </Paper>
    </Box>
  );
};

export default ChatPage;
