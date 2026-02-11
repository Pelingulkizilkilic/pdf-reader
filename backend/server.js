const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

app.get('/api/health', (req, res) => {
    console.log('Health check');
    res.json({ status: 'online', port: PORT });
});

app.post('/api/upload', (req, res) => {
    console.log('Upload request');
    res.json({ id: 'pdf_001', filename: 'uploaded.pdf', success: true });
});

app.post('/api/chat', (req, res) => {
    console.log('Chat request:', req.body);
    res.json({ 
        answer: 'Backend çalışıyor: ' + req.body.question,
        question: req.body.question,
        pdfId: req.body.pdfId,
        success: true 
    });
});

app.listen(PORT, () => {
    console.log(`✅ Backend çalışıyor: http://localhost:${PORT}`);
});
