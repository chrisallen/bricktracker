# Environment Variables Reference

## Essential Variables
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_REBRICKABLE_API_KEY` | Rebrickable API key | None | Yes |

## Common Configuration
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_DATABASE_PATH` | SQLite database path | `./app.db` | No |
| `BK_PORT` | Server port | `3333` | No |
| `BK_HOST` | Server host address | `0.0.0.0` | No |
| `BK_DEBUG` | Enable debug mode | `false` | No |
| `BK_USE_REMOTE_IMAGES` | Use remote images | `false` | No |
| `BK_DEFAULT_TABLE_PER_PAGE` | Items per page | `25` | No |
| `BK_TIMEZONE` | Timezone | `Etc/UTC` | No |

## UI Customization
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_HIDE_ADMIN` | Hide admin menu entry | `false` | No |
| `BK_HIDE_ADD_SET` | Hide 'Add' menu entry | `false` | No |
| `BK_HIDE_ADD_BULK_SET` | Hide bulk add option | `false` | No |
| `BK_HIDE_ALL_SETS` | Hide sets menu entry | `false` | No |
| `BK_HIDE_ALL_PARTS` | Hide parts menu entry | `false` | No |
| `BK_HIDE_ALL_MINIFIGURES` | Hide minifigures menu entry | `false` | No |
| `BK_HIDE_ALL_INSTRUCTIONS` | Hide instructions menu entry | `false` | No |
| `BK_HIDE_ALL_PROBLEMS_PARTS` | Hide problems parts menu entry | `false` | No |
| `BK_HIDE_TABLE_MISSING_PARTS` | Hide Missing column in tables | `false` | No |
| `BK_HIDE_TABLE_DAMAGED_PARTS` | Hide Damaged column in tables | `false` | No |
| `BK_HIDE_WISHES` | Hide wishlist menu entry | `false` | No |
| `BK_HIDE_ALL_STORAGES` | Hide storages menu entry | `false` | No |
| `BK_SHOW_GRID_SORT` | Show sort options by default | `false` | No |
| `BK_SHOW_GRID_FILTERS` | Show filter options by default | `false` | No |
| `BK_INDEPENDENT_ACCORDIONS` | Make accordions independent | `false` | No |

## Sort Order Configuration
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_SETS_DEFAULT_ORDER` | Default set sorting | `"rebrickable_sets"."number" DESC` | No |
| `BK_PARTS_DEFAULT_ORDER` | Default part sorting | `"inventory"."name" ASC` | No |
| `BK_MINIFIGURES_DEFAULT_ORDER` | Default minifig sorting | `"minifigures"."name" ASC` | No |
| `BK_WISHES_DEFAULT_ORDER` | Default wishlist sorting | `"bricktracker_wishes"."rowid" DESC` | No |
| `BK_STORAGE_DEFAULT_ORDER` | Default storage sorting | `"bricktracker_metadata_storages"."name" ASC` | No |
| `BK_PURCHASE_LOCATION_DEFAULT_ORDER` | Default purchase location sorting | `"bricktracker_metadata_purchase_locations"."name" ASC` | No |

## Purchase Configuration
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_PURCHASE_CURRENCY` | Currency for purchase prices | `€` | No |
| `BK_PURCHASE_DATE_FORMAT` | Purchase date format | `%d/%m/%Y` | No |
| `BK_FILE_DATETIME_FORMAT` | Date format for files | `%d/%m/%Y, %H:%M:%S` | No |

## External Links Configuration
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_REBRICKABLE_LINKS` | Show Rebrickable links | `false` | No |
| `BK_BRICKLINK_LINKS` | Show BrickLink links | `false` | No |
| `BK_BRICKLINK_LINK_PART_PATTERN` | BrickLink part URL pattern | `https://www.bricklink.com/v2/catalog/catalogitem.page?P={number}` | No |
| `BK_REBRICKABLE_LINK_PART_PATTERN` | Rebrickable part URL pattern | `https://rebrickable.com/parts/{number}/_/{color}` | No |
| `BK_REBRICKABLE_LINK_MINIFIGURE_PATTERN` | Rebrickable minifig URL pattern | `https://rebrickable.com/minifigs/{number}` | No |
| `BK_REBRICKABLE_LINK_INSTRUCTIONS_PATTERN` | Rebrickable instructions URL pattern | `https://rebrickable.com/instructions/{path}` | No |

