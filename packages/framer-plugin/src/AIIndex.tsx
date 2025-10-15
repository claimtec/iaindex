import * as React from "react"
import { addPropertyControls, ControlType } from "framer"

interface AIIndexProps {
  enabled: boolean
  publisherId: string
  siteName: string
  siteDescription: string
  webhookUrl: string
  autoGenerate: boolean
  customMetadata: string
}

/**
 * AI Index Component for Framer
 * Automatically generates and injects /ai-index.json for AI assistant discovery
 */
export default function AIIndex(props: AIIndexProps) {
  const {
    enabled,
    publisherId,
    siteName,
    siteDescription,
    webhookUrl,
    autoGenerate,
    customMetadata,
  } = props

  React.useEffect(() => {
    if (!enabled) return

    const generateAIIndex = async () => {
      try {
        // Get all pages from Framer site
        const pages = await fetchFramerPages()

        // Build AI Index structure
        const aiIndex = {
          version: "1.0",
          publisher: {
            id: publisherId || window.location.hostname,
            name: siteName || document.title,
            description: siteDescription || "",
            domain: window.location.hostname,
            type: "website",
            platform: "framer",
          },
          content: {
            pages: pages.map(page => ({
              id: page.id,
              title: page.title,
              description: page.description,
              url: page.url,
              path: page.path,
              published_at: page.publishedAt,
              metadata: page.metadata,
            })),
          },
          metadata: {
            generated_at: new Date().toISOString(),
            total_pages: pages.length,
            custom: customMetadata ? JSON.parse(customMetadata) : {},
          },
          access: {
            webhook_url: webhookUrl || `${window.location.origin}/api/aiindex/access`,
            verification_required: true,
          },
        }

        // Store in localStorage for access
        localStorage.setItem("ai-index", JSON.stringify(aiIndex))

        // Inject meta tag with reference
        injectMetaTag(aiIndex)

        // Post to webhook if configured
        if (autoGenerate && webhookUrl) {
          await postToWebhook(aiIndex)
        }
      } catch (error) {
        console.error("Error generating AI Index:", error)
      }
    }

    generateAIIndex()
  }, [enabled, publisherId, siteName, siteDescription, webhookUrl, autoGenerate, customMetadata])

  // Don't render anything visible
  return null
}

/**
 * Fetch all pages from Framer site
 */
async function fetchFramerPages() {
  // In Framer, we can access the site structure via the router
  const pages: any[] = []

  // Get all links from navigation
  const navLinks = document.querySelectorAll("a[href]")
  const uniqueUrls = new Set<string>()

  navLinks.forEach(link => {
    const href = link.getAttribute("href")
    if (href && href.startsWith("/")) {
      uniqueUrls.add(href)
    }
  })

  // Build page objects
  uniqueUrls.forEach(path => {
    const url = `${window.location.origin}${path}`

    pages.push({
      id: path.replace(/\//g, "-") || "home",
      title: extractTitleFromPath(path),
      description: "",
      url: url,
      path: path,
      publishedAt: new Date().toISOString(),
      metadata: {},
    })
  })

  // Add current page if not in list
  const currentPath = window.location.pathname
  if (!uniqueUrls.has(currentPath)) {
    pages.push({
      id: currentPath.replace(/\//g, "-") || "home",
      title: document.title,
      description: document.querySelector('meta[name="description"]')?.getAttribute("content") || "",
      url: window.location.href,
      path: currentPath,
      publishedAt: new Date().toISOString(),
      metadata: {},
    })
  }

  return pages
}

/**
 * Extract title from path
 */
function extractTitleFromPath(path: string): string {
  if (path === "/" || path === "") return "Home"

  return path
    .split("/")
    .filter(Boolean)
    .map(segment =>
      segment
        .split("-")
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    )
    .join(" - ")
}

/**
 * Inject meta tag with AI Index reference
 */
function injectMetaTag(aiIndex: any) {
  // Remove existing meta tag
  const existing = document.querySelector('meta[name="ai-index"]')
  if (existing) {
    existing.remove()
  }

  // Create new meta tag
  const meta = document.createElement("meta")
  meta.name = "ai-index"
  meta.content = JSON.stringify({
    url: `${window.location.origin}/ai-index.json`,
    version: aiIndex.version,
    publisher: aiIndex.publisher.id,
  })

  document.head.appendChild(meta)

  // Also create a script tag with the full index
  const existingScript = document.getElementById("ai-index-data")
  if (existingScript) {
    existingScript.remove()
  }

  const script = document.createElement("script")
  script.id = "ai-index-data"
  script.type = "application/json"
  script.textContent = JSON.stringify(aiIndex, null, 2)

  document.head.appendChild(script)
}

/**
 * Post AI Index to webhook
 */
async function postToWebhook(aiIndex: any) {
  try {
    const response = await fetch("/api/aiindex/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(aiIndex),
    })

    if (!response.ok) {
      console.error("Failed to post AI Index to webhook")
    }
  } catch (error) {
    console.error("Error posting to webhook:", error)
  }
}

// Property controls for Framer UI
addPropertyControls(AIIndex, {
  enabled: {
    type: ControlType.Boolean,
    title: "Enabled",
    defaultValue: true,
  },
  publisherId: {
    type: ControlType.String,
    title: "Publisher ID",
    placeholder: "your-site.com",
    description: "Unique identifier for your site",
  },
  siteName: {
    type: ControlType.String,
    title: "Site Name",
    placeholder: "My Awesome Site",
    description: "Your site's name",
  },
  siteDescription: {
    type: ControlType.String,
    title: "Description",
    placeholder: "A brief description of your site",
    displayTextArea: true,
  },
  webhookUrl: {
    type: ControlType.String,
    title: "Webhook URL",
    placeholder: "https://your-api.com/webhook",
    description: "URL to receive AI access notifications",
  },
  autoGenerate: {
    type: ControlType.Boolean,
    title: "Auto Generate",
    defaultValue: true,
    description: "Automatically generate on page load",
  },
  customMetadata: {
    type: ControlType.String,
    title: "Custom Metadata",
    placeholder: '{"key": "value"}',
    displayTextArea: true,
    description: "Additional metadata as JSON",
  },
})
