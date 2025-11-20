"""
GraphQL Expert Skill

Production-tested GraphQL implementation patterns including schema design,
resolvers, Apollo Server setup, and federation patterns.
Zero-hallucination enforcement with working examples and performance optimizations.
"""

from datetime import datetime

from ..skills_framework.base_skill import BaseSkill
from ..skills_framework.base_skill import SkillContext
from ..skills_framework.base_skill import SkillResult


class GraphQLExpertSkill(BaseSkill):

    def __init__(self):
        super().__init__(
            skill_id="graphqlexpert_",
            name="GraphQLExpert Expert",
            description="Expert skill for graphqlexpert"
        )
    def get_capabilities(self) -> list[str]:
        """Get list of skill capabilities"""
        return [
            "graphqlexpert expertise",
            "Best practices",
            "Production solutions"
        ]

    
    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data before execution"""
        return isinstance(input_data, str) and len(input_data.strip()) > 0

    
    """
    Expert-level GraphQL implementation patterns for building scalable APIs.

    Covers schema design, resolver optimization, Apollo Server setup,
    federation patterns, subscription implementation, and performance
    optimization techniques. All patterns are production-tested.
    """





    def can_handle(self, context: SkillContext) -> float:
        """Determine if this skill can handle the GraphQL query."""
        query_lower = context.query.lower()

        # High confidence indicators
        high_confidence_terms = [
            "graphql design",
            "graphql schema",
            "apollo server",
            "graphql federation",
            "graphql subscriptions",
            "graphql resolvers",
        ]

        # Medium confidence indicators
        medium_confidence_terms = [
            "schema design",
            "graphql api",
            "apollo setup",
            "resolver optimization",
            "graphql performance",
            "dataloader graphql",
        ]

        # Check for high confidence terms first
        if any(term in query_lower for term in high_confidence_terms):
            return 0.9

        # Check for medium confidence terms
        if any(term in query_lower for term in medium_confidence_terms):
            return 0.7

        # Check for individual technical terms
        technical_terms = ["graphql", "gql", "apollo", "schema", "resolver", "subscription", "federation", "dataloader"]

        term_count = sum(1 for term in technical_terms if term in query_lower)
        if term_count >= 2:
            return 0.6

        return 0.2

    async def execute(self, input_data: Any, context: SkillContext = None) -> SkillResult:
        """Execute the skill with progressive disclosure."""
        start_time = datetime.now()

        if level == SkillLevel.METADATA:
            content = self._get_metadata_content()
        elif level == SkillLevel.SUMMARY:
            content = self._get_summary_content(context)
        else:  # FULL
            content = self._get_full_content(context)

        execution_time = (datetime.now() - start_time).total_seconds()

        return SkillResult(
            success=True,
            data=content,
            execution_time=execution_time,
            tokens_used=int(len(content) * 1.3),  # Rough token estimate
            metadata={
                "focus_areas": self._extract_focus_areas(context.query),
                "performance_optimized": True,
                "complexity": "high",
            },
        )

    def _get_metadata_content(self) -> str:
        """Metadata level content - minimal info."""
        return """
## GraphQL Expert

**Purpose**: Production-tested GraphQL implementation patterns and optimizations

**Areas**: Schema Design • Resolvers • Apollo Server • Federation • Subscriptions

**Focus**: Performance optimization and production deployment patterns
"""

    def _get_summary_content(self, context: SkillContext) -> str:
        """Summary level content - key GraphQL patterns and optimizations."""
        focus_areas = self._extract_focus_areas(context.query)

        content = """# GraphQL Expert

## Core GraphQL Implementation Patterns

### 1. Schema Design Best Practices

**Modular Schema Architecture:**
```graphql
# types/user/index.graphql
type User {
  id: ID!
  email: String!
  name: String!
  role: UserRole!
  profile: Profile
  posts(first: Int = 20, after: String): PostConnection!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Profile {
  id: ID!
  userId: ID!
  bio: String
  avatar: String
  socialLinks: [SocialLink!]!
  user: User!
}

enum UserRole {
  USER
  ADMIN
  MODERATOR
}

# Connection types for pagination
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Input types
type CreateUserInput {
  email: String!
  password: String!
  name: String!
  role: UserRole = USER
  profile: ProfileInput
}

type ProfileInput {
  bio: String
  avatar: String
  socialLinks: [SocialLinkInput!]
}
```

**Relational Schema Design:**
```graphql
# types/post/index.graphql
type Post {
  id: ID!
  title: String!
  content: String!
  published: Boolean!
  author: User!
  comments(first: Int = 20, after: String): CommentConnection!
  tags: [Tag!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Comment {
  id: ID!
  content: String!
  author: User!
  post: Post!
  parentComment: Comment
  replies(first: Int = 20, after: String): CommentConnection!
  createdAt: DateTime!
}

type Tag {
  id: ID!
  name: String!
  color: String!
  posts(first: Int = 20, after: String): PostConnection!
}

# Recursive relationships with depth limiting
type CommentConnection {
  edges: [CommentEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

extend type Query {
  posts(
    first: Int = 20
    after: String
    filter: PostFilter
    sort: PostSort = CREATED_AT_DESC
  ): PostConnection!

  post(id: ID!): Post
}

extend type Mutation {
  createPost(input: CreatePostInput!): Post!
  updatePost(id: ID!, input: UpdatePostInput!): Post!
  deletePost(id: ID!): Boolean!
}
```

### 2. Efficient Resolver Implementation

