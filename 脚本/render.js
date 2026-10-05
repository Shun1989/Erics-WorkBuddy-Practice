// 渲染 SVG / HTML 为 PNG、PDF。用法：
//   node 脚本/render.js shot  <file.svg|file.html> <out.png>
//   node 脚本/render.js pdf   <file.html> <out.pdf>
const { chromium } = require('playwright');
const path = require('path');

const CHROME = process.env.CHROME_PATH ||
  'C:/Users/guoyu/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe';
const LAUNCH = { executablePath: CHROME };
(async () => {
  const [mode, input, out] = process.argv.slice(2);
  const url = 'file:///' + path.resolve(input).replace(/\\/g, '/');
  const browser = await chromium.launch(LAUNCH);
  if (mode === 'shot') {
    const page = await browser.newPage({ viewport: { width: 1000, height: 650 }, deviceScaleFactor: 1 });
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForTimeout(300);
    await page.screenshot({ path: out });
  } else if (mode === 'pdf') {
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForTimeout(500);
    await page.emulateMedia({ media: 'print' });
    await page.pdf({
      path: out, format: 'A4', printBackground: true,
      margin: { top: '0mm', bottom: '0mm', left: '0mm', right: '0mm' },
      displayHeaderFooter: false,
    });
  } else if (mode === 'shots') {
    // shots <dir> <outprefix>  —— 一个浏览器批量渲染目录内所有 svg
    const fs = require('fs');
    const dir = path.resolve(input);
    const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg')).sort();
    const browser2 = await chromium.launch(LAUNCH);
    const page = await browser2.newPage({ viewport: { width: 1000, height: 650 } });
    for (const f of files) {
      await page.goto('file:///' + path.join(dir, f).replace(/\\/g, '/'), { waitUntil: 'load' });
      await page.screenshot({ path: path.join(out, f.replace('.svg', '.png')) });
    }
    await browser2.close();
    console.log('shots:', files.length);
    return;
  } else if (mode === 'pagemap') {
    // 输出每个 #sec-N 锚点所在 PDF 页码 -> toc_pages.json
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'load' });
    await page.waitForTimeout(500);
    await page.emulateMedia({ media: 'print' });
    const tmp = out + '.tmp.pdf';
    await page.pdf({ path: tmp, format: 'A4', printBackground: true, margin: { top: '0mm', bottom: '0mm', left: '0mm', right: '0mm' } });
    const map = await page.evaluate(() => {
      const res = {};
      const pageH = 1122.5; // A4 @96dpi ≈ 297mm
      document.querySelectorAll('[id^="sec-"]').forEach(el => {
        const y = el.getBoundingClientRect().top + window.scrollY;
        res[el.id] = Math.floor(y / pageH) + 1;
      });
      return res;
    });
    require('fs').writeFileSync(out, JSON.stringify(map, null, 0), 'utf-8');
    console.log('pagemap entries:', Object.keys(map).length);
  }
  await browser.close();
})();
