# Player Matchup Display

A graphical web page that displays player vs player matchups with dynamic updates.

## Files

- **index.html** - Main HTML page with the visual display
- **matchup.js** - JavaScript logic for loading and updating player data
- **players.json** - Player database with names and profile pictures

## How to Use

1. Open `index.html` in a web browser
2. Use the control panel at the top to enter player IDs
3. Click "Update Matchup" or press Enter to update the display

## Customizing Players

Edit `players.json` to add or modify players:

```json
{
    "id": 11,
    "name": "Player Name",
    "image": "url-to-image"
}
```

### Image Options

- Use your own image URLs
- Use placeholder services like `https://i.pravatar.cc/200?img=X` (replace X with a number)
- Use local images by placing them in the same folder and referencing them like `"image": "player11.jpg"`

## Example

To display Player 4 vs Player 6:
1. Enter `4` in Player 1 ID field
2. Enter `6` in Player 2 ID field
3. Click "Update Matchup"

The page will automatically display Emily Davis vs Jessica Garcia with their profile pictures.
