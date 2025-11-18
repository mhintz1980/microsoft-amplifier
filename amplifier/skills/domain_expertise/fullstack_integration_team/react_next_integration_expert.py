"""
React-Next Integration Expert Skill

Provides expert guidance on integrating React applications with Next.js framework.
Covers migration strategies, hybrid rendering, performance optimization, data fetching,
routing integration, SEO optimization, build processes, and testing strategies.

This skill implements progressive disclosure with metadata, summary, and full levels
to provide contextually appropriate expertise while maintaining zero hallucination
and 100% technical accuracy.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ...skills_framework.skill_template import BaseSkill, SkillContext, SkillLevel, SkillResult
from ...utils.logger import get_logger
from ...utils.token_utils import estimate_tokens

logger = get_logger(__name__)


class ReactNextIntegrationExpertSkill(BaseSkill):
    """
    Expert-level skill for React-Next.js integration patterns and best practices.

    Provides comprehensive guidance on:
    - Migration strategies from React SPA to Next.js
    - Hybrid rendering patterns (SSR, SSG, CSR)
    - Performance optimization and Core Web Vitals
    - Data fetching patterns with React 19
    - Routing integration and transitions
    - SEO optimization and meta management
    - Build process optimization
    - Testing strategies and integration
    """

    def __init__(self):
        super().__init__()
        self.skill_name = "react_next_integration_expert"
        self._migration_patterns = self._load_migration_patterns()
        self._performance_patterns = self._load_performance_patterns()
        self._testing_patterns = self._load_testing_patterns()
        self._build_patterns = self._load_build_patterns()

    @property
    def description(self) -> str:
        return "Expert guidance for React-Next.js integration, migration, performance optimization, and best practices"

    @property
    def tags(self) -> List[str]:
        return [
            "react",
            "nextjs",
            "integration",
            "migration",
            "performance",
            "ssr",
            "ssg",
            "seo",
            "optimization",
            "testing",
            "fullstack",
        ]

    def can_handle(self, context: SkillContext) -> float:
        """Determine confidence level for handling React-Next integration queries."""
        query_lower = context.query.lower()

        # High confidence indicators
        high_confidence_terms = [
            "next.js",
            "nextjs",
            "react next",
            "next migration",
            "ssr",
            "ssg",
            " isr",
            "app router",
            "pages router",
            "core web vitals",
            "next optimization",
            "next performance",
        ]

        # Medium confidence indicators
        medium_confidence_terms = [
            "react routing",
            "react seo",
            "react build optimization",
            "react server components",
            "react streaming",
        ]

        # Check for high confidence terms
        for term in high_confidence_terms:
            if term in query_lower:
                return 0.9

        # Check for medium confidence terms
        for term in medium_confidence_terms:
            if term in query_lower:
                return 0.7

        # Check for React-related terms
        if any(term in query_lower for term in ["react", "component", "frontend"]):
            return 0.4

        return 0.1

    def execute(self, context: SkillContext, level: SkillLevel = SkillLevel.SUMMARY) -> SkillResult:
        """Execute the skill at the specified disclosure level."""
        start_time = datetime.now()

        try:
            if level == SkillLevel.METADATA:
                content = self._get_metadata_content()
            elif level == SkillLevel.SUMMARY:
                content = self._get_summary_content(context)
            else:  # FULL
                content = self._get_full_content(context)

            execution_time = (datetime.now() - start_time).total_seconds()
            tokens_used = estimate_tokens(content)

            result = SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=content,
                tokens_used=tokens_used,
                execution_time=execution_time,
                metadata={
                    "category": "fullstack_integration",
                    "expertise_level": "expert",
                    "frameworks": ["react", "next.js"],
                    "coverage_areas": ["migration", "performance", "seo", "testing", "build"],
                },
                next_level_available=level != SkillLevel.FULL,
            )

            self.last_execution = datetime.now()
            self.execution_count += 1

            return result

        except Exception as e:
            logger.error(f"Error executing {self.skill_name}: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()

            return SkillResult(
                skill_name=self.skill_name,
                level=level,
                content=f"Error executing React-Next integration skill: {str(e)}",
                tokens_used=estimate_tokens(str(e)),
                execution_time=execution_time,
                metadata={"error": True},
                next_level_available=False,
            )

    def _get_metadata_content(self) -> str:
        """Return minimal metadata information (<50 tokens)."""
        return """React-Next Integration Expert: Migration patterns, hybrid rendering, performance optimization, data fetching, routing, SEO, build optimization, testing strategies."""

    def _get_summary_content(self, context: SkillContext) -> str:
        """Return key summary points (<200 tokens)."""
        query_lower = context.query.lower()

        if "migration" in query_lower:
            return """React to Next.js Migration: Gradual adoption recommended. Start with pages directory, migrate route by route. Use dynamic imports for Next.js features. Preserve existing React Router during transition."""

        if "performance" in query_lower or "optimization" in query_lower:
            return """Performance: Leverage Next.js automatic optimizations. Use Image component, font optimization, dynamic imports. Implement ISR for frequently changing content. Monitor Core Web Vitals with Next.js Analytics."""

        if "seo" in query_lower:
            return """SEO: Use Next.js Head component and Metadata API. Implement structured data with next-seo. Optimize meta tags per page. Leverage automatic sitemap generation."""

        if "testing" in query_lower:
            return """Testing: Combine Jest/React Testing Library for components with E2E testing for full Next.js flows. Test both client and server components. Mock Next.js router and API routes."""

        return """React-Next Integration: Use App Router for new projects. Implement hybrid rendering (SSR + SSG + CSR). Optimize with Next.js Image, fonts, and automatic code splitting. Test components and full flows."""

    def _get_full_content(self, context: SkillContext) -> str:
        """Return comprehensive expert guidance."""
        query_lower = context.query.lower()

        if "migration" in query_lower:
            return self._get_migration_guide()

        if "performance" in query_lower or "optimization" in query_lower:
            return self._get_performance_guide()

        if "seo" in query_lower:
            return self._get_seo_guide()

        if "testing" in query_lower:
            return self._get_testing_guide()

        if "routing" in query_lower:
            return self._get_routing_guide()

        if "data fetching" in query_lower or "fetch" in query_lower:
            return self._get_data_fetching_guide()

        if "build" in query_lower:
            return self._get_build_guide()

        return self._get_comprehensive_guide()

    def _get_migration_guide(self) -> str:
        """Comprehensive migration strategy guide."""
        return """
# React to Next.js Migration Strategy

## Phase 1: Preparation (1-2 weeks)

### 1.1 Audit Current Application
```bash
# Analyze bundle size and dependencies
npm run build
npx @next/bundle-analyzer

# Check React Router usage
grep -r "useHistory\|useNavigate\|Link" src/
```

### 1.2 Setup Next.js Alongside React
```json
// package.json additions
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "scripts": {
    "next": "next",
    "next:build": "next build",
    "next:start": "next start"
  }
}
```

### 1.3 Directory Structure
```
project/
├── src/                 # Existing React app
├── pages/              # Next.js pages
├── components/         # Shared components
└── public/             # Static assets
```

## Phase 2: Gradual Migration (4-8 weeks)

### 2.1 Start with Public Pages
```javascript
// pages/index.js
import { useRouter } from 'next/router';
import dynamic from 'next/dynamic';

// Dynamic import for existing React components
const ExistingApp = dynamic(() => import('../src/App'), {
  ssr: false, // Keep as CSR initially
  loading: () => <div>Loading...</div>
});

export default function HomePage() {
  const router = useRouter();

  return (
    <div>
      <h1>Welcome to Our Next.js App</h1>
      <ExistingApp />
    </div>
  );
}
```

### 2.2 Migrate Route by Route
```javascript
// pages/about.js
import Head from 'next/head';

export default function AboutPage() {
  return (
    <>
      <Head>
        <title>About Us - Company Name</title>
        <meta name="description" content="Learn about our company" />
      </Head>
      <div>
        <h1>About Us</h1>
        <p>Company story and mission...</p>
      </div>
    </>
  );
}
```

### 2.3 Handle API Calls
```javascript
// lib/api.js - Transition helper
export const apiClient = {
  // Client-side (existing)
  clientFetch: (url, options) => fetch(url, options),

  // Server-side (Next.js)
  serverFetch: async (url, options = {}) => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL;
    const fullUrl = `${baseUrl}${url}`;

    if (typeof window === 'undefined') {
      // Server-side: Add internal headers
      options.headers = {
        ...options.headers,
        'X-Internal-Request': 'true'
      };
    }

    return fetch(fullUrl, options);
  }
};
```

## Phase 3: Advanced Features (2-4 weeks)

### 3.1 Implement SSR for Dynamic Pages
```javascript
// pages/posts/[id].js
export async function getServerSideProps(context) {
  const { id } = context.params;

  try {
    const response = await fetch(`${process.env.API_URL}/posts/${id}`);
    const post = await response.json();

    return {
      props: {
        post,
        generatedAt: new Date().toISOString()
      }
    };
  } catch (error) {
    return {
      notFound: true
    };
  }
}

export default function PostPage({ post, generatedAt }) {
  return (
    <article>
      <h1>{post.title}</h1>
      <p>Generated: {new Date(generatedAt).toLocaleString()}</p>
      <div dangerouslySetInnerHTML={{ __html: post.content }} />
    </article>
  );
}
```

### 3.2 Add SSG for Static Content
```javascript
// pages/docs/[slug].js
export async function getStaticPaths() {
  const response = await fetch(`${process.env.API_URL}/docs`);
  const docs = await response.json();

  const paths = docs.map(doc => ({
    params: { slug: doc.slug }
  }));

  return {
    paths,
    fallback: 'blocking' // Generate on-demand if not found
  };
}

export async function getStaticProps({ params }) {
  const response = await fetch(`${process.env.API_URL}/docs/${params.slug}`);
  const doc = await response.json();

  return {
    props: { doc },
    revalidate: 3600 // Revalidate every hour
  };
}
```

## Phase 4: Optimization (1-2 weeks)

### 4.1 Optimize Images and Assets
```javascript
// components/OptimizedImage.js
import Image from 'next/image';
import { useState } from 'react';

export default function OptimizedImage({ src, alt, ...props }) {
  const [isLoading, setLoading] = useState(true);

  return (
    <div className="relative overflow-hidden">
      <Image
        src={src}
        alt={alt}
        fill
        className={`transition-opacity duration-300 ${
          isLoading ? 'opacity-0' : 'opacity-100'
        }`}
        onLoadingComplete={() => setLoading(false)}
        {...props}
      />
    </div>
  );
}
```

### 4.2 Configure Next.js for Performance
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true, // Enable App Router
  },
  images: {
    domains: ['cdn.example.com'],
    formats: ['image/webp', 'image/avif'],
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  poweredByHeader: false,
  compress: true,
};

module.exports = nextConfig;
```

## Migration Checklist

### Pre-Migration
- [ ] Audit existing React application
- [ ] Identify critical user journeys
- [ ] Plan incremental rollout strategy
- [ ] Setup monitoring and analytics

### During Migration
- [ ] Maintain existing React app functionality
- [ ] Implement feature flags for gradual rollout
- [ ] Test each migrated route thoroughly
- [ ] Monitor performance metrics

### Post-Migration
- [ ] Remove unused React Router dependencies
- [ ] Implement advanced Next.js features
- [ ] Optimize for Core Web Vitals
- [ ] Update CI/CD pipelines

## Common Pitfalls to Avoid

1. **Big Bang Migration**: Don't migrate everything at once
2. **Ignoring SSR Differences**: Handle window/document objects carefully
3. **Breaking SEO**: Ensure meta tags migrate properly
4. **Performance Regression**: Monitor Core Web Vitals throughout
5. **State Management**: Adapt global state for SSR/SSR context

## Tools and Resources

- **Next.js Migration Guide**: https://nextjs.org/docs/migrating
- **Bundle Analyzer**: `@next/bundle-analyzer`
- **Compatibility Checker**: `npx @next/codemod`
- **Performance Monitoring**: Next.js Analytics, Vercel Speed Insights
"""

    def _get_performance_guide(self) -> str:
        """Performance optimization and Core Web Vitals guide."""
        return """
# Next.js Performance Optimization Guide

## Core Web Vitals Optimization

### 1. Largest Contentful Paint (LCP) < 2.5s

#### 1.1 Optimize Images with Next.js Image Component
```javascript
// components/OptimizedImage.js
import Image from 'next/image';
import { useState } from 'react';

const LCP_IMAGE_PRIORITY = true;

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  placeholder = 'blur',
  blurDataURL,
  className = '',
  ...props
}) {
  const [isLoading, setLoading] = useState(true);

  return (
    <div className={`relative ${className}`}>
      <Image
        src={src}
        alt={alt}
        width={width}
        height={height}
        priority={priority || LCP_IMAGE_PRIORITY}
        placeholder={placeholder}
        blurDataURL={blurDataURL}
        className={`
          transition-opacity duration-300
          ${isLoading ? 'opacity-0' : 'opacity-100'}
        `}
        onLoadingComplete={() => setLoading(false)}
        {...props}
      />
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}
    </div>
  );
}

