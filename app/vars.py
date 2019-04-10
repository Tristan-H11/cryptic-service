# In game specific stuff

config: dict = {
    "CHANCE": 20000,

    "services": {
        "SSH": {
            "default_port": 22,
            "exploit_able": True,
            "allow_remote_access": True,
        },
        "Hydra": {
            "default_port": None,
            "exploit_able": False,
            "allow_remote_access": False,
        },
        "nmap": {
            "default_port": None,
            "exploit_able": False,
            "allow_remote_access": False,
        },
        "Telnet": {
            "default_port": 23,
            "exploit_able": True,
            "allow_remote_access": True,
        }
    }
}