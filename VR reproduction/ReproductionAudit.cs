// Added for present-day verification on 2026-11-06; not historical study code.
using System;
using System.IO;
using System.Linq;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
public static class ReproductionAudit {
  public static void Run() {
    var log = new System.Text.StringBuilder();
    log.AppendLine("PRESENT-DAY ENGINEERING AUDIT; NOT A PARTICIPANT SESSION");
    log.AppendLine("UTC: " + DateTime.UtcNow.ToString("o"));
    log.AppendLine("Editor: " + Application.unityVersion);
    var scene = EditorSceneManager.OpenScene("Assets/Scenes/SampleScene.unity");
    var all = scene.GetRootGameObjects().SelectMany(g => g.GetComponentsInChildren<Transform>(true)).ToArray();
    int missing = all.Sum(t => GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(t.gameObject));
    log.AppendLine("Scene: " + scene.path);
    log.AppendLine("Transform count: " + all.Length);
    log.AppendLine("Missing MonoBehaviour scripts: " + missing);
    log.AppendLine("MeshFilter count: " + all.Count(t => t.GetComponent<MeshFilter>() != null));
    var controls = all.Select(t => t.GetComponent<RightControl>()).Where(c => c != null).ToArray();
    log.AppendLine("RightControl count: " + controls.Length);
    bool bound = controls.Length > 0;
    foreach(var c in controls) {
      foreach(var go in new[]{c.box1,c.box2,c.box3}) {
        if(go == null) { bound=false; log.AppendLine("Unassigned target"); }
        else log.AppendLine("Assigned target: " + go.name + "; localPosition=" + go.transform.localPosition.ToString("F5") + "; localEulerAngles=" + go.transform.localEulerAngles.ToString("F5") + "; localScale=" + go.transform.localScale.ToString("F5"));
      }
    }
    log.AppendLine("Headset/controller interaction tested: NO");
    log.AppendLine("Historical sequence reconstructed: NO");
    log.AppendLine("Scene dependency audit: " + ((missing==0 && bound)?"PASS":"CHECK REQUIRED"));
    string outPath=Path.GetFullPath(Path.Combine(Application.dataPath,"../../Verification logs/Editor scene audit.txt"));
    File.WriteAllText(outPath,log.ToString());
    Debug.Log(log.ToString());
    EditorApplication.Exit(missing==0 && bound ? 0 : 2);
  }
}
