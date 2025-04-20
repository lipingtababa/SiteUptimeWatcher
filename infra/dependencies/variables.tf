variable "aiven_api_token" {
  type        = string
  description = "Aiven API token"
}

variable "aiven_project" {
  type        = string
  description = "IDP"
}

variable "stage" {
  type    = string
  default = "dev"
}
