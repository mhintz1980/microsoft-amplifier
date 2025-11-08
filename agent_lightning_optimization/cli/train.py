#!/usr/bin/env python3
"""
CLI Training Interface for Agent Lightning Optimization.

This module provides comprehensive command-line interfaces for training
mechanical engineering agents with advanced RL optimization.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import click
import numpy as np
from rich.console import Console
from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.progress import TimeElapsedColumn
from rich.table import Table

from ..algorithm.apo import APOConfig
from ..algorithm.apo import APOptimizer
from ..algorithm.apo import MechanicalEngineeringTemplateGenerator
from ..store.sqlite_store import LightningStoreManager
from ..store.sqlite_store import TrainingMetrics
from ..training.curriculum import CurriculumManager
from ..training.curriculum import CurriculumStrategy
from ..training.gpu_accelerator import GPUManager
from ..training.gpu_accelerator import MultiProcessTrainer
from ..utils.logger import get_logger

logger = get_logger(__name__)
console = Console()


@click.group()
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file")
@click.option("--data-dir", "-d", type=click.Path(exists=True), help="Training data directory")
@click.option("--model-dir", "-m", type=click.Path(), help="Model output directory")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.pass_context
def cli(ctx, config, data_dir, model_dir, verbose):
    """Agent Lightning Training CLI for Mechanical Engineering Agents."""
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["data_dir"] = Path(data_dir) if data_dir else None
    ctx.obj["model_dir"] = Path(model_dir) if model_dir else Path("models")
    ctx.obj["verbose"] = verbose

    # Create model directory if it doesn't exist
    ctx.obj["model_dir"].mkdir(parents=True, exist_ok=True)


@cli.command()
@click.option(
    "--agent-type",
    "-t",
    type=click.Choice(["cad_analysis", "rag_quality", "ui_generation"]),
    required=True,
    help="Type of agent to train",
)
@click.option(
    "--strategy",
    "-s",
    type=click.Choice(["linear", "exponential", "adaptive", "self_paced"]),
    default="adaptive",
    help="Curriculum learning strategy",
)
@click.option("--epochs", "-e", default=100, help="Number of training epochs")
@click.option("--batch-size", "-b", default=32, help="Batch size for training")
@click.option("--learning-rate", "-lr", default=0.001, help="Learning rate")
@click.option("--gpu", "-g", is_flag=True, help="Use GPU acceleration if available")
@click.option("--multi-process", "-mp", is_flag=True, help="Use multi-process training")
@click.option("--curriculum", is_flag=True, help="Use curriculum learning")
@click.pass_context
def train(ctx, agent_type, strategy, epochs, batch_size, learning_rate, gpu, multi_process, curriculum):
    """Train a mechanical engineering agent."""
    console.print(f"[bold green]Training {agent_type} agent[/bold green]")

    # Initialize components
    store_manager = LightningStoreManager(ctx.obj["model_dir"] / "store")
    store = store_manager.get_store("training")
    asyncio.run(store.initialize())

    # GPU setup
    gpu_manager = GPUManager()
    gpu_manager.initialize()

    if gpu and gpu_manager.gpu_count == 0:
        console.print("[yellow]Warning: GPU requested but none available. Using CPU.[/yellow]")
        gpu = False

    # Training configuration
    config = {
        "agent_type": agent_type,
        "epochs": epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "use_gpu": gpu,
        "multi_process": multi_process,
        "curriculum_learning": curriculum,
        "strategy": strategy,
    }

    # Load data
    data_dir = ctx.obj["data_dir"] or Path("data") / agent_type
    if not data_dir.exists():
        console.print(f"[red]Error: Data directory {data_dir} does not exist[/red]")
        sys.exit(1)

    console.print(f"[blue]Loading training data from {data_dir}[/blue]")
    training_data, validation_data = load_training_data(data_dir)

    if not training_data:
        console.print("[red]Error: No training data found[/red]")
        sys.exit(1)

    console.print(
        f"[green]Found {len(training_data)} training samples and {len(validation_data)} validation samples[/green]"
    )

    # Create training session
    session_id = f"{agent_type}_{int(time.time())}"
    asyncio.run(
        store.create_training_session(
            session_id=session_id, agent_name=agent_type, algorithm="APO" if curriculum else "Baseline", config=config
        )
    )

    console.print(f"[blue]Started training session: {session_id}[/blue]")

    # Run training
    try:
        if multi_process:
            asyncio.run(
                run_multi_process_training(session_id, config, training_data, validation_data, store, gpu_manager)
            )
        elif curriculum:
            asyncio.run(
                run_curriculum_training(
                    session_id, config, training_data, validation_data, store, gpu_manager, strategy
                )
            )
        else:
            asyncio.run(run_standard_training(session_id, config, training_data, validation_data, store, gpu_manager))

        console.print("[bold green]Training completed successfully![/bold green]")

    except Exception as e:
        console.print(f"[red]Training failed: {e}[/red]")
        logger.error(f"Training error: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--agent-type",
    "-t",
    type=click.Choice(["cad_analysis", "rag_quality", "ui_generation"]),
    required=True,
    help="Type of agent for prompt optimization",
)
@click.option("--iterations", "-i", default=50, help="Number of optimization iterations")
@click.option("--population-size", "-p", default=20, help="Population size for genetic algorithms")
@click.option(
    "--strategy",
    "-s",
    type=click.Choice(["genetic_algorithm", "reinforcement_learning", "bayesian_optimization"]),
    default="reinforcement_learning",
    help="Optimization strategy",
)
@click.pass_context
def optimize(ctx, agent_type, iterations, population_size, strategy):
    """Optimize prompts using APO (Automatic Prompt Optimization)."""
    console.print(f"[bold green]Optimizing prompts for {agent_type} agent[/bold green]")

    # Initialize store
    store_manager = LightningStoreManager(ctx.obj["model_dir"] / "store")
    store = store_manager.get_store("optimization")
    asyncio.run(store.initialize())

    # Load data
    data_dir = ctx.obj["data_dir"] or Path("data") / agent_type
    training_data, validation_data = load_training_data(data_dir)

    if not validation_data:
        console.print("[red]Error: No validation data found for optimization[/red]")
        sys.exit(1)

    # Create initial template
    template_generator = MechanicalEngineeringTemplateGenerator()
    if agent_type == "cad_analysis":
        initial_template = template_generator.create_cad_analysis_template()
    elif agent_type == "rag_quality":
        initial_template = template_generator.create_rag_template()
    else:  # ui_generation
        initial_template = template_generator.create_ui_generation_template()

    # Configure APO
    apo_config = APOConfig(strategy=strategy, max_iterations=iterations, population_size=population_size)

    optimizer = APOptimizer(apo_config)

    # Create optimization session
    session_id = f"apo_{agent_type}_{int(time.time())}"
    asyncio.run(
        store.create_training_session(
            session_id=session_id,
            agent_name=f"{agent_type}_prompt_optimizer",
            algorithm="APO",
            config=apo_config.dict(),
        )
    )

    console.print(f"[blue]Starting prompt optimization: {session_id}[/blue]")
    console.print(f"[blue]Strategy: {strategy.value}[/blue]")
    console.print(f"[blue]Iterations: {iterations}[/blue]")
    console.print(f"[blue]Population size: {population_size}[/blue]")

    # Run optimization with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Optimizing prompts...", total=iterations)

        # Optimize
        optimized_template = asyncio.run(
            optimizer.optimize_prompt(
                initial_template=initial_template,
                training_data=training_data[:100],  # Limit for speed
                validation_data=validation_data[:50],
                domain_context=f"mechanical_engineering_{agent_type}",
            )
        )

        progress.update(task, completed=iterations)

    # Display results
    console.print("\n[bold green]Optimization completed![/bold green]")

    # Show improvement
    initial_reward = optimizer.optimization_log[0]["improvement"] if optimizer.optimization_log else 0
    final_reward = optimizer.optimization_log[-1]["final_reward"] if optimizer.optimization_log else 0

    console.print(f"[blue]Initial reward: {initial_reward:.4f}[/blue]")
    console.print(f"[blue]Final reward: {final_reward:.4f}[/blue]")
    console.print(f"[blue]Improvement: {final_reward - initial_reward:+.4f}[/blue]")

    # Save optimized template
    output_path = ctx.obj["model_dir"] / f"optimized_prompts_{agent_type}.json"
    save_optimized_template(optimized_template, output_path)
    console.print(f"[green]Optimized template saved to {output_path}[/green]")


@cli.command()
@click.option(
    "--agent-type",
    "-t",
    type=click.Choice(["cad_analysis", "rag_quality", "ui_generation"], required=False),
    help="Filter by agent type",
)
@click.option("--status", "-s", type=click.Choice(["running", "completed", "failed"]), help="Filter by status")
@click.option("--limit", "-l", default=10, help="Maximum number of sessions to show")
def sessions(agent_type, status, limit):
    """List training sessions."""
    store_manager = LightningStoreManager(Path("models") / "store")
    store = store_manager.get_store("training")
    asyncio.run(store.initialize())

    sessions = asyncio.run(store.list_training_sessions(agent_name=agent_type, status=status, limit=limit))

    if not sessions:
        console.print("[yellow]No training sessions found[/yellow]")
        return

    # Create table
    table = Table(title="Training Sessions")
    table.add_column("Session ID", style="cyan")
    table.add_column("Agent", style="magenta")
    table.add_column("Algorithm", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Start Time", style="blue")
    table.add_column("Duration", style="red")

    for session in sessions:
        duration = ""
        if session.end_time:
            duration = str(session.end_time - session.start_time).split(".")[0]

        status_style = {"running": "yellow", "completed": "green", "failed": "red", "paused": "blue"}.get(
            session.status, "white"
        )

        table.add_row(
            session.session_id[:8] + "...",
            session.agent_name,
            session.algorithm,
            f"[{status_style}]{session.status}[/{status_style}]",
            session.start_time.strftime("%Y-%m-%d %H:%M"),
            duration,
        )

    console.print(table)


@cli.command()
@click.argument("session_id")
def evaluate(session_id):
    """Evaluate a trained model."""
    console.print(f"[bold green]Evaluating model from session {session_id}[/bold green]")

    store_manager = LightningStoreManager(Path("models") / "store")
    store = store_manager.get_store("training")
    asyncio.run(store.initialize())

    # Get session
    session = asyncio.run(store.get_training_session(session_id))
    if not session:
        console.print(f"[red]Session {session_id} not found[/red]")
        sys.exit(1)

    console.print(f"[blue]Agent: {session.agent_name}[/blue]")
    console.print(f"[blue]Algorithm: {session.algorithm}[/blue]")

    # Get checkpoints
    checkpoints = asyncio.run(store.get_model_checkpoints(session_id, best_only=True))
    if not checkpoints:
        console.print("[red]No model checkpoints found[/red]")
        sys.exit(1)

    best_checkpoint = checkpoints[0]
    console.print(f"[blue]Best checkpoint: {best_checkpoint.checkpoint_id}[/blue]")
    console.print(f"[blue]Loss: {best_checkpoint.loss:.4f}[/blue]")

    # Load test data and evaluate
    data_dir = Path("data") / session.agent_name
    if not data_dir.exists():
        console.print(f"[yellow]Test data directory {data_dir} not found[/yellow]")
        return

    _, test_data = load_training_data(data_dir)
    if not test_data:
        console.print("[yellow]No test data available[/yellow]")
        return

    console.print(f"[blue]Evaluating on {len(test_data)} test samples[/blue]")

    # Run evaluation
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task("Evaluating model...", total=len(test_data))

        # Simulate evaluation (in practice, load actual model and evaluate)
        results = asyncio.run(run_evaluation(session.agent_name, best_checkpoint, test_data, progress, task))

    # Display results
    console.print("\n[bold green]Evaluation Results:[/bold green]")

    results_table = Table()
    results_table.add_column("Metric", style="cyan")
    results_table.add_column("Value", style="green")

    for metric, value in results.items():
        results_table.add_row(metric.replace("_", " ").title(), f"{value:.4f}")

    console.print(results_table)


@cli.command()
@click.option(
    "--agent-type",
    "-t",
    type=click.Choice(["cad_analysis", "rag_quality", "ui_generation"]),
    required=True,
    help="Type of agent to test",
)
@click.option("--model-path", "-m", type=click.Path(exists=True), help="Path to trained model")
@click.option("--input", "-i", type=click.Path(exists=True), help="Input file for inference")
def predict(agent_type, model_path, input):
    """Run inference with a trained model."""
    console.print(f"[bold green]Running inference with {agent_type} agent[/bold green]")

    if not model_path:
        console.print("[red]Model path required for inference[/red]")
        sys.exit(1)

    # Load input data
    with open(input) as f:
        input_data = json.load(f)

    console.print(f"[blue]Input: {input}[/blue]")

    # Run inference (simulated)
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Running inference...")
        result = asyncio.run(run_inference(agent_type, model_path, input_data))

    # Display results
    console.print("\n[bold green]Inference Results:[/bold green]")
    console.print(json.dumps(result, indent=2))


@cli.command()
def status():
    """Show system status and resource utilization."""
    console.print("[bold green]System Status[/bold green]")

    # GPU status
    gpu_manager = GPUManager()
    gpu_manager.initialize()

    if gpu_manager.gpu_count > 0:
        gpu_report = gpu_manager.get_gpu_utilization_report()

        gpu_table = Table(title="GPU Status")
        gpu_table.add_column("GPU ID", style="cyan")
        gpu_table.add_column("Name", style="magenta")
        gpu_table.add_column("Memory", style="green")
        gpu_table.add_column("Utilization", style="yellow")
        gpu_table.add_column("Status", style="blue")

        for gpu_detail in gpu_report["gpu_details"]:
            memory_status = f"{gpu_detail['memory_available_mb']:.0f}MB free"
            utilization = f"{gpu_detail['utilization']:.1%}"
            status = "Allocated" if gpu_detail["allocated"] else "Available"

            gpu_table.add_row(str(gpu_detail["device_id"]), gpu_detail["name"], memory_status, utilization, status)

        console.print(gpu_table)
    else:
        console.print("[yellow]No GPUs available[/yellow]")

    # Storage status
    store_manager = LightningStoreManager(Path("models") / "store")
    store = store_manager.get_store("training")
    asyncio.run(store.initialize())

    storage_stats = asyncio.run(store.get_storage_stats())

    storage_table = Table(title="Storage Status")
    storage_table.add_column("Metric", style="cyan")
    storage_table.add_column("Value", style="green")

    storage_table.add_row("Total Sessions", str(storage_stats["total_sessions"]))
    storage_table.add_row("Completed Sessions", str(storage_stats["completed_sessions"]))
    storage_table.add_row("Total Checkpoints", str(storage_stats["total_checkpoints"]))
    storage_table.add_row("Database Size", f"{storage_stats['database_size_mb']:.2f} MB")

    console.print(storage_table)


# Helper functions
def load_training_data(data_dir: Path) -> tuple[list[dict], list[dict]]:
    """Load training and validation data."""
    training_data = []
    validation_data = []

    # Load JSON files
    for json_file in data_dir.glob("**/*.json"):
        try:
            with open(json_file) as f:
                data = json.load(f)

            # Split into training/validation (80/20)
            if hash(json_file.stem) % 5 == 0:  # 20% for validation
                validation_data.append(data)
            else:
                training_data.append(data)

        except Exception as e:
            logger.warning(f"Failed to load {json_file}: {e}")

    return training_data, validation_data


async def run_standard_training(session_id, config, training_data, validation_data, store, gpu_manager):
    """Run standard training without curriculum."""
    # Mock training implementation
    epochs = config["epochs"]
    batch_size = config["batch_size"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Training...", total=epochs)

        for epoch in range(epochs):
            # Simulate training step
            await asyncio.sleep(0.1)  # Simulate computation

            # Calculate mock metrics
            loss = 1.0 * (0.95**epoch) + 0.1
            accuracy = min(0.95, 0.5 + epoch * 0.01)

            # Save metrics
            metrics = {"epoch": epoch, "loss": loss, "accuracy": accuracy}

            await store.save_training_metrics(
                TrainingMetrics(
                    metrics_id=f"{session_id}_{epoch}",
                    session_id=session_id,
                    epoch=epoch,
                    step=epoch * (len(training_data) // batch_size),
                    timestamp=datetime.now(),
                    metrics=metrics,
                )
            )

            progress.update(task, advance=1)

    # Update session
    await store.update_training_session(
        session_id,
        status="completed",
        end_time=datetime.now(),
        final_metrics={"final_accuracy": accuracy, "final_loss": loss},
    )


async def run_curriculum_training(
    session_id, config, training_data, validation_data, store, gpu_manager, strategy_name
):
    """Run curriculum-based training."""
    curriculum_manager = CurriculumManager()
    curriculum = curriculum_manager.create_mechanical_engineering_curriculum(
        config["agent_type"], CurriculumStrategy(strategy_name)
    )

    total_epochs = config["epochs"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Curriculum training...", total=total_epochs)

        epoch = 0
        while epoch < total_epochs and not curriculum.is_complete():
            current_stage = curriculum.get_current_stage()
            if not current_stage:
                break

            # Train for current stage
            stage_epochs = min(current_stage.max_epochs, total_epochs - epoch)

            for stage_epoch in range(stage_epochs):
                await asyncio.sleep(0.1)  # Simulate training

                # Mock metrics for this stage
                stage_progress = stage_epoch / stage_epochs
                loss = 1.0 * (0.9**stage_epoch) + 0.1
                accuracy = current_stage.required_accuracy * stage_progress * 0.9

                # Save metrics
                await store.save_training_metrics(
                    TrainingMetrics(
                        metrics_id=f"{session_id}_{epoch}",
                        session_id=session_id,
                        epoch=epoch,
                        step=epoch * 10,
                        timestamp=datetime.now(),
                        metrics={"loss": loss, "accuracy": accuracy, "stage": current_stage.name},
                    )
                )

                progress.update(task, advance=1)
                epoch += 1

                # Check stage completion
                if stage_epoch >= current_stage.min_epochs:
                    stage_performance = {
                        "accuracy": accuracy,
                        "epochs_in_stage": stage_epoch + 1,
                        "recent_improvement": 0.01,
                    }

                    if curriculum_manager.update_stage_performance(f"{session_id}_curriculum", stage_performance):
                        console.print(f"[green]Completed stage: {current_stage.name}[/green]")
                        break

    # Update session
    await store.update_training_session(
        session_id,
        status="completed",
        end_time=datetime.now(),
        final_metrics={"stages_completed": len(curriculum.progress.completed_stages)},
    )


async def run_multi_process_training(session_id, config, training_data, validation_data, store, gpu_manager):
    """Run multi-process training."""
    trainer = MultiProcessTrainer(gpu_manager, store)
    await trainer.initialize()

    process_id = await trainer.start_training_process(
        session_id=session_id, config=config, training_data=training_data, validation_data=validation_data
    )

    # Monitor progress
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        progress.add_task("Multi-process training...")

        while True:
            status = await trainer.get_process_status(process_id)
            if not status:
                break

            if status["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(1)

    await trainer.shutdown()


async def run_evaluation(agent_name, checkpoint, test_data, progress, task):
    """Run model evaluation."""
    # Mock evaluation
    results = {
        "test_accuracy": 0.85 + np.random.normal(0, 0.05),
        "test_loss": 0.3 + np.random.normal(0, 0.05),
        "precision": 0.82 + np.random.normal(0, 0.03),
        "recall": 0.88 + np.random.normal(0, 0.03),
        "f1_score": 0.85 + np.random.normal(0, 0.02),
    }

    for _i, _ in enumerate(test_data):
        await asyncio.sleep(0.01)  # Simulate evaluation
        progress.update(task, advance=1)

    return results


async def run_inference(agent_type, model_path, input_data):
    """Run model inference."""
    # Mock inference
    await asyncio.sleep(0.5)

    if agent_type == "cad_analysis":
        return {
            "overall_rating": 4.2,
            "acoustic_performance": {"stc": 42.5},
            "structural_integrity": {"safety_factor": 2.8},
            "manufacturability": {"cnc_feasibility": 0.85},
            "recommendations": [{"severity": "medium", "description": "Consider adding reinforcement ribs"}],
        }
    if agent_type == "rag_quality":
        return {
            "answer": "Based on the technical documentation, the recommended procedure is...",
            "sources": ["manual_page_42.pdf", "safety_guidelines.pdf"],
            "confidence": 0.92,
        }
    # ui_generation
    return {"code": "<div class='industrial-dashboard'>...</div>", "framework": "react", "accessibility_score": 0.88}


def save_optimized_template(template, output_path):
    """Save optimized template to file."""
    template_data = {
        "name": template.name,
        "description": template.description,
        "elements": [
            {"type": elem.element_type.value, "content": elem.content, "weight": elem.weight, "position": elem.position}
            for elem in template.elements
        ],
        "optimization_history": template.optimization_history,
    }

    with open(output_path, "w") as f:
        json.dump(template_data, f, indent=2)


if __name__ == "__main__":
    cli()
