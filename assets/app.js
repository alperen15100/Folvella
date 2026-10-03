const IMG={
 halloween:"https://images.unsplash.com/photo-1766186930306-ec2c3f7dbf5f?auto=format&fit=crop&w=1400&q=84",
 coffee:"https://images.unsplash.com/photo-1727911583368-39ce974c566a?auto=format&fit=crop&w=1400&q=84",
 bedroom:"https://images.unsplash.com/photo-1776482128010-a3626efb82f7?auto=format&fit=crop&w=1400&q=84",
 nails:"https://images.unsplash.com/photo-1655720348723-c16f0519249d?auto=format&fit=crop&w=1400&q=84",
 outfit:"https://images.unsplash.com/photo-1583002084130-39730178e1ad?auto=format&fit=crop&w=1400&q=84",
 charms:"https://images.unsplash.com/photo-1763056531605-4e75d78e5016?auto=format&fit=crop&w=1400&q=84"
};

const ARTICLES={
 "halloween-treats":{
  title:"21 Easy Halloween Treats That Look Expensive",category:"Food & Drinks",image:IMG.halloween,
  dek:"Party-ready Halloween desserts that look dramatic on the table without requiring pastry-school skills.",
  intro:"The best Halloween food ideas feel special before anyone takes a bite. These simple styling tricks lean on familiar ingredients, strong contrast and small decorative details so the finished table looks far more complicated than it was.",
  ideas:["Ghost-Dipped Strawberries","Mini Pumpkin Cupcakes","Spiderweb Brownie Bites","Mummy Cookie Sandwiches","Chocolate Pretzel Wands","Pumpkin Patch Cookies","Five-Minute Ghost Bark","Black Cocoa Cupcakes"],
  tip:"Build the table around two or three colors. Orange, black and cream create a polished Halloween look without needing dozens of decorations."
 },
 "fall-coffee":{
  title:"9 Fall Coffee Recipes Better Than a Coffee Shop",category:"Food & Drinks",image:IMG.coffee,
  dek:"Cozy café-style drinks with caramel, maple, cinnamon and dessert-inspired fall flavors.",
  intro:"A good fall coffee should feel rich and seasonal without turning into a sugar bomb. Start with strong coffee or espresso, add one focused flavor, then use texture—cold foam, whipped cream or a dusting of spice—to make it feel café-worthy.",
  ideas:["Maple Cinnamon Iced Latte","Pumpkin Cream Cold Coffee","Brown Sugar Oat Latte","Salted Caramel Mocha","Biscoff Iced Latte","Vanilla Chai Espresso","Cinnamon Roll Coffee","Honey Maple Flat White"],
  tip:"Make syrups in small batches and keep them refrigerated. One homemade syrup can turn an ordinary week of coffee into several different drinks."
 },
 "small-bedroom":{
  title:"30 Small Bedroom Ideas That Make Any Room Look Expensive",category:"Home & Decor",image:IMG.bedroom,
  dek:"Small-space styling tricks that create a calmer, more polished bedroom without a full renovation.",
  intro:"An expensive-looking bedroom is less about buying more and more about controlling proportion, lighting and visual clutter. These ideas use a tight palette, layered textiles and intentional storage to make a small room feel finished.",
  ideas:["Layer the Lighting","Hang Curtains Higher","Use One Oversized Mirror","Choose Full-Length Bedding","Hide Everyday Clutter","Repeat One Metal Finish","Use a Larger Rug","Style the Nightstand in Threes"],
  tip:"The fastest upgrade is usually lighting. Replace a harsh ceiling-only setup with two or three warm light sources at different heights."
 },
 "fall-nails":{
  title:"30 Fall Nail Ideas You’ll Want to Try Right Now",category:"Beauty & Nails",image:IMG.nails,
  dek:"Glossy autumn manicure ideas in chocolate, wine, copper and warm neutral tones.",
  intro:"Fall nails work best when the palette feels seasonal but the shapes stay wearable. Deep browns, burgundy, tortoiseshell and metallic accents can look dramatic without requiring every nail to carry a complicated design.",
  ideas:["Glossy Espresso","Tortoiseshell Accent Nails","Deep Burgundy Almond","Copper Chrome Tips","Caramel French Manicure","Chocolate Aura Nails","Smoky Taupe Gloss","Gold Leaf Accent"],
  tip:"If a full nail-art set feels too busy, keep four nails simple and use one statement nail per hand."
 },
 "fall-outfits":{
  title:"25 Cozy Fall Outfit Ideas You’ll Want to Wear on Repeat",category:"Fashion",image:IMG.outfit,
  dek:"Easy autumn outfits built from warm layers, denim, boots and repeatable neutral pieces.",
  intro:"The most useful fall outfits are the ones you can rebuild from pieces already in your wardrobe. Start with one structured layer, one soft texture and one practical shoe, then let the color palette do the work.",
  ideas:["Barn Jacket + Straight Denim","Camel Coat + Knit Crewneck","Leather Jacket + Wide-Leg Jeans","Oversized Cardigan + White Tee","Trench Coat + Dark Denim","Sweater Vest + Button-Down","Suede Jacket + Black Trousers","Chunky Knit + Midi Skirt"],
  tip:"Choose two base neutrals and one seasonal accent. Repeating that formula makes mixing outfits much easier."
 },
 "bag-charms":{
  title:"25 Cute Bag Charm Ideas to DIY This Fall",category:"DIY & Crafts",image:IMG.charms,
  dek:"Playful charms, bows, beads and tiny handmade details that give an everyday bag more personality.",
  intro:"Bag charms are an easy way to personalize a basic tote or handbag without committing to a new bag. Mix one larger focal piece with one or two smaller textures so the finished cluster feels intentional rather than crowded.",
  ideas:["Crochet Cherry Charm","Velvet Ribbon Bow","Pearl Initial Chain","Mini Fabric Heart","Beaded Flower Loop","Tiny Tassel Stack","Lucky Trinket Cluster","Soft Pom-Pom Clip"],
  tip:"Use lobster clasps or removable rings so you can swap the charm cluster between bags instead of making a permanent change."
 }
};

