resource "aws_s3_bucket" "weather_agent_session_store" {
  bucket_prefix = "weather-agent-session-store"
  force_destroy = true
}
