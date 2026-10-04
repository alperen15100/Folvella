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

function renderHome(posts){
  const published=posts.filter(p=>p.status!=="draft");
  const grid=document.getElementById("ideaGrid");
  if(!grid||!published.length)return;
  // Static editorial sections remain available before JS and when data cannot load.
  grid.replaceChildren(...published.map(createCard));
  const empty=document.getElementById("emptyState");
  function applyFilter(){
    const active=document.querySelector("[data-filter].active")?.dataset.filter||"all";
    const q=(document.getElementById("searchInput")?.value||"").trim().toLowerCase();
    let count=0;
    grid.querySelectorAll(".ideaCardWrap").forEach(card=>{
      const show=(active==="all"||card.dataset.cat===active)&&(!q||card.dataset.title.includes(q));
      card.hidden=!show;
      if(show)count++;
    });
    empty.hidden=count>0;
    document.getElementById("searchStatus").textContent=`${count} guide${count===1?"":"s"} found`;
  }
  document.querySelectorAll("[data-filter]").forEach(button=>button.addEventListener("click",()=>{
    document.querySelectorAll("[data-filter]").forEach(b=>{b.classList.toggle("active",b===button);b.setAttribute("aria-pressed",String(b===button))});
    applyFilter();
  }));
  document.getElementById("siteSearch")?.addEventListener("submit",event=>{
    event.preventDefault();applyFilter();
    document.getElementById("fresh")?.scrollIntoView({behavior:window.matchMedia("(prefers-reduced-motion: reduce)").matches?"instant":"smooth"});
  });
  document.getElementById("searchInput")?.addEventListener("input",applyFilter);
  applyFilter();
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