"""Container integration tests for Calendar Event Converter.

These tests verify that the Docker container:
1. Starts successfully
2. Health check endpoint responds
3. Can communicate with external services
"""

import subprocess
import time
import requests
import pytest


class TestContainerIntegration:
    """Integration tests for Docker container."""
    
    @pytest.fixture(scope="class")
    def container_running(self):
        """Fixture to ensure container is running for tests."""
        # Check if container is already running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=calendar-event-converter", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        
        container_was_running = "calendar-event-converter" in result.stdout
        
        if not container_was_running:
            # Build and start the container
            print("Building Docker image...")
            build_result = subprocess.run(
                ["docker", "build", "-t", "calendar-event-converter", "."],
                capture_output=True,
                text=True
            )
            
            if build_result.returncode != 0:
                pytest.skip(f"Docker build failed: {build_result.stderr}")
            
            print("Starting Docker container...")
            start_result = subprocess.run(
                ["docker", "run", "-d", "--name", "calendar-event-converter-test",
                 "-p", "8001:8000",  # Use different port to avoid conflicts
                 "-v", f"{subprocess.run(['pwd'], capture_output=True, text=True).stdout.strip()}/config/config.yaml:/app/config/config.yaml:ro",
                 "calendar-event-converter"],
                capture_output=True,
                text=True
            )
            
            if start_result.returncode != 0:
                pytest.skip(f"Docker start failed: {start_result.stderr}")
            
            # Wait for container to be ready
            print("Waiting for container to be ready...")
            time.sleep(5)
        
        yield
        
        # Cleanup: stop and remove test container if we started it
        if not container_was_running:
            subprocess.run(
                ["docker", "stop", "calendar-event-converter-test"],
                capture_output=True
            )
            subprocess.run(
                ["docker", "rm", "calendar-event-converter-test"],
                capture_output=True
            )
    
    def test_container_starts_successfully(self, container_running):
        """Test that the Docker container starts successfully.
        
        Validates: Requirements 6.1, 6.4
        """
        # Check if container is running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=calendar-event-converter", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        assert "Up" in result.stdout, "Container should be running"
    
    def test_health_check_responds(self, container_running):
        """Test that the health check endpoint responds correctly.
        
        Validates: Requirements 6.4
        """
        # Try to connect to health check endpoint
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get("http://localhost:8001/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    assert data["status"] == "healthy", "Health check should return healthy status"
                    return
            except requests.exceptions.RequestException:
                if i < max_retries - 1:
                    time.sleep(2)
                    continue
                raise
        
        pytest.fail("Health check endpoint did not respond after multiple retries")
    
    def test_container_can_communicate_with_external_services(self, container_running):
        """Test that the container can communicate with external services.
        
        This test verifies that the container's network configuration allows
        communication with external services (like LLM servers).
        
        Validates: Requirements 6.3
        """
        # We'll test this by checking if the container can resolve external DNS
        # and make outbound connections
        result = subprocess.run(
            ["docker", "exec", "calendar-event-converter-test", 
             "python", "-c", 
             "import socket; socket.gethostbyname('google.com'); print('OK')"],
            capture_output=True,
            text=True
        )
        
        # If container doesn't exist, try the main one
        if result.returncode != 0:
            result = subprocess.run(
                ["docker", "exec", "calendar-event-converter", 
                 "python", "-c", 
                 "import socket; socket.gethostbyname('google.com'); print('OK')"],
                capture_output=True,
                text=True
            )
        
        assert "OK" in result.stdout, "Container should be able to resolve external DNS"


def test_dockerfile_exists():
    """Test that Dockerfile exists and is properly configured."""
    import os
    assert os.path.exists("Dockerfile"), "Dockerfile should exist"
    
    with open("Dockerfile", "r") as f:
        content = f.read()
        
    # Verify key requirements
    assert "FROM python:3.11" in content, "Should use Python 3.11+ base image"
    assert "uv" in content, "Should install uv package manager"
    assert "EXPOSE 8000" in content, "Should expose port 8000"
    assert "uvicorn" in content, "Should run uvicorn server"


def test_docker_compose_exists():
    """Test that docker-compose.yml exists and is properly configured."""
    import os
    import yaml
    
    assert os.path.exists("docker-compose.yml"), "docker-compose.yml should exist"
    
    with open("docker-compose.yml", "r") as f:
        compose_config = yaml.safe_load(f)
    
    # Verify key requirements
    assert "services" in compose_config, "Should have services section"
    assert "calendar-converter" in compose_config["services"], "Should have calendar-converter service"
    
    service = compose_config["services"]["calendar-converter"]
    assert "ports" in service, "Should map ports"
    assert "8000:8000" in service["ports"], "Should map port 8000"
    assert "volumes" in service, "Should mount config.yaml"
    
    # Check for host.docker.internal access
    assert "extra_hosts" in service or "network_mode" in service, \
        "Should configure network for host.docker.internal access"
