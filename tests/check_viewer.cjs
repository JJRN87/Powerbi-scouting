// Browser verification for the local review report. Requires Playwright via NODE_PATH.
const {chromium}=require('playwright');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch({headless:true,executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1080}});
    const errors=[]; page.on('pageerror',e=>errors.push(e.message));
    await page.goto(pathToFileURL(path.resolve('outputs/revisar_rankings.html')).href);
    await page.waitForSelector('#results tr');
    const profiles=await page.locator('#profile option').evaluateAll(es=>es.map(e=>e.value));
    let checked=0;
    for(const id of profiles){
      await page.selectOption('#profile',id);
      const compared=await page.evaluate(()=>rendered.map(r=>({score:r.score,base:r.score_base,rank:r.rank,baseRank:r.rank_base})));
      assert(compared.length>0);
      for(const r of compared){assert(Math.abs(r.score-r.base)<1e-7);assert.equal(r.rank,r.baseRank);checked++;}
    }
    await page.selectOption('#profile','organizador');
    assert.equal(await page.locator('#weights input').count(),8);
    const before=await page.locator('#results tr').first().textContent();
    await page.locator('#weights input').evaluateAll(es=>es.forEach(e=>{e.value=0;e.dispatchEvent(new Event('input',{bubbles:true}))}));
    assert(await page.evaluate(()=>rendered.every(r=>r.score===null&&r.rank===null)));
    for(let slot=0;slot<8;slot++){
      await page.locator('#weights input').evaluateAll((es,slot)=>es.forEach((e,i)=>{e.value=i===slot?100:0;e.dispatchEvent(new Event('input',{bubbles:true}))}),slot);
      assert(await page.evaluate(slot=>rendered.every(r=>Math.abs(r.score-r['percentile_'+(slot+1)])<1e-7),slot));
    }
    assert.notEqual(await page.locator('#results tr').first().textContent(),before);
    await page.click('#reset');
    const fourth=page.locator('#results tr').nth(3).locator('button');
    const selectedName=await fourth.textContent();
    await fourth.click();
    assert((await page.locator('#details h2').textContent()).includes(selectedName));
    assert((await page.locator('#details').textContent()).includes('Escenario 40/5'));
    await page.fill('#minimum','3420');
    assert(await page.evaluate(()=>rendered.length===0));
    await page.fill('#minimum','900');
    await page.click('#reset');
    await page.screenshot({path:'outputs/visor-desktop.png',fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
    await page.screenshot({path:'outputs/visor-mobile.png',fullPage:true});
    assert.deepEqual(errors,[]);
    const result={status:'passed',profiles:profiles.length,baseline_candidate_scores:checked,
                  checks:['baseline parity','zero weights','single metric','order changes','selection details','empty filter','mobile width','no JS errors']};
    fs.writeFileSync('outputs/viewer-verification.json',JSON.stringify(result,null,2));
    console.log(JSON.stringify(result));
  } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
