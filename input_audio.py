from typing import Optional

import speech_recognition as sr


RECONHECEDOR = sr.Recognizer()


class CapturaAudio:
    """Captura áudio do microfone utilizando speech_recognition."""
    
    def __init__(self):
        self._reconhecedor = RECONHECEDOR
        self._audio = sr.AudioData
        
    def capturar_audio(self) -> None:
        """Captura o áudio do microfone, livre de ruídos."""
        with sr.Microphone() as source:
            print("[ Ajustando ruído... ]")
            self._reconhecedor.adjust_for_ambient_noise(source, duration=0.5)   # Escuta por 0.5 segundo para calibrar o ruído.
            print("[ Fale... ]")
            self._audio = self._reconhecedor.listen(source)

    @property
    def audio(self) -> Optional[sr.AudioData]: # Getter
        """Retorna os bytes de audio se a captura for bem sucedida."""
        return self._audio or None
