package pl.gieoerzet.teklapelletcan.newapp

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.compose.setContent
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.time.LocalDate
import java.time.LocalTime
import java.time.format.DateTimeFormatter
import kotlin.math.sin

private val Bg = Color(0xFF0B0C0F)
private val Surface = Color(0xFF15171C)
private val Surface2 = Color(0xFF1B1E24)
private val Line = Color(0xFF2A2D35)
private val Txt = Color(0xFFF2F3F5)
private val Muted = Color(0xFF969AA5)
private val Orange = Color(0xFFFF9F24)
private val Green = Color(0xFF45D58A)
private val Red = Color(0xFFFF6262)

private data class UiState(
    val devices: List<PelletDevice> = emptyList(),
    val selected: PelletDevice? = null,
    val values: PelletState = PelletState(),
    val firmware: String = "",
    val points: JSONObject? = null,
    val ble: List<BleFound> = emptyList(),
    val mdns: List<MdnsFound> = emptyList(),
    val error: String? = null,
    val page: String = "kociol"
)

class MainActivity : ComponentActivity() {
    private lateinit var store: DeviceStore
    private lateinit var ble: BleDiscovery
    private lateinit var mdns: MdnsDiscovery

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        store = DeviceStore(this)
        ble = BleDiscovery(this)
        mdns = MdnsDiscovery(this)
        window.statusBarColor = Bg.toArgb()
        window.navigationBarColor = Bg.toArgb()
        setContent { TeklaPelletApp() }
    }

    override fun onDestroy() {
        ble.stop()
        mdns.stop()
        super.onDestroy()
    }

    @Composable
    private fun TeklaPelletApp() {
        val scope = rememberCoroutineScope()
        var ui by remember { mutableStateOf(UiState(devices = store.load())) }
        val permissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
            startBle { b -> ui = ui.copy(ble = (ui.ble + b).distinctBy { it.address }) }
        }

        fun scanBle() {
            val permissions = if (android.os.Build.VERSION.SDK_INT >= 31)
                arrayOf(Manifest.permission.BLUETOOTH_SCAN, Manifest.permission.BLUETOOTH_CONNECT)
            else arrayOf(Manifest.permission.ACCESS_FINE_LOCATION)
            val missing = permissions.filter { ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED }
            if (missing.isNotEmpty()) permissionLauncher.launch(missing.toTypedArray())
            else startBle { b -> ui = ui.copy(ble = (ui.ble + b).distinctBy { it.address }) }
        }

        fun selectDevice(d: PelletDevice) {
            ui = ui.copy(selected = d, page = "kociol", error = null)
            scope.launch {
                val info = withContext(Dispatchers.IO) { PelletApi.info(d.baseUrl) }
                val pts = withContext(Dispatchers.IO) { PelletApi.points(d.baseUrl) }
                if (info == null) {
                    ui = ui.copy(selected = d.copy(online = false), error = "Brak połączenia z modułem")
                } else {
                    ui = ui.copy(selected = d.copy(online = true), firmware = info.optString("fw"), points = pts)
                    while (ui.selected?.id == d.id) {
                        val s = withContext(Dispatchers.IO) { PelletApi.states(d.baseUrl) }
                        if (s != null) ui = ui.copy(values = s, selected = ui.selected?.copy(online = true))
                        else ui = ui.copy(selected = ui.selected?.copy(online = false))
                        delay(2000)
                    }
                }
            }
        }

        fun addDevice(d: PelletDevice) {
            val clean = d.copy(baseUrl = d.baseUrl.trimEnd('/'))
            val list = ui.devices.filterNot { it.id == clean.id || it.baseUrl == clean.baseUrl }.toMutableList()
            list.add(clean)
            store.save(list)
            ui = ui.copy(devices = list, selected = clean, page = "kociol", error = null)
            selectDevice(clean)
        }

        MaterialTheme(
            colorScheme = darkColorScheme(
                background = Bg, surface = Surface, primary = Orange, secondary = Green,
                onBackground = Txt, onSurface = Txt, onPrimary = Color(0xFF17120B)
            )
        ) {
            Surface(Modifier.fillMaxSize(), color = Bg) {
                val selected = ui.selected
                if (selected == null && ui.devices.isEmpty()) {
                    Dashboard(demoState(), "TeklaPellet", true, ui.page, true, "", true,
                        { ui = ui.copy(page = it) }, { ui = ui.copy(page = "devices") })
                } else if (selected == null || ui.page == "devices") {
                    DeviceScreen(
                        ui = ui,
                        onBle = { scanBle() },
                        onMdns = {
                            ui = ui.copy(mdns = emptyList())
                            mdns.start { f -> runOnUiThread { ui = ui.copy(mdns = (ui.mdns + f).distinctBy { it.host }) } }
                        },
                        onManual = { host ->
                            scope.launch {
                                val base = if (host.startsWith("http")) host else "http://" + host
                                val info = withContext(Dispatchers.IO) { PelletApi.info(base) }
                                if (info == null) ui = ui.copy(error = "Pod tym adresem nie odpowiada TeklaPelletCAN.")
                                else {
                                    val id = info.optString("id").ifBlank { base }
                                    addDevice(PelletDevice(id, "TeklaPellet " + id.takeLast(4), base, info.optString("fw")))
                                }
                            }
                        },
                        onMdnsAdd = { f -> addDevice(PelletDevice(f.id.ifBlank { f.host }, f.name, "http://" + f.host + ":" + f.port, f.firmware)) },
                        onBleDetails = { b -> ui = ui.copy(error = "BLE: " + b.name + " • " + b.address + " • RSSI " + b.rssi + " dBm") },
                        onDemo = { ui = ui.copy(selected = null, page = "kociol") }
                    )
                } else {
                    val hasCo2 = ui.points?.toString()?.contains("co2", ignoreCase = true) == true ||
                        ui.values.values.keys.any { it.contains("co2", true) }
                    Dashboard(
                        ui.values, selected.name, false, ui.page, hasCo2, ui.firmware, selected.online,
                        { ui = ui.copy(page = it) }, { ui = ui.copy(page = "devices") },
                        { ui = ui.copy(page = "menu") }, { ui = ui.copy(selected = null, page = "devices") },
                        { id, value ->
                            scope.launch {
                                val ok = withContext(Dispatchers.IO) {
                                    PelletApi.request(selected.baseUrl, "POST", "/api/v1/write",
                                        JSONObject().put("id", id).put("value", value).toString())?.status == 200
                                }
                                ui = ui.copy(error = if (ok) "Zapisano" else "Błąd zapisu")
                            }
                        }
                    )
                }
            }
        }
    }

    private fun startBle(onFound: (BleFound) -> Unit) {
        ble.start(onFound, { })
    }

    private fun demoState() = PelletState(values = mapOf(
        "sensor.tekla_kociol_temperatura" to "64.8",
        "sensor.tekla_kociol_zadana_wynikowa" to "60",
        "sensor.tekla_temperatura_powrotu" to "41.9",
        "sensor.tekla_moc_palnika" to "0",
        "sensor.tekla_temperatura_zewnetrzna" to "-3",
        "sensor.tekla_cwu_temperatura" to "53.9",
        "sensor.tekla_cwu_zadana_wynikowa" to "55",
        "sensor.tekla_co_temperatura" to "49.8",
        "sensor.tekla_co_zadana_wynikowa" to "45",
        "sensor.tekla_paliwo_zapelnienie" to "21",
        "sensor.tekla_kociol_wlaczony" to "on",
        "sensor.tekla_palnik_stan" to "Wyłączony",
        "sensor.tekla_cwu_pompa" to "on",
        "sensor.tekla_co_pompa" to "on"
    ))
}

