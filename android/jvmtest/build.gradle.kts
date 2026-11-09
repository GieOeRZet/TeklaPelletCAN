// Testy na JVM czystych klas aplikacji (bez Androida): bramka zapisu, PIN, cache, proxy.
plugins {
    kotlin("jvm") version "2.0.21"
    application
}
repositories { mavenCentral() }
dependencies { implementation("org.json:json:20240303") }
val appSrc = "../app/src/main/kotlin/pl/gieoerzet/teklapelletcan"
sourceSets.main {
    kotlin.srcDir("src")
    kotlin.setSrcDirs(listOf("src"))
    kotlin.include("**/*.kt")
}
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    source(files("$appSrc/Security.kt", "$appSrc/Cache.kt", "$appSrc/Backend.kt", "$appSrc/Proxy.kt", "$appSrc/DemoHost.kt", "$appSrc/Native.kt"))
}
application { mainClass.set("pl.gieoerzet.teklapelletcan.TestKt") }
