const wordData=DATA.wordLocation;
let currentWordRow=wordData.rows[4],currentWordIndex=2,wordViewBox=null;
for(const row of wordData.rows)$('word-group').add(new Option(row.id+' · '+row.location,row.id));
function drawWords(){
  if(!source.complete||!source.naturalWidth)return;
  const boxes=currentWordRow.tokens.map(t=>t.box);
  const x0=Math.max(0,Math.min(...boxes.map(b=>b[0]))-12),y0=Math.max(0,Math.min(...boxes.map(b=>b[1]))-22);
  const x1=Math.min(source.width,Math.max(...boxes.map(b=>b[2]))+12),y1=Math.min(source.height,Math.max(...boxes.map(b=>b[3]))+12);
  wordViewBox=[x0,y0,x1,y1];
  const canvas=$('word-row');canvas.width=x1-x0;canvas.height=y1-y0;
  canvas.style.width=Math.min((x1-x0)*2,1100)+'px';canvas.style.maxWidth='100%';canvas.style.margin='auto';
  const ctx=canvas.getContext('2d');ctx.drawImage(source,x0,y0,x1-x0,y1-y0,0,0,x1-x0,y1-y0);
  if(!$('word-overlay').checked)return;
  currentWordRow.tokens.forEach((token,i)=>{
    const b=token.box,color=i===currentWordIndex?'#1665bd':token.status==='readable'?'#29995f':'#dda32c';
    ctx.strokeStyle=color;ctx.lineWidth=i===currentWordIndex?3:1.5;ctx.strokeRect(b[0]-x0,b[1]-y0,b[2]-b[0],b[3]-b[1]);
    ctx.fillStyle='#ffffff';ctx.fillRect(b[0]-x0,b[1]-y0-16,35,15);ctx.fillStyle='#13251b';ctx.font='11px system-ui';ctx.fillText('W'+String(i+1).padStart(2,'0'),b[0]-x0+3,b[1]-y0-4);
  });
}
function showWord(row,index=0){
  currentWordRow=row;currentWordIndex=index;$('word-group').value=row.id;
  $('word-buttons').replaceChildren();
  row.tokens.forEach((token,i)=>{const button=document.createElement('button');button.className='btn word-button'+(i===index?' word-active':'');button.setAttribute('aria-pressed',String(i===index));const word=document.createElement('span');word.lang='he';word.className='reading';word.textContent=token.text;const label=document.createElement('small');label.textContent='W'+String(i+1).padStart(2,'0');button.append(word,label);button.onclick=()=>showWord(row,i);$('word-buttons').append(button)});
  const token=row.tokens[index];$('word-crop').src='evidence/'+token.file;text('word-id',token.id);text('word-reading',token.text);text('word-state','Image transcription status: '+token.status);text('word-coordinates','Source window ['+token.box.join(', ')+']');text('word-context',row.location+' · '+row.strength+'. '+row.note);normalizeDotted();drawWords();
}
$('word-group').onchange=()=>showWord(wordData.rows.find(r=>r.id===$('word-group').value));
$('word-overlay').onchange=drawWords;
$('word-row').onclick=e=>{
  if(!wordViewBox)return;const r=e.currentTarget.getBoundingClientRect(),x=wordViewBox[0]+(e.clientX-r.left)/r.width*(wordViewBox[2]-wordViewBox[0]),y=wordViewBox[1]+(e.clientY-r.top)/r.height*(wordViewBox[3]-wordViewBox[1]);
  const matches=currentWordRow.tokens.map((t,i)=>({t,i})).filter(({t})=>x>=t.box[0]&&x<t.box[2]&&y>=t.box[1]&&y<t.box[3]);
  matches.sort((a,b)=>(a.t.box[2]-a.t.box[0])*(a.t.box[3]-a.t.box[1])-(b.t.box[2]-b.t.box[0])*(b.t.box[3]-b.t.box[1]));if(matches.length)showWord(currentWordRow,matches[0].i);
};
function drawSpacing(){
  if(!source.complete||!source.naturalWidth)return;const s=wordData.spacing.settings[Number($('spacing-threshold').value)],ctx=$('spacing-plot').getContext('2d');ctx.clearRect(0,0,1060,400);ctx.fillStyle='white';ctx.fillRect(0,0,1060,400);ctx.imageSmoothingEnabled=false;ctx.drawImage(source,390,530,212,72,0,20,1060,216);
  ctx.fillStyle='#314438';ctx.font='17px system-ui';ctx.fillText('Original context (5×)',10,17);ctx.fillText('Dark-pixel count per column; amber = low-ink runs',10,266);
  for(const run of s.low_ink_runs){ctx.fillStyle='#f9e5af';ctx.fillRect((run.x0-390)*5,280,run.width*5,94)}
  s.profile.forEach((n,i)=>{ctx.fillStyle='#35644f';ctx.fillRect(i*5,374-n*2,4,n*2)});
  ctx.strokeStyle='#6c786f';ctx.beginPath();ctx.moveTo(0,374);ctx.lineTo(1060,374);ctx.stroke();ctx.font='14px system-ui';ctx.fillStyle='#314438';for(const x of [390,430,470,510,550,590])ctx.fillText(String(x),(x-390)*5+2,397);
  text('spacing-runs','Low-ink runs [x start, x end), width: '+s.low_ink_runs.map(r=>'['+r.x0+', '+r.x1+'), '+r.width+' px').join(' · '));
}
$('spacing-threshold').onchange=drawSpacing;
for(const m of wordData.morphology){const tr=document.createElement('tr');for(const [i,value]of [m.graphic,m.parts,m.note].entries()){const td=document.createElement('td');td.textContent=value;if(i<2){td.dir='rtl';td.lang='he'}tr.append(td)}$('morphology').append(tr)}
for(const row of wordData.rows){
  const tr=document.createElement('tr'),group=document.createElement('td'),button=document.createElement('button');button.className='btn btn-xs btn-ghost';button.textContent=row.id;button.onclick=()=>{showWord(row);revealSectionTarget('word-analysis');$('word-analysis').scrollIntoView({behavior:'smooth'})};group.append(button);
  const location=document.createElement('td');location.textContent=row.location;const note=document.createElement('td');const strong=document.createElement('strong');strong.textContent=row.strength;const p=document.createElement('p');p.className='small';p.textContent=row.note;note.append(strong,p);tr.append(group,location,note);$('locations').append(tr);
  const details=document.createElement('details'),summary=document.createElement('summary');summary.textContent=row.id+' · '+row.location;details.append(summary);
  for(const candidate of row.candidates){const p=document.createElement('p');p.className='small';const he=document.createElement('span');he.dir='rtl';he.lang='he';he.textContent=candidate.reference_tokens.join(' | ');p.append(document.createTextNode(candidate.start+' to '+candidate.end+' · cost '+candidate.mean_edit_cost+' · '),he);details.append(p)}$('alignment-details').append(details);
}
text('alignment-method',wordData.alignment_method);
for(const [verse,value]of Object.entries(wordData.reference_verses)){const p=document.createElement('p');p.lang='he';p.dir='rtl';p.className='reference-verse';p.textContent='1:'+verse+'  '+value;$('reference-verses').append(p)}
source.addEventListener('load',()=>{drawWords();drawSpacing()});showWord(currentWordRow,currentWordIndex);drawSpacing();