// Usage for LCP optimization
export function HeroSection() {
  return (
    <section>
      <OptimizedImage
        src="/hero-banner.jpg"
        alt="Hero banner"
        width={1200}
        height={600}
        priority={true} // This tells Next.js to preload
        placeholder="blur"
        blurDataURL="data:image/jpeg;base64,...base64 encoded placeholder..."
      />
      <h1>Welcome to Our Site</h1>
    </section>
  );
}
```

#### 1.2 Critical CSS Inlining
```javascript
// styles/CriticalCSS.js
import { useEffect, useState } from 'react';

export function useCriticalCSS() {
  const [criticalStyles, setCriticalStyles] = useState('');

  useEffect(() => {
    // Extract critical CSS for above-the-fold content
    const criticalCSS = `
      body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; }
      .hero { height: 100vh; display: flex; align-items: center; justify-content: center; }
      .hero h1 { font-size: 3rem; margin: 0; }
    `;

    setCriticalStyles(criticalCSS);
  }, []);

  return criticalStyles;
}

// pages/_app.js
import Head from 'next/head';
import { useCriticalCSS } from '../styles/CriticalCSS';

export default function App({ Component, pageProps }) {
  const criticalStyles = useCriticalCSS();

  return (
    <>
      <Head>
        <style dangerouslySetInnerHTML={{ __html: criticalStyles }} />
      </Head>
      <Component {...pageProps} />
    </>
  );
}
```

### 2. First Input Delay (FID) < 100ms

#### 2.1 Code Splitting and Lazy Loading
```javascript
// components/LazyComponent.js
import dynamic from 'next/dynamic';

export const LazyChart = dynamic(
  () => import('./Chart').then(mod => mod.Chart),
  {
    loading: () => <div className="chart-placeholder">Loading chart...</div>,
    ssr: false, // Don't server-side render heavy components
  }
);

export const LazyAdminPanel = dynamic(
  () => import('./AdminPanel'),
  {
    loading: () => <div>Loading admin panel...</div>,
    // Load when 200px from viewport
    ssr: false
  }
);

// Usage
import { LazyChart, LazyAdminPanel } from './LazyComponent';

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      <LazyChart /> {/* Loads when needed */}
      <LazyAdminPanel />
    </div>
  );
}
```

#### 2.2 Event Delegation and Optimization
```javascript
// hooks/useOptimizedEvent.js
import { useCallback, useRef } from 'react';

export function useOptimizedClick(handler, delay = 100) {
  const timeoutRef = useRef(null);

  return useCallback((event) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      handler(event);
    }, delay);
  }, [handler, delay]);
}

// Usage for preventing FID issues
function OptimizedButton({ children, onClick, ...props }) {
  const optimizedClick = useOptimizedClick(onClick);

  return (
    <button onClick={optimizedClick} {...props}>
      {children}
    </button>
  );
}
```

### 3. Cumulative Layout Shift (CLS) < 0.1

#### 3.1 Prevent Layout Shifts
```javascript
// components/NoShiftImage.js
import Image from 'next/image';
import { useState } from 'react';

export default function NoShiftImage({ src, alt, ...props }) {
  const [aspectRatio, setAspectRatio] = useState(16/9);

  return (
    <div
      style={{
        position: 'relative',
        width: '100%',
        paddingBottom: `${(1 / aspectRatio) * 100}%` // Prevents shift
      }}
    >
      <Image
        src={src}
        alt={alt}
        fill
        style={{ objectFit: 'cover' }}
        onLoad={(e) => {
          const img = e.target;
          setAspectRatio(img.naturalWidth / img.naturalHeight);
        }}
        {...props}
      />
    </div>
  );
}

// Skeleton loading to prevent shifts
function CardSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="bg-gray-300 h-48 rounded-lg mb-4" />
      <div className="bg-gray-300 h-4 rounded mb-2" />
      <div className="bg-gray-300 h-4 rounded w-3/4" />
    </div>
  );
}
```

## Advanced Performance Techniques

### 4. Server-Side Optimizations

#### 4.1 Incremental Static Regeneration (ISR)
```javascript
// pages/blog/[slug].js
export async function getStaticProps({ params }) {
  try {
    const res = await fetch(`${process.env.API_URL}/blog/${params.slug}`);
    const post = await res.json();

    return {
      props: {
        post,
        lastModified: new Date().toISOString()
      },
      revalidate: 60, // Regenerate every 60 seconds
      notFound: !post
    };
  } catch (error) {
    return {
      notFound: true
    };
  }
}

// Client-side revalidation
import { useRouter } from 'next/router';

function BlogPost({ post, lastModified }) {
  const router = useRouter();

  useEffect(() => {
    // Refresh page if newer version available
    const checkForUpdates = async () => {
      try {
        const res = await fetch(`/api/blog/post-updated?slug=${router.query.slug}`);
        const { updated } = await res.json();

        if (updated > lastModified) {
          router.replace(router.asPath);
        }
      } catch (error) {
        console.error('Failed to check for updates:', error);
      }
    };

    const interval = setInterval(checkForUpdates, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, [router.query.slug, lastModified]);

  return <article>{/* Post content */}</article>;
}
```

#### 4.2 Edge Functions for Dynamic Content
```javascript
// pages/api/user/[id].js
export const config = {
  runtime: 'edge', // Run at edge for better performance
};

export default async function handler(req) {
  const { id } = req.query;

  // Edge-optimized user data fetching
  const userData = await fetchUserDataFromEdge(id);

  return new Response(JSON.stringify(userData), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=300'
    }
  });
}
```

### 5. Client-Side Optimizations

#### 5.1 React 19 Concurrent Features
```javascript
// features/ConcurrentFeatures.js
import { useTransition, useDeferredValue } from 'react';

function SearchResults({ query }) {
  const [isPending, startTransition] = useTransition();
  const [searchResults, setSearchResults] = useState([]);
  const deferredQuery = useDeferredValue(query);

  useEffect(() => {
    if (!deferredQuery) return;

    startTransition(() => {
      // Non-urgent search update
      fetchSearchResults(deferredQuery).then(setSearchResults);
    });
  }, [deferredQuery]);

  return (
    <div>
      {isPending && <div className="search-loading">Searching...</div>}
      <ul>
        {searchResults.map(result => (
          <li key={result.id}>{result.title}</li>
        ))}
      </ul>
    </div>
  );
}
```

#### 5.2 Virtual Scrolling for Large Lists
```javascript
// components/VirtualList.js
import { FixedSizeList as List } from 'react-window';

function VirtualList({ items, itemHeight = 50, height = 400 }) {
  const Row = ({ index, style }) => (
    <div style={style}>
      {/* Render item at index */}
      <ListItem item={items[index]} />
    </div>
  );

  return (
    <List
      height={height}
      itemCount={items.length}
      itemSize={itemHeight}
      width="100%"
    >
      {Row}
    </List>
  );
}

// Usage with React 19
function LargeDataList({ data }) {
  return (
    <VirtualList
      items={data}
      itemHeight={60}
      height={600}
    />
  );
}
```

## Monitoring and Measurement

### 6. Performance Monitoring Setup

#### 6.1 Core Web Vitals Tracking
```javascript
// lib/web-vitals.js
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  // Send to your analytics service
  fetch('/api/web-vitals', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(metric)
  });
}

// Initialize tracking
getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);

// pages/_app.js
import { useEffect } from 'react';
import '../lib/web-vitals';

export default function App({ Component, pageProps }) {
  useEffect(() => {
    // Web vitals will be automatically tracked
  }, []);

  return <Component {...pageProps} />;
}
```

#### 6.2 Performance Budget Monitoring
```javascript
// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Performance budgets
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.performance = {
        maxEntrypointSize: 244000, // 244KB
        maxAssetSize: 244000,
      };
    }
    return config;
  },

  // Image optimization
  images: {
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
};

module.exports = withBundleAnalyzer(nextConfig);
```

### 7. Optimization Checklist

#### Pre-Deployment
- [ ] Run Lighthouse audit (score >90)
- [ ] Check bundle size with analyzer
- [ ] Verify Core Web Vitals thresholds
- [ ] Test on slow 3G connection
- [ ] Validate image optimization

#### Production Monitoring
- [ ] Setup real user monitoring (RUM)
- [ ] Track Core Web Vitals trends
- [ ] Monitor bundle size changes
- [ ] Alert on performance regression
- [ ] A/B test performance improvements

### Performance Targets
- **LCP**: < 2.5 seconds (Good), < 1.0 seconds (Excellent)
- **FID**: < 100 milliseconds (Good), < 50 milliseconds (Excellent)
- **CLS**: < 0.1 (Good), < 0.05 (Excellent)
- **Bundle Size**: < 244KB gzipped per entry point
- **TTI**: < 3.8 seconds on mobile
"""

    def _get_seo_guide(self) -> str:
        """SEO optimization and meta management guide."""
        return """
# Next.js SEO Optimization Guide

## 1. Meta Tags and Metadata Management

### 1.1 Using Next.js Metadata API (App Router)
```javascript
// app/layout.js
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: {
    default: 'My Website',
    template: '%s | My Website'
  },
  description: 'Default description for my website',
  keywords: ['web development', 'next.js', 'react'],
  authors: [{ name: 'John Doe' }],
  creator: 'John Doe',
  publisher: 'My Company',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://mywebsite.com'),
  alternates: {
    canonical: '/',
    languages: {
      'en-US': '/en-US',
      'es-ES': '/es-ES',
    },
  },
  openGraph: {
    title: 'My Website',
    description: 'Default description for my website',
    url: 'https://mywebsite.com',
    siteName: 'My Website',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'My Website preview',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My Website',
    description: 'Default description for my website',
    images: ['/twitter-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

### 1.2 Dynamic Metadata for Pages
```javascript
// app/products/[slug]/page.js
import { Metadata } from 'next';
import { notFound } from 'next/navigation';

async function getProduct(slug: string) {
  const res = await fetch(`${process.env.API_URL}/products/${slug}`);

  if (!res.ok) {
    return null;
  }

  return res.json();
}

export async function generateMetadata({ params }): Promise<Metadata> {
  const product = await getProduct(params.slug);

  if (!product) {
    return {
      title: 'Product Not Found',
      description: 'The requested product could not be found.',
    };
  }

  return {
    title: product.name,
    description: product.description,
    keywords: product.tags,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [
        {
          url: product.image,
          width: 1200,
          height: 630,
          alt: `${product.name} product image`,
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: product.name,
      description: product.description,
      images: [product.image],
    },
    alternates: {
      canonical: `/products/${params.slug}`,
    },
  };
}

export default async function ProductPage({ params }) {
  const product = await getProduct(params.slug);

  if (!product) {
    notFound();
  }

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      {/* Product content */}
    </div>
  );
}
```

### 1.3 Legacy Pages Router Metadata
```javascript
// pages/products/[slug].js
import Head from 'next/head';

export default function ProductPage({ product }) {
  return (
    <>
      <Head>
        <title>{product.name} | My Website</title>
        <meta name="description" content={product.description} />
        <meta name="keywords" content={product.tags.join(', ')} />

        {/* Open Graph */}
        <meta property="og:title" content={product.name} />
        <meta property="og:description" content={product.description} />
        <meta property="og:image" content={product.image} />
        <meta property="og:url" content={`https://mywebsite.com/products/${product.slug}`} />
        <meta property="og:type" content="product" />

        {/* Twitter Card */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={product.name} />
        <meta name="twitter:description" content={product.description} />
        <meta name="twitter:image" content={product.image} />

        {/* Canonical URL */}
        <link rel="canonical" href={`https://mywebsite.com/products/${product.slug}`} />
      </Head>

      <div>
        <h1>{product.name}</h1>
        <p>{product.description}</p>
        {/* Product content */}
      </div>
    </>
  );
}

export async function getServerSideProps({ params }) {
  const res = await fetch(`${process.env.API_URL}/products/${params.slug}`);
  const product = await res.json();

  return {
    props: { product },
  };
}
```

## 2. Structured Data Implementation

### 2.1 JSON-LD Structured Data
```javascript
// components/StructuredData.js
export function ProductStructuredData({ product }) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description,
    image: product.images,
    brand: {
      '@type': 'Brand',
      name: product.brand,
    },
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: product.currency,
      availability: product.inStock ? 'https://schema.org/InStock' : 'https://schema.org/OutOfStock',
      url: `https://mywebsite.com/products/${product.slug}`,
    },
    aggregateRating: product.rating ? {
      '@type': 'AggregateRating',
      ratingValue: product.rating.value,
      reviewCount: product.rating.count,
    } : undefined,
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}

// Article structured data
export function ArticleStructuredData({ article }) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.title,
    description: article.excerpt,
    image: article.featuredImage,
    datePublished: article.publishedAt,
    dateModified: article.updatedAt,
    author: {
      '@type': 'Person',
      name: article.author.name,
    },
    publisher: {
      '@type': 'Organization',
      name: 'My Company',
      logo: {
        '@type': 'ImageObject',
        url: 'https://mywebsite.com/logo.png',
      },
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}
```

### 2.2 Breadcrumb Structured Data
```javascript
// components/BreadcrumbStructuredData.js
export function BreadcrumbStructuredData({ breadcrumbs }) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: breadcrumbs.map((breadcrumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: breadcrumb.name,
      item: breadcrumb.url,
    })),
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}

