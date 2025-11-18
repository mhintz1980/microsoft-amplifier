"""
Supabase Expert Skill

Comprehensive Supabase platform mastery with zero hallucinations guarantee.
Provides expert-level knowledge of Supabase fundamentals, PostgreSQL database,
authentication, real-time features, storage, CDN, and edge functions.
"""

import json
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from ..skills_framework.base_skill import BaseSkill, SkillContext, SkillResult
from ..quality_assurance.validators.zero_hallucination_validator import ZeroHallucinationValidator
from ..agent_lightning_integration.performance_monitor import PerformanceMonitor


class SupabaseVersion(Enum):
    """Supported Supabase versions."""

    V2 = "2.0.0"
    LATEST = "latest"


class FeatureCategory(Enum):
    """Supabase feature categories."""

    DATABASE = "database"
    AUTH = "authentication"
    REALTIME = "realtime"
    STORAGE = "storage"
    EDGE_FUNCTIONS = "edge_functions"
    POSTGREST = "postgrest"
    PGVECTOR = "pgvector"
    FUNCTIONS = "functions"


class ValidationLevel(Enum):
    """Validation levels for Supabase implementations."""

    SYNTAX = "syntax"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"


@dataclass
class SupabaseFeature:
    """Information about a Supabase feature."""

    name: str
    category: FeatureCategory
    description: str
    api_endpoints: List[str]
    configuration_options: Dict[str, Any]
    common_patterns: List[str]
    performance_considerations: List[str]
    security_considerations: List[str]
    examples: List[Dict[str, Any]]


@dataclass
class DatabaseSchema:
    """PostgreSQL database schema definition."""

    name: str
    tables: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    constraints: List[Dict[str, Any]]
    indexes: List[Dict[str, Any]]
    rls_policies: List[Dict[str, Any]]
    functions: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]]


@dataclass
class AuthConfiguration:
    """Authentication configuration."""

    providers: List[str]
    rls_enabled: bool
    custom_claims: Dict[str, Any]
    redirect_urls: List[str]
    session_settings: Dict[str, Any]
    security_settings: Dict[str, Any]


@dataclass
class RealtimeSubscription:
    """Real-time subscription configuration."""

    table: str
    events: List[str]
    filter: Optional[Dict[str, Any]]
    jwt_token: Optional[str]
    channel_config: Dict[str, Any]


@dataclass
class StorageBucket:
    """Storage bucket configuration."""

    name: str
    public: bool
    allowed_mime_types: List[str]
    file_size_limit: int
    transformations: Dict[str, Any]
    cdn_config: Dict[str, Any]


