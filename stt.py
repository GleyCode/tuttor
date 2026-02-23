from typing import Optional

import speech_recognition as sr


RECONHECEDOR = sr.Recognizer()


class TranscreveAudio:
    """"Transcreve áudio do microfone utilizando speech_recognition."""
    
    def __init__(self):
        self._reconhecedor = RECONHECEDOR
        self._texto = str
        
    def transcrever_audio(self, audio: sr.AudioData) -> None:
        """Transcreve o áudio recebido usando o serviço do Google."""
        try:
            self._texto = self._reconhecedor.recognize_google(audio)  # language="pt-BR"
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio.")
        except sr.RequestError as error:
            print(f"Não foi possível requisitar o serviço: {error}")
    
    @property
    def texto(self) -> Optional[str]:
        """Retorna o texto se a transcrição for bem sucedida."""
        return self._texto or None