# LLM Configuration Guide

## 🔧 Setting Up LLM Integration

### 1. Install Required Dependencies
```bash
pip install openai langchain faiss-cpu
```

### 2. Set Up OpenAI API Key
Create a `.env` file in the project root:
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Other LLM providers
GOOGLE_API_KEY=your_google_api_key_here
HUGGINGFACEHUB_API_TOKEN=your_hf_token_here

# Data Configuration
DATA_DIR=backend/data
HOST=0.0.0.0
PORT=8000
```

### 3. Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

### 4. Verify Installation
```bash
# Test the LLM integration
python -c "
from backend.agent.config import settings
print(f'Online mode: {settings.online_mode}')
print(f'OpenAI key configured: {bool(settings.openai_api_key)}')
"
```

## 🚀 Features Enabled with LLM

### Enhanced Capabilities:
- **Intelligent Document Retrieval**: Uses OpenAI embeddings for semantic search
- **AI-Powered Summarization**: GPT-3.5-turbo generates comprehensive insights
- **Contextual Analysis**: LLM understands context and provides relevant recommendations
- **Natural Language Processing**: Better understanding of user questions
- **Intelligent Synthesis**: Creates comprehensive reports from data points

### Fallback Behavior:
- If LLM is unavailable, the system automatically falls back to:
  - BM25 algorithm for document search
  - Statistical analysis for insights
  - Rule-based processing for recommendations

## 💰 Cost Considerations

### OpenAI Pricing (as of 2024):
- **GPT-3.5-turbo**: ~$0.002 per 1K tokens
- **Embeddings**: ~$0.0001 per 1K tokens
- **Estimated cost**: $0.01-0.05 per query depending on complexity

### Cost Optimization:
- System caches data for 1 hour to reduce API calls
- Uses efficient prompt engineering to minimize token usage
- Implements fallback to reduce unnecessary API calls

## 🔒 Security & Privacy

### Data Handling:
- Only document content is sent to OpenAI
- No personal or sensitive data is transmitted
- API keys are stored securely in environment variables
- All communications use HTTPS

### Best Practices:
- Never commit API keys to version control
- Use environment variables for configuration
- Monitor API usage and costs
- Implement rate limiting if needed

## 🛠️ Troubleshooting

### Common Issues:

1. **"LangChain not available"**
   ```bash
   pip install langchain openai faiss-cpu
   ```

2. **"OpenAI API key not found"**
   - Check `.env` file exists
   - Verify API key is correctly set
   - Restart the application

3. **"LLM query failed"**
   - Check internet connection
   - Verify API key is valid
   - Check OpenAI service status

4. **High API costs**
   - Monitor usage in OpenAI dashboard
   - Implement caching strategies
   - Use fallback mode when appropriate

### Testing LLM Integration:
```bash
# Test with a simple question
curl -X GET "http://localhost:8000/insights?q=What%20are%20the%20top%20institutions%20for%20Computer%20Science?"
```

## 📊 Performance Comparison

| Feature | Without LLM | With LLM |
|---------|-------------|----------|
| Document Search | BM25 keyword matching | Semantic similarity search |
| Insights Quality | Basic statistical summary | Comprehensive AI analysis |
| Question Understanding | Limited | Natural language processing |
| Response Relevance | Good | Excellent |
| Processing Speed | Fast | Moderate (API calls) |
| Cost | Free | ~$0.01-0.05 per query |

## 🎯 Recommendations

### For Development:
- Start with LLM enabled for better insights
- Monitor API usage and costs
- Implement proper error handling

### For Production:
- Set up monitoring and alerting
- Implement rate limiting
- Consider caching strategies
- Have fallback mechanisms ready

The LLM integration significantly enhances the quality and relevance of insights while maintaining reliability through fallback mechanisms.