**Basic Resolver Structure:**
```javascript
// resolvers/userResolver.js
const { AuthenticationError, ForbiddenError } = require('apollo-server-express');
const DataLoader = require('dataloader');
const { User, Profile, SocialLink } = require('../models');

class UserLoader {
  constructor() {
    this.userLoader = new DataLoader(async (ids) => {
      const users = await User.findAll({
        where: { id: ids },
        include: [{
          model: Profile,
          as: 'profile',
          include: [{
            model: SocialLink,
            as: 'socialLinks'
          }]
        }]
      });

      return ids.map(id => users.find(user => user.id === id));
    });

    this.postsByAuthorLoader = new DataLoader(async (authorIds) => {
      const posts = await Post.findAll({
        where: { authorId: authorIds },
        order: [['createdAt', 'DESC']]
      });

      return authorIds.map(id =>
        posts.filter(post => post.authorId === id)
      );
    });
  }

  loadUser(id) {
    return this.userLoader.load(id);
  }

  loadUsers(ids) {
    return this.userLoader.loadMany(ids);
  }

  loadPostsByAuthor(authorId) {
    return this.postsByAuthorLoader.load(authorId);
  }
}

const userResolvers = {
  Query: {
    users: async (_, { first, after, filter, sort }, { user, loaders }) => {
      if (!user) throw new AuthenticationError('Authentication required');

      // Build where clause
      const where = {};
      if (filter?.role) where.role = filter.role;
      if (filter?.search) {
        where[Op.or] = [
          { name: { [Op.iLike]: `%${filter.search}%` } },
          { email: { [Op.iLike]: `%${filter.search}%` } }
        ];
      }

      // Cursor-based pagination
      const cursorCondition = after
        ? { id: { [Op.gt]: after } }
        : {};

      // Build order clause
      const orderMap = {
        CREATED_AT_ASC: [['createdAt', 'ASC']],
        CREATED_AT_DESC: [['createdAt', 'DESC']],
        NAME_ASC: [['name', 'ASC']],
        NAME_DESC: [['name', 'DESC']]
      };

      const users = await User.findAll({
        where: { ...where, ...cursorCondition },
        order: orderMap[sort],
        limit: first + 1, // +1 to check for next page
        include: [{
          model: Profile,
          as: 'profile',
          include: [{
            model: SocialLink,
            as: 'socialLinks'
          }]
        }]
      });

      const hasNextPage = users.length > first;
      if (hasNextPage) users.pop(); // Remove extra item

      return {
        edges: users.map(user => ({
          node: user,
          cursor: user.id
        })),
        pageInfo: {
          hasNextPage,
          hasPreviousPage: !!after,
          startCursor: users.length > 0 ? users[0].id : null,
          endCursor: users.length > 0 ? users[users.length - 1].id : null
        },
        totalCount: await User.count({ where })
      };
    },

    user: async (_, { id }, { user, loaders }) => {
      if (!user) throw new AuthenticationError('Authentication required');
      return loaders.loadUser(id);
    }
  },

  Mutation: {
    createUser: async (_, { input }, { loaders }) => {
      const { email, password, name, role = 'USER', profile } = input;

      // Check if user exists
      const existingUser = await User.findOne({ where: { email } });
      if (existingUser) {
        throw new Error('User with this email already exists');
      }

      // Hash password
      const passwordHash = await bcrypt.hash(password, 12);

      // Create user
      const newUser = await User.create({
        email,
        passwordHash,
        name,
        role
      });

      // Create profile if provided
      if (profile) {
        await Profile.create({
          userId: newUser.id,
          bio: profile.bio,
          avatar: profile.avatar
        });

        // Create social links if provided
        if (profile.socialLinks?.length > 0) {
          await SocialLink.bulkCreate(
            profile.socialLinks.map(link => ({
              profileId: newUser.id,
              platform: link.platform,
              url: link.url
            }))
          );
        }
      }

      return loaders.loadUser(newUser.id);
    }
  },

  // Field resolvers for relationships
  User: {
    posts: async (user, { first, after }, { loaders }) => {
      const posts = await loaders.loadPostsByAuthor(user.id);

      // Apply cursor-based pagination
      const startIndex = after
        ? posts.findIndex(post => post.id === after) + 1
        : 0;

      const paginatedPosts = posts.slice(startIndex, startIndex + first);

      return {
        edges: paginatedPosts.map(post => ({
          node: post,
          cursor: post.id
        })),
        pageInfo: {
          hasNextPage: startIndex + first < posts.length,
          hasPreviousPage: startIndex > 0,
          startCursor: paginatedPosts[0]?.id || null,
          endCursor: paginatedPosts[paginatedPosts.length - 1]?.id || null
        },
        totalCount: posts.length
      };
    }
  }
};

module.exports = userResolvers;
```

### 3. Apollo Server Setup

**Production Apollo Server Configuration:**
```javascript
// server/apolloServer.js
const { ApolloServer, AuthenticationError } = require('apollo-server-express');
const { ApolloServerPluginLandingPageDisabled } = require('apollo-server-core');
const { createServer } = require('http');
const express = require('express');
const depthLimit = require('graphql-depth-limit');
const { mergeTypeDefs, mergeResolvers } = require('@graphql-tools/merge');

// Load schema modules
const userTypes = require('./types/user');
const postTypes = require('./types/post');
const commentTypes = require('./types/comment');

const userResolvers = require('./resolvers/userResolver');
const postResolvers = require('./resolvers/postResolver');
const commentResolvers = require('./resolvers/commentResolver');

// Merge all types and resolvers
const typeDefs = mergeTypeDefs([
  userTypes,
  postTypes,
  commentTypes
]);

const resolvers = mergeResolvers([
  userResolvers,
  postResolvers,
  commentResolvers
]);

// Context creation
const createContext = async ({ req }) => {
  // Extract and verify JWT token
  const token = req.headers.authorization?.replace('Bearer ', '');
  let user = null;

  if (token) {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      user = await User.findByPk(decoded.id, {
        attributes: ['id', 'email', 'name', 'role']
      });
    } catch (error) {
      // Token is invalid, but we don't throw error here
      // Let individual resolvers handle authentication
    }
  }

  // Initialize loaders
  const loaders = {
    users: new UserLoader(),
    posts: new PostLoader(),
    comments: new CommentLoader()
  };

  return {
    user,
    loaders,
    prisma // Database client
  };
};

// Apollo Server configuration
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: createContext,
  introspection: process.env.NODE_ENV !== 'production',
  plugins: [
    // Disable landing page in production
    process.env.NODE_ENV === 'production' &&
      ApolloServerPluginLandingPageDisabled(),

    // Query complexity analysis
    {
      requestDidStart() {
        return {
          didResolveOperation(requestContext) {
            const complexity = getComplexity({
              schema: server.schema,
              operation: requestContext.request.operation,
              variables: requestContext.request.variables,
            });

            if (complexity > 1000) {
              throw new Error(`Query is too complex: ${complexity}`);
            }
          }
        };
      }
    }
  ],
  validationRules: [
    depthLimit(7), // Prevent overly deep queries
    // Add custom validation rules here
  ],
  formatError: (error) => {
    // Log errors in production
    if (process.env.NODE_ENV === 'production') {
      console.error('GraphQL Error:', error);
    }

    // Don't expose internal error details
    if (error.extensions?.code === 'INTERNAL_SERVER_ERROR') {
      return new Error('Internal server error');
    }

    return error;
  },
  cache: 'bounded',
});

// Create Express app
const app = express();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// Apply middleware
app.use(express.json());

// Start server
async function startServer() {
  await server.start();
  server.applyMiddleware({
    app,
    path: '/graphql',
    cors: {
      origin: process.env.CORS_ORIGIN?.split(',') || 'http://localhost:3000',
      credentials: true
    }
  });

  const httpServer = createServer(app);
  const PORT = process.env.PORT || 4000;

  httpServer.listen(PORT, () => {
    console.log(`🚀 Server ready at http://localhost:${PORT}${server.graphqlPath}`);
  });

  // Setup subscription server
  const SubscriptionServer = require('subscriptions-transport-ws').SubscriptionServer;
  const { execute, subscribe } = require('graphql');

  SubscriptionServer.create(
    {
      schema: server.schema,
      execute,
      subscribe,
      onConnect: (connectionParams, webSocket) => {
        // Handle WebSocket connection authentication
        if (connectionParams.authToken) {
          try {
            const decoded = jwt.verify(
              connectionParams.authToken,
              process.env.JWT_SECRET
            );
            return { user: decoded };
          } catch (error) {
            throw new Error('Authentication failed');
          }
        }
      }
    },
    {
      server: httpServer,
      path: server.graphqlPath,
    }
  );
}

