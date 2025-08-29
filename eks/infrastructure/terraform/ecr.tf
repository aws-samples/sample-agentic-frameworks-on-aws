# ECR Repositories for Weather Agent Components

resource "aws_ecr_repository" "weather_mcp" {
  name                 = "agents-on-eks/weather-mcp"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}

resource "aws_ecr_repository" "weather_agent" {
  name                 = "agents-on-eks/weather-agent"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}

resource "aws_ecr_repository" "travel_agent" {
  name                 = "agents-on-eks/travel-agent"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}


resource "aws_ecr_repository" "agent_ui" {
  name                 = "agents-on-eks/agent-ui"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = local.tags
}