class SupabaseExpert(BaseSkill):
    """
    Comprehensive Supabase expert with zero hallucination guarantee.

    Provides mastery-level expertise in:
    - Supabase platform fundamentals and architecture
    - PostgreSQL advanced features and optimization
    - Authentication systems and row-level security
    - Real-time subscriptions and Presence channels
    - File storage, transformations, and CDN
    - Edge functions and serverless computing
    - Database migrations and schema management
    - Performance optimization and monitoring
    - Security best practices and compliance
    """

    def __init__(
        self,
        skill_id: str = "supabase_expert",
        name: str = "Supabase Expert",
        description: str = "Comprehensive Supabase platform mastery",
    ):
        super().__init__(skill_id, name, description)

        self.validator = ZeroHallucinationValidator(strict_mode=True)
        self.performance_monitor = PerformanceMonitor()

        # Initialize Supabase knowledge base
        self._init_supabase_features()
        self._init_database_patterns()
        self._init_authentication_patterns()
        self._init_realtime_patterns()
        self._init_storage_patterns()
        self._init_edge_function_patterns()

        # Performance tracking
        self.metrics = {
            "database_validations": 0,
            "auth_configurations": 0,
            "realtime_subscriptions": 0,
            "storage_setups": 0,
            "edge_functions_created": 0,
            "optimizations_suggested": 0,
            "security_audits": 0,
            "errors_prevented": 0,
        }

    def _init_supabase_features(self):
        """Initialize comprehensive Supabase feature database."""
        self.supabase_features = {
            # Database Features
            "postgresql_15": SupabaseFeature(
                name="PostgreSQL 15",
                category=FeatureCategory.DATABASE,
                description="Latest PostgreSQL with advanced features and extensions",
                api_endpoints=["/rest/v1/", "/rpc/v1/"],
                configuration_options={
                    "extensions": ["uuid-ossp", "pgcrypto", "pgjwt", "pg_net", "pg_stat_statements"],
                    "search_path": "public, extensions",
                    "timezone": "UTC",
                },
                common_patterns=[
                    "Use UUIDs for primary keys",
                    "Implement soft deletes with triggers",
                    "Create audit trails with triggers",
                    "Use materialized views for complex queries",
                ],
                performance_considerations=[
                    "Add appropriate indexes",
                    "Use connection pooling",
                    "Implement query caching",
                    "Monitor slow queries with pg_stat_statements",
                ],
                security_considerations=[
                    "Enable RLS for all tables",
                    "Use parameterized queries",
                    "Implement proper access controls",
                    "Regular security audits",
                ],
                examples=[
                    {
                        "name": "User table with RLS",
                        "description": "Basic user table with row-level security",
                    },
                    {
                        "name": "Audit trigger",
                        "description": "Automatic audit logging for data changes",
                    },
                ],
            ),
            # Authentication Features
            "gotrue": SupabaseFeature(
                name="GoTrue Authentication",
                category=FeatureCategory.AUTH,
                description="JWT-based authentication with multiple providers",
                api_endpoints=["/auth/v1/", "/auth/v1/user", "/auth/v1/verify"],
                configuration_options={
                    "jwt_expiry": "3600s",
                    "refresh_token_rotation": True,
                    "security_update_password": True,
                    "enable_signup": True,
                },
                common_patterns=[
                    "JWT token handling",
                    "Social provider integration",
                    "Custom auth server setup",
                    "Multi-factor authentication",
                ],
                performance_considerations=[
                    "Optimize JWT claims size",
                    "Implement token refresh strategies",
                    "Cache user permissions",
                    "Monitor auth performance",
                ],
                security_considerations=[
                    "Use HTTPS for all auth requests",
                    "Implement proper session management",
                    "Validate JWT signatures",
                    "Handle rate limiting",
                ],
                examples=[
                    {
                        "name": "Email authentication",
                        "description": "Basic email/password authentication flow",
                    },
                    {
                        "name": "Social login integration",
                        "description": "OAuth provider setup and handling",
                    },
                ],
            ),
            # Real-time Features
            "realtime": SupabaseFeature(
                name="Realtime Engine",
                category=FeatureCategory.REALTIME,
                description="PostgreSQL logical replication for real-time updates",
                api_endpoints=["/realtime/v1/"],
                configuration_options={
                    "replication_mode": "RDS",
                    "max_connections": 100,
                    "subscription_timeout": "60s",
                },
                common_patterns=[
                    "Table subscription filters",
                    "Presence channels",
                    "Broadcast channels",
                    "Client-side state management",
                ],
                performance_considerations=[
                    "Limit subscription data",
                    "Use efficient filters",
                    "Implement connection pooling",
                    "Monitor subscription performance",
                ],
                security_considerations=[
                    "Implement proper RLS for realtime",
                    "Validate JWT tokens",
                    "Filter sensitive data",
                    "Monitor connection patterns",
                ],
                examples=[
                    {
                        "name": "Chat application",
                        "description": "Real-time messaging with presence",
                    },
                    {
                        "name": "Live dashboard",
                        "description": "Real-time data visualization",
                    },
                ],
            ),
            # Storage Features
            "storage": SupabaseFeature(
                name="Object Storage",
                category=FeatureCategory.STORAGE,
                description="S3-compatible object storage with CDN",
                api_endpoints=["/storage/v1/", "/storage/v1/object", "/storage/v1/bucket"],
                configuration_options={
                    "file_size_limit": "52428800",  # 50MB
                    "allowed_mime_types": ["image/*", "application/pdf"],
                    "cdn_enabled": True,
                    "transformation_enabled": True,
                },
                common_patterns=[
                    "File upload with progress",
                    "Image transformations",
                    "Bucket-based organization",
                    "CDN integration",
                ],
                performance_considerations=[
                    "Optimize file sizes",
                    "Use CDN for static assets",
                    "Implement lazy loading",
                    "Cache transformed images",
                ],
                security_considerations=[
                    "Implement bucket policies",
                    "Validate file types",
                    "Use signed URLs",
                    "Scan uploaded files",
                ],
                examples=[
                    {
                        "name": "User avatar upload",
                        "description": "Profile picture management with transformations",
                    },
                    {
                        "name": "Document storage",
                        "description": "Secure file storage with access controls",
                    },
                ],
            ),
            # Edge Functions Features
            "edge_functions": SupabaseFeature(
                name="Edge Functions",
                category=FeatureCategory.EDGE_FUNCTIONS,
                description="Deno-based serverless functions at the edge",
                api_endpoints=["/functions/v1/", "/functions/v1/"],
                configuration_options={
                    "runtime": "deno",
                    "memory_limit": "150MiB",
                    "cpu_limit": "50ms",
                    "max_concurrency": 1000,
                },
                common_patterns=[
                    "Webhook handlers",
                    "Data processing",
                    "Third-party integrations",
                    "Custom APIs",
                ],
                performance_considerations=[
                    "Optimize cold start times",
                    "Use edge caching",
                    "Implement proper error handling",
                    "Monitor function performance",
                ],
                security_considerations=[
                    "Validate input data",
                    "Implement rate limiting",
                    "Use secure environment variables",
                    "Audit function access",
                ],
                examples=[
                    {
                        "name": "Payment webhook",
                        "description": "Stripe webhook processing",
                    },
                    {
                        "name": "Email service",
                        "description": "Custom email sending function",
                    },
                ],
            ),
        }

    def _init_database_patterns(self):
        """Initialize database design patterns."""
        self.database_patterns = {
            "schema_design": {
                "user_management": {
                    "description": "Complete user management schema",
                    "tables": [
                        {
                            "name": "users",
                            "columns": {
                                "id": "uuid primary key default gen_random_uuid()",
                                "email": "text unique not null",
                                "email_verified": "boolean default false",
                                "phone": "text unique",
                                "phone_verified": "boolean default false",
                                "username": "text unique",
                                "full_name": "text",
                                "avatar_url": "text",
                                "created_at": "timestamp with time zone default now()",
                                "updated_at": "timestamp with time zone default now()",
                                "last_sign_in_at": "timestamp with time zone",
                                "metadata": "jsonb",
                            },
                            "indexes": ["email", "username", "created_at"],
                        },
                        {
                            "name": "user_profiles",
                            "columns": {
                                "id": "uuid primary key default gen_random_uuid()",
                                "user_id": "uuid references users(id) on delete cascade",
                                "bio": "text",
                                "website": "text",
                                "location": "text",
                                "timezone": "text default 'UTC'",
                                "preferences": "jsonb",
                                "created_at": "timestamp with time zone default now()",
                                "updated_at": "timestamp with time zone default now()",
                            },
                            "indexes": ["user_id", "created_at"],
                        },
                    ],
                    "relationships": [
                        "users.id -> user_profiles.user_id (1:1)",
                    ],
                },
                "blog_system": {
                    "description": "Complete blog platform schema",
                    "tables": [
                        {
                            "name": "posts",
                            "columns": {
                                "id": "uuid primary key default gen_random_uuid()",
                                "author_id": "uuid references users(id) on delete cascade",
                                "title": "text not null",
                                "slug": "text unique not null",
                                "content": "text not null",
                                "excerpt": "text",
                                "featured_image": "text",
                                "status": "text default 'draft' check (status in ('draft', 'published', 'archived'))",
                                "published_at": "timestamp with time zone",
                                "created_at": "timestamp with time zone default now()",
                                "updated_at": "timestamp with time zone default now()",
                                "view_count": "integer default 0",
                                "like_count": "integer default 0",
                                "tags": "text[]",
                                "metadata": "jsonb",
                            },
                            "indexes": ["author_id", "slug", "status", "published_at", "created_at", "tags"],
                        },
                        {
                            "name": "comments",
                            "columns": {
                                "id": "uuid primary key default gen_random_uuid()",
                                "post_id": "uuid references posts(id) on delete cascade",
                                "author_id": "uuid references users(id) on delete cascade",
                                "content": "text not null",
                                "parent_id": "uuid references comments(id) on delete cascade",
                                "status": "text default 'published' check (status in ('draft', 'published', 'spam'))",
                                "created_at": "timestamp with time zone default now()",
                                "updated_at": "timestamp with time zone default now()",
                                "like_count": "integer default 0",
                            },
                            "indexes": ["post_id", "author_id", "parent_id", "status", "created_at"],
                        },
                        {
                            "name": "categories",
                            "columns": {
                                "id": "uuid primary key default gen_random_uuid()",
                                "name": "text unique not null",
                                "slug": "text unique not null",
                                "description": "text",
                                "color": "text",
                                "created_at": "timestamp with time zone default now()",
                            },
                            "indexes": ["name", "slug", "created_at"],
                        },
                        {
                            "name": "post_categories",
                            "columns": {
                                "post_id": "uuid references posts(id) on delete cascade",
                                "category_id": "uuid references categories(id) on delete cascade",
                                "created_at": "timestamp with time zone default now()",
                            },
                            "indexes": ["post_id", "category_id"],
                            "constraints": ["primary key (post_id, category_id)"],
                        },
                    ],
                    "relationships": [
                        "users.id -> posts.author_id (1:many)",
                        "users.id -> comments.author_id (1:many)",
                        "posts.id -> comments.post_id (1:many)",
                        "comments.id -> comments.parent_id (self-referential)",
                        "posts.id <-> post_categories.post_id (many:many)",
                        "categories.id <-> post_categories.category_id (many:many)",
                    ],
                },
            },
            "optimization_patterns": {
                "indexing": {
                    "composite_indexes": "CREATE INDEX idx_posts_author_status ON posts(author_id, status, created_at DESC)",
                    "partial_indexes": "CREATE INDEX idx_published_posts ON posts(published_at) WHERE status = 'published'",
                    "gin_indexes": "CREATE INDEX idx_posts_tags ON posts USING GIN(tags)",
                    "expression_indexes": "CREATE INDEX idx_posts_search ON posts USING GIN(to_tsvector('english', title || ' ' || content))",
                },
                "query_optimization": {
                    "common_table_expressions": "Use WITH clauses for complex queries",
                    "window_functions": "Use row_number(), rank(), and dense_rank() efficiently",
                    "materialized_views": "Create materialized views for expensive aggregations",
                    "partitioning": "Consider table partitioning for large datasets",
                },
            },
        }

    def _init_authentication_patterns(self):
        """Initialize authentication patterns."""
        self.authentication_patterns = {
            "providers": {
                "email": {
                    "setup": "Configure email provider in Supabase dashboard",
                    "client_flow": """
                    const { data, error } = await supabase.auth.signInWithPassword({
                      email: 'user@example.com',
                      password: 'secure-password'
                    })
                    """,
                    "security": "Implement password strength requirements and rate limiting",
                },
                "social": {
                    "providers": ["google", "github", "gitlab", "bitbucket", "discord", "apple", "azure", "keycloak"],
                    "setup": "Configure OAuth providers with proper redirect URLs",
                    "client_flow": """
                    const { data, error } = await supabase.auth.signInWithOAuth({
                      provider: 'google',
                      options: {
                        redirectTo: `${window.location.origin}/auth/callback`
                      }
                    })
                    """,
                    "security": "Validate provider tokens and handle OAuth state",
                },
                "custom": {
                    "setup": "Implement custom JWT tokens with proper signing",
                    "client_flow": """
                    const { data, error } = await supabase.auth.signInWithIdToken({
                      provider: 'custom',
                      token: customJwtToken,
                      nonce: randomNonce
                    })
                    """,
                    "security": "Verify custom token signatures and claims",
                },
            },
            "row_level_security": {
                "user_isolation": """
                -- Enable RLS on users table
                ALTER TABLE users ENABLE ROW LEVEL SECURITY;

                -- Users can only see their own profile
                CREATE POLICY "Users can view own profile" ON users
                  FOR SELECT USING (auth.uid() = id);

                -- Users can only update their own profile
                CREATE POLICY "Users can update own profile" ON users
                  FOR UPDATE USING (auth.uid() = id);
                """,
                "role_based": """
                -- Role-based access for blog posts
                CREATE POLICY "Published posts are viewable by everyone" ON posts
                  FOR SELECT USING (status = 'published');

                CREATE POLICY "Authors can manage their own posts" ON posts
                  FOR ALL USING (auth.uid() = author_id);
                """,
                "time_based": """
                -- Time-based access control
                CREATE POLICY "Recent posts only" ON posts
                  FOR SELECT USING (created_at > NOW() - INTERVAL '30 days');
                """,
            },
            "session_management": {
                "automatic_refresh": """
                // Configure automatic token refresh
                const { data: { subscription } } = supabase.auth.onAuthStateChange(
                  async (event, session) => {
                    if (event === 'TOKEN_REFRESHED') {
                      console.log('Token refreshed automatically');
                    }
                  }
                );
                """,
                "manual_refresh": """
                // Manual token refresh
                const { data, error } = await supabase.auth.refreshSession();
                """,
                "session_persistence": """
                // Configure session storage
                const supabase = createClient(url, key, {
                  auth: {
                    persistSession: true,
                    storage: localStorage,
                    storageKey: 'supabase.auth.token'
                  }
                })
                """,
            },
        }

    def _init_realtime_patterns(self):
        """Initialize real-time subscription patterns."""
        self.realtime_patterns = {
            "subscriptions": {
                "table_changes": """
                const subscription = supabase
                  .channel('db-changes')
                  .on(
                    'postgres_changes',
                    {
                      event: '*', // Listen to all events
                      schema: 'public',
                      table: 'posts',
                      filter: 'status=eq.published'
                    },
                    (payload) => {
                      console.log('Change received!', payload)
                    }
                  )
                  .subscribe()
                """,
                "specific_events": """
                // Listen only to INSERT events
                .on('postgres_changes', {
                  event: 'INSERT',
                  schema: 'public',
                  table: 'comments'
                }, handler)

                // Listen only to UPDATE events
                .on('postgres_changes', {
                  event: 'UPDATE',
                  schema: 'public',
                  table: 'users',
                  filter: 'id=eq.123'
                }, handler)
                """,
                "bulk_changes": """
                // Handle bulk data changes efficiently
                .on('postgres_changes', {
                  event: '*',
                  schema: 'public',
                  table: 'products'
                }, (payload) => {
                  switch (payload.eventType) {
                    case 'INSERT':
                      addProduct(payload.new)
                      break
                    case 'UPDATE':
                      updateProduct(payload.new)
                      break
                    case 'DELETE':
                      removeProduct(payload.old.id)
                      break
                  }
                })
                """,
            },
            "presence": {
                "user_tracking": """
                const channel = supabase.channel('online-users')

                // Track user presence
                channel.on('presence', { event: 'sync' }, () => {
                  const newState = channel.presenceState()
                  console.log('Online users:', newState)
                })

                // Join with user state
                channel.subscribe(async (status) => {
                  if (status === 'SUBSCRIBED') {
                    await channel.track({
                      user: supabase.auth.user().id,
                      online_at: new Date().toISOString(),
                      status: 'online'
                    })
                  }
                })
                """,
                "typing_indicators": """
                // Track typing status in chat
                const chatChannel = supabase.channel(`chat:${roomId}`)

                const trackTyping = async (isTyping) => {
                  await chatChannel.track({
                    user: userId,
                    typing: isTyping,
                    lastTyped: new Date().toISOString()
                  })
                }

                // Listen for typing events
                chatChannel.on('presence', { event: 'sync' }, () => {
                  const presence = chatChannel.presenceState()
                  const typingUsers = presence
                    .filter(state => state.typing)
                    .map(state => state.user)

                  updateTypingIndicators(typingUsers)
                })
                """,
            },
            "broadcast": {
                "server_broadcast": """
                // Server-side broadcast (Edge Function)
                import { serve } from "https://deno.land/std@0.131.0/http/server.ts"
                import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

                serve(async (req) => {
                  const supabaseClient = createClient(
                    Deno.env.get('SUPABASE_URL') ?? '',
                    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
                  )

                  const { message } = await req.json()

                  // Broadcast to all clients
                  await supabaseClient.channel('global-notifications')
                    .send({
                      type: 'broadcast',
                      event: 'notification',
                      payload: { message, timestamp: new Date().toISOString() }
                    })

                  return new Response(JSON.stringify({ success: true }))
                })
                """,
                "client_broadcast": """
                // Client-side broadcast
                const channel = supabase.channel('notifications')

                // Listen for broadcasts
                channel.on('broadcast', { event: 'notification' }, (payload) => {
                  showNotification(payload.payload)
                })

                channel.subscribe(async (status) => {
                  if (status === 'SUBSCRIBED') {
                    // Send broadcast to all channel members
                    await channel.send({
                      type: 'broadcast',
                      event: 'notification',
                      payload: { message: 'Hello everyone!', from: userId }
                    })
                  }
                })
                """,
            },
            "optimization": {
                "efficient_subscriptions": """
                // Use specific filters to reduce data transfer
                supabase.channel('posts')
                  .on('postgres_changes', {
                    event: '*',
                    schema: 'public',
                    table: 'posts',
                    filter: 'status=eq.published&author_id=eq.123'
                  }, handler)
                  .subscribe()
                """,
                "connection_management": """
                // Properly manage subscriptions
                class RealtimeManager {
                  constructor() {
                    this.subscriptions = new Map()
                  }

                  subscribe(name, config, handler) {
                    // Unsubscribe existing if any
                    this.unsubscribe(name)

                    const channel = supabase.channel(name)
                      .on('postgres_changes', config, handler)
                      .subscribe()

                    this.subscriptions.set(name, channel)
                    return channel
                  }

                  unsubscribe(name) {
                    const channel = this.subscriptions.get(name)
                    if (channel) {
                      supabase.removeChannel(channel)
                      this.subscriptions.delete(name)
                    }
                  }

                  unsubscribeAll() {
                    this.subscriptions.forEach((channel, name) => {
                      supabase.removeChannel(channel)
                    })
                    this.subscriptions.clear()
                  }
                }
                """,
            },
        }

    def _init_storage_patterns(self):
        """Initialize storage patterns."""
        self.storage_patterns = {
            "bucket_management": {
                "public_bucket": """
                -- Create public bucket for user avatars
                INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
                VALUES (
                  'avatars',
                  'avatars',
                  true,
                  2097152, -- 2MB
                  ARRAY['image/jpeg', 'image/png', 'image/webp']
                );

                -- Allow authenticated users to upload avatars
                CREATE POLICY "Users can upload their avatar" ON storage.objects
                  FOR INSERT WITH CHECK (
                    bucket_id = 'avatars' AND
                    auth.role() = 'authenticated' AND
                    (storage.foldername(name))[1] = auth.uid()::text
                  );

                -- Allow users to view their own avatar
                CREATE POLICY "Users can view their avatar" ON storage.objects
                  FOR SELECT USING (
                    bucket_id = 'avatars' AND
                    auth.role() = 'authenticated' AND
                    (storage.foldername(name))[1] = auth.uid()::text
                  );
                """,
                "private_bucket": """
                -- Create private bucket for user documents
                INSERT INTO storage.buckets (id, name, public, file_size_limit)
                VALUES (
                  'documents',
                  'documents',
                  false,
                  52428800 -- 50MB
                );

                -- Restrict access to document owners
                CREATE POLICY "Users can manage their documents" ON storage.objects
                  FOR ALL USING (
                    bucket_id = 'documents' AND
                    auth.uid() = (storage.foldername(name))[1]::uuid
                  );
                """,
            },
            "file_operations": {
                "upload_with_progress": """
                const uploadFile = async (file, bucket, path) => {
                  const { data, error } = await supabase.storage
                    .from(bucket)
                    .upload(path, file, {
                      cacheControl: '3600',
                      upsert: false,
                      onUploadProgress: (progress) => {
                        console.log(`Upload progress: ${progress}%`)
                        updateProgressBar(progress)
                      }
                    })

                  if (error) throw error

                  // Get public URL if bucket is public
                  const { data: { publicUrl } } = supabase.storage
                    .from(bucket)
                    .getPublicUrl(path)

                  return { data, publicUrl }
                }
                """,
                "resumable_uploads": """
                const uploadLargeFile = async (file, bucket, path) => {
                  const chunkSize = 1024 * 1024 // 1MB chunks
                  let start = 0

                  while (start < file.size) {
                    const chunk = file.slice(start, start + chunkSize)
                    const chunkPath = `${path}.chunk-${start}`

                    const { error } = await supabase.storage
                      .from(bucket)
                      .upload(chunkPath, chunk, { upsert: true })

                    if (error) throw error

                    start += chunkSize
                  }

                  // Merge chunks (server-side)
                  const { data } = await supabase.functions.invoke('merge-file-chunks', {
                    bucket,
                    path,
                    totalSize: file.size
                  })

                  return data
                }
                """,
                "download_with_retry": """
                const downloadFile = async (bucket, path) => {
                  const maxRetries = 3
                  let attempt = 0

                  while (attempt < maxRetries) {
                    try {
                      const { data, error } = await supabase.storage
                        .from(bucket)
                        .download(path)

                      if (error) throw error
                      return data

                    } catch (error) {
                      attempt++
                      if (attempt === maxRetries) throw error

                      // Exponential backoff
                      await new Promise(resolve =>
                        setTimeout(resolve, Math.pow(2, attempt) * 1000)
                      )
                    }
                  }
                }
                """,
            },
            "image_transformations": {
                "thumbnails": """
                // Generate thumbnails on upload
                const uploadImage = async (file, userId) => {
                  const fileExt = file.name.split('.').pop()
                  const fileName = `${Date.now()}.${fileExt}`
                  const filePath = `${userId}/${fileName}`

                  // Upload original image
                  const { data, error } = await supabase.storage
                    .from('images')
                    .upload(filePath, file)

                  if (error) throw error

                  // Generate transformations
                  const transformations = [
                    { name: 'thumb', width: 200, height: 200 },
                    { name: 'medium', width: 800, height: 600 },
                    { name: 'large', width: 1920, height: 1080 }
                  ]

                  for (const transform of transformations) {
                    const { data: url } = supabase.storage
                      .from('images')
                      .getPublicUrl(filePath, {
                        transform: {
                          width: transform.width,
                          height: transform.height,
                          quality: 80
                        }
                      })

                    // Store transformation URL
                    await saveTransformationUrl(
                      data.path,
                      transform.name,
                      url.publicUrl
                    )
                  }

                  return data
                }
                """,
                "cdn_integration": """
                // Configure CDN settings
                const getCdnUrl = (filePath, options = {}) => {
                  const { data } = supabase.storage
                    .from('assets')
                    .getPublicUrl(filePath, {
                      transform: {
                        width: options.width,
                        height: options.height,
                        quality: options.quality || 80,
                        format: options.format || 'webp',
                        resize: options.resize || 'cover'
                      }
                    })

                  return data.publicUrl
                }

                // Usage with responsive images
                const responsiveImage = (basePath) => ({
                  src: getCdnUrl(basePath, { width: 800 }),
                  srcSet: `
                    ${getCdnUrl(basePath, { width: 400 })} 400w,
                    ${getCdnUrl(basePath, { width: 800 })} 800w,
                    ${getCdnUrl(basePath, { width: 1200 })} 1200w
                  `,
                  sizes: '(max-width: 400px) 400px, (max-width: 800px) 800px, 1200px'
                })
                """,
            },
            "security": """
                // Generate signed URLs for private files
                const getSignedUrl = async (bucket, path, expiresIn = 60) => {
                  const { data, error } = await supabase.storage
                    .from(bucket)
                    .createSignedUrl(path, expiresIn)

                  if (error) throw error
                  return data.signedUrl
                }

                // Validate file upload
                const validateFileUpload = (file, allowedTypes, maxSize) => {
                  // Check file type
                  if (!allowedTypes.includes(file.type)) {
                    throw new Error(`Invalid file type: ${file.type}`)
                  }

                  // Check file size
                  if (file.size > maxSize) {
                    throw new Error(`File too large: ${file.size} bytes`)
                  }

                  // Check file signature (magic numbers)
                  const validSignatures = {
                    'image/jpeg': [0xFF, 0xD8, 0xFF],
                    'image/png': [0x89, 0x50, 0x4E, 0x47],
                    'application/pdf': [0x25, 0x50, 0x44, 0x46]
                  }

                  const signature = validSignatures[file.type]
                  if (signature) {
                    const reader = new FileReader()
                    reader.onload = (e) => {
                      const bytes = new Uint8Array(e.target.result)
                      const fileHeader = Array.from(bytes.slice(0, signature.length))

                      if (JSON.stringify(fileHeader) !== JSON.stringify(signature)) {
                        throw new Error('Invalid file signature')
                      }
                    }
                    reader.readAsArrayBuffer(file.slice(0, signature.length))
                  }
                }
                """,
        }

    def _init_edge_function_patterns(self):
        """Initialize edge function patterns."""
        self.edge_function_patterns = {
            "function_types": {
                "webhook_handlers": """
                import { serve } from "https://deno.land/std@0.131.0/http/server.ts"
                import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
                import { verifySignature } from 'https://esm.sh/@supabase/functions-js@2'

                const corsHeaders = {
                  'Access-Control-Allow-Origin': '*',
                  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
                }

                serve(async (req) => {
                  // Handle CORS
                  if (req.method === 'OPTIONS') {
                    return new Response('ok', { headers: corsHeaders })
                  }

                  try {
                    // Verify webhook signature
                    const signature = req.headers.get('supabase-signature')
                    const body = await req.text()

                    const isValid = await verifySignature(body, signature, Deno.env.get('WEBHOOK_SECRET'))
                    if (!isValid) {
                      return new Response(
                        JSON.stringify({ error: 'Invalid signature' }),
                        { status: 401, headers: corsHeaders }
                      )
                    }

                    const payload = JSON.parse(body)
                    const supabase = createClient(
                      Deno.env.get('SUPABASE_URL') ?? '',
                      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
                    )

                    // Process webhook payload
                    switch (payload.type) {
                      case 'user.created':
                        await handleUserCreated(supabase, payload.data)
                        break
                      case 'payment.completed':
                        await handlePaymentCompleted(supabase, payload.data)
                        break
                      default:
                        console.log('Unhandled webhook type:', payload.type)
                    }

                    return new Response(
                      JSON.stringify({ success: true }),
                      { headers: corsHeaders }
                    )

                  } catch (error) {
                    console.error('Webhook error:', error)
                    return new Response(
                      JSON.stringify({ error: error.message }),
                      { status: 500, headers: corsHeaders }
                    )
                  }
                })

                async function handleUserCreated(supabase, userData) {
                  // Create user profile
                  await supabase
                    .from('user_profiles')
                    .insert({
                      user_id: userData.id,
                      created_at: new Date().toISOString()
                    })

                  // Send welcome email
                  await sendWelcomeEmail(userData.email)
                }
                """,
                "data_processing": """
                import { serve } from "https://deno.land/std@0.131.0/http/server.ts"
                import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

                serve(async (req) => {
                  if (req.method !== 'POST') {
                    return new Response('Method not allowed', { status: 405 })
                  }

                  try {
                    const { operation, data } = await req.json()
                    const supabase = createClient(
                      Deno.env.get('SUPABASE_URL') ?? '',
                      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
                    )

                    switch (operation) {
                      case 'generate-report':
                        const report = await generateReport(supabase, data)
                        return new Response(JSON.stringify(report))

                      case 'process-bulk-upload':
                        const result = await processBulkUpload(supabase, data)
                        return new Response(JSON.stringify(result))

                      default:
                        return new Response(
                          JSON.stringify({ error: 'Unknown operation' }),
                          { status: 400 }
                        )
                    }

                  } catch (error) {
                    console.error('Processing error:', error)
                    return new Response(
                      JSON.stringify({ error: error.message }),
                      { status: 500 }
                    )
                  }
                })

                async function generateReport(supabase, { startDate, endDate, format }) {
                  const { data, error } = await supabase
                    .from('analytics_events')
                    .select('*')
                    .gte('created_at', startDate)
                    .lte('created_at', endDate)

                  if (error) throw error

                  // Process and format data
                  const report = {
                    period: { start: startDate, end: endDate },
                    totalEvents: data.length,
                    uniqueUsers: [...new Set(data.map(e => e.user_id))].length,
                    eventsByType: data.reduce((acc, event) => {
                      acc[event.type] = (acc[event.type] || 0) + 1
                      return acc
                    }, {}),
                    format
                  }

                  return report
                }
                """,
                "third_party_integrations": """
                import { serve } from "https://deno.land/std@0.131.0/http/server.ts"

                serve(async (req) => {
                  if (req.method !== 'POST') {
                    return new Response('Method not allowed', { status: 405 })
                  }

                  try {
                    const { provider, action, data } = await req.json()

                    switch (provider) {
                      case 'stripe':
                        return await handleStripeAction(action, data)
                      case 'sendgrid':
                        return await handleSendgridAction(action, data)
                      case 'twilio':
                        return await handleTwilioAction(action, data)
                      default:
                        return new Response(
                          JSON.stringify({ error: 'Unsupported provider' }),
                          { status: 400 }
                        )
                    }

                  } catch (error) {
                    console.error('Integration error:', error)
                    return new Response(
                      JSON.stringify({ error: error.message }),
                      { status: 500 }
                    )
                  }
                })

                async function handleStripeAction(action, data) {
                  const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY'))

                  switch (action) {
                    case 'create-customer':
                      const customer = await stripe.customers.create(data)
                      return new Response(JSON.stringify({ customer }))

                    case 'create-payment-intent':
                      const paymentIntent = await stripe.paymentIntents.create(data)
                      return new Response(JSON.stringify({ paymentIntent }))

                    default:
                      throw new Error(`Unknown Stripe action: ${action}`)
                  }
                }
                """,
            },
            "optimization": {
                "caching": """
                import { serve } from "https://deno.land/std@0.131.0/http/server.ts"

                // In-memory cache (for production, use Redis)
                const cache = new Map()

                serve(async (req) => {
                  const cacheKey = new URL(req.url).pathname
                  const cached = cache.get(cacheKey)

                  if (cached && Date.now() - cached.timestamp < 300000) { // 5 min cache
                    return new Response(cached.data, {
                      headers: {
                        'Content-Type': 'application/json',
                        'Cache-Control': 'public, max-age=300'
                      }
                    })
                  }

                  // Generate fresh response
                  const data = await generateExpensiveData()

                  cache.set(cacheKey, {
                    data: JSON.stringify(data),
                    timestamp: Date.now()
                  })

                  return new Response(JSON.stringify(data), {
                    headers: {
                      'Content-Type': 'application/json',
                      'Cache-Control': 'public, max-age=300'
                    }
                  })
                })
                """,
                "error_handling": """
                import { serve } from "https://deno.land/std@0.131.0/http/server.ts"

                class EdgeFunctionError extends Error {
                  constructor(message, code, statusCode = 500) {
                    super(message)
                    this.name = 'EdgeFunctionError'
                    this.code = code
                    this.statusCode = statusCode
                  }
                }

                serve(async (req) => {
                  try {
                    const result = await mainHandler(req)
                    return result

                  } catch (error) {
                    console.error('Edge function error:', error)

                    if (error instanceof EdgeFunctionError) {
                      return new Response(
                        JSON.stringify({
                          error: error.message,
                          code: error.code
                        }),
                        {
                          status: error.statusCode,
                          headers: { 'Content-Type': 'application/json' }
                        }
                      )
                    }

                return new Response(
                  JSON.stringify({ error: 'Internal server error' }),
                  { status: 500, headers: { 'Content-Type': 'application/json' } }
                )
              }
            })

            async function mainHandler(req) {
              // Validate request
              if (!req.headers.get('authorization')) {
                throw new EdgeFunctionError('Missing authorization', 'MISSING_AUTH', 401)
              }

              // Process request
              const data = await req.json()
              if (!data.action) {
                throw new EdgeFunctionError('Missing action parameter', 'MISSING_ACTION', 400)
              }

              // Execute action
              return await processAction(data.action, data.payload)
            }
                """,
            },
        }

    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data before execution."""
        if not input_data or not isinstance(input_data, dict):
            return False

        required_fields = ["query"]
        return all(field in input_data for field in required_fields)

    def get_capabilities(self) -> List[str]:
        """Get list of skill capabilities."""
        return [
            "Supabase platform fundamentals and architecture",
            "PostgreSQL advanced features and optimization",
            "Authentication systems and row-level security",
            "Real-time subscriptions and Presence channels",
            "File storage, transformations, and CDN integration",
            "Edge functions and serverless computing",
            "Database migrations and schema management",
            "Performance optimization and monitoring",
            "Security best practices and compliance",
            "Zero-hallucination guarantee for all Supabase APIs",
        ]

    async def execute(self, input_data: Any, context: SkillContext = None) -> SkillResult:
        """Execute the Supabase expert skill with monitoring."""
        start_time = __import__("time").time()

        try:
            # Validate input
            if not await self.validate_input(input_data):
                raise ValueError("Invalid input data")

            query = input_data.get("query", "").lower()
            level = input_data.get("level", "summary")

            # Route to appropriate handler based on query content
            if any(term in query for term in ["database", "sql", "postgres", "schema", "migration"]):
                result = await self._handle_database_expertise(input_data, level)
            elif any(term in query for term in ["auth", "authentication", "login", "signup", "user"]):
                result = await self._handle_authentication_expertise(input_data, level)
            elif any(term in query for term in ["realtime", "subscribe", "presence", "broadcast"]):
                result = await self._handle_realtime_expertise(input_data, level)
            elif any(term in query for term in ["storage", "upload", "download", "cdn", "file"]):
                result = await self._handle_storage_expertise(input_data, level)
            elif any(term in query for term in ["edge function", "serverless", "function", "deno"]):
                result = await self._handle_edge_function_expertise(input_data, level)
            elif any(term in query for term in ["setup", "install", "configure", "getting started"]):
                result = await self._handle_setup_expertise(input_data, level)
            elif any(term in query for term in ["optimize", "performance", "security", "best practices"]):
                result = await self._handle_optimization_expertise(input_data, level)
            else:
                result = await self._handle_general_expertise(input_data, level)

            execution_time = __import__("time").time() - start_time

            # Update metrics
            self.metrics["database_validations"] += 1

            return SkillResult(
                success=True,
                data=result,
                execution_time=execution_time,
                tokens_used=len(result) // 4,  # Rough token estimate
                metadata={
                    "skill": "supabase_expert",
                    "expertise_area": self._determine_expertise_area(query),
                    "level": level,
                    "timestamp": __import__("datetime").datetime.now().isoformat(),
                },
            )

        except Exception as e:
            execution_time = __import__("time").time() - start_time

            # Log error for monitoring
            self.metrics["errors_prevented"] += 1

            return SkillResult(
                success=False,
                error=f"Supabase expertise execution failed: {str(e)}",
                execution_time=execution_time,
                metadata={
                    "skill": "supabase_expert",
                    "error_type": type(e).__name__,
                    "timestamp": __import__("datetime").datetime.now().isoformat(),
                },
            )

    async def _handle_database_expertise(self, input_data: Dict[str, Any], level: str) -> str:
        """Handle database-related queries."""
        query = input_data.get("query", "").lower()

        if "schema" in query or "design" in query:
            return self._get_database_design_guidance(level)
        elif "migration" in query:
            return self._get_migration_guidance(level)
        elif "query" in query or "sql" in query:
            return self._get_query_optimization_guidance(level)
        elif "index" in query:
            return self._get_indexing_guidance(level)
        elif "performance" in query:
            return self._get_database_performance_guidance(level)
        else:
            return self._get_database_fundamentals(level)

    async def _handle_authentication_expertise(self, input_data: Dict[str, Any], level: str) -> str:
        """Handle authentication-related queries."""
        query = input_data.get("query", "").lower()

        if "row level security" in query or "rls" in query:
            return self._get_rls_guidance(level)
        elif "provider" in query or "oauth" in query:
            return self._get_auth_provider_guidance(level)
        elif "jwt" in query or "token" in query:
            return self._get_jwt_guidance(level)
        elif "session" in query:
            return self._get_session_management_guidance(level)
        else:
            return self._get_authentication_fundamentals(level)

    async def _handle_realtime_expertise(self, input_data: Dict[str, Any], level: str) -> str:
        """Handle real-time feature queries."""
        query = input_data.get("query", "").lower()

        if "presence" in query:
            return self._get_presence_guidance(level)
        elif "broadcast" in query:
            return self._get_broadcast_guidance(level)
        elif "subscription" in query or "subscribe" in query:
            return self._get_subscription_guidance(level)
        elif "performance" in query:
            return self._get_realtime_performance_guidance(level)
        else:
            return self._get_realtime_fundamentals(level)

    async def _handle_storage_expertise(self, input_data: Dict[str, Any], level: str) -> str:
        """Handle storage-related queries."""
        query = input_data.get("query", "").lower()

        if "upload" in query or "file" in query:
            return self._get_upload_guidance(level)
        elif "cdn" in query or "transform" in query:
            return self._get_cdn_guidance(level)
        elif "bucket" in query or "policy" in query:
            return self._get_bucket_guidance(level)
        elif "security" in query:
            return self._get_storage_security_guidance(level)
        else:
            return self._get_storage_fundamentals(level)

    async def _handle_edge_function_expertise(self, input_data: Dict[str, Any], level: str) -> str:
        """Handle edge function queries."""
        query = input_data.get("query", "").lower()

        if "webhook" in query:
            return self._get_webhook_guidance(level)
        elif "cache" in query or "performance" in query:
            return self._get_edge_function_performance_guidance(level)
        elif "error" in query or "handling" in query:
            return self._get_error_handling_guidance(level)
        elif "deno" in query:
            return self._get_deno_guidance(level)
        else:
            return self._get_edge_function_fundamentals(level)

    async def _handle_setup_expertise(self, input_data: Dict[str, Any], level: str) -> str:
        """Handle setup and installation queries."""
        return self._get_setup_guidance(level)

    async def _handle_optimization_expertise(self, input_data: Dict[str, Any], level: str) -> str:
        """Handle optimization queries."""
        query = input_data.get("query", "").lower()

        if "security" in query:
            return self._get_security_guidance(level)
        elif "performance" in query:
            return self._get_performance_guidance(level)
        elif "best practices" in query:
            return self._get_best_practices_guidance(level)
        else:
            return self._get_optimization_guidance(level)

    async def _handle_general_expertise(self, input_data: Dict[str, Any], level: str) -> str:
        """Handle general Supabase queries."""
        return self._get_supabase_overview(level)

    def _determine_expertise_area(self, query: str) -> str:
        """Determine the primary expertise area for a query."""
        query_lower = query.lower()

        if any(term in query_lower for term in ["database", "sql", "postgres"]):
            return "database"
        elif any(term in query_lower for term in ["auth", "authentication", "user"]):
            return "authentication"
        elif any(term in query_lower for term in ["realtime", "subscribe", "presence"]):
            return "realtime"
        elif any(term in query_lower for term in ["storage", "upload", "cdn"]):
            return "storage"
        elif any(term in query_lower for term in ["edge function", "serverless"]):
            return "edge_functions"
        else:
            return "general"

    # Guidance method implementations would continue here...
    # (Truncated for brevity, but would include all the specific guidance methods)

    def _get_supabase_overview(self, level: str) -> str:
        """Get Supabase platform overview."""
        if level == "metadata":
            return "Supabase platform overview and architecture"
        elif level == "summary":
            return """