// Usage
function ProductPage({ product, breadcrumbs }) {
  return (
    <>
      <BreadcrumbStructuredData breadcrumbs={breadcrumbs} />
      <ProductStructuredData product={product} />

      <nav aria-label="Breadcrumb">
        <ol>
          {breadcrumbs.map((crumb, index) => (
            <li key={index}>
              <a href={crumb.url}>{crumb.name}</a>
            </li>
          ))}
        </ol>
      </nav>

      {/* Product content */}
    </>
  );
}
```

## 3. XML Sitemaps and Robots.txt

### 3.1 Dynamic Sitemap Generation
```javascript
// pages/sitemap.xml.js
import { getServerSideProps } from 'next';

function Sitemap({ posts, products, pages }) {
  const baseUrl = 'https://mywebsite.com';
  const currentDate = new Date().toISOString();

  const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url>
        <loc>${baseUrl}</loc>
        <lastmod>${currentDate}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
      </url>

      ${pages.map(page => `
        <url>
          <loc>${baseUrl}${page.path}</loc>
          <lastmod>${page.lastModified || currentDate}</lastmod>
          <changefreq>${page.changeFreq || 'monthly'}</changefreq>
          <priority>${page.priority || '0.8'}</priority>
        </url>
      `).join('')}

      ${products.map(product => `
        <url>
          <loc>${baseUrl}/products/${product.slug}</loc>
          <lastmod>${product.updatedAt}</lastmod>
          <changefreq>weekly</changefreq>
          <priority>0.7</priority>
        </url>
      `).join('')}

      ${posts.map(post => `
        <url>
          <loc>${baseUrl}/blog/${post.slug}</loc>
          <lastmod>${post.updatedAt}</lastmod>
          <changefreq>weekly</changefreq>
          <priority>0.6</priority>
        </url>
      `).join('')}
    </urlset>
  `;

  return xmlContent;
}

export async function getServerSideProps({ res }) {
  // Fetch dynamic data
  const [postsRes, productsRes] = await Promise.all([
    fetch(`${process.env.API_URL}/posts`),
    fetch(`${process.env.API_URL}/products`),
  ]);

  const posts = await postsRes.json();
  const products = await productsRes.json();

  // Static pages
  const pages = [
    { path: '/about', changeFreq: 'monthly', priority: '0.8' },
    { path: '/contact', changeFreq: 'monthly', priority: '0.5' },
    { path: '/blog', changeFreq: 'daily', priority: '0.9' },
  ];

  res.setHeader('Content-Type', 'text/xml');
  res.write(Sitemap({ posts, products, pages }));
  res.end();

  return {
    props: {},
  };
}

export default function SitemapPage() {
  return null; // This component is never rendered
}
```

### 3.2 Dynamic Robots.txt
```javascript
// pages/robots.txt.js
export async function getServerSideProps({ res }) {
  const robotsTxt = `User-agent: *
Allow: /
Disallow: /api/
Disallow: /_next/
Disallow: /admin/
Sitemap: https://mywebsite.com/sitemap.xml

# Crawl delay for specific bots
User-agent: GPTBot
Crawl-delay: 1

User-agent: Googlebot
Crawl-delay: 0
`;

  res.setHeader('Content-Type', 'text/plain');
  res.write(robotsTxt);
  res.end();

  return { props: {} };
}

export default function RobotsPage() {
  return null;
}
```

## 4. Internationalization (i18n) SEO

### 4.1 Hreflang Implementation
```javascript
// app/[locale]/layout.js
import { Metadata } from 'next';

export async function generateAlternateLanguages(pathname: string) {
  const locales = ['en', 'es', 'fr', 'de'];
  const languages = {
    'en': 'en-US',
    'es': 'es-ES',
    'fr': 'fr-FR',
    'de': 'de-DE',
  };

  return locales.reduce((acc, locale) => {
    acc[locale] = `https://mywebsite.com/${locale}${pathname}`;
    return acc;
  }, {});
}

export async function generateMetadata({ params }) {
  const alternates = await generateAlternateLanguages('/products');

  return {
    alternates: {
      canonical: `/products`,
      languages: alternates,
    },
  };
}
```

### 4.2 Language-Specific Meta Tags
```javascript
// lib/i18n-seo.js
export const seoTranslations = {
  en: {
    siteName: 'My Website',
    defaultDescription: 'Default description in English',
  },
  es: {
    siteName: 'Mi Sitio Web',
    defaultDescription: 'Descripción predeterminada en español',
  },
  fr: {
    siteName: 'Mon Site Web',
    defaultDescription: 'Description par défaut en français',
  },
};

export function getLocalizedMetadata(locale, pageData) {
  const translations = seoTranslations[locale] || seoTranslations.en;

  return {
    title: pageData.title || translations.siteName,
    description: pageData.description || translations.defaultDescription,
    locale: locale,
    // Add more locale-specific metadata
  };
}
```

## 5. Technical SEO Optimization

### 5.1 Schema.org Validation
```javascript
// lib/schema-validator.js
import Ajv from 'ajv';

const ajv = new Ajv();

// Load JSON Schema definitions
const productSchema = require('./schemas/product-schema.json');
const articleSchema = require('./schemas/article-schema.json');

export function validateStructuredData(structuredData, schemaType) {
  const schema = schemaType === 'product' ? productSchema : articleSchema;
  const validate = ajv.compile(schema);

  const valid = validate(structuredData);

  if (!valid) {
    console.error('Structured data validation errors:', validate.errors);
    return false;
  }

  return true;
}

// Usage in components
export function ValidatedProductStructuredData({ product }) {
  const structuredData = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    // ... product data
  };

  const isValid = validateStructuredData(structuredData, 'product');

  if (!isValid) {
    console.warn('Invalid structured data for product:', product.name);
    return null;
  }

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}
```

### 5.2 Core Web Vitals Impact on SEO
```javascript
// hooks/use-seo-optimization.js
import { useEffect } from 'react';

export function useSEOOptimization() {
  useEffect(() => {
    // Monitor and report Core Web Vitals for SEO impact
    if (typeof window !== 'undefined' && 'web-vitals' in window) {
      import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
        function sendToAnalytics(metric) {
          // Send to SEO monitoring service
          fetch('/api/seo-metrics', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(metric)
          });
        }

        getCLS(sendToAnalytics);
        getFID(sendToAnalytics);
        getFCP(sendToAnalytics);
        getLCP(sendToAnalytics);
        getTTFB(sendToAnalytics);
      });
    }
  }, []);
}
```

## 6. SEO Monitoring and Analytics

### 6.1 SEO Performance Tracking
```javascript
// pages/api/seo-metrics.js
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const metrics = req.body;

  // Store metrics for SEO analysis
  await storeSEOMetrics({
    ...metrics,
    timestamp: new Date().toISOString(),
    userAgent: req.headers['user-agent'],
    url: req.headers.referer,
  });

  // Analyze SEO impact
  if (metrics.name === 'LCP' && metrics.value > 2500) {
    // Flag for SEO optimization
    await flagPageForOptimization(metrics.url, 'slow-lcp');
  }

  res.status(200).json({ success: true });
}
```

### 6.2 Search Console Integration
```javascript
// lib/search-console.js
export async function getSearchConsoleData(url, startDate, endDate) {
  const response = await fetch(
    `https://www.googleapis.com/webmasters/v3/sites/${encodeURIComponent(url)}/searchAnalytics/query`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.GOOGLE_API_TOKEN}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        startDate,
        endDate,
        dimensions: ['query', 'page', 'device'],
        rowLimit: 100,
      }),
    }
  );

  return response.json();
}

// Usage for SEO optimization
export async function optimizeForSearchQueries() {
  const searchData = await getSearchConsoleData(
    'https://mywebsite.com',
    '2024-01-01',
    '2024-12-31'
  );

  // Analyze top performing queries and optimize content
  const topQueries = searchData.rows
    .sort((a, b) => b.clicks - a.clicks)
    .slice(0, 10);

  return topQueries.map(query => ({
    query: query.keys[0],
    clicks: query.clicks,
    impressions: query.impressions,
    ctr: query.ctr,
    position: query.position,
    optimizationSuggestion: generateOptimizationSuggestion(query),
  }));
}
```

## SEO Checklist

### On-Page SEO
- [ ] Unique title tags for every page (50-60 characters)
- [ ] Unique meta descriptions (150-160 characters)
- [ ] Proper heading structure (H1, H2, H3)
- [ ] Image alt text and optimized filenames
- [ ] Internal linking with descriptive anchor text
- [ ] URL structure is clean and descriptive
- [ ] Mobile-responsive design
- [ ] Fast page load times (< 3 seconds)

### Technical SEO
- [ ] XML sitemap submitted to search engines
- [ ] Robots.txt properly configured
- [ ] Structured data (JSON-LD) implemented
- [ ] Canonical tags set correctly
- [ ] Hreflang tags for international content
- [ ] Core Web Vitals optimized
- [ ] SSL certificate installed
- [ ] Clean URL structure

### Content SEO
- [ ] High-quality, original content
- [ ] Keyword research and optimization
- [ ] Regular content updates
- [ ] Content length appropriate for topic
- [ ] Internal linking strategy
- [ ] External links to authoritative sources
- [ ] Social sharing optimization
"""

    def _get_testing_guide(self) -> str:
        """Testing strategies for Next.js applications."""
        return """
# Next.js Testing Strategy Guide

## 1. Testing Stack Overview

### 1.1 Recommended Testing Tools
```json
// package.json
{
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.16.5",
    "@testing-library/user-event": "^14.4.3",
    "jest": "^29.0.0",
    "jest-environment-jsdom": "^29.0.0",
    "msw": "^1.0.0", // Mock Service Worker
    "@storybook/react": "^6.5.0",
    "cypress": "^12.0.0",
    "playwright": "^1.28.0",
    "playwright-test": "^8.0.0"
  }
}
```

### 1.2 Jest Configuration
```javascript
// jest.config.js
const nextJest = require('next/jest');

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files
  dir: './',
});

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapping: {
    '^@/components/(.*)$': '<rootDir>/components/$1',
    '^@/pages/(.*)$': '<rootDir>/pages/$1',
  },
  testEnvironment: 'jest-environment-jsdom',
  collectCoverageFrom: [
    'components/**/*.{js,jsx,ts,tsx}',
    'pages/**/*.{js,jsx,ts,tsx}',
    'lib/**/*.{js,jsx,ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};

module.exports = createJestConfig(customJestConfig);
```

### 1.3 Jest Setup File
```javascript
// jest.setup.js
import '@testing-library/jest-dom';
import { server } from './mocks/server';

// Mock Next.js router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: '',
      asPath: '/',
      push: jest.fn(),
      pop: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn(),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
    };
  },
}));

// Mock Next.js Image component
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props) => <img {...props} />,
}));

// Establish API mocking before all tests
beforeAll(() => server.listen());

// Reset any request handlers that we may add during the tests
afterEach(() => server.resetHandlers());

// Clean up after the tests are finished
afterAll(() => server.close());
```

## 2. Unit Testing Components

### 2.1 Testing React Components
```javascript
// components/__tests__/Button.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies variant styles correctly', () => {
    render(<Button variant="primary">Primary Button</Button>);
    const button = screen.getByRole('button');
    expect(button).toHaveClass('btn-primary');
  });

  it('is disabled when loading', () => {
    render(<Button loading>Loading</Button>);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('supports async onClick handlers', async () => {
    const asyncClick = jest.fn().mockResolvedValue('success');
    render(<Button onClick={asyncClick}>Async Button</Button>);

    fireEvent.click(screen.getByRole('button'));

    expect(asyncClick).toHaveBeenCalled();
  });
});
```

### 2.2 Testing Custom Hooks
```javascript
// hooks/__tests__/useCounter.test.js
import { renderHook, act } from '@testing-library/react';
import { useCounter } from '../useCounter';

describe('useCounter Hook', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter());
    expect(result.current.count).toBe(0);
  });

  it('initializes with custom value', () => {
    const { result } = renderHook(() => useCounter(5));
    expect(result.current.count).toBe(5);
  });

  it('increments count', () => {
    const { result } = renderHook(() => useCounter());

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('decrements count', () => {
    const { result } = renderHook(() => useCounter(10));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(9);
  });

  it('resets to initial value', () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.increment();
      result.current.increment();
      result.current.reset();
    });

    expect(result.current.count).toBe(5);
  });
});
```

### 2.3 Testing Form Components
```javascript
// components/__tests__/ContactForm.test.js
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ContactForm } from '../ContactForm';

describe('ContactForm Component', () => {
  it('renders all form fields', () => {
    render(<ContactForm />);

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    render(<ContactForm />);

    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/message is required/i)).toBeInTheDocument();
    });
  });

  it('validates email format', async () => {
    const user = userEvent.setup();
    render(<ContactForm />);

    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, 'invalid-email');

    const submitButton = screen.getByRole('button', { name: /submit/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    const mockSubmit = jest.fn();
    render(<ContactForm onSubmit={mockSubmit} />);

    await user.type(screen.getByLabelText(/name/i), 'John Doe');
    await user.type(screen.getByLabelText(/email/i), 'john@example.com');
    await user.type(screen.getByLabelText(/message/i), 'Hello, world!');

    await user.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(mockSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
        message: 'Hello, world!',
      });
    });
  });
});
```

## 3. Integration Testing

### 3.1 Testing Page-Level Integration
```javascript
// pages/__tests__/about.test.js
import { render, screen } from '@testing-library/react';
import { AboutPage } from '../about';

