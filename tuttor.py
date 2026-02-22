import speech_recognition as sr
from google import genai
import os
import asyncio
import edge_tts
import wave
import io
import pygame


reconhecedor = sr.Recognizer()
cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class CapturaAudio():
    """Classe responsável pela captura do áudio."""
    
    def __init__(self):
        """Inicialize a classe com os seguintes atributos:
        
        Atributos:
            _reconhecedor:
            _audio:
        """
        self._reconhecedor = reconhecedor
        self._audio = bytes
        
    def capturar_audio(self) -> None:
        """Capture o áudio do microfone.
        
        Acessa o microfone e captura o áudio, mas antes disso cálcula a energia 
        (RMS) para eliminar o ruído do ambiente. Por fim, armazena o áudio.
        """
        with sr.Microphone() as source:
            # Escuta por 1 segundo para calibrar o ruído.
            print("[ Ajustando ruído... ]")
            self._reconhecedor.adjust_for_ambient_noise(source, duration=0.5)
            print("[ Fale... ]")
            self._audio = self._reconhecedor.listen(source)

    @property
    def audio(self): # Getter
        """Retorne os bytes de audio se a captura for bem sucedida."""
        if self._audio:
            return self._audio
        
        
class TranscreveAudio():
    """Classe responsável pela transcrição do áudio."""
    
    def __init__(self, audio_bytes):
        """Inicialize a classe com os seguintes atributos:
        
        Atributos:
            _reconhecedor = 
            _audio = 
            _texto = 
        """
        self._reconhecedor = reconhecedor
        self._audio = audio_bytes
        self._texto = ""
        
    def transcrever_audio(self) -> None:
        """"""
        try:
            self._texto = self._reconhecedor.recognize_google(self._audio)
            #language="pt-BR"
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio.")
        except sr.RequestError as error:
            print("Não foi possível requisitar o serviço: {error}")
    
    @property
    def texto(self):
        """Retorne o texto se a transcrição for bem sucedida."""
        if len(self._texto) > 0:
            return self._texto
    
        
class ProcessamentoIA():
    """"""
    
    def __init__(self):
        """"""
        self._refinador = """
        seu nome é tuttor (só diga seu nome se for perguntado por ele).
        
        Você é um tutor de inglês conciso (lacônico).
        Seu objetivo é criar um contexto, ou seja, conversação com o usuário.
        Ele lhe manda uma mensagem e você responde criando conversa.
        
        Se o usuário disse: "Não entendi" (Português), simplifique.
        
        O seu retorno será repassado a um TTS, então evite formatações.
        Resposda com texto puro.
        """
        self._resposta = ""
        self._tts = RespostaTTS()
        
    async def processar_texto(self, texto) -> None:
        """"""
        
        frase_completa = ""
    
        # Continue a execução enquanto a API retorna.
        stream = await cliente.aio.models.generate_content_stream(
            #gemini-flash-latest
            #gemini-2.5-flash
            model="gemini-flash-latest",
            config={"system_instruction": self._refinador},
            contents=texto
        )
    
        # Asynchronous Iteration
        async for chunk in stream:
            if chunk.text:
                self._resposta += chunk.text
                frase_completa += chunk.text
                
                # enviar para o TTS
                if any(p in chunk.text for p in (".", "!", "?")):
                    await self._tts.gerar_audio(frase_completa)
                
                # Limpar
                frase_completa = ""
        
    @property
    def resposta(self):
        """"""
        if len(self._resposta) > 0:
            return self._resposta
            

class RespostaTTS():
    """"""
    
    def __init__(self):
        """"""
        self._audio_buffer = io.BytesIO() # Buffer na memória.
    
    async def gerar_audio(self, resposta) -> None:
        """"""
        communicate = edge_tts.Communicate(resposta, "en-US-GuyNeural")

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                self._audio_buffer.write(chunk["data"])
                
        # Inicializa o ponteiro.
        self._audio_buffer.seek(0)
        await PlayAudio.reproduzir_audio(self._audio_buffer)
        
        
class PlayAudio():
    """"""
    
    @classmethod
    async def reproduzir_audio(cls, audio_buffer):
        """"""
        pygame.mixer.music.load(audio_buffer, "mp3")
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)


async def main():
    """Pipeline de execução do sistema."""
    pygame.mixer.init()
    
    while True:
            capturador = CapturaAudio()
            capturador.capturar_audio()
    
            transcritor = TranscreveAudio(capturador.audio)
            transcritor.transcrever_audio()
    
            print(">>> " + transcritor.texto)
    
            ia = ProcessamentoIA()
            await ia.processar_texto(transcritor.texto)
    
            print("_" + ia.resposta)
        
          
        #print("Encerando o Tuttor...")
        #pygame.mixer.quit() # Encerra a reprodução.    
    
    
if __name__ == "__main__":
    # Inicia o loop de eventos.
    asyncio.run(main())
