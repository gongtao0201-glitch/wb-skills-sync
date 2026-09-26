// 把 assets/template.html + scenes.json + gsap.min.js 打包成一个自包含 HTML（可离线播放 / 供渲染器逐帧截图）
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dir = dirname(fileURLToPath(import.meta.url));
const SKILL = resolve(__dir, "..");

const [, , scenesPath, outPath] = process.argv;
if (!scenesPath || !outPath) {
  console.error("用法: node build_html.mjs <scenes.json> <out.html>");
  process.exit(1);
}

const tpl = readFileSync(join(SKILL, "assets", "template.html"), "utf8");
const gsap = readFileSync(join(SKILL, "assets", "gsap.min.js"), "utf8");
const data = JSON.parse(readFileSync(resolve(scenesPath), "utf8"));

const scenes = data.scenes;
const meta = {
  badge: data.badge || "五鼎源 × 老歌哥",
  foot: data.foot || "",
  skin: data.skin || "tech",
  orient: data.orient || "landscape"
};

const orient = data.orient === "portrait" ? "portrait" : "landscape";
const W = orient === "portrait" ? 1080 : 1920;
const H = orient === "portrait" ? 1920 : 1080;

let html = tpl
  .replace("/*__SCENES__*/[]", JSON.stringify(scenes))
  .replace(/\/\*__META__\*\/\{[^}]*\}/, JSON.stringify(meta))
  .replace('data-orient="landscape"', `data-orient="${orient}"`)
  .replace('data-w="1920" data-h="1080"', `data-w="${W}" data-h="${H}"`)
  .replace('<script src="gsap.min.js"></script>', `<script>${gsap}</script>`);

if (!html.includes('"orient"')) { console.error("[build] ⚠️ META 替换失败，模板占位符不匹配"); process.exit(1); }

mkdirSync(dirname(resolve(outPath)), { recursive: true });
writeFileSync(resolve(outPath), html, "utf8");

const total = scenes.reduce((s, x) => s + (x.dur || 5), 0);
console.log(`[build] ${resolve(outPath)}`);
console.log(`[build] 场景 ${scenes.length} 幕 / 总时长 ${total.toFixed(2)}s / 30fps = ${Math.round(total * 30)} 帧`);
