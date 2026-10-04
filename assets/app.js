const SITE_ORIGIN="https://alperen15100.github.io/Trendora/";
const PINTEREST_ICON='<svg class="pinterestSvg" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.758-1.379l-.749 2.848c-.269 1.045-1.004 2.352-1.498 3.146 1.123.345 2.306.535 3.55.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"/></svg>';

function esc(v){return String(v??"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}
function articleUrl(slug){return encodeURIComponent(slug)+"/"}
function absoluteArticleUrl(slug){return SITE_ORIGIN+encodeURIComponent(slug)+"/"}

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
    media:new URL(post.pinCover||post.cover,SITE_ORIGIN).href,
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
    +'</a><button class="pinBubble" type="button" aria-label="Save '+esc(post.title)+' to Pinterest">'+PINTEREST_ICON+'</button>';
  wrap.querySelector(".pinBubble").addEventListener("click",()=>pinPost(post));
  return wrap;
}

function renderEmptyHero(){
  const mount=document.getElementById("heroMount");
  if(!mount)return;
  mount.innerHTML='<section class="emptyHero"><div class="shell emptyHeroIn"><span class="eyebrow">FOLVELLA</span><h1>Beautiful ideas.<br><em>Worth saving.</em></h1><p>Visual guides for the things people actually want to make, wear, decorate and try.</p></div></section>';
}

function renderHeroSlider(posts){
  const mount=document.getElementById("heroMount");
  if(!mount)return;
  const slides=posts.slice(0,5);
  if(!slides.length){renderEmptyHero();return}

  mount.innerHTML='<div class="heroSlider" aria-roledescription="carousel">'
    +slides.map((post,i)=>'<section class="hero heroSlide'+(i===0?' active':'')+'" data-hero-index="'+i+'" '+(i===0?'':'inert')+' aria-hidden="'+(i===0?'false':'true')+'">'
      +'<img '+(i===0?'fetchpriority="high"':'loading="lazy"')+' src="'+esc(post.cover)+'" alt="'+esc(post.coverAlt||post.title)+'">'
      +'<div class="heroShade"></div>'
      +'<div class="shell heroContent">'
        +'<span class="eyebrow">'+esc(post.heroLabel||"EDITOR'S PICK")+'</span>'
        +'<'+(i===0?'h1':'h2')+'>'+esc(post.title)+'</'+(i===0?'h1':'h2')+'>'
        +'<p>'+esc(post.excerpt||"")+'</p>'
        +'<div class="heroActions">'
          +'<a class="cta" href="'+articleUrl(post.slug)+'">View Ideas <span>→</span></a>'
          +'<button class="heroPin" type="button" data-hero-pin="'+i+'" aria-label="Save '+esc(post.title)+' to Pinterest">'+PINTEREST_ICON+'<span>Save</span></button>'
        +'</div>'
      +'</div>'
    +'</section>').join("")
    +'<button class="heroArrow heroPrev" type="button" aria-label="Previous story">‹</button>'
    +'<button class="heroArrow heroNext" type="button" aria-label="Next story">›</button>'
    +'<button class="heroPause" type="button" aria-label="Pause story rotation">Pause</button>'
    +'<div class="heroDots" role="group" aria-label="Latest stories">'
      +slides.map((_,i)=>'<button class="'+(i===0?'active':'')+'" type="button" data-hero-dot="'+i+'" aria-label="Show story '+(i+1)+'"></button>').join("")
    +'</div>'
  +'</div>';

  let current=0;
  let timer=null;
  let paused=false;
  const prefersReduced=window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches;

  function show(next){
    current=(next+slides.length)%slides.length;
    mount.querySelectorAll(".heroSlide").forEach((el,i)=>{
      const active=i===current;
      el.classList.toggle("active",active);
      el.setAttribute("aria-hidden",active?"false":"true");el.inert=!active;
    });
    mount.querySelectorAll("[data-hero-dot]").forEach((el,i)=>el.classList.toggle("active",i===current));
  }

  function start(){
    if(paused||prefersReduced||slides.length<2)return;
    clearInterval(timer);
    timer=setInterval(()=>show(current+1),5000);
  }

  function restart(){show(current);start()}

  mount.querySelectorAll("[data-hero-pin]").forEach(btn=>{
    btn.addEventListener("click",()=>pinPost(slides[Number(btn.dataset.heroPin)]));
  });
  mount.querySelector(".heroPrev")?.addEventListener("click",()=>{show(current-1);start()});
  mount.querySelector(".heroNext")?.addEventListener("click",()=>{show(current+1);start()});
  mount.querySelectorAll("[data-hero-dot]").forEach(btn=>{
    btn.addEventListener("click",()=>{show(Number(btn.dataset.heroDot));start()});
  });

  let touchX=null;
  mount.addEventListener("touchstart",e=>{touchX=e.changedTouches[0]?.clientX??null},{passive:true});
  mount.addEventListener("touchend",e=>{
    if(touchX===null)return;
    const dx=(e.changedTouches[0]?.clientX??touchX)-touchX;
    if(Math.abs(dx)>45){show(current+(dx<0?1:-1));start()}
    touchX=null;
  },{passive:true});

  mount.querySelector(".heroPause")?.addEventListener("click",e=>{paused=!paused;e.currentTarget.textContent=paused?"Play":"Pause";e.currentTarget.setAttribute("aria-label",paused?"Resume story rotation":"Pause story rotation");if(paused)clearInterval(timer);else start()});
  mount.addEventListener("focusin",()=>clearInterval(timer));
  mount.addEventListener("focusout",e=>{if(!mount.contains(e.relatedTarget))start()});
  mount.addEventListener("mouseenter",()=>clearInterval(timer));
  mount.addEventListener("mouseleave",start);
  document.addEventListener("visibilitychange",()=>{if(document.hidden)clearInterval(timer);else start()});
  start();
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

  renderHeroSlider(published);
  document.getElementById("emptyState").hidden=true;

  const categories=[...new Set(published.map(p=>p.category).filter(Boolean))];
  document.getElementById("categoryRow").innerHTML=categories.map(cat=>{
    const p=published.find(x=>x.category===cat);
    return '<a href="category/'+cat.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")+'/"><img src="'+esc(p.cover)+'" alt=""><span>'+esc(cat)+'</span></a>';
  }).join("");

  const filters=document.getElementById("filters");
  filters.innerHTML='<button class="active" aria-pressed="true" data-filter="all">All</button>'+categories.map(c=>'<button aria-pressed="false" data-filter="'+esc(c)+'">'+esc(c)+'</button>').join("");

  grid.innerHTML="";
  published.forEach(p=>grid.appendChild(createCard(p)));

  const latest=document.getElementById("latestGrid");
  latest.innerHTML=published.slice(0,6).map(p=>'<article class="latestCardWrap"><a class="latestCard" href="'+articleUrl(p.slug)+'"><img loading="lazy" src="'+esc(p.cover)+'" alt="'+esc(p.coverAlt||p.title)+'"><div><small>'+esc((p.category||"Ideas").toUpperCase())+'</small><h3>'+esc(p.title)+'</h3><p>'+esc(p.readMinutes||"6")+' min read</p></div></a><button class="pinMini" data-pin-slug="'+esc(p.slug)+'" type="button" aria-label="Save to Pinterest">'+PINTEREST_ICON+'</button></article>').join("");
  document.getElementById("latestSection").hidden=false;

  const popular=document.getElementById("popularCategories");
  popular.innerHTML=categories.slice(0,8).map(cat=>{
    const p=published.find(x=>x.category===cat);
    return '<a href="category/'+cat.toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-|-$/g,"")+'/"><img src="'+esc(p.cover)+'" alt=""><b>'+esc(cat)+'</b></a>';
  }).join("");
  document.getElementById("popularSection").hidden=false;

  function applyFilter(){
    const active=document.querySelector("[data-filter].active")?.dataset.filter||"all";
    const q=(document.getElementById("searchInput")?.value||"").trim().toLowerCase();
    let count=0;
    document.querySelectorAll(".ideaCardWrap").forEach(c=>{
      const cat=c.dataset.cat;
      const title=c.dataset.title;
      c.style.display=((active==="all"||cat===active)&&(!q||title.includes(q)))?"":"none";
      if(c.style.display!=="none")count++;
    });
    document.getElementById("searchStatus").textContent=count?`${count} guide${count===1?"":"s"} found`:"No matching guides. Try another title or category.";
  }
  applyFilter();
  document.querySelectorAll("[data-filter]").forEach(b=>b.addEventListener("click",()=>{
    document.querySelectorAll("[data-filter]").forEach(x=>{x.classList.remove("active");x.setAttribute("aria-pressed","false")});
    b.classList.add("active");b.setAttribute("aria-pressed","true");applyFilter();
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
  mount.innerHTML='<section class="legal shell"><span class="eyebrow dark">FOLVELLA</span><h1>This story is not published yet.</h1><p>The article may still be in production or the link may be outdated.</p><a class="cta" href="index.html">Back to Folvella →</a></section>';
  document.querySelector('meta[name="robots"]')?.setAttribute("content","noindex,follow");
}

function renderArticle(post,posts){
  document.title=post.title+" — Folvella";
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

  mount.innerHTML='<section class="articleHero shell"><div class="crumb">'+esc(post.category||"Ideas")+' · GUIDE</div><h1>'+esc(post.title)+'</h1><p class="articleDek">'+esc(post.excerpt||"")+'</p><div class="meta">'+esc(post.dateLabel||"Updated 2026")+' · Folvella Editors · '+esc(post.readMinutes||"8")+' min read</div></section>'
    +'<section class="shell articleLayout"><article class="articleMain">'
    +'<div class="articleCoverWrap"><img class="leadImg" src="'+esc(post.cover)+'" alt="'+esc(post.coverAlt||post.title)+'"><button id="articlePin" class="articlePin" type="button" aria-label="Save to Pinterest">'+PINTEREST_ICON+'<span>Save</span></button></div>'
    +'<p class="disclosure"><b>Disclosure:</b> This page may contain affiliate links. If you buy through an eligible link, Folvella may earn a commission at no extra cost to you.</p>'
    +(post.intro||[]).map(p=>'<p>'+esc(p)+'</p>').join("")
    +'<div class="adbox">ADVERTISEMENT</div>'+sections+'</article>'
    +'<aside class="articleAside"><div class="sideCard"><button id="sidePin" class="sidePin" type="button" aria-label="Save this guide to Pinterest">'+PINTEREST_ICON+'<span>Save to Pinterest</span></button><h3>More to explore</h3><div class="sideLinks">'+related.map(p=>'<a href="'+articleUrl(p.slug)+'">'+esc(p.title)+' →</a>').join("")+'</div><div class="adbox">ADVERTISEMENT</div></div></aside></section>'
    +(related.length?'<section class="related"><div class="shell"><div class="sectionHead"><div><h2>You may also like</h2><p>Keep exploring.</p></div></div><div class="relatedGrid">'+relatedHtml+'</div></div></section>':"");

  document.getElementById("articlePin")?.addEventListener("click",()=>pinPost(post));
  document.getElementById("sidePin")?.addEventListener("click",()=>pinPost(post));
}



(async()=>{
  const page=document.body.dataset.page;
  if(page==="home"){const posts=await getPosts();if(posts.length)renderHome(posts);}
  if(page==="article"){
    const posts=await getPosts();
    const slug=new URLSearchParams(location.search).get("slug");
    const post=posts.find(p=>p.slug===slug&&p.status!=="draft");
    post?location.replace(articleUrl(post.slug)):renderMissingArticle();
  }
})();