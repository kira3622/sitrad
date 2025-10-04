pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
        maven { 
            url = uri("https://jitpack.io")
            credentials { 
                username = "token"
                password = "jp_i99n1brfm1rap0ehntefglsfgf"
            }
        }
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { 
            url = uri("https://jitpack.io")
            credentials { 
                username = "token"
                password = "jp_i99n1brfm1rap0ehntefglsfgf"
            }
        }
    }
}

rootProject.name = "BetonApp"
include(":app")