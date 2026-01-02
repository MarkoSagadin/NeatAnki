# Frontend

This folder contains JS, CSS and Sass files used for styling the Anki cards.

## Structure and output

Styling is separated into three logical components:

- Themes, located inside the `src/themes`. These components dictate the
  colorschemes of paragraphs, headers and code blocks.
- Layout, located inside the `src`, consisting of various `.sass` files. They
  specify the layout, base rules, font size, screen-size dependent behaviour,
  etc.
- JavaScript logic, located in the `src/main.js`. It is small, as not much is
  needed.

After running one of the build commands (see below section), the generated files
will appear in the `dist`.

<!-- TODO: Write how the files in the build folder can be used once you figure out the workflow with
the apkg packages. -->

## Building

Install [Bun](https://bun.com/) tool.

Run one of the below commands from inside the `frontend` directory.

```bash
# Build CSS file for a single theme
bun build_theme.js <path to sass theme file>

# Build CSS files for all themes
bun build_theme.js src/themes/*.sass
```

A generated `dist` folder will be created with:

- a minified `main.js` (generated from `src/main.js`)
- one or more minified CSS files, created from combining layout components with
  one of the themes in the `src/themes` folder.

## Themes

Themes are located in the `src/themes` folder. Various `.sass` files found in it
act as a entry point for the generation of the final CSS file. They include both
the specific colorschemes (found in the `components/` dir) as well as the main
`src/main.sass` file.

Generally there are two kinds of themes:

- Singular, either a light or a dark theme. `tokyonight_day.sass` and
  `tokyonight_storm`, respectively, are an example of that.
- Dual, where both light and dark theme are combined. `tokyonight_dual.sass` is
  an example of that.

## Testing

One will often want to see how the generated CSS files will look applied to some
Anki cards. Folder `test_htmls` contains several html files that show cases
various Anki cards. You can double click on any of them to open it in the
browser of your choice or open them from the command line, for example with
`firefox test_htmls/basic.html`.

<!-- prettier-ignore -->
> [!NOTE]
> All test files by default reference the `tokyonight_day.css` theme. If
> you want to test some other theme, you will need to change the path in the html file.

### Dual themes

Dual themes don't function correctly in the browser, since always the light
theme will be show. That is because there is no way to switch between them like
it is in Anki.

If you want to test dark themes then directly reference them.
