plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

// Wersja aplikacji = wersja firmware z pliku VERSION w korzeniu repo; numer budowy z CI.
val appVersion = rootProject.file("../VERSION").readText().trim()
// Zmienne puste (np. brakujące sekrety CI) traktujemy jak nieustawione.
fun env(name: String, default: String): String = System.getenv(name)?.takeIf { it.isNotBlank() } ?: default
val buildNo = env("GITHUB_RUN_NUMBER", "1").toInt()

android {
    namespace = "pl.gieoerzet.teklapelletcan"
    compileSdk = 35

    defaultConfig {
        applicationId = "pl.gieoerzet.teklapelletcan"
        minSdk = 29
        targetSdk = 35
        versionCode = buildNo
        versionName = "$appVersion+$buildNo"
        ndk { abiFilters += listOf("arm64-v8a", "armeabi-v7a", "x86_64") }
        externalNativeBuild { cmake { cppFlags += "-std=c++17"; arguments += "-DANDROID_STL=c++_static" } }
    }

    externalNativeBuild { cmake { path = file("src/main/cpp/CMakeLists.txt") } }

    // Klucz podpisu: z sekretów CI (ANDROID_KEYSTORE_FILE/…); bez nich – klucz TESTOWY z repozytorium (android/dev-release.jks).
    signingConfigs {
        create("release") {
            storeFile = file(env("ANDROID_KEYSTORE_FILE", "../dev-release.jks"))
            storePassword = env("ANDROID_KEYSTORE_PASSWORD", "tekla-dev")
            keyAlias = env("ANDROID_KEY_ALIAS", "tekla")
            keyPassword = env("ANDROID_KEY_PASSWORD", "tekla-dev")
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("release")
        }
        debug { signingConfig = signingConfigs.getByName("release") }   // ten sam podpis: aktualizacja nad istniejącą instalacją
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
    packaging { resources.excludes += "/META-INF/{AL2.0,LGPL2.1}" }
    lint { abortOnError = false }
}

// Strony karty/urządzenia (web/) oraz powłoka aplikacji (android/shell) trafiają do assets bez kopiowania w repozytorium.
val syncAssets = tasks.register<Sync>("syncAssets") {
    from(rootProject.file("../web")) { exclude("test/**", "**/*.md"); into("web") }
    from(rootProject.file("shell")) { into("app") }
    into(layout.buildDirectory.dir("generated/tpcAssets"))
}
android.sourceSets.getByName("main").assets.srcDir(layout.buildDirectory.dir("generated/tpcAssets"))
tasks.named("preBuild") { dependsOn(syncAssets) }
