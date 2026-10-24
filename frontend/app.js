const FALLBACK_LANGS=[
  ["id","Bahasa Indonesia"],["en","English"],["ms","Bahasa Melayu"],["ar","العربية"],["ja","日本語"],
  ["ko","한국어"],["zh","简体中文"],["es","Español"],["pt","Português"],["fr","Français"]
];
let uploadedPath="", currentUser=null, translations={}, gateway=null, capabilities=null;

const I18N_FALLBACK={
  id:{menu:"Menu utama",account:"Akun",login:"Login",register:"Register",logout:"Logout",settings:"Pengaturan",language:"Bahasa",theme:"Tema",notifications:"Notifikasi",save:"Simpan",email:"Email",password:"Password",name:"Nama",login_google:"Login dengan Google",change_password:"Ganti password",current_password:"Password lama",new_password:"Password baru",create_account:"Buat akun",logged_in_as:"Login sebagai",light:"Terang",dark:"Gelap",system:"Sistem",language_count:"10 bahasa tersedia"},
  en:{menu:"Main menu",account:"Account",login:"Login",register:"Register",logout:"Logout",settings:"Settings",language:"Language",theme:"Theme",notifications:"Notifications",save:"Save",email:"Email",password:"Password",name:"Name",login_google:"Login with Google",change_password:"Change password",current_password:"Current password",new_password:"New password",create_account:"Create account",logged_in_as:"Logged in as",light:"Light",dark:"Dark",system:"System",language_count:"10 languages available"},
  ms:{menu:"Menu utama",account:"Akaun",login:"Log masuk",register:"Daftar",logout:"Log keluar",settings:"Tetapan",language:"Bahasa",theme:"Tema",notifications:"Pemberitahuan",save:"Simpan",email:"E-mel",password:"Kata laluan",name:"Nama",login_google:"Log masuk dengan Google",change_password:"Tukar kata laluan",current_password:"Kata laluan semasa",new_password:"Kata laluan baharu",create_account:"Cipta akaun",logged_in_as:"Log masuk sebagai",light:"Cerah",dark:"Gelap",system:"Sistem",language_count:"10 bahasa tersedia"},
  ar:{menu:"القائمة الرئيسية",account:"الحساب",login:"تسجيل الدخول",register:"إنشاء حساب",logout:"تسجيل الخروج",settings:"الإعدادات",language:"اللغة",theme:"السمة",notifications:"الإشعارات",save:"حفظ",email:"البريد الإلكتروني",password:"كلمة المرور",name:"الاسم",login_google:"تسجيل الدخول باستخدام Google",change_password:"تغيير كلمة المرور",current_password:"كلمة المرور الحالية",new_password:"كلمة المرور الجديدة",create_account:"إنشاء حساب",logged_in_as:"تم تسجيل الدخول باسم",light:"فاتح",dark:"داكن",system:"النظام",language_count:"10 لغات متاحة"},
  ja:{menu:"メインメニュー",account:"アカウント",login:"ログイン",register:"登録",logout:"ログアウト",settings:"設定",language:"言語",theme:"テーマ",notifications:"通知",save:"保存",email:"メール",password:"パスワード",name:"名前",login_google:"Googleでログイン",change_password:"パスワード変更",current_password:"現在のパスワード",new_password:"新しいパスワード",create_account:"アカウント作成",logged_in_as:"ログイン中",light:"ライト",dark:"ダーク",system:"システム",language_count:"10言語対応"},
  ko:{menu:"메인 메뉴",account:"계정",login:"로그인",register:"회원가입",logout:"로그아웃",settings:"설정",language:"언어",theme:"테마",notifications:"알림",save:"저장",email:"이메일",password:"비밀번호",name:"이름",login_google:"Google로 로그인",change_password:"비밀번호 변경",current_password:"현재 비밀번호",new_password:"새 비밀번호",create_account:"계정 만들기",logged_in_as:"로그인 계정",light:"라이트",dark:"다크",system:"시스템",language_count:"10개 언어 지원"},
  zh:{menu:"主菜单",account:"账户",login:"登录",register:"注册",logout:"退出登录",settings:"设置",language:"语言",theme:"主题",notifications:"通知",save:"保存",email:"邮箱",password:"密码",name:"姓名",login_google:"使用 Google 登录",change_password:"修改密码",current_password:"当前密码",new_password:"新密码",create_account:"创建账户",logged_in_as:"当前登录",light:"浅色",dark:"深色",system:"系统",language_count:"支持10种语言"},
  es:{menu:"Menú principal",account:"Cuenta",login:"Iniciar sesión",register:"Registrarse",logout:"Cerrar sesión",settings:"Configuración",language:"Idioma",theme:"Tema",notifications:"Notificaciones",save:"Guardar",email:"Correo",password:"Contraseña",name:"Nombre",login_google:"Iniciar sesión con Google",change_password:"Cambiar contraseña",current_password:"Contraseña actual",new_password:"Nueva contraseña",create_account:"Crear cuenta",logged_in_as:"Sesión iniciada como",light:"Claro",dark:"Oscuro",system:"Sistema",language_count:"10 idiomas disponibles"},
  pt:{menu:"Menu principal",account:"Conta",login:"Entrar",register:"Cadastrar",logout:"Sair",settings:"Configurações",language:"Idioma",theme:"Tema",notifications:"Notificações",save:"Salvar",email:"E-mail",password:"Senha",name:"Nome",login_google:"Entrar com Google",change_password:"Alterar senha",current_password:"Senha atual",new_password:"Nova senha",create_account:"Criar conta",logged_in_as:"Conectado como",light:"Claro",dark:"Escuro",system:"Sistema",language_count:"10 idiomas disponíveis"},
  fr:{menu:"Menu principal",account:"Compte",login:"Connexion",register:"Inscription",logout:"Déconnexion",settings:"Paramètres",language:"Langue",theme:"Thème",notifications:"Notifications",save:"Enregistrer",email:"E-mail",password:"Mot de passe",name:"Nom",login_google:"Se connecter avec Google",change_password:"Changer le mot de passe",current_password:"Mot de passe actuel",new_password:"Nouveau mot de passe",create_account:"Créer un compte",logged_in_as:"Connecté en tant que",light:"Clair",dark:"Sombre",system:"Système",language_count:"10 langues disponibles"}
};

