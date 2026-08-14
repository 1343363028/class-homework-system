import type { CapacitorConfig } from '@capacitor/cli'

const config: CapacitorConfig = {
  appId: 'com.homework.system',
  appName: '班级作业查询系统',
  webDir: '../frontend/dist',
  bundledWebRuntime: false,
  server: { androidScheme: 'https' },
  plugins: {
    SplashScreen: { launchShowDuration: 1500, backgroundColor: '#0B1C2C', showSpinner: false },
    StatusBar: { style: 'DARK', backgroundColor: '#0B1C2C' },
  },
  android: { allowMixedContent: true },
  ios: { contentInset: 'always' },
}

export default config
