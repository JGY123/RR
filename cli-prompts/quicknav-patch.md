# Quick-Nav Floating Sidebar — Patch Instructions

## What it does
A floating mini-nav on the right edge of the screen showing tile section names.
Click any item to scroll to that section. Active section highlighted as you scroll.
Hidden on mobile (<900px). Fades in on hover.

## CSS to add (before the Plotly modebar hide rule):

```css
.qnav{position:fixed;right:8px;top:50%;transform:translateY(-50%);z-index:90;display:flex;flex-direction:column;gap:2px;opacity:0.35;transition:opacity .2s}
.qnav:hover{opacity:1}
.qnav a{display:block;padding:3px 8px;font-size:8px;color:var(--txt);text-decoration:none;border-right:2px solid transparent;text-align:right;white-space:nowrap;transition:all .15s;letter-spacing:0.3px}
.qnav a:hover{color:var(--txth);border-right-color:var(--pri)}
.qnav a.qnav-active{color:var(--pri);border-right-color:var(--pri);font-weight:600}
@media(max-width:900px){.qnav{display:none}}
```

## HTML to add (right after the opening of #content div):

```html
<nav class="qnav" id="qnav"></nav>
```

## JS to add (inside the upd() function, after rExp()):

```javascript
// Build quick-nav from visible card IDs
function buildQuickNav(){
  let nav=document.getElementById('qnav');
  if(!nav)return;
  let sections=[
    {id:'heroRisk',label:'Risk'},
    {id:'cardSectors',label:'Sectors'},
    {id:'cardFacButt',label:'Factor Map'},
    {id:'cardFacDetail',label:'Factor Detail'},
    {id:'cardCountry',label:'Countries'},
    {id:'cardGroups',label:'Groups'},
    {id:'cardRanks',label:'Ranks'},
    {id:'cardChars',label:'Chars'},
    {id:'cardScatter',label:'Scatter'},
    {id:'cardTreemap',label:'Treemap'},
    {id:'cardMCR',label:'MCR'},
    {id:'cardFRB',label:'Risk Budget'},
    {id:'cardAttrib',label:'Attribution'},
    {id:'cardRegions',label:'Regions'},
  ];
  // Only show sections that exist and are visible
  let visible=sections.filter(s=>{let el=document.getElementById(s.id);return el&&el.offsetHeight>0;});
  nav.innerHTML=visible.map(s=>`<a href="#" onclick="event.preventDefault();document.getElementById('${s.id}')?.scrollIntoView({behavior:'smooth',block:'start'})">${s.label}</a>`).join('');
  
  // Scroll spy: highlight active section
  let observer=new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      let link=nav.querySelector(`a[onclick*="${e.target.id}"]`);
      if(link)link.classList.toggle('qnav-active',e.isIntersecting);
    });
  },{threshold:0.3});
  visible.forEach(s=>{let el=document.getElementById(s.id);if(el)observer.observe(el);});
}
```

Then call `buildQuickNav()` at the end of `upd()` function.

## Also add to tab switch handler
When switching between Exposures/Risk/Holdings tabs, rebuild the nav:
- Exposures: show all sections
- Risk: show Risk-specific sections
- Holdings: hide the nav (or show Holdings-specific items)