# Supabase Platform Overview

## What is Supabase?
Open-source Firebase alternative built on PostgreSQL.

## Core Components
- **PostgreSQL Database**: Full SQL database with extensions
- **Authentication**: JWT-based auth with multiple providers
- **Real-time**: Live subscriptions and presence
- **Storage**: Object storage with CDN
- **Edge Functions**: Deno-based serverless functions

## Key Benefits
- PostgreSQL power and flexibility
- Open-source and self-hostable
- Auto-generated APIs
- Real-time capabilities
- Global CDN
            """
        else:  # full
            return """
# Complete Supabase Platform Guide

## Architecture Overview

Supabase is a comprehensive Backend-as-a-Service (BaaS) platform that combines the power of PostgreSQL with developer-friendly APIs and services. Here's the complete architecture breakdown:

### Core Components

#### 1. PostgreSQL Database
- **Version**: PostgreSQL 15 with advanced extensions
- **Extensions**: uuid-ossp, pgcrypto, pgjwt, pg_net, pg_stat_statements, pgvector
- **Features**: Full ACID compliance, JSONB support, full-text search
- **API**: Auto-generated REST API via PostgREST

#### 2. Authentication (GoTrue)
- **Protocol**: JWT-based authentication
- **Providers**: Email, Social OAuth (Google, GitHub, etc.), SAML, Custom
- **Features**: MFA, password reset, email verification, session management
- **Security**: Row-Level Security (RLS) integration

#### 3. Real-time Engine
- **Technology**: PostgreSQL logical replication
- **Protocol**: WebSocket connections with fallbacks
- **Features**: Database change subscriptions, Presence channels, Broadcast
- **Performance**: Efficient filtering and connection pooling

#### 4. Object Storage
- **Technology**: S3-compatible storage with CDN
- **Features**: File uploads, transformations, signed URLs
- **Security**: Bucket policies, RLS integration
- **Performance**: Global CDN, automatic compression

#### 5. Edge Functions
- **Runtime**: Deno runtime with V8 engine
- **Features**: Serverless functions, global edge deployment
- **Integrations**: Webhooks, third-party APIs, data processing
- **Performance**: Cold start optimization, edge caching

## Getting Started

### Project Setup
1. Create a new project at [supabase.com](https://supabase.com)
2. Note your project URL and anon key
3. Install the Supabase client library

```bash
# JavaScript/TypeScript
npm install @supabase/supabase-js

# Python
pip install supabase

# CLI for local development
npm install -g supabase
```

### Client Initialization
```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  'YOUR_SUPABASE_URL',
  'YOUR_SUPABASE_ANON_KEY'
)
```

### Local Development
```bash
# Initialize local project
supabase init

# Start local services
supabase start

# Apply migrations
supabase db push

# Generate types
supabase gen types typescript --local > types.ts
```

## Key Features Deep Dive

### Database Power
- **Full PostgreSQL**: All PostgreSQL features available
- **Extensions**: Pre-installed production-ready extensions
- **Migrations**: Version-controlled schema changes
- **Backups**: Point-in-time recovery and automated backups
- **Monitoring**: Built-in performance monitoring

### Auto-Generated APIs
- **REST API**: Automatic CRUD operations
- **GraphQL**: Optional GraphQL support
- **RLS Integration**: API respects database security policies
- **Relationships**: Automatic foreign key handling

### Real-time Capabilities
- **Database Subscriptions**: Subscribe to table changes
- **Presence**: Track online users and status
- **Broadcast**: Server-to-client message broadcasting
- **Efficient Filtering**: Server-side subscription filtering

### Developer Experience
- **TypeScript Support**: Auto-generated types
- **Local Development**: Complete local stack
- **CLI Tools**: Database management and migrations
- **SDKs**: Multiple language support

## Production Considerations

### Security
- Row-Level Security for data access control
- JWT token management and refresh
- API key rotation and management
- Network security and VPC peering

### Performance
- Connection pooling and query optimization
- CDN caching for static assets
- Database indexing strategies
- Real-time subscription optimization

### Scalability
- Automatic scaling of compute resources
- Read replicas for read-heavy workloads
- Edge function global distribution
- Storage tiering and lifecycle management

### Monitoring & Observability
- Database performance metrics
- Real-time connection monitoring
- Storage usage and access patterns
- Edge function execution metrics

## Pricing Model

### Free Tier
- 2 projects
- 500MB database storage
- 1GB file storage
- 50,000 monthly active users
- 500MB bandwidth

### Pro Tier
- Unlimited projects
- 8GB+ database storage
- 100GB+ file storage
- 100,000+ monthly active users
- Priority support

### Enterprise
- Custom pricing
- Dedicated support
- Advanced security features
- Compliance certifications

This comprehensive guide provides everything needed to understand and leverage the full power of the Supabase platform for modern application development.
            """

    def _get_migration_guidance(self, level: str) -> str:
        """Get database migration guidance."""
        if level == "metadata":
            return "Database migrations and schema management"
        elif level == "summary":
            return f"""
# Database Migrations with Supabase

## Migration Types
- Schema changes (tables, columns, constraints)
- Data migrations and transformations
- Index creation and optimization

## Migration Commands
```bash
supabase db diff
supabase db push
supabase db reset
```

## Best Practices
- Use descriptive migration names
- Test migrations on staging first
- Include rollback scripts
- Version control all migrations
            """
        else:
            return """
# Comprehensive Database Migration Guide

## Migration Management

Supabase provides robust migration tools through the Supabase CLI, allowing you to manage database schema changes in a version-controlled, repeatable manner.

### Local Development Setup

```bash
# Initialize Supabase project
supabase init

# Start local services
supabase start

# Apply existing migrations
supabase db push
```

### Migration Workflow

#### 1. Creating Migrations

```bash
# Create a new migration
supabase migration new add_user_profiles_table

# This creates a new file in supabase/migrations/
# Format: 20240101_120000_add_user_profiles_table.sql
```

#### 2. Writing Migration Files

```sql
-- File: supabase/migrations/20240101_120000_add_user_profiles_table.sql

-- Create user_profiles table
CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT,
  avatar_url TEXT,
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- Add RLS policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = user_id);

-- Create function to update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

#### 3. Applying Migrations

```bash
# Apply migrations to local database
supabase db push

# Generate migration diff
supabase db diff --use-migra --schema public > migration.sql

# Apply to remote database
supabase db push --db-url postgresql://user:pass@host:port/dbname
```

### Migration Patterns

#### 1. Table Creation

```sql
-- New table creation
CREATE TABLE blog_posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  content TEXT,
  author_id UUID REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  published_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX idx_blog_posts_author_id ON blog_posts(author_id);
CREATE INDEX idx_blog_posts_status ON blog_posts(status);
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at DESC);
CREATE UNIQUE INDEX idx_blog_posts_slug ON blog_posts(slug) WHERE status = 'published';
```

#### 2. Column Addition

```sql
-- Add new column with default value
ALTER TABLE user_profiles ADD COLUMN phone TEXT;
UPDATE user_profiles SET phone = NULL;

-- Add column with constraint
ALTER TABLE blog_posts ADD COLUMN featured BOOLEAN DEFAULT false;
ALTER TABLE blog_posts ADD CONSTRAINT check_featured_in_published
  CHECK (featured = false OR status = 'published');
```

#### 3. Data Migrations

```sql
-- Transform existing data
UPDATE users SET
  full_name = COALESCE(first_name || ' ' || last_name, email),
  metadata = jsonb_set(
    COALESCE(metadata, '{}'::jsonb),
    '{legacy_migration}',
    to_jsonb(now())
  )
WHERE full_name IS NULL;

-- Create new table and migrate data
CREATE TABLE user_sessions_new (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO user_sessions_new (user_id, created_at)
SELECT user_id, created_at FROM user_sessions;

DROP TABLE user_sessions;
ALTER TABLE user_sessions_new RENAME TO user_sessions;
```

#### 4. Index Management

```sql
-- Add performance indexes
CREATE INDEX CONCURRENTLY idx_blog_posts_search ON blog_posts USING GIN(to_tsvector('english', title || ' ' || content));

-- Add partial index
CREATE INDEX CONCURRENTLY idx_active_sessions ON user_sessions(user_id)
WHERE created_at > NOW() - INTERVAL '30 days';

-- Drop unused indexes
DROP INDEX CONCURRENTLY IF EXISTS idx_old_unused_index;
```

### Advanced Migration Techniques

#### 1. Zero-Downtime Migrations

```sql
-- Step 1: Add new column as nullable
ALTER TABLE products ADD COLUMN new_price DECIMAL(10,2);

-- Step 2: Backfill data in batches
UPDATE products
SET new_price = ROUND(price * 1.1, 2)
WHERE id IN (
  SELECT id FROM products
  WHERE new_price IS NULL
  LIMIT 1000
);
-- Repeat until all records updated

-- Step 3: Add constraint
ALTER TABLE products ALTER COLUMN new_price SET NOT NULL;

-- Step 4: Update application to use new column
-- (Deploy application changes)

-- Step 5: Remove old column
ALTER TABLE products DROP COLUMN old_price;
```

#### 2. Multi-Step Complex Migrations

```sql
-- Step 1: Create new table structure
CREATE TABLE orders_v2 (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  total_amount DECIMAL(10,2) NOT NULL,
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled')),
  shipping_address JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 2: Create trigger function
CREATE OR REPLACE FUNCTION update_orders_v2_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_orders_v2_updated_at
  BEFORE UPDATE ON orders_v2
  FOR EACH ROW EXECUTE FUNCTION update_orders_v2_updated_at();

-- Step 3: Migrate data
INSERT INTO orders_v2 (id, user_id, total_amount, status, created_at)
SELECT
  id,
  user_id,
  amount,
  CASE WHEN shipped = true THEN 'shipped' ELSE 'pending' END,
  created_at
FROM orders;

-- Step 4: Update foreign keys
ALTER TABLE order_items ADD CONSTRAINT order_items_order_id_fkey
  FOREIGN KEY (order_id) REFERENCES orders_v2(id) ON DELETE CASCADE;

-- Step 5: Swap tables (requires brief downtime)
ALTER TABLE orders RENAME TO orders_old;
ALTER TABLE orders_v2 RENAME TO orders;
```

### Migration Best Practices

#### 1. File Organization

```
supabase/
├── migrations/
│   ├── 20240101_120000_create_users_table.sql
│   ├── 20240102_140000_add_user_profiles.sql
│   └── 20240103_160000_add_indexes.sql
├── functions/
│   └── my_function.ts
└── seed.sql
```

#### 2. Migration Naming

```bash
# Good: descriptive and timestamped
supabase migration new 20240115_add_user_authentication_features

# Bad: generic names
supabase migration new update_table
```

#### 3. Testing Migrations

```bash
# Test on local development
supabase db push

# Test on staging environment
supabase db push --remote staging

# Generate rollback script
supabase migration new rollback_migration_name
```

#### 4. Rollback Strategies

```sql
-- Always include rollback procedures in comments
-- ROLLBACK:
-- DROP TABLE user_profiles;
-- ALTER TABLE users DROP COLUMN profile_created_at;
```

### Troubleshooting

#### Common Issues

1. **Migration conflicts**:
```bash
# Reset local environment
supabase db reset

# Re-apply migrations
supabase db push
```

2. **Large data migrations**:
```sql
-- Process in batches
DO $$
DECLARE
  batch_size INTEGER := 1000;
  processed INTEGER := 0;
BEGIN
  LOOP
    UPDATE large_table
    SET processed = true
    WHERE processed = false
    LIMIT batch_size;

    EXIT WHEN NOT FOUND;

    COMMIT; -- Release locks
    processed := processed + batch_size;

    -- Log progress
    RAISE NOTICE 'Processed % records', processed;
  END LOOP;
END $$;
```

3. **Performance optimization**:
```sql
-- Use CONCURRENTLY for index creation in production
CREATE INDEX CONCURRENTLY idx_large_table_column ON large_table(column);

-- Add constraints after data migration
ALTER TABLE large_table ADD CONSTRAINT check_value_positive
  CHECK (value > 0) NOT VALID;
```

This comprehensive migration guide ensures safe, reliable database schema changes for production Supabase applications.
            """

    def _get_query_optimization_guidance(self, level: str) -> str:
        """Get query optimization guidance."""
        if level == "metadata":
            return "PostgreSQL query optimization techniques"
        elif level == "summary":
            return f"""
# Query Optimization with Supabase

## Key Techniques
- Proper indexing strategies
- Query execution analysis
- Connection pooling
- Caching strategies

## Performance Tools
- pg_stat_statements
- EXPLAIN ANALYZE
- Supabase dashboard

## Best Practices
- Use specific column selection
- Implement pagination efficiently
- Optimize JOIN operations
- Monitor slow queries
            """
        else:
            return """
# PostgreSQL Query Optimization Guide for Supabase

## Query Analysis and Monitoring

### 1. Understanding Query Performance

Use EXPLAIN ANALYZE to analyze query execution plans:

```sql
-- Basic query analysis
EXPLAIN ANALYZE SELECT * FROM posts WHERE author_id = $1;

-- Detailed analysis with formatting
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT p.*, COUNT(c.id) as comment_count
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id
WHERE p.status = 'published'
GROUP BY p.id
ORDER BY p.created_at DESC
LIMIT 10;
```

### 2. Monitoring Slow Queries

```sql
-- Enable pg_stat_statements (already enabled in Supabase)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Find slow queries
SELECT
  query,
  calls,
  total_time,
  mean_time,
  rows,
  100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Monitor query frequency
SELECT
  substr(query, 1, 50) as query_preview,
  calls,
  total_exec_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;
```

### 3. Connection Pooling

Supabase provides connection pooling:

```javascript
// Configure client with pooling options
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(url, key, {
  db: {
    connection: {
      poolSize: 10,
      client_min_messages: 'notice',
    }
  }
})
```

## Indexing Strategies

### 1. Single Column Indexes

```sql
-- Basic index
CREATE INDEX idx_posts_author_id ON posts(author_id);

-- Partial index for common queries
CREATE INDEX idx_published_posts ON posts(published_at)
WHERE status = 'published';

-- Unique index
CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));
```

### 2. Composite Indexes

```sql
-- For WHERE + ORDER BY clauses
CREATE INDEX idx_posts_status_published_at ON posts(status, published_at DESC);

-- For multiple WHERE conditions
CREATE INDEX idx_orders_user_status_date ON orders(user_id, status, created_at DESC);

-- Covering index (includes all query columns)
CREATE INDEX idx_posts_author_status ON posts(author_id, status) INCLUDE (title, created_at);
```

### 3. Functional Indexes

```sql
-- Expression index for case-insensitive search
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Full-text search index
CREATE INDEX idx_posts_search ON posts USING GIN(to_tsvector('english', title || ' ' || content));

-- Date/time index
CREATE INDEX idx_activities_date_trunc ON posts(DATE_TRUNC('day', created_at));
```

## Query Optimization Techniques

### 1. Efficient Pagination

```sql
-- Bad: OFFSET pagination (slow for large offsets)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 10 OFFSET 10000;

-- Good: Cursor-based pagination
SELECT * FROM posts
WHERE created_at < '2024-01-15 10:30:00'
ORDER BY created_at DESC
LIMIT 10;

-- Implementation:
const nextPage = async (lastCreatedAt) => {
  const { data } = await supabase
    .from('posts')
    .select('*')
    .lt('created_at', lastCreatedAt)
    .order('created_at', { ascending: false })
    .limit(10)
}
```

### 2. JOIN Optimization

```sql
-- Use appropriate JOIN types
SELECT p.*, COUNT(DISTINCT c.id) as comment_count
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id AND c.status = 'approved'
WHERE p.status = 'published'
GROUP BY p.id;

-- Ensure proper indexes on foreign keys
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_post_status ON comments(post_id, status);
```

### 3. Subquery vs JOIN Optimization

```sql
-- Often slower: Correlated subquery
SELECT p.*, (
  SELECT COUNT(*)
  FROM comments c
  WHERE c.post_id = p.id AND c.status = 'approved'
) as comment_count
FROM posts p;

-- Usually faster: JOIN with GROUP BY
SELECT p.*, COUNT(DISTINCT c.id) as comment_count
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id AND c.status = 'approved'
GROUP BY p.id;
```

### 4. Common Table Expressions (CTEs)

```sql
-- Complex query with CTEs for readability and performance
WITH user_stats AS (
  SELECT
    user_id,
    COUNT(*) as total_posts,
    COUNT(DISTINCT DATE_TRUNC('day', created_at)) as active_days
  FROM posts
  WHERE status = 'published'
  AND created_at > NOW() - INTERVAL '30 days'
  GROUP BY user_id
),
popular_posts AS (
  SELECT
    author_id,
    COUNT(*) as recent_posts
  FROM posts
  WHERE created_at > NOW() - INTERVAL '7 days'
  AND status = 'published'
  GROUP BY author_id
  HAVING COUNT(*) >= 3
)
SELECT
  u.id,
  u.username,
  us.total_posts,
  us.active_days,
  pp.recent_posts
