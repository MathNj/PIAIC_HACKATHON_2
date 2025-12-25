"""
Voice API routes for Text-to-Speech functionality.

Provides:
- OpenAI TTS integration for English voices
- Google TTS (gTTS) for multilingual support (Urdu, Arabic, French)
"""

import os
import logging
from typing import Literal
from uuid import UUID
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from openai import OpenAI
from gtts import gTTS

from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Voice options from OpenAI TTS
VoiceOption = Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Language codes for gTTS multilingual support
MultilingualLang = Literal["en", "ur", "ar", "fr"]


class TTSRequest(BaseModel):
    """Text-to-Speech request schema."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Text to convert to speech (max 4096 characters)"
    )
    voice: VoiceOption = Field(
        default="alloy",
        description="Voice personality for TTS"
    )
    model: Literal["tts-1", "tts-1-hd"] = Field(
        default="tts-1",
        description="TTS model (tts-1 is faster and cheaper)"
    )
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="Playback speed (0.25 to 4.0)"
    )


def get_openai_client() -> OpenAI:
    """
    Get OpenAI-compatible client (supports OpenAI, Groq with custom base URL).

    Raises:
        ValueError: If OPENAI_API_KEY is not configured
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required for TTS")

    base_url = os.getenv("OPENAI_BASE_URL")

    # Note: If using Groq, it may not support TTS API
    # In that case, use standard OpenAI endpoint for TTS
    if base_url and "groq" in base_url.lower():
        logger.info("Groq base URL detected, using OpenAI endpoint for TTS")
        return OpenAI(api_key=api_key)  # Use default OpenAI endpoint for TTS
    elif base_url:
        logger.info(f"Using custom base URL for TTS: {base_url}")
        return OpenAI(api_key=api_key, base_url=base_url)
    else:
        return OpenAI(api_key=api_key)


@router.post("/speak")
async def text_to_speech(
    request: TTSRequest,
    current_user: UUID = Depends(get_current_user)
) -> StreamingResponse:
    """
    Convert text to speech using OpenAI TTS API.

    **Authentication**: Requires valid JWT token

    **Rate Limiting**: 100 requests/minute per user (not yet implemented)

    **Args**:
        request: TTS request with text, voice, model, and speed
        current_user: User ID from JWT token

    **Returns**:
        StreamingResponse: MP3 audio stream

    **Raises**:
        HTTPException 400: Text too long, invalid voice, invalid speed
        HTTPException 500: OpenAI API error

    **Example**:
        ```bash
        curl -X POST http://localhost:8000/api/voice/speak \\
          -H "Authorization: Bearer <token>" \\
          -H "Content-Type: application/json" \\
          -d '{"text": "Hello world", "voice": "alloy"}'
        ```
    """
    logger.info(
        f"TTS request from user {current_user}",
        extra={
            "user_id": str(current_user),
            "text_length": len(request.text),
            "voice": request.voice,
            "model": request.model
        }
    )

    try:
        # Get OpenAI client
        client = get_openai_client()

        # Call OpenAI TTS API
        response = client.audio.speech.create(
            model=request.model,
            voice=request.voice,
            input=request.text,
            response_format="mp3",
            speed=request.speed
        )

        # Calculate estimated cost
        characters = len(request.text)
        estimated_cost = (characters / 1000) * 0.015  # $0.015 per 1K chars

        logger.info(
            f"TTS successful for user {current_user}",
            extra={
                "user_id": str(current_user),
                "characters": characters,
                "estimated_cost_usd": round(estimated_cost, 4),
                "voice": request.voice
            }
        )

        # Return audio stream
        return StreamingResponse(
            response.iter_bytes(),
            media_type="audio/mpeg",
            headers={
                "X-Characters-Billed": str(characters),
                "X-Estimated-Cost": f"${estimated_cost:.4f}",
                "X-Voice": request.voice,
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )

    except ValueError as e:
        # API key not configured
        logger.error(f"TTS configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "code": "TTS_NOT_CONFIGURED"}
        )

    except Exception as e:
        # OpenAI API error or other unexpected error
        logger.error(
            f"TTS error for user {current_user}: {str(e)}",
            extra={"user_id": str(current_user), "error": str(e)}
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Text-to-speech service temporarily unavailable",
                "code": "TTS_SERVICE_ERROR",
                "message": str(e)
            }
        )


