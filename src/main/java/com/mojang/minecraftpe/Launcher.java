package com.mojang.minecraftpe;

import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Iterator;

public class Launcher extends MainActivity {
    private String mcPath;

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
