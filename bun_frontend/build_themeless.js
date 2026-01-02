import { writeFileSync, mkdirSync } from "fs";

const sass = require("sass");

mkdirSync("dist", { recursive: true });

const result = sass.compile("src/style/themeless_main.sass", {
  style: "compressed",
});

writeFileSync("dist/main.css", result.css);
