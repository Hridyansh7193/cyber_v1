from pathlib import Path

# Paths relative to the repository root
DOCKER_DIR = Path("docker")
CONTAINERS_DIR = DOCKER_DIR / "containers"

def test_dockerfiles_exist():
    base_dockerfile = CONTAINERS_DIR / "base" / "Dockerfile"
    recon_dockerfile = CONTAINERS_DIR / "recon" / "Dockerfile"
    vuln_dockerfile = CONTAINERS_DIR / "vuln" / "Dockerfile"
    js_dockerfile = CONTAINERS_DIR / "js" / "Dockerfile"
    api_dockerfile = CONTAINERS_DIR / "api" / "Dockerfile"

    assert base_dockerfile.exists(), "Base Dockerfile missing"
    assert recon_dockerfile.exists(), "Recon Dockerfile missing"
    assert vuln_dockerfile.exists(), "Vuln Dockerfile missing"
    assert js_dockerfile.exists(), "JS Dockerfile missing"
    assert api_dockerfile.exists(), "API Dockerfile missing"

def test_docker_compose_exists():
    compose_file = DOCKER_DIR / "docker-compose.yml"
    assert compose_file.exists(), "docker-compose.yml missing"

def test_docker_compose_syntax():
    # Simple syntax check reading the YAML
    import yaml
    compose_file = DOCKER_DIR / "docker-compose.yml"
    with open(compose_file, "r") as f:
        data = yaml.safe_load(f)
    
    assert "version" in data
    assert "services" in data
    
    services = data["services"]
    assert "recon" in services
    assert "vuln" in services
    assert "js" in services
    assert "api" in services

    # Verify resource limits
    for service_name, config in services.items():
        assert "deploy" in config
        assert "limits" in config["deploy"]["resources"]
        assert config["deploy"]["resources"]["limits"]["cpus"] == "2"
        assert config["deploy"]["resources"]["limits"]["memory"] == "2G"

def test_dockerfiles_base_image_pinning():
    # Ensure they pin correctly
    base_dockerfile = CONTAINERS_DIR / "base" / "Dockerfile"
    content = base_dockerfile.read_text()
    assert "FROM ubuntu:24.04" in content, "Base image not pinned to ubuntu:24.04"

    # Others inherit from bughunter-base:latest
    for category in ["recon", "vuln", "js", "api"]:
        dockerfile = CONTAINERS_DIR / category / "Dockerfile"
        content = dockerfile.read_text()
        assert "FROM bughunter-base:latest" in content, f"{category} image not inheriting correctly"

def test_dockerfile_contents():
    # Check Recon
    recon_content = (CONTAINERS_DIR / "recon" / "Dockerfile").read_text()
    for tool in ["subfinder", "assetfinder", "httpx", "katana", "gau"]:
        assert tool in recon_content

    # Check Vuln
    vuln_content = (CONTAINERS_DIR / "vuln" / "Dockerfile").read_text()
    for tool in ["nuclei", "dalfox", "ffuf", "subzy"]:
        assert tool in vuln_content

    # Check JS
    js_content = (CONTAINERS_DIR / "js" / "Dockerfile").read_text()
    for tool in ["LinkFinder", "SecretFinder", "trufflehog"]:
        assert tool.lower() in js_content.lower()
