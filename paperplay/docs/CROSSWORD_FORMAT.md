# Crossword JSON format (schemaVersion 1)

PaperPlay crosswords are stored as JSON files.

## Top-level fields
- **schemaVersion**: integer (currently `1`)
- **title**: string
- **author**: string
- **width**: integer
- **height**: integer
- **blocks**: `height` × `width` booleans (`true` = block)
- **solution**: `height` × `width` strings (`\"A\"..\"Z\"` or `\"\"` for empty). Blocks should be `\"\"`.
- **cluesAcross**: object mapping clue numbers to clue text
- **cluesDown**: object mapping clue numbers to clue text

## Notes
- Clue numbering is computed from the `blocks` grid using standard crossword rules.\n  A number appears where an entry **starts** (Across and/or Down) and the entry length is at least 2.\n- `cluesAcross` / `cluesDown` keys are written as strings in JSON (because JSON object keys are strings), but are interpreted as integers.

## Example
```json
{
  \"schemaVersion\": 1,
  \"title\": \"Sample 7×7\",
  \"author\": \"PaperPlay\",
  \"width\": 7,
  \"height\": 7,
  \"blocks\": [[false,false,false,true,false,false,false]],
  \"solution\": [[\"S\",\"U\",\"N\",\"\",\"S\",\"K\",\"Y\"]],
  \"cluesAcross\": {\"1\": \"Star at the center of our solar system\"},
  \"cluesDown\": {\"1\": \"Opposite of moon (in this puzzle's theme)\"}
}
```

