# DiaNav Developer Mode

This document describes the developer mode feature that allows users to switch between sample data and real diagnostic data modes.

## 🎯 Overview

Developer Mode provides two distinct operating modes for DiaNav:

1. **Sample Mode** (Default): Uses dummy DTC data for testing and demonstration
2. **Real Mode**: Uses actual diagnostic data with proper authentication

## 🔧 Implementation

### Environment Configuration

Create a `.env` file in the project root:

```bash
# DiaNav Environment Configuration
DIANAV_MODE=sample  # Options: sample, real
DIANAV_AUTH_ENABLED=false  # Enable authentication for real mode
DIANAV_DATA_PATH=./data/real  # Path to real diagnostic data
DIANAV_SAMPLE_PATH=./data/sample  # Path to sample data
```

### Backend Configuration

Add environment variable handling to `dianav_backend.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
DIANAV_MODE = os.getenv('DIANAV_MODE', 'sample')
DIANAV_AUTH_ENABLED = os.getenv('DIANAV_AUTH_ENABLED', 'false').lower() == 'true'
DIANAV_DATA_PATH = os.getenv('DIANAV_DATA_PATH', './data/sample')
```

### Frontend Configuration

Add mode switching to the React app:

```typescript
// Environment configuration
const DIANAV_MODE = process.env.REACT_APP_DIANAV_MODE || 'sample';
const DIANAV_AUTH_ENABLED = process.env.REACT_APP_AUTH_ENABLED === 'true';

// Mode indicator component
const ModeIndicator = () => {
  return (
    <div className="dianav-mode-indicator">
      <span className={`mode-badge ${DIANAV_MODE}`}>
        {DIANAV_MODE === 'sample' ? '🧪 Sample Mode' : '🔐 Real Mode'}
      </span>
    </div>
  );
};
```

## 🔐 Authentication System

### Real Mode Authentication

When `DIANAV_MODE=real`, implement authentication:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if DIANAV_MODE == 'sample':
        return {"username": "sample_user", "role": "developer"}
    
    # Real authentication logic
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": "technician"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Protected Endpoints

```python
@app.post("/query")
async def query_dianav(
    request: QueryRequest,
    current_user: dict = Depends(get_current_user)
):
    if DIANAV_MODE == 'real':
        # Log access for audit trail
        log_access(current_user["username"], request.query)
    
    # Rest of the query logic...
```

## 📊 Data Management

### Sample Data Structure

```
data/sample/
├── dtc_codes/
│   ├── sample_dtc_data.txt
│   └── sample_dtc_codes.json
├── images/
│   ├── sample_diagrams/
│   └── sample_schematics/
└── config/
    └── sample_config.json
```

### Real Data Structure

```
data/real/
├── dtc_codes/
│   ├── real_dtc_data.txt
│   └── real_dtc_codes.json
├── images/
│   ├── confidential_diagrams/
│   └── proprietary_schematics/
├── config/
│   └── real_config.json
└── audit/
    └── access_logs.json
```

## 🎨 UI Enhancements

### Mode Switching Interface

```typescript
const ModeSwitcher = () => {
  const [currentMode, setCurrentMode] = useState(DIANAV_MODE);
  
  const handleModeSwitch = async (newMode: string) => {
    if (newMode === 'real' && !isAuthenticated()) {
      // Redirect to login
      window.location.href = '/login';
      return;
    }
    
    // Update mode
    setCurrentMode(newMode);
    localStorage.setItem('dianav_mode', newMode);
    
    // Reload data
    await reloadData(newMode);
  };
  
  return (
    <div className="dianav-mode-switcher">
      <button 
        className={`mode-btn ${currentMode === 'sample' ? 'active' : ''}`}
        onClick={() => handleModeSwitch('sample')}
      >
        🧪 Sample Mode
      </button>
      <button 
        className={`mode-btn ${currentMode === 'real' ? 'active' : ''}`}
        onClick={() => handleModeSwitch('real')}
      >
        🔐 Real Mode
      </button>
    </div>
  );
};
```

### Visual Indicators

```css
/* Mode indicator styles */
.dianav-mode-indicator {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.mode-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.mode-badge.sample {
  background: #ffd700;
  color: #000;
}

.mode-badge.real {
  background: #dc3545;
  color: #fff;
}

/* Mode switcher styles */
.dianav-mode-switcher {
  display: flex;
  gap: 10px;
  margin: 20px 0;
}

.mode-btn {
  padding: 10px 20px;
  border: 2px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-btn.active {
  border-color: #007bff;
  background: #007bff;
  color: #fff;
}
```

## 🔒 Security Considerations

### Real Mode Security

1. **Authentication Required**: All real mode access requires valid credentials
2. **Audit Logging**: All data access is logged for compliance
3. **Data Encryption**: Real diagnostic data is encrypted at rest
4. **Access Control**: Role-based access control for different user types
5. **Session Management**: Secure session handling with timeouts

### Sample Mode Security

1. **No Authentication**: Sample mode is open for testing
2. **No Real Data**: Only dummy/sample data is used
3. **No Logging**: No sensitive data logging in sample mode
4. **Clear Indicators**: Visual indicators show sample mode status

## 🚀 Deployment

### Development Setup

```bash
# Sample mode (default)
cp .env.sample .env

# Real mode setup
cp .env.real .env
# Edit .env with real credentials and data paths
```

### Production Setup

```bash
# Set environment variables
export DIANAV_MODE=real
export DIANAV_AUTH_ENABLED=true
export DIANAV_DATA_PATH=/secure/diagnostic/data
export DIANAV_SECRET_KEY=your-secret-key

# Start with real mode
python dianav_backend.py
```

## 📋 Usage Guidelines

### For Developers

1. **Always use Sample Mode** for development and testing
2. **Never commit real data** to version control
3. **Test authentication** in sample mode with mock credentials
4. **Use environment variables** for configuration

### For End Users

1. **Sample Mode**: For learning and demonstration
2. **Real Mode**: For actual diagnostic work (requires authentication)
3. **Clear Mode Indicators**: Always visible to prevent confusion
4. **Secure Data Handling**: Real mode follows strict security protocols

## 🔄 Migration Guide

### From Sample to Real Mode

1. **Set up authentication** system
2. **Configure real data paths**
3. **Implement audit logging**
4. **Test security measures**
5. **Deploy with proper credentials**

### From Real to Sample Mode

1. **Switch environment variables**
2. **Clear authentication cache**
3. **Reload sample data**
4. **Verify no real data exposure**
5. **Test all functionality**

This developer mode feature ensures DiaNav can be used safely for both development and production while maintaining the highest security standards for confidential automotive data. 