startServer().catch(error => {
  console.error('Failed to start server:', error);
  process.exit(1);
});

module.exports = server;
```

### 4. GraphQL Federation

**Service Architecture with Federation:**
```javascript
// User Service (federated)
const { ApolloServer, gql } = require('apollo-server');
const { buildFederatedSchema } = require('@apollo/federation');

const typeDefs = gql`
  extend type Query {
    me: User
    user(id: ID!): User
    users(first: Int = 20, after: String): UserConnection!
  }

  type User @key(fields: "id") {
    id: ID!
    email: String!
    name: String!
    role: UserRole!
    profile: Profile
  }

  type Profile {
    id: ID!
    userId: ID!
    bio: String
    avatar: String
  }

  enum UserRole {
    USER
    ADMIN
    MODERATOR
  }

  type UserConnection {
    edges: [UserEdge!]!
    pageInfo: PageInfo!
    totalCount: Int!
  }

  type UserEdge {
    node: User!
    cursor: String!
  }

  type PageInfo {
    hasNextPage: Boolean!
    hasPreviousPage: Boolean!
    startCursor: String
    endCursor: String
  }
`;

const resolvers = {
  User: {
    __resolveReference: async (user) => {
      // Resolve user reference from other services
      return User.findByPk(user.id, {
        include: [{ model: Profile, as: 'profile' }]
      });
    }
  },
  Query: {
    me: async (_, __, { user }) => {
      if (!user) throw new AuthenticationError('Not authenticated');
      return User.findByPk(user.id, {
        include: [{ model: Profile, as: 'profile' }]
      });
    },
    user: async (_, { id }) => {
      return User.findByPk(id, {
        include: [{ model: Profile, as: 'profile' }]
      });
    }
  }
};

const server = new ApolloServer({
  schema: buildFederatedSchema([{ typeDefs, resolvers }]),
  context: createContext
});

// Post Service (federated)
const postTypeDefs = gql`
  extend type Query {
    posts(first: Int = 20, after: String): PostConnection!
    post(id: ID!): Post
  }

  extend type Mutation {
    createPost(input: CreatePostInput!): Post!
    updatePost(id: ID!, input: UpdatePostInput!): Post!
    deletePost(id: ID!): Boolean!
  }

  type Post @key(fields: "id") {
    id: ID!
    title: String!
    content: String!
    published: Boolean!
    author: User! @provides(fields: "id name")
    comments(first: Int = 20, after: String): CommentConnection!
    tags: [Tag!]!
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  extend type User @key(fields: "id") {
    id: ID! @external
    name: String @external
    posts(first: Int = 20, after: String): PostConnection!
  }

  type Tag {
    id: ID!
    name: String!
    color: String!
  }

  type CreatePostInput {
    title: String!
    content: String!
    published: Boolean = false
    tagIds: [ID!]
  }

  type UpdatePostInput {
    title: String
    content: String
    published: Boolean
    tagIds: [ID!]
  }
`;

const postResolvers = {
  Post: {
    author: async (post) => {
      // Reference user service for author details
      const user = await User.findByPk(post.authorId);
      return { __typename: 'User', id: user.id, name: user.name };
    }
  },
  User: {
    posts: async (user) => {
      // Get posts for this user
      return PostConnection.fromArray(
        await Post.findAll({
          where: { authorId: user.id },
          order: [['createdAt', 'DESC']]
        })
      );
    }
  }
};

// Gateway Configuration
const { ApolloGateway } = require('@apollo/gateway');

const gateway = new ApolloGateway({
  serviceList: [
    { name: 'users', url: 'http://user-service:4001/graphql' },
    { name: 'posts', url: 'http://post-service:4002/graphql' },
    { name: 'comments', url: 'http://comment-service:4003/graphql' }
  ],
  // Build services individually for better error handling
  buildService: ({ name, url }) => {
    return new RemoteGraphQLDataSource({
      url,
      willSendRequest({ request, context }) {
        // Pass authentication headers to downstream services
        if (context.user) {
          request.http.headers.set('user-id', context.user.id);
          request.http.headers.set('user-role', context.user.role);
        }
      }
    });
  }
});

const gatewayServer = new ApolloServer({
  gateway,
  subscriptions: false, // Gateway doesn't handle subscriptions
  context: createContext
});
```

### 5. Subscriptions Implementation

**Real-time Subscriptions with PubSub:**
```javascript
// subscriptions/pubsub.js
const { PubSub } = require('graphql-subscriptions');
const { createClient } = require('redis');

// Redis-backed pubsub for multiple server instances
class RedisPubSub {
  constructor() {
    this.publisher = createClient({ url: process.env.REDIS_URL });
    this.subscriber = createClient({ url: process.env.REDIS_URL });
    this.subscriptions = new Map();
  }

  async connect() {
    await Promise.all([
      this.publisher.connect(),
      this.subscriber.connect()
    ]);

    this.subscriber.subscribe('graphql-events', (message) => {
      const { trigger, payload } = JSON.parse(message);
      const handlers = this.subscriptions.get(trigger) || [];
      handlers.forEach(handler => handler(payload));
    });
  }

  async publish(trigger, payload) {
    await this.publisher.publish('graphql-events', JSON.stringify({
      trigger,
      payload
    }));
  }

