{
  description = "Java development template";

  inputs = {
    utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    utils,
    ...
  }:
    utils.lib.eachDefaultSystem
    (
      system: let
        javaVersion = 17;
        overlays = [
          (final: prev: rec {
            jdk = prev."jdk${toString javaVersion}";
            gradle = prev.gradle.override {java = jdk;};
          })
        ];
        pkgs = import nixpkgs {
          inherit system overlays;
          config = {
            android_sdk.accept_license = true;
            allowUnfree = true;
          };
        };
      in {
        # Used by `nix develop`
        devShells.default = let
          buildToolsVersion = "34.0.0";
          platformVersion = "35";
          android-composition = pkgs.androidenv.composeAndroidPackages {
            buildToolsVersions = [buildToolsVersion];
            platformVersions = [platformVersion];
            includeEmulator = false;
            includeSources = false;
            includeSystemImages = false;
          };
          android-sdk = android-composition.androidsdk;
          root-home = "${android-sdk}/libexec/android-sdk";
        in
          pkgs.mkShell {
            # packages = with pkgs; [
            #   jdk
            #   gradle
            #   android-tools
            #   # android-sdk
            # ];
            buildInputs = with pkgs; [
              jdk
              gradle
              android-tools
              android-sdk
              #apksigner sign \
              # --ks release-key.jks \
              # --ks-key-alias release \
              # --out app-release.apk \
              # app/build/outputs/apk/release/app-release-unsigned.apk
              apksigner #
              #emulator
            ];

            JAVA_HOME = pkgs.jdk.home;
            ANDROID_SDK_ROOT = "${root-home}";
            ANDROID_HOME = "${root-home}";
          };
      }
    );
}
