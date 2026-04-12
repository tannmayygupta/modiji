import os
import json
import tempfile
import subprocess
from groq import Groq

# Lazy client — reads key at call time, NOT import time
# This ensures pydantic-settings has already loaded .env before we use it.
_groq_client: Groq | None = None

def get_client() -> Groq:
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    # Import here to avoid circular imports
    from app.config import get_settings
    api_key = get_settings().GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in your .env file. Please add it and restart the server.")
    _groq_client = Groq(api_key=api_key)
    return _groq_client

ANALYSIS_PROMPT = """You are an internship coordinator evaluating a candidate's self-introduction video for India's PM Internship Scheme (Government of India initiative).

The candidate was asked to speak for 2-3 minutes covering:
1. Their name and background
2. Their top skills and what they've done with them
3. What kind of work excites them
4. What they want from an internship

Transcript of their video:
"{transcript}"

Video duration: {duration} seconds
Word count: {word_count}

Analyze this transcript carefully and return ONLY a valid JSON object with no extra text, no markdown, no explanation — just the raw JSON:

{{
  "communication_score": <integer 0-100, based on clarity, coherence, confidence expressed in words>,
  "confidence_score": <integer 0-100, based on assertive language, lack of excessive filler words>,
  "clarity_score": <integer 0-100, based on how clearly ideas are expressed>,
  "overall_score": <integer 0-100, weighted average>,
  "skills_mentioned": [<list of specific skills the candidate mentioned, e.g. "Python", "Excel", "Communication">],
  "sectors_mentioned": [<list of sectors/industries they showed interest in>],
  "languages_used": [<list of languages detected, e.g. "English", "Hindi">],
  "is_bilingual": <true if they used Hindi+English mix, false otherwise>,
  "filler_word_count": <integer count of "um", "uh", "like", "you know", "basically", "actually" etc>,
  "word_count": {word_count},
  "speech_pace": <"slow" if word_count/duration < 1.5, "fast" if > 2.5, otherwise "moderate">,
  "top_strength": "<1 short sentence about their strongest quality based on what they said>",
  "summary": "<2 sentences summarizing what the candidate said about themselves>",
  "feedback_for_candidate": "<1 constructive, encouraging sentence suggesting one specific improvement>",
  "is_valid_intro": <true if the transcript is a coherent self-introduction, false if it's gibberish/empty/wrong content>
}}"""


