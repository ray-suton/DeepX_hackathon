from __future__ import annotations

import pathlib
import sys
import unittest

import onnx
from onnx import TensorProto, helper

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from app.contracts import HardwareResult
from app.errors import InvalidInputError, ParseFailedError, UnsupportedModelError
from app.service import (
    build_demo_report,
    build_report,
    build_report_from_upload,
    derive_winner_summary,
    normalize_request,
)


def build_test_onnx_bytes() -> bytes:
    input_tensor = helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, 224, 224])
    output_tensor = helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, 3, 224, 224])
    relu_node = helper.make_node("Relu", inputs=["input"], outputs=["output"])
    graph = helper.make_graph([relu_node], "paladin-test-graph", [input_tensor], [output_tensor])
    model = helper.make_model(graph)
    return model.SerializeToString()


class PaladinServiceTests(unittest.TestCase):
    def test_sample_mode_report_matches_contract_shape(self) -> None:
        payload = {
            "input_mode": "sample",
            "model_name": None,
            "sample_model_id": "resnet50-demo",
            "batch_size": 8,
            "precision": "fp16",
        }
        report = build_report(payload).to_dict()

        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["request"]["sample_model_id"], "resnet50-demo")
        self.assertEqual(len(report["hardware_results"]), 3)
        self.assertIn("winner_summary", report)
        self.assertIn("confidence", report)
        self.assertIn("assumptions", report)

    def test_invalid_batch_size_rejected(self) -> None:
        with self.assertRaises(InvalidInputError):
            normalize_request(
                {
                    "input_mode": "sample",
                    "model_name": None,
                    "sample_model_id": "resnet50-demo",
                    "batch_size": 0,
                    "precision": "fp16",
                }
            )

    def test_unknown_sample_model_rejected(self) -> None:
        with self.assertRaises(UnsupportedModelError):
            build_report(
                {
                    "input_mode": "sample",
                    "model_name": None,
                    "sample_model_id": "unknown-demo",
                    "batch_size": 8,
                    "precision": "fp16",
                }
            )

    def test_unknown_upload_model_rejected_as_parse_failed(self) -> None:
        with self.assertRaises(ParseFailedError):
            build_report(
                {
                    "input_mode": "upload",
                    "model_name": "unknown-model.onnx",
                    "sample_model_id": None,
                    "batch_size": 8,
                    "precision": "fp16",
                }
            )

    def test_no_clear_winner_is_neutral(self) -> None:
        spec = normalize_request(
            {
                "input_mode": "sample",
                "model_name": None,
                "sample_model_id": "resnet50-demo",
                "batch_size": 8,
                "precision": "fp16",
            }
        )
        results = [
            HardwareResult(
                hardware_id="a",
                hardware_label="A",
                latency_ms=10.0,
                throughput_inf_per_sec=80.0,
                power_watts=40.0,
                perf_per_watt=2.0,
                breakdown={"compute_ms": 7.0, "memory_ms": 2.0, "overhead_ms": 1.0},
            ),
            HardwareResult(
                hardware_id="b",
                hardware_label="B",
                latency_ms=10.3,
                throughput_inf_per_sec=78.0,
                power_watts=39.0,
                perf_per_watt=2.0,
                breakdown={"compute_ms": 7.1, "memory_ms": 2.2, "overhead_ms": 1.0},
            ),
        ]
        summary = derive_winner_summary(results, spec.batch_size)
        self.assertEqual(summary.winner_dimension, "balanced")

    def test_build_demo_report_is_ephemeral(self) -> None:
        demo = build_demo_report()
        self.assertTrue(demo["report_id"].startswith("ephemeral-"))

    def test_uploaded_onnx_builds_real_report(self) -> None:
        report = build_report_from_upload(
            filename="uploaded-test.onnx",
            file_bytes=build_test_onnx_bytes(),
            batch_size=4,
            precision="fp16",
        ).to_dict()
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["request"]["model_name"], "uploaded-test.onnx")
        self.assertEqual(report["workload_spec"]["input_shape"], [1, 3, 224, 224])
        self.assertEqual(len(report["hardware_results"]), 3)


if __name__ == "__main__":
    unittest.main()