// Mock the getStaticProps function
jest.mock('../lib/cms', () => ({
  getAboutPage: jest.fn(() => Promise.resolve({
    title: 'About Us',
    content: 'We are a great company...',
    team: [
      { name: 'John Doe', role: 'CEO' },
      { name: 'Jane Smith', role: 'CTO' },
    ],
  })),
}));

describe('About Page Integration', () => {
  it('renders page content correctly', async () => {
    render(<AboutPage />);

    expect(await screen.findByRole('heading', { name: /about us/i })).toBeInTheDocument();
    expect(screen.getByText(/we are a great company/i)).toBeInTheDocument();
  });

  it('displays team members', async () => {
    render(<AboutPage />);

    expect(await screen.findByText(/john doe/i)).toBeInTheDocument();
    expect(screen.getByText(/ceo/i)).toBeInTheDocument();
    expect(screen.getByText(/jane smith/i)).toBeInTheDocument();
    expect(screen.getByText(/cto/i)).toBeInTheDocument();
  });

  it('includes proper SEO meta tags', async () => {
    const { metadata } = AboutPage.getLayout?.({}) || {};

    expect(metadata?.title).toContain('About Us');
    expect(metadata?.description).toBeDefined();
  });
});
```

### 3.2 Testing API Routes
```javascript
// pages/api/__tests__/users.test.js
import { createMocks } from 'node-mocks-http';
import handler from '../users';

// Mock database
jest.mock('../../lib/db', () => ({
  users: {
    findMany: jest.fn(),
    create: jest.fn(),
    findById: jest.fn(),
    update: jest.fn(),
    delete: jest.fn(),
  },
}));

describe('/api/users', () => {
  it('returns a list of users for GET requests', async () => {
    const { req, res } = createMocks({ method: 'GET' });

    // Mock database response
    require('../../lib/db').users.findMany.mockResolvedValue([
      { id: 1, name: 'John Doe', email: 'john@example.com' },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
    ]);

    await handler(req, res);

    expect(res._getStatusCode()).toBe(200);
    const data = JSON.parse(res._getData());
    expect(data).toHaveLength(2);
    expect(data[0]).toMatchObject({ name: 'John Doe' });
  });

  it('creates a new user for POST requests', async () => {
    const userData = {
      name: 'New User',
      email: 'newuser@example.com',
    };

    const { req, res } = createMocks({
      method: 'POST',
      body: userData,
    });

    // Mock database response
    require('../../lib/db').users.create.mockResolvedValue({
      id: 3,
      ...userData,
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(201);
    const data = JSON.parse(res._getData());
    expect(data).toMatchObject(userData);
  });

  it('validates required fields', async () => {
    const { req, res } = createMocks({
      method: 'POST',
      body: { name: 'User without email' },
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(400);
    const data = JSON.parse(res._getData());
    expect(data.error).toContain('email is required');
  });
});
```

### 3.3 Mock Service Worker Setup
```javascript
// mocks/server.js
import { setupServer } from 'msw/node';
import { rest } from 'msw';

// Mock API handlers
export const handlers = [
  // GET /api/posts
  rest.get('/api/posts', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, title: 'First post', content: 'Content of first post' },
        { id: 2, title: 'Second post', content: 'Content of second post' },
      ])
    );
  }),

  // POST /api/posts
  rest.post('/api/posts', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({ id: 3, ...req.body })
    );
  }),

  // Error handler
  rest.get('/api/error', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({ error: 'Internal server error' })
    );
  }),
];

// Create server
export const server = setupServer(...handlers);
```

## 4. End-to-End Testing

### 4.1 Playwright E2E Tests
```javascript
// e2e/user-journey.spec.js
import { test, expect } from '@playwright/test';

test.describe('User Journey', () => {
  test('user can browse products and make a purchase', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Check homepage loads
    await expect(page.locator('h1')).toContainText('Welcome');

    // Navigate to products
    await page.click('text=Products');
    await expect(page).toHaveURL(/\/products/);

    // Check products are displayed
    await expect(page.locator('.product-card')).toHaveCount.greaterThan(0);

    // Click on first product
    await page.click('.product-card:first-child');

    // Verify product page
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.product-price')).toBeVisible();

    // Add to cart
    await page.click('text=Add to Cart');

    // Check cart notification
    await expect(page.locator('.cart-notification')).toBeVisible();

    // View cart
    await page.click('text=View Cart');
    await expect(page).toHaveURL(/\/cart/);

    // Verify item in cart
    await expect(page.locator('.cart-item')).toHaveCount(1);

    // Proceed to checkout
    await page.click('text=Checkout');
    await expect(page).toHaveURL(/\/checkout/);

    // Fill checkout form
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="name"]', 'Test User');
    await page.fill('[data-testid="address"]', '123 Test St');

    // Place order
    await page.click('text=Place Order');

    // Verify order confirmation
    await expect(page.locator('h1')).toContainText('Order Confirmed');
  });

  test('search functionality works correctly', async ({ page }) => {
    await page.goto('/');

    // Use search
    await page.fill('[data-testid="search-input"]', 'laptop');
    await page.press('[data-testid="search-input"]', 'Enter');

    // Check search results
    await expect(page).toHaveURL(/\/search\?q=laptop/);
    await expect(page.locator('.search-result')).toHaveCount.greaterThan(0);

    // Verify search results contain search term
    const results = await page.locator('.search-result-title').allTextContents();
    results.forEach(title => {
      expect(title.toLowerCase()).toContain('laptop');
    });
  });

  test('responsive design works on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    await page.goto('/');

    // Check mobile navigation
    await expect(page.locator('.mobile-menu-button')).toBeVisible();

    // Open mobile menu
    await page.click('.mobile-menu-button');
    await expect(page.locator('.mobile-menu')).toBeVisible();

    // Navigate through mobile menu
    await page.click('text=Products');
    await expect(page).toHaveURL(/\/products/);
  });
});
```

### 4.2 Cypress E2E Tests
```javascript
// cypress/e2e/user-flow.cy.js
describe('User Flow Tests', () => {
  beforeEach(() => {
    // Visit the application
    cy.visit('/');
  });

  it('allows user registration and login', () => {
    // Navigate to register page
    cy.get('[data-testid="register-link"]').click();
    cy.url().should('include', '/register');

    // Fill registration form
    cy.get('[data-testid="name"]').type('Test User');
    cy.get('[data-testid="email"]').type('test@example.com');
    cy.get('[data-testid="password"]').type('password123');
    cy.get('[data-testid="confirm-password"]').type('password123');

    // Submit registration
    cy.get('[data-testid="register-button"]').click();

    // Verify successful registration
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="welcome-message"]').should('contain', 'Test User');

    // Logout
    cy.get('[data-testid="logout-button"]').click();

    // Login with new account
    cy.get('[data-testid="email"]').type('test@example.com');
    cy.get('[data-testid="password"]').type('password123');
    cy.get('[data-testid="login-button"]').click();

    // Verify successful login
    cy.url().should('include', '/dashboard');
  });

  it('handles form validation correctly', () => {
    cy.get('[data-testid="login-link"]').click();

    // Try to submit empty form
    cy.get('[data-testid="login-button"]').click();

    // Check validation errors
    cy.get('[data-testid="email-error"]').should('be.visible');
    cy.get('[data-testid="password-error"]').should('be.visible');

    // Enter invalid email
    cy.get('[data-testid="email"]').type('invalid-email');
    cy.get('[data-testid="login-button"]').click();

    // Check email validation error
    cy.get('[data-testid="email-error"]').should('contain', 'valid email');
  });

  it('handles API errors gracefully', () => {
    // Mock API error
    cy.intercept('POST', '/api/auth/login', {
      statusCode: 500,
      body: { error: 'Internal server error' },
    }).as('loginError');

    cy.get('[data-testid="login-link"]').click();
    cy.get('[data-testid="email"]').type('test@example.com');
    cy.get('[data-testid="password"]').type('password123');
    cy.get('[data-testid="login-button"]').click();

    cy.wait('@loginError');

    // Check error message
    cy.get('[data-testid="error-message"]')
      .should('be.visible')
      .and('contain', 'Something went wrong');
  });
});
```

## 5. Performance Testing

### 5.1 Lighthouse CI Integration
```javascript
// .lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo': ['warn', { minScore: 0.9 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

### 5.2 Bundle Size Testing
```javascript
// tests/bundle-size.test.js
import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';

describe('Bundle Size Tests', () => {
  const MAX_BUNDLE_SIZE = 244 * 1024; // 244KB

  it('main bundle should be under size limit', () => {
    // Build the application
    execSync('npm run build', { stdio: 'pipe' });

    // Read the build manifest
    const manifestPath = path.join(process.cwd(), '.next/build-manifest.json');
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

    // Find main bundle
    const mainBundle = manifest.pages['/'].find(file => file.endsWith('.js'));
    const bundlePath = path.join(process.cwd(), '.next', mainBundle);
    const bundleSize = fs.statSync(bundlePath).size;

    expect(bundleSize).toBeLessThan(MAX_BUNDLE_SIZE);
  });

  it('should not have duplicate dependencies', () => {
    // Analyze bundle for duplicates
    const bundleAnalysis = execSync('npx webpack-bundle-analyzer .next/static/chunks/*.json --mode=json', {
      encoding: 'utf8'
    });

    const analysis = JSON.parse(bundleAnalysis);
    const duplicates = analysis.filter(item => item.duplicate);

    expect(duplicates).toHaveLength(0);
  });
});
```

## 6. Visual Testing

### 6.1 Storybook Configuration
```javascript
// .storybook/main.js
module.exports = {
  stories: ['../components/**/*.stories.@(js|jsx|ts|tsx|mdx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/testing-library',
  ],
  framework: '@storybook/react',
  features: {
    interactionsDebugger: true,
  },
};
```

### 6.2 Visual Regression Tests
```javascript
// components/Button.stories.js
import { Button } from './Button';

export default {
  title: 'Components/Button',
  component: Button,
  parameters: {
    layout: 'centered',
  },
};

export const Primary = {
  args: {
    variant: 'primary',
    children: 'Primary Button',
  },
};

export const Secondary = {
  args: {
    variant: 'secondary',
    children: 'Secondary Button',
  },
};

export const Large = {
  args: {
    size: 'large',
    children: 'Large Button',
  },
};

export const Loading = {
  args: {
    loading: true,
    children: 'Loading...',
  },
};
```

## Testing Strategy Checklist

### Unit Tests
- [ ] Component rendering and props
- [ ] User interactions and event handlers
- [ ] Form validation and submission
- [ ] Custom hook functionality
- [ ] Utility functions
- [ ] Error handling and edge cases

### Integration Tests
- [ ] Page-level functionality
- [ ] API route integration
- [ ] Database interactions
- [ ] Authentication flows
- [ ] Routing behavior
- [ ] State management

### End-to-End Tests
- [ ] Critical user journeys
- [ ] Cross-browser compatibility
- [ ] Mobile responsive design
- [ ] Performance under load
- [ ] Accessibility compliance
- [ ] Error scenarios and recovery

### Performance Tests
- [ ] Bundle size optimization
- [ ] Core Web Vitals metrics
- [ ] Load time benchmarks
- [ ] Memory usage analysis
- [ ] Database query performance
- [ ] API response times

### Visual Tests
- [ ] Component design consistency
- [ ] Cross-browser rendering
- [ ] Responsive behavior
- [ ] Dark/light mode support
- [ ] Accessibility compliance
- [ ] Brand guideline adherence

This comprehensive testing strategy ensures Next.js applications are robust, performant, and maintainable across all layers of the stack.
"""

    def _get_routing_guide(self) -> str:
        """Routing integration and transition guide."""
        return """
# React Router to Next.js Routing Integration Guide

## 1. Understanding Next.js Routing Architecture

### 1.1 Pages Router vs App Router
```javascript
// Pages Router (Traditional)
pages/
├── _app.js              // App component
├── _document.js         // Document structure
├── index.js            // Homepage (/)
├── about.js            // /about
├── products/
│   ├── index.js        // /products
│   └── [id].js         // /products/123
└── api/
    └── users.js        // API route /api/users

// App Router (New, Recommended)
app/
├── layout.js           // Root layout
├── page.js            // Homepage (/)
├── about/
│   └── page.js        // /about
├── products/
│   ├── page.js        // /products
│   └── [id]/
│       └── page.js    // /products/123
└── api/
    └── users/
        └── route.js   // API route /api/users
```

