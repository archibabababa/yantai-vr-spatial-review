# VR project

- [Unity source](Yantai%20VR%20-%20Unity%20source.zip)
- [Windows build](Yantai%20VR%20-%20Archived%20Windows%20build.zip)
- [SketchUp source](Yantai%20VR%20-%20July%202025%20study%20-%20SketchUp%20source.skp): earlier editable model; the Unity scene uses the more detailed `5.15.fbx`.

## Run

Extract the Unity source and open `Assets/Scenes/SampleScene.unity` in Unity 2022.3.53f1c1. Allow package restoration, configure SteamVR and HTC Vive controllers, then enter Play mode. For the Windows build, keep the extracted runtime files together and launch `EXE/VR_DemoFbx.exe` with SteamVR running.

Right trigger rotates; right/left grips move the linked volumes in opposite directions; left trigger adjusts scale; right menu adjusts height. Scale and height follow preset steps.

## Acknowledgements and licences

Shanghai Jiahe Architectural Design Co., Ltd. and Shanghai Jiujing Culture Technology Co., Ltd. provided equipment and facilities. Tracking and controller input use SteamVR/OpenVR.

The Unity project includes Valve SteamVR/OpenVR. See [SteamVR LICENSE.txt](SteamVR%20LICENSE.txt) and the [upstream licence](https://github.com/ValveSoftware/steamvr_unity_plugin/blob/master/LICENSE). JSON.NET licences are retained under Assets/SteamVR/Input/Plugins/JSON.NET in the source archive.

Unity dependencies are listed in the archived Packages/manifest.json and packages-lock.json. The local OpenVR package is included. Unity Editor, the SteamVR runtime and bundled runtime components remain subject to their respective licences.

Original rights and licence notices apply to all software and project assets.