const order=["halloween-treats","fall-coffee","small-bedroom","fall-nails","fall-outfits","bag-charms"];

function esc(v){return String(v||"").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;")}

function articleUrl(slug){return "article.html?slug="+encodeURIComponent(slug)}

function renderCards(){
 const grid=document.getElementById("ideaGrid"), latest=document.getElementById("latestGrid");
 if(!grid)return;
 const draw=(list)=>{
   grid.innerHTML=list.map(slug=>{const a=ARTICLES[slug];return '<a class="ideaCard" data-cat="'+esc(a.category.split(" ")[0])+'" data-title="'+esc(a.title.toLowerCase())+'" href="'+articleUrl(slug)+'"><img loading="lazy" src="'+a.image+'" alt="'+esc(a.title)+'"><div class="cardText"><small>'+esc(a.category)+'</small><h3>'+esc(a.title)+'</h3><span>Read ideas →</span></div></a>'}).join("");
 };
 draw(order);
 if(latest) latest.innerHTML=order.map(slug=>{const a=ARTICLES[slug];return '<a class="latestCard" href="'+articleUrl(slug)+'"><img loading="lazy" src="'+a.image+'" alt="'+esc(a.title)+'"><div><small>'+esc(a.category.toUpperCase())+'</small><h3>'+esc(a.title)+'</h3><p>5–7 min read</p></div></a>'}).join("");
 const buttons=[...document.querySelectorAll("[data-filter]")];
 function filter(){
   const active=document.querySelector("[data-filter].active")?.dataset.filter||"all";
   const q=(document.getElementById("searchInput")?.value||"").trim().toLowerCase();
   document.querySelectorAll(".ideaCard").forEach(c=>{
     const okCat=active==="all"||c.dataset.cat===active;
     const okQ=!q||c.dataset.title.includes(q);
     c.style.display=okCat&&okQ?"":"none";
   });
 }
 buttons.forEach(b=>b.onclick=()=>{buttons.forEach(x=>x.classList.remove("active"));b.classList.add("active");filter()});
 document.getElementById("siteSearch")?.addEventListener("submit",e=>{e.preventDefault();filter();document.getElementById("fresh")?.scrollIntoView({behavior:"smooth"})});
 document.getElementById("searchInput")?.addEventListener("input",filter);
 const params=new URLSearchParams(location.search);if(params.get("q")){document.getElementById("searchInput").value=params.get("q");filter()}
}

function renderArticle(){
 const mount=document.getElementById("articleMount");if(!mount)return;
 const slug=new URLSearchParams(location.search).get("slug")||"halloween-treats";
 const a=ARTICLES[slug]||ARTICLES["halloween-treats"];
 document.title=a.title+" — Trendora";
 const desc=document.getElementById("pageDescription");if(desc)desc.content=a.dek;
 const blocks=a.ideas.map((idea,i)=>'<section class="ideaBlock"><h2>'+(i+1)+'. '+esc(idea)+'</h2><p>'+esc(idea)+' works because it keeps the idea simple and visually focused. Use what you already have where possible, then add one polished detail that makes the finished result feel intentional.</p>'+(i===1||i===5?'<div class="adbox">ADVERTISEMENT</div>':'')+'</section>').join("");
 const related=order.filter(x=>x!==slug).slice(0,3).map(s=>{const x=ARTICLES[s];return '<a href="'+articleUrl(s)+'"><img loading="lazy" src="'+x.image+'" alt="'+esc(x.title)+'"><b>'+esc(x.title)+'</b></a>'}).join("");
 mount.innerHTML='<section class="articleHero shell"><div class="crumb">'+esc(a.category)+' · IDEAS</div><h1>'+esc(a.title)+'</h1><p class="articleDek">'+esc(a.dek)+'</p><div class="meta">Updated October 2026 · Trendora Editors · 6 min read</div></section><section class="shell articleLayout"><article class="articleMain"><img class="leadImg" src="'+a.image+'" alt="'+esc(a.title)+'"><p class="disclosure"><b>Disclosure:</b> This page may contain affiliate links. If you buy through an eligible link, Trendora may earn a commission at no extra cost to you.</p><p>'+esc(a.intro)+'</p><div class="adbox">ADVERTISEMENT</div><div class="note"><b>Quick tip:</b> '+esc(a.tip)+'</div>'+blocks+'<h2>Save the idea for later</h2><p>The easiest way to use inspiration is to save the combinations that fit your space, taste or routine, then adapt them with items you already own.</p></article><aside class="articleAside"><div class="sideCard"><h3>More to explore</h3><div class="sideLinks">'+order.filter(x=>x!==slug).slice(0,5).map(s=>'<a href="'+articleUrl(s)+'">'+esc(ARTICLES[s].title)+' →</a>').join("")+'</div><div class="adbox">ADVERTISEMENT</div></div></aside></section><section class="related"><div class="shell"><div class="sectionHead"><div><h2>You may also like</h2><p>Keep exploring.</p></div></div><div class="relatedGrid">'+related+'</div></div></section>';
}

const OPS=[
 {slug:"halloween-treats",score:98,stage:"PUBLISH NOW",board:"Halloween Food & Party Ideas",hook:"You can make #7 in 5 minutes →",pin:"21 Easy Halloween Treats That Look Expensive",desc:"Easy Halloween treats that look impressive but are simple to make. Save these spooky dessert ideas for parties, school events and October weekends."},
 {slug:"fall-coffee",score:94,stage:"PUBLISH NOW",board:"Fall Drinks & Coffee Recipes",hook:"You need to try #4 →",pin:"9 Fall Coffee Recipes Better Than a Coffee Shop",desc:"Cozy fall coffee recipes to make at home, from caramel and maple flavors to dessert-style iced coffee."},
 {slug:"fall-nails",score:91,stage:"PUBLISH NOW",board:"Fall Nails & Nail Inspiration",hook:"#12 is the new obsession →",pin:"30 Fall Nail Ideas You’ll Want to Try Right Now",desc:"Fall nail ideas in chocolate, burgundy, copper and warm glossy finishes. Save these designs for your next manicure."},
 {slug:"bag-charms",score:89,stage:"WATCH",board:"DIY Crafts & Cute Projects",hook:"You’ll want to make #3 →",pin:"25 Cute Bag Charm Ideas to DIY This Fall",desc:"Cute DIY bag charm ideas using bows, beads, crochet details and playful trinkets."},
 {slug:"small-bedroom",score:86,stage:"EVERGREEN",board:"Small Bedroom & Home Decor Ideas",hook:"Most people get #7 wrong →",pin:"30 Small Bedroom Ideas That Make Any Room Look Expensive",desc:"Small bedroom decorating ideas that look polished and expensive without a major renovation."},
 {slug:"fall-outfits",score:84,stage:"WATCH",board:"Fall Outfits & Autumn Style",hook:"Outfit #6 is a must →",pin:"25 Cozy Fall Outfit Ideas You’ll Want to Wear on Repeat",desc:"Easy fall outfit ideas with cozy layers, denim, boots and warm neutral tones."}
];

function studio(){
 const q=document.getElementById("studioQueue");if(!q)return;
 q.innerHTML=OPS.map((o,i)=>{const a=ARTICLES[o.slug],url="https://alperen15100.github.io/Trendora/"+articleUrl(o.slug);return '<section class="brief"><div class="briefTop"><div><span class="stage">#'+(i+1)+' · '+o.stage+'</span><h2>'+esc(a.title)+'</h2><small>'+esc(o.board)+'</small></div><span class="score">'+o.score+'/100</span></div><div class="briefGrid"><div class="field"><small>PIN TITLE</small><code>'+esc(o.pin)+'</code><button class="copy" data-copy="'+esc(o.pin)+'">Copy</button></div><div class="field"><small>CREATIVE HOOK</small><code>'+esc(o.hook)+'</code><button class="copy" data-copy="'+esc(o.hook)+'">Copy</button></div><div class="field"><small>DESCRIPTION</small><code>'+esc(o.desc)+'</code><button class="copy" data-copy="'+esc(o.desc)+'">Copy</button></div><div class="field"><small>TARGET URL</small><code>'+esc(url)+'</code><button class="copy" data-copy="'+esc(url)+'">Copy</button></div></div></section>'}).join("");
 document.querySelectorAll("[data-copy]").forEach(b=>b.onclick=async()=>{try{await navigator.clipboard.writeText(b.dataset.copy);const t=b.textContent;b.textContent="Copied ✓";setTimeout(()=>b.textContent=t,1000)}catch(e){}});
}

document.getElementById("newsletterForm")?.addEventListener("submit",e=>{e.preventDefault();document.getElementById("newsletterMsg").textContent="Thanks — you’re on the list.";e.currentTarget.reset()});
if(document.body.dataset.page==="home")renderCards();
if(document.body.dataset.page==="article")renderArticle();
if(document.body.dataset.page==="studio")studio();