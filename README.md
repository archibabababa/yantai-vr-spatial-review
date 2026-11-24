# Yantai VR spatial configuration review

**Participant study: July 2025.**

At the Yantai High-Tech Zone Science Popularization Museum, feedback from building users identified problems with circulation, spatial scale and exhibit viewing distance. This project developed a VR tool that let architects adjust three linked gallery volumes and inspect the resulting spaces from within the model. The selected layout was redrawn in CAD and assessed through space syntax analysis and feedback from 15 architecture students and 15 architectural experts.

Materials accompany the manuscript *Editing linked spaces in virtual reality: A museum study of layout and representation*, by **Fan Huang, Yan Zhu and Jia Ning Luo**.

## Research contribution

- **Linked editing in VR:** a Unity/C# prototype maps HTC Vive controller inputs to the translation, rotation, size and height of three predefined gallery volumes. SteamVR/OpenVR provides tracking, input and navigation components.
- **Connecting local edits to the wider layout:** CAD and Depthmap comparisons examine how the selected revision changes visibility across the floor and between particular locations.
- **Evaluating the proposed design:** participant ratings and comments describe how reviewers assessed spatial scale, structure, presence and the revised scheme.

The mean longest horizontal sightline increased from **31.5 to 41.3 m**. From the approach stair, visibility improved substantially towards the broad steps but changed little towards the anteroom. Most reviewers endorsed improvements in circulation and display function. These results show why an overall spatial measure needs to be considered alongside local connections and reviewers' experience.

![Original and revised floor plans, with corresponding landmarks and local visibility measures](Figures/Figure%204%20Plan%20comparison.png)

*Figure 4. Original and revised plans at the same scale. Values are medians for sampled positions within 1.2 m of each landmark; arrows run from original to revised values. Sightlines are horizontal. See the [figure guide](Figures/README.md) for all analytical figures.*

## Author contributions

**Fan Huang** developed the research, implemented the VR prototype, conducted the spatial analysis, prepared the figures and wrote the manuscript. His involvement in the architectural project provided access to the building drawings, model and post-occupancy feedback.

**Yan Zhu** organised the participant study. **Jia Ning Luo** provided academic guidance. Shanghai Jiahe Architectural Design Co., Ltd. and Shanghai Jiujing Culture Technology Co., Ltd. provided equipment and facilities.

## Explore the materials

| Material | Contents |
| --- | --- |
| [SketchUp source model](VR%20reproduction/Yantai%20VR%20-%20July%202025%20study%20-%20SketchUp%20source.skp) | Editable architectural model for the July 2025 study (4.4 MB) |
| [Unity source project](VR%20reproduction/Yantai%20VR%20-%20Unity%20source.zip) | Assets, Packages and ProjectSettings, including the scene, three project FBX models and dependencies (84.4 MB) |
| [Windows build](VR%20reproduction/Yantai%20VR%20-%20Archived%20Windows%20build.zip) | Archived executable and runtime files (33.1 MB); requires compatible VR hardware |
| [CAD drawing](Supplementary%20data/Technical%20sources/Drawing1.dxf) | Plan geometry used for the original and revised layouts |
| [Figures and captions](Figures/README.md) | Workflow, plan comparisons and participant rating distributions |
| [Core interaction code](Supplementary%20data/Technical%20sources/RightControl.cs) | Controller mappings for the three linked volumes |
| [Data and analysis guide](Supplementary%20data/Read%20me.txt) | Questionnaire coding, spatial measures and script instructions |
| [VR setup guide](VR%20reproduction/Reproduction%20guide.txt) | Software requirements, controls and testing scope |
| [File checksums](Checksums.csv) | File sizes and SHA-256 hashes |

The SketchUp model corresponds geometrically to the earlier FBX export in the Unity archive (SHA-256 prefix `fe5fb7ff33fb`). The scene uses `5.15.fbx`, which includes additional mesh detail. Use the SketchUp file to inspect the editable architectural source and the archived FBX to reproduce the supplied scene; an exact native source for the final FBX has not been located. One verified SketchUp version is included. Original asset names, file contents and CAD layer names are preserved.

The numerical scripts require Python 3.10 or later; figure generation also requires NumPy and Matplotlib. Follow the command sequence in the data and analysis guide. The VR prototype uses Unity and SteamVR/OpenVR with HTC Vive controllers.

## Study scope

This is a case study of one proposed redesign. Drawings and video clips showed the original layout, followed by VR of the revision, so VR ratings combine differences in layout, medium and presentation order. Experts had previously visited the building; students used photographs and renderings as their reference. The findings describe model geometry and participants' assessments; effects on actual visitor routes, comfort and viewing conditions remain to be measured.

The [data guide](Supplementary%20data/Read%20me.txt) explains uncertain student responses and the alternate expert tabulation. The [VR guide](VR%20reproduction/Reproduction%20guide.txt) records software checks and the extent of hardware verification. [Third-party notices](VR%20reproduction/Third-party%20notices.txt) accompany the archived software.