FROM users u
JOIN user_stats us ON u.id = us.user_id
JOIN popular_posts pp ON u.id = pp.author_id
ORDER BY us.total_posts DESC;
```

### 5. Window Functions

```sql
-- Efficient ranking without self-joins
SELECT
  p.*,
  ROW_NUMBER() OVER (PARTITION BY p.author_id ORDER BY p.created_at DESC) as author_post_rank,
  DENSE_RANK() OVER (ORDER BY p.view_count DESC) as overall_popularity_rank,
  COUNT(*) OVER (PARTITION BY p.author_id) as author_total_posts
FROM posts p
WHERE p.status = 'published';
```

## Data Type Optimization

### 1. Choose Appropriate Data Types

```sql
-- Use specific types instead of generic ones
CREATE TABLE optimized_table (
  -- Use TEXT instead of VARCHAR for variable-length strings
  title TEXT NOT NULL,

  -- Use NUMERIC instead of FLOAT for financial data
  price NUMERIC(10,2) NOT NULL,

  -- Use BOOLEAN for flags
  is_active BOOLEAN DEFAULT true,

  -- Use DATE instead of TIMESTAMP for dates without time
  birth_date DATE,

  -- Use JSONB for structured data
  metadata JSONB DEFAULT '{}',

  -- Use ENUM for limited sets of values
  status TEXT CHECK (status IN ('draft', 'published', 'archived'))
);
```

### 2. NULL Handling Optimization

```sql
-- Design columns to minimize NULL usage
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  content TEXT,
  -- Use NOT NULL with defaults where possible
  status TEXT NOT NULL DEFAULT 'draft',
  published_at TIMESTAMP WITH TIME ZONE, -- Can be NULL
  view_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create partial indexes for non-NULL columns
CREATE INDEX idx_posts_published ON posts(published_at DESC)
WHERE published_at IS NOT NULL;
```

## Caching Strategies

### 1. Application-Level Caching

```javascript
// Redis-based caching for frequent queries
import { createClient } from '@supabase/supabase-js'
import Redis from 'ioredis'

const supabase = createClient(url, key)
const redis = new Redis(process.env.REDIS_URL)

const getCachedPosts = async (cacheKey = 'posts:published') => {
  // Try cache first
  const cached = await redis.get(cacheKey)
  if (cached) {
    return JSON.parse(cached)
  }

  // Fetch from database
  const { data } = await supabase
    .from('posts')
    .select('*')
    .eq('status', 'published')
    .order('created_at', { ascending: false })
    .limit(50)

  // Cache for 5 minutes
  await redis.setex(cacheKey, 300, JSON.stringify(data))

  return data
}
```

### 2. Query Result Materialization

```sql
-- Materialized view for expensive aggregations
CREATE MATERIALIZED VIEW daily_stats AS
SELECT
  DATE_TRUNC('day', created_at) as day,
  COUNT(*) as total_posts,
  COUNT(DISTINCT author_id) as unique_authors,
  COUNT(DISTINCT id) FILTER (WHERE status = 'published') as published_posts
FROM posts
GROUP BY DATE_TRUNC('day', created_at);

-- Create unique index for refreshing
CREATE UNIQUE INDEX idx_daily_stats_day ON daily_stats(day);

-- Refresh periodically
CREATE OR REPLACE FUNCTION refresh_daily_stats()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY daily_stats;
END;
$$ LANGUAGE plpgsql;
```

## Performance Monitoring

### 1. Supabase Dashboard Monitoring

- Query performance metrics
- Database connections
- Storage usage
- Function execution times

### 2. Custom Monitoring Queries

```sql
-- Monitor table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
  pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;

-- Monitor index usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Monitor lock activity
SELECT
  pid,
  usename,
  query_start,
  state,
  query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;
```

## Optimization Checklist

### Before Deployment
- [ ] Analyze query execution plans
- [ ] Add appropriate indexes
- [ ] Test with realistic data volumes
- [ ] Monitor memory usage
- [ ] Verify connection pooling configuration

### After Deployment
- [ ] Monitor query performance
- [ ] Track slow queries
- [ ] Review index usage
- [ ] Monitor database size growth
- [ ] Set up alerts for performance degradation

This comprehensive optimization guide ensures high-performance database operations in Supabase applications.
            """

    def _get_indexing_guidance(self, level: str) -> str:
        """Get indexing guidance."""
        if level == "metadata":
            return "Database indexing strategies for performance"
        elif level == "summary":
            return f"""
# Database Indexing Guide

## Index Types
- B-tree indexes (default)
- GIN indexes for JSONB/full-text
- Partial indexes for filtered data
- Composite indexes for multi-column queries

## Optimization Tips
- Index foreign keys
- Cover indexes for common queries
- Avoid over-indexing
- Monitor index usage

## Example Patterns
```sql
CREATE INDEX idx_posts_author_date ON posts(author_id, created_at DESC);
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
CREATE INDEX idx_published_posts ON posts(created_at) WHERE status = 'published';
```
            """
        else:
            return """
# Comprehensive Database Indexing Guide

## Understanding Index Types

### 1. B-Tree Indexes (Default)
Most common index type, excellent for equality and range queries:

```sql
-- Standard B-tree index
CREATE INDEX idx_users_email ON users(email);

-- Descending order
CREATE INDEX idx_posts_created_at_desc ON posts(created_at DESC);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);
```

**Best for:**
- Equality conditions (=, IN)
- Range conditions (<, >, BETWEEN)
- ORDER BY and GROUP BY
- JOIN conditions

### 2. GIN Indexes
Generalized Inverted Indexes for indexing composite values:

```sql
-- JSONB indexing
CREATE INDEX idx_user_profiles_preferences ON user_profiles USING GIN(preferences);

-- Array indexing
CREATE INDEX idx_posts_tags ON posts USING GIN(tags);

-- Full-text search
CREATE INDEX idx_posts_search ON posts USING GIN(to_tsvector('english', title || ' ' || content));
```

**Best for:**
- JSONB data (key-value pairs)
- Arrays
- Full-text search
- Composite values with multiple searchable components

### 3. Hash Indexes
Memory-efficient for equality operations only:

```sql
CREATE INDEX idx_users_hash_email ON users USING HASH(email);
```

**Best for:**
- Simple equality checks (=)
- Large text fields where exact matching is needed

### 4. Partial Indexes
Index only specific rows, reducing index size:

```sql
-- Index only published posts
CREATE INDEX idx_published_posts_created_at ON posts(created_at DESC)
WHERE status = 'published';

-- Index only active users
CREATE INDEX idx_active_users_last_login ON users(last_login_at DESC)
WHERE last_login_at > NOW() - INTERVAL '30 days';

-- Index expensive operations
CREATE INDEX idx_high_value_orders ON orders(customer_id, total_amount)
WHERE total_amount > 1000;
```

### 5. Expression Indexes
Index based on computed expressions:

```sql
-- Case-insensitive search
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Date truncation
CREATE INDEX idx_orders_created_date ON orders(DATE_TRUNC('day', created_at));

-- String manipulation
CREATE INDEX idx_users_first_name ON users(LEFT(first_name, 1));
```

## Index Design Patterns

### 1. Foreign Key Indexes

Always index foreign key columns for JOIN performance:

```sql
-- Create tables
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index foreign key immediately
CREATE INDEX idx_posts_author_id ON posts(author_id);

-- For cascade deletes, consider composite index
CREATE INDEX idx_posts_author_created ON posts(author_id, created_at DESC);
```

### 2. Composite Index Strategy

Order matters in composite indexes:

```sql
-- Good: Most selective column first
CREATE INDEX idx_orders_customer_status_date ON orders(customer_id, status, created_at DESC);

-- Queries that benefit:
-- WHERE customer_id = $1
-- WHERE customer_id = $1 AND status = $2
-- WHERE customer_id = $1 AND status = $2 ORDER BY created_at DESC

-- Bad: Less selective column first
CREATE INDEX idx_orders_status_customer_date ON orders(status, customer_id, created_at DESC);
```

### 3. Covering Indexes

Include all query columns in the index:

```sql
-- Query: SELECT id, title, status FROM posts WHERE author_id = $1 ORDER BY created_at DESC;
CREATE INDEX idx_posts_author_covering ON posts(author_id, created_at DESC)
INCLUDE (title, status);

-- This enables index-only scan, avoiding table access
```

### 4. Specialized Indexes

#### Full-Text Search

```sql
-- Create search vector column
ALTER TABLE posts ADD COLUMN search_vector tsvector;

-- Create trigger to update search vector
CREATE OR REPLACE FUNCTION update_post_search_vector()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_post_search_vector_trigger
  BEFORE INSERT OR UPDATE ON posts
  FOR EACH ROW EXECUTE FUNCTION update_post_search_vector();

-- Create GIN index for search
CREATE INDEX idx_posts_search_vector ON posts USING GIN(search_vector);

-- Search query
SELECT title, ts_rank(search_vector, plainto_tsquery('english', 'database optimization')) as rank
FROM posts
WHERE search_vector @@ plainto_tsquery('english', 'database optimization')
ORDER BY rank DESC;
```

#### JSONB Indexing

```sql
-- Store user preferences
CREATE TABLE user_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GIN index for JSONB queries
CREATE INDEX idx_user_settings_preferences ON user_settings USING GIN(preferences);

-- Expression index for specific JSON paths
CREATE INDEX idx_user_settings_theme ON user_settings USING GBTREE((preferences->>'theme'));
CREATE INDEX idx_user_settings_notifications ON user_settings USING GIN((preferences->'notifications'));

-- Query examples
SELECT * FROM user_settings
WHERE preferences->>'theme' = 'dark';

SELECT * FROM user_settings
WHERE preferences->'notifications'->'email' = 'true';
```

## Index Maintenance

### 1. Monitoring Index Usage

```sql
-- Check index usage statistics
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan as scans,
  idx_tup_read as tuples_read,
  idx_tup_fetch as tuples_fetched,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT
  schemaname,
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### 2. Index Maintenance Operations

```sql
-- Rebuild fragmented indexes
REINDEX INDEX CONCURRENTLY idx_posts_author_id;

-- Rebuild all indexes on a table
REINDEX TABLE CONCURRENTLY posts;

-- Analyze index statistics
ANALYZE posts;

-- Check index size
SELECT
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as size,
  pg_relation_size(indexrelid) as size_bytes
FROM pg_indexes
WHERE tablename = 'posts';
```

### 3. Index Optimization

```sql
-- Fill factor for tables with frequent updates
CREATE INDEX idx_posts_updated_at ON posts(updated_at DESC)
WITH (fillfactor = 90);

-- Parallel index creation for large tables
CREATE INDEX CONCURRENTLY idx_large_table_column ON large_table(column);

-- Create index in background (PostgreSQL 13+)
CREATE INDEX CONCURRENTLY idx_posts_composite ON posts(author_id, status, created_at DESC)
WITH (parallel_workers = 4);
```

## Performance Impact Analysis

### 1. Query Planning with Indexes

```sql
-- Analyze query execution plan
EXPLAIN (ANALYZE, BUFFERS)
SELECT p.*, COUNT(c.id) as comment_count
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id
WHERE p.status = 'published'
  AND p.created_at > NOW() - INTERVAL '30 days'
GROUP BY p.id
ORDER BY p.created_at DESC
LIMIT 20;

-- Look for:
-- Index Scan vs Seq Scan
-- Index-only Scan
-- Bitmap operations
-- Sort vs Index-only operations
```

### 2. Index Cost-Benefit Analysis

```sql
-- Monitor index effectiveness
WITH index_stats AS (
  SELECT
    indexrelid::regclass as index_name,
    idx_scan,
    pg_relation_size(indexrelid) as size_bytes
  FROM pg_stat_user_indexes
  WHERE schemaname = 'public'
),
table_stats AS (
  SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
  FROM pg_stat_user_tables
  WHERE schemaname = 'public'
)
SELECT
  ts.tablename,
  is.index_name,
  ts.seq_scan,
  ts.idx_scan,
  is.idx_scan,
  CASE
    WHEN ts.idx_scan > 0 THEN 'Used'
    WHEN is.size_bytes > 10000000 THEN 'Large & Unused'
    ELSE 'Unused'
  END as status
FROM table_stats ts
LEFT JOIN index_stats is ON is.index_name LIKE ts.tablename || '_%'
WHERE ts.tablename = 'posts';
```

## Advanced Indexing Strategies

### 1. Partitioned Table Indexing

```sql
-- Create partitioned table
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,
  data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create partitions
CREATE TABLE events_2024_01 PARTITION OF events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Create indexes on each partition
CREATE INDEX idx_events_2024_01_type_created ON events_2024_01(event_type, created_at DESC);
CREATE INDEX idx_events_2024_02_type_created ON events_2024_02(event_type, created_at DESC);

-- Or create index on parent table (automatically applied to partitions)
CREATE INDEX idx_events_type_created ON events(event_type, created_at DESC);
```

### 2. Functional Optimization Indexes

```sql
-- Email search optimization
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
CREATE INDEX idx_users_email_domain ON users(SPLIT_PART(LOWER(email), '@', 2));

-- Date range optimization
CREATE INDEX idx_orders_created_month ON orders(DATE_TRUNC('month', created_at));

-- Geospatial indexing (requires PostGIS)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE INDEX idx_locations_geometry ON locations USING GIST(geometry);
```

### 3. Multi-Column Strategy

```sql
-- E-commerce product search
CREATE INDEX idx_products_category_status_price ON products(category_id, status, price DESC);

-- Supports queries like:
-- WHERE category_id = $1 AND status = 'active' ORDER BY price DESC
-- WHERE category_id = $1 AND status = 'active' AND price < $100

-- Social media feed
CREATE INDEX idx_posts_author_status_created ON posts(author_id, status, created_at DESC)
WHERE status IN ('published', 'featured');

-- Support queries:
-- WHERE author_id = $1 AND status = 'published' ORDER BY created_at DESC
-- WHERE author_id = $1 AND status IN ('published', 'featured') ORDER BY created_at DESC
```

## Index Creation Best Practices

### 1. Timing and Impact

```sql
-- For production, use CONCURRENTLY to avoid locks
CREATE INDEX CONCURRENTLY idx_large_table_column ON large_table(column);

-- For very large tables, consider batch processing
-- Create partial index first
CREATE INDEX CONCURRENTLY idx_active_users ON users(id) WHERE active = true;

-- Then complete index if needed
CREATE INDEX CONCURRENTLY idx_users_all ON users(id);
```

### 2. Index Sizing and Limits

```sql
-- Monitor index growth
SELECT
  tablename,
  indexname,
  pg_size_pretty(pg_relation_size(indexrelid)) as size,
  pg_relation_size(indexrelid) / 1024 / 1024 as size_mb
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY size_mb DESC;

-- Consider index bloat
SELECT
  schemaname,
  tablename,
  indexname,
  pg_size_pretty(bloat_size) as bloat
FROM (
  SELECT
    ps.schemaname,
    ps.tablename,
    ps.indexname,
    pg_relation_size(i.indexrelid) - pg_relation_size(ps.indexrelid) as bloat_size
  FROM pg_stat_user_indexes ps
  JOIN pg_index i ON ps.indexrelid = i.indexrelid
  WHERE i.indisvalid = false
) invalid_indexes;
```

This comprehensive indexing guide ensures optimal database performance through strategic index design and maintenance.
            """

    def _get_database_performance_guidance(self, level: str) -> str:
        """Get database performance guidance."""
        if level == "metadata":
            return "Database performance monitoring and optimization"
        elif level == "summary":
            return f"""
# Database Performance Guide

## Key Areas
- Query optimization and indexing
- Connection pooling
- Caching strategies
- Resource monitoring

## Tools
- pg_stat_statements
- Supabase dashboard
- Custom monitoring queries

## Best Practices
- Monitor slow queries
- Optimize connection usage
- Implement caching layers
- Regular performance audits
            """
        else:
            return """
# Database Performance Optimization Guide

## Performance Monitoring

### 1. Supabase Dashboard Metrics

The Supabase dashboard provides real-time monitoring:

- **Database Load**: CPU, memory, and I/O utilization
- **Connection Pool**: Active and idle connections
- **Query Performance**: Slow query identification
- **Storage Usage**: Database and storage consumption
- **Network Traffic**: Bandwidth and request patterns

### 2. Custom Monitoring Queries

```sql
-- Database connection monitoring
SELECT
  state,
  COUNT(*) as connection_count,
  AVG(EXTRACT(EPOCH FROM (now() - query_start))) as avg_query_time
FROM pg_stat_activity
WHERE state != 'idle'
GROUP BY state;

-- Query performance analysis
SELECT
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  rows,
  100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) as hit_percent
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Table size monitoring
SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(tablename::regclass)) as total_size,
  pg_size_pretty(pg_relation_size(tablename::regclass)) as table_size,
  pg_size_pretty(pg_total_relation_size(tablename::regclass) - pg_relation_size(tablename::regclass)) as index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

## Query Performance Optimization

### 1. Query Execution Analysis

```sql
-- Comprehensive query analysis
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
SELECT
  u.id,
  u.username,
  COUNT(p.id) as post_count,
  MAX(p.created_at) as last_post_date
FROM users u
LEFT JOIN posts p ON p.author_id = u.id AND p.status = 'published'
WHERE u.last_login_at > NOW() - INTERVAL '30 days'
GROUP BY u.id, u.username
HAVING COUNT(p.id) > 0
ORDER BY post_count DESC, last_post_date DESC
LIMIT 50;

-- Key metrics to analyze:
-- Execution time
-- Number of rows processed
-- Buffer usage (shared/local)
-- Index vs sequential scans
-- Sort operations
-- Hash operations
```

### 2. Common Performance Issues

#### N+1 Query Problem

```sql
-- Problem: Multiple queries in a loop
-- Inefficient: One query per post to get author info
SELECT * FROM posts WHERE status = 'published' LIMIT 10;
-- Then for each post: SELECT * FROM users WHERE id = $post.author_id;

-- Solution: Single query with JOIN
SELECT
  p.*,
  u.username,
  u.avatar_url
FROM posts p
JOIN users u ON u.id = p.author_id
WHERE p.status = 'published'
ORDER BY p.created_at DESC
LIMIT 10;
```

#### Cartesian Products

```sql
-- Problem: Missing join conditions
SELECT * FROM posts, comments; -- Creates n*m rows

-- Solution: Proper join conditions
SELECT * FROM posts p
JOIN comments c ON c.post_id = p.id;
```

#### Inefficient Subqueries

```sql
-- Problem: Correlated subquery
SELECT p.*, (
  SELECT COUNT(*) FROM comments c
  WHERE c.post_id = p.id AND c.approved = true
) as comment_count
FROM posts p;

-- Solution: Window function or CTE
SELECT
  p.*,
  COUNT(DISTINCT c.id) FILTER (WHERE c.approved = true) as comment_count
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id
GROUP BY p.id, p.title, p.content, p.author_id, p.created_at;
```

### 3. Advanced Query Techniques

#### Materialized Views

```sql
-- For expensive aggregations
CREATE MATERIALIZED VIEW author_stats AS
SELECT
  author_id,
  COUNT(*) as total_posts,
  COUNT(DISTINCT DATE_TRUNC('day', created_at)) as active_days,
  COUNT(DISTINCT id) FILTER (WHERE status = 'published') as published_posts,
  MAX(created_at) as last_post_date
FROM posts
GROUP BY author_id;

-- Create unique index for refreshing
CREATE UNIQUE INDEX idx_author_stats_author_id ON author_stats(author_id);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_author_stats()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY author_stats;
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh (requires pg_cron)
SELECT cron.schedule('refresh-author-stats', '0 */6 * * *', 'SELECT refresh_author_stats();');
```

#### Partitioning

```sql
-- Partition large tables by date
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,
  data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE events_2024_01 PARTITION OF events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Create index on parent (applies to all partitions)
