from flask import Flask, render_template_string, request, jsonify
from groq import Groq
import os
import requests
from bs4 import BeautifulSoup

# ============= CONFIGURACIÓN =============
class Config:
    NOMBRE = "Prometeo"
    
    # 🔑 Clave: se lee de forma segura desde la nube
    CLAVE_GROQ = os.environ.get("GROQ_API_KEY", "")
    
    # ✅ Modelo vigente en Groq
    MODELO_GROQ = "openai/gpt-oss-20b"
    
    TEMPERATURA = 0.7
    MAX_TOKENS = 600
    BUSCAR_EN_INTERNET = True
    RESULTADOS_MAX = 3

# ============= INICIALIZACIÓN =============
app = Flask(__name__)
config = Config()
cliente_ia = Groq(api_key=config.CLAVE_GROQ)

# ============= 🌐 BÚSQUEDA =============
def buscar_en_web(consulta):
    if not config.BUSCAR_EN_INTERNET:
        return []
    try:
        url = f"https://duckduckgo.com/html/?q={requests.utils.quote(consulta)}"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        sopa = BeautifulSoup(resp.text, "html.parser")
        res = []
        for elem in sopa.find_all("div", class_="result")[:config.RESULTADOS_MAX]:
            tit = elem.find("h2")
            resu = elem.find("a", class_="result__snippet")
            link = elem.find("a", class_="result__url")
            if tit and resu:
                res.append({
                    "titulo": tit.get_text(strip=True),
                    "resumen": resu.get_text(strip=True),
                    "fuente": link.get_text(strip=True) if link else "Web"
                })
        return res
    except Exception as e:
        print(f"Búsqueda: {e}")
        return []

def necesita_busqueda(texto):
    palabras = ["hoy", "ahora", "dólar", "precio", "clima", "tiempo", "noticia", "actual", "cotización", "valor"]
    t = texto.lower()
    return any(p in t for p in palabras)

# ============= 🧠 RESPUESTA =============
def obtener_sistema():
    return f"""Eres {config.NOMBRE}, tu asistente.
- Habla en español claro y natural
- Si hay datos de internet, úsalos y menciona la fuente
- Sé directo, preciso y honesto
- No inventes información que no tengas"""

def responder_pregunta(pregunta):
    contexto = ""
    if necesita_busqueda(pregunta):
        datos = buscar_en_web(pregunta)
        if datos:
            contexto = "\n--- INFORMACIÓN ENCONTRADA ---\n"
            for d in datos:
                contexto += f"• {d['titulo']}\n  {d['resumen']}\n  Fuente: {d['fuente']}\n\n"
    
    mensaje = f"{contexto}Pregunta: {pregunta}" if contexto else pregunta
    
    respuesta = cliente_ia.chat.completions.create(
        model=config.MODELO_GROQ,
        messages=[
            {"role": "system", "content": obtener_sistema()},
            {"role": "user", "content": mensaje}
        ],
        temperature=config.TEMPERATURA,
        max_tokens=config.MAX_TOKENS,
        stream=False
    )
    return respuesta.choices[0].message.content.strip()

