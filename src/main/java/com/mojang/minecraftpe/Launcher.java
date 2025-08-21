package com.mojang.minecraftpe;

import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Iterator;

public class Launcher extends MainActivity {
    private String mcPath;

    private static boolean shouldLoadMaesdk() {
        try {
            String versionCode = getMinecraftVersion();
            if (versionCode == null || versionCode.isEmpty()) {
                return false;
            }

            if (versionCode.contains("beta")) {
                return isVersionAtLeast(versionCode, "1.21.110.22");
            } else {
                return isVersionAtLeast(versionCode, "1.21.110");
            }
        } catch (Exception e) {
            return false;
        }
    }

    private static String getMinecraftVersion() {
        try {
            File dataDir = new File("/data/data/org.levimc.launcher");
            File[] minecraftDirs = dataDir.listFiles((dir, name) -> name.startsWith("minecraft/"));
            if (minecraftDirs != null) {
                for (File minecraftDir : minecraftDirs) {
                    File versionFile = new File(minecraftDir, "version.txt");
                    if (versionFile.exists()) {
                        return readFileToString(versionFile);
                    }
                }
            }
        } catch (Exception e) {
            try {
                File externalDir = new File(Environment.getExternalStorageDirectory(), "games/org.levimc/minecraft");
                File[] versionDirs = externalDir.listFiles();
                if (versionDirs != null) {
                    for (File versionDir : versionDirs) {
                        if (versionDir.isDirectory()) {
                            File dataDir = new File("/data/data/org.levimc.launcher/minecraft/" + versionDir.getName());
                            File versionFile = new File(dataDir, "version.txt");
                            if (versionFile.exists()) {
                                return readFileToString(versionFile);
                            }
                        }
                    }
                }
            } catch (Exception ex) {
                // Ignore
            }
        }
        return null;
    }

    private static String readFileToString(File file) {
        try (FileInputStream fis = new FileInputStream(file)) {
            byte[] data = new byte[(int) file.length()];
            fis.read(data);
            return new String(data, StandardCharsets.UTF_8).trim();
        } catch (Exception e) {
            return null;
        }
    }

    private static boolean isVersionAtLeast(String currentVersion, String targetVersion) {
        try {
            String[] current = currentVersion.replaceAll("[^0-9.]", "").split("\\.");
            String[] target = targetVersion.split("\\.");

            int maxLength = Math.max(current.length, target.length);

            for (int i = 0; i < maxLength; i++) {
                int currentPart = i < current.length ? Integer.parseInt(current[i]) : 0;
                int targetPart = i < target.length ? Integer.parseInt(target[i]) : 0;

                if (currentPart > targetPart) {
                    return true;
                } else if (currentPart < targetPart) {
                    return false;
                }
            }

            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    @Override
    public void onCreate(Bundle bundle) {
        try {
            this.mcPath = getIntent().getStringExtra("MC_PATH");
            Method declaredMethod = getAssets().getClass().getDeclaredMethod("addAssetPath", String.class);
            declaredMethod.invoke(getAssets(), getIntent().getStringExtra("MC_SRC"));

            ArrayList<String> stringArrayListExtra = getIntent().getStringArrayListExtra("MC_SPLIT_SRC");
            if (stringArrayListExtra != null) {
                Iterator<String> it = stringArrayListExtra.iterator();
                while (it.hasNext()) {
                    declaredMethod.invoke(getAssets(), it.next());
                }
            }
            super.onCreate(bundle);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    static {
        System.loadLibrary("c++_shared");
        System.loadLibrary("fmod");
        if (shouldLoadMaesdk()) {
            System.loadLibrary("maesdk");
        }
        System.loadLibrary("minecraftpe");
        System.loadLibrary("preloader");
    }

    public String getExternalStoragePath() {
        return this.mcPath.isEmpty() ? getExternalFilesDir(null).getAbsolutePath() : this.mcPath;
    }

    public String getLegacyExternalStoragePath(String str) throws IOException {
        boolean z;
        if (this.mcPath.isEmpty()) {
            File externalStorageDirectory = Environment.getExternalStorageDirectory();
            try {
                new FileOutputStream(new File(new File(externalStorageDirectory, str), "test")).close();
                z = true;
            } catch (Exception e) {
                z = false;
            }
            return z ? externalStorageDirectory.getAbsolutePath() : "";
        }
        return "";
    }

    public String getInternalStoragePath() {
        if (this.mcPath.isEmpty()) {
            if (Build.VERSION.SDK_INT >= 24) {
                return getDataDir().getAbsolutePath();
            } else {
                return getFilesDir().getParent();
            }
        }
        return this.mcPath;
    }
}