import { createHash } from "node:crypto";
import {
  cpSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  renameSync,
  rmSync,
} from "node:fs";
import { dirname, join, relative, resolve, sep } from "node:path";
import { fileURLToPath } from "node:url";

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const source = resolve(repositoryRoot, "apps/desktop/dist");
const target = resolve(repositoryRoot, "src/paradev/resources/gui");
const targetParent = dirname(target);
const expectedParent = resolve(repositoryRoot, "src/paradev/resources");
const check = process.argv.includes("--check");

if (targetParent !== expectedParent || !target.startsWith(`${expectedParent}${sep}`)) {
  throw new Error(`refusing to sync outside ParaDev package resources: ${target}`);
}
if (!existsSync(join(source, "index.html"))) {
  throw new Error(`desktop build is missing: ${source}; run npm build first`);
}

function inventory(root) {
  const rows = new Map();
  const visit = (directory) => {
    for (const entry of readdirSync(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) {
        visit(path);
      } else if (entry.isFile()) {
        const key = relative(root, path).split(sep).join("/");
        rows.set(key, createHash("sha256").update(readFileSync(path)).digest("hex"));
      }
    }
  };
  if (existsSync(root)) {
    visit(root);
  }
  return rows;
}

function equal(left, right) {
  return left.size === right.size && [...left].every(([key, value]) => right.get(key) === value);
}

if (check) {
  if (!equal(inventory(source), inventory(target))) {
    throw new Error("packaged GUI assets are stale; run npm build in apps/desktop");
  }
  console.log(`[sync-gui] checked ${inventory(source).size} packaged files`);
  process.exit(0);
}

mkdirSync(targetParent, { recursive: true });
const temporary = resolve(targetParent, `.gui-sync-${process.pid}`);
const previous = resolve(targetParent, `.gui-previous-${process.pid}`);
rmSync(temporary, { recursive: true, force: true });
rmSync(previous, { recursive: true, force: true });
cpSync(source, temporary, { recursive: true });

try {
  if (existsSync(target)) {
    renameSync(target, previous);
  }
  renameSync(temporary, target);
  rmSync(previous, { recursive: true, force: true });
} catch (error) {
  if (!existsSync(target) && existsSync(previous)) {
    renameSync(previous, target);
  }
  rmSync(temporary, { recursive: true, force: true });
  throw error;
}

console.log(`[sync-gui] packaged ${inventory(target).size} files`);
