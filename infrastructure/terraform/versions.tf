terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  # Optional: uncomment to use remote state in Azure Storage
  # backend "azurerm" {
  #   resource_group_name  = "rg-terraform-state"
  #   storage_account_name = "CHANGE_ME_tfstate"
  #   container_name       = "tfstate"
  #   key                  = "employee-api.tfstate"
  # }
}
