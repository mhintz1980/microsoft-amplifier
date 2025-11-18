# Overview

> AI-powered coding with GLM-4.6 in Claude Code, Cline, OpenCode, Roo Code and more. Plans start at $3/month to help you code faster, smarter, and more reliably.

The GLM Coding Plan is a subscription package designed specifically for AI-powered coding. GLM-4.6 is now available in top coding tools, starting at just \$3/month — powering Claude Code, Cline, OpenCode, Roo Code and more. The package is designed to make coding faster, smarter, and more reliable.

<Tip>
  [Subscribe](https://z.ai/subscribe?utm_source=z.ai\&utm_medium=link\&utm_term=glm-devpack\&utm_campaign=Platform_Ops&_channel_track_key=jFgqJREK) now.

  Subscribed users can refer to [Quick Start](/devpack/quick-start) to begin your efficient coding journey.

  Exclusive to PRO and higher plans: [Vision Understanding MCP Server](/devpack/mcp/vision-mcp-server) / [Web Search MCP Server](/devpack/mcp/search-mcp-server)
</Tip>

## <Icon icon="list" iconType="solid" color="#ffffff" size={36} />   Usage

The plan can be applied to coding tools such as Claude Code, Cline, and OpenCode, covering a wide range of development scenarios:

<AccordionGroup>
  <Accordion title="Natural Language Programming">
    Describe requirements in plain language to automatically generate plans, write code, debug issues, and ensure smooth execution.
  </Accordion>

  <Accordion title="Intelligent Code Completion">
    Get real-time, context-aware completion suggestions that reduce manual typing and significantly improve productivity.
  </Accordion>

  <Accordion title="Code Debugging & Repair">
    Input error messages or descriptions to automatically analyze your codebase, locate problems, and provide fixes.
  </Accordion>

  <Accordion title="Codebase Q&A">
    Ask questions about your team’s codebase anytime, maintain global understanding, and receive precise answers with external data integration.
  </Accordion>

  <Accordion title="Automated Task Handling">
    Automatically fix lint issues, resolve merge conflicts, and generate release notes—allowing developers to stay focused on core logic.
  </Accordion>
</AccordionGroup>

## <Icon icon="stars" iconType="solid" color="#ffffff" size={36} />   Advantages

* **Access to a Top-Tier Coding Model:** GLM-4.6 delivers state-of-the-art performance in reasoning, coding, and agent capabilities—leading in tool use and complex task execution.
* **Works with Multiple Coding Tools:** Beyond Claude Code, it also supports Cline, OpenCode, and other mainstream coding tools, giving you flexibility across development workflows.
* **Faster, More Reliable Response:** Generate over 55 tokens per second for real-time interaction. No network restrictions, no account bans—just smooth, uninterrupted coding.
* **Generous Usage at a Fair Price:** Get higher call limits than standard plans. Starting at just 3 USD per month, with Pro plans from 15 USD per month designed for high-frequency, complex projects.
* **Expanded Capabilities:** The Pro and Max plans support built-in Vision Understanding, Web Search MCP, supporting multimodal analysis and real-time information retrieval.

## <Icon icon="gauge-max" iconType="solid" color="#ffffff" size={36} />   Usage Limits

### Usage Instruction

* **Lite Plan**: Up to \~120 prompts every 5 hours — about 3× the usage quota of the Claude Pro plan.
* **Pro Plan**: Up to \~600 prompts every 5 hours — about 3× the usage quota of the Claude Max (5x) plan.
* **Max Plan**: Up to \~2400 prompts every 5 hours — about 3× the usage quota of the Claude Max (20x) plan.

In terms of token consumption, each prompt typically allows 15–20 model calls, giving a total monthly allowance of tens of billions of tokens — all at only \~1% of standard API pricing, making it extremely cost-effective.

<Tip>
  The above figures are estimates. Actual usage may vary depending on project complexity, codebase size, and whether auto-accept features are enabled.
</Tip>

### Supported Tools

* The plan can only be used within specific coding tools, including Claude Code, Roo Code, Kilo Code, Cline, OpenCode, Crush, Goose and more.
* Once subscribed, GLM-4.6 is automatically available in the supported tools using your plan’s quota—no additional configuration required. If the quota is exhausted, it will automatically reset at the start of the next 5-hour cycle. The system will not consume other resource packs or account balance. Users with a Coding Plan can only use the plan’s quota in supported tools and cannot call the model separately via API.
* API calls are billed separately and do not use the Coding Plan quota. Please refer to the API pricing for details.

### How to Switch Models

Mapping between Claude Code internal model environment variables and GLM models, with the default configuration as follows:

* `ANTHROPIC_DEFAULT_OPUS_MODEL`: `GLM-4.6`
* `ANTHROPIC_DEFAULT_SONNET_MODEL`: `GLM-4.6`
* `ANTHROPIC_DEFAULT_HAIKU_MODEL`: `GLM-4.5-Air`

If adjustments are needed, you can directly modify the configuration file (for example, `~/.claude/settings.json` in Claude Code) to switch to GLM-4.5 or other models.

## <Icon icon="list-check" iconType="solid" color="#ffffff" size={36} />   How to Integrate with Coding Tools

<CardGroup cols={3}>
  <Card title="Claude Code" color="#ffffff" href="https://docs.z.ai/devpack/tool/claude" />

  <Card title="Roo Code" color="#ffffff" href="https://docs.z.ai/devpack/tool/roo" />

  <Card title="Kilo Code" color="#ffffff" href="https://docs.z.ai/devpack/tool/kilo" />

  <Card title="Cline" color="#ffffff" href="https://docs.z.ai/devpack/tool/cline" />

  <Card title="OpenCode" color="#ffffff" href="https://docs.z.ai/devpack/tool/opencode" />

  <Card title="Crush" color="#ffffff" href="https://docs.z.ai/devpack/tool/crush" />

  <Card title="Goose" color="#ffffff" href="https://docs.z.ai/devpack/tool/goose" />

  <Card title="Other Tools" color="#ffffff" href="https://docs.z.ai/devpack/tool/others" />
</CardGroup>

## <Icon icon="dollar-sign" iconType="solid" color="#ffffff" size={36} />   Billing and Invoices

You can manage your subscription, view billing details, and cancel the subscription as follows:

1. Log in to the Z.ai [API Platform](https://z.ai/subscribe?utm_source=zai\&utm_medium=index\&utm_term=glm-coding-plan\&utm_campaign=Platform_Ops&_channel_track_key=6lShUDnv).
2. Click your profile icon in the top-right corner → [Payment Method](https://z.ai/manage-apikey/billing).
3. In the left menu, select [Subscription](https://z.ai/manage-apikey/subscription).
4. To view billing history, go to Billing → [Billing History](https://z.ai/manage-apikey/billing).

<Steps>
  <Step title="How do I request a refund?" icon="stars">
    Please note that subscriptions are non-refundable once purchased. Even if you haven’t used your full plan, the fees cannot be returned. We recommend choosing a subscription plan and billing cycle that best fits your usage needs.
  </Step>
</Steps>

## <Icon icon="shield-quartered" iconType="solid" color="#ffffff" size={36} />   Data Privacy

* All [Z.ai](http://z.ai/) services are based in Singapore.
* We do not store any of the content you provide or generate while using our Services. This includes any text prompts, images, or other data you input.
* See [Privacy Policy](https://docs.z.ai/legal-agreement/privacy-policy) for furture details.