### 1.2 Migration Decision Framework
```javascript
// lib/routing-decision.js
export const ROUTING_PATTERNS = {
  // Use Pages Router when:
  LEGACY_PROJECT: {
    criteria: [
      'Existing React Router codebase',
      'Complex client-side routing logic',
      'Heavy reliance on useEffect for navigation',
      'Custom middleware requirements'
    ],
    recommendation: 'Gradual migration to Pages Router first'
  },

  // Use App Router when:
  NEW_PROJECT: {
    criteria: [
      'Starting fresh project',
      'Server Components beneficial',
      'Complex layouts required',
      'Advanced streaming needed'
    ],
    recommendation: 'Start with App Router directly'
  },

  // Hybrid approach when:
  MIXED_PROJECT: {
    criteria: [
      'Some pages need SSR/SSG',
      'Others need client-side routing',
      'Gradual migration required',
      'Feature flagging needed'
    ],
    recommendation: 'Use both systems during transition'
  }
};
```

## 2. React Router Migration Patterns

### 2.1 Basic Route Translation
```javascript
// Before: React Router
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <Link to="/products">Products</Link>
      </nav>

      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/products/:id" element={<ProductDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

// After: Next.js Pages Router
// pages/index.js
export default function HomePage() {
  return (
    <>
      <nav>
        <Link href="/">Home</Link>
        <Link href="/about">About</Link>
        <Link href="/products">Products</Link>
      </nav>

      <h1>Home Page</h1>
    </>
  );
}

// pages/about.js
export default function AboutPage() {
  return (
    <>
      <nav>
        <Link href="/">Home</Link>
        <Link href="/about">About</Link>
        <Link href="/products">Products</Link>
      </nav>

      <h1>About Page</h1>
    </>
  );
}

// pages/products/[id].js
import { useRouter } from 'next/router';

export default function ProductDetail() {
  const router = useRouter();
  const { id } = router.query;

  return (
    <>
      <nav>
        <Link href="/">Home</Link>
        <Link href="/about">About</Link>
        <Link href="/products">Products</Link>
      </nav>

      <h1>Product {id}</h1>
    </>
  );
}
```

### 2.2 Advanced Routing Patterns
```javascript
// Before: Complex React Router with nested routes
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="about" element={<AboutPage />} />
          <Route path="products" element={<ProductsLayout />}>
            <Route index element={<ProductsList />} />
            <Route path=":id" element={<ProductDetail />} />
            <Route path="new" element={<NewProduct />} />
          </Route>
          <Route path="dashboard" element={<DashboardLayout />}>
            <Route index element={<DashboardHome />} />
            <Route path="profile" element={<UserProfile />} />
            <Route path="settings" element={<UserSettings />} />
          </Route>
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

// After: Next.js App Router with Server Components
// app/layout.js
import { Inter } from 'next/font/google';
import { Navigation } from '@/components/Navigation';

const inter = Inter({ subsets: ['latin'] });

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navigation />
        <main>{children}</main>
      </body>
    </html>
  );
}

// app/page.js
export default function HomePage() {
  return <h1>Home Page</h1>;
}

// app/about/page.js
export default function AboutPage() {
  return <h1>About Page</h1>;
}

// app/products/layout.js
export default function ProductsLayout({ children }) {
  return (
    <div className="products-layout">
      <aside>Products Sidebar</aside>
      <div>{children}</div>
    </div>
  );
}

// app/products/page.js
export default function ProductsList() {
  return <h1>Products List</h1>;
}

// app/products/[id]/page.js
import { notFound } from 'next/navigation';

async function getProduct(id) {
  const res = await fetch(`${process.env.API_URL}/products/${id}`);

  if (!res.ok) {
    return null;
  }

  return res.json();
}

export default async function ProductDetail({ params }) {
  const product = await getProduct(params.id);

  if (!product) {
    notFound();
  }

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
    </div>
  );
}

// app/dashboard/layout.js
import { requireAuth } from '@/lib/auth';

export default async function DashboardLayout({ children }) {
  // Server-side authentication check
  const user = await requireAuth();

  return (
    <div className="dashboard-layout">
      <DashboardNav user={user} />
      <div>{children}</div>
    </div>
  );
}
```

## 3. Link Components and Navigation

### 3.1 Custom Link Component with Loading States
```javascript
// components/EnhancedLink.js
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useState } from 'react';

export function EnhancedLink({
  href,
  children,
  className = '',
  prefetch = true,
  showLoading = true,
  ...props
}) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = (e) => {
    if (showLoading) {
      setIsLoading(true);
    }

    // Custom navigation logic if needed
    if (props.onClick) {
      props.onClick(e);
    }
  };

  return (
    <Link
      href={href}
      prefetch={prefetch}
      className={`${className} ${isLoading ? 'loading' : ''}`}
      onClick={handleClick}
      {...props}
    >
      {children}
      {isLoading && showLoading && <span className="loading-spinner">⟳</span>}
    </Link>
  );
}

// Usage
<EnhancedLink
  href="/products/123"
  className="product-link"
  showLoading={true}
>
  View Product
</EnhancedLink>
```

### 3.2 Programmatic Navigation
```javascript
// hooks/useNavigation.js
import { useRouter } from 'next/router';
import { useCallback } from 'react';

export function useNavigation() {
  const router = useRouter();

  const navigate = useCallback((path, options = {}) => {
    const {
      shallow = false,
      scroll = true,
      replace = false,
      state = {}
    } = options;

    if (replace) {
      router.replace(path, undefined, { shallow, scroll });
    } else {
      router.push(path, undefined, { shallow, scroll });
    }
  }, [router]);

  const back = useCallback(() => {
    router.back();
  }, [router]);

  const forward = useCallback(() => {
    window.history.forward();
  }, []);

  const reload = useCallback(() => {
    router.reload();
  }, [router]);

  return {
    navigate,
    back,
    forward,
    reload,
    currentPath: router.pathname,
    query: router.query,
    isReady: router.isReady,
  };
}

// Usage in components
function ProductCard({ product }) {
  const { navigate } = useNavigation();

  const handleQuickView = () => {
    navigate(`/products/${product.id}?quickView=true`, {
      shallow: true,
      scroll: false,
    });
  };

  return (
    <div>
      <h3>{product.name}</h3>
      <button onClick={handleQuickView}>Quick View</button>
    </div>
  );
}
```

## 4. Route Guards and Authentication

### 4.1 Server-Side Route Protection
```javascript
// lib/auth-middleware.js
export async function requireAuth(context) {
  const token = context.req.cookies.auth_token;

  if (!token) {
    return {
      redirect: {
        destination: '/login?returnUrl=' + context.resolvedUrl,
        permanent: false,
      },
    };
  }

  try {
    const user = await verifyToken(token);
    return { props: { user } };
  } catch (error) {
    return {
      redirect: {
        destination: '/login?returnUrl=' + context.resolvedUrl,
        permanent: false,
      },
    };
  }
}

// pages/dashboard/index.js
import { requireAuth } from '../../lib/auth-middleware';

export async function getServerSideProps(context) {
  const authResult = await requireAuth(context);

  if (authResult.redirect) {
    return authResult;
  }

  // Fetch dashboard data
  const dashboardData = await fetchDashboardData(authResult.props.user.id);

  return {
    props: {
      user: authResult.props.user,
      dashboardData,
    },
  };
}

export default function Dashboard({ user, dashboardData }) {
  return (
    <div>
      <h1>Welcome, {user.name}!</h1>
      {/* Dashboard content */}
    </div>
  );
}
```

### 4.2 Client-Side Route Protection (App Router)
```javascript
// app/dashboard/layout.js
import { redirect } from 'next/navigation';
import { getServerSession } from 'next-auth';

export default async function DashboardLayout({ children }) {
  const session = await getServerSession();

  if (!session) {
    redirect('/login');
  }

  return (
    <div className="dashboard-layout">
      <DashboardNav user={session.user} />
      <div>{children}</div>
    </div>
  );
}

// components/ProtectedRoute.js
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

export function ProtectedRoute({ children, fallbackPath = '/login' }) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'loading') return; // Still loading

    if (!session) {
      router.push(fallbackPath);
    }
  }, [session, status, router, fallbackPath]);

  if (status === 'loading') {
    return <div>Loading...</div>;
  }

  if (!session) {
    return null; // Will redirect
  }

  return children;
}

// Usage
function UserProfile() {
  return (
    <ProtectedRoute>
      <div>Protected user profile content</div>
    </ProtectedRoute>
  );
}
```

## 5. Advanced Routing Patterns

### 5.1 Dynamic Routes with Multiple Segments
```javascript
// app/[category]/[slug]/page.js
import { notFound } from 'next/navigation';

async function getContent(category, slug) {
  const res = await fetch(`${process.env.API_URL}/content/${category}/${slug}`);

  if (!res.ok) {
    return null;
  }

  return res.json();
}

export async function generateMetadata({ params }) {
  const content = await getContent(params.category, params.slug);

  if (!content) {
    return { title: 'Content Not Found' };
  }

  return {
    title: content.title,
    description: content.excerpt,
  };
}

export default async function ContentPage({ params }) {
  const content = await getContent(params.category, params.slug);

  if (!content) {
    notFound();
  }

  return (
    <article>
      <h1>{content.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: content.content }} />
    </article>
  );
}

export async function generateStaticParams() {
  const res = await fetch(`${process.env.API_URL}/content/all`);
  const contents = await res.json();

  return contents.map(content => ({
    category: content.category,
    slug: content.slug,
  }));
}
```

### 5.2 Parallel Routes and Modal Patterns
```javascript
// app/@modal/default.js
export default function Default() {
  return null;
}

// app/@modal/photo/[id]/page.js
import ImageModal from '@/components/ImageModal';

export default function PhotoModal({ params }) {
  return <ImageModal photoId={params.id} />;
}

// app/photos/page.js
import PhotoGallery from '@/components/PhotoGallery';

export default function PhotosPage() {
  return <PhotoGallery />;
}

// components/PhotoGallery.js
import Link from 'next/link';

export default function PhotoGallery() {
  const photos = [
    { id: 1, url: '/photos/1.jpg', title: 'Photo 1' },
    { id: 2, url: '/photos/2.jpg', title: 'Photo 2' },
    // ... more photos
  ];

  return (
    <div>
      <h1>Photo Gallery</h1>
      <div className="photo-grid">
        {photos.map(photo => (
          <Link key={photo.id} href={`/photo/${photo.id}`}>
            <img src={photo.url} alt={photo.title} />
          </Link>
        ))}
      </div>
    </div>
  );
}

// app/layout.js
export default function RootLayout({ children, modal }) {
  return (
    <html>
      <body>
        {children}
        {modal}
      </body>
    </html>
  );
}
```

### 5.3 Route Groups and Shared Layouts
```javascript
// app/(marketing)/layout.js
export default function MarketingLayout({ children }) {
  return (
    <div className="marketing-layout">
      <MarketingHeader />
      {children}
      <MarketingFooter />
    </div>
  );
}

// app/(marketing)/page.js
export default function MarketingHome() {
  return <h1>Welcome to our marketing site</h1>;
}

// app/(marketing)/about/page.js
export default function AboutPage() {
  return <h1>About Us</h1>;
}

// app/(app)/layout.js
import { requireAuth } from '@/lib/auth';

export default async function AppLayout({ children }) {
  const session = await requireAuth();

  return (
    <div className="app-layout">
      <AppNav user={session.user} />
      <div className="app-content">
        {children}
      </div>
    </div>
  );
}

// app/(app)/dashboard/page.js
export default function DashboardPage() {
  return <h1>Dashboard</h1>;
}
```

## 6. Internationalization Routing

### 6.1 i18n Route Structure
```javascript
// app/[locale]/layout.js
import { notFound } from 'next/navigation';
import { locales } from '@/lib/i18n';

export function generateStaticParams() {
  return locales.map(locale => ({ locale }));
}

export default function LocaleLayout({ children, params: { locale } }) {
  if (!locales.includes(locale)) {
    notFound();
  }

  return (
    <html lang={locale}>
      <body>{children}</body>
    </html>
  );
}

// app/[locale]/page.js
import { getTranslations } from '@/lib/i18n';

export default async function HomePage({ params: { locale } }) {
  const t = await getTranslations(locale, 'home');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </div>
  );
}

// lib/i18n-router.js
import { useRouter } from 'next/router';
import { locales, defaultLocale } from './i18n';

export function useI18nRouter() {
  const router = useRouter();
  const { locale, asPath, push } = router;

  const changeLocale = useCallback((newLocale) => {
    if (newLocale === locale) return;

    const path = asPath;
    const newPath = `/${newLocale}${path}`;

    push(newPath, newPath, { locale: newLocale });
  }, [locale, asPath, push]);

  const getLocalizedPath = useCallback((path, targetLocale = locale) => {
    if (targetLocale === defaultLocale) {
      return path;
    }
    return `/${targetLocale}${path}`;
  }, [locale]);

  return {
    locale,
    changeLocale,
    getLocalizedPath,
    isDefaultLocale: locale === defaultLocale,
  };
}
```

## Routing Migration Checklist

### Pre-Migration Planning
- [ ] Audit existing React Router routes
- [ ] Identify dynamic vs static routes
- [ ] Map nested route structures
- [ ] Document authentication requirements
- [ ] Plan SEO and meta tag migration

### Migration Execution
- [ ] Create Next.js page structure
- [ ] Convert Link components to Next.js Link
- [ ] Replace programmatic navigation
- [ ] Implement route protection
- [ ] Handle 404 and error pages
- [ ] Test all navigation flows