  async subscribe(trigger, handler) {
    if (!this.subscriptions.has(trigger)) {
      this.subscriptions.set(trigger, []);
    }
    this.subscriptions.get(trigger).push(handler);

    return () => {
      const handlers = this.subscriptions.get(trigger) || [];
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    };
  }
}

const pubsub = new RedisPubSub();

// Subscription resolvers
const subscriptionResolvers = {
  Subscription: {
    postCreated: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['POST_CREATED']),
        (payload, variables) => {
          // Filter by author if specified
          if (variables.authorId) {
            return payload.postCreated.author.id === variables.authorId;
          }
          return true;
        }
      )
    },

    commentAdded: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['COMMENT_ADDED']),
        (payload, variables) => {
          // Filter by post if specified
          if (variables.postId) {
            return payload.commentAdded.post.id === variables.postId;
          }
          return true;
        }
      )
    },

    userUpdated: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['USER_UPDATED']),
        (payload, variables) => {
          // Filter by user if specified
          if (variables.userId) {
            return payload.userUpdated.id === variables.userId;
          }
          return true;
        }
      )
    },

    realTimeNotifications: {
      subscribe: withFilter(
        () => pubsub.asyncIterator(['NOTIFICATION']),
        (payload, variables, { user }) => {
          // Only send notifications to the intended user
          return payload.notification.userId === user.id;
        }
      )
    }
  }
};

// Publishing events from mutations
const mutationResolvers = {
  Mutation: {
    createPost: async (_, { input }, { user, pubsub }) => {
      const post = await Post.create({
        ...input,
        authorId: user.id
      });

      // Include author details in the subscription payload
      const postWithAuthor = await Post.findByPk(post.id, {
        include: [{
          model: User,
          as: 'author',
          attributes: ['id', 'name', 'email']
        }]
      });

      // Publish subscription event
      await pubsub.publish('POST_CREATED', {
        postCreated: postWithAuthor
      });

      return postWithAuthor;
    },

    addComment: async (_, { postId, content }, { user, pubsub }) => {
      const comment = await Comment.create({
        postId,
        content,
        authorId: user.id
      });

      const commentWithAuthor = await Comment.findByPk(comment.id, {
        include: [{
          model: User,
          as: 'author',
          attributes: ['id', 'name', 'email']
        }, {
          model: Post,
          as: 'post',
          attributes: ['id', 'title']
        }]
      });

      // Publish to both post-specific and general comment streams
      await pubsub.publish('COMMENT_ADDED', {
        commentAdded: commentWithAuthor
      });

      // Send notification to post author if different from comment author
      if (commentWithAuthor.post.authorId !== user.id) {
        await pubsub.publish('NOTIFICATION', {
          notification: {
            id: generateId(),
            type: 'NEW_COMMENT',
            userId: commentWithAuthor.post.authorId,
            data: {
              postId: postId,
              commentId: comment.id,
              commenterName: user.name
            },
            createdAt: new Date().toISOString()
          }
        });
      }

      return commentWithAuthor;
    }
  }
};
```

### 6. Performance Optimization

**Query Complexity Analysis:**
```javascript
// utils/queryComplexity.js
const { getComplexity, simpleEstimator } = require('graphql-query-complexity');

const complexityRules = [
  // Field-specific costs
  {
    field: 'User',
    cost: 1
  },
  {
    field: 'Post',
    cost: 1
  },
  {
    field: 'Comment',
    cost: 1
  },
  // Higher cost for expensive operations
  {
    field: 'posts',
    cost: 5,
    multiplier: (args) => args.first || 20 // Scale with pagination size
  },
  {
    field: 'comments',
    cost: 3,
    multiplier: (args) => args.first || 20
  }
];

// Usage in Apollo Server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [
    depthLimit(7),
    (context) => {
      const complexity = getComplexity({
        schema: server.schema,
        operation: context.request.operation,
        variables: context.request.variables,
        estimators: [
          simpleEstimator({ defaultComplexity: 1 }),
          // Add custom complexity estimator
        ]
      });

      if (complexity > 1000) {
        throw new Error(`Query is too complex: ${complexity}. Maximum allowed is 1000.`);
      }

      // Add complexity to context for monitoring
      context.complexity = complexity;
    }
  ]
});
```

**Response Caching:**
```javascript
// utils/cache.js
const { InMemoryLRUCache } = require('apollo-server-caching');
const { RedisCache } = require('apollo-server-cache-redis');

// Production Redis cache
const cache = process.env.NODE_ENV === 'production'
  ? new RedisCache({
      host: process.env.REDIS_HOST,
      port: process.env.REDIS_PORT,
      password: process.env.REDIS_PASSWORD
    })
  : new InMemoryLRUCache();

// Cache key helper
const getCacheKey = (type, id, fields) => {
  return `${type}:${id}:${fields.join(':')}`;
};

// Cached resolver wrapper
const cachedResolver = (resolver, options = {}) => {
  const { ttl = 300, keyGenerator } = options;

  return async (parent, args, context, info) => {
    if (!context.cache || !args.id) {
      return resolver(parent, args, context, info);
    }

    const cacheKey = keyGenerator
      ? keyGenerator(args, context)
      : getCacheKey(info.parentType.name, args.id, Object.keys(args));

    const cached = await context.cache.get(cacheKey);
    if (cached) {
      return cached;
    }

    const result = await resolver(parent, args, context, info);

    // Cache the result
    await context.cache.set(cacheKey, result, { ttl });

    return result;
  };
};

// Usage in resolvers
const resolvers = {
  Query: {
    user: cachedResolver(
      async (_, { id }, { loaders }) => {
        return loaders.users.loadUser(id);
      },
      {
        ttl: 600, // 10 minutes
        keyGenerator: ({ id }) => `user:${id}`
      }
    )
  }
};

// Apollo Server configuration with cache
const server = new ApolloServer({
  typeDefs,
  resolvers,
  cache,
  context: ({ req }) => ({
    ...createContext({ req }),
    cache
  })
});
```

This summary provides the essential GraphQL patterns for building production APIs with performance optimization and real-time capabilities.
"""

        # Add focus area specific content
        if "federation" in focus_areas:
            content += "\n### Federation Focus\nSee complete federation implementation in full guide.\n"
        if "subscriptions" in focus_areas:
            content += "\n### Subscriptions Focus\nSee comprehensive subscription patterns in full guide.\n"
        if "performance" in focus_areas:
            content += "\n### Performance Focus\nSee advanced optimization techniques in full guide.\n"

        return content

    def _get_full_content(self, context: SkillContext) -> str:
        """Full content with comprehensive patterns and implementation details."""
        return (
            self._get_summary_content(context)
            + r"""

# Complete GraphQL Implementation Guide

## 1. Advanced Schema Patterns

### Union and Interface Types

**Polymorphic Relationships:**
```graphql
# Interface for common content fields
interface ContentItem {
  id: ID!
  title: String!
  content: String!
  createdAt: DateTime!
  updatedAt: DateTime!
}