@Composable private fun DeviceScreen(
    ui: UiState, onBle: () -> Unit, onMdns: () -> Unit, onManual: (String) -> Unit,
    onMdnsAdd: (MdnsFound) -> Unit, onBleDetails: (BleFound) -> Unit, onDemo: () -> Unit
) {
    var host by remember { mutableStateOf("") }
    val context = LocalContext.current
    Column(Modifier.fillMaxSize().background(Bg).padding(horizontal = 18.dp, vertical = 12.dp).verticalScroll(rememberScrollState())) {
        TopBar("Dodaj moduł", "BLE • Wi‑Fi • mDNS")
        GlassCard {
            Text("Wykrywanie BLE", color = Orange, fontWeight = FontWeight.Bold)
            Text("Świeżo uruchomiony moduł reklamuje się jako TeklaPellet-xxxxxx.", color = Muted, fontSize = 13.sp)
            Spacer(Modifier.height(10.dp))
            Button(onClick = onBle, colors = ButtonDefaults.buttonColors(containerColor = Orange, contentColor = Color.Black)) {
                Icon(Icons.Default.Bluetooth, null); Spacer(Modifier.width(6.dp)); Text("Skanuj BLE")
            }
            ui.ble.forEach { b -> DeviceRow(b.name, b.address + " • " + b.rssi + " dBm", true) { onBleDetails(b) } }
            if (ui.ble.isEmpty()) Text("Brak znalezionych modułów BLE.", color = Muted, fontSize = 13.sp, modifier = Modifier.padding(top = 8.dp))
        }
        GlassCard {
            Text("Po Wi‑Fi", color = Orange, fontWeight = FontWeight.Bold)
            Text("Po konfiguracji moduł jest sterowany przez REST/WebSocket po Wi‑Fi. mDNS działa dla _teklapelletcan._tcp.", color = Muted, fontSize = 13.sp)
            Spacer(Modifier.height(8.dp)); Button(onClick = onMdns) { Text("Szukaj w sieci") }
            ui.mdns.forEach { f -> DeviceRow(f.name, f.host + ":" + f.port + " • " + f.firmware, true) { onMdnsAdd(f) } }
        }
        GlassCard {
            Text("Adres ręczny", color = Orange, fontWeight = FontWeight.Bold)
            OutlinedTextField(host, { host = it }, label = { Text("192.168.1.50 lub http://...") }, singleLine = true, modifier = Modifier.fillMaxWidth())
            Spacer(Modifier.height(8.dp)); Button(onClick = { onManual(host) }, enabled = host.isNotBlank()) { Text("Sprawdź i dodaj") }
        }
        GlassCard {
            Text("Awaryjna konfiguracja AP", color = Orange, fontWeight = FontWeight.Bold)
            Text("Jeżeli moduł nie ma jeszcze Wi‑Fi, użyj sieci TeklaPellet-XXXXXX jako ścieżki serwisowej.", color = Muted, fontSize = 13.sp)
            Spacer(Modifier.height(8.dp))
            OutlinedButton(onClick = { val i = Intent(Settings.ACTION_WIFI_SETTINGS); onDemo(); }) { Text("Ustawienia Wi‑Fi") }
        }
        if (ui.devices.isNotEmpty()) GlassCard {
            Text("Moje moduły", color = Orange, fontWeight = FontWeight.Bold)
            ui.devices.forEach { d -> DeviceRow(d.name, d.baseUrl, d.online) { } }
        }
        ui.error?.let { Text(it, color = Red, modifier = Modifier.padding(8.dp)) }
        if (ui.devices.isEmpty()) TextButton(onClick = onDemo) { Text("Zostań w trybie DEMO", color = Muted) }
    }
}

