{
    "${TYK_POLICY_ID}": {
        "access_rights": {
        },
        "active": true,
        "name": "CanDIG Policy",
        "rate": 100,
        "per": 1,
        "quota_max": 10000,
        "quota_renewal_rate": 3600,
        "tags": ["Startup Users"]
    },

    "default": {
        "rate": 1000,
        "per": 1,
        "quota_max": 100,
        "quota_renewal_rate": 60,
        "access_rights": {
            "41433797848f41a558c1573d3e55a410": {
            "api_name": "My API",
            "api_id": "41433797848f41a558c1573d3e55a410",
            "versions": [
                "Default"
            ]
            }
        },
        "org_id": "54de205930c55e15bd000001",
        "hmac_enabled": false
    }
}
