#!/usr/bin/env python3
"""
Autonomous Predictive Trading System (APTS)
Fixed Version - Production Ready
Architecture: Modular with error handling, logging, and state management
"""

import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional
import schedule

from data_fetcher import DataFetcher
from feature_engineer import FeatureEngineer
from signal_generator import SignalGenerator
from trade_executor import TradeExecutor
from firebase_client import FirebaseClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('apts.log')
    ]
)
logger = logging.getLogger(__name__)


class APTS:
    """Main Autonomous Predictive Trading System orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize APTS with configuration"""
        self.config = config
        self.running = False
        
        # Initialize components with error handling
        try:
            logger.info("Initializing APTS components...")
            self.firebase = FirebaseClient(config.get('FIREBASE_CREDENTIALS_PATH'))
            self.data_fetcher = DataFetcher(config)
            self.feature_engineer = FeatureEngineer(config)
            self.signal_generator = SignalGenerator(config)
            self.trade_executor = TradeExecutor(config, self.firebase)
            
            logger.info("APTS initialization complete")
        except Exception as e:
            logger.error(f"Failed to initialize APTS: {e}")
            raise
    
    def run_cycle(self) -> bool:
        """Execute one complete trading cycle"""
        logger.info("Starting trading cycle...")
        
        try:
            # 1. Fetch market data
            logger.info("Fetching market data...")
            raw_data = self.data_fetcher.fetch_ohlcv()
            if raw_data is None or raw_data.empty:
                logger.error("No data retrieved")
                return False
            
            # 2. Engineer features
            logger.info("Engineering features...")
            features = self.feature_engineer.transform(raw_data)
            if features is None or features.empty:
                logger.error("Feature engineering failed")
                return False
            
            # 3. Generate trading signals
            logger.info("Generating trading signals...")
            signals = self.signal_generator.generate_signals(features)
            if not signals:
                logger.info("No trading