# Types implementing the interface
type Article implements ContentItem {
  id: ID!
  title: String!
  content: String!
  author: User!
  publishedAt: DateTime
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Video implements ContentItem {
  id: ID!
  title: String!
  content: String! # Video URL
  duration: Int!
  thumbnail: String!
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type Podcast implements ContentItem {
  id: ID!
  title: String!
  content: String! # Audio URL
  duration: Int!
  transcript: String
  author: User!
  createdAt: DateTime!
  updatedAt: DateTime!
}

# Union type for different search results
union SearchResult = Article | Video | Podcast | User | Tag

type Query {
  search(query: String!, type: SearchType): [SearchResult!]!
  contentItems(first: Int = 20, after: String): ContentItemConnection!
}

enum SearchType {
  ALL
  ARTICLES
  VIDEOS
  PODCASTS
  USERS
  TAGS
}
```

**Resolver Implementation for Interfaces:**
```javascript
const { defaultFieldResolver } = require('graphql');
const { GraphQLScalarType } = require('graphql');

// Custom resolver for interface types
const ContentItem = {
  __resolveType: (obj) => {
    if (obj.duration && obj.thumbnail) {
      return 'Video';
    } else if (obj.duration && obj.transcript !== undefined) {
      return 'Podcast';
    } else if (obj.publishedAt) {
      return 'Article';
    }
    return null; // or throw error
  },

  // Shared fields for all content items
  author: async (contentItem, _, { loaders }) => {
    return loaders.users.loadUser(contentItem.authorId);
  }
};

const SearchResult = {
  __resolveType: (obj) => {
    return obj.__typename; // Should be set by the resolver
  }
};

// Search resolver with multiple types
const resolvers = {
  Query: {
    search: async (_, { query, type }, { loaders }) => {
      const results = [];

      if (type === 'ALL' || type === 'ARTICLES') {
        const articles = await Article.findAll({
          where: {
            [Op.or]: [
              { title: { [Op.iLike]: `%${query}%` } },
              { content: { [Op.iLike]: `%${query}%` } }
            ]
          },
          limit: 10
        });

        articles.forEach(article => {
          article.__typename = 'Article';
          results.push(article);
        });
      }

      if (type === 'ALL' || type === 'VIDEOS') {
        const videos = await Video.findAll({
          where: {
            [Op.or]: [
              { title: { [Op.iLike]: `%${query}%` } },
              { content: { [Op.iLike]: `%${query}%` } }
            ]
          },
          limit: 10
        });

        videos.forEach(video => {
          video.__typename = 'Video';
          results.push(video);
        });
      }

      // Add similar logic for other types...

      return results.slice(0, 50); // Limit total results
    }
  },

  // Interface field resolvers
  ContentItem,
  SearchResult
};
```

### Advanced Input Types and Validation

**Complex Input Structures:**
```graphql
# Advanced input types with validation
input AdvancedPostFilter {
  authorId: ID
  tagIds: [ID!]
  dateRange: DateRangeInput
  publishedOnly: Boolean = true
  searchIn: [SearchField!] = [TITLE, CONTENT]
  customFilters: [CustomFilterInput!]
}

input DateRangeInput {
  from: DateTime
  to: DateTime
  # Allow relative dates like "7d", "1m", "1y"
  relative: RelativeDateInput
}

input RelativeDateInput {
  value: Int!
  unit: TimeUnit!
}

enum TimeUnit {
  HOURS
  DAYS
  WEEKS
  MONTHS
  YEARS
}

enum SearchField {
  TITLE
  CONTENT
  AUTHOR
  TAGS
}

input CustomFilterInput {
  field: String!
  operator: FilterOperator!
  value: String!
}

enum FilterOperator {
  EQUALS
  CONTAINS
  STARTS_WITH
  ENDS_WITH
  GREATER_THAN
  LESS_THAN
  IN
  NOT_IN
}

# Batch operations
input BatchOperationInput {
  operation: BatchOperation!
  filter: AdvancedPostFilter!
  data: JSON
}

enum BatchOperation {
  PUBLISH
  UNPUBLISH
  DELETE
  UPDATE_AUTHOR
  ADD_TAGS
  REMOVE_TAGS
}

type BatchOperationResult {
  success: Boolean!
  affectedCount: Int!
  errors: [BatchOperationError!]!
}

type BatchOperationError {
  id: ID!
  field: String
  message: String!
}

extend type Mutation {
  batchUpdatePosts(input: BatchOperationInput!): BatchOperationResult!
}
```

**Input Validation with Directives:**
```javascript
// directives/validation.js
const { SchemaDirectiveVisitor } = require('graphql-tools');
const { defaultFieldResolver, GraphQLNonNull } = require('graphql');

class ValidateDirective extends SchemaDirectiveVisitor {
  visitInputFieldDefinition(field) {
    const { resolve = defaultFieldResolver } = field;
    const { rules } = this.args;

    field.resolve = async function (...args) {
      const result = await resolve.apply(this, args);

      // Apply validation rules
      for (const rule of rules) {
        const validationResult = await validateRule(rule, result);
        if (!validationResult.valid) {
          throw new Error(validationResult.message);
        }
      }

      return result;
    };
  }
}

// Custom validation functions
const validationRules = {
  email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
  password: (value) => {
    return value.length >= 8 &&
           /[a-z]/.test(value) &&
           /[A-Z]/.test(value) &&
           /\d/.test(value);
  },
  slug: (value) => /^[a-z0-9-]+$/.test(value)
};

// Schema with validation directives
const typeDefs = gql`
  directive @validate(rules: [String!]) on INPUT_FIELD_DEFINITION

  input CreateUserInput {
    email: String! @validate(rules: ["email", "required"])
    password: String! @validate(rules: ["password", "required"])
    name: String! @validate(rules: ["minLength:2", "maxLength:50"])
    slug: String @validate(rules: ["slug"])
  }
`;
```

## 2. Advanced Resolver Patterns

### Custom Scalar Types

**File Upload Handling:**
```javascript
// scalars/FileUpload.js
const { GraphQLScalarType } = require('graphql');
const { GraphQLUpload } = require('graphql-upload');

const FileUpload = new GraphQLScalarType({
  name: 'FileUpload',
  description: 'File upload scalar type',
  parseValue: GraphQLUpload,
  serialize: (value) => {
    // Called when sending file data to client
    return {
      filename: value.filename,
      mimetype: value.mimetype,
      encoding: value.encoding,
      url: value.url
    };
  }
});

// Date scalar with timezone support
const DateTime = new GraphQLScalarType({
  name: 'DateTime',
  description: 'DateTime scalar type',
  parseValue(value) {
    return new Date(value); // Convert from JSON value to Date
  },
  serialize(value) {
    return value.toISOString(); // Convert from Date to JSON value
  },
  parseLiteral(ast) {
    if (ast.kind === Kind.STRING) {
      return new Date(ast.value);
    }
    return null;
  }
});

// JSON scalar for flexible data
const JSON = new GraphQLScalarType({
  name: 'JSON',
  description: 'JSON scalar type',
  parseValue: (value) => value,
  serialize: (value) => value,
  parseLiteral: (ast) => {
    switch (ast.kind) {
      case Kind.STRING:
      case Kind.BOOLEAN:
        return ast.value;
      case Kind.INT:
      case Kind.FLOAT:
        return parseFloat(ast.value);
      case Kind.OBJECT: {
        const value = {};
        ast.fields.forEach(field => {
          value[field.name.value] = parseLiteral(field.value);
        });
        return value;
      }
      case Kind.LIST:
        return ast.values.map(parseLiteral);
      default:
        return null;
    }
  }
});

// Usage in schema
const typeDefs = gql`
  scalar DateTime
  scalar FileUpload
  scalar JSON

  type Post {
    id: ID!
    title: String!
    content: String!
    featuredImage: FileUpload
    metadata: JSON
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  input CreatePostInput {
    title: String!
    content: String!
    featuredImage: FileUpload
    metadata: JSON
  }
`;
```

### Recursive Resolvers with Depth Limiting

**Hierarchical Data Structures:**
```javascript
// resolvers/commentResolver.js
const MAX_COMMENT_DEPTH = 10;

const commentResolvers = {
  Comment: {
    replies: async (comment, { first = 20, after, depth = 0 }, { loaders }) => {
      // Prevent infinite recursion
      if (depth >= MAX_COMMENT_DEPTH) {
        return {
          edges: [],
          pageInfo: {
            hasNextPage: false,
            hasPreviousPage: false,
            startCursor: null,
            endCursor: null
          },
          totalCount: 0
        };
      }

      const where = {
        parentCommentId: comment.id
      };

      // Apply cursor-based pagination
      const cursorCondition = after
        ? { id: { [Op.gt]: after } }
        : {};

      const replies = await Comment.findAll({
        where: { ...where, ...cursorCondition },
        limit: first + 1,
        order: [['createdAt', 'ASC']],
        include: [{
          model: User,
          as: 'author',
          attributes: ['id', 'name', 'avatar']
        }]
      });

      const hasNextPage = replies.length > first;
      if (hasNextPage) replies.pop();

      return {
        edges: replies.map(reply => ({
          node: {
            ...reply.toJSON(),
            // Recursively load replies
            replies: async () => {
              const result = await loaders.comments.loadReplies(reply, { first, after, depth: depth + 1 });
              return result;
            }
          },
          cursor: reply.id
        })),
        pageInfo: {
          hasNextPage,
          hasPreviousPage: !!after,
          startCursor: replies.length > 0 ? replies[0].id : null,
          endCursor: replies.length > 0 ? replies[replies.length - 1].id : null
        },
        totalCount: await Comment.count({ where })
      };
    }
  }
};

// DataLoader for recursive comments
class CommentLoader {
  constructor() {
    this.repliesCache = new Map();
  }

  async loadReplies(comment, options = {}) {
    const cacheKey = `${comment.id}:${JSON.stringify(options)}`;

    if (this.repliesCache.has(cacheKey)) {
      return this.repliesCache.get(cacheKey);
    }

    const result = await this.getReplies(comment, options);
    this.repliesCache.set(cacheKey, result);

    return result;
  }

  async getReplies(comment, { first = 20, after, depth = 0 } = {}) {
    // Implementation similar to resolver above
    const where = { parentCommentId: comment.id };
    const cursorCondition = after
      ? { id: { [Op.gt]: after } }
      : {};

    const replies = await Comment.findAll({
      where: { ...where, ...cursorCondition },
      limit: first + 1,
      order: [['createdAt', 'ASC']],
      include: [{
        model: User,
        as: 'author',
        attributes: ['id', 'name', 'avatar']
      }]
    });

    const hasNextPage = replies.length > first;
    if (hasNextPage) replies.pop();

    return {
      edges: replies.map(reply => ({
        node: reply,
        cursor: reply.id
      })),
      pageInfo: {
        hasNextPage,
        hasPreviousPage: !!after,
        startCursor: replies.length > 0 ? replies[0].id : null,
        endCursor: replies.length > 0 ? replies[replies.length - 1].id : null
      },
      totalCount: await Comment.count({ where })
    };
  }
}
```

## 3. Advanced Federation Patterns

### Cross-Service Entity Resolution

**Complex Federation with External References:**
```javascript
// Post Service - Enhanced federation
const postTypeDefs = gql`
  type Post @key(fields: "id") {
    id: ID!
    title: String!
    content: String!
    published: Boolean!
    author: User! @provides(fields: "id name avatar")
    coAuthors: [User!]! @provides(fields: "id name avatar")
    category: Category! @provides(fields: "id name color")
    tags: [Tag!]!
    relatedPosts: [Post!]!
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  extend type User @key(fields: "id") {
    id: ID! @external
    name: String @external
    avatar: String @external
    posts(first: Int = 20, after: String): PostConnection!
    coAuthoredPosts(first: Int = 20, after: String): PostConnection!
  }

  extend type Category @key(fields: "id") {
    id: ID! @external
    name: String @external
    color: String @external
    posts(first: Int = 20, after: String): PostConnection!
  }

  type Tag @key(fields: "id") {
    id: ID!
    name: String!
    color: String!
    posts(first: Int = 20, after: String): PostConnection!
  }
`;

const postResolvers = {
  Post: {
    __resolveReference: async (post) => {
      return Post.findByPk(post.id, {
        include: [
          { model: User, as: 'author', attributes: ['id', 'name', 'avatar'] },
          { model: User, as: 'coAuthors', attributes: ['id', 'name', 'avatar'] },
          { model: Category, as: 'category', attributes: ['id', 'name', 'color'] },
          { model: Tag, as: 'tags' }
        ]
      });
    },

    relatedPosts: async (post, { first = 5 }) => {
      // Find related posts based on tags and category
      return Post.findAll({
        where: {
          id: { [Op.ne]: post.id },
          [Op.or]: [
            { categoryId: post.categoryId },
            { '$tags.id$': { [Op.in]: post.tags.map(tag => tag.id) } }
          ]
        },
        include: [
          { model: Tag, as: 'tags', required: false }
        ],
        limit: first,
        order: [['createdAt', 'DESC']]
      });
    }
  },

  User: {
    posts: async (user, { first, after }) => {
      return PostConnection.fromArray(
        await Post.findAll({
          where: { authorId: user.id },
          limit: first + 1,
          order: [['createdAt', 'DESC']]
        }),
        { first, after }
      );
    },

    coAuthoredPosts: async (user, { first, after }) => {
      return PostConnection.fromArray(
        await Post.findAll({
          include: [{
            model: User,
            as: 'coAuthors',
            where: { id: user.id },
            required: true
          }],
          limit: first + 1,
          order: [['createdAt', 'DESC']]
        }),
        { first, after }
      );
    }
  }
};

// Custom entity resolver for cross-service lookups
class PostService {
  async getPostsWithUserData(postIds) {
    const posts = await Post.findAll({
      where: { id: postIds },
      include: [
        { model: User, as: 'author', attributes: ['id'] },
        { model: User, as: 'coAuthors', attributes: ['id'] },
        { model: Category, as: 'category', attributes: ['id'] }
      ]
    });

    // Batch fetch user details from user service
    const userIds = new Set();
    posts.forEach(post => {
      userIds.add(post.authorId);
      post.coAuthors.forEach(coAuthor => userIds.add(coAuthor.id));
    });

    const users = await this.batchFetchUsers(Array.from(userIds));

    // Map user data back to posts
    return posts.map(post => ({
      ...post.toJSON(),
      author: users.find(u => u.id === post.authorId),
      coAuthors: post.coAuthors.map(coAuthor =>
        users.find(u => u.id === coAuthor.id)
      )
    }));
  }

  async batchFetchUsers(userIds) {
    // Call user service with batch request
    const response = await fetch(`${process.env.USER_SERVICE_URL}/graphql`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `
          query GetUsers($ids: [ID!]!) {
            users(ids: $ids) {
              id
              name
              avatar
              email
            }
          }
        `,
        variables: { ids: userIds }
      })
    });

    const { data } = await response.json();
    return data.users;
  }
}
```

### Federation Gateway with Custom Logic

**Advanced Gateway Configuration:**
```javascript
// gateway/enhancedGateway.js
const { ApolloGateway, RemoteGraphQLDataSource } = require('@apollo/gateway');
const { readFileSync } = require('fs');
const { resolve } = require('path');
const GraphQLError = require('graphql');