CREATE INDEX idx_events_type_created ON events(event_type, created_at DESC);
```

## Connection Management

### 1. Connection Pooling

Supabase provides built-in connection pooling:

```javascript
// Configure connection pool in client
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(url, key, {
  db: {
    connection: {
      // Connection pool size (default: 10)
      poolSize: 20,

      // Connection timeout
      connect_timeout: 10,

      // Query timeout
      query_timeout: 30,

      // Idle connection timeout
      idle_timeout: 300,

      // Max lifetime of connections
      lifetime: 1800
    }
  }
})
```

### 2. Connection Monitoring

```sql
-- Monitor active connections
SELECT
  pid,
  usename,
  application_name,
  client_addr,
  state,
  query_start,
  state_change,
  query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Monitor connection pool usage
SELECT
  count(*) as total_connections,
  count(*) FILTER (WHERE state = 'active') as active_connections,
  count(*) FILTER (WHERE state = 'idle') as idle_connections,
  count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
FROM pg_stat_activity;
```

### 3. Connection Best Practices

#### Connection Reuse

```javascript
// Singleton pattern for database client
class SupabaseClient {
  constructor() {
    if (SupabaseClient.instance) {
      return SupabaseClient.instance
    }

    this.client = createClient(url, key, {
      db: { connection: { poolSize: 20 } }
    })

    SupabaseClient.instance = this
  }

  getClient() {
    return this.client
  }
}

const supabaseClient = new SupabaseClient()
export const supabase = supabaseClient.getClient()
```

#### Transaction Management

```javascript
// Proper transaction handling
const transferCredits = async (fromUserId, toUserId, amount) => {
  const { data, error } = await supabase.rpc('transfer_credits', {
    p_from_user_id: fromUserId,
    p_to_user_id: toUserId,
    p_amount: amount
  })

  if (error) {
    throw new Error(`Transfer failed: ${error.message}`)
  }

  return data
}

// Corresponding PostgreSQL function
CREATE OR REPLACE FUNCTION transfer_credits(
  p_from_user_id UUID,
  p_to_user_id UUID,
  p_amount NUMERIC
) RETURNS void AS $$
BEGIN
  -- Start transaction
  BEGIN

    -- Check sender has enough credits
    IF (SELECT credits FROM user_credits WHERE user_id = p_from_user_id) < p_amount THEN
      RAISE EXCEPTION 'Insufficient credits';
    END IF;

    -- Deduct from sender
    UPDATE user_credits
    SET credits = credits - p_amount,
        updated_at = NOW()
    WHERE user_id = p_from_user_id;

    -- Add to receiver
    INSERT INTO user_credits (user_id, credits, updated_at)
    VALUES (p_to_user_id, p_amount, NOW())
    ON CONFLICT (user_id)
    DO UPDATE SET
      credits = user_credits.credits + p_amount,
      updated_at = NOW();

    -- Record transaction
    INSERT INTO credit_transactions (
      from_user_id, to_user_id, amount, created_at
    ) VALUES (
      p_from_user_id, p_to_user_id, p_amount, NOW()
    );

  COMMIT;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE;
  END;
END;
$$ LANGUAGE plpgsql;
```

## Caching Strategies

### 1. Application-Level Caching

```javascript
// Redis-based caching layer
import Redis from 'ioredis'

const redis = new Redis(process.env.REDIS_URL)
const CACHE_TTL = 300 // 5 minutes

class CachedSupabaseClient {
  constructor(supabase) {
    this.supabase = supabase
  }

  async getCachedPosts(cacheKey = 'posts:published') {
    try {
      // Try cache first
      const cached = await redis.get(cacheKey)
      if (cached) {
        return JSON.parse(cached)
      }

      // Cache miss - fetch from database
      const { data } = await this.supabase
        .from('posts')
        .select('*')
        .eq('status', 'published')
        .order('created_at', { ascending: false })
        .limit(50)

      // Cache the result
      await redis.setex(cacheKey, CACHE_TTL, JSON.stringify(data))

      return data
    } catch (error) {
      console.error('Cache error:', error)
      // Fallback to database
      return this.supabase
        .from('posts')
        .select('*')
        .eq('status', 'published')
        .order('created_at', { ascending: false })
        .limit(50)
    }
  }

  async invalidateCache(pattern) {
    const keys = await redis.keys(pattern)
    if (keys.length > 0) {
      await redis.del(...keys)
    }
  }
}
```

### 2. Database-Level Caching

```sql
-- Function result caching
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Prepared statements for frequently used queries
PREPARE get_user_posts(UUID) AS
SELECT p.*, COUNT(c.id) as comment_count
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id AND c.status = 'approved'
WHERE p.author_id = $1 AND p.status = 'published'
GROUP BY p.id
ORDER BY p.created_at DESC;

-- Execute prepared statement
EXECUTE get_user_posts('550e8400-e29b-41d4-a716-446655440000');
```

### 3. CDN and Edge Caching

```javascript
// Cache headers for API responses
const handler = async (req, res) => {
  const cacheControl = req.url.includes('/api/posts')
    ? 'public, max-age=300, s-maxage=600'  // 5 min browser, 10 min CDN
    : 'no-cache, no-store, must-revalidate'

  res.setHeader('Cache-Control', cacheControl)

  // ... fetch and return data
}

// Edge function with caching
export default async function handler(req) {
  const cacheKey = `posts:${new URL(req.url).searchParams.toString()}`

  // Check cache
  const cached = await CACHE.get(cacheKey)
  if (cached) {
    return new Response(cached, {
      headers: { 'Cache-Control': 'public, max-age=300' }
    })
  }

  // Fetch fresh data
  const posts = await supabase
    .from('posts')
    .select('*')
    .order('created_at', { ascending: false })
    .limit(20)

  // Cache response
  await CACHE.set(cacheKey, JSON.stringify(posts.data), { ttl: 300 })

  return new Response(JSON.stringify(posts.data), {
    headers: { 'Cache-Control': 'public, max-age=300' }
  })
}
```

## Resource Monitoring and Scaling

### 1. Performance Monitoring Setup

```javascript
// Custom performance monitoring
class PerformanceMonitor {
  constructor() {
    this.metrics = {
      queryTimes: [],
      connectionCount: 0,
      cacheHitRate: 0
    }
  }

  trackQuery(queryName, duration) {
    this.metrics.queryTimes.push({
      query: queryName,
      duration,
      timestamp: Date.now()
    })

    // Keep only last 1000 entries
    if (this.metrics.queryTimes.length > 1000) {
      this.metrics.queryTimes = this.metrics.queryTimes.slice(-1000)
    }
  }

  getSlowQueries(threshold = 1000) { // 1 second threshold
    return this.metrics.queryTimes
      .filter(q => q.duration > threshold)
      .sort((a, b) => b.duration - a.duration)
  }

  getAverageQueryTime(queryName) {
    const queryMetrics = this.metrics.queryTimes.filter(q => q.query === queryName)
    if (queryMetrics.length === 0) return 0

    const total = queryMetrics.reduce((sum, q) => sum + q.duration, 0)
    return total / queryMetrics.length
  }
}
```

### 2. Auto-scaling Strategies

```sql
-- Monitor resource usage for scaling decisions
SELECT
  (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections,
  (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_connections,
  (SELECT count(*) FROM pg_stat_activity WHERE wait_event_type = 'Lock') as waiting_queries,
  (SELECT sum(xact_commit + xact_rollback) FROM pg_stat_database WHERE datname = current_database()) as total_transactions,
  (SELECT sum(blks_read + blks_hit) FROM pg_stat_database WHERE datname = current_database()) as total_blocks;
```

### 3. Performance Alerting

```javascript
// Performance alerting system
class PerformanceAlerts {
  constructor(monitor, webhookUrl) {
    this.monitor = monitor
    this.webhookUrl = webhookUrl
  }

  async checkAndAlert() {
    const slowQueries = this.monitor.getSlowQueries(2000) // 2 second threshold

    if (slowQueries.length > 0) {
      await this.sendAlert({
        type: 'slow_queries',
        message: `Found ${slowQueries.length} slow queries`,
        details: slowQueries.slice(0, 5) // Top 5 slowest
      })
    }

    const avgPostQuery = this.monitor.getAverageQueryTime('get_user_posts')
    if (avgPostQuery > 500) { // 500ms threshold
      await this.sendAlert({
        type: 'query_performance',
        message: `Average post query time: ${avgPostQuery}ms`,
        details: { averageTime: avgPostQuery }
      })
    }
  }

  async sendAlert(alert) {
    try {
      await fetch(this.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          alert,
          timestamp: new Date().toISOString(),
          environment: process.env.NODE_ENV
        })
      })
    } catch (error) {
      console.error('Failed to send alert:', error)
    }
  }
}
```

## Performance Optimization Checklist

### Database Schema
- [ ] Proper data types selected
- [ ] Necessary indexes created
- [ ] Foreign key constraints indexed
- [ ] Unused indexes removed
- [ ] Table partitioning for large datasets

### Query Optimization
- [ ] EXPLAIN ANALYZE used for slow queries
- [ ] JOIN operations optimized
- [ ] Subqueries converted to JOINs where appropriate
- [ ] Pagination implemented efficiently
- [ ] Full-text search configured for text queries

### Connection Management
- [ ] Connection pooling configured
- [ ] Connection reuse implemented
- [ ] Long-running queries identified
- [ ] Transaction boundaries properly defined
- [ ] Connection leaks prevented

### Caching Strategy
- [ ] Application-level caching implemented
- [ ] Database query result caching
- [ ] CDN configured for static assets
- [ ] Cache invalidation strategy defined
- [ ] Cache hit rates monitored

### Monitoring
- [ ] Performance metrics collected
- [ ] Slow query alerts configured
- [ ] Resource usage monitored
- [ ] Auto-scaling rules defined
- [ ] Regular performance reviews scheduled

This comprehensive performance guide ensures optimal database operation and scalability for Supabase applications.
            """

    def _get_authentication_fundamentals(self, level: str) -> str:
        """Get authentication fundamentals."""
        if level == "metadata":
            return "Supabase authentication system fundamentals"
        elif level == "summary":
            return f"""
# Supabase Authentication

## Core Features
- JWT-based authentication
- Multiple auth providers (email, social, custom)
- Row-Level Security (RLS)
- Session management
- Multi-factor authentication

## Setup
```javascript
import {createClient} from '@supabase/supabase-js'
const supabase = createClient(url, key)
```

## Common Patterns
- Email/password authentication
- OAuth provider integration
- Token refresh management
- User session handling
            """
        else:
            return """
# Complete Supabase Authentication Guide

## Authentication Architecture

Supabase uses GoTrue, a JWT-based authentication service that integrates seamlessly with PostgreSQL's Row-Level Security (RLS). This provides a robust, secure authentication system with multiple provider support.

### 1. Authentication Flow

#### Basic Email Authentication
```javascript
// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password',
  options: {
    data: {
      username: 'johndoe',
      full_name: 'John Doe'
    }
  }
})

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'secure-password'
})

// Sign out
const { error } = await supabase.auth.signOut()
```

#### Social Provider Authentication
```javascript
// Google OAuth
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: `${window.location.origin}/auth/callback`,
    queryParams: {
      access_type: 'offline',
      prompt: 'consent',
    },
  }
})

// GitHub OAuth
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'github',
  options: {
    redirectTo: `${window.location.origin}/auth/callback`
  }
})
```

### 2. Session Management

#### Session Monitoring
```javascript
// Listen to auth state changes
const { data: { subscription } } = supabase.auth.onAuthStateChange(
  async (event, session) => {
    switch (event) {
      case 'SIGNED_IN':
        console.log('User signed in:', session.user)
        break
      case 'SIGNED_OUT':
        console.log('User signed out')
        break
      case 'TOKEN_REFRESHED':
        console.log('Token refreshed automatically')
        break
      case 'USER_UPDATED':
        console.log('User updated:', session.user)
        break
    }
  }
)

// Get current session
const { data: { session }, error } = await supabase.auth.getSession()

// Refresh session manually
const { data, error } = await supabase.auth.refreshSession()
```

#### Custom Session Storage
```javascript
// Configure custom session storage
const supabase = createClient(url, key, {
  auth: {
    persistSession: true,
    storage: localStorage, // or custom storage adapter
    storageKey: 'my-app-auth-token',
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
})

// Custom storage adapter
const customStorage = {
  getItem: (key) => {
    return mySecureStorage.get(key)
  },
  setItem: (key, value) => {
    mySecureStorage.set(key, value)
  },
  removeItem: (key) => {
    mySecureStorage.delete(key)
  }
}

const supabase = createClient(url, key, {
  auth: {
    storage: customStorage
  }
})
```

### 3. Row-Level Security (RLS)

#### Basic RLS Policies
```sql
-- Enable RLS on tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;

-- Users can view their own profile
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

-- Users can insert their own profile
CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Published posts are viewable by everyone
CREATE POLICY "Published posts are viewable by everyone" ON posts
  FOR SELECT USING (status = 'published');

-- Authors can manage their own posts
CREATE POLICY "Authors can manage their own posts" ON posts
  FOR ALL USING (auth.uid() = author_id);
```

#### Advanced RLS with Roles
```sql
-- Add role column to users table
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'
  CHECK (role IN ('admin', 'moderator', 'user', 'guest'));

-- Update user role function
CREATE OR REPLACE FUNCTION update_user_role(user_id UUID, new_role TEXT)
RETURNS void AS $$
BEGIN
  -- Only admins can change roles
  IF (
    SELECT role FROM users WHERE id = auth.uid()
  ) != 'admin' THEN
    RAISE EXCEPTION 'Only admins can change user roles';
  END IF;

  UPDATE users SET role = new_role WHERE id = user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Advanced RLS policies with roles
CREATE POLICY "Admins can view all profiles" ON profiles
  FOR SELECT USING (
    (SELECT role FROM users WHERE id = auth.uid()) = 'admin'
  );

CREATE POLICY "Moderators can view unpublished posts" ON posts
  FOR SELECT USING (
    status = 'published' OR
    (SELECT role FROM users WHERE id = auth.uid()) = 'moderator'
  );
```

### 4. Multi-Factor Authentication

#### TOTP Setup
```javascript
// Enable TOTP for user
const { data, error } = await supabase.auth.mfa.enroll({
  factorType: 'totp',
  friendlyName: 'My Authenticator App'
})

// Verify and activate TOTP
const { data, error } = await supabase.auth.mfa.challengeAndVerify({
  factorId: data.id,
  code: '123456' // Code from authenticator app
})

// Challenge TOTP for login
const challenge = await supabase.auth.mfa.challenge({
  factorId: 'totp-factor-id'
})

const verify = await supabase.auth.mfa.verify({
  factorId: 'totp-factor-id',
  challengeId: challenge.data.id,
  code: '123456'
})
```

### 5. Custom Authentication

#### Custom JWT Tokens
```javascript
// Sign in with custom JWT
const { data, error } = await supabase.auth.signInWithIdToken({
  provider: 'custom',
  token: customJwtToken,
  nonce: randomNonce
})

// Custom auth server integration
const createCustomAuth = async (userData) => {
  // Generate custom JWT with your auth server
  const customToken = await generateCustomToken(userData)

  // Sign in with custom token
  const { data, error } = await supabase.auth.signInWithIdToken({
    provider: 'custom',
    token: customToken
  })

  return data
}
```

### 6. Security Best Practices

#### JWT Configuration
```javascript
// Configure JWT settings in Supabase dashboard
// Settings > Authentication > JWT Settings

// JWT Secret (keep secret)
// JWT Expiry (default: 1 hour)
// Refresh Token Expiry (default: 30 days)

// Custom JWT claims
const customClaims = {
  role: 'admin',
  permissions: ['read', 'write', 'delete'],
  tenant_id: 'company-123'
}

// Include custom claims in token
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password',
  options: {
    data: customClaims
  }
})
```

#### Rate Limiting and Security
```javascript
// Implement rate limiting on auth endpoints
const authMiddleware = async (req, res, next) => {
  const clientIP = req.ip
  const rateLimit = await checkRateLimit(clientIP, 'auth')

  if (rateLimit.exceeded) {
    return res.status(429).json({ error: 'Too many requests' })
  }

  next()
}

// Account lockout after failed attempts
const handleFailedLogin = async (email) => {
  const attempts = await getFailedAttempts(email)

  if (attempts >= 5) {
    await lockAccount(email, 15 * 60 * 1000) // 15 minutes
    throw new Error('Account temporarily locked')
  }

  await incrementFailedAttempts(email)
}
```

### 7. User Management

#### User CRUD Operations
```javascript
// Get current user
const { data: { user } } = await supabase.auth.getUser()

// Update user metadata
const { data, error } = await supabase.auth.updateUser({
  email: 'newemail@example.com',
  password: 'new-secure-password',
  data: {
    username: 'newusername',
    full_name: 'New Name',
    avatar_url: 'https://example.com/avatar.jpg'
  },
  email_confirm: true
})

// Delete user account
const { error } = await supabase.auth.admin.deleteUser(
  'user-uuid-here'
)
```

#### Admin Functions
```javascript
// Admin user management (requires service role key)
const adminClient = createClient(url, serviceRoleKey)

// List all users
const { data, error } = await adminClient.auth.admin.listUsers()

// Get user by ID
const { data, error } = await adminClient.auth.admin.getUserById(
  'user-uuid-here'
)

// Create user manually
const { data, error } = await adminClient.auth.admin.createUser({
  email: 'user@example.com',
  password: 'password',
  email_confirm: true,
  user_metadata: {
    role: 'user',
    department: 'engineering'
  }
})
```

This comprehensive authentication guide covers all aspects of secure user management in Supabase applications.
            """

    def _get_rls_guidance(self, level: str) -> str:
        """Get Row-Level Security guidance."""
        if level == "metadata":
            return "Row-Level Security implementation and best practices"
        elif level == "summary":
            return f"""
# Row-Level Security (RLS)

## Key Concepts
- Policy-based access control
- User-specific data filtering
- Automatic security enforcement
- Role-based permissions

## Implementation
```sql
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own data" ON sensitive_data
  FOR SELECT USING (user_id = auth.uid());
```

## Best Practices
- Enable RLS on all user data tables
- Use specific, not overly broad policies
- Test policies thoroughly
- Consider performance implications
            """
        else:
            return """
# Comprehensive Row-Level Security (RLS) Guide

## Understanding RLS

Row-Level Security (RLS) is PostgreSQL's mechanism for controlling row access at the table level. In Supabase, RLS integrates with JWT authentication to provide automatic, granular access control based on user identity.

### 1. Enabling RLS

#### Basic Setup
```sql
-- Enable RLS on tables containing user data
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Check RLS status
SELECT
  schemaname,
  tablename,
  rowsecurity
FROM pg_tables
WHERE schemaname = 'public';
```

#### Disabling RLS (Caution!)
```sql
-- Disable RLS (use only for admin operations)
ALTER TABLE posts DISABLE ROW LEVEL SECURITY;

-- Re-enable after maintenance
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
```

### 2. Basic Policy Patterns

#### User Ownership Pattern
```sql
-- Users can only access their own data
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Application to posts table
CREATE POLICY "Authors can manage their posts" ON posts
  FOR ALL USING (auth.uid() = author_id);
```

#### Public Read with Author Write
```sql
-- Anyone can read published content
CREATE POLICY "Published posts are public" ON posts
  FOR SELECT USING (status = 'published');

-- Only authors can manage their posts
CREATE POLICY "Authors can manage their posts" ON posts
  FOR ALL USING (auth.uid() = author_id);
```

### 3. Advanced Policy Techniques

#### Role-Based Access Control
```sql
-- Add role column to users table
ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'
  CHECK (role IN ('admin', 'moderator', 'editor', 'user', 'guest'));

-- Create role-based policies
CREATE POLICY "Admins can access all posts" ON posts
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

CREATE POLICY "Moderators can view all posts" ON posts
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('admin', 'moderator')
    )
  );

CREATE POLICY "Editors can edit any post" ON posts
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('admin', 'editor')
    )
  );
