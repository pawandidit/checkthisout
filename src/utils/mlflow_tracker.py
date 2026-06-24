"""MLflow integration for model tracking and experiment management."""
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MLFlowTracker:
    """Track models and experiments with MLflow."""

    def __init__(self, experiment_name: str = "options-trading", tracking_uri: Optional[str] = None):
        """
        Initialize MLflow tracker.

        Args:
            experiment_name: Name of the experiment
            tracking_uri: MLflow tracking server URI (e.g., http://localhost:5000 or local path)
        """
        self.experiment_name = experiment_name
        self.tracking_uri = tracking_uri or os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
        self.mlflow = None
        self._initialize()

    def _initialize(self):
        """Initialize MLflow."""
        try:
            import mlflow

            self.mlflow = mlflow
            self.mlflow.set_tracking_uri(self.tracking_uri)
            self.mlflow.set_experiment(self.experiment_name)
            logger.info(f"MLflow initialized with experiment: {self.experiment_name}")
        except ImportError:
            logger.warning("MLflow not installed. Model tracking disabled. Install with: pip install mlflow")

    def start_run(self, run_name: str) -> Optional[str]:
        """Start an MLflow run."""
        if not self.mlflow:
            return None

        try:
            run = self.mlflow.start_run(run_name=run_name)
            logger.info(f"MLflow run started: {run_name}")
            return run.info.run_id
        except Exception as e:
            logger.error(f"Error starting MLflow run: {e}")
            return None

    def end_run(self):
        """End current MLflow run."""
        if not self.mlflow:
            return

        try:
            self.mlflow.end_run()
            logger.info("MLflow run ended")
        except Exception as e:
            logger.error(f"Error ending MLflow run: {e}")

    def log_params(self, params: Dict[str, Any]) -> bool:
        """Log parameters."""
        if not self.mlflow:
            return False

        try:
            for key, value in params.items():
                self.mlflow.log_param(key, value)
            logger.debug(f"Logged {len(params)} parameters")
            return True
        except Exception as e:
            logger.error(f"Error logging parameters: {e}")
            return False

    def log_metrics(self, metrics: Dict[str, float]) -> bool:
        """Log metrics."""
        if not self.mlflow:
            return False

        try:
            for key, value in metrics.items():
                self.mlflow.log_metric(key, value)
            logger.debug(f"Logged {len(metrics)} metrics")
            return True
        except Exception as e:
            logger.error(f"Error logging metrics: {e}")
            return False

    def log_model(self, model, artifact_path: str = "model") -> bool:
        """Log a model artifact."""
        if not self.mlflow:
            return False

        try:
            # Simple pickle-based logging
            import pickle
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pkl") as f:
                pickle.dump(model, f)
                self.mlflow.log_artifact(f.name, artifact_path=artifact_path)

            logger.info(f"Logged model artifact: {artifact_path}")
            return True
        except Exception as e:
            logger.error(f"Error logging model: {e}")
            return False

    def log_backtest_results(self, results: Dict[str, Any]) -> bool:
        """Log backtest results."""
        if not self.mlflow:
            return False

        try:
            self.log_metrics({
                "total_return_pct": results.get("total_return_pct", 0),
                "win_rate": results.get("win_rate", 0),
                "max_drawdown": results.get("max_drawdown", 0),
                "num_trades": results.get("num_trades", 0),
                "avg_win": results.get("avg_win", 0),
                "avg_loss": results.get("avg_loss", 0),
            })
            logger.info("Logged backtest results")
            return True
        except Exception as e:
            logger.error(f"Error logging backtest results: {e}")
            return False


# Global tracker instance
_tracker = None


def get_tracker(experiment_name: str = "options-trading") -> MLFlowTracker:
    """Get or create global MLflow tracker."""
    global _tracker
    if _tracker is None:
        _tracker = MLFlowTracker(experiment_name=experiment_name)
    return _tracker