@Composable private fun Dashboard(
    state: PelletState, name: String, demo: Boolean, page: String, hasCo2: Boolean,
    firmware: String = "", online: Boolean = true, onPage: (String) -> Unit, onAdd: () -> Unit,
    onMenu: () -> Unit = {}, onDisconnect: () -> Unit = {}, onWrite: (String, String) -> Unit = { _, _ -> }
) {
    val temp = state.num("sensor.tekla_kociol_temperatura") ?: 64.8
    val set = state.num("sensor.tekla_kociol_zadana_wynikowa") ?: 60.0
    val ret = state.num("sensor.tekla_temperatura_powrotu") ?: 41.9
    val power = state.num("sensor.tekla_moc_palnika") ?: 0.0
    val outside = state.num("sensor.tekla_temperatura_zewnetrzna") ?: -3.0
    val co1 = state.num("sensor.tekla_co_temperatura") ?: 49.8
    val co1Set = state.num("sensor.tekla_co_zadana_wynikowa") ?: 45.0
    val co2 = state.fuzzy("co2", "temperatura")?.toDoubleOrNull() ?: 36.0
    val cwu = state.num("sensor.tekla_cwu_temperatura") ?: 53.9
    val cwuSet = state.num("sensor.tekla_cwu_zadana_wynikowa") ?: 55.0
    val fuel = state.num("sensor.tekla_paliwo_zapelnienie") ?: 21.0
    val burner = state.v("sensor.tekla_palnik_stan") ?: "Wyłączony"
    val boilerOn = state.v("sensor.tekla_kociol_wlaczony") == "on"
    Column(Modifier.fillMaxSize().background(Bg)) {
        Column(Modifier.weight(1f).verticalScroll(rememberScrollState()).padding(horizontal = 18.dp)) {
            TopBar(name, if (demo) "TRYB DEMO" else if (online) "● online" else "● brak połączenia")
            when (page) {
                "kociol" -> BoilerPage(temp,set,ret,power,outside,co1,co1Set,co2,cwu,cwuSet,fuel,burner,boilerOn,demo,onAdd)
                "palnik" -> BurnerPage(state,power,burner,onWrite)
                "co" -> SimpleDomainPage("CO1",co1,co1Set,state.v("sensor.tekla_co_pompa")=="on")
                "co2" -> SimpleDomainPage("CO2",co2,35.0,state.fuzzy("co2","pompa")=="on")
                "cwu" -> SimpleDomainPage("CWU",cwu,cwuSet,state.v("sensor.tekla_cwu_pompa")=="on")
                "menu" -> MenuPage(demo,onAdd,onDisconnect)
                else -> BoilerPage(temp,set,ret,power,outside,co1,co1Set,co2,cwu,cwuSet,fuel,burner,boilerOn,demo,onAdd)
            }
        }
        NavigationBar(containerColor=Color(0xFF101216), tonalElevation=0.dp) {
            val keys=listOf("kociol","palnik","co","co2","cwu","menu")
            val labels=listOf("Kocioł","Palnik","CO","CO2","CWU","Menu")
            val icons=listOf(Icons.Default.LocalFireDepartment,Icons.Default.Whatshot,Icons.Default.Thermostat,Icons.Default.ThermostatAuto,Icons.Default.WaterDrop,Icons.Default.Menu)
            keys.forEachIndexed { i,key ->
                if (key!="co2" || hasCo2) NavigationBarItem(
                    selected=page==key, onClick={if(key=="menu")onMenu()else onPage(key)},
                    icon={Icon(icons[i],null)}, label={Text(labels[i],fontSize=10.sp)},
                    colors=NavigationBarItemDefaults.colors(selectedIconColor=Orange,selectedTextColor=Orange,unselectedIconColor=Muted,unselectedTextColor=Muted,indicatorColor=Color.Transparent)
                )
            }
        }
    }
}

