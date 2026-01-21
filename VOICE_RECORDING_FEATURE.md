# 🎙️ Voice Recording Feature

## Overview
The patient form now includes voice recording functionality using ElevenLabs Speech-to-Text API to transcribe doctor-patient conversations in Uzbek.

## How It Works

### Frontend (User Interface)
1. **Microphone Button** appears at the top of the patient creation form
2. Click "Ёзишни бошлаш" (Start Recording) to begin
3. Recording indicator shows:
   - Red pulsing dot
   - Timer (minutes:seconds)
   - Progress bar
4. Click "Ёзишни тўхтатиш" (Stop Recording) to finish
5. Audio is automatically sent to backend for transcription
6. Transcription appears below the recording section

### Backend (Processing)
1. **Record Audio** - Browser captures audio using MediaRecorder API
2. **Send to Server** - Audio file (WebM format) sent to `/transcribe-audio/`
3. **ElevenLabs API** - Transcribes audio using `scribe_v2` model
4. **Language:** Uzbek (`uzb` language code)
5. **Features:**
   - Speaker diarization (who is speaking)
   - Audio event tagging (laughter, etc.)
6. **Return Transcription** - Text displayed on screen

## Files Modified/Created

### New Files:
- `static/js/voice_recorder.js` - JavaScript for recording
- `patients/views.py` - Added `transcribe_audio` view

### Modified Files:
- `healthcare_crm/settings.py` - Added ELEVENLABS_API_KEY
- `patients/urls.py` - Added `/transcribe-audio/` route
- `templates/patients/patient_form.html` - Added recording UI

## API Configuration

### ElevenLabs Settings:
- **API Key:** Stored in `settings.ELEVENLABS_API_KEY`
- **Model:** `scribe_v2`
- **Language:** Uzbek (`uzb`)
- **Diarization:** Enabled
- **Audio Events:** Enabled

## How to Use

### Step 1: Access Patient Form
```
http://127.0.0.1:8000/patients/create/
```

### Step 2: Grant Microphone Permission
- Browser will ask for microphone access
- Click "Allow"

### Step 3: Record Conversation
1. Click "Ёзишни бошлаш"
2. Speak in Uzbek
3. Click "Ёзишни тўхтатиш" when done

### Step 4: View Transcription
- Transcription appears automatically
- Currently just displays text (not auto-filling form fields yet)

## Technical Details

### Audio Format
- **Input:** Browser microphone
- **Recording Format:** WebM/Opus
- **Sent to API:** WebM blob

### API Request
```python
transcription = elevenlabs.speech_to_text.convert(
    file=audio_data,
    model_id="scribe_v2",
    tag_audio_events=True,
    language_code="uzb",  # Uzbek
    diarize=True,  # Speaker identification
)
```

### Response Format
```json
{
    "success": true,
    "transcription": "Transcribed text here...",
    "message": "Audio muvaffaqiyatli transkripsiya qilindi!"
}
```

## Browser Compatibility
- ✅ Chrome 49+
- ✅ Firefox 25+
- ✅ Edge 79+
- ✅ Safari 14.1+
- ❌ Internet Explorer (not supported)

## Limitations
1. **Internet Required** - API calls need internet connection
2. **Audio Quality** - Better microphone = better transcription
3. **Language** - Currently set to Uzbek only
4. **File Size** - Large recordings may take longer to process

## Future Enhancements (Not Implemented Yet)
- [ ] Auto-fill form fields from transcription
- [ ] AI extraction of patient name, age, symptoms
- [ ] Save audio file for record keeping
- [ ] Real-time transcription (streaming)
- [ ] Multiple language support
- [ ] Transcription editing

## Troubleshooting

### Microphone Not Working?
1. Check browser permissions
2. Try HTTPS (some browsers require it)
3. Check if another app is using microphone

### Transcription Empty?
1. Check internet connection
2. Verify ElevenLabs API key is valid
3. Check audio was recorded (timer should show >0:00)

### API Errors?
1. Verify API key in `settings.py`
2. Check ElevenLabs account has credits
3. Look at browser console for error messages

## Cost Estimation
- ElevenLabs charges per character transcribed
- Approximate: $0.001 per 1000 characters
- 1 minute audio ≈ 150 words ≈ 900 characters ≈ $0.0009

## Demo Flow

1. Go to: `http://127.0.0.1:8000/patients/create/`
2. See "Овозли ёзув" section at top
3. Click microphone button
4. Allow microphone access
5. Say something in Uzbek
6. Stop recording
7. Wait for transcription
8. See text appear below

---

**Status:** ✅ Fully Implemented
**Tested:** Ready for demo
**Language:** Uzbek (UZB)
