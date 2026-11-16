const {chromium}=require('playwright');
const csstree=require('css-tree');
const fs=require('fs');
const path=require('path');
const {pathToFileURL}=require('url');
const assert=require('assert');
(async()=>{
 const css=fs.readFileSync(path.join(__dirname,'lavender-refresh.css'),'utf8');
 csstree.parse(css);
 const report={scope:'Independent CSS previews and fixture patching only. The original EDS app was not accessed or tested.',css_parse:'PASS',viewports:[],original_app_tested:false};
 const browser=await chromium.launch({headless:true});
 const out=path.resolve(__dirname,'../deliverables');
 fs.mkdirSync(out,{recursive:true});
 for(const kind of ['input','result']){
  for(const width of [1536,1280,900,390]){
   const page=await browser.newPage({viewport:{width,height:960},deviceScaleFactor:1});
   const errors=[];
   page.on('pageerror',e=>errors.push(String(e)));
   await page.goto(pathToFileURL(path.join(__dirname,kind+'-preview.html')).href);
   await page.evaluate(()=>document.fonts.ready);
   const metrics=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:window.innerWidth,heading:getComputedStyle(document.querySelector('h1')).fontSize}));
   assert(metrics.scroll<=width+1,kind+' body horizontal overflow at '+width+': '+JSON.stringify(metrics));
   assert.equal(errors.length,0);
   if(kind==='result'){
    const colors=await page.evaluate(()=>({
      normal:getComputedStyle(document.querySelector('#cmp-matrix thead tr:first-child th:nth-child(2)')).backgroundColor,
      defect:getComputedStyle(document.querySelector('#cmp-matrix thead tr:nth-child(2) th:nth-child(2)')).backgroundColor
    }));
    assert.notEqual(colors.normal,colors.defect,'Normal-only highlight must not spread to a defect column');
   }
   report.viewports.push({page:kind,width,body_horizontal_overflow:false,browser_errors:0});
   if(width===1536){
    const name=kind==='input'?'EDS_CSS_Input_Preview.png':'EDS_CSS_Result_Preview.png';
    await page.screenshot({path:path.join(out,name),fullPage:true});
   }
   await page.close();
  }
 }
 await browser.close();
 fs.writeFileSync(path.join(out,'CSS_Preview_Verification.json'),JSON.stringify(report,null,2));
 console.log('EDS_SAFE_REPORT '+JSON.stringify(report));
 for(const name of ['EDS_CSS_Input_Preview.png','EDS_CSS_Result_Preview.png']){
  console.log('EDS_IMAGE_BEGIN '+name);
  console.log(fs.readFileSync(path.join(out,name)).toString('base64'));
  console.log('EDS_IMAGE_END');
 }
})().catch(e=>{console.error(e);process.exit(1);});