## File Storage Configuration
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_INSTRUCTIONS_FOLDER` | Instructions storage path | `instructions` | No |
| `BK_MINIFIGURES_FOLDER` | Minifigures storage path | `minifigs` | No |
| `BK_PARTS_FOLDER` | Parts storage path | `parts` | No |
| `BK_SETS_FOLDER` | Sets storage path | `sets` | No |
| `BK_INSTRUCTIONS_ALLOWED_EXTENSIONS` | Allowed instruction file types | `.pdf` | No |

## API and Network Configuration
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_DOMAIN_NAME` | CORS origin restriction | None | No |
| `BK_REBRICKABLE_PAGE_SIZE` | Items per API call | `100` | No |
| `BK_SOCKET_NAMESPACE` | Socket.IO namespace | `bricksocket` | No |
| `BK_SOCKET_PATH` | Socket.IO path | `/bricksocket/` | No |
| `BK_NO_THREADED_SOCKET` | Disable socket threading | `false` | No |
| `BK_REBRICKABLE_USER_AGENT` | Custom User-Agent | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36` | No |

## External Data Sources
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_RETIRED_SETS_FILE_URL` | Retired sets list URL | `https://docs.google.com/spreadsheets/d/1rlYfEXtNKxUOZt2Mfv0H17DvK7bj6Pe0CuYwq6ay8WA/gviz/tq?tqx=out:csv&sheet=Sorted%20by%20Retirement%20Date` | No |
| `BK_RETIRED_SETS_PATH` | Local retired sets file path | `./retired_sets.csv` | No |
| `BK_THEMES_FILE_URL` | Themes list URL | `https://cdn.rebrickable.com/media/downloads/themes.csv.gz` | No |
| `BK_THEMES_PATH` | Local themes file path | `./themes.csv` | No |
| `BK_REBRICKABLE_IMAGE_NIL` | Missing image placeholder | `https://rebrickable.com/static/img/nil.png` | No |
| `BK_REBRICKABLE_IMAGE_NIL_MINIFIGURE` | Missing minifig placeholder | `https://rebrickable.com/static/img/nil_mf.jpg` | No |

## Behavior Configuration
| Variable | Purpose | Default | Required |
|----------|---------|----------|-----------|
| `BK_RANDOM` | Shuffle front page lists | `false` | No |
| `BK_SKIP_SPARE_PARTS` | Ignore spare parts | `false` | No |
| `BK_DATABASE_TIMESTAMP_FORMAT` | Backup timestamp format | `%Y-%m-%d-%H-%M-%S` | No |
| `BK_AUTHENTICATION_KEY` | Secret key for auth tokens | None | If using authentication |
| `BK_AUTHENTICATION_PASSWORD` | Admin area password | None | No |

## Sort Order Examples
```bash
# Sort sets by year ascending
BK_SETS_DEFAULT_ORDER="rebrickable_sets"."year" ASC

# Sort parts by missing count descending
BK_PARTS_DEFAULT_ORDER="total_missing" DESC, "inventory"."name" ASC

# Sort minifigures by ID
BK_MINIFIGURES_DEFAULT_ORDER="minifigures"."fig_num" ASC

# Sort wishlist by set number
BK_WISHES_DEFAULT_ORDER="bricktracker_wishes"."set" ASC
```

## File Extensions Example
```bash
# Allow multiple instruction file types
BK_INSTRUCTIONS_ALLOWED_EXTENSIONS=.pdf, .docx, .png
```