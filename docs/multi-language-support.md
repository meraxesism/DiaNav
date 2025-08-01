# DiaNav Multi-Language Support

This document describes the multi-language support implementation for DiaNav, supporting English, Hindi, and Marathi languages with dynamic translation capabilities using Llama 3.

## 🌍 Overview

DiaNav now supports multiple languages through a comprehensive internationalization (i18n) system:

- **Static Translations**: Pre-defined UI text in JSON files
- **Dynamic Translations**: Real-time translation using Llama 3 AI
- **Language Detection**: Automatic language detection and switching
- **Caching**: Translation caching for performance

## 🚀 Features

### Supported Languages
- **English** (en) - Default language
- **Hindi** (hi) - हिंदी
- **Marathi** (mr) - मराठी

### Key Features
- ✅ Language switcher in header
- ✅ Persistent language preference
- ✅ Dynamic content translation
- ✅ Technical term preservation
- ✅ Translation caching
- ✅ Fallback to English
- ✅ Mobile-responsive design

## 📁 File Structure

```
dianav-frontend/
├── src/
│   ├── i18n.ts                          # i18n configuration
│   ├── locales/
│   │   ├── en.json                      # English translations
│   │   ├── hi.json                      # Hindi translations
│   │   └── mr.json                      # Marathi translations
│   ├── components/
│   │   ├── LanguageSwitcher.tsx         # Language switcher component
│   │   └── LanguageSwitcher.css         # Language switcher styles
│   └── services/
│       └── translationService.ts        # Dynamic translation service
```

## 🔧 Implementation Details

### Frontend (React + TypeScript)

#### 1. i18n Configuration (`src/i18n.ts`)
```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: { translation: enTranslations },
  hi: { translation: hiTranslations },
  mr: { translation: mrTranslations }
};

i18n.use(initReactI18next).init({
  resources,
  lng: localStorage.getItem('language') || 'en',
  fallbackLng: 'en',
  interpolation: { escapeValue: false }
});
```

#### 2. Language Switcher Component
```typescript
const LanguageSwitcher: React.FC = () => {
  const { t, i18n } = useTranslation();
  
  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
    localStorage.setItem('language', languageCode);
    window.dispatchEvent(new CustomEvent('languageChanged'));
  };
  
  return (
    <div className="language-switcher">
      {/* Language selection UI */}
    </div>
  );
};
```

#### 3. Translation Usage
```typescript
const { t } = useTranslation();

// Static translation
<h1>{t('chat.welcome')}</h1>

// With interpolation
<p>{t('diagnostic.pageNumber', { number: pageNum })}</p>
```

### Backend (FastAPI + Python)

#### 1. Translation Endpoint
```python
@app.post("/translate")
def translate_text(request: TranslationRequest):
    translated_text = translate_text_with_llama(
        request.text, 
        request.target_language, 
        request.source_language
    )
    return {
        "translated_text": translated_text,
        "success": True
    }
```

#### 2. Llama 3 Integration
```python
def translate_text_with_llama(text: str, target_language: str, source_language: str = "en") -> str:
    prompt = f"""You are a professional translator. Translate the following text from {source_language} to {target_language}.

Text to translate: "{text}"

Please provide only the translated text without any explanations. If the text contains technical automotive terms, maintain their technical accuracy while translating.

Translation:"""
    
    response = call_ollama_llm(prompt, model="llama3.2:3b")
    return response.strip()
```

## 🎨 UI Components

### Language Switcher
- **Location**: Header (top-right)
- **Features**: 
  - Dropdown with language flags
  - Current language indicator
  - Smooth animations
  - Mobile-responsive

### Styling
```css
.language-switcher {
  position: relative;
  display: inline-block;
}

.language-switcher-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
}
```

## 📝 Translation Files Structure

### English (`en.json`)
```json
{
  "common": {
    "newChat": "New Chat",
    "search": "Search",
    "send": "Send"
  },
  "chat": {
    "welcome": "Welcome to DiaNav",
    "placeholder": "Ask about diagnostic codes..."
  }
}
```

### Hindi (`hi.json`)
```json
{
  "common": {
    "newChat": "नई चैट",
    "search": "खोजें",
    "send": "भेजें"
  },
  "chat": {
    "welcome": "DiaNav में आपका स्वागत है",
    "placeholder": "डायग्नोस्टिक कोड के बारे में पूछें..."
  }
}
```

### Marathi (`mr.json`)
```json
{
  "common": {
    "newChat": "नवीन चॅट",
    "search": "शोधा",
    "send": "पाठवा"
  },
  "chat": {
    "welcome": "DiaNav मध्ये आपले स्वागत आहे",
    "placeholder": "डायग्नोस्टिक कोड बद्दल विचारा..."
  }
}
```

## 🔄 Dynamic Translation Service

### Usage
```typescript
import TranslationService from './services/translationService';

const translationService = TranslationService.getInstance();

// Translate single text
const translatedText = await translationService.translateText(
  "Check engine light is on", 
  "hi", 
  "en"
);

// Translate multiple texts
const translatedTexts = await translationService.translateBatch(
  ["Hello", "World"], 
  "mr", 
  "en"
);
```

### Features
- **Caching**: Automatic caching of translations
- **Error Handling**: Fallback to original text on errors
- **Batch Processing**: Translate multiple texts efficiently
- **Performance**: Optimized for minimal API calls

