variable "location" {
  description = "Azure region"
  type        = string
  default     = "centralindia"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-employee-api"
}

variable "acr_name" {
  description = "Azure Container Registry name (globally unique, alphanumeric)"
  type        = string
  # CHANGE_ME
}

variable "app_name" {
  description = "App Service name (globally unique)"
  type        = string
  # CHANGE_ME
}

variable "app_service_sku" {
  description = "App Service Plan SKU"
  type        = string
  default     = "B1"
}

variable "key_vault_name" {
  description = "Key Vault name (globally unique, 3-24 alphanumeric)"
  type        = string
  # CHANGE_ME
}

variable "tags" {
  description = "Common tags"
  type        = map(string)
  default = {
    project     = "employee-api"
    environment = "dev"
    managed_by  = "terraform"
  }
}
