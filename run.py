import json
from kutana import Kutana, load_plugins
from kutana.backends import Vkontakte
from kutana.backends import Telegram

# Import configuration
with open("config.json") as fh:
    config = json.load(fh)

# Create application
app = Kutana()

# Add manager to application
app.add_backend(Vkontakte(token=config["vk_token"]))
# app.add_backend(Telegram(token=config["tg_token"]))

# Load and register plugins
app.add_plugins(load_plugins("plugins/"))

if __name__ == "__main__":
    # Run application
    app.run()
