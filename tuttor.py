import os
import io
from typing import Optional
import time

import speech_recognition as sr
from google import genai
import edge_tts
import pygame


RECONHECEDOR = sr.Recognizer()
CLIENTE = genai.Client(api_key=os.getenv("GEMINI_API_KEY_TUTTOR"))


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
        
        
class TranscreveAudio:
    """"Transcreve áudio do microfone utilizando speech_recognition."""
    
    def __init__(self):
        self._reconhecedor = RECONHECEDOR
        self._texto = ""
        
    def transcrever_audio(self, audio: sr.AudioData) -> None:
        """Transcreve o áudio recebido usando o serviço do Google."""
        try:
            self._texto = self._reconhecedor.recognize_google(audio, language="pt-BR")  # language="pt-BR"
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio.")
        except sr.RequestError as error:
            print(f"Não foi possível requisitar o serviço: {error}")
    
    @property
    def texto(self) -> Optional[str]:
        """Retorna o texto se a transcrição for bem sucedida."""
        return self._texto or None
    
        
class ProcessamentoIA:
    """Gera uma resposta usando a API do modelo do Gemini."""
    
    def __init__(self):
        self._refinador = (
            "seu nome é tuttor (só diga se for perguntado por ele).\n"
            "Você é um psicologa (lacônico).\n"
            "Seu objetivo é criar um contexto; conversação com o usuário.\n"
            "Ele lhe manda uma mensagem e você responde criando conversa.\n"
            "O seu retorno será repassado a um TTS, então evite formatações.\n"
            "Responda com texto puro.\n"
        )
        self._resposta = ""
        
    def processar_texto(self, texto: str) -> None:
        """Gera uma resposta para o texto informado usando a API do gemini."""
    
        self._resposta = CLIENTE.models.generate_content(
            model="gemini-flash-latest",  # gemini-flash-latest gemini-2.5-flash
            config={"system_instruction": self._refinador},
            contents=texto
        ).text
            
    @property
    def resposta(self) -> Optional[str]:
        """Retorna a resposta se a operação for bem sucedida."""
        return self._resposta or None
            

class RespostaTTS:
    """Gera um áudio para a resposta do gemini usando voz neural do edge."""
    
    def gerar_audio(self, resposta: str) -> None:
        """Gera um áudio do texto usando voz neural do edge-tts."""
        audio_buffer = io.BytesIO() # Buffer na memória para armazenar o áudio.
        
        communicate = edge_tts.Communicate(resposta, "pt-BR-FranciscaNeural")

        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
                
        # Inicializa o ponteiro para que o pygame reproduza do inicio.
        audio_buffer.seek(0)
        return audio_buffer
        
        
class PlayAudio:
    """Reproduz o áudio usando via Pygame."""
    
    @classmethod
    def reproduzir_audio(cls, audio_buffer: io.BytesIO) -> None:
        """Reproduza o áudio recebido usando os recuros do pygame."""
        pygame.mixer.music.load(audio_buffer, "mp3")  # Carrega o áudio do buffer.
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)


def main():
    """Pipeline de execução do sistema."""
    capturador = CapturaAudio()
    transcritor = TranscreveAudio()
    ia = ProcessamentoIA()
    tts = RespostaTTS()
    
    pygame.mixer.init()
    
    while True:
        capturador.capturar_audio()

        audio = capturador.audio
        if audio is None:
            continue
        
        transcritor.transcrever_audio(audio)
    
        # print(">>> " + transcritor.texto)
    
        texto = transcritor.texto
        if texto is None:
            continue
        
        ia.processar_texto(texto)
        audio_buffer = tts.gerar_audio(ia.resposta)
        PlayAudio.reproduzir_audio(audio_buffer)
            
        # print("_" + ia.resposta)
        
        # print("Encerando o Tuttor...")    
    
if __name__ == "__main__":
    # Inicia o loop de eventos.
    try:
        main()
    except KeyboardInterrupt:
        print("Encerrando o Tuttor...")
        pygame.mixer.quit() # Libera corretamente o fone.