## 🚀 Getting Started

### 1. Install Dependencies
```bash
cd dianav-frontend
npm install i18next react-i18next
```

### 2. Start the Application
```bash
# Start backend (with Llama 3)
python dianav_backend.py

# Start frontend
cd dianav-frontend
npm start
```

### 3. Test Language Switching
1. Open the application
2. Click the language switcher in the header
3. Select Hindi or Marathi
4. Verify UI text changes
5. Test dynamic translations

## 🔧 Configuration

### Environment Variables
```bash
# Backend
DIANAV_MODE=sample
DIANAV_AUTH_ENABLED=false

# Frontend
REACT_APP_DEFAULT_LANGUAGE=en
REACT_APP_FALLBACK_LANGUAGE=en
```

### Adding New Languages

1. **Create Translation File**
```bash
# Create new locale file
touch dianav-frontend/src/locales/gu.json  # For Gujarati
```

2. **Add Language to i18n.ts**
```typescript
import guTranslations from './locales/gu.json';

const resources = {
  en: { translation: enTranslations },
  hi: { translation: hiTranslations },
  mr: { translation: mrTranslations },
  gu: { translation: guTranslations }  // New language
};
```

3. **Update Language Switcher**
```typescript
const languages: LanguageOption[] = [
  { code: 'en', name: 'English', nativeName: 'English', flag: '🇺🇸' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिंदी', flag: '🇮🇳' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', flag: '🇮🇳' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', flag: '🇮🇳' }  // New language
];
```

4. **Update Backend Language Mapping**
```python
language_names = {
    "hi": "Hindi",
    "mr": "Marathi",
    "gu": "Gujarati",  # New language
    "en": "English"
}
```

## 🧪 Testing

### Manual Testing
1. **Language Switching**: Test all language options
2. **Persistence**: Refresh page, verify language preference
3. **Dynamic Translation**: Test AI-powered translations
4. **Fallback**: Test with backend offline
5. **Mobile**: Test on mobile devices

### Automated Testing
```typescript
// Test language switching
test('should switch language correctly', () => {
  render(<LanguageSwitcher />);
  fireEvent.click(screen.getByText('हिंदी'));
  expect(localStorage.getItem('language')).toBe('hi');
});

// Test translation service
test('should translate text correctly', async () => {
  const service = TranslationService.getInstance();
  const result = await service.translateText('Hello', 'hi', 'en');
  expect(result).toBe('नमस्ते');
});
```

## 🔍 Troubleshooting

### Common Issues

1. **Translations Not Loading**
   - Check if translation files exist
   - Verify i18n configuration
   - Check browser console for errors

2. **Dynamic Translation Failing**
   - Ensure Llama 3 is running
   - Check backend logs
   - Verify API endpoint is accessible

3. **Language Not Persisting**
   - Check localStorage permissions
   - Verify language change event handling
   - Check browser storage settings

### Debug Commands
```bash
# Check translation cache
console.log(TranslationService.getInstance().getCacheStats());

# Clear translation cache
TranslationService.getInstance().clearCache();

# Check current language
console.log(i18n.language);
```

## 📊 Performance Considerations

### Optimization Tips
1. **Caching**: Translation service caches results
2. **Lazy Loading**: Load translation files on demand
3. **Batch Processing**: Use batch translation for multiple texts
4. **CDN**: Serve translation files from CDN
5. **Compression**: Compress translation files

### Monitoring
```typescript
// Monitor translation performance
const startTime = performance.now();
const result = await translationService.translateText(text, targetLang);
const endTime = performance.now();
console.log(`Translation took ${endTime - startTime}ms`);
```

## 🔮 Future Enhancements

### Planned Features
- [ ] **Auto-detection**: Detect user's preferred language
- [ ] **Voice Input**: Voice-to-text in multiple languages
- [ ] **Offline Support**: Offline translation capabilities
- [ ] **More Languages**: Support for additional Indian languages
- [ ] **Context Awareness**: Better technical term translation
- [ ] **User Preferences**: Per-user language preferences

### API Enhancements
- [ ] **Translation Memory**: Learn from user corrections
- [ ] **Quality Scoring**: Rate translation quality
- [ ] **Bulk Operations**: Efficient bulk translation
- [ ] **Webhook Support**: Real-time translation updates

## 🤝 Contributing

### Adding Translations
1. Fork the repository
2. Add translations to locale files
3. Test with the application
4. Submit a pull request

### Translation Guidelines
- Maintain technical accuracy
- Use consistent terminology
- Follow language conventions
- Test with native speakers
- Document any special terms

## 📚 Resources

### Documentation
- [React i18next Documentation](https://react.i18next.com/)
- [i18next Documentation](https://www.i18next.com/)
- [Llama 3 Documentation](https://ollama.ai/library/llama3.2)

### Tools
- [i18next Browser Language Detector](https://github.com/i18next/i18next-browser-languagedetector)
- [i18next HTTP Backend](https://github.com/i18next/i18next-http-backend)
- [Translation Memory Tools](https://www.memoq.com/)

---

This multi-language support system provides a robust foundation for making DiaNav accessible to users in multiple languages while maintaining the technical accuracy required for automotive diagnostics. 