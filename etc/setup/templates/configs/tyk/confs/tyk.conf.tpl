{
  "app_path": "/opt/tyk-gateway/apps",
  "policies": {
    "policy_source": "file",
    "policy_record_name": "/opt/tyk-gateway/policies/policies.json"
  },
  
  "Monitor": {
    "configuration": {
      "event_timeout": 0,
      "header_map": null,
      "method": "",
      "target_path": "",
      "template_path": ""
    },
    "enable_trigger_monitors": false,
    "global_trigger_limit": 0,
    "monitor_org_keys": false,
    "monitor_user_keys": false
  },
  "allow_insecure_configs": true,
  "allow_master_keys": false,
  "allow_remote_config": true,
  "analytics_config": {
    "enable_detailed_recording": false,
    "enable_geo_ip": false,
    "geo_ip_db_path": "./GeoLite2-City.mmdb",
    "ignored_ips": [],
    "normalise_urls": {
      "custom_patterns": [],
      "enabled": true,
      "normalise_numbers": true,
      "normalise_uuids": true
    },
    "type": ""
  },
  "auth_override": {
    "auth_provider": {
      "meta": null,
      "name": "",
      "storage_engine": ""
    },
    "force_auth_provider": false,
    "force_session_provider": false,
    "session_provider": {
      "meta": null,
      "name": "",
      "storage_engine": ""
    }
  },
  "close_connections": false,
  "close_idle_connections": false,
  "control_api_hostname": "",
  "disable_dashboard_zeroconf": false,
  "disable_virtual_path_blobs": false,
  "enable_analytics": false,
  "enable_api_segregation": false,
  "enable_bundle_downloader": true,
  "enable_coprocess": false,
  "enable_custom_domains": true,
  "enable_jsvm": true,
  "enable_non_transactional_rate_limiter": true,
  "enable_sentinel_rate_limiter": false,
  "enable_separate_cache_store": false,
  "enforce_org_data_age": true,
  "enforce_org_data_detail_logging": false,
  "enforce_org_quotas": true,
  "event_handlers": {
    "events": {}
  },
  "event_trigers_defunct": {},
  "experimental_process_org_off_thread": false,
  "graylog_network_addr": "",
  "hash_keys": true,
  "health_check": {
    "enable_health_checks": false,
    "health_check_value_timeouts": 60
  },
  "hide_generator_header": false,
  "hostname": "",
  "http_server_options": {
    "certificates": [],
    "enable_websockets": true,
    "flush_interval": 0,
    "min_version": 0,
    "override_defaults": false,
    "read_timeout": 0,
    "server_name": "${CANDIG_HOST_NAME}",
    "use_ssl": false,
    "use_ssl_le": false,
    "write_timeout": 0
  },
  "listen_address": "",
  "listen_port": 8080,
  "local_session_cache": {
    "cached_session_eviction": 0,
    "cached_session_timeout": 0,
    "disable_cached_session_state": true
  },
  "logstash_network_addr": "",
  "logstash_transport": "",
  "max_idle_connections_per_host": 500,
  "middleware_path": "./middleware",
  "node_secret": "${SECRET_KEY}",
  "oauth_redirect_uri_separator": ";",
  "oauth_refresh_token_expire": 0,
  "oauth_token_expire": 0,
  "optimisations_use_async_session_write": true,
  "pid_file_location": "./tyk-gateway.pid",
  
  "public_key_path": "",
  "secret": "${SECRET_KEY}",
  "sentry_code": "",
  "service_discovery": {
    "default_cache_timeout": 0
  },
  "slave_options": {
    "api_key": "",
    "bind_to_slugs": false,
    "connection_string": "",
    "disable_keyspace_sync": false,
    "enable_rpc_cache": false,
    "group_id": "",
    "rpc_key": "",
    "use_rpc": false
  },
  "storage": {
    "database": 0,
    "enable_cluster": false,
    "host": "tyk-redis",
    "hosts": null,
    "optimisation_max_active": 5000,
    "optimisation_max_idle": 3000,
    "password": "",
    "port": 6379,
    "type": "redis",
    "username": ""
  },
  "suppress_default_org_store": false,
  "suppress_redis_signal_reload": false,
  "syslog_network_addr": "",
  "syslog_transport": "",
  "template_path": "./templates",
  "uptime_tests": {
    "config": {
      "checker_pool_size": 50,
      "enable_uptime_analytics": false,
      "failure_trigger_sample_size": 1,
      "time_wait": 2
    },
    "disable": true
  },
  "use_graylog": false,
  "use_logstash": false,
  "use_redis_log": true,
  "use_sentry": false,
  "use_syslog": false
}