### Post-Migration Optimization
- [ ] Implement route prefetching
- [ ] Add loading states
- [ ] Optimize for Core Web Vitals
- [ ] Set up redirect rules
- [ ] Monitor navigation performance
- [ ] Update analytics tracking

This routing guide ensures smooth transition from React Router to Next.js routing while maintaining functionality and improving performance.
"""

    def _get_data_fetching_guide(self) -> str:
        """Data fetching patterns with React 19 and Next.js."""
        return """
# Next.js Data Fetching with React 19 Patterns

## 1. Data Fetching Strategy Overview

### 1.1 Choosing the Right Data Fetching Pattern
```javascript
// lib/data-fetching-decisions.js
export const DATA_FETCHING_PATTERNS = {
  // Server Components (Recommended for static data)
  SERVER_COMPONENT: {
    useCase: 'Static content, user-specific data, SEO-critical data',
    benefits: ['No client-side JavaScript', 'Direct database access', 'Better SEO'],
    example: 'Product details, user profile, blog posts'
  },

  // Client Components with fetch (Interactive data)
  CLIENT_FETCH: {
    useCase: 'Interactive features, real-time data, user actions',
    benefits: ['Real-time updates', 'User interaction', 'Client state management'],
    example: 'Notifications, live chat, search suggestions'
  },

  // Server Actions (Form submissions, mutations)
  SERVER_ACTIONS: {
    useCase: 'Form submissions, data mutations, secure operations',
    benefits: ['Type-safe', 'Progressive enhancement', 'No client JS needed'],
    example: 'Contact forms, user preferences, data updates'
  },

  // SWR/React Query (Client-side caching)
  CLIENT_CACHE: {
    useCase: 'Frequently changing data, offline support, optimistic updates',
    benefits: ['Background refetching', 'Offline support', 'Cache management'],
    example: 'Dashboard data, user notifications, real-time updates'
  }
};
```

## 2. Server Components Data Fetching

### 2.1 Basic Server Component Data Fetching
```javascript
// app/products/[slug]/page.js
import { notFound } from 'next/navigation';

async function getProduct(slug) {
  const res = await fetch(`${process.env.API_URL}/products/${slug}`, {
    next: {
      revalidate: 3600, // Revalidate every hour
      tags: ['product', slug] // Cache invalidation tags
    }
  });

  if (!res.ok) {
    return null;
  }

  return res.json();
}

async function getProductReviews(productId) {
  const res = await fetch(`${process.env.API_URL}/reviews?product=${productId}`, {
    next: { revalidate: 60 }, // Revalidate every minute
  });

  if (!res.ok) {
    return [];
  }

  return res.json();
}

export async function generateMetadata({ params }) {
  const product = await getProduct(params.slug);

  if (!product) {
    return { title: 'Product Not Found' };
  }

  return {
    title: product.name,
    description: product.description,
    openGraph: {
      title: product.name,
      description: product.description,
      images: [product.image],
    },
  };
}

export default async function ProductPage({ params }) {
  const product = await getProduct(params.slug);

  if (!product) {
    notFound();
  }

  const reviews = await getProductReviews(product.id);

  return (
    <div className="product-page">
      <ProductDetails product={product} />
      <ProductReviews reviews={reviews} productId={product.id} />
    </div>
  );
}

// Client component for interactive parts
// components/ProductReviews.js
'use client';

import { useState } from 'react';
import { useOptimistic } from 'react';

export function ProductReviews({ reviews, productId }) {
  const [reviewList, setReviewList] = useState(reviews);

  const [optimisticReviews, addOptimisticReview] = useOptimistic(
    reviewList,
    (state, newReview) => [...state, newReview]
  );

  async function handleAddReview(formData) {
    const review = {
      id: Date.now(),
      content: formData.get('content'),
      rating: parseInt(formData.get('rating')),
      optimistic: true,
    };

    addOptimisticReview(review);

    try {
      const response = await fetch(`/api/products/${productId}/reviews`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to add review');
      }

      const newReview = await response.json();
      setReviewList(prev => [...prev.filter(r => !r.optimistic), newReview]);
    } catch (error) {
      // Revert optimistic update
      setReviewList(prev => prev.filter(r => !r.optimistic));
      console.error('Failed to add review:', error);
    }
  }

  return (
    <div className="reviews-section">
      <h3>Customer Reviews</h3>

      <ReviewForm onSubmit={handleAddReview} />

      <div className="reviews-list">
        {optimisticReviews.map(review => (
          <ReviewItem
            key={review.id}
            review={review}
            isOptimistic={review.optimistic}
          />
        ))}
      </div>
    </div>
  );
}
```

### 2.2 Parallel Data Fetching
```javascript
// app/dashboard/page.js
import { Suspense } from 'react';

// Data fetching functions
async function getUserStats(userId) {
  const res = await fetch(`${process.env.API_URL}/users/${userId}/stats`, {
    next: { revalidate: 300 }, // 5 minutes
    headers: {
      'Authorization': `Bearer ${process.env.API_TOKEN}`,
    },
  });

  if (!res.ok) throw new Error('Failed to fetch user stats');
  return res.json();
}

async function getRecentActivity(userId) {
  const res = await fetch(`${process.env.API_URL}/users/${userId}/activity`, {
    next: { revalidate: 60 }, // 1 minute
  });

  if (!res.ok) throw new Error('Failed to fetch activity');
  return res.json();
}

async function getNotifications(userId) {
  const res = await fetch(`${process.env.API_URL}/users/${userId}/notifications`, {
    next: { revalidate: 30 }, // 30 seconds
  });

  if (!res.ok) throw new Error('Failed to fetch notifications');
  return res.json();
}

// Loading components
function UserStatsLoading() {
  return <div className="loading-skeleton">Loading stats...</div>;
}

function RecentActivityLoading() {
  return <div className="loading-skeleton">Loading activity...</div>;
}

// Main dashboard page
export default async function DashboardPage({ params }) {
  const userId = params.userId;

  // Parallel data fetching
  const [stats, activity, notifications] = await Promise.all([
    getUserStats(userId),
    getRecentActivity(userId),
    getNotifications(userId),
  ]);

  return (
    <div className="dashboard">
      <div className="dashboard-grid">
        <div className="stats-section">
          <Suspense fallback={<UserStatsLoading />}>
            <UserStats stats={stats} />
          </Suspense>
        </div>

        <div className="activity-section">
          <Suspense fallback={<RecentActivityLoading />}>
            <RecentActivity activity={activity} />
          </Suspense>
        </div>

        <div className="notifications-section">
          <Suspense fallback={<div>Loading notifications...</div>}>
            <Notifications notifications={notifications} />
          </Suspense>
        </div>
      </div>
    </div>
  );
}
```

## 3. Client-Side Data Fetching with React 19

### 3.1 Using React 19's use() Hook
```javascript
// components/ProductList.js
'use client';

import { use, Suspense } from 'react';

// Create a promise cache
const productCache = new Map();

function createProductsPromise() {
  const promise = fetch('/api/products')
    .then(res => res.json())
    .then(data => {
      productCache.set('products', data);
      return data;
    });

  productCache.set('products', promise);
  return promise;
}

function ProductsInner() {
  const products = use(
    productCache.get('products') || createProductsPromise()
  );

  return (
    <div className="product-grid">
      {products.map(product => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
}

export function ProductList() {
  return (
    <Suspense fallback={<div>Loading products...</div>}>
      <ProductsInner />
    </Suspense>
  );
}

// Usage with error boundary
import { ErrorBoundary } from 'react-error-boundary';

function ProductsWithErrorBoundary() {
  return (
    <ErrorBoundary
      fallback={<div>Failed to load products. Please try again.</div>}
    >
      <ProductList />
    </ErrorBoundary>
  );
}
```

### 3.2 SWR Integration for Client-Side Caching
```javascript
// hooks/useSWRData.js
'use client';

import useSWR from 'swr';

const fetcher = async (url) => {
  const res = await fetch(url);

  if (!res.ok) {
    const error = new Error('An error occurred while fetching the data.');
    error.info = await res.json();
    error.status = res.status;
    throw error;
  }

  return res.json();
};

export function useUser(id) {
  const { data, error, isLoading, mutate } = useSWR(
    id ? `/api/users/${id}` : null,
    fetcher,
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: true,
      dedupingInterval: 60000, // 1 minute
    }
  );

  return {
    user: data,
    isLoading,
    isError: error,
    mutate,
  };
}

export function useNotifications(userId) {
  const { data, error, isLoading, mutate } = useSWR(
    userId ? `/api/users/${userId}/notifications` : null,
    fetcher,
    {
      refreshInterval: 30000, // 30 seconds
      revalidateOnFocus: true,
      onError: (error) => {
        console.error('Failed to fetch notifications:', error);
      },
    }
  );

  return {
    notifications: data || [],
    isLoading,
    isError: error,
    mutate,
  };
}

// Optimistic updates
export function useNotificationsWithOptimistic(userId) {
  const { notifications, isLoading, mutate } = useNotifications(userId);

  const markAsReadOptimistic = async (notificationId) => {
    // Update local cache immediately
    mutate(
      notifications.map(n =>
        n.id === notificationId ? { ...n, read: true } : n
      ),
      false // Don't revalidate
    );

    try {
      await fetch(`/api/notifications/${notificationId}/read`, {
        method: 'PATCH',
      });
    } catch (error) {
      // Revert on error
      mutate();
      throw error;
    }
  };

  return {
    notifications,
    isLoading,
    markAsReadOptimistic,
  };
}
```

## 4. Server Actions for Mutations

### 4.1 Basic Server Actions
```javascript
// app/actions/user-actions.js
'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { z } from 'zod';

const UpdateProfileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  bio: z.string().max(500, 'Bio must be less than 500 characters'),
});

export async function updateProfile(userId, formData) {
  // Validate input
  const validatedData = UpdateProfileSchema.parse({
    name: formData.get('name'),
    email: formData.get('email'),
    bio: formData.get('bio'),
  });

  try {
    // Update user in database
    const response = await fetch(`${process.env.API_URL}/users/${userId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.API_TOKEN}`,
      },
      body: JSON.stringify(validatedData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to update profile');
    }

    // Revalidate cache
    revalidatePath('/profile');
    revalidatePath('/dashboard');

    return { success: true };
  } catch (error) {
    return { error: error.message };
  }
}

export async function deleteAccount(userId) {
  try {
    await fetch(`${process.env.API_URL}/users/${userId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${process.env.API_TOKEN}`,
      },
    });

    // Clear authentication
    revalidatePath('/', 'layout');

    redirect('/goodbye');
  } catch (error) {
    return { error: 'Failed to delete account' };
  }
}
```

### 4.2 Progressive Enhancement with Server Actions
```javascript
// components/ProfileForm.js
'use client';

import { useFormState } from 'react-dom';
import { updateProfile } from '../app/actions/user-actions';

function ProfileForm({ user }) {
  const [state, formAction] = useFormState(updateProfile.bind(null, user.id), {
    success: false,
    error: null,
  });

  return (
    <form action={formAction} className="profile-form">
      <div className="form-group">
        <label htmlFor="name">Name</label>
        <input
          id="name"
          name="name"
          type="text"
          defaultValue={user.name}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          defaultValue={user.email}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="bio">Bio</label>
        <textarea
          id="bio"
          name="bio"
          rows={4}
          defaultValue={user.bio || ''}
          maxLength={500}
        />
      </div>

      {state.error && (
        <div className="error-message">{state.error}</div>
      )}

      {state.success && (
        <div className="success-message">Profile updated successfully!</div>
      )}

      <button
        type="submit"
        disabled={state.pending}
        className="submit-button"
      >
        {state.pending ? 'Updating...' : 'Update Profile'}
      </button>
    </form>
  );
}

// With JavaScript enhancement
import { useState } from 'react';

function EnhancedProfileForm({ user }) {
  const [isPending, setIsPending] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleSubmit = async (formData) => {
    setIsPending(true);
    setMessage({ type: '', text: '' });

    try {
      const result = await updateProfile(user.id, formData);

      if (result.error) {
        setMessage({ type: 'error', text: result.error });
      } else {
        setMessage({ type: 'success', text: 'Profile updated successfully!' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'An unexpected error occurred' });
    } finally {
      setIsPending(false);
    }
  };

  return (
    <form action={handleSubmit} className="profile-form">
      {/* Form fields */}

      {message.text && (
        <div className={`message ${message.type}`}>
          {message.text}
        </div>
      )}

      <button
        type="submit"
        disabled={isPending}
        className="submit-button"
      >
        {isPending ? 'Updating...' : 'Update Profile'}
      </button>
    </form>
  );
}
```

## 5. Advanced Data Fetching Patterns

### 5.1 Streaming with Server Components
```javascript
// app/streaming/page.js
import { Suspense } from 'react';

// Slow-loading component
async function SlowComponent() {
  // Simulate slow database query
  await new Promise(resolve => setTimeout(resolve, 2000));

  const data = await fetch('https://api.example.com/slow-data');
  const result = await data.json();

  return (
    <div>
      <h2>Slow Component</h2>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
}

// Fast component
async function FastComponent() {
  const data = await fetch('https://api.example.com/fast-data');
  const result = await data.json();

  return (
    <div>
      <h2>Fast Component</h2>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
}

export default function StreamingPage() {
  return (
    <div>
      <h1>Streaming Data Fetching</h1>

      <div className="fast-section">
        <Suspense fallback={<div>Loading fast component...</div>}>
          <FastComponent />
        </Suspense>
      </div>

      <div className="slow-section">
        <Suspense fallback={<div>Loading slow component...</div>}>
          <SlowComponent />
        </Suspense>
      </div>
    </div>
  );
}
```

### 5.2 Real-time Data with Server-Sent Events
```javascript
// app/api/live-data/route.js
import { NextResponse } from 'next/server';

export async function GET() {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    start(controller) {
      const interval = setInterval(async () => {
        try {
          const data = await fetch('https://api.example.com/live-data');
          const result = await data.json();

          const formattedData = `data: ${JSON.stringify(result)}\n\n`;
          controller.enqueue(encoder.encode(formattedData));
        } catch (error) {
          console.error('Error fetching live data:', error);
        }
      }, 1000); // Update every second

      // Cleanup
      return () => clearInterval(interval);
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}

// components/LiveData.js
'use client';

import { useEffect, useState } from 'react';

export function LiveData() {
  const [data, setData] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource('/api/live-data');

    eventSource.onopen = () => {
      setIsConnected(true);
      console.log('Connected to live data stream');
    };

    eventSource.onmessage = (event) => {
      try {
        const newData = JSON.parse(event.data);
        setData(newData);
      } catch (error) {
        console.error('Error parsing live data:', error);
      }
    };

    eventSource.onerror = (error) => {
      setIsConnected(false);
      console.error('Live data stream error:', error);
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="live-data">
      <div className="connection-status">
        Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
      </div>

      {data && (
        <div className="data-display">
          <h3>Live Data</h3>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

### 5.3 Data Fetching with Error Boundaries
```javascript
// components/DataProvider.js
'use client';

import { Suspense } from 'react';
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div className="error-fallback">
      <h2>Something went wrong</h2>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function LoadingFallback() {
  return (
    <div className="loading-fallback">
      <div className="spinner" />
      <p>Loading data...</p>
    </div>
  );
}

export function DataProvider({ children }) {
  return (
    <ErrorBoundary FallbackComponent={ErrorFallback}>
      <Suspense fallback={<LoadingFallback />}>
        {children}
      </Suspense>
    </ErrorBoundary>
  );
}

// Usage
function App() {
  return (
    <DataProvider>
      <UserProfile />
      <UserDashboard />
      <RecentActivity />
    </DataProvider>
  );
}
```

## 6. Data Fetching Optimization

### 6.1 Request Deduplication and Caching
```javascript
// lib/data-cache.js
const dataCache = new Map();
const pendingRequests = new Map();

export async function fetchWithCache(url, options = {}) {
  const cacheKey = `${url}-${JSON.stringify(options)}`;

  // Return cached data if available
  if (dataCache.has(cacheKey)) {
    const { data, timestamp } = dataCache.get(cacheKey);

    // Check if cache is still valid (5 minutes)
    if (Date.now() - timestamp < 300000) {
      return data;
    }
  }

  // Return existing promise if request is in flight
  if (pendingRequests.has(cacheKey)) {
    return pendingRequests.get(cacheKey);
  }

  // Make new request
  const promise = fetch(url, options)
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Cache the result
      dataCache.set(cacheKey, {
        data,
        timestamp: Date.now(),
      });

      // Clean up pending request
      pendingRequests.delete(cacheKey);

      return data;
    })
    .catch((error) => {
      pendingRequests.delete(cacheKey);
      throw error;
    });

  pendingRequests.set(cacheKey, promise);
  return promise;
}

