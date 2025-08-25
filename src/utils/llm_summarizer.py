"""
Academic LocalLLM Integration for InfoGetter
===========================================

This integrates the Academic LocalLLM system specialized for academic paper summarization
"""

import logging
from .academic_localllm import AcademicLocalLLM

# Use the Academic LocalLLM implementation
LLMSummarizer = AcademicLocalLLM
