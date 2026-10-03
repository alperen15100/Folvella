const SITE_ORIGIN="https://alperen15100.github.io/Trendora/";

function esc(v){return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}
function articleUrl(slug){return "article.html?slug="+encodeURIComponent(slug)}
function absoluteArticleUrl(slug){return SITE_ORIGIN+articleUrl(slug)}

async function loadJSON(path,fallback=[]){
  try{
    const r=await fetch(path,{cache:"no-store"});
    if(!r.ok) throw new Error("HTTP "+r.status);
    return await r.json();
  }catch(e){return fallback}
}
async function getPosts(){return await loadJSON("data/posts.json",[])}

function pinPost(post){
  const payload={
    url:absoluteArticleUrl(post.slug),
    media:post.pinCover||post.cover,
    description:post.pinDescription||post.excerpt||post.title
  };
  if(window.PinUtils&&typeof window.PinUtils.pinOne==="function"){
    window.PinUtils.pinOne(payload);
    return;
  }
  const u="https://www.pinterest.com/pin/create/button/?url="+encodeURIComponent(payload.url)
    +"&media="+encodeURIComponent(payload.media)
    +"&description="+encodeURIComponent(payload.description);
  window.open(u,"_blank","noopener,noreferrer");
}
window.pinPost=pinPost;

function createCard(post){
  const wrap=document.createElement("article");
  wrap.className="ideaCardWrap";
  wrap.dataset.cat=post.category||"Ideas";
  wrap.dataset.title=(post.title||"").toLowerCase();
  wrap.innerHTML='<a class="ideaCard" href="'+articleUrl(post.slug)+'">'
    +'<img loading="lazy" src="'+esc(post.cover)+'" alt="'+esc(post.coverAlt||post.title)+'">'
    +'<div class="cardText"><small>'+esc(post.category||"Ideas")+'</small><h3>'+esc(post.title)+'</h3><span>Read ideas →</span></div>'
    +'</a><button class="pinBubble" type="button" aria-label="Save '+esc(post.title)+' to Pinterest">P</button>';
  wrap.querySelector(".pinBubble").addEventListener("click",()=>pinPost(post));
  return wrap;
}

function renderEmptyHero(){
  const mount=document.getElementById("heroMount");
  if(!mount)return;
  mount.innerHTML='<section class="emptyHero"><div class="shell emptyHeroIn"><span class="eyebrow">TRENDORA</span><h1>Beautiful ideas.<br><em>Worth saving.</em></h1><p>Visual guides for the things people actually want to make, wear, decorate and try.</p></div></section>';
}

function renderHero(post){
  const mount=document.getElementById("heroMount");
  if(!mount)return;
  mount.innerHTML='<section class="hero"><img src="'+esc(post.cover)+'" alt="'+esc(post.coverAlt||post.title)+'"><div class="heroShade"></div><div class="shell heroContent"><span class="eyebrow">'+esc(post.heroLabel||"EDITOR'S PICK")+'</span><h1>'+esc(post.title)+'</h1><p>'+esc(post.excerpt||"")+'</p><div class="heroActions"><a class="cta" href="'+articleUrl(post.slug)+'">View Ideas <span>→</span></a><button class="heroPin" id="heroPin" type="button">P Save</button></div></div></section>';
  document.getElementById("heroPin")?.addEventListener("click",()=>pinPost(post));
}

