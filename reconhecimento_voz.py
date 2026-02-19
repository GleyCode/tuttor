import speech_recognition as sr
from google import genai
import os
import io
import edge_tts
import pygame
import asyncio


class Pergunta():
    """Classe responsável pela captura e trascrição do áudio."""
    
    def __init__(self):
        """Inicialize a classe com os seguintes atributos:
        
        Atributos:
            _reconhecedor: Funcionalidades de reconhecimento de fala.
            _audio: Áudio capturado do microfone.
            _texto: Resultado da transcrição do áudio.
        """
        self._reconhecedor = sr.Recognizer()
        self._audio = None
        self._texto = None
        
    def capturar_audio(self):
        """Acesse o microfone do dispositivo para capturar o áudio.
        
        Usa um gerenciador de contexto para acessar o microfone, em seguida usa 
        adjust_for_ambient_noise para trechos de áudio sem fala (calibrador de 
        energia ambiente) onde é interrompido quando uma fala for detectada. 
        Por fim, usa lister para armazenar blocos de dados de áudio. 
        """
        with sr.Microphone() as source:
            print("Escutando...")
            self._reconhecedor.adjust_for_ambient_noise(source, duration=0.5)
            self._audio = self._reconhecedor.listen(source)
    
    def transcrever_audio(self):
        """Use o servíço de reconhecimento de voz do Google.
        
        Usa recognize_google para acessar o servíço de reconhecimento de voz do 
        Google com a opção de 'pt-BR' para português do Brasil.
        """
        try:
            self._texto = self._reconhecedor.recognize_google(self._audio,language="pt-BR")
        except sr.UnknownValueError:
            print(f"Não foi possível entender o áudio")
        except sr.RequestError as error:
            print(f"Erro ao solicitar resultados de voz; {error}")
            

class Tuttor():
    """"""
    
    def __init__(self):
        """"""
        self._cliente = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self._resposta = None
        
    def processar_texto(self, texto):
        """"""
        refinador = """Você se chama Tuttor e é um tutor educativo conciso, 
        claro e lacônico ao máximo. A saída deve ser em texto puro sem nenhuma 
        formatação. O texto será passado para um síntetizador de voz. Evite 
        qualquer formatação."""
        
        self._resposta = self._cliente.models.generate_content(
            model="gemini-flash-latest",
            config={"system_instruction": refinador},
            contents=texto
        ).text
        

class Resposta():
    """"""
    
    def __init__(self):
        """"""
        self._audio_buffer = io.BytesIO() # Buffer na mémoria.
        self._communicate = None
        
    def criar_audio_resposta(self, resposta):
        """"""
        self._communicate = edge_tts.Communicate(resposta, "pt-BR-AntonioNeural")

        # Coletamos os pedaços (chunks) do áudio e escrevemos no buffer
        for chunk in self._communicate.stream_sync():
            if chunk["type"] == "audio":
                self._audio_buffer.write(chunk["data"])
        
        # Voltamos o cursor do buffer para o início
        self._audio_buffer.seek(0)

    def reproduzir_audio(self):
        """"""
        pygame.mixer.init() # Inicia o módulo de som.
        pygame.mixer.music.load(self._audio_buffer, "mp3")
        pygame.mixer.music.play()
        
        # Verifica se o áudio está sendo reproduzido.
        while pygame.mixer.music.get_busy():
            asyncio.sleep(0.1)
        
        pygame.mixer.quit() # Encerra a reprodução.
        

def main():
    """"""
    while True:
        pergunta = Pergunta()
        pergunta.capturar_audio()
        pergunta.transcrever_audio()
    
        tuttor = Tuttor()
        tuttor.processar_texto(pergunta._texto)
        
        resposta = Resposta()
        resposta.criar_audio_resposta(tuttor._resposta)
        resposta.reproduzir_audio()
    
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Encerrando o Tuttor...")