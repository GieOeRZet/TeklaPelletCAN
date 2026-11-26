plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "pl.gieoerzet.teklapelletcan.newapp"
    compileSdk = 35
    defaultConfig {
        applicationId = "pl.gieoerzet.teklapelletcan.newapp"
        minSdk = 29
        targetSdk = 35
        versionCode = 2
        versionName = "0.2.0"
    }
    buildTypes {
        release { isMinifyEnabled = false }
        debug { isMinifyEnabled = false }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}

dependencies {
    implementation("androidx.activity:activity-compose:1.10.1")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("androidx.compose.ui:ui:1.7.8")
    implementation("androidx.compose.ui:ui-tooling-preview:1.7.8")
    implementation("androidx.compose.material3:material3:1.3.1")
    implementation("androidx.compose.material:material-icons-extended:1.7.8")
    implementation("androidx.core:core-ktx:1.15.0")
    debugImplementation("androidx.compose.ui:ui-tooling:1.7.8")
}
