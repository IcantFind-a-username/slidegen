"""
Image Service - Automatic Image Integration

This module handles image discovery, caching, and placement for slides.
Images are semantically aligned with slide content based on intent and keywords.

Design Principles:
1. Images are DECORATIVE but SEMANTICALLY RELEVANT
2. Every image has a defined ROLE (hero, illustrative, icon, decorative)
3. Images are placed in PREDEFINED LAYOUT REGIONS
4. Fallback to placeholder/shape when no suitable image found

Author: SlideGen Team
"""

import os
import hashlib
import json
import requests
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
from io import BytesIO

from .deck_architect import ImageRole, SlideIntent, INTENT_IMAGE_KEYWORDS


# =============================================================================
# CONFIGURATION
# =============================================================================

# Image cache directory
CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "image_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Unsplash API (free tier)
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Placeholder image dimensions by role
IMAGE_DIMENSIONS = {
    ImageRole.HERO: (1920, 1080),
    ImageRole.ILLUSTRATIVE: (800, 600),
    ImageRole.DECORATIVE: (400, 300),
    ImageRole.ICON: (128, 128),
    ImageRole.DATA_VIZ: (800, 500),
    ImageRole.NONE: (0, 0),
}

# Layout position specifications (in inches from origin)
IMAGE_POSITIONS = {
    "background": {"left": 0, "top": 0, "width": 13.33, "height": 7.5, "opacity": 0.3},
    "left": {"left": 0.5, "top": 1.5, "width": 4.5, "height": 5.0, "opacity": 1.0},
    "right": {"left": 8.0, "top": 1.5, "width": 4.5, "height": 5.0, "opacity": 1.0},
    "bottom": {"left": 2.0, "top": 4.5, "width": 9.0, "height": 2.5, "opacity": 1.0},
    "corner": {"left": 11.0, "top": 0.3, "width": 2.0, "height": 1.5, "opacity": 0.8},
}


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ImageSpec:
    """Specification for an image to be placed on a slide."""
    url: Optional[str]
    local_path: Optional[str]
    role: ImageRole
    position: str  # "background", "left", "right", "bottom", "corner"
    width: float
    height: float
    opacity: float
    alt_text: str
    attribution: Optional[str]
    is_placeholder: bool = False


@dataclass
class ImageSearchResult:
    """Result from image search."""
    url: str
    thumbnail_url: str
    width: int
    height: int
    alt_text: str
    attribution: str
    source: str


# =============================================================================
# IMAGE SEARCH PROVIDERS
# =============================================================================

class ImageProvider:
    """Base class for image providers."""
    
    def search(self, keywords: List[str], count: int = 3) -> List[ImageSearchResult]:
        raise NotImplementedError