def _get_ffmpeg_path() -> str:
    """Get ffmpeg binary path — prefer imageio-ffmpeg's bundled version, fallback to system."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"  # fallback to system PATH


def extract_audio_from_video(video_bytes: bytes, original_filename: str) -> bytes:
    """Extract audio from video file using ffmpeg. Returns mp3 bytes.
    Falls back to raw bytes if ffmpeg is unavailable or fails."""
    ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else 'mp4'
    ffmpeg_bin = _get_ffmpeg_path()

    with tempfile.NamedTemporaryFile(suffix=f'.{ext}', delete=False) as video_tmp:
        video_tmp.write(video_bytes)
        video_path = video_tmp.name

    audio_path = video_path.replace(f'.{ext}', '.mp3')

    try:
        subprocess.run(
            [ffmpeg_bin, '-i', video_path, '-vn', '-acodec', 'libmp3lame', '-ab', '64k', '-ar', '16000', '-ac', '1', audio_path, '-y'],
            capture_output=True, timeout=120, check=True
        )
        with open(audio_path, 'rb') as f:
            compressed = f.read()
        print(f"[VideoAnalysis] Extracted audio: {len(video_bytes)} bytes video → {len(compressed)} bytes mp3")
        return compressed
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
        print(f"[VideoAnalysis] ffmpeg extraction failed: {error_output}")
        if len(video_bytes) > 24 * 1024 * 1024:
            raise ValueError(f"Video is too large ({len(video_bytes) // 1024 // 1024}MB). Max 24MB without ffmpeg installed.")
        return video_bytes
    except Exception as e:
        print(f"[VideoAnalysis] ffmpeg not found or failed. Falling back to native video bytes. Error: {e}")
        if len(video_bytes) > 24 * 1024 * 1024:
            raise ValueError(f"Video is too large ({len(video_bytes) // 1024 // 1024}MB). Groq API limits to 25MB without FFmpeg compression. Please upload a shorter/compressed video.")
        return video_bytes
    finally:
        for p in [video_path, audio_path]:
            if os.path.exists(p):
                try:
                    os.unlink(p)
                except Exception:
                    pass


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.mp3") -> dict:
    """
    Transcribe audio using Groq's Whisper API (FREE).
    Supports mp3, mp4, webm, wav, and other formats Groq accepts.
    """
    client = get_client()

    # Use the correct extension from the filename so Groq can decode it properly
    ext = os.path.splitext(filename)[1].lower() or '.mp3'
    
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    
    try:
        with open(tmp_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(filename, audio_file.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                language=None, # auto-detect
                temperature=0.0
            )
        
        transcript_text = transcription.text
        duration = getattr(transcription, 'duration', 0) or 0
        
        return {
            "transcript": transcript_text,
            "duration_seconds": round(duration),
            "word_count": len(transcript_text.split()),
            "detected_language": getattr(transcription, 'language', 'unknown')
        }
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def analyze_transcript(transcript: str, duration_seconds: int, word_count: int) -> dict:
    """
    Analyze transcript using Groq's Llama 3.3 70B.
    """
    client = get_client()

    if not transcript or len(transcript.strip()) < 20:
        return {
            "communication_score": 0,
            "confidence_score": 0,
            "clarity_score": 0,
            "overall_score": 0,
            "skills_mentioned": [],
            "sectors_mentioned": [],
            "languages_used": ["Unknown"],
            "is_bilingual": False,
            "filler_word_count": 0,
            "word_count": word_count,
            "speech_pace": "unknown",
            "top_strength": "Video was too short or unclear to analyze",
            "summary": "Could not analyze. Please re-record.",
            "feedback_for_candidate": "Please record a clearer video with at least 1 minute of speech.",
            "is_valid_intro": False
        }
    
    prompt = ANALYSIS_PROMPT.format(
        transcript=transcript[:3000],
        duration=duration_seconds,
        word_count=word_count
    )
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a precise JSON generator. You ONLY output valid JSON. No markdown. No explanation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=800
    )
    
    raw_response = response.choices[0].message.content.strip()
    
    if raw_response.startswith("```"):
        raw_response = raw_response.split("```")[1]
        if raw_response.startswith("json"):
            raw_response = raw_response[4:]
    raw_response = raw_response.strip()
    
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        return {
            "communication_score": 50,
            "confidence_score": 50,
            "clarity_score": 50,
            "overall_score": 50,
            "skills_mentioned": [],
            "sectors_mentioned": [],
            "languages_used": ["English"],
            "is_bilingual": False,
            "filler_word_count": 0,
            "word_count": word_count,
            "speech_pace": "moderate",
            "top_strength": "Error analyzing video.",
            "summary": "Processed, but detailed analysis failed.",
            "feedback_for_candidate": "Manual review pending.",
            "is_valid_intro": True
        }


def process_video_intro(video_bytes: bytes, filename: str) -> dict:
    """Main pipeline: extract audio → transcribe → analyze → return scores."""
    video_extensions = ['mp4', 'mov', 'avi', 'webm', 'mkv']
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    if ext in video_extensions:
        try:
            audio_bytes = extract_audio_from_video(video_bytes, filename)
            # If ffmpeg returned raw bytes back (fallback), keep original filename
            audio_filename = filename if audio_bytes is video_bytes else (filename.rsplit('.', 1)[0] + '.mp3')
        except Exception as e:
            raise ValueError(str(e))
    else:
        audio_bytes = video_bytes
        audio_filename = filename

    transcription_result = transcribe_audio(audio_bytes, audio_filename)

    analysis = analyze_transcript(
        transcription_result["transcript"],
        transcription_result["duration_seconds"],
        transcription_result["word_count"]
    )

    return {
        **analysis,
        "transcript": transcription_result["transcript"],
        "duration_seconds": transcription_result["duration_seconds"],
        "detected_language": transcription_result["detected_language"]
    }