# ============= 🎨 INTERFAZ =============
PAGINA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROMETEO — 24/7</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700&family=Rajdhani:wght@400;500;600&display=swap');
        *{margin:0;padding:0;box-sizing:border-box;}
        :root{--fondo:#00050a;--azul:#00ccff;--verde:#00ff88;--naranja:#ff9900;--borde:rgba(0,204,255,.5);}
        body{background:radial-gradient(ellipse at top,#001a33,#00050a);min-height:100vh;font-family:'Rajdhani',sans-serif;color:#e6f0ff;}
        .red{position:fixed;inset:0;background-image:linear-gradient(rgba(0,204,255,.03)1px,transparent 1px),linear-gradient(90deg,rgba(0,204,255,.03)1px,transparent 1px);background-size:40px 40px;pointer-events:none;}
        .cont{max-width:850px;margin:0 auto;padding:20px;position:relative;z-index:2;}
        .cab{text-align:center;padding:20px;margin-bottom:15px;}
        .logo{width:70px;height:70px;margin:0 auto 12px;border-radius:50%;border:2px solid var(--azul);display:flex;align-items:center;justify-content:center;box-shadow:0 0 20px rgba(0,204,255,.4);}
        .logo span{font-family:'Orbitron',sans-serif;font-size:2rem;color:var(--azul);}
        h1{font-family:'Orbitron',sans-serif;font-size:2rem;letter-spacing:4px;color:#fff;margin-bottom:5px;}
        .sub{color:#80b3ff;font-size:.9rem;}
        .barra{display:flex;justify-content:space-between;align-items:center;padding:10px 20px;border:1px solid var(--borde);background:rgba(0,20,40,.6);margin-bottom:15px;border-radius:6px;}
        .punto{width:10px;height:10px;border-radius:50%;background:var(--verde);box-shadow:0 0 8px var(--verde);display:inline-block;margin-right:8px;animation:latido 2s infinite;}
        @keyframes latido{0%,100%{opacity:1}50%{opacity:.4}}
        .panel{border:1px solid var(--borde);background:rgba(0,10,25,.7);height:550px;overflow-y:auto;padding:25px;margin-bottom:15px;border-radius:6px;backdrop-filter:blur(8px);}
        .panel::-webkit-scrollbar{width:5px;}
        .panel::-webkit-scrollbar-thumb{background:var(--azul);border-radius:3px;}
        .mensaje{margin-bottom:25px;animation:entra .4s ease forwards;opacity:0;}
        @keyframes entra{from{opacity:0;transform:translateY(8px)}to{opacity:1}}
        .etq{font-family:'Orbitron',sans-serif;font-size:.75rem;letter-spacing:2px;margin-bottom:6px;opacity:.8;}
        .u .etq{color:var(--azul)}
        .p .etq{color:var(--verde)}
        .txt{padding:14px 18px;border-radius:8px;line-height:1.7;font-size:1rem;}
        .u .txt{background:rgba(0,204,255,.1);border-left:3px solid var(--azul);}
        .p .txt{background:rgba(0,255,136,.08);border-left:3px solid var(--verde);}
        .buscando{color:var(--naranja);padding:10px 15px;background:rgba(255,153,0,.08);border-radius:6px;margin:10px 0;font-style:italic;}
        .entrada{display:flex;gap:12px;align-items:center;border:1px solid var(--borde);background:rgba(0,10,25,.7);padding:18px;border-radius:6px;}
        .campo{flex:1;background:rgba(0,50,100,.15);border:1px solid rgba(0,204,255,.3);color:#fff;padding:14px 20px;font-size:1rem;outline:none;border-radius:4px;}
        .campo:focus{border-color:var(--azul);box-shadow:0 0 12px rgba(0,204,255,.25);}
        .btn{background:linear-gradient(135deg,#0099ff,#0066cc);border:none;color:#fff;padding:14px 30px;font-family:'Orbitron',sans-serif;letter-spacing:2px;cursor:pointer;border-radius:4px;transition:transform .2s;}
        .btn:hover{transform:scale(1.05);}
        .btn:disabled{opacity:.4;transform:none;}
    </style>
</head>
<body>
    <div class="red"></div>
    <div class="cont">
        <div class="cab">
            <div class="logo"><span>P</span></div>
            <h1>PROMETEO</h1>
            <p class="sub">🌐 ACTIVO 24/7 — Desde cualquier lugar</p>
        </div>
        <div class="barra">
            <div><span class="punto"></span><span id="estado">CONECTADO EN LA NUBE</span></div>
            <div id="reloj" style="color:var(--azul);font-family:'Orbitron',sans-serif;font-size:.9rem;"></div>
        </div>
        <div class="panel" id="panel">
            <div class="mensaje p">
                <div class="etq">PROMETEO</div>
                <div class="txt">✅ <strong>FASE 24/7 LISTA</strong><br><br>Estoy en la nube, siempre encendido.<br>Puedes entrar desde tu celular o cualquier equipo.<br><br>¿Qué quieres saber?</div>
            </div>
        </div>
        <div class="entrada">
            <span style="color:var(--azul);font-size:1.3rem;">›</span>
            <input type="text" class="campo" id="texto" placeholder="Escribe tu mensaje...">
            <button class="btn" id="btn" onclick="enviar()">ENVIAR</button>
        </div>
    </div>
    <script>
        let ocupado = false;
        function reloj(){const d=new Date();document.getElementById('reloj').textContent=d.toLocaleString('es-ES',{hour12:false});}
        reloj();setInterval(reloj,1000);
        function bajar(){const p=document.getElementById('panel');p.scrollTop=p.scrollHeight;}
        async function enviar(){
            if(ocupado)return;
            const t=document.getElementById('texto');const txt=t.value.trim();if(!txt)return;
            ocupado=true;t.value='';document.getElementById('btn').disabled=true;
            const panel=document.getElementById('panel');const estado=document.getElementById('estado');
            panel.innerHTML+=`<div class="mensaje u"><div class="etq">TÚ</div><div class="txt">${txt.replace(/</g,'&lt;')}</div></div>`;bajar();
            const buscar=/hoy|precio|dólar|clima|tiempo|noticia|actual/i.test(txt);let aviso;
            if(buscar){estado.textContent='Buscando...';aviso=document.createElement('div');aviso.className='buscando';aviso.textContent='🔍 Buscando en internet...';panel.appendChild(aviso);bajar();}
            else{estado.textContent='Escribiendo...';}
            try{
                const res=await fetch('/responder',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pregunta:txt})});
                const datos=await res.json();
                if(aviso)aviso.remove();
                panel.innerHTML+=`<div class="mensaje p"><div class="etq">PROMETEO</div><div class="txt">${datos.respuesta.replace(/</g,'&lt;')}</div></div>`;
                estado.textContent='✅ Listo';
            }catch(e){estado.textContent='❌ Error';panel.innerHTML+=`<div class="mensaje p"><div class="etq">SISTEMA</div><div class="txt" style="color:#ff6666;">Error de conexión</div></div>`;}
            ocupado=false;document.getElementById('btn').disabled=false;bajar();
        }
        document.getElementById('texto').addEventListener('keydown',e=>e.key==='Enter'&&enviar());
    </script>
</body>
</html>
"""

# ============= RUTAS =============
@app.route('/')
def inicio():
    return render_template_string(PAGINA)

@app.route('/responder', methods=['POST'])
def responder():
    datos = request.json
    pregunta = datos.get('pregunta', '').strip()
    if not pregunta:
        return jsonify({'respuesta': 'No recibí tu mensaje.'}), 400
    texto = responder_pregunta(pregunta)
    return jsonify({'respuesta': texto})

# ============= ARRANQUE =============
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)