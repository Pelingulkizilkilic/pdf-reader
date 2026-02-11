// PDF AI Assistant API Service
// BU DOSYAYI DEĞİŞTİRME!

const API_URL = "http://localhost:5000";

// 1. Backend bağlantı testi
export async function testBackend() {
  try {
    const response = await fetch(API_URL);
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: "Backend not connected" };
  }
}

// 2. PDF yükleme (DEMO MOD - Backend bağlantısı yoksa)
export async function uploadPDF(file: File) {
  console.log("Uploading PDF:", file.name);
  
  // Önce backend'i test et
  const backendTest = await testBackend();
  
  if (!backendTest.success) {
    // Backend yoksa DEMO mod
    return {
      id: "demo-" + Date.now(),
      filename: file.name,
      message: "Demo mode - Backend not connected",
      pages: 15,
      size: file.size,
      isDemo: true
    };
  }
  
  // Backend varsa gerçek yükleme yap
  try {
    const formData = new FormData();
    formData.append("file", file);
    
    const response = await fetch(API_URL + "/api/upload", {
      method: "POST",
      body: formData
    });
    
    if (!response.ok) throw new Error("Upload failed");
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    // Upload başarısız olursa yine demo mod
    return {
      id: "fallback-" + Date.now(),
      filename: file.name,
      message: "Upload failed, using demo mode",
      isDemo: true
    };
  }
}

// 3. Soru sorma (DEMO MOD - Backend bağlantısı yoksa)
export async function askQuestion(pdfId: string, question: string) {
  console.log("Asking question:", question);
  
  // Önce backend'i test et
  const backendTest = await testBackend();
  
  if (!backendTest.success) {
    // Backend yoksa DEMO cevap
    return {
      answer: `**Demo AI Response**\n\n` +
              `Question: "${question}"\n\n` +
              `This is a demo response. The backend server is not connected.\n\n` +
              `Please start the backend server: \`python backend.py\` in backend folder`,
      confidence: 0.7,
      isDemo: true
    };
  }
  
  // Backend varsa gerçek AI'ya sor
  try {
    const response = await fetch(API_URL + `/api/chat/${pdfId}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question })
    });
    
    if (!response.ok) throw new Error("AI failed");
    
    const data = await response.json();
    return data;
    
  } catch (error) {
    // AI başarısız olursa demo cevap
    return {
      answer: `**Connection Issue**\n\n` +
              `Could not connect to AI backend.\n\n` +
              `Backend URL: ${API_URL}\n` +
              `PDF ID: ${pdfId}\n\n` +
              `Please check:\n` +
              `1. Backend server is running\n` +
              `2. Port 8000 is accessible\n` +
              `3. API endpoints are correct`,
      isDemo: true
    };
  }
}

// 4. PDF listesi (basit)
export async function getPDFs() {
  return [
    { id: "1", filename: "Business-Plan.pdf", date: "2024-01-30" },
    { id: "2", filename: "Research-Paper.pdf", date: "2024-01-29" }
  ];
}

