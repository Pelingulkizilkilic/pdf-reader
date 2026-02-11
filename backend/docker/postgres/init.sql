-- docker/postgres/init.sql
-- ÖNCE VARSA TABLOLARI SİL (development için)
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS pdf_documents CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS api_keys CASCADE;

-- Kullanıcılar tablosu
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- PDF Dokümanları tablosu
CREATE TABLE pdf_documents (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_path TEXT NOT NULL,
    file_size INTEGER,
    page_count INTEGER,
    chunk_count INTEGER,
    vector_store_path TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    processing_error TEXT,
    document_metadata JSONB DEFAULT '{}'::jsonb  -- metadata → document_metadata
);

-- Index'ler
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_pdf_documents_user_id ON pdf_documents(user_id);

-- Test kullanıcısı (şifre: test123)
INSERT INTO users (username, email, hashed_password) 
SELECT 'testuser', 'test@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'testuser'
);

-- Yeni test kullanıcısı
INSERT INTO users (username, email, hashed_password) 
SELECT 'pln', 'plnkzklc@gmail.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE username = 'pln'
);