output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "acr_name" {
  value = azurerm_container_registry.main.name
}

output "app_service_name" {
  value = azurerm_linux_web_app.main.name
}

output "app_service_default_hostname" {
  value = azurerm_linux_web_app.main.default_hostname
}

output "key_vault_uri" {
  value = azurerm_key_vault.main.vault_uri
}

output "managed_identity_client_id" {
  value = azurerm_user_assigned_identity.app.client_id
}

output "application_insights_connection_string" {
  value     = azurerm_application_insights.main.connection_string
  sensitive = true
}