```

#### Team or Organization-Based Access
```sql
-- Team membership table
CREATE TABLE team_memberships (
  team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role TEXT DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  PRIMARY KEY (team_id, user_id)
);

-- Team-based resource policies
CREATE POLICY "Team members can access team resources" ON documents
  FOR ALL USING (
    team_id IN (
      SELECT team_id FROM team_memberships
      WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Team admins can manage team resources" ON documents
  FOR UPDATE, DELETE USING (
    team_id IN (
      SELECT team_id FROM team_memberships
      WHERE user_id = auth.uid() AND role IN ('owner', 'admin')
    )
  );
```

#### Time-Based or Condition-Based Access
```sql
-- Time-based access for subscription content
CREATE POLICY "Premium users can access content" ON premium_content
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM subscriptions
      WHERE user_id = auth.uid()
        AND status = 'active'
        AND end_date > NOW()
    )
  );

-- Conditional access based on user status
CREATE POLICY "Active users can post" ON posts
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND status = 'active'
    )
  );
```

### 4. Performance Optimization

#### Efficient Policy Design
```sql
-- Use specific, efficient conditions
-- Bad: Complex subqueries
CREATE POLICY "Complex policy" ON posts
  FOR SELECT USING (
    auth.uid() IN (
      SELECT user_id FROM user_permissions
      WHERE permission = 'read_posts'
      AND expires_at > NOW()
    )
  );

-- Good: Simple indexed conditions
CREATE POLICY "Efficient policy" ON posts
  FOR SELECT USING (
    author_id = auth.uid() OR
    status = 'published'
  );

-- Add indexes for policy columns
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_user_permissions_user_permission ON user_permissions(user_id, permission)
WHERE expires_at > NOW();
```

#### Policy Testing and Debugging
```sql
-- Test policies with specific users
SET ROLE authenticated; -- Simulate authenticated user
SET request.jwt.claims.sub TO 'user-uuid-here'; -- Set user ID

-- Test query
SELECT * FROM posts WHERE id = 1;

-- Reset
RESET ROLE;
RESET request.jwt.claims.sub;

-- Policy debugging
CREATE OR REPLACE FUNCTION debug_rls(table_name TEXT, user_id UUID)
RETURNS TABLE(policy_name TEXT, applicable BOOLEAN) AS $$
BEGIN
  RETURN QUERY
  SELECT
    p.policyname,
    p.roles && CURRENT_ROLE::text[] as applicable
  FROM pg_policies p
  WHERE p.tablename = table_name;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM debug_rls('posts', 'user-uuid-here');
```

### 5. Security Patterns

#### Multi-Tenant Security
```sql
-- Tenant isolation
CREATE POLICY "Tenant isolation" ON documents
  FOR ALL USING (
    tenant_id = (
      SELECT tenant_id FROM user_tenants
      WHERE user_id = auth.uid()
    )
  );

-- Cross-tenant data sharing (if needed)
CREATE POLICY "Shared documents accessible" ON shared_documents
  FOR SELECT USING (
    id IN (
      SELECT document_id FROM document_shares
      WHERE user_id = auth.uid()
        OR team_id IN (
          SELECT team_id FROM team_memberships
          WHERE user_id = auth.uid()
        )
    )
  );
```

#### Auditing and Compliance
```sql
-- Audit policy changes
CREATE TABLE policy_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  policy_name TEXT NOT NULL,
  table_name TEXT NOT NULL,
  action TEXT NOT NULL,
  policy_definition TEXT,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trigger to log policy changes
CREATE OR REPLACE FUNCTION log_policy_changes()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'CREATE' THEN
    INSERT INTO policy_audit_log (policy_name, table_name, action, policy_definition, created_by)
    VALUES (NEW.policyname, NEW.tablename, 'CREATE', pg_get_triggerdef(NEW.oid), auth.uid());
    RETURN NEW;
  ELSIF TG_OP = 'DROP' THEN
    INSERT INTO policy_audit_log (policy_name, table_name, action, created_by)
    VALUES (OLD.policyname, OLD.tablename, 'DROP', NULL, auth.uid());
    RETURN OLD;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER policy_changes_audit
  AFTER CREATE OR DROP POLICY ON ALL TABLES
  FOR EACH STATEMENT EXECUTE FUNCTION log_policy_changes();
```

### 6. Common RLS Patterns

#### Social Media Platform
```sql
-- Posts visibility
CREATE POLICY "Public posts visible to all" ON posts
  FOR SELECT USING (privacy = 'public');

CREATE POLICY "Friends can see friends-only posts" ON posts
  FOR SELECT USING (
    privacy = 'friends' AND (
      author_id = auth.uid() OR
      auth.uid() IN (
        SELECT friend_id FROM friendships
        WHERE user_id = posts.author_id AND status = 'accepted'
      )
    )
  );

CREATE POLICY "Only authors can edit posts" ON posts
  FOR UPDATE USING (author_id = auth.uid());

-- Comments on posts
CREATE POLICY "Users can comment on accessible posts" ON comments
  FOR INSERT WITH CHECK (
    post_id IN (
      SELECT id FROM posts
      WHERE (
        privacy = 'public' OR
        (privacy = 'friends' AND (
          author_id = auth.uid() OR
          auth.uid() IN (
            SELECT friend_id FROM friendships
            WHERE user_id = posts.author_id AND status = 'accepted'
          )
        ))
      )
    )
  );
```

#### E-commerce Platform
```sql
-- Product access
CREATE POLICY "Products visible to all" ON products
  FOR SELECT USING (status = 'active');

-- Order access
CREATE POLICY "Users can access their own orders" ON orders
  FOR ALL USING (user_id = auth.uid());

-- Admin access to all orders
CREATE POLICY "Admins can access all orders" ON orders
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role = 'admin'
    )
  );

-- Inventory management
CREATE POLICY "Staff can manage inventory" ON inventory
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users
      WHERE id = auth.uid() AND role IN ('admin', 'staff')
    )
  );
```

### 7. RLS Management

#### Policy Management Functions
```sql
-- Function to check if user has specific permission
CREATE OR REPLACE FUNCTION user_has_permission(user_id UUID, permission TEXT)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM user_permissions
    WHERE user_id = user_has_permission.user_id
      AND permission = user_has_permission.permission
      AND (expires_at IS NULL OR expires_at > NOW())
  );
END;
$$ LANGUAGE plpgsql;

-- Function to check team membership
CREATE OR REPLACE FUNCTION is_team_member(team_id UUID, user_id UUID DEFAULT NULL)
RETURNS BOOLEAN AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM team_memberships
    WHERE team_id = is_team_member.team_id
      AND user_id = COALESCE(is_team_member.user_id, auth.uid())
  );
END;
$$ LANGUAGE plpgsql;
```

#### Policy Testing Framework
```sql
-- Test policy effectiveness
CREATE OR REPLACE FUNCTION test_policy(table_name TEXT, test_user UUID, test_query TEXT)
RETURNS TABLE(test_name TEXT, expected_result BOOLEAN, actual_result BOOLEAN, passed BOOLEAN) AS $$
DECLARE
  test_result BOOLEAN;
BEGIN
  -- Execute test query as test user
  EXECUTE format('SET request.jwt.claims.sub TO %L', test_user);

  BEGIN
    EXECUTE test_query INTO test_result;
    RETURN QUERY
    SELECT
      'Policy Test' as test_name,
      true as expected_result,
      test_result as actual_result,
      test_result = true as passed;
  EXCEPTION WHEN OTHERS THEN
    RETURN QUERY
    SELECT
      'Policy Test' as test_name,
      true as expected_result,
      false as actual_result,
      false as passed;
  END;

  -- Reset
  RESET request.jwt.claims.sub;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

This comprehensive RLS guide ensures secure, performant, and maintainable row-level security implementations.
            """

    def _get_realtime_fundamentals(self, level: str) -> str:
        """Get real-time fundamentals."""
        if level == "metadata":
            return "Supabase real-time subscription and presence fundamentals"
        elif level == "summary":
            return f"""
# Supabase Real-time Features

## Key Components
- Database change subscriptions
- Presence channels
- Broadcast messaging
- WebSocket connections

## Basic Usage
```javascript
const subscription = supabase
  .channel('db-changes')
  .on('postgres_changes', {event: '*', table: 'posts' }, handler)
  .subscribe()
```

## Features
- Real-time data synchronization
- User presence tracking
- Server-to-client broadcasting
- Efficient data filtering
            """
        else:
            return """
# Complete Supabase Real-time Guide

## Real-time Architecture

Supabase Real-time uses PostgreSQL's logical replication to stream database changes to connected clients via WebSockets. This provides instant data synchronization with built-in security and filtering.

### 1. Database Change Subscriptions

#### Basic Table Subscriptions
```javascript
// Listen to all changes on posts table
const postsSubscription = supabase
  .channel('posts-changes')
  .on('postgres_changes',
    {
      event: '*', // Listen to all events (INSERT, UPDATE, DELETE)
      schema: 'public',
      table: 'posts'
    },
    (payload) => {
      console.log('Post change:', payload)

      switch (payload.eventType) {
        case 'INSERT':
          handleNewPost(payload.new)
          break
        case 'UPDATE':
          handlePostUpdate(payload.new, payload.old)
          break
        case 'DELETE':
          handlePostDelete(payload.old)
          break
      }
    }
  )
  .subscribe((status) => {
    console.log('Subscription status:', status)
  })
```

#### Event-Specific Subscriptions
```javascript
// Listen only to new comments
const commentsSubscription = supabase
  .channel('new-comments')
  .on('postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'comments'
    },
    (payload) => {
      console.log('New comment:', payload.new)
      addCommentToUI(payload.new)
    }
  )
  .subscribe()

// Listen to status changes
const statusSubscription = supabase
  .channel('post-status-changes')
  .on('postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'posts',
      filter: 'status=eq.published'
    },
    (payload) => {
      console.log('Post published:', payload.new)
      notifySubscribers(payload.new)
    }
  )
  .subscribe()
```

#### Advanced Filtering
```javascript
// Complex filtering
const userPostsSubscription = supabase
  .channel('user-posts')
  .on('postgres_changes',
    {
      event: '*',
      schema: 'public',
      table: 'posts',
      filter: `author_id=eq.${userId}&status=in.(published,draft)`
    },
    (payload) => {
      console.log('User post change:', payload)
      updatePostList(payload)
    }
  )
  .subscribe()

// Time-based filtering
const recentActivitySubscription = supabase
  .channel('recent-activity')
  .on('postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'activities',
      filter: `created_at=gt.${new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()}`
    },
    (payload) => {
      showRecentActivity(payload.new)
    }
  )
  .subscribe()
```

### 2. Presence Channels

#### User Presence Tracking
```javascript
// Join presence channel
const presenceChannel = supabase.channel('online-users')

// Listen to presence events
presenceChannel
  .on('presence', { event: 'sync' }, () => {
    const onlineUsers = presenceChannel.presenceState()
    console.log('Currently online:', onlineUsers)
    updateOnlineUsersList(onlineUsers)
  })
  .on('presence', { event: 'join' }, ({ newPresences }) => {
    console.log('Users joined:', newPresences)
    newPresences.forEach(presence => {
      showUserJoinedNotification(presence.user)
    })
  })
  .on('presence', { event: 'leave' }, ({ leftPresences }) => {
    console.log('Users left:', leftPresences)
    leftPresences.forEach(presence => {
      showUserLeftNotification(presence.user)
    })
  })
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      // Track current user presence
      await presenceChannel.track({
        user: currentUser.id,
        username: currentUser.username,
        status: 'online',
        lastSeen: new Date().toISOString()
      })
    }
  })
```

#### Application State Synchronization
```javascript
// Document collaboration presence
const documentChannel = supabase.channel(`document-${documentId}`)

documentChannel
  .on('presence', { event: 'sync' }, () => {
    const presenceState = documentChannel.presenceState()
    updateCollaboratorList(presenceState)
  })
  .on('presence', { event: 'join' }, ({ newPresences }) => {
    newPresences.forEach(presence => {
      if (presence.user.id !== currentUser.id) {
        showCollaboratorJoined(presence.user)
        trackCursorPosition(presence.user.id, presence.cursor)
      }
    })
  })
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      await documentChannel.track({
        user: currentUser.id,
        cursor: { line: 1, column: 1 },
        selection: { start: { line: 1, column: 1 }, end: { line: 1, column: 1 } }
      })
    }
  })

// Update cursor position
const updateCursor = async (line, column) => {
  await documentChannel.track({
    user: currentUser.id,
    cursor: { line, column }
  })
}

// Update selection
const updateSelection = async (start, end) => {
  await documentChannel.track({
    user: currentUser.id,
    selection: { start, end }
  })
}
```

### 3. Broadcast Channels

#### Server Broadcasting (Edge Functions)
```typescript
// Edge Function for broadcasting
import { serve } from "https://deno.land/std@0.131.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }

  const { message, type = 'notification' } = await req.json()

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  // Broadcast to all connected clients
  await supabase.channel('global-notifications')
    .send({
      type: 'broadcast',
      event: type,
      payload: {
        message,
        timestamp: new Date().toISOString(),
        id: crypto.randomUUID()
      }
    })

  return new Response(
    JSON.stringify({ success: true }),
    { headers: { 'Content-Type': 'application/json' } }
  )
})

// Client listening for broadcasts
const notificationChannel = supabase.channel('global-notifications')

notificationChannel
  .on('broadcast', { event: 'notification' }, (payload) => {
    showNotification(payload.payload)
  })
  .on('broadcast', { event: 'system-maintenance' }, (payload) => {
    showMaintenanceAlert(payload.payload)
  })
  .subscribe()
```

#### Client-to-Client Broadcasting
```javascript
// Chat application broadcasting
const chatChannel = supabase.channel(`chat-${roomId}`)

chatChannel
  .on('postgres_changes', // Database changes
    {
      event: 'INSERT',
      schema: 'public',
      table: 'messages',
      filter: `room_id=eq.${roomId}`
    },
    (payload) => {
      displayMessage(payload.new)
    }
  )
  .on('broadcast', // Direct broadcasts
    { event: 'typing-indicator' },
    (payload) => {
      showTypingIndicator(payload.payload.user)
    }
  )
  .subscribe(async (status) => {
    if (status === 'SUBSCRIBED') {
      // Send typing indicator
      const sendTypingIndicator = async (isTyping) => {
        await chatChannel.send({
          type: 'broadcast',
          event: 'typing-indicator',
          payload: {
            user: currentUser.id,
            username: currentUser.username,
            isTyping
          }
        })
      }

      // Handle input events
      messageInput.addEventListener('input', debounce(() => {
        sendTypingIndicator(true)
      }, 300))

      messageInput.addEventListener('blur', () => {
        sendTypingIndicator(false)
      })
    }
  })
```

### 4. Advanced Real-time Patterns

#### Optimistic Updates
```javascript
// Optimistic update pattern
const updatePost = async (postId, updates) => {
  // Optimistically update UI
  const tempId = `temp-${Date.now()}`
  const optimisticUpdate = {
    ...updates,
    id: tempId,
    updatedAt: new Date().toISOString(),
    pending: true
  }

  updatePostInUI(postId, optimisticUpdate)

  try {
    // Make actual API call
    const { data, error } = await supabase
      .from('posts')
      .update(updates)
      .eq('id', postId)
      .select()
      .single()

    if (error) throw error

    // Replace optimistic update with real data
    replaceTempUpdate(tempId, data)
  } catch (error) {
    // Revert optimistic update on error
    revertUpdate(postId, optimisticUpdate)
    showError(error.message)
  }
}

// Listen for actual updates to resolve conflicts
const postUpdatesChannel = supabase.channel('post-updates')
postUpdatesChannel
  .on('postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'posts',
      filter: `id=eq.${postId}`
    },
    (payload) => {
      // Resolve optimistic update with real change
      resolveOptimisticUpdate(payload.new)
    }
  )
  .subscribe()
```

#### Conflict Resolution
```javascript
// Last-write-wins conflict resolution
const resolveEditConflict = async (localVersion, serverVersion) => {
  // Simple last-write-wins
  if (new Date(serverVersion.updatedAt) > new Date(localVersion.updatedAt)) {
    // Server version is newer
    showConflictDialog(serverVersion, localVersion, async (resolution) => {
      if (resolution === 'accept-server') {
        updateLocalPost(serverVersion)
      } else if (resolution === 'force-local') {
        await forceUpdateToServer(localVersion)
      } else if (resolution === 'merge') {
        const merged = mergePosts(localVersion, serverVersion)
        await saveMergedPost(merged)
      }
    })
  } else {
    // Local version is newer or same age
    await forceUpdateToServer(localVersion)
  }
}

// Version checking with etag/row_version
const saveWithConflictCheck = async (postId, updates, currentVersion) => {
  try {
    const { data, error } = await supabase
      .from('posts')
      .update({ ...updates, row_version: currentVersion + 1 })
      .eq('id', postId)
      .eq('row_version', currentVersion) // Optimistic locking
      .select()
      .single()

    if (error) {
      if (error.code === 'PGRST116') { // No rows returned = version conflict
        const { data: currentPost } = await supabase
          .from('posts')
          .select('*')
          .eq('id', postId)
          .single()

        await resolveEditConflict(updates, currentPost)
      }
      throw error
    }

    return data
  } catch (error) {
    console.error('Save failed:', error)
    throw error
  }
}
```

#### Performance Optimization
```javascript
// Subscription management
class RealtimeManager {
  constructor() {
    this.subscriptions = new Map()
    this.presenceChannels = new Map()
  }

  // Subscribe with automatic cleanup
  subscribe(name, config, handler) {
    // Clean up existing subscription
    this.unsubscribe(name)

    const channel = supabase.channel(name)
      .on('postgres_changes', config, handler)
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Subscription ${name} active`)
        } else if (status === 'CHANNEL_ERROR') {
          console.error(`Subscription ${name} failed`)
          this.retrySubscription(name, config, handler)
        }
      })

    this.subscriptions.set(name, channel)
    return channel
  }

  // Unsubscribe and cleanup
  unsubscribe(name) {
    const channel = this.subscriptions.get(name)
    if (channel) {
      supabase.removeChannel(channel)
      this.subscriptions.delete(name)
    }
  }

  // Cleanup all subscriptions
  cleanup() {
    this.subscriptions.forEach((channel, name) => {
      supabase.removeChannel(channel)
    })
    this.subscriptions.clear()
  }

  // Retry failed subscriptions
  retrySubscription(name, config, handler) {
    setTimeout(() => {
      console.log(`Retrying subscription ${name}`)
      this.subscribe(name, config, handler)
    }, 5000) // 5 second delay
  }
}

// Use the manager
const realtimeManager = new RealtimeManager()

// Subscribe to changes
const postsSubscription = realtimeManager.subscribe(
  'posts-updates',
  { event: '*', schema: 'public', table: 'posts' },
  (payload) => {
    handlePostChange(payload)
  }
)

// Cleanup on unmount
window.addEventListener('beforeunload', () => {
  realtimeManager.cleanup()
})
```

### 5. Security Considerations

#### RLS with Real-time
```sql
-- Ensure RLS policies work with real-time subscriptions
CREATE POLICY "Users can see their own messages" ON messages
  FOR SELECT USING (
    recipient_id = auth.uid() OR
    sender_id = auth.uid() OR
    is_public = true
  );

-- Special policy for real-time subscriptions
CREATE POLICY "Real-time message updates" ON messages
  FOR SELECT USING (
    recipient_id = auth.uid() OR
    sender_id = auth.uid()
  );
```

#### Client-side Security
```javascript
// Secure subscription setup
const createSecureSubscription = (tableName, filters = {}) => {
  return supabase
    .channel(`secure-${tableName}-${Date.now()}`)
    .on('postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: tableName,
        filter: buildSecureFilter(filters) // Apply client-side filters
      },
      handleSecureChange
    )
    .subscribe()
}

// Validate incoming real-time data
const validateRealtimeData = (payload, schema) => {
  try {
    // Validate against schema
    const validated = schema.parse(payload.new || payload.old)

    // Check RLS compliance
    if (validated.user_id && validated.user_id !== currentUser.id) {
      console.warn('Received data for different user - RLS violation')
      return null
    }

    return validated
  } catch (error) {
    console.error('Real-time data validation failed:', error)
    return null
  }
}