class UnsplashProvider(ImageProvider):
    """Unsplash API provider."""
    
    def __init__(self, access_key: str = None):
        self.access_key = access_key or UNSPLASH_ACCESS_KEY
    
    def search(self, keywords: List[str], count: int = 3) -> List[ImageSearchResult]:
        if not self.access_key:
            return []
        
        query = " ".join(keywords[:3])
        
        try:
            response = requests.get(
                UNSPLASH_API_URL,
                params={
                    "query": query,
                    "per_page": count,
                    "orientation": "landscape",
                },
                headers={"Authorization": f"Client-ID {self.access_key}"},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for photo in data.get("results", []):
                results.append(ImageSearchResult(
                    url=photo["urls"]["regular"],
                    thumbnail_url=photo["urls"]["thumb"],
                    width=photo["width"],
                    height=photo["height"],
                    alt_text=photo.get("alt_description", ""),
                    attribution=f"Photo by {photo['user']['name']} on Unsplash",
                    source="unsplash"
                ))
            return results
            
        except Exception as e:
            print(f"Unsplash search failed: {e}")
            return []


class PlaceholderProvider(ImageProvider):
    """Fallback placeholder provider."""
    
    PLACEHOLDER_COLORS = {
        ImageRole.HERO: "1e3a5f",
        ImageRole.ILLUSTRATIVE: "2d5a87",
        ImageRole.DECORATIVE: "4a7ba7",
        ImageRole.ICON: "e07b39",
        ImageRole.DATA_VIZ: "66b2b2",
    }
    
    def search(self, keywords: List[str], count: int = 1, role: ImageRole = ImageRole.DECORATIVE) -> List[ImageSearchResult]:
        """Generate placeholder image URLs."""
        width, height = IMAGE_DIMENSIONS.get(role, (400, 300))
        color = self.PLACEHOLDER_COLORS.get(role, "cccccc")
        
        # Using placeholder.com or similar service
        url = f"https://via.placeholder.com/{width}x{height}/{color}/ffffff?text={'+'.join(keywords[:2])}"
        
        return [ImageSearchResult(
            url=url,
            thumbnail_url=url,
            width=width,
            height=height,
            alt_text=" ".join(keywords),
            attribution="Placeholder",
            source="placeholder"
        )]


# =============================================================================
# IMAGE SERVICE
# =============================================================================

class ImageService:
    """
    Main service for image discovery and management.
    
    Workflow:
    1. Receive slide intent and keywords
    2. Determine image role from intent
    3. Search for appropriate images
    4. Download and cache selected image
    5. Return ImageSpec for renderer
    """
    
    def __init__(self, enable_web_search: bool = False):
        self.enable_web_search = enable_web_search and bool(UNSPLASH_ACCESS_KEY)
        self.unsplash = UnsplashProvider()
        self.placeholder = PlaceholderProvider()
        self._cache: Dict[str, ImageSpec] = {}
    
    def get_image_for_slide(
        self,
        intent: SlideIntent,
        keywords: List[str],
        position: str = None
    ) -> Optional[ImageSpec]:
        """
        Get an appropriate image for a slide.
        
        Args:
            intent: Slide intent
            keywords: Search keywords
            position: Optional position override
        
        Returns:
            ImageSpec with image details, or None if no image needed
        """
        from .deck_architect import INTENT_IMAGE_ROLE
        
        # Get image role
        role = INTENT_IMAGE_ROLE.get(intent, ImageRole.NONE)
        
        if role == ImageRole.NONE:
            return None
        
        # Generate cache key
        cache_key = self._generate_cache_key(intent, keywords)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Determine position
        if position is None:
            position = self._default_position_for_role(role)
        
        # Get position specs
        pos_spec = IMAGE_POSITIONS.get(position, IMAGE_POSITIONS["right"])
        
        # Search for images
        results = self._search_images(keywords, role)
        
        if not results:
            # Use placeholder
            results = self.placeholder.search(keywords, role=role)
        
        if results:
            result = results[0]
            image_spec = ImageSpec(
                url=result.url,
                local_path=self._get_cached_path(cache_key),
                role=role,
                position=position,
                width=pos_spec["width"],
                height=pos_spec["height"],
                opacity=pos_spec["opacity"],
                alt_text=result.alt_text,
                attribution=result.attribution,
                is_placeholder=(result.source == "placeholder")
            )
            
            # Cache the spec
            self._cache[cache_key] = image_spec
            
            return image_spec
        
        return None
    
    def _search_images(self, keywords: List[str], role: ImageRole) -> List[ImageSearchResult]:
        """Search for images using available providers."""
        
        # Add role-specific keywords
        enhanced_keywords = keywords.copy()
        role_keywords = {
            ImageRole.HERO: ["abstract", "professional"],
            ImageRole.ILLUSTRATIVE: ["illustration", "concept"],
            ImageRole.DECORATIVE: ["minimal", "simple"],
        }
        enhanced_keywords.extend(role_keywords.get(role, []))
        
        if self.enable_web_search:
            results = self.unsplash.search(enhanced_keywords)
            if results:
                return results
        
        return []
    
    def _default_position_for_role(self, role: ImageRole) -> str:
        """Get default position for an image role."""
        return {
            ImageRole.HERO: "background",
            ImageRole.ILLUSTRATIVE: "right",
            ImageRole.DECORATIVE: "corner",
            ImageRole.ICON: "corner",
            ImageRole.DATA_VIZ: "bottom",
        }.get(role, "right")
    
    def _generate_cache_key(self, intent: SlideIntent, keywords: List[str]) -> str:
        """Generate cache key for image lookup."""
        content = f"{intent.value}:{':'.join(sorted(keywords[:5]))}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _get_cached_path(self, cache_key: str) -> str:
        """Get path for cached image."""
        return str(CACHE_DIR / f"{cache_key}.jpg")
    
    def download_and_cache(self, image_spec: ImageSpec) -> bool:
        """Download image and save to cache."""
        if not image_spec.url or image_spec.is_placeholder:
            return False
        
        try:
            response = requests.get(image_spec.url, timeout=30)
            response.raise_for_status()
            
            with open(image_spec.local_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            print(f"Failed to download image: {e}")
            return False
    
    def get_image_bytes(self, image_spec: ImageSpec) -> Optional[BytesIO]:
        """Get image as BytesIO for direct insertion."""
        if image_spec.local_path and os.path.exists(image_spec.local_path):
            with open(image_spec.local_path, 'rb') as f:
                return BytesIO(f.read())
        
        if image_spec.url:
            try:
                response = requests.get(image_spec.url, timeout=30)
                response.raise_for_status()
                return BytesIO(response.content)
            except Exception:
                pass
        
        return None


# =============================================================================
# IMAGE PLACEHOLDER GENERATOR
# =============================================================================

class PlaceholderGenerator:
    """
    Generates placeholder visuals when real images aren't available.
    Uses shapes and gradients to create professional-looking placeholders.
    """
    
    @staticmethod
    def generate_for_role(role: ImageRole, keywords: List[str] = None) -> Dict[str, Any]:
        """
        Generate placeholder specification for a role.
        
        Returns dict with:
        - type: "gradient", "pattern", "solid"
        - colors: list of colors
        - text: optional overlay text
        """
        if role == ImageRole.HERO:
            return {
                "type": "gradient",
                "colors": ["#1e3a5f", "#2d5a87"],
                "direction": "diagonal",
                "text": None
            }
        elif role == ImageRole.ILLUSTRATIVE:
            return {
                "type": "pattern",
                "colors": ["#4a7ba7", "#6699cc"],
                "pattern": "dots",
                "text": keywords[0] if keywords else None
            }
        elif role == ImageRole.DECORATIVE:
            return {
                "type": "solid",
                "colors": ["#e8f0f8"],
                "text": None
            }
        else:
            return {
                "type": "solid",
                "colors": ["#f5f5f5"],
                "text": None
            }


# =============================================================================
# BATCH IMAGE PROCESSOR
# =============================================================================

class BatchImageProcessor:
    """
    Processes images for an entire deck at once.
    Enables parallel downloading and better caching.
    """
    
    def __init__(self, image_service: ImageService):
        self.service = image_service
    
    def process_deck(self, slides: List[Dict[str, Any]]) -> Dict[str, ImageSpec]:
        """
        Process all slides and return image specs keyed by slide_id.
        """
        results = {}
        
        for slide in slides:
            slide_id = slide.get('slide_id', '')
            intent_str = slide.get('intent', 'concept')
            keywords = slide.get('image_keywords', [])
            
            try:
                intent = SlideIntent(intent_str)
            except ValueError:
                intent = SlideIntent.KEY_POINTS
            
            image_spec = self.service.get_image_for_slide(intent, keywords)
            if image_spec:
                results[slide_id] = image_spec
                
                # Download in background (could be parallelized)
                self.service.download_and_cache(image_spec)
        
        return results


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'ImageSpec',
    'ImageSearchResult',
    'ImageService',
    'PlaceholderGenerator',
    'BatchImageProcessor',
    'IMAGE_POSITIONS',
    'IMAGE_DIMENSIONS',
]

