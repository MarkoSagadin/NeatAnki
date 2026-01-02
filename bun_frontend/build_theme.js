import { writeFileSync, mkdirSync } from "fs";
import path from "path";

const sass = require("sass");

const [, , theme_path] = process.argv;

if (!theme_path) {
  console.error("missing theme path");
  process.exit(1);
}

mkdirSync("dist", { recursive: true });

const result = sass.compile(theme_path, {
  style: "compressed",
});

const out_path = path.join("dist", path.parse(theme_path).name + ".css");

writeFileSync(out_path, result.css);
