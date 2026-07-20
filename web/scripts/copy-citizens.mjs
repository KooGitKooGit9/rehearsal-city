import { copyFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const src = resolve(__dirname, "../../data/cache/seongsu_citizens.geojson");
const destDir = resolve(__dirname, "../public");
const dest = resolve(destDir, "citizens.geojson");

if (!existsSync(src)) {
  console.error(
    `[copy-citizens] ${src} 파일이 없습니다. 먼저 다음을 실행하세요:\n` +
      "  .venv/bin/python -m engine.generate_population"
  );
  process.exit(1);
}

mkdirSync(destDir, { recursive: true });
copyFileSync(src, dest);
console.log(`[copy-citizens] ${src} -> ${dest}`);
