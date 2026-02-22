from typing import Optional, AsyncGenerator
import os

from google import genai


CLIENTE = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class ProcessamentoIA:
    """Gera uma resposta usando a API do modelo do Gemini."""
    
    def __init__(self):
        self._refinador = (
            "seu nome é tuttor (só diga se for perguntado por ele).\n"
            "Você é um tutor de inglês conciso (lacônico).\n"
            "Seu objetivo é criar um contexto; conversação com o usuário.\n"
            "Ele lhe manda uma mensagem e você responde criando conversa.\n"
            "Se o usuário disse: 'Não entendi' (Português), simplifique.\n"
            "O seu retorno será repassado a um TTS, então evite formatações.\n"
            "Responda com texto puro.\n"
        )
        self._resposta = str
        
    async def processar_texto(self, texto: str) -> AsyncGenerator[str, None]:
        """Gera uma resposta para o texto informado usando a API do gemini."""
        self._resposta = ""
        frase_completa = ""
    
        # Continua a execução enquanto a API retorna.
        stream = await CLIENTE.aio.models.generate_content_stream(
            model="gemini-2.5-flash",  # gemini-flash-latest
            config={"system_instruction": self._refinador},
            contents=texto
        )
    
        # Asynchronous Iteration para acessar pedaços da resposta do modelo.
        async for chunk in stream:
            if chunk.text:
                self._resposta += chunk.text
                frase_completa += chunk.text
                
                if any(p in chunk.text for p in (".", "!", "?", "\n")):  # envia para o TTS
                    yield frase_completa  # Entrega pedaços sem finalizar a função.
                
                    frase_completa = ""  # Limpa para a próxima frase completa.
        
    @property
    def resposta(self) -> Optional[str]:
        """Retorna a resposta se a operação for bem sucedida."""
        return self._resposta or None