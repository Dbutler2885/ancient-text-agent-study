"""Manual word windows, reproducible spacing measurements, and explicit text alignment.

The reference text is consulted only at this stage, after image-only readings.
Token windows are manual annotations, not automatic recognition or stroke masks.
"""
from pathlib import Path
import hashlib
import json
import re
import unicodedata
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site/evidence'
findings = json.loads((ROOT/'analysis/findings.json').read_text())
im = Image.open(OUT/'source.png').convert('RGB')
gray = np.asarray(im.convert('L'))

# Each entry follows right-to-left reading order. Boxes are approximate word
# windows; ascenders and adjacent marks may overlap them.
WORDS = {
 'S01': [('אלהים',(835,280,1010,389)),('את',(750,310,835,377)),('השמים',(552,300,748,376)),('ואת',(440,294,552,366)),('הארץ',(281,292,440,368))],
 'S02': [('ב̣ר̣א̣',(1030,345,1180,418))],
 'S03': [('ורוח',(885,404,1030,472)),('אלהים',(708,372,885,471)),('מרחפת',(512,395,708,463)),('על',(425,350,506,445)),('פני',(348,392,430,452)),('המים',(174,375,348,460))],
 'S04': [('◊[…]הים',(869,464,1098,536)),('את',(772,462,865,522)),('האור',(621,462,773,522)),('כי',(554,463,619,522)),('טוב',(439,455,556,515)),('ויבדל',(279,435,438,519)),('אלה[…]',(165,432,278,498))],
 'S05': [('אלהים',(705,505,875,611)),('לאור',(573,503,704,603)),('יומם',(416,530,560,598)),('ולחשך',(244,493,416,602)),('קר[…]',(170,516,244,596))],
 'S06': [('ויקרא',(1035,574,1200,645))],
 'S07': [('יום',(1092,656,1194,730)),('אחד',(992,651,1092,725))],
 'S08': [('ויאמר',(1032,715,1190,782)),('אלהים',(868,688,1032,782)),('יהי',(781,704,874,778)),('רקיע',(652,690,781,781)),('בתוך',(520,688,653,783)),('המים',(352,696,514,789)),('ויהי',(235,716,353,784)),('מב[…]',(163,726,235,792))],
 'S09': [('אלהים',(1014,774,1187,865)),('את',(940,794,1015,859)),('הרקיע',(785,786,940,861)),('ויבדל',(635,751,783,860)),('בין',(553,774,635,853)),('המים',(409,771,553,859)),('אשר',(281,789,409,860)),('מת[…]',(163,794,281,862))],
 'S10': [('מעל',(1061,840,1181,936)),('לרקיע',(917,843,1063,938)),('ויהי',(797,855,917,930)),('כן',(740,852,797,938)),('ויקרא',(567,849,740,938)),('אלהים',(385,833,566,943)),('לרקיע',(211,833,382,943))],
 'S11': [('יום',(1036,946,1157,1025)),('שני',(947,933,1037,1015))],
 'S12': [('וי◊[…]',(1043,1021,1160,1098)),('אלהים',(846,986,1038,1106)),('יקוו',(709,1007,846,1100)),('המים',(552,1014,709,1107)),('מתחת',(399,1019,552,1109)),('לשמים',(200,989,401,1111))],
 'S13': [('ויקרא',(569,1063,744,1159)),('אלהים',(398,1067,572,1171)),('ליבשה',(201,1077,398,1177))],
 'S14': [('כי',(652,1169,709,1233)),('טוב',(550,1169,654,1236))],
 'S15': [('ויא̣◊',(245,1162,365,1248))],
}

