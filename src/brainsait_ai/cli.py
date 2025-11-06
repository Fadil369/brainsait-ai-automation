"""CLI interface for BrainSAIT AI-powered business discovery."""

import asyncio
import json
import logging
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .ai.client import LLMConfig, OpenAILLM
from .config import Settings
from .features.engineering import FeatureVector
from .generation.offers import (
    BusinessAnalysis as OfferInput,
    OfferGenerator,
    OutreachMessage,
    TailoredOffer,
)
from .google_places.client import BusinessRecord, Coordinates
from .pipeline.orchestrator import (
    AnalyzedBusiness,
    DiscoveryResult,
    PipelineConfig,
    run_pipeline_cli,
)
from .scoring.digital_maturity import MaturityAssessment, SubScores
from .storage.persistence import DataStore
from .logging_utils import configure_logging

# Initialize Typer app
app = typer.Typer(
    name="brainsait-discover",
    help="BrainSAIT AI-powered business discovery and analysis tool",
    rich_markup_mode="rich"
)

# Initialize console for rich output
console = Console()


@app.command()
def discover(
    business_types: List[str] = typer.Argument(..., help="Business types to search for (e.g., restaurant, clinic, hospital)"),
    location: str = typer.Option("24.7136,46.6753", "--location", "-l", help="Coordinates (lat,lng) for search center (default: Riyadh)"),
    radius: int = typer.Option(25000, "--radius", "-r", help="Search radius in meters (default: 25000 = 25km)"),
    max_businesses: int = typer.Option(100, "--max", "-m", help="Maximum businesses to discover (default: 100)"),
    batch_size: int = typer.Option(20, "--batch", "-b", help="Batch size for processing (default: 20)"),
    no_web_analysis: bool = typer.Option(False, "--no-web-analysis", help="Skip web content analysis"),
    no_offers: bool = typer.Option(False, "--no-offers", help="Skip AI offer generation"),
    output_dir: str = typer.Option("results", "--output", "-o", help="Output directory for results"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="Path to configuration file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    save_intermediate: bool = typer.Option(True, "--save-intermediate", help="Save intermediate results")
):
    """Discover and analyze businesses using AI-powered digital maturity assessment."""
    
    # Setup logging
    configure_logging(logging.DEBUG if verbose else logging.INFO)
    
    # Parse location coordinates
    try:
        lat, lng = map(float, location.split(','))
        search_location = (lat, lng)
    except ValueError:
        console.print(f"[red]Error:[/red] Invalid location format. Use 'lat,lng' (e.g., '24.7136,46.6753')")
        raise typer.Exit(1)
    
    # Create pipeline configuration
    config = PipelineConfig(
        search_radius=radius,
        max_businesses=max_businesses,
        batch_size=batch_size,
        include_web_analysis=not no_web_analysis,
        generate_offers=not no_offers,
        save_intermediate_results=save_intermediate,
        output_directory=output_dir
    )
    
    # Display configuration
    console.print(Panel.fit(
        f"[bold blue]BrainSAIT Business Discovery Pipeline[/bold blue]\n\n"
        f"Business Types: {', '.join(business_types)}\n"
        f"Location: {lat}, {lng}\n"
        f"Radius: {radius}m ({radius/1000:.1f}km)\n"
        f"Max Businesses: {max_businesses}\n"
        f"Web Analysis: {'Enabled' if not no_web_analysis else 'Disabled'}\n"
        f"Offer Generation: {'Enabled' if not no_offers else 'Disabled'}\n"
        f"Output Directory: {output_dir}"
    ))
    
    # Run the discovery pipeline
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Starting pipeline...", total=None)
            
            # Run async pipeline
            result = asyncio.run(run_pipeline_cli(business_types, search_location, config))
            
            progress.update(task, description="Pipeline completed!")
        
        # Display results
        display_results(result)
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def analyze(
    business_data: Path = typer.Argument(..., help="Path to business data JSON/JSONL file"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file for analysis summary"),
    generate_offers: bool = typer.Option(False, "--offers/--no-offers", help="Generate AI offers (use 'offers' command instead)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Analyze existing business data for digital maturity."""
    
    configure_logging(logging.DEBUG if verbose else logging.INFO)
    
    if not business_data.exists():
        console.print(f"[red]Error:[/red] File not found: {business_data}")
        raise typer.Exit(1)
    
    try:
        records = _load_analysis_records(business_data)
        console.print(f"[green]Loaded[/green] {len(records)} business records from {business_data}")
        
        summary = _summarise_records(records)
        
        # Display summary table
        summary_table = Table(title="Analysis Summary")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")
        
        summary_table.add_row("Total Businesses", str(summary["total"]))
        if summary.get("average_score"):
            summary_table.add_row("Average Maturity Score", f"{summary['average_score']:.1f}")
        
        console.print(summary_table)
        
        # Industry breakdown
        if summary.get("industries"):
            industry_table = Table(title="Industry Distribution")
            industry_table.add_column("Industry", style="cyan")
            industry_table.add_column("Count", style="green")
            
            for industry, count in list(summary["industries"].items())[:10]:
                industry_table.add_row(industry, str(count))
            
            console.print(industry_table)
        
        if output_file:
            output_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
            console.print(f"[green]Summary saved to[/green] {output_file}")
        
        if generate_offers:
            console.print("[yellow]Note:[/yellow] Use the 'offers' command to generate tailored offers.")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def offers(
    business_analysis_file: Path = typer.Argument(..., help="Path to business analysis JSON/JSONL file"),
    output_dir: str = typer.Option("offers", "--output", "-o", help="Output directory for offers"),
    batch_size: int = typer.Option(10, "--batch", "-b", help="Number of offers to generate per batch"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging")
):
    """Generate AI-powered tailored offers for analyzed businesses."""
    
    configure_logging(logging.DEBUG if verbose else logging.INFO)
    
    if not business_analysis_file.exists():
        console.print(f"[red]Error:[/red] File not found: {business_analysis_file}")
        raise typer.Exit(1)
    
    try:
        analyses = _load_analysis_records(business_analysis_file)
        console.print(f"[green]Loaded[/green] {len(analyses)} business analyses")
        
        # Initialize LLM and generator
        settings = Settings()
        llm = OpenAILLM(
            api_key=settings.openai_api_key,
            config=LLMConfig(
                model=settings.openai_model,
                temperature=settings.llm_temperature,
            ),
        )
        generator = OfferGenerator(llm)
        data_store = DataStore(Path(output_dir))
        data_store.root.mkdir(parents=True, exist_ok=True)
        
        offers_created = 0
        skipped = 0
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating offers...", total=len(analyses))
            
            for index, record in enumerate(analyses, start=1):
                analyzed = _dict_to_analyzed_business(record)
                
                # Skip if offer already exists
                if analyzed.offer is not None and analyzed.outreach is not None:
                    skipped += 1
                    progress.advance(task)
                    continue
                
                # Build offer input profile
                profile = OfferInput(
                    business=analyzed.business,
                    feature_vector=analyzed.feature_vector,
                    maturity=analyzed.maturity,
                    industry=analyzed.industry,
                    web_page_titles=[page.get("title", "") for page in record.get("pages", []) if page.get("title")],
                )
                
                # Generate offer and outreach
                offer = generator.generate_tailored_offer(profile)
                outreach = generator.create_outreach_message(profile, offer)
                
                analyzed.offer = offer
                analyzed.outreach = outreach
                offers_created += 1
                
                # Persist to file
                filename = Path(output_dir) / f"offer_{_slugify(analyzed.business.name)}.json"
                generator.save_offer_to_file(profile, offer, outreach, filename)
                
                progress.update(task, description=f"Generated {offers_created}/{len(analyses) - skipped} offers...")
                progress.advance(task)
        
        console.print(f"[green]✓ Generated {offers_created} new offers[/green]")
        if skipped:
            console.print(f"[yellow]↻ Skipped {skipped} existing offers[/yellow]")
        console.print(f"[blue]→ Offers saved to {output_dir}[/blue]")
        
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def config():
    """Display current configuration and setup instructions."""
    
    settings = Settings()
    
    table = Table(title="BrainSAIT Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_column("Status", style="yellow")
    
    # Check API keys
    google_status = "✅ Set" if settings.google_maps_api_key else "❌ Missing"
    openai_status = "✅ Set" if settings.openai_api_key else "❌ Missing"
    
    table.add_row("Google Maps API Key", settings.google_maps_api_key[:10] + "..." if settings.google_maps_api_key else "Not configured", google_status)
    table.add_row("OpenAI API Key", settings.openai_api_key[:10] + "..." if settings.openai_api_key else "Not configured", openai_status)
    table.add_row("Default Location", "24.7136, 46.6753 (Riyadh)", "✅ Default")
    table.add_row("Search Radius", "25km", "✅ Default")
    table.add_row("Batch Size", "20", "✅ Default")
    
    console.print(table)
    
    console.print("\n[bold blue]Setup Instructions:[/bold blue]")
    console.print("1. Copy .env.example to .env")
    console.print("2. Add your Google Maps API key")
    console.print("3. Add your OpenAI API key (optional, for enhanced AI features)")
    console.print("4. Run: brainsait-discover restaurant clinic hospital")


@app.command()
def version():
    """Display version information."""
    console.print("BrainSAIT AI Business Discovery v1.0.0")


def display_results(result: DiscoveryResult) -> None:
    """Display pipeline results in a nice format."""
    
    # Results summary
    summary_table = Table(title="Pipeline Results Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    summary_table.add_column("Description", style="dim")
    
    summary_table.add_row(
        "Businesses Discovered", 
        str(result.businesses_discovered), 
        "Total unique businesses found via Google Places API"
    )
    summary_table.add_row(
        "Businesses Analyzed", 
        str(len(result.analyses)), 
        "Successfully processed with digital maturity scoring"
    )
    summary_table.add_row(
        "Offers Generated", 
        str(result.offers_generated), 
        "AI-generated tailored business offers"
    )
    summary_table.add_row(
        "Output Files", 
        str(len(result.output_files)), 
        "JSON files with complete analysis and offers"
    )
    
    console.print(summary_table)
    
    # Industry breakdown (if available)
    if result.summary.get("industries"):
        industries_table = Table(title="Industry Distribution")
        industries_table.add_column("Industry", style="cyan")
        industries_table.add_column("Count", style="green")
        industries_table.add_column("Percentage", style="yellow")
        
        total_businesses = result.summary["total_businesses"]
        for industry, count in list(result.summary["industries"].items())[:10]:  # Top 10
            percentage = (count / total_businesses) * 100
            industries_table.add_row(industry, str(count), f"{percentage:.1f}%")
        
        console.print(industries_table)
    
    # Digital maturity distribution
    if result.summary.get("maturity_distribution"):
        maturity_table = Table(title="Digital Maturity Distribution")
        maturity_table.add_column("Maturity Level", style="cyan")
        maturity_table.add_column("Count", style="green")
        maturity_table.add_column("Score Range", style="yellow")
        
        distribution = result.summary["maturity_distribution"]
        maturity_table.add_row("Low", str(distribution.get("low (0-30)", 0)), "0-30 points")
        maturity_table.add_row("Medium", str(distribution.get("medium (31-70)", 0)), "31-70 points")
        maturity_table.add_row("High", str(distribution.get("high (71-100)", 0)), "71-100 points")
        
        console.print(maturity_table)
        
        # Average maturity score
        avg_score = result.summary.get("average_maturity_score", 0)
        score_color = "green" if avg_score > 70 else "yellow" if avg_score > 30 else "red"
        console.print(f"\n[bold]Average Digital Maturity Score:[/bold] [{score_color}]{avg_score}[/{score_color}]")
    
    # File outputs
    if result.output_files:
        files_panel = Panel.fit(
            "[bold]Output Files Created:[/bold]\n" + 
            "\n".join(f"• {Path(f).name}" for f in result.output_files[:10]) +
            ("\n... and more" if len(result.output_files) > 10 else ""),
            title="Results Location",
            border_style="blue"
        )
        console.print(files_panel)
    
    # Next steps
    console.print("\n[bold blue]Next Steps:[/bold blue]")
    console.print("• Review generated offers in the output files")
    console.print("• Use the outreach messages for business contact")
    console.print("• Run targeted campaigns based on digital maturity scores")
    console.print("• Monitor business responses and track conversion rates")


# ============================================================================
# Helper Functions
# ============================================================================

def _load_analysis_records(path: Path) -> List[Dict[str, Any]]:
    """Load analysis records from JSON or JSONL file."""
    if path.suffix.lower() == ".jsonl":
        records: List[Dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
    
    # Standard JSON
    data = json.load(path.open("r", encoding="utf-8"))
    if isinstance(data, dict) and "analyses" in data:
        return list(data["analyses"])
    if isinstance(data, list):
        return data
    raise typer.Exit(f"Unsupported analysis data format in {path}")


def _summarise_records(records: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    """Create summary statistics from analysis records."""
    if not records:
        return {"total": 0}
    
    scores = [record.get("digital_maturity", {}).get("overall_score", 0) for record in records]
    industries: Dict[str, int] = {}
    for record in records:
        industry = record.get("industry") or record.get("features", {}).get("industry", "General")
        industries[industry] = industries.get(industry, 0) + 1
    
    return {
        "total": len(records),
        "average_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "industries": industries,
    }


def _dict_to_analyzed_business(payload: Dict[str, Any]) -> AnalyzedBusiness:
    """Reconstruct AnalyzedBusiness from dict payload."""
    business = payload.get("business", {})
    location = business.get("location", {})
    record = BusinessRecord(
        place_id=business.get("place_id", ""),
        name=business.get("name", "Unknown"),
        address=business.get("address", ""),
        location=Coordinates(lat=location.get("lat", 0.0), lng=location.get("lng", 0.0)),
        types=tuple(business.get("types", [])),
        rating=business.get("rating"),
        user_ratings_total=business.get("user_ratings_total"),
        website=business.get("website"),
        phone_number=business.get("phone_number"),
        google_maps_url=business.get("google_maps_url", ""),
    )
    
    fv_data = payload.get("feature_vector", {})
    feature_vector = FeatureVector(
        place_id=fv_data.get("place_id", record.place_id),
        business_name=fv_data.get("business_name", record.name),
        website=fv_data.get("website"),
        total_pages=fv_data.get("total_pages", 0),
        languages=list(fv_data.get("languages", [])),
        avg_word_count=fv_data.get("avg_word_count", 0.0),
        has_structured_data=fv_data.get("has_structured_data", False),
        has_meta_description=fv_data.get("has_meta_description", False),
        has_open_graph=fv_data.get("has_open_graph", False),
        has_analytics=fv_data.get("has_analytics", False),
        has_contact_cta=fv_data.get("has_contact_cta", False),
        has_viewport_meta=fv_data.get("has_viewport_meta", False),
        has_email_address=fv_data.get("has_email_address", False),
        has_phone_number=fv_data.get("has_phone_number", False),
    )
    
    maturity_data = payload.get("digital_maturity", {})
    subscores_data = maturity_data.get("subscores", {})
    subscores = SubScores(
        technical=subscores_data.get("technical", 0.0),
        seo=subscores_data.get("seo", 0.0),
        content=subscores_data.get("content", 0.0),
        trust=subscores_data.get("trust", 0.0),
    )
    maturity = MaturityAssessment(
        place_id=maturity_data.get("place_id", record.place_id),
        business_name=maturity_data.get("business_name", record.name),
        overall_score=maturity_data.get("overall_score", 0.0),
        subscores=subscores,
        highlights_en=maturity_data.get("highlights_en", ""),
        highlights_ar=maturity_data.get("highlights_ar", ""),
        recommendations_en=maturity_data.get("recommendations_en", ""),
        recommendations_ar=maturity_data.get("recommendations_ar", ""),
    )
    
    industry = payload.get("industry") or payload.get("features", {}).get("industry", "General")
    
    offer_payload = payload.get("tailored_offer")
    outreach_payload = payload.get("outreach_message")
    
    offer = None
    outreach = None
    if offer_payload:
        from .generation.offers import ServicePackage
        offer = TailoredOffer(
            package_recommendation=ServicePackage(offer_payload.get("package_recommendation", "basic")),
            adjusted_price=offer_payload.get("adjusted_price", 0),
            justification=offer_payload.get("justification", ""),
            arabic_summary=offer_payload.get("arabic_summary", ""),
            english_summary=offer_payload.get("english_summary", ""),
            priority_features=list(offer_payload.get("priority_features", [])),
            roi_projection=offer_payload.get("roi_projection", ""),
            next_steps=list(offer_payload.get("next_steps", [])),
        )
    if outreach_payload:
        outreach = OutreachMessage(
            subject_ar=outreach_payload.get("subject_ar", ""),
            subject_en=outreach_payload.get("subject_en", ""),
            body_ar=outreach_payload.get("body_ar", ""),
            body_en=outreach_payload.get("body_en", ""),
            call_to_action=outreach_payload.get("call_to_action", ""),
            business_specific_details=outreach_payload.get("business_specific_details", ""),
        )
    
    return AnalyzedBusiness(
        business=record,
        feature_vector=feature_vector,
        pages=[],
        maturity=maturity,
        industry=industry,
        offer=offer,
        outreach=outreach,
    )


def _slugify(value: str) -> str:
    """Convert text to filesystem-safe slug."""
    value = value.strip().lower()
    value = "".join(ch if ch.isalnum() else "-" for ch in value)
    return "-".join(part for part in value.split("-") if part) or "business"


if __name__ == "__main__":
    app()
