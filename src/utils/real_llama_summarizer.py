# Mistral-7B-Instruct Redirect for InfoGetter
from .mistral_summarizer import MistralSummarizer as RealLlamaSummarizer
from .mistral_summarizer import MistralSummarizer as LocalLLMSummarizer
__all__ = ['RealLlamaSummarizer', 'LocalLLMSummarizer']
