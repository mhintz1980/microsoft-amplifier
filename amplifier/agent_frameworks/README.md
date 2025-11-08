# Multi-Framework Agent Integration System

A comprehensive framework-agnostic integration system for AI agents, providing seamless multi-framework support, advanced data transformation, and specialized optimizations for mechanical engineering applications.

## Overview

This package embodies the amplifier philosophy of ruthless simplicity and modular "bricks & studs" design, enabling:

- **Multi-framework integration** with LangChain, OpenAI SDK, AutoGen, and CrewAI
- **Framework-agnostic interfaces** for universal agent management
- **Advanced data transformation** for mechanical engineering domains
- **Cross-framework interoperability** and migration capabilities
- **Agent Lightning training integration** with specialized optimizations

## Key Components

### 1. Multi-Framework Integration (`multi_framework_integration.py`)

Provides unified adapters for major agent frameworks:

```python
from amplifier.agent_frameworks import (
    FrameworkType, AgentConfig, MultiFrameworkOrchestrator,
    create_mechanical_engineering_config
)

# Create multi-framework system
frameworks = [FrameworkType.LANGCHAIN, FrameworkType.AUTOGEN, FrameworkType.CREWAI]
orchestrator = await create_multi_framework_system(frameworks)

# Execute across all frameworks
results = await orchestrator.execute_all_frameworks("Analyze CAD design for manufacturability")
```

### 2. Advanced Data Transformation (`advanced_adapters.py`)

Specialized adapters for mechanical engineering data:

```python
from amplifier.agent_frameworks import (
    DataFormat, EngineeringDomain, EngineeringData,
    create_mechanical_engineering_pipeline
)

# Create engineering data
cad_data = EngineeringData(
    content=cad_file_content,
    format=DataFormat.CAD_STEP,
    domain=EngineeringDomain.MECHANICAL
)

# Process with specialized pipeline
pipeline = create_mechanical_engineering_pipeline()
features = await pipeline.process_engineering_data([cad_data])
```

### 3. Framework-Agnostic Layer (`framework_agnostic_layer.py`)

Universal interfaces and task scheduling:

```python
from amplifier.agent_frameworks import (
    TaskType, TaskDefinition, UniversalAgentManager,
    create_mechanical_engineering_tasks
)

# Create universal agent system
manager = await create_universal_system(frameworks, configs)

# Execute tasks regardless of framework
tasks = create_mechanical_engineering_tasks()
results = await manager.execute_workflow(tasks)
```

### 4. Framework Optimizations (`framework_optimizations.py`)

Training integration and performance optimization:

```python
from amplifier.agent_frameworks import (
    OptimizationStrategy, create_mechanical_engineering_optimization
)

# Create optimization configuration
config = create_mechanical_engineering_optimization(
    strategy=OptimizationStrategy.REINFORCEMENT_LEARNING,
    mode=TrainingMode.PERFORMANCE
)

# Optimize all frameworks
results = await optimize_all_frameworks_for_mechanical_engineering(
    training_data, OptimizationStrategy.REINFORCEMENT_LEARNING
)
```

### 5. Interoperability Layer (`interoperability_layer.py`)

Cross-framework migration and hybrid architectures:

```python
from amplifier.agent_frameworks import (
    create_mechanical_engineering_hybrid_architecture,
    HybridOrchestrator, MigrationAnalyzer
)

# Create hybrid architecture
architecture = create_mechanical_engineering_hybrid_architecture()
orchestrator = HybridOrchestrator()
orchestrator.create_hybrid_architecture("mech_hybrid", architecture)

# Execute with hybrid architecture
result = await orchestrator.execute_with_architecture("mech_hybrid", task)
```

## Quick Start

### Installation

Install the required framework dependencies:

```bash
# Core dependencies (always required)
pip install asyncio dataclasses typing pathlib

# Framework dependencies (install as needed)
pip install langchain          # For LangChain integration
pip install openai             # For OpenAI SDK integration
pip install pyautogen          # For AutoGen integration
pip install crewai             # For CrewAI integration
```

### Basic Usage

```python
import asyncio
from amplifier.agent_frameworks import quick_mechanical_engineering_agent

async def main():
    # Create a simple mechanical engineering agent
    agent_manager = await quick_mechanical_engineering_agent("langchain")

    # Execute mechanical engineering task
    task = TaskDefinition(
        task_type=TaskType.DESIGN_REVIEW,
        description="Review bracket design for CNC manufacturing",
        requirements=["Check tolerances", "Assess material selection"]
    )

    result = await agent_manager.scheduler.execute_task(task)
    print(f"Analysis result: {result.output}")

asyncio.run(main())
```

