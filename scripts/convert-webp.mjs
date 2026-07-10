import sharp from "sharp";
import { readdir } from "node:fs/promises";
import path from "node:path";

const publicDir = path.join(process.cwd(), "public");

const files = await readdir(publicDir);
const pngs = files.filter((f) => f.toLowerCase().endsWith(".png"));

console.log(`Found ${pngs.length} PNG files. Converting to WebP...`);

for (const file of pngs) {
  const input = path.join(publicDir, file);
  const output = path.join(publicDir, file.replace(/\.png$/i, ".webp"));
  try {
    await sharp(input)
      .webp({ quality: 90, effort: 6 })
      .toFile(output);
    console.log(`✓ ${file} -> ${path.basename(output)}`);
  } catch (err) {
    console.error(`✗ ${file}: ${err.message}`);
  }
}

console.log("Done.");