# Consonantal transcription of the public-domain Hebrew biblical text on the
# cited page. Pointing, accents, punctuation, and maqaf are removed; verse
# boundaries and ordinary Hebrew prefix spelling are retained.
VERSES = {
 1:'בראשית ברא אלהים את השמים ואת הארץ',
 2:'והארץ היתה תהו ובהו וחשך על פני תהום ורוח אלהים מרחפת על פני המים',
 3:'ויאמר אלהים יהי אור ויהי אור',
 4:'וירא אלהים את האור כי טוב ויבדל אלהים בין האור ובין החשך',
 5:'ויקרא אלהים לאור יום ולחשך קרא לילה ויהי ערב ויהי בקר יום אחד',
 6:'ויאמר אלהים יהי רקיע בתוך המים ויהי מבדיל בין מים למים',
 7:'ויעש אלהים את הרקיע ויבדל בין המים אשר מתחת לרקיע ובין המים אשר מעל לרקיע ויהי כן',
 8:'ויקרא אלהים לרקיע שמים ויהי ערב ויהי בקר יום שני',
 9:'ויאמר אלהים יקוו המים מתחת השמים אל מקום אחד ותראה היבשה ויהי כן',
 10:'ויקרא אלהים ליבשה ארץ ולמקוה המים קרא ימים וירא אלהים כי טוב',
 11:'ויאמר אלהים תדשא הארץ דשא עשב מזריע זרע עץ פרי עשה פרי למינו אשר זרעו בו על הארץ ויהי כן',
}
SOURCE = {'title':'Mechon Mamre, Genesis 1, Hebrew text', 'url':'https://mechon-mamre.org/p/pt/pt0101.htm',
          'consulted':'2026-09-12', 'scope':'Genesis 1:1-11 only',
          'provenance':'Direct page access for the user-requested textual-location layer. No image search or manuscript identification.',
          'normalization':'Consonants only; pointing, cantillation and punctuation removed; maqaf separated into tokens. Consonantal spellings not harmonized to the image.'}

LOCATIONS = {
 'S01':('Genesis 1:1','Strong phrase alignment','The sequence of five visible words matches the end of the verse.'),
 'S02':('Genesis 1:1?','Conditional','If the image-only candidate ברא is right, it precedes S01 in this verse. The text cannot establish its damaged letters or prove a physical join.'),
 'S03':('Genesis 1:2','Strong phrase alignment','The six-word sequence identifies the latter part of the verse.'),
 'S04':('Genesis 1:4','Strong phrase alignment','The middle sequence is distinctive despite damaged words at both ends.'),
 'S05':('Genesis 1:5','Strong phrase alignment; spelling difference','The surrounding words locate the phrase. Image reading יומם differs from reference יום and is not normalized away.'),
 'S06':('Genesis 1:5?','Context-dependent','ויקרא alone also occurs in 1:8 and 1:10. Its placement to the right of S05 favors 1:5.'),
 'S07':('Genesis 1:5','Strong within this passage','The two-word phrase fits the end of the first-day account.'),
 'S08':('Genesis 1:6','Strong phrase alignment','The long surviving sequence fixes the location without completing מב[…].'),
 'S09':('Genesis 1:7','Strong phrase alignment','The eight visible or partial tokens align with the middle of this verse.'),
 'S10':('Genesis 1:7-8','Strong phrase alignment','One physical row crosses the modern verse division: מעל לרקיע ויהי כן | ויקרא אלהים לרקיע.'),
 'S11':('Genesis 1:8','Strong within this passage','The two-word phrase fits the end of the second-day account.'),
 'S12':('Genesis 1:9','Strong phrase alignment; spelling difference','The image reading לשמים differs from reference השמים. The location is supported by the surrounding words.'),
 'S13':('Genesis 1:10','Strong phrase alignment','The three-word phrase identifies the naming of the dry land.'),
 'S14':('Genesis 1:10?','Context-dependent','כי טוב occurs in both 1:4 and 1:10 within the selected range. Its position after S13 favors 1:10.'),
 'S15':('Genesis 1:11?','Weak, sequence-dependent','If ויא̣◊ begins ויאמר and follows the end of 1:10, it could begin 1:11. The short trace cannot identify a verse independently.'),
}

def consonants(value):
    return ''.join(c for c in value if '\u05d0' <= c <= '\u05ea')

def edit_distance(a,b):
    row=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        current=[i]
        for j,y in enumerate(b,1):
            current.append(min(current[-1]+1,row[j]+1,row[j-1]+(x!=y)))
        row=current
    return row[-1]

def cost(observed, reference):
    visible=consonants(observed)
    if not visible:return .5
    # Partial-token compatibility is deliberately weak: a match never supplies
    # missing letters and contributes less independent evidence.
    if '…' in observed or '◊' in observed:
        return .15 if visible in reference else .6 + .4*edit_distance(visible,reference)/max(len(visible),len(reference))
    distance=edit_distance(visible,reference)/max(len(visible),len(reference))
    return .1 + .8*distance if '\u0323' in observed else distance