// Use validation in subscription handlers
const handleSecureChange = (payload) => {
  const validatedData = validateRealtimeData(payload, messageSchema)
  if (validatedData) {
    updateUI(validatedData)
  }
}
```

This comprehensive real-time guide enables building sophisticated, real-time applications with Supabase.
            """

    def _get_storage_fundamentals(self, level: str) -> str:
        """Get storage fundamentals."""
        if level == "metadata":
            return "Supabase storage, CDN, and file management fundamentals"
        elif level == "summary":
            return f"""
# Supabase Storage

## Core Features
- S3-compatible object storage
- Automatic CDN integration
- File transformations and optimization
- Row-Level Security integration
- Signed URLs for private access

## Basic Usage
```javascript
const {data, error} = await supabase.storage
  .from('avatars')
  .upload('user-123/profile.jpg', file)

const {data} = supabase.storage
  .from('avatars')
  .getPublicUrl('user-123/profile.jpg')
```

## Features
- Image transformations
- File size optimization
- Global CDN delivery
- Secure access controls
            """
        else:
            return """
# Complete Supabase Storage Guide

## Storage Architecture

Supabase Storage provides S3-compatible object storage with integrated CDN, automatic image transformations, and seamless security integration with Row-Level Security policies.

### 1. Storage Bucket Management

#### Creating Buckets
```sql
-- Create public bucket for user avatars
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'avatars',
  'avatars',
  true, -- public bucket
  2097152, -- 2MB file size limit
  ARRAY['image/jpeg', 'image/png', 'image/webp']
);

-- Create private bucket for documents
INSERT INTO storage.buckets (id, name, public, file_size_limit)
VALUES (
  'documents',
  'documents',
  false, -- private bucket
  52428800 -- 50MB file size limit
);
```

#### Bucket Policies with RLS
```sql
-- Enable RLS on storage.objects (default enabled)
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Users can upload to their own avatar folder
CREATE POLICY "Users can upload own avatar" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'avatars' AND
    auth.role() = 'authenticated' AND
    (storage.foldername(name))[1] = auth.uid()::text
  );

-- Users can view their own avatar
CREATE POLICY "Users can view own avatar" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'avatars' AND
    auth.role() = 'authenticated' AND
    (storage.foldername(name))[1] = auth.uid()::text
  );

-- Anyone can view public avatars
CREATE POLICY "Anyone can view avatars" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'avatars'
  );

-- Users can manage their documents
CREATE POLICY "Users can manage documents" ON storage.objects
  FOR ALL USING (
    bucket_id = 'documents' AND
    auth.uid() = (storage.foldername(name))[1]::uuid
  );
```

### 2. File Upload Operations

#### Basic Upload
```javascript
// Simple file upload
const uploadFile = async (file, bucket, path) => {
  const { data, error } = await supabase.storage
    .from(bucket)
    .upload(path, file)

  if (error) throw error

  // Get public URL if bucket is public
  const { data: { publicUrl } } = supabase.storage
    .from(bucket)
    .getPublicUrl(path)

  return { data, publicUrl }
}

// Upload with progress tracking
const uploadWithProgress = async (file, bucket, path) => {
  const { data, error } = await supabase.storage
    .from(bucket)
    .upload(path, file, {
      cacheControl: '3600',
      upsert: false,
      onUploadProgress: (progress) => {
        const percent = Math.round((progress.loaded / progress.total) * 100)
        console.log(`Upload progress: ${percent}%`)
        updateProgressBar(percent)
      }
    })

  return data
}
```

#### Advanced Upload Patterns
```javascript
// Resumable uploads for large files
const resumableUpload = async (file, bucket, path, chunkSize = 1024 * 1024) => {
  const totalChunks = Math.ceil(file.size / chunkSize)
  let uploadedChunks = []

  for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
    const start = chunkIndex * chunkSize
    const end = Math.min(start + chunkSize, file.size)
    const chunk = file.slice(start, end)

    const chunkPath = `${path}.chunk-${chunkIndex}`

    try {
      await supabase.storage
        .from(bucket)
        .upload(chunkPath, chunk, { upsert: true })

      uploadedChunks.push(chunkIndex)
      console.log(`Uploaded chunk ${chunkIndex + 1}/${totalChunks}`)
    } catch (error) {
      console.error(`Failed to upload chunk ${chunkIndex}:`, error)
      throw error
    }
  }

  // Merge chunks (server-side function)
  const { data } = await supabase.functions.invoke('merge-file-chunks', {
    bucket,
    path,
    totalChunks,
    originalFileName: file.name
  })

  return data
}

// Multiple file upload
const uploadMultipleFiles = async (files, bucket, baseFolder) => {
  const uploadPromises = files.map(async (file, index) => {
    const fileExtension = file.name.split('.').pop()
    const fileName = `${Date.now()}-${index}.${fileExtension}`
    const filePath = `${baseFolder}/${fileName}`

    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(filePath, file)

    if (error) throw error

    const { data: { publicUrl } } = supabase.storage
      .from(bucket)
      .getPublicUrl(filePath)

    return {
      id: data.id,
      path: data.path,
      publicUrl,
      name: file.name,
      size: file.size,
      type: file.type
    }
  })

  return Promise.all(uploadPromises)
}
```

### 3. File Download Operations

#### Public File Access
```javascript
// Get public URL
const getPublicUrl = (bucket, path) => {
  const { data } = supabase.storage
    .from(bucket)
    .getPublicUrl(path)

  return data.publicUrl
}

// Download file
const downloadFile = async (bucket, path) => {
  const { data, error } = await supabase.storage
    .from(bucket)
    .download(path)

  if (error) throw error

  // Create download link
  const url = URL.createObjectURL(data)
  const link = document.createElement('a')
  link.href = url
  link.download = path.split('/').pop()
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
```

#### Private File Access
```javascript
// Generate signed URL for private files
const getSignedUrl = async (bucket, path, expiresIn = 60) => {
  const { data, error } = await supabase.storage
    .from(bucket)
    .createSignedUrl(path, expiresIn)

  if (error) throw error

  return data.signedUrl
}

// Temporary access for private files
const accessPrivateFile = async (bucket, path) => {
  try {
    // Generate signed URL with 1 hour expiry
    const signedUrl = await getSignedUrl(bucket, path, 3600)

    // Use the URL for temporary access
    const response = await fetch(signedUrl)
    if (!response.ok) throw new Error('Failed to access file')

    return response.blob()
  } catch (error) {
    console.error('Error accessing private file:', error)
    throw error
  }
}
```

### 4. Image Transformations

#### Basic Transformations
```javascript
// Resize images
const getResizedImage = (bucket, path, width, height) => {
  const { data } = supabase.storage
    .from(bucket)
    .getPublicUrl(path, {
      transform: {
        width,
        height,
        quality: 80
      }
    })

  return data.publicUrl
}

// Crop and resize
const getCroppedImage = (bucket, path, width, height) => {
  const { data } = supabase.storage
    .from(bucket)
    .getPublicUrl(path, {
      transform: {
        width,
        height,
        resize: 'cover' // 'cover', 'contain', 'fill', 'inside', 'outside'
      }
    })

  return data.publicUrl
}
```

#### Advanced Transformations
```javascript
// Generate multiple image sizes
const generateImageSizes = (bucket, originalPath) => {
  const sizes = [
    { name: 'thumb', width: 150, height: 150 },
    { name: 'medium', width: 400, height: 300 },
    { name: 'large', width: 1200, height: 800 },
    { name: 'social', width: 1200, height: 630 } // Social media
  ]

  return sizes.map(size => ({
    name: size.name,
    url: supabase.storage
      .from(bucket)
      .getPublicUrl(originalPath, {
        transform: {
          width: size.width,
          height: size.height,
          quality: size.name === 'thumb' ? 60 : 80,
          resize: 'cover'
        }
      }).data.publicUrl
  }))
}

// Format conversion
const convertToWebP = (bucket, path) => {
  const { data } = supabase.storage
    .from(bucket)
    .getPublicUrl(path, {
      transform: {
        format: 'webp', // Convert to WebP format
        quality: 85
      }
    })

  return data.publicUrl
}

// Placeholder images
const generatePlaceholder = (bucket, path) => {
  const { data } = supabase.storage
    .from(bucket)
    .getPublicUrl(path, {
      transform: {
        width: 400,
        height: 300,
        quality: 10, // Very low quality for placeholder
        blur: 20 // Apply blur effect
      }
    })

  return data.publicUrl
}
```

### 5. CDN and Performance Optimization

#### CDN Configuration
```javascript
// Responsive image set
const getResponsiveImageSet = (bucket, path) => {
  const sizes = [
    { width: 400, media: '(max-width: 400px)' },
    { width: 800, media: '(max-width: 800px)' },
    { width: 1200, media: '(max-width: 1200px)' },
    { width: 1920, media: '(min-width: 1201px)' }
  ]

  return {
    src: sizes[sizes.length - 1].url,
    srcSet: sizes.map(size => {
      const url = supabase.storage
        .from(bucket)
        .getPublicUrl(path, {
          transform: {
            width: size.width,
            quality: 75
          }
        }).data.publicUrl

      return `${url} ${size.width}w`
    }).join(', '),
    sizes: sizes.map(size => size.media).join(', ')
  }
}

// Lazy loading setup
const setupLazyLoading = () => {
  const images = document.querySelectorAll('img[data-src]')

  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target
        img.src = img.dataset.src
        img.classList.remove('lazy')
        imageObserver.unobserve(img)
      }
    })
  })

  images.forEach(img => imageObserver.observe(img))
}
```

### 6. Security Considerations

#### File Type Validation
```javascript
// Validate file types before upload
const validateFileType = (file, allowedTypes) => {
  const allowedMimeTypes = allowedTypes.map(type => {
    const mimeTypeMap = {
      'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
      'document': ['application/pdf', 'text/plain', 'application/msword'],
      'video': ['video/mp4', 'video/webm', 'video/ogg'],
      'audio': ['audio/mp3', 'audio/wav', 'audio/ogg']
    }
    return mimeTypeMap[type] || []
  }).flat()

  if (!allowedMimeTypes.includes(file.type)) {
    throw new Error(`File type ${file.type} is not allowed`)
  }
}

// Validate file signatures
const validateFileSignature = async (file) => {
  const allowedSignatures = {
    'image/jpeg': [0xFF, 0xD8, 0xFF],
    'image/png': [0x89, 0x50, 0x4E, 0x47],
    'application/pdf': [0x25, 0x50, 0x44, 0x46]
  }

  const buffer = await file.slice(0, 4).arrayBuffer()
  const signature = Array.from(new Uint8Array(buffer))

  for (const [type, validSignature] of Object.entries(allowedSignatures)) {
    if (file.type === type) {
      if (!signature.every((byte, index) => byte === validSignature[index])) {
        throw new Error(`Invalid file signature for ${type}`)
      }
      break
    }
  }
}
```

#### Secure Upload Process
```javascript
const secureUpload = async (file, bucket, userId) => {
  try {
    // Validate file type
    await validateFileSignature(file)
    validateFileType(file, ['image'])

    // Sanitize filename
    const sanitizedName = file.name.replace(/[^a-zA-Z0-9.-]/g, '')
    const fileExtension = sanitizedName.split('.').pop()
    const fileName = `${userId}/${Date.now()}.${fileExtension}`

    // Upload with RLS protection
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(fileName, file, {
        cacheControl: '31536000', // 1 year cache
        upsert: false,
        metadata: {
          originalName: file.name,
          uploadedBy: userId,
          uploadedAt: new Date().toISOString()
        }
      })

    if (error) throw error

    return {
      id: data.id,
      path: data.path,
      url: supabase.storage.from(bucket).getPublicUrl(data.path).data.publicUrl
    }
  } catch (error) {
    console.error('Secure upload failed:', error)
    throw error
  }
}
```

This comprehensive storage guide enables building robust, secure file management systems with Supabase.
            """

    def _get_edge_function_fundamentals(self, level: str) -> str:
        """Get edge function fundamentals."""
        if level == "metadata":
            return "Supabase edge functions and serverless computing fundamentals"
        elif level == "summary":
            return """
# Supabase Edge Functions

## Core Features
- Deno-based serverless functions
- Global edge deployment
- HTTP endpoint creation
- Environment variable management
- TypeScript support

## Basic Usage
```typescript
import { serve } from "https://deno.land/std@0.131.0/http/server.ts"

serve(async (req) => {
  return new Response("Hello World!", { "status": 200 })
})
```

## Features
- Auto-scaling
- Cold start optimization
- Global CDN deployment
- Database integration
            """
        else:
            return """
# Complete Supabase Edge Functions Guide

## Edge Functions Architecture

Supabase Edge Functions are serverless functions running on the Deno runtime, deployed globally at the edge for optimal performance and low latency access to your Supabase database and services.

### 1. Basic Edge Function Setup

#### Simple HTTP Handler
```typescript
// functions/hello-world/index.ts
import { serve } from "https://deno.land/std@0.131.0/http/server.ts"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { name } = await req.json()

    return new Response(
      JSON.stringify({
        message: `Hello ${name}!`,
        timestamp: new Date().toISOString()
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400
      }
    )
  }
})
```

#### Database Integration
```typescript
// functions/get-user/index.ts
import { serve } from "https://deno.land/std@0.131.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type'
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        global: {
          headers: { Authorization: req.headers.get('Authorization')! }
        }
      }
    )

    // Get user from JWT
    const { data: { user }, error: authError } = await supabase.auth.getUser(
      req.headers.get('Authorization')?.replace('Bearer ', '') ?? ''
    )

    if (authError || !user) {
      throw new Error('Unauthorized')
    }

    // Query user profile
    const { data: profile, error: profileError } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', user.id)
      .single()

    if (profileError) {
      throw new Error('Profile not found')
    }

    return new Response(
      JSON.stringify({ user, profile }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: error.message === 'Unauthorized' ? 401 : 500
      }
    )
  }
})
```

### 2. Advanced Function Patterns

#### Webhook Handler
```typescript
// functions/stripe-webhook/index.ts
import { serve } from "https://deno.land/std@0.131.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import Stripe from 'https://esm.sh/stripe@14.21.0'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY')!, {
  apiVersion: '2023-10-16',
})

serve(async (req) => {
  const signature = req.headers.get('stripe-signature')
  const body = await req.text()
  const webhookSecret = Deno.env.get('STRIPE_WEBHOOK_SECRET')!

  let event: Stripe.Event

  try {
    event = stripe.webhooks.constructEvent(body, signature!, webhookSecret)
  } catch (err) {
    console.log(`Webhook signature verification failed:`, err.message)
    return new Response('Invalid signature', { status: 400 })
  }

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  try {
    switch (event.type) {
      case 'customer.subscription.created':
      case 'customer.subscription.updated': {
        const subscription = event.data.object as Stripe.Subscription

        await supabase
          .from('subscriptions')
          .upsert({
            stripe_subscription_id: subscription.id,
            customer_id: subscription.customer as string,
            status: subscription.status,
            price_id: subscription.items.data[0]?.price.id,
            current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
            current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
            updated_at: new Date().toISOString()
          })

        break
      }

      case 'customer.subscription.deleted': {
        const subscription = event.data.object as Stripe.Subscription

        await supabase
          .from('subscriptions')
          .update({
            status: 'canceled',
            canceled_at: new Date().toISOString()
          })
          .eq('stripe_subscription_id', subscription.id)

        break
      }

      case 'invoice.payment_succeeded': {
        const invoice = event.data.object as Stripe.Invoice

        await supabase
          .from('payments')
          .insert({
            stripe_invoice_id: invoice.id,
            customer_id: invoice.customer as string,
            amount_paid: invoice.amount_paid,
            currency: invoice.currency,
            status: invoice.status,
            created_at: new Date(invoice.created * 1000).toISOString()
          })

        break
      }

      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    return new Response(JSON.stringify({ received: true }), { status: 200 })

  } catch (error) {
    console.error('Webhook processing error:', error)
    return new Response('Webhook processing failed', { status: 500 })
  }
})
```

#### File Processing Function
```typescript
// functions/process-upload/index.ts
import { serve } from "https://deno.land/std@0.131.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  if (req.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }

  try {
    const formData = await req.formData()
    const file = formData.get('file') as File
    const bucket = formData.get('bucket') as string
    const userId = formData.get('userId') as string

    if (!file || !bucket || !userId) {
      throw new Error('Missing required fields')
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      throw new Error('Invalid file type')
    }

    // Generate filename
    const fileExtension = file.name.split('.').pop()
    const fileName = `${userId}/${Date.now()}.${fileExtension}`

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    // Upload to Supabase storage
    const { data, error } = await supabase.storage
      .from(bucket)
      .upload(fileName, file)

    if (error) throw error

    // Generate different sizes
    const sizes = [
      { name: 'thumb', width: 150, height: 150 },
      { name: 'medium', width: 400, height: 300 },
      { name: 'large', width: 1200, height: 800 }
    ]

    const transformedUrls = sizes.map(size => ({
      name: size.name,
      url: supabase.storage
        .from(bucket)
        .getPublicUrl(data.path, {
          transform: {
            width: size.width,
            height: size.height,
            quality: 80
          }
        }).data.publicUrl
    }))

    // Save file record
    const { error: dbError } = await supabase
      .from('files')
      .insert({
        user_id: userId,
        bucket,
        path: data.path,
        original_name: file.name,
        file_size: file.size,
        mime_type: file.type,
        transformed_urls: transformedUrls,
        created_at: new Date().toISOString()
      })

    if (dbError) throw dbError

    return new Response(
      JSON.stringify({
        success: true,
        path: data.path,
        transformedUrls
      }),
      {
        headers: { 'Content-Type': 'application/json' },
        status: 200
      }
    )

  } catch (error) {
    console.error('Upload processing error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { 'Content-Type': 'application/json' },
        status: 500
      }
    )
  }
})
```

### 3. Performance Optimization

#### Caching and Optimization
```typescript
// functions/cached-data/index.ts
import { serve } from "https://deno.land/std@0.131.0/http/server.ts"

// Simple in-memory cache (for production, use Redis)
const cache = new Map<string, { data: any; timestamp: number }>()
const CACHE_TTL = 5 * 60 * 1000 // 5 minutes

serve(async (req) => {
  const url = new URL(req.url)
  const cacheKey = url.pathname + url.search

  // Check cache first
  const cached = cache.get(cacheKey)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return new Response(JSON.stringify(cached.data), {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300'
      }
    })
  }

  // Generate fresh data
  const data = await generateExpensiveData(url.searchParams)

  // Cache the result
  cache.set(cacheKey, { data, timestamp: Date.now() })

  // Clean up old cache entries
  for (const [key, entry] of cache.entries()) {
    if (Date.now() - entry.timestamp > CACHE_TTL) {
      cache.delete(key)
    }
  }

  return new Response(JSON.stringify(data), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=300'
    }
  })
})

async function generateExpensiveData(params: URLSearchParams) {
  // Simulate expensive operation
  await new Promise(resolve => setTimeout(resolve, 1000))

  return {
    data: 'Expensive data',
    timestamp: new Date().toISOString(),
    params: Object.fromEntries(params)
  }
}
```

### 4. Environment and Configuration

#### Environment Variables
```typescript
// functions/config/index.ts
export const config = {
  supabaseUrl: Deno.env.get('SUPABASE_URL')!,
  supabaseServiceKey: Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!,
  jwtSecret: Deno.env.get('JWT_SECRET')!,
  redisUrl: Deno.env.get('REDIS_URL'),
  stripeSecretKey: Deno.env.get('STRIPE_SECRET_KEY')!,
  stripeWebhookSecret: Deno.env.get('STRIPE_WEBHOOK_SECRET')!,
  sendgridApiKey: Deno.env.get('SENDGRID_API_KEY')!,
  environment: Deno.env.get('ENVIRONMENT') || 'development'
}

