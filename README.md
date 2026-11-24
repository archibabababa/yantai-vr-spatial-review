# Yantai VR spatial review

**Study conducted in July 2025.**

This study examines a VR revision of three linked gallery volumes at the Yantai High-Tech Zone Science Popularization Museum. The original and revised layouts were compared using CAD and visibility analysis. Fifteen architecture students and fifteen architectural experts assessed the representations, revised layout and VR tool.

Accompanies *Editing linked spaces in virtual reality: A museum study of layout and representation*, by Fan Huang, Yan Zhu and Jia Ning Luo.

## Contributions

Fan Huang designed the study, implemented linked-volume controls in Unity, conducted the spatial analysis and prepared the manuscript and figures. Yan Zhu organised the participant study; Jia Ning Luo provided academic guidance. Shanghai Jiahe Architectural Design Co., Ltd. and Shanghai Jiujing Culture Technology Co., Ltd. provided equipment and facilities. Tracking and controller input use SteamVR/OpenVR.

## Files

| Material | Contents |
| --- | --- |
| [Unity project](VR%20reproduction/Yantai%20VR%20-%20Unity%20source.zip) | Scene, FBX models, scripts and dependencies |
| [Windows build](VR%20reproduction/Yantai%20VR%20-%20Archived%20Windows%20build.zip) | Executable and runtime files |
| [SketchUp model](VR%20reproduction/Yantai%20VR%20-%20July%202025%20study%20-%20SketchUp%20source.skp) | Earlier editable model; the Unity scene uses the more detailed `5.15.fbx` |
| [CAD drawing](Supplementary%20data/Technical%20sources/Drawing1.dxf) | Original and revised plan geometry |
| [Interaction code](Supplementary%20data/Technical%20sources/RightControl.cs) | Linked-volume controls |
| [Data and analysis](Supplementary%20data/Read%20me.txt) | Ratings, native graphs, main result tables and analysis scripts |
| [Figures](Figures/README.md) | Analytical figures and captions |

## Run

Extract the Unity project and open `Assets/Scenes/SampleScene.unity` in Unity 2022.3.53f1c1. Allow package restoration, configure SteamVR and HTC Vive controllers, then enter Play mode. For the Windows build, keep the extracted runtime files together and launch `EXE/VR_DemoFbx.exe` with SteamVR running.

Controls: right trigger rotates; right/left grips move the linked volumes in opposite directions; left trigger adjusts scale; right menu adjusts height. Scale and height adjustments follow preset steps.

## Scope

This is a single-site design study. Layout, medium and presentation order changed together. Experts had site experience; students used photographs and renderings. Findings concern model geometry and participant assessments, not measured visitor behaviour.

[Third-party notices](VR%20reproduction/Third-party%20notices.txt)
