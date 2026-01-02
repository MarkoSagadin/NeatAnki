import { writeFileSync, mkdirSync } from "fs";
import path from "path";
import * as sass from "sass";

const theme_paths = process.argv.slice(2);

if (theme_paths.length === 0) {
  console.error("missing theme path(s)");
  console.error("usage: node build_theme.js <path1> [path2] [path3] ...");
  process.exit(1);
}

mkdirSync("dist", { recursive: true });

for (const theme_path of theme_paths) {
  console.log(`Building ${theme_path}...`);

  const result = sass.compile(theme_path, {
    style: "compressed",
  });

  const out_path = path.join("dist", path.parse(theme_path).name + ".css");

  writeFileSync(out_path, result.css);
  console.log(`  → ${out_path}`);
}

await Bun.build({
  entrypoints: ["src/main.js"],
  outdir: "dist",
  minify: true,
  bundle: true,
});