@router.get("/voices")
async def list_voices():
    """
    List available TTS voices.

    **Returns**:
        List of voice options with descriptions
    """
    return {
        "voices": [
            {"id": "alloy", "name": "Alloy", "description": "Neutral, balanced voice"},
            {"id": "echo", "name": "Echo", "description": "Male voice with clarity"},
            {"id": "fable", "name": "Fable", "description": "Warm, storytelling voice"},
            {"id": "onyx", "name": "Onyx", "description": "Deep, authoritative voice"},
            {"id": "nova", "name": "Nova", "description": "Energetic female voice"},
            {"id": "shimmer", "name": "Shimmer", "description": "Soft, friendly voice"}
        ],
        "default": "alloy"
    }


# ============================================================================
# Multilingual TTS with gTTS (Urdu, Arabic, French support)
# ============================================================================


class MultilingualTTSRequest(BaseModel):
    """Multilingual Text-to-Speech request schema using Google TTS."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Text to convert to speech"
    )
    lang: MultilingualLang = Field(
        default="en",
        description="Language code (en=English, ur=Urdu, ar=Arabic, fr=French)"
    )
    slow: bool = Field(
        default=False,
        description="Slow speech rate for better clarity"
    )


@router.post("/multilingual")
async def multilingual_text_to_speech(
    request: MultilingualTTSRequest,
    current_user: UUID = Depends(get_current_user)
) -> StreamingResponse:
    """
    Convert text to speech with multilingual support using Google TTS.

    Supports Urdu, Arabic, French, and English with proper pronunciation.
    Free service with no API key required.

    **Authentication**: Requires valid JWT token

    **Args**:
        request: TTS request with text, language, and speed
        current_user: User ID from JWT token

    **Returns**:
        StreamingResponse: MP3 audio stream

    **Supported Languages**:
        - en: English
        - ur: Urdu (اردو) - Excellent support
        - ar: Arabic (العربية) - Excellent support
        - fr: French (Français)

    **Example**:
        ```bash
        curl -X POST http://localhost:8000/api/voice/multilingual \\
          -H "Authorization: Bearer <token>" \\
          -H "Content-Type: application/json" \\
          -d '{"text": "ٹاسک کا نام اپ ڈیٹ کر دیا گیا ہے", "lang": "ur"}'
        ```
    """
    logger.info(
        f"Multilingual TTS request from user {current_user}",
        extra={
            "user_id": str(current_user),
            "text_length": len(request.text),
            "lang": request.lang,
            "slow": request.slow
        }
    )

    try:
        # Generate speech using gTTS
        tts = gTTS(
            text=request.text,
            lang=request.lang,
            slow=request.slow
        )

        # Save to BytesIO buffer
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        audio_size = len(audio_buffer.getvalue())

        logger.info(
            f"Multilingual TTS successful for user {current_user}",
            extra={
                "user_id": str(current_user),
                "characters": len(request.text),
                "audio_size_bytes": audio_size,
                "lang": request.lang
            }
        )

        # Return audio stream
        return StreamingResponse(
            audio_buffer,
            media_type="audio/mpeg",
            headers={
                "X-Characters": str(len(request.text)),
                "X-Language": request.lang,
                "X-Audio-Size": str(audio_size),
                "Content-Disposition": "inline; filename=speech.mp3",
                "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
            }
        )

    except Exception as e:
        # gTTS error
        logger.error(
            f"Multilingual TTS error for user {current_user}: {str(e)}",
            extra={"user_id": str(current_user), "error": str(e), "lang": request.lang}
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Multilingual text-to-speech service temporarily unavailable",
                "code": "GTTS_SERVICE_ERROR",
                "message": str(e)
            }
        )


@router.get("/multilingual/languages")
async def list_multilingual_languages():
    """
    List available languages for multilingual TTS.

    **Returns**:
        List of supported languages with details
    """
    return {
        "languages": [
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "description": "Standard English pronunciation"
            },
            {
                "code": "ur",
                "name": "Urdu",
                "native_name": "اردو",
                "description": "Excellent Urdu support with proper Nastaliq pronunciation"
            },
            {
                "code": "ar",
                "name": "Arabic",
                "native_name": "العربية",
                "description": "Modern Standard Arabic"
            },
            {
                "code": "fr",
                "name": "French",
                "native_name": "Français",
                "description": "Standard French pronunciation"
            }
        ],
        "default": "en",
        "notes": "Free service powered by Google Text-to-Speech"
    }
