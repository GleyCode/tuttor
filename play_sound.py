import asyncio
import io

import pygame


class PlayAudio:
    """Reproduz o áudio usando via Pygame."""
    
    @classmethod
    async def reproduzir_audio(cls, audio_buffer: io.BytesIO) -> None:
        """Reproduza o áudio recebido usando os recuros do pygame."""
        pygame.mixer.music.load(audio_buffer, "mp3")  # Carrega o áudio do buffer.
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
