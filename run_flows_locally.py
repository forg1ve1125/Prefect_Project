#!/usr/bin/env python
"""
Local Flow Execution Script
Executes Flows directly locally, without relying on Cloud managed execution.
Can be scheduled via Task Scheduler or cron.
"""
import asyncio
from flows.currency_acquisition_flow import currency_acquisition_flow
from flows.prepare_batch_flow import prepare_batch_flow
from flows.process_batch_flow import process_batch_flow
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_currency_acquisition():
    """Run Currency Acquisition Flow"""
    logger.info("=" * 70)
    logger.info("Starting: currency_acquisition_flow")
    logger.info("=" * 70)
    
    try:
        result = currency_acquisition_flow()
        logger.info(f"✅ currency_acquisition_flow completed successfully")
        logger.info(f"Result: {result}")
        return True
    except Exception as e:
        logger.error(f"❌ currency_acquisition_flow failed: {str(e)}")
        return False


async def run_prepare_batch():
    """Run Batch Preparation Flow"""
    logger.info("=" * 70)
    logger.info("Starting: prepare_batch_flow")
    logger.info("=" * 70)
    
    try:
        result = prepare_batch_flow()
        logger.info(f"✅ prepare_batch_flow completed successfully")
        logger.info(f"Result: {result}")
        return True
    except Exception as e:
        logger.error(f"❌ prepare_batch_flow failed: {str(e)}")
        return False


async def run_process_batch():
    """Run Batch Processing Flow"""
    logger.info("=" * 70)
    logger.info("Starting: process_batch_flow")
    logger.info("=" * 70)
    
    try:
        result = process_batch_flow()
        logger.info(f"✅ process_batch_flow completed successfully")
        logger.info(f"Result: {result}")
        return True
    except Exception as e:
        logger.error(f"❌ process_batch_flow failed: {str(e)}")
        return False


async def main():
    """Main Program - Execute all Flows in sequence"""
    logger.info("")
    logger.info("╔" + "=" * 68 + "╗")
    logger.info("║" + " " * 68 + "║")
    logger.info("║" + "  Prefect Local Flow Execution".center(68) + "║")
    logger.info("║" + f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(68) + "║")
    logger.info("║" + " " * 68 + "║")
    logger.info("╚" + "=" * 68 + "╝")
    logger.info("")
    
    results = {}
    
    # Execute Flow 1: Currency Acquisition
    results['currency_acquisition'] = await run_currency_acquisition()
    logger.info("")
    
    # Execute Flow 2: Batch Preparation
    results['prepare_batch'] = await run_prepare_batch()
    logger.info("")
    
    # Execute Flow 3: Batch Processing
    results['process_batch'] = await run_process_batch()
    logger.info("")
    
    # Summary
    logger.info("=" * 70)
    logger.info("Execution Summary")
    logger.info("=" * 70)
    for flow_name, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{flow_name:25} {status}")
    logger.info("=" * 70)
    logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