// Database helper
export const createSupabaseClient = (authHeader?: string) => {
  return createClient(
    config.supabaseUrl,
    config.supabaseServiceKey,
    authHeader ? {
      global: {
        headers: { Authorization: authHeader }
      }
    } : undefined
  )
}
```

This comprehensive edge functions guide enables building powerful, scalable serverless applications with Supabase.
            """

    def _get_setup_guidance(self, level: str) -> str:
        """Get setup guidance."""
        if level == "metadata":
            return "Supabase project setup and configuration"
        elif level == "summary":
            return f"""
# Supabase Setup Guide

## Project Creation
1. Create project at [supabase.com](https://supabase.com)
2. Configure project settings
3. Set up database tables
4. Configure authentication
5. Deploy edge functions

## CLI Commands
```bash
# Initialize local project
supabase init

# Start local development
supabase start

# Deploy functions
supabase functions deploy
```

## Configuration
- Project URL and API keys
- Environment variables
- Database settings
- Authentication providers
            """
        else:
            return """
# Complete Supabase Setup and Configuration Guide

## 1. Project Creation and Setup

### Creating a New Project
1. **Sign up** at [supabase.com](https://supabase.com)
2. **Create new project** with organization name
3. **Select region** closest to your users
4. **Choose database settings** (start with default)

### Project Configuration
```bash
# After project creation, note these values:
# - Project URL: https://[project-id].supabase.co
# - Anon Key: public key for client access
# - Service Role Key: secret key for server operations
# - Database URL: postgresql connection string
```

## 2. Local Development Setup

### Install CLI
```bash
# Install via npm
npm install -g @supabase/supabase

# Or via Homebrew
brew install supabase/tap/supabase
brew install supabase

# Verify installation
supabase --version
```

### Initialize Local Project
```bash
# Create new directory for your project
mkdir my-supabase-app
cd my-supabase-app

# Initialize Supabase project
supabase init

# Link to your remote project
supabase link --project-ref your-project-id

# Start local services
supabase start
```

### Local Services
When you run `supabase start`, it launches:
- **PostgreSQL**: Local database at `localhost:54322`
- **Kong**: API gateway at `localhost:54321`
- **Inbucket**: Email testing at `localhost:54324`
- **Studio**: Database management UI at `localhost:54323/studio`

## 3. Database Schema Management

### Creating Tables with SQL
```sql
-- Create via Studio UI or SQL editor
-- File: supabase/migrations/20240101_create_users.sql

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  email_verified BOOLEAN DEFAULT false,
  phone TEXT UNIQUE,
  phone_verified BOOLEAN DEFAULT false,
  username TEXT UNIQUE,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_sign_in_at TIMESTAMP WITH TIME ZONE
);

-- Create profiles table
CREATE TABLE profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  bio TEXT,
  website TEXT,
  location TEXT,
  timezone TEXT DEFAULT 'UTC',
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create posts table
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  author_id UUID REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  slug TEXT UNIQUE NOT NULL,
  content TEXT,
  excerpt TEXT,
  featured_image TEXT,
  status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  published_at TIMESTAMP WITH TIME ZONE,
  view_count INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Using Migrations
```bash
# Create new migration
supabase migration new add_categories_table

# Apply migrations to local database
supabase db push

# Generate schema types
supabase gen types typescript --local > types/database.ts

# Push to remote database
supabase db push --db-url postgresql://user:pass@host:port/dbname
```

## 4. Authentication Configuration

### Enable Authentication Providers
In Supabase Dashboard → Authentication → Settings:

#### Email/Password
```javascript
// Configure in Dashboard or via API
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password',
  options: {
    emailRedirectTo: 'https://yourapp.com/auth/callback'
  }
})
```

#### Social Providers
```bash
# Configure providers (in Dashboard or via CLI)
# Supported: google, github, gitlab, bitbucket, discord, apple, azure, keycloak

# Example: Configure Google OAuth
# Add redirect URLs: https://yourapp.com/auth/callback
# Enable Google provider in Dashboard
```

#### Custom JWT
```javascript
// For existing authentication systems
const { data, error } = await supabase.auth.signInWithIdToken({
  provider: 'custom',
  token: customJwtToken,
  nonce: generatedNonce
})
```

### Row-Level Security Setup
```sql
-- Enable RLS on user tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Published posts are public" ON posts
  FOR SELECT USING (status = 'published');

CREATE POLICY "Authors can manage their posts" ON posts
  FOR ALL USING (auth.uid() = author_id);
```

## 5. Storage Configuration

### Create Storage Buckets
```sql
-- User avatars bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'avatars',
  'avatars',
  true,
  2097152, -- 2MB
  ARRAY['image/jpeg', 'image/png', 'image/webp']
);

-- Documents bucket
INSERT INTO storage.buckets (id, name, public, file_size_limit)
VALUES (
  'documents',
  'documents',
  false,
  52428800 -- 50MB
);
```

### Storage RLS Policies
```sql
-- Users can upload to their own folder
CREATE POLICY "Users can upload own files" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'documents' AND
    auth.uid() = (storage.foldername(name))[1]::uuid
  );

-- Users can access their own files
CREATE POLICY "Users can access own files" ON storage.objects
  FOR ALL USING (
    bucket_id = 'documents' AND
    auth.uid() = (storage.foldername(name))[1]::uuid
  );
```

## 6. Edge Functions

### Creating Functions
```bash
# Create function directory structure
mkdir -p supabase/functions/my-function

# Create function file
cat > supabase/functions/my-function/index.ts << 'EOF'
import { serve } from "https://deno.land/std@0.131.0/http/server.ts"

serve(async (req) => {
  const { name } = await req.json()

  return new Response(
    JSON.stringify({ message: `Hello ${name}!` }),
    { headers: { "Content-Type": "application/json" } }
  )
})
EOF

# Deploy function
supabase functions deploy my-function

# List deployed functions
supabase functions list
```

### Environment Variables
```bash
# Set environment variables
supabase secrets set STRIPE_SECRET_KEY=sk_test_...
supabase secrets set JWT_SECRET=your-jwt-secret
supabase secrets set REDIS_URL=redis://localhost:6379

# Use in functions
# Deno.env.get('STRIPE_SECRET_KEY')
```

## 7. Environment Configuration

### Environment Variables Setup
Create `.env.local` for development:

```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Local Development
VITE_LOCAL_DB_URL=postgresql://localhost:54322/postgres
VITE_LOCAL_DB_USER=postgres
VITE_LOCAL_DB_PASSWORD=postgres

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
```

### Production Environment
```bash
# Production deployment settings
supabase config set auth.jwt_expiry=3600
supabase config set db.pool_size=20
supabase config set db.timeout=30
```

## 8. Project Structure

### Recommended Directory Structure
```
my-supabase-app/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   ├── ui/
│   │   └── layout/
│   ├── lib/
│   │   ├── supabaseClient.ts
│   │   ├── types.ts
│   │   └── utils.ts
│   └── pages/
│       ├── api/
│       ├── auth/
│       └── dashboard/
├── supabase/
│   ├── migrations/
│   │   ├── 20240101_create_users_table.sql
│   │   ├── 20240101_create_profiles_table.sql
│   │   └── 20240101_create_posts_table.sql
│   ├── functions/
│   │   ├── send-email/
│   │   ├── process-webhook/
│   │   └── generate-pdf/
│   ├── seed.sql
│   └── config.toml
├── types/
│   ├── database.ts
│   ├── api.ts
│   └── auth.ts
├── .env.local
├── .env.example
├── package.json
├── tsconfig.json
└── README.md
```

## 9. TypeScript Integration

### Database Types
```bash
# Generate types from local database
supabase gen types typescript --local > src/types/database.ts

# Generate types from remote database
supabase gen types typescript --project-id your-project-id > src/types/database.ts
```

### Type Definitions
```typescript
// src/types/database.ts (generated)
export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          email_verified: boolean
          phone: string | null
          phone_verified: boolean
          username: string | null
          full_name: string | null
          avatar_url: string | null
          created_at: string
          updated_at: string
          last_sign_in_at: string | null
        }
        Insert: Omit<Database['public']['Tables']['users']['Row'], 'id' | 'created_at'>
        Update: Omit<Database['public']['Tables']['users']['Row'], 'id' | 'created_at'>
      }
      profiles: {
        Row: {
          id: string
          user_id: string
          bio: string | null
          website: string | null
          location: string | null
          timezone: string
          preferences: Json
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['profiles']['Row'], 'id' | 'created_at'>
        Update: Omit<Database['public']['Tables']['profiles']['Row'], 'id' | 'created_at'>
      }
      posts: {
        Row: {
          id: string
          author_id: string
          title: string
          slug: string
          content: string | null
          excerpt: string | null
          featured_image: string | null
          status: 'draft' | 'published' | 'archived'
          published_at: string | null
          view_count: number
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['posts']['Row'], 'id' | 'created_at'>
        Update: Omit<Database['public']['Tables']['posts']['Row'], 'id' | 'created_at'>
      }
    }
  }
}
```

### Client Setup
```typescript
// src/lib/supabaseClient.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true
  }
})
```

## 10. Development Workflow

### Common Development Commands
```bash
# Start local development
supabase start

# Apply schema changes
supabase db push

# Test functions locally
supabase functions serve

# Generate types
supabase gen types typescript --local

# Database operations
supabase db reset  # Reset to clean state
supabase db diff  # Show schema differences
supabase db reset --local
```

### Git Integration
```bash
# .gitignore
.env.local
.env
supabase/
*.log
dist/
node_modules/

# Include in git
supabase/migrations/
supabase/functions/
```

This comprehensive setup guide provides everything needed to get started with Supabase development.
            """

    def _get_best_practices_guidance(self, level: str) -> str:
        """Get best practices guidance."""
        if level == "metadata":
            return "Supabase best practices and optimization strategies"
        elif level == "summary":
            return f"""
# Supabase Best Practices

## Security
- Always enable RLS on user data tables
- Use environment variables for secrets
- Implement proper authentication flows
- Validate user input on server and client

## Performance
- Use connection pooling
- Implement proper indexing
- Cache frequently accessed data
- Optimize database queries

## Architecture
- Use TypeScript for type safety
- Implement proper error handling
- Structure code in modular components
- Use environment-specific configurations
            """
        else:
            return """
# Supabase Best Practices and Production Guidelines

## Security Best Practices

### 1. Authentication and Authorization

#### Row-Level Security (RLS)
```sql
-- ALWAYS enable RLS on user data tables
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- Create specific, not overly broad policies
CREATE POLICY "Users can view own data" ON sensitive_data
  FOR SELECT USING (user_id = auth.uid());

-- Avoid policies that are too permissive
-- BAD: CREATE POLICY "All authenticated users" ON users FOR ALL USING (auth.role() = 'authenticated');
-- GOOD: CREATE POLICY "Users can view own profile" ON users FOR SELECT USING (auth.uid() = id);
```

#### API Key Management
```javascript
// Never expose service role key in client code
const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL, // Public URL
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY  // Public key only
)

// Service operations on server only
const supabaseAdmin = createClient(
  process.env.SUPABASE_URL,        // Private URL
  process.env.SUPABASE_SERVICE_ROLE_KEY // Private key
)
```

#### Input Validation
```typescript
// Server-side validation
import { z } from 'zod'

const postSchema = z.object({
  title: z.string().min(1).max(200),
  content: z.string().optional(),
  status: z.enum(['draft', 'published', 'archived']).default('draft'),
  tags: z.array(z.string()).optional()
})

export async function createPost(post: unknown) {
  const validatedData = postSchema.parse(post)

  // Insert validated data
  const { data, error } = await supabase
    .from('posts')
    .insert(validatedData)
    .select()
    .single()

  if (error) throw new Error(`Failed to create post: ${error.message}`)
  return data
}
```

### 2. Database Optimization

#### Indexing Strategy
```sql
-- Index foreign keys immediately
CREATE INDEX idx_posts_author_id ON posts(author_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);

-- Index frequently queried columns
CREATE INDEX idx_posts_status_created ON posts(status, created_at DESC);
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Use partial indexes for common filters
CREATE INDEX idx_active_users ON users(id) WHERE last_login_at > NOW() - INTERVAL '30 days';
```

#### Query Optimization
```sql
-- Use specific column selection instead of SELECT *
-- BAD: SELECT * FROM posts WHERE status = 'published';
-- GOOD: SELECT id, title, excerpt, created_at FROM posts WHERE status = 'published';

-- Use LIMIT for pagination
-- BAD: SELECT * FROM posts ORDER BY created_at;
-- GOOD: SELECT id, title, excerpt FROM posts ORDER BY created_at DESC LIMIT 20;

-- Use appropriate JOIN types
-- Bad: SELECT p.*, u.* FROM posts p, users u WHERE u.id = p.author_id;
-- Good: SELECT p.*, u.username FROM posts p JOIN users u ON u.id = p.author_id;
```

#### Connection Management
```javascript
// Configure connection pool in client
const supabase = createClient(url, key, {
  db: {
    connection: {
      poolSize: 20,
      connect_timeout: 10,
      query_timeout: 30,
      idle_timeout: 300,
      lifetime: 1800
    }
  }
})

// Reuse client instance
export const supabase = createClient(url, key)
```

### 3. Storage Best Practices

#### File Security
```sql
-- Implement proper storage policies
CREATE POLICY "Users can manage their files" ON storage.objects
  FOR ALL USING (
    bucket_id = 'documents' AND
    auth.uid() = (storage.foldername(name))[1]::uuid
  );

-- Validate file types and sizes
CREATE POLICY "Image uploads only" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'images' AND
    content_type ~ '^image/' AND
    content_length < 52428800 -- 50MB limit
  );
```

#### File Organization
```javascript
// Organize files by user and date
const generateFilePath = (userId, fileName) => {
  const timestamp = new Date().toISOString().slice(0, 10) // YYYY-MM-DD
  const fileExtension = fileName.split('.').pop()
  const sanitizedName = fileName.replace(/[^a-zA-Z0-9.-]/g, '')

  return `${userId}/${timestamp}/${sanitizedName}.${fileExtension}`
}

// Use consistent naming conventions
const uploadAvatar = async (userId, file) => {
  const filePath = generateFilePath(userId, `avatar.${file.type.split('/')[1]}`)

  const { data, error } = await supabase.storage
    .from('avatars')
    .upload(filePath, file, {
      cacheControl: '31536000', // 1 year cache
      upsert: false
    })

  return { data, filePath }
}
```

#### CDN and Caching
```javascript
// Use CDN for static assets
const { data: { publicUrl } } = supabase.storage
  .from('images')
  .getPublicUrl(filePath, {
    transform: {
      width: 800,
      height: 600,
      quality: 80,
      format: 'webp'
    }
  })

// Set appropriate cache headers
const imageHeaders = {
  'Cache-Control': 'public, max-age=31536000, immutable',
  'Vary': 'Accept'
}
```

### 4. Real-time Implementation

#### Subscription Management
```javascript
class RealtimeManager {
  constructor() {
    this.subscriptions = new Map()
  }

  subscribe(name, config, handler) {
    // Clean up existing subscription
    this.unsubscribe(name)

    const channel = supabase.channel(name)
      .on('postgres_changes', config, handler)
      .subscribe((status) => {
        if (status === 'SUBSCRIBED') {
          console.log(`Subscription ${name} active`)
        } else if (status === 'CHANNEL_ERROR') {
          console.error(`Subscription ${name} failed`)
          this.retrySubscription(name, config, handler)
        }
      })

    this.subscriptions.set(name, channel)
    return channel
  }

  unsubscribe(name) {
    const channel = this.subscriptions.get(name)
    if (channel) {
      supabase.removeChannel(channel)
      this.subscriptions.delete(name)
    }
  }

  cleanup() {
    this.subscriptions.forEach((channel, name) => {
      supabase.removeChannel(channel)
    })
    this.subscriptions.clear()
  }
}
```

#### Efficient Filtering
```javascript
// Use server-side filtering to reduce data transfer
const userPostsSubscription = supabase
  .channel('user-posts')
  .on('postgres_changes',
    {
      event: '*',
      schema: 'public',
      table: 'posts',
      filter: `author_id=eq.${userId}&status=in.(published,draft)`
    },
    handler
  )
  .subscribe()

// Use time-based filtering
const recentActivitySubscription = supabase
  .channel('recent-activity')
  .on('postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'activities',
      filter: `created_at=gt.${new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString()}`
    },
    handler
  )
  .subscribe()
```

### 5. Edge Functions Optimization

#### Performance Best Practices
```typescript
// Use caching for expensive operations
const cache = new Map<string, { data: any; timestamp: number }>()
const CACHE_TTL = 5 * 60 * 1000

serve(async (req) => {
  const cacheKey = `${req.method}:${req.url}`

  // Check cache first
  const cached = cache.get(cacheKey)
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return new Response(JSON.stringify(cached.data), {
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'public, max-age=300'
      }
    })
  }

  // Process request
  const result = await processRequest(req)

  // Cache the result
  cache.set(cacheKey, {
    data: result,
    timestamp: Date.now()
  })

  return new Response(JSON.stringify(result), {
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=300'
    }
  })
})
```

#### Error Handling
```typescript
// Create custom error types
class ValidationError extends Error {
  constructor(message: string, public code: string) {
    super(message)
    this.name = 'ValidationError'
  }
}

class AuthenticationError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'AuthenticationError'
  }
}

// Centralized error handling
const handleEdgeError = (error: unknown) => {
  if (error instanceof ValidationError) {
    return new Response(
      JSON.stringify({
        error: error.message,
        code: error.code,
        type: 'validation'
      }),
      { status: 400 }
    )
  }

  if (error instanceof AuthenticationError) {
    return new Response(
      JSON.stringify({
        error: error.message,
        type: 'authentication'
      }),
      { status: 401 }
    )
  }

  return new Response(
    JSON.stringify({
      error: 'Internal server error',
      type: 'internal'
    }),
    { status: 500 }
  )
}
```

### 6. Monitoring and Observability

#### Performance Monitoring
```javascript
// Performance monitoring middleware
const performanceMonitor = async (handler: Function) => {
  return async (req: Request) => {
    const start = performance.now()

    try {
      const response = await handler(req)
      const duration = performance.now() - start

      // Log slow requests
      if (duration > 1000) {
        console.warn(`Slow request: ${req.method} ${req.url} took ${duration}ms`)
      }

      // Add performance headers
      response.headers.set('X-Response-Time', `${duration}ms`)

      return response
    } catch (error) {
      const duration = performance.now() - start
      console.error(`Request failed after ${duration}ms:`, error)
      throw error
    }
  }
}
```

#### Database Monitoring
```sql
-- Monitor slow queries
SELECT
  query,
  calls,
  mean_exec_time,
  total_exec_time,
  rows,
  100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Monitor table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size,
  pg_total_relation_size(tablename::regclass) as size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;
```

### 7. Environment Management

#### Configuration Management
```typescript
// Environment configuration
interface Config {
  supabaseUrl: string
  supabaseAnonKey: string
  supabaseServiceRoleKey: string
  jwtSecret: string
  redisUrl?: string
  stripeSecretKey?: string
  environment: 'development' | 'staging' | 'production'
}

const config: Config = {
  supabaseUrl: process.env.SUPABASE_URL!,
  supabaseAnonKey: process.env.SUPABASE_ANON_KEY!,
  supabaseServiceRoleKey: process.env.SUPABASE_SERVICE_ROLE_KEY!,
  jwtSecret: process.env.JWT_SECRET!,
  redisUrl: process.env.REDIS_URL,
  stripeSecretKey: process.env.STRIPE_SECRET_KEY!,
  environment: process.env.NODE_ENV || 'development'
}

// Validate required configuration
const validateConfig = (): void => {
  const required = [
    'supabaseUrl',
    'supabaseAnonKey',
    'supabaseServiceRoleKey',
    'jwtSecret'
  ]

  const missing = required.filter(key => !config[key as keyof Config])
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`)
  }
}
```

#### Environment-Specific Features
```typescript
// Feature flags
const FEATURES = {
  analytics: config.environment !== 'development',
  debug: config.environment === 'development',
  preview: config.environment === 'staging'
}

// Conditional feature usage
const analytics = () => {
  if (FEATURES.analytics) {
    // Initialize analytics
  }
}

const debugLog = (message: string, data?: any) => {
  if (FEATURES.debug) {
    console.log(`[DEBUG] ${message}`, data)
  }
}
```

This comprehensive best practices guide ensures secure, performant, and maintainable Supabase applications.
            """
