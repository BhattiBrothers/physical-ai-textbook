from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging

from services.translation_service import translation_service
from routers.auth import get_current_user
from models import User

router = APIRouter(prefix="/translation", tags=["translation"])
logger = logging.getLogger(__name__)

class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "ur"
    use_cache: bool = True

class TranslateBatchRequest(BaseModel):
    texts: List[str]
    target_lang: str = "ur"

@router.post("/translate")
async def translate_text(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Translate text to target language.

    Parameters:
    - text: Text to translate
    - target_lang: Target language code (default: 'ur' for Urdu)
    - use_cache: Whether to use cached translations (default: True)

    Returns:
    - Translation result with original text, translated text, and metadata
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        result = translation_service.translate_text(
            text=request.text,
            target_lang=request.target_lang,
            use_cache=request.use_cache
        )

        # Log translation request for user analytics
        logger.info(f"Translation requested by user {current_user.id}: {request.target_lang}, length: {len(request.text)}")

        return result
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/translate-batch")
async def translate_batch(
    request: TranslateBatchRequest,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Translate multiple texts in batch.
    """
    try:
        if not request.texts:
            raise HTTPException(status_code=400, detail="Texts list cannot be empty")

        results = translation_service.translate_batch(request.texts, request.target_lang)

        # Log batch translation for user analytics
        logger.info(f"Batch translation requested by user {current_user.id}: {request.target_lang}, items: {len(request.texts)}")

        return results
    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch translation failed: {str(e)}")

@router.get("/languages")
async def get_supported_languages(
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Get supported languages for translation.

    Returns:
    - Dictionary of language codes and their display names
    """
    try:
        languages = translation_service.get_supported_languages()
        return languages
    except Exception as e:
        logger.error(f"Failed to get supported languages: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get supported languages: {str(e)}")

@router.post("/clear-cache")
async def clear_translation_cache(
    older_than_days: int = None,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Clear translation cache.

    Parameters:
    - older_than_days: Clear cache entries older than this many days (optional)

    Returns:
    - Success message
    """
    try:
        translation_service.clear_cache(older_than_days)
        message = "Translation cache cleared successfully"
        if older_than_days:
            message += f" (entries older than {older_than_days} days)"

        logger.info(f"Cache cleared by user {current_user.id}: {message}")

        return {"message": message}
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@router.get("/technical-terms")
async def get_technical_terms() -> Dict[str, str]:
    """
    Get the technical terminology dictionary (English to Urdu).

    Returns:
    - Dictionary of English technical terms and their Urdu translations
    """
    try:
        # Access the technical terms directly from the service
        return translation_service.technical_terms
    except Exception as e:
        logger.error(f"Failed to get technical terms: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get technical terms: {str(e)}")