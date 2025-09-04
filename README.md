# BIGPIAI

AI-powered document processing platform with three integrated phases for comprehensive document workflow automation.

## Features

- **Phase 1**: Writing Plan Creation - Generate structured writing plans from documents
- **Phase 2**: Template Generation - Create customizable templates with AI-powered content extraction
- **Phase 3**: CV Processing - Automated CV template processing with Jinja2 placeholder mapping

## Requirements

- Python 3.8+
- Flask web framework
- AI API keys (OpenAI for Phase 1&2, Gemini for Phase 3)

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd BIGPIAI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Configure your `.env` file:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# Production Settings
PRODUCTION=false
USE_WAITRESS=false

# AI Configuration
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# File Upload Settings
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bigpiai.log
```

5. Run the development server:
```bash
# Using the startup script (recommended)
./start.sh dev

# Or directly
python run_local.py
```

The application will be available at `http://localhost:5000`

### Production Deployment

1. Set production environment variables:
```env
PRODUCTION=true
USE_WAITRESS=true
FLASK_ENV=production
FLASK_DEBUG=0
```

2. Install production dependencies:
```bash
pip install waitress gunicorn
```

3. Run with production server:
```bash
# Using the startup script (recommended)
./start.sh prod

# Or using the production script directly
python run_production.py

# Or manually with Waitress
waitress-serve --host=0.0.0.0 --port=5000 run:app

# Or manually with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

## Project Structure

```
BIGPIAI/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── cv_processor/            # CV processing modules
│   ├── routes/                  # Route handlers
│   │   ├── modules/             # Phase 1&2 processing logic
│   │   ├── phase3/              # Phase 3 CV processing
│   │   ├── home.py              # Main page route
│   │   ├── login.py             # Authentication
│   │   ├── upload_phase1.py     # Phase 1 endpoints
│   │   └── upload_phase2.py     # Phase 2 endpoints
│   ├── static/                  # Static assets
│   └── templates/               # HTML templates
├── uploads/                     # File upload directory
├── outputs/                     # Generated file outputs
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── run_local.py                 # Development server
├── run_production.py            # Production server
├── run.py                       # WSGI entry point
├── start.sh                     # Startup script
├── test_ai.py                   # AI integration tests
└── test_env.py                  # Environment validation
```

## API Endpoints

### Phase 1 - Writing Plans
- `POST /upload-phase1` - Process documents for writing plan generation

### Phase 2 - Template Generation  
- `POST /upload-phase2` - Generate templates from document analysis

### Phase 3 - CV Processing
- `POST /phase3/process` - Start CV batch processing
- `GET /phase3/status/<session_id>` - Check processing status
- `GET /phase3/download/<file_id>` - Download individual processed CV
- `GET /phase3/download-all/<session_id>` - Download all processed CVs as ZIP

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key | Yes | - |
| `JWT_SECRET_KEY` | JWT token secret | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key for Phase 1&2 | Yes | - |
| `GEMINI_API_KEY` | Google Gemini API key for Phase 3 | Yes | - |
| `FLASK_ENV` | Flask environment | No | `development` |
| `PRODUCTION` | Production mode flag | No | `false` |
| `HOST` | Server host | No | `0.0.0.0` |
| `PORT` | Server port | No | `5000` |
| `MAX_CONTENT_LENGTH` | Max upload size in bytes | No | `16777216` |

## Testing

Test environment configuration:
```bash
# Using the startup script
./start.sh test

# Or directly
python test_env.py
```

Test AI integration:
```bash
python test_ai.py
```

## File Formats Supported

- **Input**: PDF, DOCX, TXT
- **Output**: DOCX, PDF, XLSX (depending on phase)
- **Templates**: DOCX with Jinja2 placeholders

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required API keys are set in `.env`
2. **File Upload Errors**: Check `MAX_CONTENT_LENGTH` setting
3. **Processing Failures**: Verify AI API quotas and connectivity
4. **Windows COM Errors**: Some features require Windows environment for full functionality

### Logs

Check application logs in the `logs/` directory for detailed error information.

## License

This project is proprietary software. All rights reserved.