function byId(id){return document.getElementById(id)}
function setText(id,value){const el=byId(id);if(el)el.textContent=value}
async function api(url,options={}){
  const controller=new AbortController();
  const timeoutMs=Number(options.timeoutMs||30000);
  const timer=window.setTimeout(()=>controller.abort(),timeoutMs);
  const requestOptions={...options,signal:controller.signal};
  delete requestOptions.timeoutMs;
  try{
    const response=await fetch(url,{credentials:"same-origin",...requestOptions});
    const data=await response.json().catch(()=>({detail:response.statusText||"Request gagal"}));
    if(!response.ok) throw new Error(data.detail||"Request gagal");
    return data;
  }catch(error){
    if(error.name==="AbortError") throw new Error("Request timeout.");
    throw error;
  }finally{
    window.clearTimeout(timer);
  }
}
function languageOptions(select,selected){
  select.innerHTML="";
  FALLBACK_LANGS.forEach(([code,label])=>{
    const option=document.createElement("option");
    option.value=code;option.textContent=label;option.selected=code===selected;
    select.append(option);
  });
}
async function loadTranslations(language){
  try{
    const data=await api("/api/i18n/"+encodeURIComponent(language));
    translations=data.translations||I18N_FALLBACK[language]||I18N_FALLBACK.id;
  }catch{
    translations=I18N_FALLBACK[language]||I18N_FALLBACK.id;
  }
}
function applyTranslations(language){
  translations=translations&&Object.keys(translations).length?translations:(I18N_FALLBACK[language]||I18N_FALLBACK.id);
  document.documentElement.lang=language;
  document.querySelectorAll("[data-i18n]").forEach(el=>{
    const key=el.getAttribute("data-i18n");
    if(translations[key]) el.textContent=translations[key];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el=>{
    const key=el.getAttribute("data-i18n-placeholder");
    if(translations[key]) el.placeholder=translations[key];
  });
  document.documentElement.dir=language==="ar"?"rtl":"ltr";
}
function applyTheme(theme){
  let actual=theme;
  if(theme==="system") actual=window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light";
  document.documentElement.dataset.theme=actual;
  localStorage.setItem("asset_lab_theme",theme);
}
function saveLocalSettings(){
  localStorage.setItem("asset_lab_language",byId("settingsLanguage").value);
  localStorage.setItem("asset_lab_theme",byId("settingsTheme").value);
  localStorage.setItem("asset_lab_notifications",String(byId("settingsNotifications").checked));
}
async function loadAuthStatus(){
  const data=await api("/api/auth/status");
  capabilities=await api("/api/capabilities");
  gateway=await api("/api/gateway/health");
  if(!gateway || gateway.version!==capabilities.version) throw new Error("Gateway dan backend berbeda versi.");
  const langs=data.languages?.length?data.languages:FALLBACK_LANGS.map(x=>x[0]);
  const options=FALLBACK_LANGS.filter(([code])=>langs.includes(code));
  FALLBACK_LANGS.splice(0,FALLBACK_LANGS.length,...options);
  const localLang=localStorage.getItem("asset_lab_language")||"id";
  languageOptions(byId("registerLanguage"),localLang);
  languageOptions(byId("settingsLanguage"),localLang);
  byId("settingsTheme").value=localStorage.getItem("asset_lab_theme")||"light";
  byId("settingsNotifications").checked=localStorage.getItem("asset_lab_notifications")!=="false";
  await loadTranslations(localLang);
  applyTranslations(localLang);
  applyTheme(byId("settingsTheme").value);
  if(!data.google_enabled){
    byId("googleButton").disabled=true;
    byId("googleButton").title="Google Login belum dikonfigurasi oleh administrator.";
  }
}
async function loadMe(){
  try{
    currentUser=await api("/api/auth/me");
    byId("loggedOut").classList.add("hidden");
    byId("loggedIn").classList.remove("hidden");
    byId("passwordSection").classList.remove("hidden");
    byId("accountName").textContent=currentUser.name;
    byId("accountEmail").textContent=currentUser.email;
    byId("accountStatus").textContent=(translations.logged_in_as||"Login sebagai")+" "+currentUser.name;
    byId("avatar").src=currentUser.avatar_url||"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='44'%3E%3Crect width='44' height='44' rx='22' fill='%2316a34a'/%3E%3Ctext x='22' y='28' text-anchor='middle' font-size='18' fill='white'%3E%3F%3C/text%3E%3C/svg%3E";
    byId("settingsName").value=currentUser.name||"";
    byId("settingsLanguage").value=currentUser.language||"id";
    byId("settingsTheme").value=currentUser.theme||"light";
    byId("settingsNotifications").checked=!!currentUser.notifications;
    await loadTranslations(currentUser.language||"id");
    applyTranslations(currentUser.language||"id");
    applyTheme(currentUser.theme||"light");
  }catch{
    currentUser=null;
    byId("loggedOut").classList.remove("hidden");
    byId("loggedIn").classList.add("hidden");
    byId("passwordSection").classList.add("hidden");
  }
}
async function registerUser(){
  try{
    const data=await api("/api/auth/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      name:byId("registerName").value.trim(),email:byId("registerEmail").value.trim(),password:byId("registerPassword").value,language:byId("registerLanguage").value
    })});
    currentUser=data.user;setText("registerResult","Akun berhasil dibuat.");await loadMe();
  }catch(error){setText("registerResult",error.message)}
}
async function loginUser(){
  try{
    const data=await api("/api/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      email:byId("loginEmail").value.trim(),password:byId("loginPassword").value
    })});
    currentUser=data.user;setText("loginResult","Login berhasil.");await loadMe();
  }catch(error){setText("loginResult",error.message)}
}
function googleLogin(){window.location.href="/api/auth/google/start"}
async function logoutUser(){
  try{await api("/api/auth/logout",{method:"POST"});location.reload()}catch(error){setText("accountStatus",error.message)}
}
async function logoutAll(){
  try{await api("/api/auth/logout-all",{method:"POST"});location.reload()}catch(error){setText("accountStatus",error.message)}
}
async function saveSettings(){
  const language=byId("settingsLanguage").value,theme=byId("settingsTheme").value,notifications=byId("settingsNotifications").checked;
  await loadTranslations(language);applyTranslations(language);applyTheme(theme);saveLocalSettings();
  if(!currentUser){setText("settingsResult","Pengaturan lokal tersimpan.");return}
  try{
    const data=await api("/api/auth/settings",{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({language,theme,notifications})});
    currentUser=data.user;
    const profile=byId("settingsName").value.trim();
    if(profile && profile!==currentUser.name){
      const profileData=await api("/api/auth/profile",{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:profile})});
      currentUser=profileData.user;
    }
    setText("settingsResult",translations.save+" ✓");await loadTranslations(language);applyTranslations(language);
    byId("accountName").textContent=currentUser.name;
  }catch(error){setText("settingsResult",error.message)}
}
async function changePassword(){
  if(!currentUser){setText("passwordResult","Login diperlukan.");return}
  try{
    await api("/api/auth/password",{method:"PUT",headers:{"Content-Type":"application/json"},body:JSON.stringify({current_password:byId("currentPassword").value,new_password:byId("newPassword").value})});
    setText("passwordResult","Password berhasil diubah.");byId("currentPassword").value="";byId("newPassword").value="";
  }catch(error){setText("passwordResult",error.message)}
}
async function uploadAsset(){
  const file=byId("file").files[0];
  if(!file){setText("uploadResult","Pilih file dulu.");return}
  const form=new FormData();form.append("file",file);setText("uploadResult","Mengunggah...");
  try{
    const data=await api("/api/assets/upload",{method:"POST",body:form});
    uploadedPath=data.path;byId("templatePath").value=data.path;setText("uploadResult",JSON.stringify(data,null,2));await inspectUploaded();
  }catch(error){setText("uploadResult",error.message)}
}
async function inspectUploaded(){
  const path=uploadedPath||byId("templatePath").value.trim();
  if(!path){setText("uploadResult","Belum ada path file.");return}
  try{const data=await api("/api/assets/inspect?path="+encodeURIComponent(path));setText("uploadResult",JSON.stringify(data,null,2));renderEntries(data)}
  catch(error){setText("uploadResult",error.message)}
}
function renderEntries(data){
  const box=byId("entries");box.innerHTML="";const entries=(data&&data.entries)||[];
  if(!entries.length){box.textContent="Tidak ada entry archive. Export Asset akan mengirim file sumber.";return}
  const title=document.createElement("strong");title.textContent="Entries archive";box.appendChild(title);
  for(const entry of entries){if(entry.is_dir)continue;const label=document.createElement("label");const checkbox=document.createElement("input");checkbox.type="checkbox";checkbox.value=entry.name;checkbox.className="entry-check";label.append(checkbox," ",entry.name," (",entry.size," bytes)");box.appendChild(label)}
}
function exportSelected(){
  const path=uploadedPath||byId("templatePath").value.trim();const result=byId("exportResult");
  if(!path){result.textContent="Belum ada file.";return}
  const selected=[...document.querySelectorAll(".entry-check:checked")].map(x=>x.value);const params=new URLSearchParams();params.set("path",path);selected.forEach(name=>params.append("selected",name));
  result.innerHTML='<a class="badge" href="/api/assets/export?'+params.toString()+'">Download export ZIP</a>';
}
async function classifyTemplate(){
  const path=byId("templatePath").value.trim();if(!path){setText("templateResult","Masukkan path file.");return}
  try{setText("templateResult",JSON.stringify(await api("/api/templates/classify?path="+encodeURIComponent(path)),null,2))}
  catch(error){setText("templateResult",error.message)}
}
async function loadRepository(){
  try{setText("repositoryResult",JSON.stringify(await api("/api/repository"),null,2))}
  catch(error){setText("repositoryResult",error.message)}
}
async function loadTree(){
  try{setText("repositoryResult",JSON.stringify(await api("/api/repository/tree"),null,2))}
  catch(error){setText("repositoryResult",error.message)}
}
async function loadFolderDescriptions(){
  const result=byId("folderResult");
  result.classList.remove("hidden");
  try{
    const data=await api("/api/repository/folders");
    result.textContent=JSON.stringify(data,null,2);
  }catch(error){
    result.textContent=error.message;
  }
}
async function scrapePage(){
  const url=byId("scraperUrl").value.trim();if(!url){setText("scraperResult","Masukkan URL publik dulu.");return}
  setText("scraperResult","Mengambil halaman...");
  try{setText("scraperResult",JSON.stringify(await api("/api/scraper/fetch?url="+encodeURIComponent(url)),null,2))}
  catch(error){setText("scraperResult",error.message)}
}
async function crawlSite(){
  const url=byId("scraperUrl").value.trim(),pages=Number(byId("scraperPages").value);if(!url){setText("scraperResult","Masukkan URL publik dulu.");return}
  if(!Number.isInteger(pages)||pages<1||pages>25){setText("scraperResult","Jumlah halaman harus 1-25.");return}
  setText("scraperResult","Menjalankan crawl...");
  try{setText("scraperResult",JSON.stringify(await api("/api/scraper/crawl?url="+encodeURIComponent(url)+"&max_pages="+pages+"&max_bytes=5242880"),null,2))}
  catch(error){setText("scraperResult",error.message)}
}
async function getRoblox(){
  const u=byId("url").value.trim();if(!u){setText("result","Masukkan URL Roblox dulu.");return}
  try{const data=await api("/api/assets/roblox/validate?url="+encodeURIComponent(u));setText("result","Asset ID "+data.asset_id+" valid. Memulai download...");window.location.href="/api/assets/roblox/url?url="+encodeURIComponent(u)}
  catch(error){setText("result",error.message)}
}
async function extractSpriteSheet(){
  const path=uploadedPath||byId("templatePath").value.trim(),columns=Number(byId("spriteColumns").value),rows=Number(byId("spriteRows").value),result=byId("spriteResult");
  if(!path){result.textContent="Upload atau pilih file image dulu.";return}
  if(!Number.isInteger(columns)||!Number.isInteger(rows)||columns<1||columns>64||rows<1||rows>64){result.textContent="Rows dan columns harus bilangan bulat 1-64.";return}
  result.innerHTML='<a class="badge" href="/api/sprite-sheet/extract?path='+encodeURIComponent(path)+'&columns='+columns+'&rows='+rows+'">Download frame ZIP</a>';
}
for(const t of ["strobo","rotator","ledbar"]){
  const card=document.createElement("div");card.className="card";card.innerHTML="<h3>"+t.toUpperCase()+'</h3><div class="row"><a data-i18n="bussid_zip" href="/api/lights/'+t+'/download?platform=bussid">BUSSID ZIP</a><a data-i18n="roblox_zip" href="/api/lights/'+t+'/download?platform=roblox">Roblox ZIP</a><a data-i18n="json_preview" href="/api/lights/'+t+'">JSON Preview</a></div>';byId("lightsGrid").append(card)
}

