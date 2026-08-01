# Parts filter test matrix

Click through list for the parts filter work. Run it twice, once in each pagination
mode, because the two modes take different code paths to the same query.

**Run 1, client side (the default):** leave `BK_PARTS_SERVER_SIDE_PAGINATION` and
`BK_PROBLEMS_SERVER_SIDE_PAGINATION` unset.

**Run 2, server side:** set both to `true` and restart.

There is also a script that checks the query itself, no clicking needed:

```
python3 scripts/check_part_filters.py [path/to/app.db]
```

It copies your database first and seeds a couple of rows, so nothing is written to
your real data. Needs a database with at least two storages, one owner and one status.

---

## Each filter on its own

Do this on **/parts** and again on **/parts/problem**. Both pages carry the same seven
filters now, so both lists are identical.

| Filter | What to check |
|---|---|
| Owner | Result count drops. Individual parts do not disappear. |
| Color | Result count drops. |
| Theme | Result count drops. Used to do nothing at all. |
| Year | Result count drops. Used to do nothing at all. |
| Storage | Result count drops. Used to do nothing on the problem page and did not exist on the parts page. |
| Tag | Result count drops. Used to do nothing. |
| Status | Result count drops. Brand new. |

For each one also click the `=` button next to it so it flips to `≠`, and check the
result is the opposite selection.

## Storage in particular

- [ ] Pick a storage. Only parts in that storage show.
- [ ] Pick **No storage**. Only parts with nothing assigned show.
- [ ] Storage plus No storage together should cover everything. Pick each in turn and
      the two counts should add up to at least the unfiltered count.
- [ ] A part sitting in a lot that has a storage shows up under that storage, even
      though the part itself has none.
- [ ] Set `≠` on a storage. Parts that only live in that storage disappear, parts that
      also live elsewhere stay.

## Combinations

- [ ] Owner plus storage
- [ ] Storage plus status
- [ ] Theme plus year
- [ ] Storage with `≠` plus owner
- [ ] Every filter at once

Counts should keep shrinking, and nothing should error.

## The awkward cases

- [ ] Filter down to zero results. **The filter bar and the Clear button must still be
      on screen.** This used to hide them and the only way out was editing the URL.
- [ ] From there, click Clear. All seven reset and the full list comes back.
- [ ] `/parts/?page=abc` loads instead of throwing an error.
- [ ] `/parts/?page=0` loads.
- [ ] `/parts/?page=99999` loads and you can navigate back.
- [ ] Search box still works alongside the filters.
- [ ] The Individuals button on /parts still works.

## Pagination mode only (run 2)

- [ ] The count in the footer matches the filtered result, not the unfiltered total.
- [ ] Go to page 2 with a filter on. The filter is still applied.
- [ ] Sorting a column with a filter on keeps the filter.

## Things that should look different after this work

Not bugs, these are the intended corrections:

- [ ] **/parts/problem, pick an owner.** Individual parts now show up. They used to
      vanish completely.
- [ ] **/parts/problem, Figures column.** Shows real numbers. It used to always read 0.
- [ ] **/parts/problem quantities** for parts belonging to an individual minifigure you
      own more than one of. They are now multiplied by how many of that minifigure you
      have, matching what /parts already did.

Everything else should show the same numbers as before.

## Sets regression pass

The sets work only affects server side pagination, which is off by default, so run 2
only. Set `BK_SETS_SERVER_SIDE_PAGINATION=true`.

- [ ] Every filter on /sets still works.
- [ ] Owner and tag filters keep the grouped card view when `BK_SETS_CONSOLIDATION=true`.
      They used to silently switch the page to one card per copy.
- [ ] Status **Missing instructions** combined with a year. The year is now applied.
      It used to be thrown away.
- [ ] Status **Missing instructions** combined with the duplicates button. Same.
- [ ] `≠` works on owner, tag, theme, year, storage and purchase location.
- [ ] The theme dropdown lists the themes of the filtered sets, not of everything.
