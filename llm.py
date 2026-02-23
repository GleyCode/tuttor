from typing import Optional
import os

from google import genai


CLIENTE = genai.Client(api_key=os.getenv("GEMINI_API_KEY_TUTTOR"))


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