

import json
import mysql.connector
from mysql.connector import Error
from pathlib import Path

# Old JSON file path
json_file = "/root/Baseline_Backend/Automation/Baseline_Automation_Backend/MCP_Client/detail.json"

# # Database config
# db_config = {
#     "host": "10.0.1.39",
#     "user": "resonance",
#     "password": "VBhkk!op",   # change if needed
#     "database": "SSOauthentication"
# }

# Database config
db_config = {
    "host": "10.0.1.39",
    "user": "automation",
    "password": "Aut0mat1on",   # change if needed
    "database": "SSO_AUTOMATION"
}

def migrate():
    # Load JSON config
    if not Path(json_file).exists():
        print(f"❌ JSON config file not found: {json_file}")
        return
    
    with open(json_file, "r") as f:
        servers = json.load(f)

    if not servers:
        print("⚠ No server configs found in JSON")
        return

    print(f"🔄 Migrating {len(servers)} servers from JSON → DB...")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        sql = """
            INSERT INTO mcp_servers (name, command, args, host, port, ssh_tunnel, ssh_host, ssh_user, module)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                command=VALUES(command),
                args=VALUES(args),
                host=VALUES(host),
                port=VALUES(port),
                ssh_tunnel=VALUES(ssh_tunnel),
                ssh_host=VALUES(ssh_host),
                ssh_user=VALUES(ssh_user),
                module=VALUES(module)
        """

        for name, config in servers.items():
            if "transport" in config and config["transport"] == "streamable_http":
                # Special case: streamable_http configs don't use command/args
                cursor.execute(sql, (
                    name,
                    "",             # command
                    "[]",           # args
                    config.get("url", ""),
                    None,           # port
                    False,          # ssh_tunnel
                    None,
                    None,
                    None
                ))
            else:
                cursor.execute(sql, (
                    name,
                    config.get("command", ""),
                    json.dumps(config.get("args", [])),
                    config.get("host", "localhost"),
                    config.get("port"),
                    config.get("ssh_tunnel", False),
                    config.get("ssh_host"),
                    config.get("ssh_user"),
                    config.get("module")
                ))

            print(f"   ✓ Migrated server: {name}")

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Migration complete!")

    except Error as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    migrate()