function renderHome(posts){
  const grid=document.getElementById("ideaGrid");
  if(!grid)return;
  if(!posts.length){
    renderEmptyHero();
    document.getElementById("emptyState").hidden=false;
    document.getElementById("categoryRow").innerHTML="";
    document.getElementById("filters").innerHTML="";
    return;
  }

  const published=posts.filter(p=>p.status!=="draft");
  if(!published.length){renderEmptyHero();return}

  renderHero(published.find(p=>p.featured)||published[0]);
  document.getElementById("emptyState").hidden=true;

  const categories=[...new Set(published.map(p=>p.category).filter(Boolean))];
  document.getElementById("categoryRow").innerHTML=categories.map(cat=>{
    const p=published.find(x=>x.category===cat);
    return '<a href="#fresh" data-category-jump="'+esc(cat)+'"><img src="'+esc(p.cover)+'" alt=""><span>'+esc(cat)+'</span></a>';
  }).join("");

  const filters=document.getElementById("filters");
  filters.innerHTML='<button class="active" data-filter="all">All</button>'+categories.map(c=>'<button data-filter="'+esc(c)+'">'+esc(c)+'</button>').join("");

  grid.innerHTML="";
  published.forEach(p=>grid.appendChild(createCard(p)));

  const latest=document.getElementById("latestGrid");
  latest.innerHTML=published.slice(0,6).map(p=>'<article class="latestCardWrap"><a class="latestCard" href="'+articleUrl(p.slug)+'"><img loading="lazy" src="'+esc(p.cover)+'" alt="'+esc(p.coverAlt||p.title)+'"><div><small>'+esc((p.category||"Ideas").toUpperCase())+'</small><h3>'+esc(p.title)+'</h3><p>'+esc(p.readMinutes||"6")+' min read</p></div></a><button class="pinMini" data-pin-slug="'+esc(p.slug)+'" type="button">P</button></article>').join("");
  document.getElementById("latestSection").hidden=false;

  const popular=document.getElementById("popularCategories");
  popular.innerHTML=categories.slice(0,8).map(cat=>{
    const p=published.find(x=>x.category===cat);
    return '<a href="#fresh" data-category-jump="'+esc(cat)+'"><img src="'+esc(p.cover)+'" alt=""><b>'+esc(cat)+'</b></a>';
  }).join("");
  document.getElementById("popularSection").hidden=false;

  function applyFilter(){
    const active=document.querySelector("[data-filter].active")?.dataset.filter||"all";
    const q=(document.getElementById("searchInput")?.value||"").trim().toLowerCase();
    document.querySelectorAll(".ideaCardWrap").forEach(c=>{
      const cat=c.dataset.cat;
      const title=c.dataset.title;
      c.style.display=((active==="all"||cat===active)&&(!q||title.includes(q)))?"":"none";
    });
  }
  document.querySelectorAll("[data-filter]").forEach(b=>b.addEventListener("click",()=>{
    document.querySelectorAll("[data-filter]").forEach(x=>x.classList.remove("active"));
    b.classList.add("active");applyFilter();
  }));
  document.querySelectorAll("[data-category-jump]").forEach(a=>a.addEventListener("click",()=>{
    const cat=a.dataset.categoryJump;
    const btn=[...document.querySelectorAll("[data-filter]")].find(x=>x.dataset.filter===cat);
    if(btn){btn.click()}
  }));
  document.getElementById("siteSearch")?.addEventListener("submit",e=>{e.preventDefault();applyFilter();document.getElementById("fresh")?.scrollIntoView({behavior:"smooth"})});
  document.getElementById("searchInput")?.addEventListener("input",applyFilter);
  document.querySelectorAll(".pinMini").forEach(b=>b.addEventListener("click",()=>{
    const p=published.find(x=>x.slug===b.dataset.pinSlug);if(p)pinPost(p);
  }));
}

function renderMissingArticle(){
  const mount=document.getElementById("articleMount");
  mount.innerHTML='<section class="legal shell"><span class="eyebrow dark">TRENDORA</span><h1>This story is not published yet.</h1><p>The article may still be in production or the link may be outdated.</p><a class="cta" href="index.html">Back to Trendora →</a></section>';
  document.querySelector('meta[name="robots"]')?.setAttribute("content","noindex,follow");
}

