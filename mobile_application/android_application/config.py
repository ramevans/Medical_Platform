load(":build_defs.bzl", "create_aar_targets", "create_jar_targets")

lib_deps = []

create_aar_targets(glob(["libs/*.aar"]))

create_jar_targets(glob(["libs/*.jar"]))

android_library(
    name = "all-libs",
    exported_deps = lib_deps,
)

android_library(
    name = "app-code",
    srcs = glob([
        "src/main/java/**/*.java",
    ]),
    deps = [
        ":all-libs",
        ":build_config",
        ":res",
    ],
)

android_build_config(
    name = "build_config",
    package = "us.josephrossi.medops",
)

android_resource(
    name = "res",
    package = "us.josephrossi.medops",
    res = "src/main/res",
)

android_binary(
    name = "app",
    keystore = "//android/keystores:debug",
    manifest = "src/main/AndroidManifest.xml",
    package_type = "debug",
    deps = [
        ":app-code",
    ],
)

def enableHermes = project.ext.react.get("enableHermes", false);

android {
    compileSdkVersion rootProject.ext.compileSdkVersion

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    defaultConfig {
        applicationId 'us.josephrossi.medops'
        minSdkVersion rootProject.ext.minSdkVersion
        targetSdkVersion rootProject.ext.targetSdkVersion
        versionCode 1
        versionName "1.0.0"
    }
    splits {
        abi {
            reset()
            enable enableSeparateBuildPerCPUArchitecture
            universalApk false  // If true, also generate a universal APK
            include "armeabi-v7a", "x86", "arm64-v8a", "x86_64"
        }
    }
    signingConfigs {
        debug {
            storeFile file('debug.keystore')
            storePassword 'android'
            keyAlias 'androiddebugkey'
            keyPassword 'android'
        }
    }
    buildTypes {
        debug {
            signingConfig signingConfigs.debug
        }
        release {
            // Caution! In production, you need to generate your own keystore file.
            // see https://reactnative.dev/docs/signed-apk-android.
            signingConfig signingConfigs.debug
            minifyEnabled enableProguardInReleaseBuilds
            proguardFiles getDefaultProguardFile("proguard-android.txt"), "proguard-rules.pro"
        }
    }

    // applicationVariants are e.g. debug, release
    applicationVariants.all { variant ->
        variant.outputs.each { output ->
            // For each separate APK per architecture, set a unique version code as described here:
            // https://developer.android.com/studio/build/configure-apk-splits.html
            def versionCodes = ["armeabi-v7a": 1, "x86": 2, "arm64-v8a": 3, "x86_64": 4]
            def abi = output.getFilter(OutputFile.ABI)
            if (abi != null) {  // null for the universal-debug, universal-release variants
                output.versionCodeOverride =
                        versionCodes.get(abi) * 1048576 + defaultConfig.versionCode
            }

        }
    }
}

dependencies {
    implementation fileTree(dir: "libs", include: ["*.jar"])
    //noinspection GradleDynamicVersion
    implementation "com.facebook.react:react-native:+"  // From node_modules

    def isGifEnabled = (findProperty('expo.gif.enabled') ?: "") == "true";
    def isWebpEnabled = (findProperty('expo.webp.enabled') ?: "") == "true";
    def isWebpAnimatedEnabled = (findProperty('expo.webp.animated') ?: "") == "true";

    // If your app supports Android versions before Ice Cream Sandwich (API level 14)
    // All fresco packages should use the same version
    if (isGifEnabled || isWebpEnabled) {
        implementation 'com.facebook.fresco:fresco:2.0.0'
        implementation 'com.facebook.fresco:imagepipeline-okhttp3:2.0.0'
    }

    if (isGifEnabled) {
        // For animated gif support
        implementation 'com.facebook.fresco:animated-gif:2.0.0'
    }

    if (isWebpEnabled) {
        // For webp support
        implementation 'com.facebook.fresco:webpsupport:2.0.0'
        if (isWebpAnimatedEnabled) {
            // Animated webp support
            implementation 'com.facebook.fresco:animated-webp:2.0.0'
        }
    }

    implementation "androidx.swiperefreshlayout:swiperefreshlayout:1.0.0"
    debugImplementation("com.facebook.flipper:flipper:${FLIPPER_VERSION}") {
      exclude group:'com.facebook.fbjni'
    }
    debugImplementation("com.facebook.flipper:flipper-network-plugin:${FLIPPER_VERSION}") {
        exclude group:'com.facebook.flipper'
        exclude group:'com.squareup.okhttp3', module:'okhttp'
    }
    debugImplementation("com.facebook.flipper:flipper-fresco-plugin:${FLIPPER_VERSION}") {
        exclude group:'com.facebook.flipper'
    }

    if (enableHermes) {
        debugImplementation files(new File(["node", "--print", "require.resolve('hermes-engine/package.json')"].execute(null, rootDir).text.trim(), "../android/hermes-debug.aar"))
        releaseImplementation files(new File(["node", "--print", "require.resolve('hermes-engine/package.json')"].execute(null, rootDir).text.trim(), "../android/hermes-release.aar"))
    } else {
        implementation jscFlavor
    }
}

// Run this once to be able to run the application with BUCK
// puts all compile dependencies into folder libs for BUCK to use
task copyDownloadableDepsToLibs(type: Copy) {
    from configurations.compile
    into 'libs'
}

apply from: new File(["node", "--print", "require.resolve('@react-native-community/cli-platform-android/package.json')"].execute(null, rootDir).text.trim(), "../native_modules.gradle");
applyNativeModulesAppBuildGradle(project)
