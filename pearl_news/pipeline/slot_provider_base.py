"""
Slot Provider Base — Abstract interface for filling slot contracts.

All slot providers:
- Read a pending slot contract file
- Fill only allowed slots (required_slots)
- Write completed contract to file
- Exit cleanly

Providers must NOT overwrite deterministic teacher-meaning slots.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


class SlotProviderBase(ABC):
    """Abstract base class for slot providers."""

    provider_name: str = "base"

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    @abstractmethod
    def fill_slots(
        self,
        contract: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """
        Fill the required slots from the contract.

        Args:
            contract: The slot contract with required_slots to fill.
            context: Optional additional context (source content, etc).

        Returns:
            Dict mapping slot name to filled value.
            Only slots listed in contract['required_slots'] may be filled.
        """
        raise NotImplementedError

    def load_pending_contract(self, path: Path) -> dict[str, Any]:
        """Load a pending slot contract from file."""
        if not path.exists():
            raise FileNotFoundError(f"Pending contract not found: {path}")

        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            data = json.loads(text)
        elif yaml is not None and path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(text) or {}
        else:
            raise ValueError(f"Unsupported contract format: {path.suffix}")

        if not isinstance(data, dict):
            raise ValueError(f"Contract must be a dict, got {type(data).__name__}")

        data["_source_path"] = str(path)
        return data

    def validate_filled_slots(
        self,
        contract: dict[str, Any],
        filled: dict[str, str],
    ) -> list[str]:
        """
        Validate that filled slots are allowed and complete.

        Returns list of error messages (empty = valid).
        """
        errors: list[str] = []
        required_slots = contract.get("required_slots") or {}

        if not isinstance(required_slots, dict):
            errors.append("contract.required_slots is not a dict")
            return errors

        allowed_keys = set(required_slots.keys())
        filled_keys = set(filled.keys())

        for key in filled_keys:
            if key not in allowed_keys:
                errors.append(f"filled_slot_not_allowed:{key}")

        for key in allowed_keys:
            value = filled.get(key, "")
            if not str(value or "").strip():
                errors.append(f"missing_required_slot:{key}")

        return errors

    def write_completed_contract(
        self,
        contract: dict[str, Any],
        filled: dict[str, str],
        slots_root: Path,
    ) -> Path:
        """
        Write a completed contract with filled slots.

        Moves from pending to completed directory.
        """
        article_id = contract.get("article_id")
        if not article_id:
            raise ValueError("Contract missing article_id")

        for slot, value in filled.items():
            if slot in (contract.get("required_slots") or {}):
                contract["required_slots"][slot] = value

        contract["status"] = "completed"
        contract["provenance"] = {
            "filled_by": self.provider_name,
            "filled_at": datetime.now(timezone.utc).isoformat(),
            "provider": self.provider_name,
        }

        completed_dir = slots_root / "completed"
        completed_dir.mkdir(parents=True, exist_ok=True)

        if yaml is not None:
            path = completed_dir / f"{article_id}.yaml"
            path.write_text(
                yaml.safe_dump(contract, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
        else:
            path = completed_dir / f"{article_id}.json"
            path.write_text(
                json.dumps(contract, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        logger.info("Wrote completed contract: %s", path)
        return path

    def process_contract(
        self,
        pending_path: Path,
        slots_root: Path,
        context: dict[str, Any] | None = None,
    ) -> tuple[Path, list[str]]:
        """
        Full flow: load pending → fill → validate → write completed.

        Returns:
            Tuple of (completed_path, errors).
            If errors is non-empty, completed_path may still be written
            but assembly should not proceed.
        """
        contract = self.load_pending_contract(pending_path)
        filled = self.fill_slots(contract, context)
        errors = self.validate_filled_slots(contract, filled)

        if errors:
            logger.warning(
                "Contract %s has validation errors: %s",
                contract.get("article_id"),
                errors,
            )

        completed_path = self.write_completed_contract(contract, filled, slots_root)
        return completed_path, errors

    def process_all_pending(
        self,
        slots_root: Path,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Process all pending contracts in slots_root/pending/.

        Returns list of results with article_id, completed_path, errors.
        """
        pending_dir = slots_root / "pending"
        if not pending_dir.exists():
            logger.info("No pending directory at %s", pending_dir)
            return []

        results: list[dict[str, Any]] = []
        for path in sorted(pending_dir.glob("*.yaml")) + sorted(pending_dir.glob("*.json")):
            try:
                completed_path, errors = self.process_contract(path, slots_root, context)
                results.append({
                    "article_id": path.stem,
                    "pending_path": str(path),
                    "completed_path": str(completed_path),
                    "errors": errors,
                    "success": len(errors) == 0,
                })
            except Exception as e:
                logger.error("Failed to process %s: %s", path, e)
                results.append({
                    "article_id": path.stem,
                    "pending_path": str(path),
                    "completed_path": None,
                    "errors": [str(e)],
                    "success": False,
                })

        return results
