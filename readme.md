# Archiver

Archives backups of Discord channels, stores them on disk and restores them to other Discord channels.

# Commands

All commands are bot owner-only.

Commands are detailed in the `help` command.

`archive [channel] [limit]`

Archives a channel, and returns the ID of the archived file.

Parameters:

* `limit` : How many messages to archive. Defaults to 100.
* `channel` : An ID, channel mention or channel name.

`clone [archive ID] [channel]`

Restores an archived channel to an existing Discord channel.

Parameters:

* `archive ID` : The archive to restore. This must be the ID of an existing archive, as returned by `archive` and listed by `list`.
* `channel` : An ID, channel mention or channel name.

Notes:

Due to API limitations, this takes a long time to execute for larger archives.

`list`

Lists existing archives, including archive ID, guild / channel data, archival date, message count.

# Convenience commands

`logout`

Logs out of the client.

`invite`

Returns an invite URL with the required permissions.

# Hosting

The bot requires a `setup.json` file to run. It must contain the following fields:

* `token` : The bot token
* `prefixes` : A list of prefix strings the bot will recognize commands using.

# Details

Logging is done to a `log.txt` file.

Archive files are stored in the format `archives/guilds/[guild ID]/[channel ID]/[archive ID].json`.

Archive files contain the following message data:

* `attachments`: List of attachment references
* `author`: Object containing `id`, `nick` (display name) and `avatar` (reference to an avatar) fields
* `content` : Message content
* `created_at` : Message timestamp
* `embeds` : List of Objects representing embeds. See the discord.py documentation for more.
* `reactions` : List of unicode emoji characters representing message reactions.
* `type`: The message type.

The `attachments` and `avatar` (within `author`) fields will contain references to user avatars and message attachments.

User avatars are stored in the format `archives/users/[user-id].[image-format]`. `image-format` is `gif` for animated avatars and `webp` otherwise. References to avatars are in the format `[user-id].[image-format]`.

Message attachments are stored in the format `archives/guilds/[guild-id]/[channel-id]/data/[attachment-id]_[filename]`. `filename` includes the file format. References to attachments are in the format `[attachment-id]_[filename]`.
