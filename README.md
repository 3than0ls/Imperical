# Imperical
Discord bot that has uncommon but handy functions.

# Key features:
1) Create and assign groups of roles (known as profiles) to users.
2) Create a jail channel and jail users to restrict them to only type and see that channel.
3) Archive (or re-open) old channels that contain messages you want to save and not delete.

# Setting up

Due to how small it is, it lacks an actual database and instead uses .json files to store data and act as a database. It also utilizes a config.json file.

To start, create a `config.json` file in the root folder and copy and paste this and fill out values accordingly.
```
{
    "key": "your bot key (in string)",
    "logging": false,
    "owner": discord ID (in numbers),
    "has_access": []
}
```

To create the "database," create a `servers.json` file and copy and paste the following. 
```
{
    "has_access": [],
    "default": {
        "prefix": "+",
        "permission_type": "administrator",
        "custom_has_permission": [],
        "profiles": {},
        "jail_role": null,
        "jail_channel": null
    },
}
```

Ping the bot for help or use the help command. Default prefix is +, which can be changed through commands or through manually editing the servers.json file.
The bot can be invited to multiple servers and have different settings for each server.