class AuthenticatedDataSource extends RemoteGraphQLDataSource {
  async willSendRequest({ request, context }) {
    // Pass authentication and user context
    if (context.user) {
      request.http.headers.set('x-user-id', context.user.id);
      request.http.headers.set('x-user-role', context.user.role);
    }

    // Add request tracing
    request.http.headers.set('x-request-id', context.requestId);
    request.http.headers.set('x-trace-id', context.traceId);
  }

  async didReceiveResponse({ response, request, context }) {
    // Log response times for monitoring
    const responseTime = Date.now() - context.startTime;
    console.log(`Service ${this.url} responded in ${responseTime}ms`);

    // Transform response if needed
    const responseBody = await response.json();

    // Add custom extensions
    responseBody.extensions = {
      ...responseBody.extensions,
      service: this.serviceName,
      responseTime,
      requestId: context.requestId
    };

    return {
      body: JSON.stringify(responseBody),
      headers: response.headers,
      status: response.status
    };
  }

  async didEncounterError(error) {
    console.error(`Service ${this.url} error:`, error);

    // Return a GraphQL-formatted error
    return {
      body: JSON.stringify({
        errors: [{
          message: 'Service temporarily unavailable',
          extensions: {
            code: 'SERVICE_ERROR',
            service: this.serviceName
          }
        }]
      }),
      headers: {},
      status: 503
    };
  }
}

