<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta name="theme-color" content="#00FF88">
<title>BEXIA v4.0</title>
<link rel="icon" href="https://i.imgur.com/8QmQd5a.png">
<style>
*{box-sizing:border-box}body{margin:0;background:#000;color:#fff;font-family:monospace;display:flex;flex-direction:column;height:100vh}
#h{text-align:center;padding:22px;border-bottom:1px solid #111}
#av{width:108px;height:108px;border-radius:50%;border:2px solid #00FF88;box-shadow:0 0 20px #00FF8855}
#st{color:#00FF88;margin-top:10px;font-weight:bold;letter-spacing:1px}
#sub{font-size:10px;color:#666;margin-top:4px}
#chat{flex:1;overflow-y:auto;padding:16px;padding-bottom:90px}
.b{padding:12px 14px;border-radius:18px;margin:8px 0;max-width:85%;line-height:1.4;font-size:14px}
.u{background:#00FF88;color:#000;margin-left:auto;border-bottom-right-radius:4px}
.bx{background:#161616;color:#eee;border-bottom-left-radius:4px;border:1px solid #222}
#in{position:fixed;bottom:0;left:0;right:0;display:flex;padding:12px;background:linear-gradient(transparent,#000 30%);gap:10px}
#txt{flex:1;background:#161616;color:#fff;border:1px solid #222;padding:13px 16px;border-radius:25px;outline:none}
#btn{background:#00FF88;border:0;width:48px;height:48px;border-radius:50%;font-weight:bold;font-size:18px}
#dot{display:inline-block;width:8px;height:8px;background:#00FF88;border-radius:50%;margin-right:6px;box-shadow:0 0 8px #00FF88;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
</style>
<link id="manifestLink" rel="manifest" href="">
</head>
<body>
<div id="h">
<img id="av" src="https://i.imgur.com/8QmQd5a.png" alt="BEXIA">
<div id="st"><span id="dot"></span>BEXIA v4.0 - SYSTEM ONLINE</div>
<div id="sub">NEURAL LINK 98.7% | MOTOR: INFINITO | VOZ: ACTIVA</div>
</div>
<div id="chat">
<div class="b bx">Hola, soy BEXIA v4.0. Tu clon de Meta AI con memoria infinita. ¿En qué te ayudo?</div>
</div>
<div id="in">
<input id="txt" placeholder="Habla con Bexia..." onkeydown="if(event.key==='Enter')enviar()">
<button id="btn" onclick="enviar()">></button>
</div>
<script>
// PWA MANIFEST EMBEBIDO - hace que sea instalable como APK
const manifest = {
  name:"BEXIA v4.0",
  short_name:"BEXIA",
  start_url:".",
  display:"standalone",
  background_color:"#000000",
  theme_color:"#00FF88",
  icons:[{src:"https://i.imgur.com/8QmQd5a.png",sizes:"512x512",type:"image/png"}]
};
const blob = new Blob([JSON.stringify(manifest)], {type:'application/json'});
document.getElementById('manifestLink').href = URL.createObjectURL(blob);

// CAMBIA ESTA IP POR LA TUYA - Ej: 192.168.1.10
const API_URL = "http://192.168.1.10:8000/app/chat";

async function enviar(){
  let t=document.getElementById('txt').value.trim(); if(!t) return;
  let c=document.getElementById('chat');
  c.innerHTML+=`<div class="b u">${t}</div>`;
  document.getElementById('txt').value=''; c.scrollTop=c.scrollHeight;
  try{
    let r=await fetch(API_URL,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});
    let d=await r.json();
    c.innerHTML+=`<div class="b bx">${d.bexia||d.reply||'Error de link neural'}</div>`;
  }catch(e){
    c.innerHTML+=`<div class="b bx" style="border-color:#ff4444">⚠️ No conecto al cerebro local.<br>Corre en tu PC:<br><b>python bexia_v4_final.py</b><br>y cambia la IP en el código.</div>`;
  }
  c.scrollTop=c.scrollHeight;
}
if('serviceWorker' in navigator){ navigator.serviceWorker.register('data:text/javascript,'); }
</script>
</body>
</html>
