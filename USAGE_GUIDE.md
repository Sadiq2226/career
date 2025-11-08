# Career Outcomes Intelligence Platform - Usage Guide

## 🎯 Overview

This is an AI-powered career outcomes analysis platform for Indian educational institutions. The system provides real-time insights into employment rates, salary trends, and institutional comparisons without using external LLM APIs.

## 🚀 Quick Start

### 1. Start the Backend
```bash
# Navigate to the project directory
cd "Career Outcome"

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend
```bash
# In a new terminal, start the Streamlit UI
streamlit run ui/app.py
```

### 3. Test the Application
```bash
# Run the test script to verify everything works
python test_app.py
```

## 🏗️ Architecture

### Technology Stack
- **Backend:** FastAPI (Python web framework)
- **Frontend:** Streamlit (Python web app framework)
- **Data Processing:** Pandas, NumPy
- **Search:** BM25 algorithm (offline retrieval)
- **No LLM:** Uses rule-based analysis and statistical methods

### How the Agent Works

The system uses **statistical analysis** and **rule-based processing** instead of LLMs:

1. **Data Loading:** Loads employment, salary, and support services data from CSV/JSON files
2. **Statistical Analysis:** Uses pandas for data aggregation, trend analysis, and calculations
3. **BM25 Search:** Implements offline document retrieval for question answering
4. **ROI Calculations:** Performs financial analysis using mathematical formulas
5. **Institution Comparison:** Uses statistical metrics for comparative analysis

## 📊 Features

### 1. Career Outcomes Dashboard
- **Input:** Degree program (text field) and graduation year (number input)
- **Output:** Employment rates, salary data, top institutions, trend analysis
- **No Dropdowns:** All inputs are now text/number fields for flexibility

### 2. AI-Powered Insights
- **Input:** Natural language questions (text area)
- **Sample Questions:** Clickable buttons with pre-defined questions
- **Output:** Statistical analysis and data-driven insights
- **Search:** Uses BM25 algorithm for document retrieval

### 3. Support Services & ROI Analysis
- **Support Services:** View comprehensive institutional support offerings
- **ROI Calculator:** Calculate return on investment for education choices
- **Input Fields:** Institution name, degree program, tuition, program length

### 4. Institution Comparison
- **Input:** Two institution names and graduation year
- **Output:** Side-by-side comparison of employment rates, salaries, and metrics
- **Analysis:** Statistical comparison with winner determination

## 🎨 UI Improvements

### Enhanced Styling
- **Gradient Headers:** Modern gradient backgrounds
- **Card Layouts:** Clean, organized information display
- **Interactive Elements:** Hover effects and smooth transitions
- **Form Validation:** Better input validation and help text
- **Responsive Design:** Works on different screen sizes

### User Experience
- **No Dropdowns:** All inputs are now text/number fields
- **Help Text:** Contextual help for all input fields
- **Sample Questions:** Clickable buttons for common queries
- **Form Organization:** Logical grouping of related inputs
- **Visual Feedback:** Loading spinners and status indicators

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom API base URL
export API_BASE="http://localhost:8000"
```

### Data Sources
The system uses these data files:
- `backend/data/employment_real.csv` - Employment rate data
- `backend/data/salary_real.csv` - Salary information
- `backend/data/support_services_real.csv` - Support services data
- `backend/data/reports/` - Text reports for analysis

## 📈 Data Processing

### Statistical Methods
- **Employment Analysis:** Mean, median, standard deviation calculations
- **Trend Analysis:** Year-over-year comparison and trend detection
- **ROI Calculations:** Financial projections with growth rates
- **Institution Scoring:** Weighted scoring for support services

### BM25 Search
- **Document Retrieval:** Offline search through text reports
- **Relevance Scoring:** BM25 algorithm for question matching
- **Context Extraction:** Statistical summarization of relevant content

## 🚨 Troubleshooting

### Common Issues

1. **Backend Not Starting**
   ```bash
   # Check if port 8000 is available
   netstat -an | grep 8000
   
   # Try different port
   uvicorn backend.main:app --reload --port 8001
   ```

2. **Frontend Connection Issues**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/
   
   # Update API_BASE in ui/app.py if needed
   ```

3. **Data Loading Errors**
   ```bash
   # Check if data files exist
   ls -la backend/data/
   
   # Verify file permissions
   chmod 644 backend/data/*.csv
   ```

### Performance Tips
- **Data Caching:** The system caches data for 1 hour
- **Batch Processing:** Multiple requests are processed efficiently
- **Memory Usage:** Data is loaded once and reused

## 🔍 API Endpoints

### Available Endpoints
- `GET /` - Health check and service info
- `POST /analyze` - Employment analysis
- `GET /insights` - Question answering
- `POST /compare` - Institution comparison
- `GET /support-services` - Support services data
- `POST /roi` - ROI calculations

### Example API Usage
```python
import requests

# Analyze employment data
response = requests.post("http://localhost:8000/analyze", 
                        json={"degree": "Computer Science", "year": 2025})

# Get insights
response = requests.get("http://localhost:8000/insights", 
                       params={"q": "What are the top institutions?"})
```

## 📝 Development

### Adding New Features
1. **Backend:** Add new endpoints in `backend/main.py`
2. **Service:** Implement logic in `backend/agent/service.py`
3. **Frontend:** Add UI components in `ui/app.py`
4. **Data:** Add new data sources in `backend/data/`

### Testing
```bash
# Run the test suite
python test_app.py

# Test specific endpoints
curl -X POST http://localhost:8000/analyze \
     -H "Content-Type: application/json" \
     -d '{"degree": "Engineering", "year": 2025}'
```

## 🎯 Key Benefits

1. **No External Dependencies:** No LLM API costs or internet requirements
2. **Fast Performance:** Local processing with data caching
3. **Flexible Input:** Text fields instead of restrictive dropdowns
4. **Statistical Accuracy:** Data-driven insights using proven methods
5. **User-Friendly:** Modern UI with helpful guidance
6. **Scalable:** Easy to add new data sources and features

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify all dependencies are installed
3. Ensure data files are present and accessible
4. Check backend and frontend logs for error messages

The system is designed to be self-contained and work offline, making it reliable and cost-effective for career outcomes analysis.
