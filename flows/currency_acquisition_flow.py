import os
import pandas as pd
from prefect import flow, get_run_logger
from prefect.artifacts import create_markdown_artifact
from utils.exchange_rate_fetcher import fetch_last_month_rates


@flow(name="currency_acquisition_flow")
def currency_acquisition_flow():
    """
    Fetch last month's FX rates (idempotent).
    Scheduled monthly via Prefect Cloud.
    """
    logger = get_run_logger()
    logger.info("Running monthly FX acquisition task...")

    fx_path = fetch_last_month_rates()

    logger.info(f"FX acquisition complete: {fx_path}")

    # Create Prefect Artifact
    try:
        df = pd.read_csv(fx_path)
        filename = os.path.basename(fx_path)
        
        # Create a markdown table
        # We limit the rows to avoid hitting artifact size limits if the file is huge
        # But for monthly exchange rates it should be fine.
        markdown_report = f"# Currency Exchange Rates Report\n\n"
        markdown_report += f"**File:** {filename}\n"
        markdown_report += f"**Total Rows:** {len(df)}\n\n"
        
        # Convert to markdown table
        markdown_report += df.to_markdown(index=False)
        
        create_markdown_artifact(
            key="exchange-rates-data",
            markdown=markdown_report,
            description=f"Exchange Rates for {filename}"
        )
        logger.info("Successfully created markdown artifact with exchange rate data.")
        
    except Exception as e:
        logger.error(f"Failed to create artifact: {e}")

    return fx_path


if __name__ == "__main__":
    currency_acquisition_flow()
