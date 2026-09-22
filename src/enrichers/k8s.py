import logging
import os
from typing import Dict, Any
from kubernetes import client, config
from kubernetes.client.exceptions import ApiException

logger = logging.getLogger("podwarden.enricher")

class K8sTelemetryEnricher:
    def __init__(self, use_in_cluster: bool = False):
        """
        Initializes the Kubernetes client. 
        Tries loading in-cluster config first, then falls back to local kubeconfig (~/.kube/config).
        """
        self.offline_mode = False
        try:
            if use_in_cluster:
                config.load_incluster_config()
            else:
                config.load_kube_config()
            
            self.v1 = client.CoreV1Api()
            logger.info("Successfully connected to Kubernetes cluster API.")
        except Exception as e:
            logger.warning(f"Could not initialize Kubernetes client ({e}). Falling back to OFFLINE MOCK MODE.")
            self.offline_mode = True

    def fetch_pod_telemetry(self, namespace: str, pod_name: str) -> Dict[str, Any]:
        """
        Gathers live container logs, exit codes, and recent events for a target pod.
        """
        if self.offline_mode:
            return self._get_mock_telemetry(namespace, pod_name)

        telemetry = {
            "namespace": namespace,
            "pod_name": pod_name,
            "logs": "",
            "restart_count": 0,
            "last_termination_reason": "Unknown",
            "events": []
        }

        try:
            # 1. Fetch recent container logs (last 100 lines)
            logs = self.v1.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                tail_lines=100,
                timestamps=True
            )
            telemetry["logs"] = logs
        except ApiException as e:
            telemetry["logs"] = f"Error fetching logs: {e.reason}"

        try:
            # 2. Inspect pod status and container restart states
            pod_obj = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            if pod_obj.status.container_statuses:
                c_status = pod_obj.status.container_statuses[0]
                telemetry["restart_count"] = c_status.restart_count
                
                if c_status.last_state.terminated:
                    telemetry["last_termination_reason"] = c_status.last_state.terminated.reason

            # 3. Fetch recent events associated with this pod
            field_selector = f"involvedObject.name={pod_name},involvedObject.namespace={namespace}"
            events = self.v1.list_namespaced_event(namespace=namespace, field_selector=field_selector)
            
            telemetry["events"] = [
                f"[{ev.type}] {ev.reason}: {ev.message}" for ev in events.items[-5:]
            ]

        except ApiException as e:
            logger.error(f"Kubernetes API error while enriching pod {namespace}/{pod_name}: {e}")

        return telemetry

    def _get_mock_telemetry(self, namespace: str, pod_name: str) -> Dict[str, Any]:
        """Provides realistic mock data for local testing without a live cluster."""
        return {
            "namespace": namespace,
            "pod_name": pod_name,
            "logs": (
                "2026-09-22T03:15:10Z [INFO] Starting auth-service v2.4.1...\n"
                "2026-09-22T03:15:11Z [ERROR] Database connection failed to 'postgres-cluster:5432': Connection refused\n"
                "2026-09-22T03:15:12Z [FATAL] Unhandled exception during startup. Exiting..."
            ),
            "restart_count": 5,
            "last_termination_reason": "Error",
            "events": [
                "[Warning] BackOff: Back-off restarting failed container",
                "[Normal] Killing: Container auth-service failed startup probe"
            ]
        }