### Mechanical Engineering Workflows

```python
from amplifier.agent_frameworks.mechanical_engineering_examples import (
    MechanicalEngineeringWorkflows, CADAnalysisRequest
)

async def cad_analysis_example():
    workflows = MechanicalEngineeringWorkflows()
    await workflows.initialize_frameworks(["langchain", "autogen"])

    request = CADAnalysisRequest(
        cad_file_path="designs/engine_block.step",
        analysis_type="manufacturability",
        requirements=["Check CNC feasibility", "Assess material requirements"]
    )

    result = await workflows.cad_analysis_workflow(request)
    return result
```

## Architecture

The system follows the amplifier philosophy with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
│  (mechanical_engineering_examples.py, custom workflows)    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Framework-Agnostic Layer                     │
│  (UniversalAgentInterface, TaskScheduler, Training)        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│               Multi-Framework Integration                    │
│  (LangChain, OpenAI SDK, AutoGen, CrewAI adapters)        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                  Advanced Adapters                           │
│  (CAD, Technical Documents, UI Components, Data Transform)  │
└─────────────────────────────────────────────────────────────┘
```

## Design Philosophy

### Bricks & Studs Architecture

Each component is a self-contained "brick" with clear interfaces ("studs"):

- **Independent Modules**: Each framework adapter can be used standalone
- **Clear Contracts**: Universal interfaces define exactly what each component provides
- **Composable**: Components can be combined in various ways
- **Replaceable**: Any component can be swapped without affecting others

### Ruthless Simplicity

- **Direct Integration**: No unnecessary abstraction layers
- **Framework-Native**: Use each framework as intended
- **Minimal Dependencies**: Only essential dependencies required
- **Clear APIs**: Simple, intuitive interfaces

### Mechanical Engineering Domain Expertise

- **Specialized Adapters**: CAD files, technical documents, UI components
- **Domain Knowledge**: Engineering standards, safety requirements, manufacturing processes
- **Practical Workflows**: Real-world mechanical engineering tasks
- **Quality Focus**: Emphasis on accuracy, safety, and reliability

## Framework Support

### LangChain Integration

```python
from amplifier.agent_frameworks import LangChainAdapter

adapter = LangChainAdapter(config)
await adapter.initialize()
result = await adapter.execute("Analyze mechanical design for manufacturability")
```

### OpenAI SDK Integration

```python
from amplifier.agent_frameworks import OpenAIAdapter

adapter = OpenAIAdapter(config)
await adapter.initialize()
result = await adapter.execute("Review safety compliance for pressure vessel")
```

### AutoGen Integration

```python
from amplifier.agent_frameworks import AutoGenAdapter

adapter = AutoGenAdapter(config)
await adapter.initialize()
result = await adapter.execute("Coordinate multi-agent mechanical design review")
```

### CrewAI Integration

```python
from amplifier.agent_frameworks import CrewAIAdapter

adapter = CrewAIAdapter(config)
await adapter.initialize()
result = await adapter.execute("Execute mechanical engineering crew workflow")
```

## Training and Optimization

### Agent Lightning Integration

```python
from amplifier.agent_frameworks import TrainingDataPipeline, OptimizationManager

# Create training pipeline
pipeline = create_mechanical_engineering_pipeline()
training_data = await pipeline.process_engineering_data(engineering_data_list)

# Optimize frameworks
manager = OptimizationManager()
results = await manager.optimize_frameworks(
    ["langchain", "autogen", "crewai"],
    config,
    training_data
)
```

### Performance Monitoring

```python
# Monitor framework performance
performance = manager.compare_frameworks()
print(f"Best performing framework: {performance['best_framework']}")

# Track execution statistics
stats = orchestrator.get_training_data()
print(f"Total training samples: {len(stats)}")
```

## Migration and Interoperability

### Framework Migration

```python
from amplifier.agent_frameworks import MigrationAnalyzer, FrameworkMigrator

# Analyze migration feasibility
analyzer = MigrationAnalyzer()
plan = analyzer.analyze_migration_feasibility(agent_profile, "crewai")

# Execute migration
migrator = FrameworkMigrator(analyzer)
success, migrated_profile = await migrator.migrate_agent(agent_profile, "crewai")
```

### Hybrid Architectures

```python
from amplifier.agent_frameworks import create_mechanical_engineering_hybrid_architecture

# Create specialized hybrid architecture
architecture = create_mechanical_engineering_hybrid_architecture()

