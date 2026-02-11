import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  CircularProgress,
  Avatar,
  Container,
  IconButton,
  Card,
  CardContent,
  Chip,
  Alert
} from "@mui/material";
import { Send as SendIcon, SmartToy as AIIcon, Person as UserIcon, CheckCircle } from "@mui/icons-material";
import ReactMarkdown from "react-markdown";
import { askQuestion } from "../services/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  pdfId: string;
  pdfName: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ pdfId, pdfName }) => {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content: `🎉 **Backend Connected Successfully!**\n\n` +
               `You are now chatting with **${pdfName}**\n` +
               `PDF ID: \`${pdfId}\`\n\n` +
               `**How to use:**\n` +
               `• Ask about the content\n` +
               `• Request summaries\n` +
               `• Get specific information\n\n` +
               `_Real AI responses from FastAPI backend_`,
      timestamp: new Date()
    }
  ]);
  
  const [connectionStatus, setConnectionStatus] = useState<"connected" | "error">("connected");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleAskQuestion = async () => {
    if (!question.trim() || loading) return;
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: question,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);
    const currentQuestion = question;
    setQuestion("");

    try {
      const response = await askQuestion(pdfId, currentQuestion);
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: response.answer || response.message || "No response from AI",
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setConnectionStatus("connected");
      
    } catch (error: any) {
      console.error("Chat error:", error);
      
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content: `**Connection Error**\n\n` +
                 `Unable to reach backend AI.\n` +
                 `Please check:\n` +
                 `1. Backend server is running\n` +
                 `2. API endpoints are correct\n` +
                 `3. Network connection`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
      setConnectionStatus("error");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAskQuestion();
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("tr-TR", { 
      hour: "2-digit", 
      minute: "2-digit" 
    });
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ 
        height: "85vh", 
        display: "flex", 
        flexDirection: "column",
        bgcolor: "background.default",
        borderRadius: 2,
        overflow: "hidden",
        border: 1,
        borderColor: "divider",
        boxShadow: 3
      }}>
        {/* Header */}
        <Paper 
          elevation={0} 
          sx={{ 
            p: 2, 
            bgcolor: connectionStatus === "connected" ? "primary.main" : "error.main",
            color: "white",
            borderRadius: 0,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center" }}>
            <CheckCircle sx={{ mr: 1 }} />
            <Typography variant="h6">
              💬 PDF AI Chat
            </Typography>
          </Box>
          <Box>
            <Chip 
              label={connectionStatus === "connected" ? "Backend Connected" : "Connection Error"}
              color={connectionStatus === "connected" ? "success" : "error"}
              size="small"
              sx={{ color: "white" }}
            />
            <Typography variant="caption" display="block" sx={{ mt: 0.5, opacity: 0.9 }}>
              PDF: {pdfName}
            </Typography>
          </Box>
        </Paper>

        {/* Messages Area */}
        <Box sx={{ 
          flex: 1, 
          overflow: "auto", 
          p: 2,
          bgcolor: "grey.50",
          backgroundImage: "linear-gradient(45deg, #f9f9f9 25%, transparent 25%, transparent 75%, #f9f9f9 75%)",
          backgroundSize: "20px 20px"
        }}>
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: "flex",
                justifyContent: message.role === "user" ? "flex-end" : "flex-start",
                mb: 2,
                animation: "fadeIn 0.3s ease"
              }}
            >
              <Card
                sx={{
                  maxWidth: "75%",
                  bgcolor: message.role === "user" ? "primary.light" : "white",
                  color: message.role === "user" ? "white" : "text.primary",
                  borderRadius: 3,
                  boxShadow: 2,
                  borderLeft: message.role === "assistant" ? "4px solid #4CAF50" : "none"
                }}
              >
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                    <Avatar sx={{ 
                      width: 28, 
                      height: 28, 
                      mr: 1,
                      bgcolor: message.role === "user" ? "primary.main" : "secondary.main"
                    }}>
                      {message.role === "user" ? <UserIcon /> : <AIIcon />}
                    </Avatar>
                    <Typography variant="caption" sx={{ opacity: 0.7, fontWeight: "bold" }}>
                      {message.role === "user" ? "You" : "AI Assistant"} • {formatTime(message.timestamp)}
                    </Typography>
                  </Box>
                  
                  {message.role === "assistant" ? (
                    <Box sx={{ pl: 1 }}>
                      <ReactMarkdown
                        components={{
                          p: ({node, ...props}) => <Typography variant="body1" paragraph sx={{ mb: 1 }} {...props} />,
                          h1: ({node, ...props}) => <Typography variant="h6" gutterBottom sx={{ mt: 2 }} {...props} />,
                          h2: ({node, ...props}) => <Typography variant="subtitle1" gutterBottom {...props} />,
                          ul: ({node, ...props}) => <Typography component="ul" sx={{ pl: 2, mb: 1 }} {...props} />,
                          li: ({node, ...props}) => <Typography component="li" sx={{ mb: 0.5 }} {...props} />,
                          code: ({node, ...props}) => (
                            <code style={{ 
                              backgroundColor: "#f5f5f5", 
                              padding: "2px 6px", 
                              borderRadius: "4px",
                              fontFamily: "'Courier New', monospace",
                              fontSize: "0.9em"
                            }} {...props} />
                          ),
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </Box>
                  ) : (
                    <Typography variant="body1" sx={{ pl: 1 }}>
                      {message.content}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Box>
          ))}
          
          {loading && (
            <Box sx={{ display: "flex", justifyContent: "flex-start", mb: 2, animation: "pulse 1.5s infinite" }}>
              <Card sx={{ bgcolor: "white", borderRadius: 3 }}>
                <CardContent sx={{ display: "flex", alignItems: "center", p: 2 }}>
                  <CircularProgress size={20} sx={{ mr: 2 }} />
                  <Typography variant="body2" color="text.secondary">
                    AI is thinking...
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          )}
          
          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Paper 
          elevation={3} 
          sx={{ 
            p: 2, 
            borderRadius: 0,
            borderTop: 1,
            borderColor: "divider",
            bgcolor: "white"
          }}
        >
          <Box sx={{ display: "flex", gap: 1, alignItems: "flex-end" }}>
            <TextField
              fullWidth
              multiline
              maxRows={3}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about the PDF... (Press Enter to send)"
              disabled={loading}
              variant="outlined"
              size="medium"
              sx={{
                "& .MuiOutlinedInput-root": {
                  borderRadius: 2
                }
              }}
            />
            <IconButton
              color="primary"
              onClick={handleAskQuestion}
              disabled={!question.trim() || loading}
              sx={{ 
                bgcolor: "primary.main",
                color: "white",
                height: "56px",
                width: "56px",
                "&:hover": { bgcolor: "primary.dark" },
                "&.Mui-disabled": { bgcolor: "grey.400" }
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
          
          <Box sx={{ display: "flex", justifyContent: "space-between", mt: 1 }}>
            <Typography variant="caption" color="text.secondary">
              💡 Try: "What is this about?", "Summarize", "Key points"
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Estonya Startup Visa Project
            </Typography>
          </Box>
        </Paper>
      </Box>
      
      <style>
        {`
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}
      </style>
    </Container>
  );
};

export default ChatInterface;