async function refreshProjectStatus(){
  const state=byId("liveState"),apiState=byId("liveApiState"),updated=byId("liveUpdatedAt");
  state.textContent="Memeriksa…";state.classList.remove("live-error");
  try{
    const data=await api("/api/project/status",{timeoutMs:10000});
    setText("liveProjectId",data.project_id||"Tidak tersedia");
    setText("liveVersion",data.version||"Tidak tersedia");
    setText("liveApiState",data.status==="operational"?"Online":"Status: "+String(data.status||"unknown"));
    setText("liveUpdatedAt",data.generated_at?new Date(data.generated_at).toLocaleString():"Timestamp tidak tersedia");
    setText("projectFeatures",JSON.stringify({project_id:data.project_id,name:data.name,version:data.version,status:data.status,generated_at:data.generated_at,features:data.features},null,2));
    state.textContent="● Terhubung";state.classList.add("live-ok");
  }catch(error){
    state.textContent="● Tidak terhubung";state.classList.add("live-error");
    setText("liveApiState","Tidak dapat dijangkau");setText("projectFeatures","Status proyek gagal diambil: "+error.message+"\\nData tidak ditebak atau ditampilkan sebagai data real-time.");
  }
}
async function askProjectAssistant(event){
  event.preventDefault();
  const input=byId("assistantMessage"),button=byId("assistantSubmit"),status=byId("assistantStatus"),reply=byId("assistantReply");
  const message=input.value.trim();
  if(!message){status.textContent="Tulis pertanyaan terlebih dahulu.";return}
  button.disabled=true;status.textContent="Memproses…";reply.textContent="Menunggu respons server…";
  try{
    const data=await api("/api/project/assistant",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message}),timeoutMs:15000});
    reply.textContent=String(data.reply||data.message||"Server tidak mengembalikan jawaban.");
    status.textContent=(data.mode||"built_in_rules")==="built_in_rules"?"Selesai · aturan bawaan":"Selesai";
  }catch(error){reply.textContent="Asisten tidak tersedia: "+error.message;status.textContent="Gagal";}
  finally{button.disabled=false}
}

