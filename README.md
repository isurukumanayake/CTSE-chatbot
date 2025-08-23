# 🎓 CTSE Learning Assistant

A smart chatbot for Current Trends in Software Engineering course materials built with Streamlit and Google Gemini AI.

## ✨ Features

- 📄 **Multi-format Support**: PDF, PowerPoint, Word, and text files
- 🤖 **AI-Powered**: Google Gemini 1.5 Flash for intelligent responses
- 🔍 **Vector Search**: Fast similarity search through course materials
- 💬 **Chat Interface**: Interactive conversation with source citations
- 📊 **Analytics**: Performance metrics and usage statistics
- 🔒 **Secure**: API keys stored safely, no data persistence

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/isurukumanayake/CTSE-chatbot
cd CTSE-chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Key

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create `.env` file from template:
   ```bash
   cp .env.example .env
   ```
3. Add your API key to `.env`:
   ```
   GOOGLE_API_KEY=your_actual_api_key_here
   ```

### 4. Run Application

```bash
streamlit run app.py
```

## 📁 Project Structure

```
ctse-chatbot/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── src/                  # Source code
│   ├── core/            # Core business logic
│   ├── ui/              # UI components
│   └── utils/           # Utility functions
├── data/                # Data storage
│   ├── documents/       # Uploaded documents
│   └── vectorstore/     # Vector database
└── logs/                # Application logs
```

## 🚀 Deployment

### Streamlit Cloud (Free)

1. Push code to GitHub
2. Connect repository to [Streamlit Cloud](https://share.streamlit.io/)
3. Add `GOOGLE_API_KEY` to secrets
4. Deploy automatically

## 📖 Usage

1. **Upload Documents**: Use the sidebar to upload course materials
2. **Wait for Processing**: Documents are automatically processed and indexed
3. **Ask Questions**: Type questions about your course content
4. **Review Sources**: Check citations and source materials
5. **Manage Files**: Add, remove, or update documents as needed

## ⚙️ Configuration

Key settings in `config.py`:

- **File size limit**: 50MB per file
- **Chunk size**: 1000 characters with 200 overlap
- **Retrieval count**: 5 most relevant documents
- **Model**: Gemini 1.5 Flash

## 🛠 Development

### Adding New File Types

1. Update `ALLOWED_EXTENSIONS` in `config.py`
2. Add loader in `document_processor.py`
3. Test with sample files

### Customizing UI

- Modify components in `src/ui/`
- Update styling with Streamlit themes
- Add new features in modular components

### Performance Optimization

- Increase `CHUNK_SIZE` for longer documents
- Adjust `RETRIEVAL_K` for more context
- Cache embeddings for faster startup

## 🔧 Troubleshooting

### Common Issues

**"No module named 'sentence_transformers'"**

```bash
pip install sentence-transformers
```

**"API key not found"**

- Check `.env` file exists and contains `GOOGLE_API_KEY`
- For Streamlit Cloud, add key to secrets

**"Out of memory"**

- Reduce `CHUNK_SIZE` in config
- Use smaller embedding model
- Process fewer documents at once

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for detailed logging.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the web framework
- [LangChain](https://langchain.com/) for document processing
- [Google](https://ai.google.dev/) for Gemini AI
- [Hugging Face](https://huggingface.co/) for embeddings

---

Built with ❤️ for CTSE students