function renderArticle(post,posts){
  document.title=post.title+" — Trendora";
  document.getElementById("pageDescription")?.setAttribute("content",post.excerpt||"");
  const mount=document.getElementById("articleMount");
  const sections=(post.sections||[]).map((s,i)=>{
    const paras=(s.paragraphs||[]).map(p=>'<p>'+esc(p)+'</p>').join("");
    const image=s.image?'<figure class="articleFigure"><img loading="lazy" src="'+esc(s.image)+'" alt="'+esc(s.alt||s.heading||post.title)+'">'+(s.caption?'<figcaption>'+esc(s.caption)+'</figcaption>':'')+'</figure>':"";
    const ad=(i>0&&i%2===1)?'<div class="adbox">ADVERTISEMENT</div>':"";
    return '<section class="longSection"><h2>'+esc(s.heading||"")+'</h2>'+paras+image+ad+'</section>';
  }).join("");

  const related=posts.filter(p=>p.slug!==post.slug&&p.status!=="draft").slice(0,3);
  const relatedHtml=related.map(p=>'<a href="'+articleUrl(p.slug)+'"><img loading="lazy" src="'+esc(p.cover)+'" alt="'+esc(p.coverAlt||p.title)+'"><b>'+esc(p.title)+'</b></a>').join("");

  mount.innerHTML='<section class="articleHero shell"><div class="crumb">'+esc(post.category||"Ideas")+' · GUIDE</div><h1>'+esc(post.title)+'</h1><p class="articleDek">'+esc(post.excerpt||"")+'</p><div class="meta">'+esc(post.dateLabel||"Updated 2026")+' · Trendora Editors · '+esc(post.readMinutes||"8")+' min read</div></section>'
    +'<section class="shell articleLayout"><article class="articleMain">'
    +'<div class="articleCoverWrap"><img class="leadImg" src="'+esc(post.cover)+'" alt="'+esc(post.coverAlt||post.title)+'"><button id="articlePin" class="articlePin" type="button"><b>P</b><span>Save</span></button></div>'
    +'<p class="disclosure"><b>Disclosure:</b> This page may contain affiliate links. If you buy through an eligible link, Trendora may earn a commission at no extra cost to you.</p>'
    +(post.intro||[]).map(p=>'<p>'+esc(p)+'</p>').join("")
    +'<div class="adbox">ADVERTISEMENT</div>'+sections+'</article>'
    +'<aside class="articleAside"><div class="sideCard"><button id="sidePin" class="sidePin" type="button"><b>P</b> Save this guide</button><h3>More to explore</h3><div class="sideLinks">'+related.map(p=>'<a href="'+articleUrl(p.slug)+'">'+esc(p.title)+' →</a>').join("")+'</div><div class="adbox">ADVERTISEMENT</div></div></aside></section>'
    +(related.length?'<section class="related"><div class="shell"><div class="sectionHead"><div><h2>You may also like</h2><p>Keep exploring.</p></div></div><div class="relatedGrid">'+relatedHtml+'</div></div></section>':"");

  document.getElementById("articlePin")?.addEventListener("click",()=>pinPost(post));
  document.getElementById("sidePin")?.addEventListener("click",()=>pinPost(post));
}

async function renderStudio(){
  const q=document.getElementById("studioQueue");if(!q)return;
  const ops=await loadJSON("data/ops.json",[]);
  const posts=await getPosts();
  document.getElementById("studioPublished").textContent=posts.filter(p=>p.status!=="draft").length;
  document.getElementById("studioQueueCount").textContent=ops.length;
  q.innerHTML=ops.length?ops.map((o,i)=>'<section class="brief"><div class="briefTop"><div><span class="stage">#'+(i+1)+' · '+esc(o.stage||"RESEARCHED")+'</span><h2>'+esc(o.title)+'</h2><small>'+esc(o.category||"")+'</small></div><span class="score">'+esc(o.score||"—")+'/100</span></div><div class="briefGrid"><div class="field"><small>PIN HOOK</small><code>'+esc(o.hook||"")+'</code></div><div class="field"><small>ARTICLE ANGLE</small><code>'+esc(o.angle||"")+'</code></div><div class="field"><small>BOARD</small><code>'+esc(o.board||"")+'</code></div><div class="field"><small>STATUS</small><code>'+esc(o.stage||"")+'</code></div></div></section>').join(""):'<div class="brief"><h2>No researched topics in the queue.</h2></div>';
}

document.getElementById("newsletterForm")?.addEventListener("submit",e=>{e.preventDefault();document.getElementById("newsletterMsg").textContent="Thanks — you’re on the list.";e.currentTarget.reset()});

(async()=>{
  const page=document.body.dataset.page;
  if(page==="home")renderHome(await getPosts());
  if(page==="article"){
    const posts=await getPosts();
    const slug=new URLSearchParams(location.search).get("slug");
    const post=posts.find(p=>p.slug===slug&&p.status!=="draft");
    post?renderArticle(post,posts):renderMissingArticle();
  }
  if(page==="studio")renderStudio();
})();