flat=[{'verse':v,'word':i+1,'text':t} for v,verse in VERSES.items() for i,t in enumerate(verse.split())]
rows=[]
for sid, entries in WORDS.items():
    tokens=[]
    for i,(value,box) in enumerate(entries,1):
        assert 0<=box[0]<box[2]<=im.width and 0<=box[1]<box[3]<=im.height
        wid=f'{sid}.W{i:02}'
        file=f'word-{wid}.png'
        im.crop(box).save(OUT/file)
        status='partial' if ('…' in value or '◊' in value) else 'uncertain' if '\u0323' in value else 'readable'
        tokens.append({'id':wid,'text':value,'box':box,'status':status,'file':file})
    candidates=[]
    for start in range(len(flat)-len(entries)+1):
        window=flat[start:start+len(entries)]
        score=sum(cost(observed,r['text']) for (observed,_),r in zip(entries,window))/len(entries)
        candidates.append({'mean_edit_cost':round(score,4),'start':f"1:{window[0]['verse']}.{window[0]['word']}",
                           'end':f"1:{window[-1]['verse']}.{window[-1]['word']}",'reference_tokens':[r['text'] for r in window]})
    candidates.sort(key=lambda x:x['mean_edit_cost'])
    location,strength,note=LOCATIONS[sid]
    rows.append({'id':sid,'tokens':tokens,'location':location,'strength':strength,'note':note,'candidates':candidates[:5]})

# This narrow band isolates the visible body of the disputed "day" group.
# Low-ink columns are measured rather than equated with word boundaries.
band=[390,545,602,592]
spacing=[]
for threshold in (65,85,105):
    profile=(gray[band[1]:band[3],band[0]:band[2]]<threshold).sum(axis=0)
    low=profile<3
    runs=[]; start=None
    for i,value in enumerate(low.tolist()+[False]):
        if value and start is None:start=i
        if not value and start is not None:
            if i-start>=3:runs.append({'x0':band[0]+start,'x1':band[0]+i,'width':i-start})
            start=None
    spacing.append({'threshold':threshold,'profile':profile.tolist(),'low_ink_runs':runs})

data={'source':SOURCE,'reference_verses':VERSES,'rows':rows,
      'segmentation_method':'Manual orthographic word windows in right-to-left order. These are approximate inspection boxes, not automatic word recognition or exact stroke contours. Adjacent marks can enter a window.',
      'alignment_method':'All equal-token-length contiguous windows within Genesis 1:1-11, ranked by average normalized character edit cost. No insertions/deletions of whole tokens are modelled. Partial/uncertain tokens receive penalties. Costs are NOT probabilities. Short recurring phrases require sequence and physical context.',
      'spacing':{'band':band,'occupancy_rule':'Original grayscale < threshold; low ink means fewer than 3 such pixels in a column; report runs at least 3 columns wide.',
                 'settings':spacing,'conclusion':'The day group has 20-23 low-ink columns to its left and 30-32 to its right in this band. Interior low-ink runs are only 3-6 columns. This supports treating יומם as one graphic word; it does not by itself identify its letters. No internal vertical gap separates the two mem-shaped structures.'},
      'morphology':[{'graphic':'ורוח','parts':'ו + רוח','note':'Prefixed conjunction; one graphic word.'},
                    {'graphic':'לאור','parts':'ל + אור','note':'Prefixed lamed; one graphic word.'},
                    {'graphic':'ולחשך','parts':'ו + ל + חשך','note':'Two prefixes; still one graphic word.'},
                    {'graphic':'לשמים','parts':'ל + שמים','note':'The prefix is part of the visible word, not a separately spaced token.'}],
      'limits':['Verse numbering is modern reference metadata, not visible on this fragment.',
                'Genesis 1:3 is not securely represented among the surviving groups; this does not show that a scribe omitted it.',
                'The alignment does not establish original column width, missing word counts, the fit of restored text in tears, or physical joins.',
                'Apparent differences from the reference text remain provisional image readings, not established manuscript variants.',
                'The quoted text identifies the passage; it does not identify or authenticate the manuscript.']}
(OUT/'word-location-analysis.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

sheet=Image.new('RGB',(1200,((sum(len(r['tokens']) for r in rows)+3)//4)*150),'white')
draw=ImageDraw.Draw(sheet)
index=0
for row in rows:
    for token in row['tokens']:
        x,y=(index%4)*300,(index//4)*150
        draw.text((x+8,y+5),token['id'],fill='black')
        crop=Image.open(OUT/token['file']); crop.thumbnail((284,117))
        sheet.paste(crop,(x+8,y+26));index+=1
sheet.save(OUT/'word-window-atlas.png')
print(json.dumps({'word_windows':index,'physical_groups':len(rows),'spacing':[{ 'threshold':s['threshold'],'runs':s['low_ink_runs']} for s in spacing]}))
