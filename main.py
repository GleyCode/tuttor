import pygame

from input_audio import CapturaAudio
from stt import TranscreveAudio
from llm import ProcessamentoIA
from tts import RespostaTTS
from play_sound import PlayAudio


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

    
        texto = transcritor.texto
        if texto is None:
            continue
        
        ia.processar_texto(texto)
        audio_buffer =  tts.gerar_audio(ia.resposta)
        PlayAudio.reproduzir_audio(audio_buffer)   
    
    
if __name__ == "__main__":
    # Inicia o loop de eventos.
    try:
        main()
    except KeyboardInterrupt:
        print("Encerrando o Tuttor...")
        pygame.mixer.quit() # Libera corretamente o fone.