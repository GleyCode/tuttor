import speech_recognition as sr
from google import genai
import os
import asyncio
import edge_tts
import io
import pygame


reconhecedor = sr.Recognizer()
cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class CapturaAudio():
    """Classe responsável pela captura do áudio."""
    
    def __init__(self):
        """Inicialize a classe com os seguintes atributos:
        
        Atributos:
            _reconhecedor: Instância de Recognizer para coleta do áudio.
            _audio: Bytes do áudio capturado.
        """
        self._reconhecedor = reconhecedor
        self._audio = bytes
        
    def capturar_audio(self) -> None:
        """Capture o áudio do microfone.
        
        Acessa o microfone e captura o áudio, mas antes disso cálcula a energia 
        (RMS) para eliminar o ruído do ambiente. Por fim, armazena o áudio.
        """
        with sr.Microphone() as source:
            # Escuta por 0.5 segundo para calibrar o ruído.
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
    
    def __init__(self):
        """Inicialize a classe com os seguintes atributos:
        
        Atributos:
            _reconhecedor = Instância de Recognizer para transcrição do áudio.
            _audio = Bytes do áudio capturado.
            _texto = Áudio transcrito.
        """
        self._reconhecedor = reconhecedor
        self._texto = ""
        
    def transcrever_audio(self, audio) -> None:
        """Trascreva o áudio recebido.
        
        Recebe o áudio como bytes, em seguida passa para o serviço de FTT do 
        google. 
        """
        try:
            self._texto = self._reconhecedor.recognize_google(audio)
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
    """Classe responsável pelo processamento da resposta."""
    
    def __init__(self):
        """Inicialize a classe com os seguintes atributos:
        
        Atributos:
            _refinado: Instruções para o modelo, afim de melhorar o desempenho.
            _tts: Classe responsável pela geração do áudio.
        """
        self._refinador = """
        seu nome é tuttor (só diga seu nome se for perguntado por ele).
        
        Você é um tutor de inglês conciso (lacônico).
        Seu objetivo é criar um contexto, ou seja, conversação com o usuário.
        Ele lhe manda uma mensagem e você responde criando conversa.
        
        Se o usuário disse: "Não entendi" (Português), simplifique.
        
        O seu retorno será repassado a um TTS, então evite formatações.
        Resposda com texto puro.
        """
        self._tts = RespostaTTS()
        self._resposta = ""
        
    async def processar_texto(self, texto) -> None:
        """Gere uma reposta para o texto informado.
        
        Recebe um texto e repassa para o modelo do Gemini responsável pela 
        geração de uma resposta aleatória, mas contextualizada.
        """
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
                if any(p in chunk.text for p in (".", "!", "?", "\n")):
                    await self._tts.gerar_audio(frase_completa)
                
                # Limpar
                frase_completa = ""
        
    @property
    def resposta(self):
        """Retorne a resposta se a operação for bem sucedida."""
        if len(self._resposta) > 0:
            return self._resposta
            

class RespostaTTS():
    """Classe responsável pela geração do áudio."""
    
    def __init__(self):
        """Inicialize a classe com os seguintes atributos:
        
        Atributos:
            _audio_buffer: Local na memória RAM onde será armazenado o áudio.
        """
        self._audio_buffer = io.BytesIO() # Buffer na memória.
    
    async def gerar_audio(self, resposta) -> None:
        """Gere um áudio do texto.
        
        Recebe um texto (resposta) e gera um áudio com uma voz neural do edge; 
        em seguida armazena de forma assíncrona os chunks (pedaços) do áudio em 
        um buffer na memória.
        
        Args:
            resposta: Resposta (texto) que será transformado em áudio.
        """
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
        """Reproduza o áudio recebido.
        
        Recebe o áudio da resposta e utiliza o módulo de mixer do Pygame para 
        reproduzir o áudio."""
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
    
            transcritor = TranscreveAudio()
            transcritor.transcrever_audio(capturador.audio)
    
            #print(">>> " + transcritor.texto)
    
            ia = ProcessamentoIA()
            await ia.processar_texto(transcritor.texto)
    
            #print("_" + ia.resposta)
        
          
        #print("Encerando o Tuttor...")
        #pygame.mixer.quit() # Encerra a reprodução.    
    
    
if __name__ == "__main__":
    # Inicia o loop de eventos.
    asyncio.run(main())
