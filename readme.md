# Archiver

Archives backups of Discord channels, stores them on disk and restores them to other Discord channels.

# Commands

`archive [limit] [channel]`

Archives a channel, and returns the name of the archived file.

Parameters:

* `limit` : Int
* `channel` : An ID, channel mention or channel name.

`clone [file] [channel]`

Restores an archived channel.

Parameters:

* `file` : The archive filename to restore. This must be the name of an existing archive, as returned by `archive`.
* `channel` : An ID, channel mention or channel name.

Notes:

Due to API limitations, this takes a long time to execute for larger archives.

# Details

Archive files are stored in the format `archives/guilds/[guild-id]/[channel-id]/[timestamp].json`.

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