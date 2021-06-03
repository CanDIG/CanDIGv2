{
  "listen_port": 3000,
  "tyk_api_config": {
    "Host": "${CANDIG_PUBLIC_URL}",
    "Port": "8080",
    "Secret": "${TYK_NODE_SECRET}"
  },
  "mongo_url": "mongodb://tyk-mongo:27017/tyk_analytics",
  "page_size": 10,
  "admin_secret": "${TYK_ANALYTIC_ADMIN_SECRET}",
  "shared_node_secret": "${TYK_NODE_SECRET}",
  "redis_port": 6379,
  "redis_host": "tyk-redis",
  "redis_password": "",
  "enable_cluster": false,
  "force_api_defaults": false,
  "notify_on_change": true,
  "license_key": "${ANALYTIC_LIC_KEY}",
  "redis_database": 0,
  "redis_hosts": null,
  "hash_keys": true,
  "email_backend": {
    "enable_email_notifications": false,
    "code": "sendgrid",
    "settings": {
      "ClientKey": ""
    },
    "default_from_email": "${TYK_DASH_FROM_EMAIL}",
    "default_from_name": "${TYK_DASH_FROM_NAME}"
  },
  "hide_listen_path": false,
  "sentry_code": "",
  "sentry_js_code": "",
  "use_sentry": false,
  "enable_master_keys": false,
  "enable_duplicate_slugs": true,
  "show_org_id": true,
  "host_config": {
    "enable_host_names": true,
    "disable_org_slug_prefix": true,
    "hostname": "www.tyk-test.com",
    "override_hostname": "www.tyk-test.com:8080",
    "portal_domains": {},
    "portal_root_path": "/portal",
    "generate_secure_paths": false,
    "use_strict_hostmatch": false
  },
  "http_server_options": {
    "use_ssl": false,
    "certificates": [],
    "min_version": 0
  },
  "ui": {
    "languages": {
      "Chinese": "cn",
      "English": "en",
      "Korean": "ko"
    },
    "hide_help": true,
    "default_lang": "en",
    "login_page": {},
    "nav": {
      "dont_show_admin_sockets": false,
      "hide_activity_by_api_section": false,
      "hide_geo": false,
      "hide_licenses_section": false,
      "hide_logs": false,
      "hide_tib_section": false
    },
    "uptime": {},
    "portal_section": null,
    "designer": {},
    "dont_show_admin_sockets": false,
    "dont_allow_license_management": false,
    "dont_allow_license_management_view": false
  },
  "home_dir": "/opt/tyk-dashboard",
  "tagging_options": {
    "tag_all_apis_by_org": false
  },
  "use_sharded_analytics": true,
  "enable_aggregate_lookups": true,
  "enable_analytics_cache": false,
  "aggregate_lookup_cutoff": "26/05/2016",
  "maintenance_mode": false,
  "allow_explicit_policy_id": true,
  "private_key_path": "",
  "node_schema_path": "",
  "oauth_redirect_uri_separator": ";",
  "statsd_connection_string": "",
  "statsd_prefix": ""
}