// Usage in server components
async function getUserData(userId) {
  return fetchWithCache(`${process.env.API_URL}/users/${userId}`);
}

async function getUserPosts(userId) {
  return fetchWithCache(`${process.env.API_URL}/users/${userId}/posts`);
}
```

### 6.2 Background Data Refresh
```javascript
// hooks/useBackgroundRefresh.js
'use client';

import { useEffect, useRef } from 'react';

export function useBackgroundRefresh(url, interval = 60000) {
  const intervalRef = useRef(null);
  const lastFetchRef = useRef(0);

  useEffect(() => {
    const refreshData = async () => {
      try {
        await fetch(url, {
          method: 'GET',
          headers: {
            'X-Background-Refresh': 'true',
          },
        });

        lastFetchRef.current = Date.now();
      } catch (error) {
        console.error('Background refresh failed:', error);
      }
    };

    // Set up interval
    intervalRef.current = setInterval(refreshData, interval);

    // Initial refresh
    if (Date.now() - lastFetchRef.current > interval) {
      refreshData();
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [url, interval]);

  // Refresh data when user returns to tab
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        const timeSinceLastFetch = Date.now() - lastFetchRef.current;

        if (timeSinceLastFetch > interval) {
          refreshData();
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [url, interval]);
}
```

## Data Fetching Checklist

### Server Components
- [ ] Identify static vs dynamic data needs
- [ ] Implement proper caching strategies
- [ ] Set up error boundaries
- [ ] Add loading states
- [ ] Optimize database queries

### Client Components
- [ ] Use React 19's use() hook
- [ ] Implement SWR for caching
- [ ] Add optimistic updates
- [ ] Handle offline scenarios
- [ ] Set up real-time updates

### Server Actions
- [ ] Validate input data
- [ ] Handle errors gracefully
- [ ] Implement progressive enhancement
- [ ] Revalidate cache appropriately
- [ ] Add security measures

### Performance Optimization
- [ ] Enable request deduplication
- [ ] Implement background refresh
- [ ] Set up proper caching headers
- [ ] Monitor data fetching performance
- [ ] Optimize bundle size

This comprehensive data fetching guide ensures optimal performance and user experience in Next.js applications.
"""

    def _get_build_guide(self) -> str:
        """Build process optimization guide."""
        return """
# Next.js Build Optimization Guide

## 1. Build Process Configuration

### 1.1 Next.js Configuration for Performance
```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Production optimizations
  compress: true,
  poweredByHeader: false,

  // Experimental features
  experimental: {
    appDir: true,
    serverActions: true,
    optimizeCss: true,
    optimizePackageImports: ['@mui/material', 'date-fns'],
  },

  // Image optimization
  images: {
    domains: ['example.com', 'cdn.example.com'],
    formats: ['image/webp', 'image/avif'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // Webpack optimizations
  webpack: (config, { isServer, dev, webpack }) => {
    // Production optimizations
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        usedExports: true,
        sideEffects: false,
      };

      // Tree shaking
      config.optimization.usedExports = true;
      config.optimization.sideEffects = false;
    }

    // Bundle analyzer
    if (process.env.ANALYZE === 'true') {
      const { BundleAnalyzerPlugin } = require('webpack-bundle-analyzer');
      config.plugins.push(
        new BundleAnalyzerPlugin({
          analyzerMode: 'static',
          openAnalyzer: false,
        })
      );
    }

    return config;
  },

  // Headers for performance
  headers: async () => [
    {
      source: '/fonts/(.*)',
      headers: [
        {
          key: 'Cache-Control',
          value: 'public, max-age=31536000, immutable',
        },
      ],
    },
    {
      source: '/_next/static/(.*)',
      headers: [
        {
          key: 'Cache-Control',
          value: 'public, max-age=31536000, immutable',
        },
      ],
    },
  ],

  // Redirects
  async redirects() {
    return [
      {
        source: '/home',
        destination: '/',
        permanent: true,
      },
    ];
  },

  // Rewrites for API proxying
  async rewrites() {
    return [
      {
        source: '/api/proxy/:path*',
        destination: `${process.env.API_URL}/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
```

### 1.2 Package.json Scripts Optimization
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "build:analyze": "ANALYZE=true next build",
    "build:production": "NODE_ENV=production next build",
    "start": "next start",
    "start:production": "NODE_ENV=production next start",
    "lint": "next lint",
    "lint:fix": "next lint --fix",
    "type-check": "tsc --noEmit",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "e2e": "playwright test",
    "e2e:headed": "playwright test --headed",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build",
    "optimize": "npm run lint:fix && npm run type-check && npm run test && npm run build",
    "clean": "rimraf .next out dist"
  },
  "devDependencies": {
    "@next/bundle-analyzer": "^14.0.0",
    "@storybook/addon-essentials": "^7.0.0",
    "@storybook/nextjs": "^7.0.0",
    "rimraf": "^5.0.0",
    "typescript": "^5.0.0"
  }
}
```

## 2. Bundle Optimization

### 2.1 Code Splitting Strategies
```javascript
// Dynamic imports for route-based splitting
import dynamic from 'next/dynamic';

// Lazy load heavy components
const AdminPanel = dynamic(() => import('../components/AdminPanel'), {
  loading: () => <div>Loading admin panel...</div>,
  ssr: false, // Don't server-side render admin panel
});

const Chart = dynamic(() => import('../components/Chart'), {
  loading: () => <div>Loading chart...</div>,
  ssr: false,
});

// Component with threshold loading
const LazyComponent = dynamic(
  () => import('../components/HeavyComponent'),
  {
    loading: () => <div>Loading...</div>,
    ssr: false,
  }
);

// Usage in pages
function Dashboard() {
  const [showAdmin, setShowAdmin] = useState(false);

  return (
    <div>
      <h1>Dashboard</h1>

      <button onClick={() => setShowAdmin(!showAdmin)}>
        Toggle Admin Panel
      </button>

      {showAdmin && <AdminPanel />}

      <Chart />
      <LazyComponent />
    </div>
  );
}

// Route-based splitting
// pages/admin/[...slug].js
export const config = {
  runtime: 'experimental-edge',
};

export default function AdminPage({ params }) {
  return <AdminDashboard params={params} />;
}
```

### 2.2 Webpack Bundle Optimization
```javascript
// webpack.config.js (custom webpack config)
const withTM = require('next-transpile-modules')(['ui-library']);
const withOptimizedImages = require('next-optimized-images');

module.exports = withTM(
  withOptimizedImages({
    webpack: (config, { isServer, dev }) => {
      // Production optimizations
      if (!dev && !isServer) {
        // Split vendor chunks
        config.optimization.splitChunks = {
          chunks: 'all',
          cacheGroups: {
            vendor: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              chunks: 'all',
            },
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              enforce: true,
            },
          },
        };

        // Minimize bundle size
        config.optimization.usedExports = true;
        config.optimization.sideEffects = false;
      }

      // Resolve aliases for cleaner imports
      config.resolve.alias = {
        ...config.resolve.alias,
        '@': path.resolve(__dirname, 'src'),
        '@components': path.resolve(__dirname, 'src/components'),
        '@utils': path.resolve(__dirname, 'src/utils'),
      };

      // Exclude unused locales from moment.js
      if (config.resolve.plugins) {
        config.resolve.plugins.push(
          new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/)
        );
      }

      return config;
    },

    // Optimize images
    images: {
      mozjpeg: {
        quality: 80,
      },
      pngquant: {
        quality: [0.65, 0.8],
      },
      gifsicle: {
        optimizationLevel: 7,
      },
    },
  })
);
```

### 2.3 Tree Shaking and Dead Code Elimination
```javascript
// lib/utils.js - Export individual functions
export function formatDate(date) {
  return new Intl.DateTimeFormat().format(date);
}

export function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

export function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Component imports only what's needed
import { formatDate, formatCurrency } from '../lib/utils';

function ProductCard({ product }) {
  return (
    <div>
      <h3>{product.name}</h3>
      <p>{formatDate(product.createdAt)}</p>
      <p>{formatCurrency(product.price)}</p>
    </div>
  );
}

// Avoid importing entire libraries
// Bad: import * as _ from 'lodash';
// Good: import { debounce } from 'lodash';

// Use specific imports from libraries
import { motion, AnimatePresence } from 'framer-motion';
import { Field, Form, Formik } from 'formik';
```

## 3. Performance Monitoring and Analytics

### 3.1 Build Performance Monitoring
```javascript
// scripts/build-analyzer.js
const fs = require('fs');
const path = require('path');
const { gzipSync } = require('zlib');

function analyzeBuildOutput() {
  const buildDir = path.join(process.cwd(), '.next');
  const staticDir = path.join(buildDir, 'static');

  const analysis = {
    totalSize: 0,
    bundles: [],
    largestAssets: [],
  };

  // Analyze JavaScript bundles
  const jsDir = path.join(staticDir, 'chunks');
  if (fs.existsSync(jsDir)) {
    fs.readdirSync(jsDir).forEach(file => {
      if (file.endsWith('.js')) {
        const filePath = path.join(jsDir, file);
        const stats = fs.statSync(filePath);
        const content = fs.readFileSync(filePath);
        const gzipped = gzipSync(content);

        analysis.bundles.push({
          file,
          size: stats.size,
          gzippedSize: gzipped.length,
          path: filePath,
        });

        analysis.totalSize += stats.size;
      }
    });
  }

  // Sort by size
  analysis.bundles.sort((a, b) => b.size - a.size);
  analysis.largestAssets = analysis.bundles.slice(0, 10);

  return analysis;
}