# Execute with different frameworks for different tasks
result = await orchestrator.execute_with_architecture("mech_hybrid", {
    "type": "design_analysis",
    "input": "Analyze complex mechanical assembly"
})
```

## Examples and Use Cases

### 1. CAD Analysis Workflow

```python
request = CADAnalysisRequest(
    cad_file_path="designs/engine_block.step",
    analysis_type="manufacturability",
    requirements=["Check CNC machining", "Assess material needs"],
    constraints=["Cost < $500", "Tolerance ±0.1mm"]
)

result = await workflows.cad_analysis_workflow(request)
```

### 2. Safety Review System

```python
request = SafetyReviewRequest(
    design_description="Pressure vessel for compressed air",
    safety_standards=["ASME", "OSHA"],
    risk_factors=["High pressure", "Cyclic loading"]
)

result = await workflows.safety_review_workflow(request)
```

### 3. Manufacturing Assessment

```python
request = ManufacturingAssessmentRequest(
    part_specifications={"material": "Aluminum 6061", "tolerance": ±0.1},
    available_processes=["CNC", "3D_printing"],
    volume_requirements={"prototype": 10, "production": 10000}
)

result = await workflows.manufacturing_assessment_workflow(request)
```

## Performance Characteristics

### Framework Comparison

| Framework | Strengths | Best For | Performance |
|-----------|-----------|-----------|-------------|
| LangChain | Rich ecosystem, tool integration | Complex tool workflows | High accuracy, medium latency |
| OpenAI SDK | Direct API access, fastest | Simple tasks, high throughput | Lowest latency, good accuracy |
| AutoGen | Multi-agent coordination | Collaborative problem solving | High quality, higher latency |
| CrewAI | Role-based workflows | Specialized domain tasks | Highest quality, highest latency |

### Optimization Strategies

- **Reinforcement Learning**: Optimize agent decision-making
- **Behavior Cloning**: Learn from expert demonstrations
- **Reward Modeling**: Improve response quality
- **Curriculum Learning**: Progressive difficulty training
- **Multi-Objective**: Balance accuracy, efficiency, safety

## Configuration

### Environment Setup

```python
# Framework configurations
langchain_config = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.1,
    "agent_type": "chat-conversational-react-description",
    "tools": ["cad_analyzer", "safety_checker"]
}

autogen_config = {
    "model": "gpt-3.5-turbo",
    "max_round": 10,
    "human_input_mode": "NEVER",
    "agents": ["mechanical_engineer", "safety_specialist"]
}
```

### Custom Adapters

```python
class CustomMechanicalAdapter(FrameworkAdapter):
    async def execute(self, input_message: str, **kwargs):
        # Custom mechanical engineering logic
        return AgentInteraction(
            agent_id="custom_mech",
            input_message=input_message,
            output_message="Custom mechanical analysis result"
        )
```

## Best Practices

### 1. Framework Selection

- **LangChain**: Use when you need complex tool chains and rich ecosystem
- **OpenAI SDK**: Use for simple tasks requiring maximum speed
- **AutoGen**: Use for multi-agent collaboration and complex reasoning
- **CrewAI**: Use for specialized domain workflows with clear roles

### 2. Performance Optimization

- Choose the right framework for your specific use case
- Use hybrid architectures for complex workflows
- Monitor performance and adjust configurations accordingly
- Consider framework migration if requirements change

### 3. Mechanical Engineering Integration

- Leverage domain-specific adapters for CAD and technical data
- Use specialized workflows for safety and manufacturing
- Incorporate engineering standards and best practices
- Maintain focus on accuracy, safety, and reliability

### 4. Training and Optimization

- Start with behavior cloning for stable baseline
- Use reinforcement learning for performance improvement
- Monitor training metrics and convergence
- Validate with real mechanical engineering scenarios

## Troubleshooting

### Common Issues

1. **Framework Import Errors**: Install missing framework dependencies
2. **Performance Issues**: Check framework selection and configuration
3. **Migration Failures**: Verify compatibility and configuration requirements
4. **Training Problems**: Ensure adequate training data and appropriate hyperparameters

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
from amplifier.utils.logger import get_logger
logger = get_logger(__name__)
logger.setLevel("DEBUG")
```

## Contributing

This package follows the amplifier philosophy:

1. **Keep it Simple**: Avoid unnecessary complexity
2. **Modular Design**: Independent, composable components
3. **Clear Interfaces**: Well-defined contracts between modules
4. **Domain Focus**: Mechanical engineering expertise
5. **Performance**: Optimize for real-world usage

When contributing:

- Follow the existing code style and patterns
- Add comprehensive tests for new functionality
- Update documentation for any API changes
- Ensure backward compatibility when possible
- Focus on practical mechanical engineering use cases

## License

This package is part of the amplifier project and follows the same license terms.