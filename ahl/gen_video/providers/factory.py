"""Factory for creating image providers."""

from .base import ImageProvider
from .openrouter_provider import OpenRouterProvider


def create_provider(
    provider: str = "openrouter",
    model: str | None = None,
    local_variant: str = "schnell",
) -> ImageProvider:
    """Create an image provider by name.

    Args:
        provider: 'openrouter', 'local', or 'auto' (try local first, fallback to openrouter).
        model: Model name override (for openrouter, e.g. 'black-forest-labs/flux.2-pro').
        local_variant: Which local FLUX variant to use ('schnell', 'dev', '2-dev').

    Returns:
        An ImageProvider instance.

    Raises:
        ValueError: If provider name is unknown.
    """
    provider = provider.lower()

    if provider == "openrouter":
        return OpenRouterProvider(model=model or "black-forest-labs/flux.2-pro")

    elif provider == "local":
        from .local_provider import LocalGPUProvider

        return LocalGPUProvider(variant=local_variant)

    elif provider == "auto":
        # Try local first, fall back to openrouter
        try:
            from .local_provider import LocalGPUProvider

            # Quick check if model exists
            model_paths = {
                "schnell": "/root/FLUX.1-schnell",
                "dev": "/root/FLUX.1-dev",
                "2-dev": "/root/FLUX.2-dev",
            }
            model_dir = model_paths.get(local_variant)
            if model_dir and os.path.isdir(model_dir):
                print(f"  Auto: using local GPU (FLUX.{local_variant})")
                return LocalGPUProvider(variant=local_variant)
        except Exception:
            pass
        print("  Auto: falling back to OpenRouter")
        return OpenRouterProvider(model=model or "black-forest-labs/flux.2-pro")

    else:
        valid = ["openrouter", "local", "auto"]
        raise ValueError(f"Unknown provider '{provider}'. Valid: {valid}")


# Need os for auto check
import os  # noqa: E402
