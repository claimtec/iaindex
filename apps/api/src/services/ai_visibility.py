"""
AI Visibility Service
Checks if websites are mentioned in AI search engines (ChatGPT, Perplexity, Claude)
"""
import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from ..config import settings

logger = logging.getLogger(__name__)


class AIPlatform(str, Enum):
    """AI search platform types"""
    CHATGPT = "chatgpt"
    PERPLEXITY = "perplexity"
    CLAUDE = "claude"


class AIVisibilityService:
    """Service for checking website visibility in AI search engines"""

    def __init__(self):
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        self.max_retries = 2

    async def check_visibility(
        self,
        url: str,
        queries: List[str],
        platforms: Optional[List[AIPlatform]] = None
    ) -> Dict[str, Any]:
        """
        Check if a URL appears in AI search results for given queries

        Args:
            url: Website URL to check visibility for
            queries: List of search queries to test
            platforms: Optional list of platforms to check (defaults to all)

        Returns:
            Dictionary with visibility score and mention details
        """
        if not platforms:
            platforms = [AIPlatform.CHATGPT, AIPlatform.PERPLEXITY]

        # Extract domain from URL for matching
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace('www.', '')

        all_mentions = []
        platform_scores = {}

        # Check each platform
        for platform in platforms:
            try:
                platform_mentions = await self._check_platform(
                    platform=platform,
                    domain=domain,
                    url=url,
                    queries=queries
                )
                all_mentions.extend(platform_mentions)

                # Calculate platform-specific score
                platform_scores[platform.value] = self._calculate_platform_score(
                    platform_mentions
                )

                logger.info(
                    f"Checked {platform.value} for {domain}: "
                    f"{len(platform_mentions)} mentions found"
                )

            except Exception as e:
                logger.error(f"Error checking {platform.value} for {domain}: {e}")
                platform_scores[platform.value] = 0

        # Calculate overall visibility score
        visibility_score = self.get_visibility_score(all_mentions)

        return {
            'visibility_score': visibility_score,
            'mentions': all_mentions,
            'platform_scores': platform_scores,
            'total_mentions': len(all_mentions),
            'checked_at': datetime.utcnow().isoformat(),
            'queries_tested': queries,
            'platforms_checked': [p.value for p in platforms]
        }

    async def _check_platform(
        self,
        platform: AIPlatform,
        domain: str,
        url: str,
        queries: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Check visibility on a specific AI platform

        Args:
            platform: AI platform to check
            domain: Domain to search for
            url: Full URL for reference
            queries: Search queries to test

        Returns:
            List of mention dictionaries
        """
        mentions = []

        for query in queries:
            try:
                if platform == AIPlatform.CHATGPT:
                    mention = await self._check_chatgpt_search(query, domain, url)
                elif platform == AIPlatform.PERPLEXITY:
                    mention = await self._check_perplexity_search(query, domain, url)
                elif platform == AIPlatform.CLAUDE:
                    # Claude doesn't have a public search API yet
                    # This is a placeholder for future implementation
                    mention = None
                else:
                    mention = None

                if mention:
                    mentions.append(mention)

            except Exception as e:
                logger.warning(
                    f"Error checking {platform.value} for query '{query}': {e}"
                )
                continue

        return mentions

    async def _check_chatgpt_search(
        self,
        query: str,
        domain: str,
        url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check ChatGPT Search API for URL mentions

        Args:
            query: Search query
            domain: Domain to look for
            url: Full URL

        Returns:
            Mention dictionary if found, None otherwise
        """
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured, skipping ChatGPT check")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Note: Using OpenAI's chat completion with web browsing
                # This is a simplified approach - adjust based on actual API
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Search the web and provide sources."
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.3
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get("choices", [{}])[0].get(
                        "message", {}
                    ).get("content", "")

                    # Check if domain is mentioned in response
                    if domain.lower() in response_text.lower():
                        # Try to find position (rough estimate)
                        position = self._estimate_mention_position(
                            response_text, domain
                        )

                        # Extract context snippet
                        context = self._extract_context_snippet(
                            response_text, domain
                        )

                        return {
                            'platform': AIPlatform.CHATGPT.value,
                            'query': query,
                            'mentioned': True,
                            'position': position,
                            'context_snippet': context,
                            'checked_at': datetime.utcnow().isoformat()
                        }

                return None

        except httpx.HTTPError as e:
            logger.error(f"ChatGPT API error for query '{query}': {e}")
            return None

    async def _check_perplexity_search(
        self,
        query: str,
        domain: str,
        url: str
    ) -> Optional[Dict[str, Any]]:
        """
        Check Perplexity API for URL mentions

        Args:
            query: Search query
            domain: Domain to look for
            url: Full URL

        Returns:
            Mention dictionary if found, None otherwise
        """
        if not settings.perplexity_api_key:
            logger.warning("Perplexity API key not configured, skipping check")
            return None

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-sonar-large-128k-online",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Be precise and concise. Provide sources."
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.2,
                        "return_citations": True,
                        "search_domain_filter": []
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    # Check citations for domain
                    citations = data.get("citations", [])
                    for idx, citation in enumerate(citations):
                        if domain.lower() in citation.lower():
                            response_text = data.get("choices", [{}])[0].get(
                                "message", {}
                            ).get("content", "")

                            context = self._extract_context_snippet(
                                response_text, domain
                            )

                            return {
                                'platform': AIPlatform.PERPLEXITY.value,
                                'query': query,
                                'mentioned': True,
                                'position': idx + 1,
                                'context_snippet': context,
                                'citation_url': citation,
                                'checked_at': datetime.utcnow().isoformat()
                            }

                    # Also check response text even if not in citations
                    response_text = data.get("choices", [{}])[0].get(
                        "message", {}
                    ).get("content", "")

                    if domain.lower() in response_text.lower():
                        position = self._estimate_mention_position(
                            response_text, domain
                        )
                        context = self._extract_context_snippet(
                            response_text, domain
                        )

                        return {
                            'platform': AIPlatform.PERPLEXITY.value,
                            'query': query,
                            'mentioned': True,
                            'position': position,
                            'context_snippet': context,
                            'checked_at': datetime.utcnow().isoformat()
                        }

                return None

        except httpx.HTTPError as e:
            logger.error(f"Perplexity API error for query '{query}': {e}")
            return None

    def _estimate_mention_position(self, text: str, domain: str) -> int:
        """
        Estimate position of mention in response (1-10 scale)

        Args:
            text: Response text
            domain: Domain to find

        Returns:
            Position estimate (1 = early/top, 10 = late/bottom)
        """
        text_lower = text.lower()
        domain_lower = domain.lower()

        index = text_lower.find(domain_lower)
        if index == -1:
            return 10

        # Convert character position to 1-10 scale
        relative_position = index / len(text)
        position = int(relative_position * 10) + 1
        return min(position, 10)

    def _extract_context_snippet(
        self,
        text: str,
        domain: str,
        context_length: int = 200
    ) -> str:
        """
        Extract context snippet around domain mention

        Args:
            text: Full text
            domain: Domain to find
            context_length: Characters of context to extract

        Returns:
            Context snippet
        """
        text_lower = text.lower()
        domain_lower = domain.lower()

        index = text_lower.find(domain_lower)
        if index == -1:
            return ""

        # Extract context around mention
        start = max(0, index - context_length // 2)
        end = min(len(text), index + len(domain) + context_length // 2)

        snippet = text[start:end].strip()

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def _calculate_platform_score(self, mentions: List[Dict[str, Any]]) -> int:
        """
        Calculate visibility score for a specific platform

        Args:
            mentions: List of mentions on the platform

        Returns:
            Platform score (0-100)
        """
        if not mentions:
            return 0

        # Base score from number of mentions
        mention_score = min(len(mentions) * 15, 50)

        # Position bonus (earlier mentions = higher score)
        position_score = 0
        for mention in mentions:
            position = mention.get('position', 10)
            # Lower position number = higher score
            position_score += max(0, 10 - position)

        # Average position score
        if mentions:
            position_score = (position_score / len(mentions)) * 5

        # Citation bonus (if in citations, add extra points)
        citation_bonus = 0
        for mention in mentions:
            if 'citation_url' in mention:
                citation_bonus += 10

        total_score = mention_score + position_score + citation_bonus
        return min(int(total_score), 100)

    def get_visibility_score(self, mentions: List[Dict[str, Any]]) -> int:
        """
        Calculate overall visibility score based on mentions

        Args:
            mentions: List of all mentions across platforms

        Returns:
            Overall visibility score (0-100)
        """
        if not mentions:
            return 0

        # Group mentions by platform
        platform_mentions = {}
        for mention in mentions:
            platform = mention.get('platform', 'unknown')
            if platform not in platform_mentions:
                platform_mentions[platform] = []
            platform_mentions[platform].append(mention)

        # Calculate score for each platform
        platform_scores = []
        for platform, p_mentions in platform_mentions.items():
            score = self._calculate_platform_score(p_mentions)
            platform_scores.append(score)

        # Overall score is weighted average of platform scores
        if platform_scores:
            # Give bonus for being on multiple platforms
            multi_platform_bonus = min(len(platform_scores) * 5, 15)
            avg_score = sum(platform_scores) / len(platform_scores)
            total_score = avg_score + multi_platform_bonus
            return min(int(total_score), 100)

        return 0

    async def get_historical_visibility(
        self,
        website_id: str,
        supabase_client
    ) -> Dict[str, Any]:
        """
        Get historical visibility data for a website

        Args:
            website_id: Website ID
            supabase_client: Supabase client instance

        Returns:
            Historical visibility data
        """
        try:
            # Get all visibility checks for this website
            response = supabase_client.table("ai_mentions").select(
                "*"
            ).eq("website_id", website_id).order(
                "checked_at", desc=True
            ).limit(100).execute()

            checks = response.data if response.data else []

            if not checks:
                return {
                    'checks': [],
                    'average_score': 0,
                    'trend': 'stable',
                    'total_checks': 0
                }

            # Calculate average score
            scores = [check.get('visibility_score', 0) for check in checks]
            average_score = sum(scores) / len(scores) if scores else 0

            # Calculate trend (compare recent vs older)
            if len(checks) >= 6:
                recent_avg = sum(scores[:3]) / 3
                older_avg = sum(scores[-3:]) / 3
                if recent_avg > older_avg + 10:
                    trend = 'improving'
                elif recent_avg < older_avg - 10:
                    trend = 'declining'
                else:
                    trend = 'stable'
            else:
                trend = 'insufficient_data'

            return {
                'checks': checks[:20],  # Return last 20 checks
                'average_score': round(average_score, 1),
                'trend': trend,
                'total_checks': len(checks),
                'highest_score': max(scores) if scores else 0,
                'lowest_score': min(scores) if scores else 0,
                'last_checked': checks[0].get('checked_at') if checks else None
            }

        except Exception as e:
            logger.error(f"Error getting historical visibility: {e}")
            raise
