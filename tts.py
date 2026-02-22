import io

import edge_tts


class RespostaTTS:
    """Gera um áudio para a resposta do gemini usando voz neural do edge."""
    
    async def gerar_audio(cls, resposta: str) -> None:
        """Gera um áudio do texto usando voz neural do edge-tts."""
        audio_buffer = io.BytesIO() # Buffer na memória para armazenar o áudio.
        
        communicate = edge_tts.Communicate(resposta, "en-US-GuyNeural")

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
                
        # Inicializa o ponteiro para que o pygame reproduza do inicio.
        audio_buffer.seek(0)
        return audio_buffer