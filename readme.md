# Archiver

Takes a Discord channel and archives it onto disk. Stores images and other attachments alongside the archives.

# Commands

`archive [limit] [channel]`

Archives a channel.

Parameters:

`limit`   : Int
`channel` : An ID, channel mention or channel name.

# Details

Archive files are stored in the format `archives/guilds/[guild-id]/[channel-id]/[timestamp].json`.

Archive files contain the following message data:

* `attachments`: List of attachment references
* `author`: Object containing `nick` (display name) and `avatar` (reference to an avatar) fields
* `content` : Message content
* `created_at` : Message timestamp
* `embeds` : List of Objects representing embeds. See the discord.py documentation for more.
* `type`: The message type ID and name.

The `attachments` and `avatar` (within `author`) fields will contain references to user avatars and message attachments.

User avatars are stored in the format `archives/users/[user-id].[image-format]`. `image-format` is `gif` for animated avatars and `webp` otherwise. References to avatars are in the format `[user-id].[image-format]`.

Message attachments are stored in the format `archives/guilds/[guild-id]/[channel-id]/data/[attachment-id]_[filename]`. `filename` includes the file format. References to attachments are in the format `[attachment-id]_[filename]`.