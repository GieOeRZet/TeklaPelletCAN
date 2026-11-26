plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}
android {
    namespace = "pl.gieoerzet.teklapelletcan.newapp"
    compileSdk = 35
    defaultConfig {
        applicationId = "pl.gieoerzet.teklapelletcan.newapp"
        minSdk = 29
        targetSdk = 35
        versionCode = 3
        versionName = "0.3.0"
    }
    buildTypes { release { isMinifyEnabled = false }; debug { isMinifyEnabled = false } }
    compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
    kotlinOptions { jvmTarget = "17" }
}
tasks.register<Copy>("syncUiAssets") {
    from(rootProject.projectDir.parentFile.resolve("android/ui")) {
        exclude("index.html")
        exclude("style.css")
    }
    into(layout.buildDirectory.dir("generated/ui"))
}
tasks.named("preBuild").configure { dependsOn("syncUiAssets") }
android.sourceSets["main"].assets.srcDir(layout.buildDirectory.dir("generated/ui"))
