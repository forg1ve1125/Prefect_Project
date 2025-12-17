from prefect import flow, get_run_logger
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
    return fx_path


if __name__ == "__main__":
    currency_acquisition_flow()
