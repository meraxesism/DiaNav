interface TranslationRequest {
  text: string;
  target_language: string;
  source_language?: string;
}

interface TranslationResponse {
  translated_text: string;
  original_text: string;
  source_language: string;
  target_language: string;
  success: boolean;
  error?: string;
}

class TranslationService {
  private static instance: TranslationService;
  private cache = new Map<string, string>();

  private constructor() {}

  static getInstance(): TranslationService {
    if (!TranslationService.instance) {
      TranslationService.instance = new TranslationService();
    }
    return TranslationService.instance;
  }

  /**
   * Translate text using the backend API with Llama 3
   */
  async translateText(
    text: string, 
    targetLanguage: string, 
    sourceLanguage: string = 'en'
  ): Promise<string> {
    // Check cache first
    const cacheKey = `${text}_${sourceLanguage}_${targetLanguage}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    try {
      const response = await fetch('/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          target_language: targetLanguage,
          source_language: sourceLanguage,
        } as TranslationRequest),
      });

      if (!response.ok) {
        throw new Error(`Translation failed: ${response.statusText}`);
      }

      const data: TranslationResponse = await response.json();
      
      if (data.success) {
        // Cache the result
        this.cache.set(cacheKey, data.translated_text);
        return data.translated_text;
      } else {
        console.warn('Translation failed:', data.error);
        return text; // Return original text on failure
      }
    } catch (error) {
      console.error('Translation service error:', error);
      return text; // Return original text on error
    }
  }

  /**
   * Translate multiple texts in batch
   */
  async translateBatch(
    texts: string[], 
    targetLanguage: string, 
    sourceLanguage: string = 'en'
  ): Promise<string[]> {
    const results = await Promise.all(
      texts.map(text => this.translateText(text, targetLanguage, sourceLanguage))
    );
    return results;
  }

  /**
   * Clear translation cache
   */
  clearCache(): void {
    this.cache.clear();
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): { size: number } {
    return { size: this.cache.size };
  }
}

export default TranslationService; 