$ErrorActionPreference = "Continue"
& ./mvnw compile 2>&1 | Tee-Object -FilePath "build_output.log"
