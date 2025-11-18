#!/usr/bin/env python3
"""
Demonstration of progressive context compression system

Shows how to use the compression system to manage context efficiently.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from progressive_compression import CompressionLevel
from progressive_compression import ContextCompressor
from progressive_compression import estimate_usage_percentage


def create_sample_context():
    """Create a sample context for demonstration"""
    return """
# Project Analysis Report

## Overview
This document contains analysis of the current project state and recommendations for improvements.

## Critical Issues Found

### ERROR: Database Connection Failure
The main database connection is failing intermittently. This is blocking all user operations.

**Error Details:**
- Connection timeout after 30 seconds
- Error code: DB_CONN_TIMEOUT
- Impact: Users cannot access their data
- Priority: CRITICAL

**Root Cause Analysis:**
The connection pool configuration is incorrect. The max_connections setting is too low for current load.

### Security Vulnerability Detected
Found potential SQL injection vulnerability in user authentication module.

**Vulnerability Details:**
- Location: auth/user_login.py line 45
- Severity: HIGH
- Impact: Potential data breach
- Action Required: Immediate fix needed

## Implementation Details

### Main Processing Function
```python
def process_user_request(user_id, request_data):
    '''Main entry point for processing user requests'''
    # Validate input
    if not validate_user_data(request_data):
        raise ValidationError("Invalid user data")

    # Process request
    result = execute_business_logic(user_id, request_data)
    return result
```

### Configuration Management
The system uses environment-based configuration management:

```python
class Config:
    DATABASE_URL = os.getenv('DATABASE_URL')
    MAX_CONNECTIONS = int(os.getenv('MAX_CONNECTIONS', '10'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

## Test Results

### Unit Test Results
- Total tests: 156
- Passed: 148
- Failed: 8
- Coverage: 87%

### Integration Test Results
- API endpoints tested: 23
- Success rate: 95.6%
- Average response time: 245ms

## Debug Information

### Debug Trace for User Login
[DEBUG] Starting user login process
[DEBUG] Validating user credentials
[DEBUG] Checking database connection
[DEBUG] Querying user table
[DEBUG] Verifying password hash
[DEBUG] Generating session token
[DEBUG] Login completed successfully

### Background Task Logs
[INFO] Background task scheduler started
[INFO] Processing email queue
[INFO] Sending 23 pending emails
[INFO] Email queue processing completed

## Success Stories

### Performance Improvement Achieved
SUCCESS: Database optimization reduced query time by 67%

After implementing connection pooling and query optimization:
- Average query time: 45ms (was 135ms)
- Concurrent users supported: 500+ (was 200)
- Database CPU usage: 35% (was 78%)

### User Feedback
User satisfaction score improved from 3.2 to 4.7 out of 5 after recent UI improvements.

## Recommendations

1. Fix database connection configuration immediately
2. Address SQL injection vulnerability within 24 hours
3. Implement automated security scanning
4. Add more comprehensive integration tests
5. Monitor performance metrics continuously

## Next Steps

1. Schedule emergency maintenance window for database fixes
2. Roll out security patch to production
3. Set up monitoring and alerting
4. Plan performance optimization phase 2

## Conclusion

The system is functional but has critical issues that need immediate attention.
The security vulnerability and database connection problems are blocking normal operations.

Priority order for fixes:
1. Database connection (CRITICAL)
2. SQL injection security fix (HIGH)
3. Performance monitoring (MEDIUM)
4. Additional testing (LOW)
    """.strip()


async def demonstrate_compression():
    """Demonstrate the compression system"""
    print("🗜️  Progressive Context Compression Demo")
    print("=" * 50)

    # Create sample context
    original_content = create_sample_context()
    original_tokens = len(original_content.split())
    print(f"Original context: {original_tokens} words")
    print(f"Estimated tokens: {original_tokens * 1.3:.0f}")
    print()

    # Show usage percentage
    usage = estimate_usage_percentage(original_content)
    print(f"Context usage: {usage:.1%}")
    print()

    # Test different compression levels
    compressor = ContextCompressor()

    levels_to_test = [
        CompressionLevel.FULL,
        CompressionLevel.SUMMARY,
        CompressionLevel.ESSENTIAL,
        CompressionLevel.METADATA,
    ]

    results = {}

    for level in levels_to_test:
        print(f"Testing {level.value} compression...")
        result = await compressor.compress(original_content, level)
        results[level] = result

        compressed_words = len(result.compressed_content.split())
        reduction = (1 - result.compression_ratio) * 100

        print(f"  Original tokens: {result.original_tokens:.0f}")
        print(f"  Compressed tokens: {result.compressed_tokens:.0f}")
        print(f"  Reduction: {reduction:.1f}%")
        print(f"  Content length: {len(result.compressed_content)} chars")
        print()

    # Show actual compressed content
    print("📋 Compressed Content Samples")
    print("=" * 50)

    for level, result in results.items():
        print(f"\n{level.value} Level:")
        print("-" * 30)

        # Show first 200 characters
        preview = (
            result.compressed_content[:200] + "..."
            if len(result.compressed_content) > 200
            else result.compressed_content
        )
        print(preview)
        print()

    # Show compression statistics
    print("📊 Compression Statistics")
    print("=" * 50)
    stats = compressor.get_compression_stats()

    for key, value in stats.items():
        if key != "compression_levels_used":
            print(f"{key}: {value}")

    print(f"Compression levels used: {stats.get('compression_levels_used', {})}")
    print()

    # Demonstrate automatic level selection
    print("🎯 Automatic Level Selection")
    print("=" * 50)

    short_content = "This is a short message."
    auto_result = await compressor.compress(short_content)

    print(f"Short content ({len(short_content.split())} words): {auto_result.level.value}")
    print(f"Reason: {auto_result.metadata.get('reason', 'automatic')}")
    print()

    # Demonstrate importance scoring
    print("🎯 Semantic Importance Scoring")
    print("=" * 50)

    chunks = compressor.chunk_context(original_content)

    # Show top 5 most important chunks
    sorted_chunks = sorted(chunks, key=lambda x: x.importance_score, reverse=True)[:5]

    for i, chunk in enumerate(sorted_chunks, 1):
        preview = chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content
        print(f"{i}. Score: {chunk.importance_score:.2f} | Type: {chunk.chunk_type}")
        print(f"   {preview}")
        print()

    print("✅ Demo completed!")


if __name__ == "__main__":
    asyncio.run(demonstrate_compression())