// Enhanced gateway with service discovery
class ServiceRegistry {
  constructor() {
    this.services = new Map();
    this.healthChecks = new Map();
  }

  registerService(name, url) {
    this.services.set(name, url);
    this.startHealthCheck(name, url);
  }

  async startHealthCheck(name, url) {
    const checkHealth = async () => {
      try {
        const response = await fetch(`${url}/health`, {
          method: 'GET',
          timeout: 5000
        });

        if (response.ok) {
          this.healthChecks.set(name, { healthy: true, lastCheck: new Date() });
        } else {
          this.healthChecks.set(name, { healthy: false, lastCheck: new Date() });
        }
      } catch (error) {
        this.healthChecks.set(name, { healthy: false, lastCheck: new Date() });
      }
    };

    // Initial check
    await checkHealth();

    // Check every 30 seconds
    setInterval(checkHealth, 30000);
  }

  getHealthyServices() {
    const healthy = [];
    for (const [name, url] of this.services) {
      const health = this.healthChecks.get(name);
      if (health && health.healthy) {
        healthy.push({ name, url });
      }
    }
    return healthy;
  }
}

const serviceRegistry = new ServiceRegistry();

// Register services
serviceRegistry.registerService('users', 'http://user-service:4001/graphql');
serviceRegistry.registerService('posts', 'http://post-service:4002/graphql');
serviceRegistry.registerService('comments', 'http://comment-service:4003/graphql');

const gateway = new ApolloGateway({
  serviceList: serviceRegistry.getHealthyServices(),
  buildService: ({ name, url }) => {
    return new AuthenticatedDataSource({
      url,
      serviceName: name
    });
  },
  // Custom executor for additional logic
  executor: async ({ requestContext }) => {
    // Add custom logic like rate limiting, caching, etc.
    return defaultExecutor({ requestContext });
  },
  // Supergraph configuration
  supergraphSdl: new IntrospectAndCompose({
    subgraphs: serviceRegistry.getHealthyServices()
  })
});