@Composable private fun BoilerPage(
    temp:Double,set:Double,ret:Double,power:Double,outside:Double,co1:Double,co1Set:Double,co2:Double,cwu:Double,cwuSet:Double,fuel:Double,burner:String,on:Boolean,demo:Boolean,onAdd:()->Unit
) {
    GlassCard {
        Row(Modifier.fillMaxWidth(),verticalAlignment=Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(temp.one(),fontSize=54.sp,fontWeight=FontWeight.Light); Text("°C",color=Orange,fontSize=19.sp)
                Text(burner,color=Orange,fontSize=18.sp,fontWeight=FontWeight.SemiBold); Text("zadana "+set.one()+" °C",color=Muted)
            }
            Column(horizontalAlignment=Alignment.End) {
                Metric("Moc palnika",power.one()+" %"); Metric("Spalanie",if(power>0)"aktywny" else "0.0 kg/h")
                Metric("Powrót",ret.one()+" °C"); Metric("Palnik","0 °C")
            }
        }
        Spacer(Modifier.height(12.dp)); Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){StatusDot("Dmuchawa",false);StatusDot("Podajnik",false);StatusDot("Podajnik palnika",false)}
        Row(horizontalArrangement=Arrangement.spacedBy(8.dp)){StatusDot("Zapalarka",false);StatusDot("Ruszt",false);StatusDot("Pompa",true)}
        Spacer(Modifier.height(8.dp)); Text("Temperatura kotła",color=Muted,fontSize=12.sp); MiniGraph()
    }
    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(12.dp)){SmallCard("ZEWN.",outside.one()+" °C",Modifier.weight(1f));SmallCard("ZASILANIE",if(on)"Włączone" else "Wyłączone",Modifier.weight(1f),on)}
    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(12.dp)){SmallCard("CO1",co1.one()+"° / "+co1Set.one()+"°",Modifier.weight(1f),true);SmallCard("CO2",co2.one()+"° / 35°",Modifier.weight(1f))}
    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(12.dp)){SmallCard("CWU",cwu.one()+"° / "+cwuSet.one()+"°",Modifier.weight(1f),true);SmallCard("PALIWO",fuel.one()+" kg",Modifier.weight(1f))}
    if(demo)Button(onClick=onAdd,modifier=Modifier.fillMaxWidth().padding(vertical=12.dp),colors=ButtonDefaults.buttonColors(containerColor=Orange,contentColor=Color.Black)){Text("＋ Dodaj moduł")}
}
@Composable private fun BurnerPage(state:PelletState,power:Double,burner:String,onWrite:(String,String)->Unit){
    GlassCard{Text("Palnik",color=Orange,fontSize=22.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(10.dp));Metric("Stan",burner);Metric("Moc",power.one()+" %");Metric("Temperatura",(state.num("sensor.tekla_temperatura_palnika")?:0.0).one()+" °C");Metric("Dmuchawa",state.v("sensor.tekla_dmuchawa_pracuje")?:"—");Metric("Podajnik",state.v("sensor.tekla_podajnik_pracuje")?:"—")}
    GlassCard{Text("Sterowanie",color=Orange,fontWeight=FontWeight.Bold);Text("Zapis przechodzi przez API modułu i wymaga właściwego poziomu dostępu.",color=Muted,fontSize=13.sp);Row(horizontalArrangement=Arrangement.spacedBy(8.dp),modifier=Modifier.padding(top=10.dp)){Button(onClick={onWrite("boiler_mode","1")}){Text("Auto")};OutlinedButton(onClick={onWrite("boiler_mode","0")}){Text("Stop")}}}
}
@Composable private fun SimpleDomainPage(title:String,temp:Double,set:Double,pump:Boolean){
    GlassCard{Text(title,color=Orange,fontSize=22.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(14.dp));Text(temp.one()+" °C",fontSize=48.sp,fontWeight=FontWeight.Light);Text("zadana "+set.one()+" °C",color=Muted);Spacer(Modifier.height(12.dp));StatusDot("Pompa",pump)}
    GlassCard{Text("Nastawy",color=Orange,fontWeight=FontWeight.Bold);Metric("Temperatura",temp.one()+" °C");Metric("Zadana",set.one()+" °C");Metric("Pompa",if(pump)"Włączona" else "Wyłączona")}
}
@Composable private fun MenuPage(demo:Boolean,onAdd:()->Unit,onDisconnect:()->Unit){
    GlassCard{Text("Moduły instalacji",color=Orange,fontWeight=FontWeight.Bold);MenuRow("Solar","dynamicznie z konfiguracji");MenuRow("Bufor","dynamicznie z konfiguracji");MenuRow("Kaskada","dynamicznie z konfiguracji");MenuRow("Magazyn paliwa","dynamicznie z konfiguracji")}
    GlassCard{Text("Urządzenie",color=Orange,fontWeight=FontWeight.Bold);MenuRow("Konfiguracja","Wi‑Fi • OTA • diagnostyka");MenuRow("Poziom kotła","PIN 0900 / 0999");MenuRow("Wygląd","Material 3 + Glass");if(!demo)Button(onClick=onDisconnect,modifier=Modifier.fillMaxWidth().padding(top=10.dp)){Text("Zmień moduł")}else Button(onClick=onAdd,modifier=Modifier.fillMaxWidth().padding(top=10.dp),colors=ButtonDefaults.buttonColors(containerColor=Orange,contentColor=Color.Black)){Text("Dodaj moduł")}}
}
@Composable private fun TopBar(title:String,sub:String){
    Row(Modifier.fillMaxWidth().padding(top=8.dp,bottom=14.dp),verticalAlignment=Alignment.CenterVertically){
        Box(Modifier.size(48.dp).clip(RoundedCornerShape(15.dp)).background(Surface2),contentAlignment=Alignment.Center){Icon(Icons.Default.Menu,null,tint=Txt)}
        Spacer(Modifier.width(12.dp));Column(Modifier.weight(1f)){Text(title,fontSize=22.sp,fontWeight=FontWeight.Bold);Text(LocalDate.now().format(DateTimeFormatter.ofPattern("EEE, dd MMM"))+" • "+sub,color=Muted,fontSize=12.sp)}
        Text(LocalTime.now().format(DateTimeFormatter.ofPattern("HH:mm")),color=Orange,fontSize=24.sp,fontWeight=FontWeight.SemiBold)
    }
}
@Composable private fun GlassCard(content:@Composable ColumnScope.()->Unit){Column(Modifier.fillMaxWidth().padding(bottom=12.dp).clip(RoundedCornerShape(22.dp)).background(Brush.linearGradient(listOf(Surface2,Surface))).border(1.dp,Line,RoundedCornerShape(22.dp)).padding(16.dp),content=content)}
@Composable private fun Metric(label:String,value:String){Row(Modifier.fillMaxWidth().padding(vertical=4.dp),horizontalArrangement=Arrangement.SpaceBetween){Text(label,color=Muted);Text(value,fontWeight=FontWeight.SemiBold)}}
@Composable private fun StatusDot(label:String,on:Boolean){Row(verticalAlignment=Alignment.CenterVertically){Box(Modifier.size(9.dp).clip(CircleShape).background(if(on)Green else Color(0xFF343740)));Spacer(Modifier.width(6.dp));Text(label,color=Muted,fontSize=12.sp)}}
@Composable private fun SmallCard(label:String,value:String,modifier:Modifier=Modifier,on:Boolean=false){Column(modifier.clip(RoundedCornerShape(18.dp)).background(Surface).border(1.dp,Line,RoundedCornerShape(18.dp)).padding(14.dp)){Text(label,color=Muted,fontSize=12.sp,fontWeight=FontWeight.Bold);Spacer(Modifier.height(12.dp));Text(value,fontSize=25.sp);if(on){Spacer(Modifier.height(5.dp));StatusDot("Aktywne",true)}}}
@Composable private fun MenuRow(a:String,b:String){Row(Modifier.fillMaxWidth().padding(vertical=8.dp),horizontalArrangement=Arrangement.SpaceBetween){Text(a);Text(b,color=Muted,fontSize=12.sp)}}
@Composable private fun DeviceRow(name:String,sub:String,on:Boolean,click:()->Unit){ Row(Modifier.fillMaxWidth().padding(vertical=6.dp).clip(RoundedCornerShape(15.dp)).background(Surface2).clickable(onClick=click).padding(12.dp),verticalAlignment=Alignment.CenterVertically){ Box(Modifier.size(10.dp).clip(CircleShape).background(if(on) Green else Muted)); Spacer(Modifier.width(10.dp)); Column(Modifier.weight(1f)){ Text(name,maxLines=1,overflow=TextOverflow.Ellipsis,fontWeight=FontWeight.SemiBold); Text(sub,color=Muted,fontSize=12.sp) }; Text("Dodaj",color=Orange,fontWeight=FontWeight.Bold) } }
@Composable private fun MiniGraph(){Canvas(Modifier.fillMaxWidth().height(42.dp)){val pts=(0..40).map{i->androidx.compose.ui.geometry.Offset(i/40f*size.width,size.height*(.48f+.22f*sin(i*.35f)))};for(i in 0 until pts.lastIndex)drawLine(Orange,pts[i],pts[i+1],2.5f,StrokeCap.Round)}}
private fun Double.one()=String.format("%.1f",this)
