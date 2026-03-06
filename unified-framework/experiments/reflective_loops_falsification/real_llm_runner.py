"""
Real LLM Runner for Reflective Loops Experiment

This module provides API integration for testing reflective loops with actual LLMs.
Supports multiple providers: OpenAI (GPT-4o), Anthropic (Claude), and xAI (Grok).
"""

import os
import json
import time
from typing import Dict, List, Optional, Literal
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM API calls."""
    provider: Literal["openai", "anthropic", "xai"]
    model: str
    api_key: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 60


@dataclass
class LLMResponse:
    """Response from an LLM API call."""
    text: str
    model: str
    provider: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    latency_ms: Optional[float] = None
    error: Optional[str] = None


class RealLLMRunner:
    """
    Runner for calling real LLM APIs with different system prompts.
    
    This replaces the simulation with actual API calls to test the
    reflective loops hypothesis with real model behavior.
    """
    
    def __init__(self, config: LLMConfig):
        """
        Initialize the LLM runner.
        
        Args:
            config: LLMConfig specifying provider and model details
        """
        self.config = config
        self._validate_config()
        self._init_client()
    
    def _validate_config(self):
        """Validate configuration and API keys."""
        if self.config.api_key is None:
            # Try to get from environment
            env_var_map = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "xai": "XAI_API_KEY"
            }
            env_var = env_var_map.get(self.config.provider)
            if env_var:
                self.config.api_key = os.environ.get(env_var)
            
            if self.config.api_key is None:
                logger.warning(
                    f"No API key provided for {self.config.provider}. "
                    f"Set {env_var} environment variable or pass api_key in config."
                )
    
    def _init_client(self):
        """Initialize the appropriate API client."""
        self.client = None
        
        if self.config.provider == "openai":
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.config.api_key)
            except ImportError:
                logger.error("OpenAI library not installed. Install with: pip install openai")
        
        elif self.config.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.config.api_key)
            except ImportError:
                logger.error("Anthropic library not installed. Install with: pip install anthropic")
        
        elif self.config.provider == "xai":
            try:
                import openai  # xAI uses OpenAI-compatible API
                self.client = openai.OpenAI(
                    api_key=self.config.api_key,
                    base_url="https://api.x.ai/v1"
                )
            except ImportError:
                logger.error("OpenAI library not installed (needed for xAI). Install with: pip install openai")
    
    def call_llm(
        self,
        system_prompt: str,
        user_message: str,
        additional_instructions: Optional[List[str]] = None
    ) -> LLMResponse:
        """
        Call the LLM with specified prompts.
        
        Args:
            system_prompt: Base system prompt (standard or reflective)
            user_message: User query/message
            additional_instructions: Optional additional instructions to inject
        
        Returns:
            LLMResponse with the model's output and metadata
        """
        if self.client is None:
            return LLMResponse(
                text="",
                model=self.config.model,
                provider=self.config.provider,
                error="API client not initialized"
            )
        
        # Construct full system prompt
        full_system_prompt = system_prompt
        if additional_instructions:
            full_system_prompt += "\n\nAdditional Instructions:\n"
            for i, instruction in enumerate(additional_instructions, 1):
                full_system_prompt += f"{i}. {instruction}\n"
        
        start_time = time.time()
        
        try:
            if self.config.provider in ["openai", "xai"]:
                response = self._call_openai_compatible(full_system_prompt, user_message)
            elif self.config.provider == "anthropic":
                response = self._call_anthropic(full_system_prompt, user_message)
            else:
                response = LLMResponse(
                    text="",
                    model=self.config.model,
                    provider=self.config.provider,
                    error=f"Unknown provider: {self.config.provider}"
                )
            
            response.latency_ms = (time.time() - start_time) * 1000
            return response
        
        except Exception as e:
            logger.error(f"Error calling {self.config.provider}: {e}")
            return LLMResponse(
                text="",
                model=self.config.model,
                provider=self.config.provider,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000
            )
    
    def _call_openai_compatible(self, system_prompt: str, user_message: str) -> LLMResponse:
        """Call OpenAI or OpenAI-compatible API (xAI)."""
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            timeout=self.config.timeout
        )
        
        return LLMResponse(
            text=response.choices[0].message.content,
            model=self.config.model,
            provider=self.config.provider,
            prompt_tokens=response.usage.prompt_tokens if response.usage else None,
            completion_tokens=response.usage.completion_tokens if response.usage else None
        )
    
    def _call_anthropic(self, system_prompt: str, user_message: str) -> LLMResponse:
        """Call Anthropic Claude API."""
        response = self.client.messages.create(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message}
            ],
            timeout=self.config.timeout
        )
        
        # Extract text from response
        text = ""
        for block in response.content:
            if hasattr(block, 'text'):
                text += block.text
        
        return LLMResponse(
            text=text,
            model=self.config.model,
            provider=self.config.provider,
            prompt_tokens=response.usage.input_tokens if response.usage else None,
            completion_tokens=response.usage.output_tokens if response.usage else None
        )


def load_prompt(prompt_path: str) -> str:
    """Load a prompt from file."""
    with open(prompt_path, 'r') as f:
        return f.read()


def create_runner_from_env(
    provider: str = "openai",
    model: Optional[str] = None
) -> RealLLMRunner:
    """
    Create a runner using environment variables for API keys.
    
    Args:
        provider: One of "openai", "anthropic", "xai"
        model: Model name (uses defaults if not specified)
    
    Returns:
        Configured RealLLMRunner instance
    """
    # Default models
    default_models = {
        "openai": "gpt-4o",
        "anthropic": "claude-3-5-sonnet-20241022",
        "xai": "grok-2-1212"
    }
    
    if model is None:
        model = default_models.get(provider, "gpt-4o")
    
    config = LLMConfig(
        provider=provider,
        model=model
    )
    
    return RealLLMRunner(config)


# Example usage
if __name__ == "__main__":
    # This is a simple test - the real experiment uses experiment_orchestrator.py
    
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python real_llm_runner.py <provider>")
        print("Providers: openai, anthropic, xai")
        print("\nNote: Set appropriate API key environment variable:")
        print("  OPENAI_API_KEY for OpenAI")
        print("  ANTHROPIC_API_KEY for Anthropic")
        print("  XAI_API_KEY for xAI")
        sys.exit(1)
    
    provider = sys.argv[1]
    
    print(f"Testing {provider} runner...")
    print("=" * 70)
    
    # Load prompts
    standard_prompt = load_prompt("prompts/standard/system_prompt.txt")
    
    # Create runner
    runner = create_runner_from_env(provider=provider)
    
    # Test call
    print("\nTesting standard prompt...")
    response = runner.call_llm(
        system_prompt=standard_prompt,
        user_message="What is 2+2? Please respond concisely."
    )
    
    if response.error:
        print(f"Error: {response.error}")
    else:
        print(f"Response: {response.text}")
        print(f"Tokens: {response.prompt_tokens} prompt, {response.completion_tokens} completion")
        print(f"Latency: {response.latency_ms:.1f}ms")
    
    print("\n" + "=" * 70)
    print("Test complete. Use experiment_orchestrator.py for full experiment.")