const ACTIONS={
  loginUser,googleLogin,registerUser,logoutUser,logoutAll,saveSettings,changePassword,
  uploadAsset,inspectUploaded,exportSelected,classifyTemplate,loadRepository,loadTree,
  loadFolderDescriptions,scrapePage,crawlSite,getRoblox,extractSpriteSheet
};
document.addEventListener("click",async(event)=>{
  const target=event.target.closest("[data-action]");
  if(!target)return;
  const action=target.dataset.action;
  const handler=ACTIONS[action];
  if(typeof handler!=="function")return;
  if(target.dataset.busy==="1")return;
  target.dataset.busy="1";
  target.classList.add("loading");
  target.setAttribute("aria-busy","true");
  try{await handler()}finally{
    target.dataset.busy="0";
    target.classList.remove("loading");
    target.removeAttribute("aria-busy");
  }
});
const menuButton=byId("menuButton"),menu=byId("menu");
menuButton.addEventListener("click",()=>{const open=menu.classList.toggle("open");menuButton.setAttribute("aria-expanded",String(open))});
menu.querySelectorAll("a").forEach(link=>link.addEventListener("click",()=>menu.classList.remove("open")));
window.matchMedia("(prefers-color-scheme: dark)").addEventListener?.("change",()=>{if((localStorage.getItem("asset_lab_theme")||"light")==="system")applyTheme("system")});
if("serviceWorker" in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
(async()=>{try{await loadAuthStatus();await loadMe()}catch(e){console.error(e)}loadRepository()})();

byId("refreshProject")?.addEventListener("click",refreshProjectStatus);
byId("assistantForm")?.addEventListener("submit",askProjectAssistant);
refreshProjectStatus();
window.setInterval(refreshProjectStatus,30000);