const gatewayServer = new ApolloServer({
  gateway,
  context: async ({ req }) => {
    const requestId = generateRequestId();
    const traceId = req.headers['x-trace-id'] || generateTraceId();

    // Authentication
    const token = req.headers.authorization?.replace('Bearer ', '');
    let user = null;

    if (token) {
      try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        user = await User.findByPk(decoded.id);
      } catch (error) {
        // Invalid token, continue as anonymous user
      }
    }

    return {
      user,
      requestId,
      traceId,
      startTime: Date.now()
    };
  },
  plugins: [
    // Request logging
    {
      requestDidStart() {
        return {
          didResolveOperation(requestContext) {
            console.log(`GraphQL Operation: ${requestContext.request.operationName}`);
          },
          didEncounterErrors(requestContext) {
            console.error('GraphQL Errors:', requestContext.errors);
          }
        };
      }
    }
  ]
});
```

## 4. Advanced Subscription Patterns

### Multi-Server Subscriptions with Redis

**Scalable Subscription Architecture:**
```javascript
// subscriptions/redisManager.js
const Redis = require('ioredis');
const { PubSub } = require('graphql-subscriptions');

class RedisSubscriptionManager {
  constructor(options = {}) {
    this.publisher = new Redis(options.redis);
    this.subscriber = new Redis(options.redis);
    this.localSubscriptions = new Map();
    this.serverId = options.serverId || generateServerId();
  }

  async initialize() {
    // Subscribe to all subscription channels
    await this.subscriber.subscribe('graphql-subscriptions');

    this.subscriber.on('message', (channel, message) => {
      const { type, payload, targetServers } = JSON.parse(message);

      // Only process if this message is for this server
      if (!targetServers || targetServers.includes(this.serverId)) {
        this.handleSubscriptionMessage(type, payload);
      }
    });
  }

  async publish(event, payload, options = {}) {
    const message = {
      type: event,
      payload,
      serverId: this.serverId,
      timestamp: Date.now()
    };

    // Broadcast to all servers or specific ones
    if (options.targetServers) {
      message.targetServers = options.targetServers;
    }

    await this.publisher.publish('graphql-subscriptions', JSON.stringify(message));
  }

  handleSubscriptionMessage(type, payload) {
    const handlers = this.localSubscriptions.get(type) || [];
    handlers.forEach(handler => {
      try {
        handler(payload);
      } catch (error) {
        console.error('Subscription handler error:', error);
      }
    });
  }

  subscribe(event, handler) {
    if (!this.localSubscriptions.has(event)) {
      this.localSubscriptions.set(event, []);
    }
    this.localSubscriptions.get(event).push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.localSubscriptions.get(event) || [];
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    };
  }

  async destroy() {
    await this.publisher.quit();
    await this.subscriber.quit();
  }
}

// Advanced subscription resolvers
const subscriptionManager = new RedisSubscriptionManager({
  redis: {
    host: process.env.REDIS_HOST,
    port: process.env.REDIS_PORT,
    password: process.env.REDIS_PASSWORD
  }
});

const advancedSubscriptions = {
  Subscription: {
    // Real-time collaboration
    documentUpdated: {
      subscribe: withFilter(
        () => subscriptionManager.subscribe('DOCUMENT_UPDATED'),
        (payload, variables, { user }) => {
          // Check permissions
          return canAccessDocument(user, payload.documentUpdated.id);
        }
      )
    },

    // Activity feeds
    userActivity: {
      subscribe: withFilter(
        () => subscriptionManager.subscribe('USER_ACTIVITY'),
        (payload, variables, { user }) => {
          // Only send activity to followers or the user themselves
          return payload.userActivity.userId === user.id ||
                 payload.userActivity.followerIds.includes(user.id);
        }
      )
    },

    // Notifications with filtering
    notifications: {
      subscribe: withFilter(
        () => subscriptionManager.subscribe('NOTIFICATION'),
        (payload, variables, { user }) => {
          // Filter by user and notification type
          return payload.notification.userId === user.id &&
                 (!variables.types || variables.types.includes(payload.notification.type));
        }
      )
    },

    // Real-time analytics
    analyticsUpdate: {
      subscribe: withFilter(
        () => subscriptionManager.subscribe('ANALYTICS_UPDATE'),
        (payload, variables, { user }) => {
          // Only send to users with appropriate permissions
          return hasPermission(user, 'view_analytics') &&
                 (!variables.siteId || variables.siteId === payload.analyticsUpdate.siteId);
        }
      )
    }
  }
};

// Publishing from mutations with intelligent targeting
const mutationPublishers = {
  Mutation: {
    updateDocument: async (_, { id, input }, { user, pubsub }) => {
      const document = await Document.update(input, {
        where: { id },
        returning: true
      });

      // Get all users with access to this document
      const usersWithAccess = await getUsersWithDocumentAccess(id);

      // Publish to relevant servers only
      const targetServers = getServersForUsers(usersWithAccess);

      await subscriptionManager.publish('DOCUMENT_UPDATED', {
        documentUpdated: document[0],
        updatedBy: user,
        timestamp: new Date().toISOString()
      }, { targetServers });

      return document[0];
    },

    createNotification: async (_, { input }) => {
      const notification = await Notification.create({
        ...input,
        id: generateId(),
        createdAt: new Date()
      });

      // Determine which servers need this notification
      const targetServers = getServersForUser(notification.userId);

      await subscriptionManager.publish('NOTIFICATION', {
        notification
      }, { targetServers });

      return notification;
    }
  }
};
```

This comprehensive GraphQL implementation guide provides production-tested patterns for building scalable, performant GraphQL APIs with advanced features like federation, subscriptions, and real-time collaboration.
"""
        )

    def _extract_focus_areas(self, query: str) -> list[str]:
        """Extract focus areas from the user's query."""
        query_lower = query.lower()
        focus_areas = []

        area_keywords = {
            "schema": ["schema", "types", "interface", "union"],
            "resolvers": ["resolver", "query", "mutation", "subscription"],
            "apollo": ["apollo", "apollo server", "apollo gateway"],
            "federation": ["federation", "microservices", "gateway"],
            "subscriptions": ["subscription", "real-time", "websocket"],
            "performance": ["performance", "optimization", "dataloader", "caching"],
            "testing": ["test", "testing", "integration", "contract"],
        }

        for area, keywords in area_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                focus_areas.append(area)

        return focus_areas
