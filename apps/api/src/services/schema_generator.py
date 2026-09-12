"""
Schema Generation Service
Uses Claude API to scrape websites and generate AI-optimized schema markup
"""
import json
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
from anthropic import Anthropic
from bs4 import BeautifulSoup

from ..config import settings
from ..utils.url_validator import validate_url, SSRFProtectionError


class SchemaGeneratorService:
    """Service for generating schema.org JSON-LD markup using Claude AI"""

    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        self.model = "claude-3-5-sonnet-20241022"

    async def scrape_website(self, url: str) -> Dict[str, Any]:
        """
        Scrape website content including HTML, meta tags, and text

        Args:
            url: Website URL to scrape

        Returns:
            Dictionary with scraped content

        Raises:
            SSRFProtectionError: If URL fails security validation
            Exception: If scraping fails
        """
        # SECURITY: Validate URL to prevent SSRF attacks
        try:
            validated_url = validate_url(url, allow_private=False)
        except SSRFProtectionError as e:
            raise Exception(f"Invalid URL: {str(e)}")

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                # Use validated URL for the request
                response = await client.get(validated_url, headers={
                    'User-Agent': 'IAIndex Schema Generator Bot/1.0 (+https://iaindex.org/bot)'
                })
                response.raise_for_status()

                html = response.text
                soup = BeautifulSoup(html, 'html.parser')

                # Extract metadata
                title = soup.find('title')
                title_text = title.string if title else ""

                meta_description = soup.find('meta', attrs={'name': 'description'})
                description = meta_description.get('content', '') if meta_description else ""

                # Extract existing schema markup if present
                existing_schemas = []
                for script in soup.find_all('script', type='application/ld+json'):
                    try:
                        existing_schemas.append(json.loads(script.string))
                    except:
                        pass

                # Extract main content (remove nav, footer, scripts)
                for tag in soup(['nav', 'footer', 'script', 'style', 'header']):
                    tag.decompose()

                main_content = soup.get_text(separator=' ', strip=True)
                # Limit to first 5000 chars to keep within token limits
                main_content = main_content[:5000]

                # Extract images
                images = []
                for img in soup.find_all('img', src=True)[:5]:
                    images.append(img['src'])

                return {
                    'url': validated_url,  # Use validated URL
                    'title': title_text,
                    'description': description,
                    'main_content': main_content,
                    'existing_schemas': existing_schemas,
                    'images': images,
                    'scraped_at': datetime.utcnow().isoformat()
                }

        except httpx.HTTPError as e:
            raise Exception(f"Failed to scrape website: {str(e)}")

    async def generate_schema(
        self,
        url: str,
        business_type: Optional[str] = None,
        business_name: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI-optimized schema markup for a website

        Args:
            url: Website URL
            business_type: Type of business (e.g., 'Restaurant', 'LocalBusiness')
            business_name: Name of the business
            location: Location data (address, city, country, coordinates)

        Returns:
            Generated schema markup and metadata
        """
        # First scrape the website
        scraped_data = await self.scrape_website(url)

        # Build prompt for Claude
        prompt = self._build_schema_generation_prompt(
            scraped_data,
            business_type,
            business_name,
            location
        )

        # Call Claude API
        try:
            message = self.anthropic.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,
                system="""You are an expert in schema.org markup and SEO optimization for AI search engines.
Your task is to generate comprehensive, AI-optimized JSON-LD schema markup that maximizes visibility
in ChatGPT, Perplexity, Claude, and other AI search engines.

Focus on:
1. Complete and accurate schema properties
2. Rich structured data that AI can easily parse
3. Multiple schema types when appropriate (Organization, LocalBusiness, WebSite, etc.)
4. Proper nesting and relationships
5. Optimization for answer engine queries

Return ONLY valid JSON-LD markup, no explanations.""",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract JSON from response
            response_text = message.content[0].text
            schema_markup = self._extract_json_from_response(response_text)

            # Generate recommendations
            recommendations = await self._generate_recommendations(
                scraped_data,
                schema_markup
            )

            return {
                'schema_markup': schema_markup,
                'recommendations': recommendations,
                'scraped_data': {
                    'title': scraped_data['title'],
                    'description': scraped_data['description'],
                    'has_existing_schema': len(scraped_data['existing_schemas']) > 0
                },
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            raise Exception(f"Failed to generate schema: {str(e)}")

    def _build_schema_generation_prompt(
        self,
        scraped_data: Dict[str, Any],
        business_type: Optional[str],
        business_name: Optional[str],
        location: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for Claude schema generation"""

        prompt_parts = [
            "Generate comprehensive schema.org JSON-LD markup for the following website:",
            f"\nURL: {scraped_data['url']}",
            f"Title: {scraped_data['title']}",
            f"Description: {scraped_data['description']}",
        ]

        if business_name:
            prompt_parts.append(f"Business Name: {business_name}")

        if business_type:
            prompt_parts.append(f"Business Type: {business_type}")

        if location:
            prompt_parts.append(f"Location: {json.dumps(location)}")

        prompt_parts.append(f"\nWebsite Content:\n{scraped_data['main_content']}")

        if scraped_data['existing_schemas']:
            prompt_parts.append(
                f"\nExisting Schema (improve upon this):\n{json.dumps(scraped_data['existing_schemas'], indent=2)}"
            )

        prompt_parts.extend([
            "\nGenerate schema markup that:",
            "1. Uses appropriate schema.org types (Organization, LocalBusiness, Product, etc.)",
            "2. Includes all relevant properties (name, description, address, contactPoint, etc.)",
            "3. Is optimized for AI search engines to easily extract and cite",
            "4. Includes proper @context and @type fields",
            "5. Uses nested schemas where appropriate",
            "\nReturn ONLY the JSON-LD markup, properly formatted."
        ])

        return "\n".join(prompt_parts)

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Extract JSON from Claude's response"""
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find raw JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("No valid JSON found in response")

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in response: {str(e)}")

    async def _generate_recommendations(
        self,
        scraped_data: Dict[str, Any],
        schema_markup: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate optimization recommendations based on scraped data and schema

        Returns:
            List of recommendation objects
        """
        recommendations = []

        # Check for missing meta description
        if not scraped_data['description'] or len(scraped_data['description']) < 50:
            recommendations.append({
                'type': 'metadata',
                'priority': 'high',
                'title': 'Add or improve meta description',
                'description': 'Meta descriptions help AI search engines understand your page content',
                'action_items': [
                    'Write a compelling 150-160 character meta description',
                    'Include primary keywords naturally',
                    'Make it informative and actionable'
                ],
                'impact_score': 75
            })

        # Check for schema completeness
        if '@type' not in schema_markup:
            recommendations.append({
                'type': 'schema',
                'priority': 'critical',
                'title': 'Schema markup missing @type',
                'description': 'Schema must include a @type field',
                'action_items': ['Add appropriate @type field to schema'],
                'impact_score': 90
            })

        # Check for contact information in schema
        if 'contactPoint' not in schema_markup and 'telephone' not in schema_markup:
            recommendations.append({
                'type': 'schema',
                'priority': 'medium',
                'title': 'Add contact information to schema',
                'description': 'Contact information helps AI engines provide users with ways to reach you',
                'action_items': [
                    'Add contactPoint with telephone and email',
                    'Include contactType (customer service, sales, etc.)'
                ],
                'impact_score': 60
            })

        # Check for images in schema
        if 'image' not in schema_markup and scraped_data['images']:
            recommendations.append({
                'type': 'schema',
                'priority': 'medium',
                'title': 'Add images to schema markup',
                'description': 'Images increase visibility in AI search results',
                'action_items': [
                    'Add high-quality images to schema',
                    'Use proper image URLs',
                    'Include image alt text'
                ],
                'impact_score': 55
            })

        # Check for FAQ schema opportunity
        if 'FAQ' in scraped_data['main_content'].upper() or '?' in scraped_data['main_content']:
            if schema_markup.get('@type') != 'FAQPage':
                recommendations.append({
                    'type': 'schema',
                    'priority': 'high',
                    'title': 'Add FAQ schema markup',
                    'description': 'FAQ schema is highly visible in AI search results',
                    'action_items': [
                        'Create FAQPage schema',
                        'Include common questions and answers',
                        'Format with proper Question and Answer types'
                    ],
                    'impact_score': 80
                })

        return recommendations

    async def validate_schema(self, schema_markup: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate schema markup against schema.org standards

        Args:
            schema_markup: JSON-LD schema to validate

        Returns:
            Validation results with errors and warnings
        """
        errors = []
        warnings = []

        # Check required fields
        if '@context' not in schema_markup:
            errors.append("Missing required @context field")
        elif schema_markup['@context'] != 'https://schema.org':
            warnings.append("@context should be 'https://schema.org'")

        if '@type' not in schema_markup:
            errors.append("Missing required @type field")

        # Check for name field (required for most types)
        if 'name' not in schema_markup:
            warnings.append("Missing recommended 'name' field")

        # Check for description
        if 'description' not in schema_markup:
            warnings.append("Missing recommended 'description' field")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'score': max(0, 100 - (len(errors) * 25) - (len(warnings) * 5))
        }