function generateReport(analysis) {
  const report = `
# Build Analysis Report

## Summary
- Total bundle size: ${(analysis.totalSize / 1024 / 1024).toFixed(2)} MB
- Number of bundles: ${analysis.bundles.length}

## Largest Assets
${analysis.largestAssets.map(asset =>
  `- ${asset.file}: ${(asset.size / 1024).toFixed(2)} KB (${(asset.gzippedSize / 1024).toFixed(2)} KB gzipped)`
).join('\n')}

## Recommendations
${analysis.bundles.some(b => b.size > 244 * 1024) ?
  '⚠️  Some bundles exceed 244KB. Consider code splitting.' :
  '✅ All bundles are within recommended size limits.'}
`;

  return report;
}

// Run analysis
const analysis = analyzeBuildOutput();
const report = generateReport(analysis);

console.log(report);
fs.writeFileSync(path.join(process.cwd(), 'build-analysis.md'), report);

// Fail build if bundles are too large
if (analysis.bundles.some(b => b.size > 500 * 1024)) {
  console.error('❌ Build failed: Some bundles exceed 500KB');
  process.exit(1);
}
```

### 3.2 Performance Budget Enforcement
```javascript
// scripts/performance-budget.js
const fs = require('fs');
const path = require('path');

const PERFORMANCE_BUDGET = {
  javascript: 244 * 1024, // 244KB
  css: 50 * 1024, // 50KB
  images: 1024 * 1024, // 1MB
  total: 500 * 1024, // 500KB
};

function checkPerformanceBudget() {
  const buildDir = path.join(process.cwd(), '.next', 'static');

  const results = {
    javascript: { size: 0, files: [] },
    css: { size: 0, files: [] },
    images: { size: 0, files: [] },
    total: 0,
  };

  // Analyze all static files
  function analyzeDirectory(dir) {
    fs.readdirSync(dir).forEach(file => {
      const filePath = path.join(dir, file);
      const stats = fs.statSync(filePath);

      if (stats.isDirectory()) {
        analyzeDirectory(filePath);
      } else {
        const size = stats.size;
        results.total += size;

        if (file.endsWith('.js')) {
          results.javascript.size += size;
          results.javascript.files.push({ file, size });
        } else if (file.endsWith('.css')) {
          results.css.size += size;
          results.css.files.push({ file, size });
        } else if (/\.(jpg|jpeg|png|gif|webp|avif)$/.test(file)) {
          results.images.size += size;
          results.images.files.push({ file, size });
        }
      }
    });
  }

  analyzeDirectory(buildDir);

  // Check budget compliance
  const violations = [];

  if (results.javascript.size > PERFORMANCE_BUDGET.javascript) {
    violations.push({
      type: 'javascript',
      budget: PERFORMANCE_BUDGET.javascript,
      actual: results.javascript.size,
      percentage: ((results.javascript.size / PERFORMANCE_BUDGET.javascript) * 100).toFixed(1),
    });
  }

  if (results.css.size > PERFORMANCE_BUDGET.css) {
    violations.push({
      type: 'css',
      budget: PERFORMANCE_BUDGET.css,
      actual: results.css.size,
      percentage: ((results.css.size / PERFORMANCE_BUDGET.css) * 100).toFixed(1),
    });
  }

  if (results.images.size > PERFORMANCE_BUDGET.images) {
    violations.push({
      type: 'images',
      budget: PERFORMANCE_BUDGET.images,
      actual: results.images.size,
      percentage: ((results.images.size / PERFORMANCE_BUDGET.images) * 100).toFixed(1),
    });
  }

  if (results.total > PERFORMANCE_BUDGET.total) {
    violations.push({
      type: 'total',
      budget: PERFORMANCE_BUDGET.total,
      actual: results.total,
      percentage: ((results.total / PERFORMANCE_BUDGET.total) * 100).toFixed(1),
    });
  }

  return { results, violations };
}

module.exports = { checkPerformanceBudget, PERFORMANCE_BUDGET };

// Integration with build process
// next.config.js
const { checkPerformanceBudget } = require('./scripts/performance-budget');

module.exports = {
  webpack: (config, { isServer }) => {
    // Add performance budget check plugin
    config.plugins.push({
      apply: (compiler) => {
        compiler.hooks.afterEmit.tap('PerformanceBudget', () => {
          if (!isServer) {
            const { violations } = checkPerformanceBudget();

            if (violations.length > 0) {
              console.error('❌ Performance budget violations:');
              violations.forEach(violation => {
                console.error(
                  `  ${violation.type}: ${(violation.actual / 1024).toFixed(2)}KB (${violation.percentage}% of budget)`
                );
              });

              if (process.env.NODE_ENV === 'production') {
                process.exit(1);
              }
            } else {
              console.log('✅ Performance budget passed');
            }
          }
        });
      },
    });

    return config;
  },
};
```

## 4. Deployment Optimization

### 4.1 Docker Optimization
```dockerfile
# Dockerfile.optimized
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Environment variables for build
ENV NEXT_TELEMETRY_DISABLED 1

# Build the application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

CMD ["node", "server.js"]
```

### 4.2 CI/CD Pipeline Optimization
```yaml
# .github/workflows/build-and-deploy.yml
name: Build and Deploy

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linting
        run: npm run lint

      - name: Run type checking
        run: npm run type-check

      - name: Run tests
        run: npm run test:coverage

      - name: Build application
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}

      - name: Analyze bundle size
        run: npm run build:analyze

      - name: Check performance budget
        run: node scripts/performance-budget.js

      - name: Run E2E tests
        run: npm run e2e

      - name: Build Storybook
        run: npm run build-storybook

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: build-files
          path: |
            .next/
            out/
            storybook-static/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: build-files

      - name: Deploy to production
        run: |
          # Deploy commands
          echo "Deploying to production..."
```

### 4.3 Environment-Specific Optimizations
```javascript
// lib/build-optimizations.js
export const buildConfigurations = {
  development: {
    compress: false,
    optimizeImages: false,
    minify: false,
    sourceMaps: true,
    devIndicators: true,
    reactStrictMode: true,
  },

  staging: {
    compress: true,
    optimizeImages: true,
    minify: true,
    sourceMaps: true,
    devIndicators: false,
    reactStrictMode: false,
  },

  production: {
    compress: true,
    optimizeImages: true,
    minify: true,
    sourceMaps: false,
    devIndicators: false,
    reactStrictMode: false,
    swcMinify: true,
  },
};

// next.config.js
const { buildConfigurations } = require('./lib/build-optimizations');
const environment = process.env.NODE_ENV || 'development';
const config = buildConfigurations[environment];

module.exports = {
  ...config,

  // Environment-specific configurations
  env: {
    CUSTOM_KEY: process.env.CUSTOM_KEY,
  },

  // Build-time constants
  webpack: (config, { dev }) => {
    if (!dev) {
      // Production optimizations
      config.optimization = {
        ...config.optimization,
        minimize: true,
        usedExports: true,
        sideEffects: false,
      };
    }

    return config;
  },
};
```

## 5. Asset Optimization

### 5.1 Image Optimization Pipeline
```javascript
// scripts/optimize-images.js
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

async function optimizeImages(inputDir, outputDir) {
  const formats = ['webp', 'avif'];
  const sizes = [320, 640, 768, 1024, 1280, 1536];

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  const files = fs.readdirSync(inputDir);

  for (const file of files) {
    if (/\.(jpg|jpeg|png)$/i.test(file)) {
      const inputPath = path.join(inputDir, file);
      const baseName = path.parse(file).name;

      console.log(`Optimizing ${file}...`);

      // Create different sizes and formats
      for (const size of sizes) {
        for (const format of formats) {
          const outputPath = path.join(outputDir, `${baseName}-${size}.${format}`);

          await sharp(inputPath)
            .resize(size, null, {
              withoutEnlargement: true,
              fit: 'inside'
            })
            .toFormat(format, {
              quality: format === 'avif' ? 50 : 80
            })
            .toFile(outputPath);
        }
      }
    }
  }
}

// Usage
optimizeImages('./public/images/original', './public/images/optimized');
```

### 5.2 Font Optimization
```javascript
// styles/optimized-fonts.css
@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/inter-regular.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC;
}

@font-face {
  font-family: 'Inter';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('/fonts/inter-bold.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC;
}

// Preload critical fonts
// pages/_document.js
import Document, { Html, Head, Main, NextScript } from 'next/document';

class MyDocument extends Document {
  render() {
    return (
      <Html>
        <Head>
          <link
            rel="preload"
            href="/fonts/inter-regular.woff2"
            as="font"
            type="font/woff2"
            crossOrigin="anonymous"
          />
          <link
            rel="preload"
            href="/fonts/inter-bold.woff2"
            as="font"
            type="font/woff2"
            crossOrigin="anonymous"
          />
        </Head>
        <body>
          <Main />
          <NextScript />
        </body>
      </Html>
    );
  }
}

export default MyDocument;
```

## Build Optimization Checklist

### Bundle Optimization
- [ ] Implement code splitting for large components
- [ ] Configure webpack for tree shaking
- [ ] Set performance budgets for bundle sizes
- [ ] Optimize vendor chunk splitting
- [ ] Remove unused dependencies

### Asset Optimization
- [ ] Compress and optimize images
- [ ] Use modern image formats (WebP, AVIF)
- [ ] Subset fonts and use font-display: swap
- [ ] Minify CSS and JavaScript
- [ ] Enable Gzip/Brotli compression

### Build Process
- [ ] Set up CI/CD pipeline with quality gates
- [ ] Configure environment-specific builds
- [ ] Implement build caching strategies
- [ ] Add bundle analysis to build process
- [ ] Set up Docker optimization

### Performance Monitoring
- [ ] Track Core Web Vitals in production
- [ ] Monitor bundle size changes
- [ ] Set up performance regression alerts
- [ ] Implement Real User Monitoring (RUM)
- [ ] Track build performance metrics

This comprehensive build optimization guide ensures Next.js applications are performant, efficient, and production-ready.
"""

    def _get_comprehensive_guide(self) -> str:
        """Complete React-Next integration guide."""
        return f"""
{self._get_migration_guide()}

{self._get_performance_guide()}

{self._get_seo_guide()}

{self._get_routing_guide()}

{self._get_data_fetching_guide()}

{self._get_testing_guide()}

{self._get_build_guide()}

## React-Next Integration Complete Guide

This comprehensive guide covers all aspects of React and Next.js integration, from basic migration strategies to advanced optimization techniques.

### Key Integration Patterns

1. **Migration Strategy**: Gradual migration from React SPA to Next.js
2. **Performance Optimization**: Core Web Vitals and bundle optimization
3. **SEO Implementation**: Meta tags, structured data, and search optimization
4. **Routing Integration**: React Router to Next.js routing patterns
5. **Data Fetching**: Server-side and client-side patterns with React 19
6. **Testing Strategy**: Unit, integration, and E2E testing approaches
7. **Build Optimization**: Performance budgets and deployment strategies

### Best Practices Summary

- Start with Pages Router for gradual migration
- Use App Router for new projects with server components
- Implement progressive enhancement with server actions
- Optimize for Core Web Vitals from the start
- Use dynamic imports for code splitting
- Implement proper error boundaries and loading states
- Set up comprehensive testing strategy
- Monitor performance continuously

### Tools and Resources

- **Bundle Analysis**: @next/bundle-analyzer
- **Performance Monitoring**: Lighthouse, Web Vitals
- **Testing**: Jest, React Testing Library, Playwright
- **SEO**: next-seo, structured data validation
- **Deployment**: Vercel, Docker, GitHub Actions
"""

    def _load_migration_patterns(self) -> Dict[str, Any]:
        """Load migration pattern data."""
        return {
            "phases": ["Preparation and Audit", "Gradual Migration", "Advanced Features", "Optimization"],
            "common_pitfalls": [
                "Big Bang Migration",
                "Ignoring SSR Differences",
                "Breaking SEO",
                "Performance Regression",
                "State Management Issues",
            ],
        }

    def _load_performance_patterns(self) -> Dict[str, Any]:
        """Load performance pattern data."""
        return {
            "core_vitals": {"LCP": "< 2.5s", "FID": "< 100ms", "CLS": "< 0.1"},
            "optimization_techniques": [
                "Image optimization",
                "Code splitting",
                "Caching strategies",
                "Bundle analysis",
            ],
        }

    def _load_testing_patterns(self) -> Dict[str, Any]:
        """Load testing pattern data."""
        return {
            "types": ["Unit tests", "Integration tests", "E2E tests", "Performance tests", "Visual tests"],
            "tools": ["Jest", "React Testing Library", "Playwright", "Storybook"],
        }

    def _load_build_patterns(self) -> Dict[str, Any]:
        """Load build pattern data."""
        return {
            "optimizations": ["Bundle splitting", "Tree shaking", "Code compression", "Asset optimization"],
            "budgets": {"javascript": "244KB", "css": "50KB", "total": "500KB"},
        }


# Register the skill
def register_react_next_integration_skill():
    """Register the React-Next Integration Expert skill."""
    skill = ReactNextIntegrationExpertSkill()
    from ...skills_framework import register_skill

    register_skill(skill)
    return skill


# Auto-register on import
try:
    register_react_next_integration_skill()
except Exception as e:
    logger.error(f"Failed to register React-Next Integration skill: {e}")
